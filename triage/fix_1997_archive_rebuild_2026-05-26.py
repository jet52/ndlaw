"""Fix the 16 mislabeled 1997 rows by rebuilding from their (correct) linked
archive.ndcourts.gov HTML.

Diagnosis (verify_1997_archive_2026-05-26): each row has the CORRECT neutral cite
and a CORRECT archive HTML source, but its text_content/case_name/docket leaked
from a misnamed markdown file (the refs-migration-nd-opin batch). The real opinion
is in the linked archive HTML. Per user (2026-05-26): rebuild from on-disk archive
HTML via the canonical parser; leave N.W.2d parallels alone (archive-title parallels
are unreliable).

Per row: re-parse archive/1997/<docket>.htm with scrape_archive.parse_opinion_page,
take the clean case_name from the year index, rebuild text_content (frontmatter+text)
the same way scrape_archive.ingest_opinions does, set date/author/per_curiam/docket,
make archive the primary source, and detach the misnamed ND markdown source.
Citations are untouched (neutral cite stays primary; 12476 keeps 566 N.W.2d 407 —
distinct from 1997 ND 129's 566 N.W.2d 406, so not contamination).

Snapshot: opinions.db.bak-pre-1997archive-2026-05-26. NOT changelog-revertible
for text_content swaps (snapshot only).
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from ndcourts_mcp.scrape_archive import (parse_citation_index, parse_opinion_page,
                                         _normalize_author)

REFS = Path("/Users/jerod/refs/nd/opin")
BATCH = "fix-1997-archive-rebuild-2026-05-26"
FLAGGED = [18248, 18249, 18250, 18251, 18252, 18270, 18271, 18272, 18274,
           18275, 18276, 18277, 18278, 18279, 18280, 12476]


def build_index() -> dict:
    idx = (REFS / "archive/1997/_index.htm").read_text(encoding="utf-8", errors="replace")
    return {e["nd_cite"]: e for e in parse_citation_index(idx, 1997)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    index = build_index()
    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")
    fixed = 0
    for oid in FLAGGED:
        row = conn.execute(
            "SELECT case_name, date_filed, docket_number, author, per_curiam, "
            "(SELECT citation FROM citations WHERE opinion_id=? AND reporter='ND-neutral' LIMIT 1) cite "
            "FROM opinions WHERE id=?", (oid, oid)).fetchone()
        label = row["cite"]
        entry = index.get(label)
        if not entry:
            print(f"  oid {oid} {label}: NO INDEX ENTRY — skipped")
            continue
        docket = entry["docket"]
        htm = REFS / f"archive/1997/{docket}.htm"
        if not htm.exists():
            print(f"  oid {oid} {label}: archive htm {docket}.htm MISSING — skipped")
            continue
        parsed = parse_opinion_page(htm.read_text(encoding="utf-8", errors="replace"))
        case_name = entry["case_name"]
        date_filed = parsed.get("date_filed") or row["date_filed"]
        author_raw = parsed.get("meta_author") or parsed.get("author_raw")
        author = _normalize_author(author_raw) if author_raw else None
        per_curiam = 1 if (author_raw and "per curiam" in author_raw.lower()) else 0
        text = parsed.get("text", "")
        if not text:
            print(f"  oid {oid} {label}: archive parse produced NO TEXT — skipped")
            continue
        arch_rel = f"archive/1997/{docket}.htm"
        full_text = (f'---\ntitle: "{case_name}"\ncourt: "North Dakota Supreme Court"\n'
                     f'date_filed: {date_filed}\ncitations:\n - "{label}"\n'
                     f'docket_number: "{docket}"\n---\n\n{text}')

        print(f"  oid {oid} {label}: '{row['case_name'][:30]}' -> '{case_name}'  "
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
                   authority=f"text_content rebuilt from {arch_rel} (was misnamed-markdown leak)")
        conn.execute(
            "UPDATE opinions SET case_name=?, date_filed=?, docket_number=?, author=?, "
            "per_curiam=?, text_content=?, source_reporter='archive', source_path=? WHERE id=?",
            (case_name, date_filed, docket, author, per_curiam, full_text, arch_rel, oid))
        # sources: drop the misnamed ND markdown row; make archive primary
        conn.execute("DELETE FROM opinion_sources WHERE opinion_id=? AND source_reporter='ND'", (oid,))
        conn.execute("UPDATE opinion_sources SET is_primary=1, text_length=? "
                     "WHERE opinion_id=? AND source_reporter='archive'", (len(full_text), oid))
        fixed += 1

    if args.apply:
        log_provenance(
            conn, operation="fix_1997_archive_rebuild",
            command="python -m triage.fix_1997_archive_rebuild_2026-05-26 --apply",
            rows_affected=fixed,
            notes=(f"batch {BATCH}; rebuilt {fixed} mislabeled 1997 rows from their "
                   f"linked archive.ndcourts.gov HTML (correct cite+archive source; "
                   f"text/caption/docket had leaked from misnamed markdown). Archive "
                   f"made primary; misnamed ND markdown source detached. Snapshot "
                   f"opinions.db.bak-pre-1997archive-2026-05-26."))
        conn.commit()
        print(f"  committed. fixed={fixed}")
    conn.close()


if __name__ == "__main__":
    main()
