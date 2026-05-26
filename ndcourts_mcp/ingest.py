"""Ingest opinions from ~/refs/nd/opin/ into SQLite.

Processes NW and NW2d opinions first (they have rich JSON metadata from
CourtListener), then ND neutral-cite opinions (under markdown/), deduplicating
against already-ingested records by matching parallel citations.
"""

import json
import re
import sys
from pathlib import Path

from .db import DEFAULT_DB_PATH, create_schema, get_connection

REFS_DIR = Path.home() / "refs" / "nd" / "opin"

# Reporters to ingest, in order. NW/NW2d first because they have JSON metadata.
# ND neutral-cite opinions (under markdown/) are then matched against existing records.
# Map logical reporter name → actual subdirectory name under REFS_DIR.
REPORTERS = ["NW", "NW2d", "ND"]
REPORTER_DIRS = {"NW": "NW", "NW2d": "NW2d", "ND": "markdown"}


def _parse_json_metadata(json_path: Path) -> dict | None:
    """Parse a CourtListener JSON metadata file."""
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        return data
    except (json.JSONDecodeError, OSError):
        return None


def _extract_author(judges_str: str | None, text: str) -> tuple[str | None, bool]:
    """Extract opinion author and per curiam status.

    Returns (author_name, is_per_curiam).
    """
    if not judges_str and not text:
        return None, False

    # Check for per curiam
    first_500 = text[:500].lower() if text else ""
    if "per curiam" in first_500:
        return None, True

    # Try to find author from text patterns like "Justice Tufte writing"
    # or "Sandstrom, Justice." at the start
    author_patterns = [
        r"(?:Chief\s+)?Justice\s+(\w+)\s+(?:writing|delivered)",
        r"(\w+),\s+(?:Chief\s+)?Justice\.",
    ]
    for pattern in author_patterns:
        m = re.search(pattern, text[:2000] if text else "")
        if m:
            return m.group(1), False

    # Fall back to first judge listed (often the author)
    if judges_str:
        first = judges_str.split(",")[0].strip()
        # Remove title prefixes
        first = re.sub(r"^(Chief\s+)?Justice\s+", "", first).strip()
        if first:
            return first, False

    return None, False


# Contract 1 (SCHEMA.md): closed citations.reporter taxonomy.
# is_primary selection ladder (Contract 2): highest available wins.
PRIMARY_LADDER = ["ND-neutral", "ND", "NW3d", "NW2d", "NW"]
SECONDARY_REPORTERS = {"ALR", "LRA", "US", "SCT", "LED"}
# §10 back-assigned medium-neutral cites (YYYY ND nnn) for pre-1997 opinions.
# Synthetic/editorial — a stable unique ID, NOT how the case was published, so
# is_primary=0 ALWAYS (kept out of PRIMARY_LADDER → recompute_primary never picks
# it; enforced by the synthetic_never_primary invariant). The reporter value is
# set explicitly by the §10 insert path, never emitted by _classify_reporter
# (whose string-only view cannot tell a synthetic YYYY ND nnn from a native one).
SYNTHETIC_REPORTERS = {"ND-neutral-synthetic"}
REPORTER_TAXONOMY = set(PRIMARY_LADDER) | SECONDARY_REPORTERS | SYNTHETIC_REPORTERS


def _classify_reporter(citation: str) -> str | None:
    """Return the Contract-1 reporter key for a citation string.

    ND-neutral = `YYYY ND N` medium-neutral (official since 1997).
    ND         = `<v> N.D. <p>` official North Dakota Reports (vols 1-79).
    NW/NW2d/NW3d = North Western Reporter regional parallel series.
    ALR/LRA      = secondary annotation reprints (never primary).
    US/SCT/LED   = foreign U.S. Supreme Court reporters (never primary).
    """
    if re.search(r"\d{4}\s+ND\s+\d+", citation):
        return "ND-neutral"
    if "A.L.R." in citation:
        return "ALR"
    if "L.R.A." in citation:
        return "LRA"
    if re.search(r"\d+\s+U\.S\.\s+\d+", citation):
        return "US"
    if "S.Ct." in citation or "S. Ct." in citation:
        return "SCT"
    if "L.Ed." in citation or "L. Ed." in citation:
        return "LED"
    if "N.W.2d" in citation:
        return "NW2d"
    if "N.W.3d" in citation:
        return "NW3d"
    if "N.W." in citation:
        return "NW"
    if "N.D." in citation and "N.D. LEXIS" not in citation:
        return "ND"
    return None


