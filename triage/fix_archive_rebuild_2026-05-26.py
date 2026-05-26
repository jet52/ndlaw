"""Generalized archive-rebuild fix (same failure mode as the 1997 batch, any year).

For each oid: the row has the correct neutral cite + a correctly-linked
archive.ndcourts.gov HTML source, but text_content/case_name/docket leaked from a
misnamed markdown file. Rebuild from the linked archive HTML via the canonical
parser; archive becomes primary; misnamed ND markdown source detached. Year is
derived from the label cite; archive index/htm read from archive/<year>/.

Group A (2000/2003), verified archive_cite == label_cite:
  18358 2000 ND 198 State v. Lunstad; 18361 2000 ND 215 State v. Lee;
  18462 2003 ND 165 Klingenstein v. Klingenstein.

Snapshot: opinions.db.bak-pre-archiverebuild-groupA-2026-05-26.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from ndcourts_mcp.scrape_archive import (parse_citation_index, parse_opinion_page,
                                         _normalize_author)

REFS = Path("/Users/jerod/refs/nd/opin")
BATCH = "fix-archive-rebuild-2026-05-26"
OIDS = [18358, 18361, 18462]

_INDEX: dict[int, dict] = {}


def index_for(year: int) -> dict:
    if year not in _INDEX:
        idx = (REFS / f"archive/{year}/_index.htm").read_text(encoding="utf-8", errors="replace")
        _INDEX[year] = {e["nd_cite"]: e for e in parse_citation_index(idx, year)}
    return _INDEX[year]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")
    fixed = 0
    for oid in OIDS:
        row = conn.execute(
            "SELECT case_name, date_filed, docket_number, author, per_curiam, "
            "(SELECT citation FROM citations WHERE opinion_id=? AND reporter='ND-neutral' LIMIT 1) cite "
            "FROM opinions WHERE id=?", (oid, oid)).fetchone()
        label = row["cite"]
        year = int(label.split()[0])
        entry = index_for(year).get(label)
        if not entry:
            print(f"  oid {oid} {label}: NO INDEX ENTRY — skipped")
            continue
        docket = entry["docket"]
        htm = REFS / f"archive/{year}/{docket}.htm"
        if not htm.exists():
            print(f"  oid {oid} {label}: {htm} MISSING — skipped")
            continue
        parsed = parse_opinion_page(htm.read_text(encoding="utf-8", errors="replace"))
        case_name = entry["case_name"]
        date_filed = parsed.get("date_filed") or row["date_filed"]
        author_raw = parsed.get("meta_author") or parsed.get("author_raw")
        author = _normalize_author(author_raw) if author_raw else None
        per_curiam = 1 if (author_raw and "per curiam" in author_raw.lower()) else 0
        text = parsed.get("text", "")
        if not text:
            print(f"  oid {oid} {label}: NO TEXT — skipped")
            continue
        arch_rel = f"archive/{year}/{docket}.htm"
        full_text = (f'---\ntitle: "{case_name}"\ncourt: "North Dakota Supreme Court"\n'
                     f'date_filed: {date_filed}\ncitations:\n - "{label}"\n'
                     f'docket_number: "{docket}"\n---\n\n{text}')
        print(f"  oid {oid} {label}: '{row['case_name'][:28]}' -> '{case_name}'  "
              f"date {row['date_filed']}->{date_filed}  docket {row['docket_number']}->{docket}  "
              f"pc={per_curiam} author={author}  textlen={len(text)}")
        if not args.apply:
            continue
        for fld, old, new in [("case_name", row["case_name"], case_name),
                              ("date_filed", row["date_filed"], date_filed),
                              ("docket_number", row["docket_number"], docket),
                              ("author", row["author"], author),
                              ("per_curiam", str(row["per_curiam"]), str(per_curiam))]:
            if str(old) != str(new):
                log_change(conn, BATCH, oid, fld, str(old), str(new),
                           authority=f"rebuilt from archive {arch_rel}")
        log_change(conn, BATCH, oid, "text_content",
                   f"<leaked: {row['case_name'][:40]}>", f"<archive: {case_name[:40]}>",
                   authority=f"text_content rebuilt from {arch_rel} (misnamed-markdown leak)")
        conn.execute(
            "UPDATE opinions SET case_name=?, date_filed=?, docket_number=?, author=?, "
            "per_curiam=?, text_content=?, source_reporter='archive', source_path=? WHERE id=?",
            (case_name, date_filed, docket, author, per_curiam, full_text, arch_rel, oid))
        conn.execute("DELETE FROM opinion_sources WHERE opinion_id=? AND source_reporter='ND'", (oid,))
        conn.execute("UPDATE opinion_sources SET is_primary=1, text_length=? "
                     "WHERE opinion_id=? AND source_reporter='archive'", (len(full_text), oid))
        fixed += 1

    if args.apply:
        log_provenance(
            conn, operation="fix_archive_rebuild",
            command="python -m triage.fix_archive_rebuild_2026-05-26 --apply",
            rows_affected=fixed,
            notes=(f"batch {BATCH}; rebuilt {fixed} mislabeled archive-era rows "
                   f"(2000/2003) from linked archive HTML; archive made primary, "
                   f"misnamed ND markdown detached. Snapshot "
                   f"opinions.db.bak-pre-archiverebuild-groupA-2026-05-26."))
        conn.commit()
        print(f"  committed. fixed={fixed}")
    conn.close()


if __name__ == "__main__":
    main()
