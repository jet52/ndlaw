"""Fix the Feldmann/Pipeline-Petition row contamination at oid 16829.

The CourtListener metadata at ``NW2d/889/399.json`` mistakenly lists
``2017 ND 255`` as a parallel cite of the actual opinion at that page,
which is *In the Matter of a Petition to Permit Temporary Provision of
Legal Services* (the Dakota Access Pipeline pro hac vice order, filed
2017-01-18). Our ingest dutifully attached the bogus cite, then the ND-
side ingest matched ``2017 ND 255`` to ``markdown/2017/2017ND255.md``
(which is actually the Estate of Feldmann opinion at oid 17060),
linking the wrong markdown as the primary source. ``merge_nd_metadata``
then overwrote the row's case_name, date_filed, and author with
Feldmann's data.

Truth (verified by reading both source files and the year JSON):

  oid 16829  represents 2017 ND 1 / 889 N.W.2d 399, the Pipeline
             Petition. Filed 2017-01-18. Per Curiam.
  oid 17060  represents 2017 ND 255 / 903 N.W.2d 280, Estate of
             Feldmann. Filed 2017-10-26. Already correct, untouched.

Fix for oid 16829:
  1. Drop stray cite ``2017 ND 255`` from the citations table.
  2. Detach archive linkage to ``archive/2017/20170034.htm`` (that's
     the Feldmann archive, owned correctly by oid 17060).
  3. Update opinion_sources ND row's source_path:
        ``markdown/2017/2017ND255.md`` → ``markdown/2017/2017ND1.md``.
  4. Update the opinions row to reflect the actual opinion:
        - source_path  → markdown/2017/2017ND1.md
        - text_content → re-read from markdown/2017/2017ND1.md
        - case_name    → "Petition to Permit Temporary Provision of Legal Services"
        - date_filed   → 2017-01-18
        - per_curiam   → 1
        - author       → NULL (per curiam)

After this script runs, ``cite_extract`` should be re-run for opinion
16829 so its text_citations / cited_by reflect the corrected text.

Usage:
    python -m ndcourts_mcp.fix_feldmann_2017 [--db PATH] [--apply]
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from .db import DEFAULT_DB_PATH, log_provenance

DEFAULT_BATCH = "fix-feldmann-2017-2026-05-04"
TARGET_OID = 16829
NEW_CASE_NAME = "Petition to Permit Temporary Provision of Legal Services"
NEW_DATE = "2017-01-18"
NEW_SOURCE_PATH = "markdown/2017/2017ND1.md"
OLD_SOURCE_PATH = "markdown/2017/2017ND255.md"
WRONG_ARCHIVE = "archive/2017/20170034.htm"
STRAY_CITE = "2017 ND 255"


def _log(conn, batch, oid, field_name, old, new):
    conn.execute(
        "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
        "VALUES (?, ?, ?, ?, ?)",
        (batch, oid, field_name, old, new),
    )


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("--refs", type=Path,
                   default=Path.home() / "refs" / "nd" / "opin")
    p.add_argument("--apply", action="store_true",
                   help="Write changes (default is dry-run)")
    p.add_argument("--batch", default=DEFAULT_BATCH)
    args = p.parse_args()

    new_md = args.refs / NEW_SOURCE_PATH
    if not new_md.exists():
        sys.exit(f"!! markdown source missing: {new_md}")
    new_text = new_md.read_text(encoding="utf-8")

    print(f"Planned changes for opinion {TARGET_OID}:")
    print(f"  drop stray cite        {STRAY_CITE!r}")
    print(f"  detach archive         {WRONG_ARCHIVE}")
    print(f"  repoint ND source_path {OLD_SOURCE_PATH} → {NEW_SOURCE_PATH}")
    print(f"  opinions.case_name    → {NEW_CASE_NAME!r}")
    print(f"  opinions.date_filed   → {NEW_DATE}")
    print(f"  opinions.source_path  → {NEW_SOURCE_PATH}")
    print(f"  opinions.text_content → re-read from {NEW_SOURCE_PATH} ({len(new_text)} chars)")
    print(f"  opinions.per_curiam   → 1")
    print(f"  opinions.author       → NULL")

    if not args.apply:
        print("\n(dry-run; pass --apply to write changes)")
        return

    conn = sqlite3.connect(str(args.db))
    conn.row_factory = sqlite3.Row
    written = 0
    try:
        # 1. Drop stray cite
        cite_row = conn.execute(
            "SELECT id FROM citations WHERE opinion_id = ? AND citation = ?",
            (TARGET_OID, STRAY_CITE),
        ).fetchone()
        if cite_row:
            conn.execute("DELETE FROM citations WHERE id = ?", (cite_row["id"],))
            _log(conn, args.batch, TARGET_OID, "citations.stray",
                 f"{STRAY_CITE!r} removed (CL metadata contamination)", None)
            written += 1

        # 2. Detach wrong archive linkage
        arch_row = conn.execute(
            "SELECT id FROM opinion_sources "
            "WHERE opinion_id = ? AND source_reporter = 'archive' AND source_path = ?",
            (TARGET_OID, WRONG_ARCHIVE),
        ).fetchone()
        if arch_row:
            conn.execute("DELETE FROM opinion_sources WHERE id = ?",
                         (arch_row["id"],))
            _log(conn, args.batch, TARGET_OID, "opinion_sources.archive",
                 f"row {arch_row['id']} → {WRONG_ARCHIVE}", None)
            written += 1

        # 3. Repoint ND opinion_sources row
        nd_row = conn.execute(
            "SELECT id, source_path FROM opinion_sources "
            "WHERE opinion_id = ? AND source_reporter = 'ND' AND source_path = ?",
            (TARGET_OID, OLD_SOURCE_PATH),
        ).fetchone()
        if nd_row:
            conn.execute(
                "UPDATE opinion_sources SET source_path = ? WHERE id = ?",
                (NEW_SOURCE_PATH, nd_row["id"]),
            )
            _log(conn, args.batch, TARGET_OID, "opinion_sources.ND.source_path",
                 OLD_SOURCE_PATH, NEW_SOURCE_PATH)
            written += 1

        # 4. Update opinions row
        old = conn.execute(
            "SELECT case_name, date_filed, source_path, per_curiam, author "
            "FROM opinions WHERE id = ?", (TARGET_OID,),
        ).fetchone()
        conn.execute(
            "UPDATE opinions SET case_name = ?, date_filed = ?, source_path = ?, "
            "text_content = ?, per_curiam = 1, author = NULL WHERE id = ?",
            (NEW_CASE_NAME, NEW_DATE, NEW_SOURCE_PATH, new_text, TARGET_OID),
        )
        for field, oldv, newv in (
            ("case_name", old["case_name"], NEW_CASE_NAME),
            ("date_filed", old["date_filed"], NEW_DATE),
            ("source_path", old["source_path"], NEW_SOURCE_PATH),
            ("per_curiam", str(old["per_curiam"]), "1"),
            ("author", old["author"], None),
        ):
            if str(oldv) != str(newv):
                _log(conn, args.batch, TARGET_OID, f"opinions.{field}",
                     str(oldv) if oldv is not None else None, newv)
                written += 1
        # text_content always logged (large field, just record the swap)
        _log(conn, args.batch, TARGET_OID, "opinions.text_content",
             f"(was {OLD_SOURCE_PATH} content)",
             f"(now {NEW_SOURCE_PATH} content, {len(new_text)} chars)")
        written += 1

        log_provenance(
            conn,
            operation="fix_feldmann_2017",
            command=" ".join(sys.argv),
            rows_affected=written,
            notes=f"batch={args.batch}",
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    print(f"\nDone. {written} changelog rows written.")
    print("Next: run `python -m ndcourts_mcp.cite_extract` to refresh "
          "text_citations and cited_by for the corrected text.")


if __name__ == "__main__":
    main()