def recompute_primary(conn, opinion_id: int) -> list[tuple[int, int, int]]:
    """Set citations.is_primary for one opinion per the Contract-2 ladder.

    Exactly one citation row gets is_primary=1: the highest rung
    (ND-neutral > ND > NW3d > NW2d > NW) present; ties broken by lowest
    citation id. Secondary/foreign reporters are never primary. Returns the
    list of (citation_id, old_is_primary, new_is_primary) rows that changed
    so callers can log them to the changelog.
    """
    rows = conn.execute(
        "SELECT id, reporter, is_primary FROM citations "
        "WHERE opinion_id = ? ORDER BY id",
        (opinion_id,),
    ).fetchall()
    best_id = None
    best_rank = None
    for r in rows:
        rep = r["reporter"]
        if rep in PRIMARY_LADDER:
            rank = PRIMARY_LADDER.index(rep)
            if best_rank is None or rank < best_rank:
                best_rank = rank
                best_id = r["id"]
    changed: list[tuple[int, int, int]] = []
    for r in rows:
        want = 1 if r["id"] == best_id else 0
        if r["is_primary"] != want:
            conn.execute(
                "UPDATE citations SET is_primary = ? WHERE id = ?",
                (want, r["id"]),
            )
            changed.append((r["id"], r["is_primary"], want))
    return changed


def _normalize_citation(citation: str) -> str:
    """Normalize whitespace in a citation for matching."""
    return re.sub(r"\s+", " ", citation.strip())


def _maybe_commit(conn, processed: int, commit_every: int) -> None:
    """Memory-bounded ingest: with one transaction per reporter, ~12k large
    text_content rows + their FTS5 trigger writes accumulate uncommitted in
    the WAL for the whole pass and can OOM the process (exit 137) under
    memory pressure — this is what the unattended weekly launchd job hits.
    Committing every `commit_every` records and truncating the WAL bounds
    in-flight memory. commit_every=0 restores the legacy single
    transaction. Re-running ingest converges (cluster_id/citation dedup +
    idempotent _record_source), so the loss of whole-pass atomicity is
    safe for this additive pipeline."""
    if commit_every and processed and processed % commit_every == 0:
        conn.commit()
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")


def ingest_reporter_opinions(conn, reporter: str, reporter_dir: Path,
                             refs_dir: Path, stats: dict,
                             commit_every: int = 500,
                             since_year: int | None = None):
    """Ingest all opinions from a reporter directory."""
    if not reporter_dir.is_dir():
        print(f"  {reporter}: directory not found, skipping")
        return

    if reporter in ("NW", "NW2d"):
        _ingest_nw_opinions(conn, reporter, reporter_dir, refs_dir, stats,
                            commit_every)
    elif reporter == "ND":
        _ingest_nd_opinions(conn, reporter, reporter_dir, refs_dir, stats,
                            commit_every, since_year)


