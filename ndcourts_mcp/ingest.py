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


def _classify_reporter(citation: str) -> str | None:
    """Return reporter key for a citation string."""
    if re.search(r"\d{4}\s+ND\s+\d+", citation):
        return "ND"
    if "N.W.2d" in citation:
        return "NW2d"
    if "N.W.3d" in citation:
        return "NW3d"
    if "N.W." in citation:
        return "NW"
    if "N.D." in citation and "N.D. LEXIS" not in citation:
        return "NDold"
    return None


def _normalize_citation(citation: str) -> str:
    """Normalize whitespace in a citation for matching."""
    return re.sub(r"\s+", " ", citation.strip())


def ingest_reporter_opinions(conn, reporter: str, reporter_dir: Path, refs_dir: Path, stats: dict):
    """Ingest all opinions from a reporter directory."""
    if not reporter_dir.is_dir():
        print(f"  {reporter}: directory not found, skipping")
        return

    if reporter in ("NW", "NW2d"):
        _ingest_nw_opinions(conn, reporter, reporter_dir, refs_dir, stats)
    elif reporter == "ND":
        _ingest_nd_opinions(conn, reporter, reporter_dir, refs_dir, stats)


def _ingest_nw_opinions(conn, reporter: str, reporter_dir: Path, refs_dir: Path, stats: dict):
    """Ingest NW/NW2d opinions that have JSON metadata."""
    json_files = sorted(reporter_dir.rglob("*.json"))
    print(f"  {reporter}: found {len(json_files)} metadata files")

    for json_path in json_files:
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


def _ingest_nd_opinions(conn, reporter: str, reporter_dir: Path, refs_dir: Path, stats: dict):
    """Ingest ND neutral-cite opinions, deduplicating against existing records."""
    md_files = sorted(reporter_dir.rglob("*.md"))
    # Exclude .bak directories
    md_files = [f for f in md_files if ".bak" not in str(f)]
    print(f"  {reporter}: found {len(md_files)} opinion files")

    for md_path in md_files:
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

        reporter = _classify_reporter(cite) or source_reporter
        is_primary = 1 if reporter == source_reporter else 0

        # Don't insert duplicates
        existing = conn.execute(
            "SELECT id FROM citations WHERE opinion_id = ? AND citation = ?",
            (opinion_id, cite),
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO citations (opinion_id, citation, reporter, is_primary) VALUES (?, ?, ?, ?)",
                (opinion_id, cite, reporter, is_primary),
            )


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
    args = parser.parse_args()

    refs_dir = args.refs

    if args.rebuild and args.db.exists():
        args.db.unlink()
        print(f"Removed existing {args.db}")

    conn = get_connection(args.db)
    create_schema(conn)

    stats = {"ingested": 0, "deduped": 0, "no_text": 0, "errors": 0}

    print(f"Ingesting from {refs_dir} into {args.db}")
    for reporter in REPORTERS:
        reporter_dir = refs_dir / REPORTER_DIRS[reporter]
        ingest_reporter_opinions(conn, reporter, reporter_dir, refs_dir, stats)
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
