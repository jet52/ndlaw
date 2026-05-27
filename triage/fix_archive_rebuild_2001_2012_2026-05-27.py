"""Rebuild 17 mislabeled 2001-2012 rows from their on-disk archive HTML.

Surfaced by the detect_cite_swap DOCKET pass (and INVISIBLE to its CITE pass:
these markdown files lead with a `# Title\\nNorth Dakota Supreme Court\\n<cite>`
block — not YAML `---` — so the frontmatter stripper left the correct cite
visible and the leak was masked). Each row has CORRECT metadata (neutral cite,
case_name, N.W.2d parallel, docket) but its text_content leaked a DIFFERENT,
nearby-numbered opinion (e.g. 13527 labeled 2001 ND 172 *Farmers Elevator*
held 2001 ND 176 *McDowell*). The leaked bodies duplicate opinions that exist
correctly in their own rows; each flagged row's real opinion text is missing.

All 17 have the correct opinion in archive/<year>/<docket>.htm on disk (docket
from the DB, which is correct — archive HTML exists at it). Rebuild text_content
from the archive HTML (independent of the analyzer that produced the leak) via
the canonical parse_opinion_page; KEEP the already-correct case_name + cites;
refresh date/author/per_curiam from the parse; make archive the primary source;
detach the leaked ND markdown source. Guard: the DB neutral label must appear
in the archive HTML's title citations (confirms the right opinion).

Snapshot opinions.db.bak-pre-archive-rebuild-2001-2012-2026-05-27; text swaps
revert via snapshot only. Dry-run default.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ndcourts_mcp.db import (DEFAULT_DB_PATH, get_connection, log_change,
                             log_provenance)
from ndcourts_mcp.scrape_archive import parse_opinion_page, _normalize_author

REFS = Path("/Users/jerod/refs/nd/opin")
BATCH = "fix-archive-rebuild-2001-2012-2026-05-27"
FLAGGED = [13527, 13713, 13552, 14128, 14412, 14868, 14837, 15112, 15246,
           15217, 15557, 15508, 15515, 15642, 15743, 15656, 15850]


def _docket8(s: str | None) -> str | None:
    import re
    m = re.search(r"\d{8}", s or "")
    return m.group(0) if m else None


def _norm_nd(c: str) -> str:
    """Normalize a neutral cite to 'YYYY ND N' (no zero-pad) so the archive
    title's '2010 ND 04' matches the DB '2010 ND 4'."""
    import re
    m = re.search(r"(\d{4})\s+ND\s+0*(\d+)", c or "")
    return f"{m.group(1)} ND {m.group(2)}" if m else (c or "")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")
    fixed = 0
    for oid in FLAGGED:
        row = conn.execute(
            "SELECT case_name, date_filed, docket_number, author, per_curiam "
            "FROM opinions WHERE id=?", (oid,)).fetchone()
        label = conn.execute(
            "SELECT citation FROM citations WHERE opinion_id=? AND "
            "reporter='ND-neutral' LIMIT 1", (oid,)).fetchone()["citation"]
        cites = [c["citation"] for c in conn.execute(
            "SELECT citation FROM citations WHERE opinion_id=? "
            "ORDER BY is_primary DESC, id", (oid,))]
        docket = _docket8(row["docket_number"])
        year = label[:4]
        htm = REFS / f"archive/{year}/{docket}.htm"
        if not docket or not htm.exists():
            print(f"  oid {oid} {label}: archive {docket}.htm MISSING — SKIP")
            continue
        parsed = parse_opinion_page(htm.read_text(encoding="utf-8", errors="replace"))
        # GUARD: the archive HTML must be this opinion (its title cites the label)
        title_cites = {_norm_nd(c) for c in (parsed.get("citations") or [])}
        if _norm_nd(label) not in title_cites:
            print(f"  oid {oid} {label}: GUARD FAIL — archive title cites "
                  f"{parsed.get('citations')} (not {label}); SKIP")
            continue
        text = parsed.get("text", "")
        if len(text) < 200:
            print(f"  oid {oid} {label}: parsed text too short ({len(text)}); SKIP")
            continue
        date_filed = parsed.get("date_filed") or row["date_filed"]
        author_raw = parsed.get("author_raw") or parsed.get("meta_author")
        per_curiam = 1 if (author_raw and "per curiam" in author_raw.lower()) else 0
        author = None if per_curiam else (_normalize_author(author_raw) if author_raw else row["author"])
        arch_rel = f"archive/{year}/{docket}.htm"
        cite_lines = "".join(f' - "{c}"\n' for c in cites)
        full_text = (f'---\ntitle: "{row["case_name"]}"\ncourt: "North Dakota '
                     f'Supreme Court"\ndate_filed: {date_filed}\ncitations:\n'
                     f'{cite_lines}docket_number: "{docket}"\n---\n\n{text}')

        print(f"  oid {oid} {label}: keep '{row['case_name'][:34]}'  "
              f"date {row['date_filed']}->{date_filed}  pc={row['per_curiam']}->{per_curiam}  "
              f"author={row['author']!r}->{author!r}  textlen={len(text)}")

        if not args.apply:
            continue
        for fld, old, new in [("date_filed", row["date_filed"], date_filed),
                              ("author", row["author"], author),
                              ("per_curiam", str(row["per_curiam"]), str(per_curiam))]:
            if str(old) != str(new):
                log_change(conn, BATCH, oid, fld, str(old), str(new),
                           authority=f"rebuilt from archive {arch_rel}")
        log_change(conn, BATCH, oid, "text_content",
                   f"<leaked wrong opinion>", f"<archive: {label}>",
                   authority=f"text_content rebuilt from {arch_rel} (markdown body leak)")
        conn.execute(
            "UPDATE opinions SET date_filed=?, author=?, per_curiam=?, "
            "text_content=?, source_reporter='archive', source_path=? WHERE id=?",
            (date_filed, author, per_curiam, full_text, arch_rel, oid))
        # detach leaked ND markdown source; install archive primary
        conn.execute("DELETE FROM opinion_sources WHERE opinion_id=? AND source_reporter='ND'", (oid,))
        conn.execute("UPDATE opinion_sources SET is_primary=0 WHERE opinion_id=?", (oid,))
        existing = conn.execute("SELECT id FROM opinion_sources WHERE opinion_id=? "
                                "AND source_reporter='archive'", (oid,)).fetchone()
        if existing:
            conn.execute("UPDATE opinion_sources SET source_path=?, text_length=?, "
                         "is_primary=1 WHERE id=?", (arch_rel, len(full_text), existing["id"]))
        else:
            conn.execute(
                "INSERT INTO opinion_sources (opinion_id, source_reporter, source_path, "
                "text_length, is_primary, added_at) VALUES (?, 'archive', ?, ?, 1, "
                "strftime('%Y-%m-%dT%H:%M:%S','now'))", (oid, arch_rel, len(full_text)))
        conn.execute(
            "UPDATE validation_status SET crosscheck_state='corrected', authority_source=?, "
            "batch=?, validated_at=strftime('%Y-%m-%dT%H:%M:%S','now'), note=? WHERE opinion_id=?",
            (f"archive {arch_rel}", BATCH,
             "leaked markdown body replaced with the correct opinion from archive HTML", oid))
        fixed += 1

    if args.apply:
        log_provenance(
            conn, operation="fix_archive_rebuild_2001_2012",
            command="python -m triage.fix_archive_rebuild_2001_2012_2026-05-27 --apply",
            rows_affected=fixed,
            notes=(f"batch {BATCH}; rebuilt {fixed} mislabeled 2001-2012 rows "
                   f"(text leaked a nearby opinion; metadata correct) from on-disk "
                   f"archive HTML; archive made primary, leaked ND markdown detached. "
                   f"Snapshot opinions.db.bak-pre-archive-rebuild-2001-2012-2026-05-27."))
        conn.commit()
        print(f"\n  committed. fixed={fixed}")
    conn.close()


if __name__ == "__main__":
    main()