def _ingest_nw_opinions(conn, reporter: str, reporter_dir: Path,
                        refs_dir: Path, stats: dict,
                        commit_every: int = 500):
    """Ingest NW/NW2d opinions that have JSON metadata."""
    json_files = sorted(reporter_dir.rglob("*.json"))
    print(f"  {reporter}: found {len(json_files)} metadata files")

    for _i, json_path in enumerate(json_files, 1):
        _maybe_commit(conn, _i - 1, commit_every)
        meta = _parse_json_metadata(json_path)
        if not meta:
            stats["errors"] += 1
            continue

        # Find corresponding markdown
        md_path = json_path.with_suffix(".md")
        if not md_path.is_file():
            stats["no_text"] += 1
            continue

        text = md_path.read_text(encoding="utf-8")
        if not text.strip():
            stats["no_text"] += 1
            continue

        cluster_id = meta.get("cluster_id")
        case_name = meta.get("case_name", "Unknown")
        case_name_full = meta.get("case_name_full")
        date_filed = meta.get("date_filed", "")
        judges = meta.get("judges", "")
        docket_number = meta.get("docket_number", "")
        absolute_url = meta.get("absolute_url", "")
        citations = meta.get("citations", [])

        # Skip if cluster_id already ingested (from another reporter)
        if cluster_id:
            existing = conn.execute(
                "SELECT id FROM opinions WHERE cluster_id = ?", (cluster_id,)
            ).fetchone()
            if existing:
                # Add any new citations from this reporter
                _add_citations(conn, existing["id"], citations, reporter)
                # Record this reporter's file as a secondary source
                _record_source(
                    conn, existing["id"], reporter, md_path, refs_dir, text,
                    is_primary=0, cluster_id=cluster_id,
                )
                stats["deduped"] += 1
                continue

        author, per_curiam = _extract_author(judges, text)

        cur = conn.execute(
            """INSERT INTO opinions
               (cluster_id, case_name, case_name_full, date_filed, docket_number,
                judges, per_curiam, author, absolute_url, source_reporter, source_path,
                text_content)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                cluster_id,
                case_name,
                case_name_full,
                date_filed,
                docket_number,
                judges,
                1 if per_curiam else 0,
                author,
                absolute_url,
                reporter,
                str(md_path.relative_to(refs_dir)),
                text,
            ),
        )
        opinion_id = cur.lastrowid
        _add_citations(conn, opinion_id, citations, reporter)
        _record_source(
            conn, opinion_id, reporter, md_path, refs_dir, text,
            is_primary=1, cluster_id=cluster_id,
        )
        stats["ingested"] += 1

    conn.commit()


def _ingest_nd_opinions(conn, reporter: str, reporter_dir: Path,
                        refs_dir: Path, stats: dict,
                        commit_every: int = 500,
                        since_year: int | None = None):
    """Ingest ND neutral-cite opinions, deduplicating against existing records.

    `since_year` (incremental mode) skips files whose `YYYYNDn.md` filename
    year is older than the given year — applied from the filename BEFORE any
    file read, so old years cost nothing. This is what makes the weekly
    pipeline both cheap and safe: it never re-scans the historical trees
    where §6-merged-away duplicates' source files still live, so a full
    re-ingest can't resurrect them (their citation was re-pointed to the
    keep row, so a re-scan would otherwise re-insert the orphaned file)."""
    md_files = sorted(reporter_dir.rglob("*.md"))
    # Exclude .bak directories
    md_files = [f for f in md_files if ".bak" not in str(f)]
    print(f"  {reporter}: found {len(md_files)} opinion files"
          + (f" (incremental: year >= {since_year})" if since_year else ""))

    for _i, md_path in enumerate(md_files, 1):
        _maybe_commit(conn, _i - 1, commit_every)
        if since_year is not None:
            ym = re.match(r"(\d{4})ND", md_path.stem)
            if not ym or int(ym.group(1)) < since_year:
                continue
        text = md_path.read_text(encoding="utf-8")
        if not text.strip():
            stats["no_text"] += 1
            continue

        # Extract neutral citation from filename: 2024ND156.md -> 2024 ND 156
        stem = md_path.stem
        m = re.match(r"(\d{4})ND(\d+)", stem)
        if not m:
            stats["errors"] += 1
            continue

        year, num = m.group(1), m.group(2)
        neutral_cite = f"{year} ND {num}"

        # Check if this opinion is already in the database via citation match
        existing = conn.execute(
            "SELECT opinion_id FROM citations WHERE citation = ?",
            (neutral_cite,),
        ).fetchone()

        if existing:
            # Already have it from NW/NW2d ingest
            opinion_id = existing["opinion_id"]
            op_row = conn.execute(
                "SELECT text_content, date_filed, source_reporter FROM opinions WHERE id = ?",
                (opinion_id,),
            ).fetchone()

            # Record the ND markdown as a source. Mark it primary for 1997+
            # (ndcourts.gov is authoritative for that era).
            nd_is_primary = 1 if op_row["date_filed"] >= "1997-01-01" else 0
            inserted = _record_source(
                conn, opinion_id, reporter, md_path, refs_dir, text,
                is_primary=nd_is_primary,
            )
            if inserted and nd_is_primary and op_row["source_reporter"] != "ND":
                # Flip existing primary flag off, promote the opinions row
                conn.execute(
                    "UPDATE opinion_sources SET is_primary = 0 "
                    "WHERE opinion_id = ? AND source_reporter != 'ND'",
                    (opinion_id,),
                )
                conn.execute(
                    "UPDATE opinions SET source_reporter = 'ND', source_path = ? WHERE id = ?",
                    (str(md_path.relative_to(refs_dir)), opinion_id),
                )

            # ND opinions have [¶N] markers — prefer those
            if "[¶" in text and "[¶" not in op_row["text_content"]:
                conn.execute(
                    "UPDATE opinions SET text_content = ?, source_path = ? WHERE id = ?",
                    (text, str(md_path.relative_to(refs_dir)), opinion_id),
                )

            stats["deduped"] += 1
            continue

        # New opinion not found via NW/NW2d — ingest fresh
        # Try to extract metadata from the text itself
        case_name = _extract_case_name_from_text(text, md_path)
        date_filed = _extract_date_from_text(text) or f"{year}-01-01"
        author, per_curiam = _extract_author(None, text)

        cur = conn.execute(
            """INSERT INTO opinions
               (cluster_id, case_name, case_name_full, date_filed, docket_number,
                judges, per_curiam, author, absolute_url, source_reporter, source_path,
                text_content)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                None,
                case_name,
                None,
                date_filed,
                None,
                None,
                1 if per_curiam else 0,
                author,
                None,
                reporter,
                str(md_path.relative_to(refs_dir)),
                text,
            ),
        )
        opinion_id = cur.lastrowid
        _add_citations(conn, opinion_id, [neutral_cite], reporter)
        _record_source(
            conn, opinion_id, reporter, md_path, refs_dir, text, is_primary=1,
        )
        stats["ingested"] += 1

    conn.commit()


def _extract_case_name_from_text(text: str, path: Path) -> str:
    """Best-effort case name extraction from opinion text."""
    # Look for "v." pattern in first few lines
    for line in text.splitlines()[:20]:
        line = line.strip()
        if " v. " in line or " v " in line:
            # Clean up
            name = re.sub(r"\s+", " ", line).strip()
            if len(name) < 200:
                return name
    return path.stem


def _extract_date_from_text(text: str) -> str | None:
    """Try to find a filed date in the opinion text."""
    # Patterns like "Filed May 16, 2024" or "Filed 05/16/2024"
    m = re.search(
        r"[Ff]iled\s+(\w+\s+\d{1,2},?\s+\d{4})", text[:3000]
    )
    if m:
        from datetime import datetime

        try:
            dt = datetime.strptime(m.group(1).replace(",", ""), "%B %d %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def _add_citations(
    conn, opinion_id: int, citations: list[str], source_reporter: str
) -> None:
    """Add citations for an opinion, skipping LEXIS/WL cites."""
    for cite in citations:
        cite = _normalize_citation(cite)
        # Skip non-useful citation formats
        if any(skip in cite for skip in ("LEXIS", "WL ", "Westlaw")):
            continue

        # citations.reporter is the citation-series axis (Contract 1); never
        # fall back to source_reporter (text-provenance axis) — that would
        # poison the taxonomy with values like 'westlaw'/'archive'.
        reporter = _classify_reporter(cite)

        # Don't insert duplicates
        existing = conn.execute(
            "SELECT id FROM citations WHERE opinion_id = ? AND citation = ?",
            (opinion_id, cite),
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO citations (opinion_id, citation, reporter, is_primary) VALUES (?, ?, ?, 0)",
                (opinion_id, cite, reporter),
            )

    # is_primary follows the Contract-2 ladder, not text provenance.
    recompute_primary(conn, opinion_id)


def _record_source(
    conn,
    opinion_id: int,
    reporter: str,
    md_path: Path,
    refs_dir: Path,
    text: str,
    is_primary: int,
    cluster_id: int | None = None,
) -> bool:
    """Insert an opinion_sources row if one doesn't already exist for this
    (opinion_id, source_reporter). Returns True if a row was inserted."""
    existing = conn.execute(
        "SELECT id FROM opinion_sources WHERE opinion_id = ? AND source_reporter = ?",
        (opinion_id, reporter),
    ).fetchone()
    if existing:
        return False
    conn.execute(
        """INSERT INTO opinion_sources
           (opinion_id, source_reporter, source_path, cluster_id, text_length,
            is_primary, added_at)
           VALUES (?, ?, ?, ?, ?, ?,
            strftime('%Y-%m-%dT%H:%M:%S', 'now'))""",
        (
            opinion_id,
            reporter,
            str(md_path.relative_to(refs_dir)),
            cluster_id,
            len(text),
            is_primary,
        ),
    )
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Ingest opinions into SQLite")
    parser.add_argument(
        "--db", type=Path, default=DEFAULT_DB_PATH, help="Database path"
    )
    parser.add_argument(
        "--refs", type=Path, default=REFS_DIR, help="Refs opinion directory"
    )
    parser.add_argument(
        "--rebuild", action="store_true", help="Drop and rebuild the database"
    )
    parser.add_argument(
        "--commit-every", type=int, default=500,
        help="Memory-bounded mode: commit + truncate the WAL every N "
             "processed records (default 500; 0 = single transaction per "
             "reporter, the legacy unbounded behavior that can OOM)",
    )
    parser.add_argument(
        "--incremental", action="store_true",
        help="Only ingest new ND opinions from the current era forward "
             "(ND markdown, year >= the DB's latest opinion year; NW/NW2d "
             "historical trees skipped). This is the safe weekly mode: it "
             "cannot resurrect §6-merged-away duplicates (whose orphaned "
             "source files live in the skipped historical trees) and is "
             "inherently memory-light. Use the default full mode only for "
             "a deliberate full rebuild.",
    )
    args = parser.parse_args()

    refs_dir = args.refs

    if args.rebuild and args.db.exists():
        args.db.unlink()
        print(f"Removed existing {args.db}")

    conn = get_connection(args.db, must_exist=False)
    # Bound SQLite's page cache (~20 MB) for this bulk-ingest connection so
    # a large run can't balloon cache memory on top of the WAL.
    conn.execute("PRAGMA cache_size=-20000")
    create_schema(conn)

    stats = {"ingested": 0, "deduped": 0, "no_text": 0, "errors": 0}

    reporters = REPORTERS
    since_year = None
    if args.incremental:
        latest = conn.execute(
            "SELECT MAX(date_filed) FROM opinions"
        ).fetchone()[0]
        if latest and len(latest) >= 4 and latest[:4].isdigit():
            since_year = int(latest[:4])
            # Weekly ndcourts.gov scrape only adds ND markdown; NW/NW2d are
            # historical CourtListener bulk that never changes weekly and is
            # exactly where merged-away dup source files live — skip it.
            reporters = ["ND"]
            print(f"Incremental: ND only, year >= {since_year} "
                  f"(latest DB opinion {latest})")
        else:
            print("Incremental requested but DB has no dated opinions — "
                  "falling back to full ingest")

    print(f"Ingesting from {refs_dir} into {args.db}")
    for reporter in reporters:
        reporter_dir = refs_dir / REPORTER_DIRS[reporter]
        ingest_reporter_opinions(conn, reporter, reporter_dir, refs_dir, stats,
                                 args.commit_every, since_year)
        print(
            f"    Running totals: {stats['ingested']} ingested, "
            f"{stats['deduped']} deduped, {stats['no_text']} no text, "
            f"{stats['errors']} errors"
        )

    # Final stats
    total_opinions = conn.execute("SELECT COUNT(*) FROM opinions").fetchone()[0]
    total_citations = conn.execute("SELECT COUNT(*) FROM citations").fetchone()[0]
    date_range = conn.execute(
        "SELECT MIN(date_filed), MAX(date_filed) FROM opinions"
    ).fetchone()

    conn.close()

    print(f"\nDone.")
    print(f"  {total_opinions} opinions ({date_range[0]} to {date_range[1]})")
    print(f"  {total_citations} citation records")
    print(f"  {stats['deduped']} duplicates merged")
    if stats["errors"]:
        print(f"  {stats['errors']} errors")


if __name__ == "__main__":
    main()
