"""Fix the Kitchen/Kleinsmith cross-pollution at 2013 ND 18 / 2013 ND 19.

Both opinions are reciprocal-discipline matters filed Feb 12, 2013.
Reading the markdown sources confirms:

  ``markdown/2013/2013ND18.md`` is the **Kitchen** opinion (Craig V.
                                  Kitchen, suspension with conditions).
  ``markdown/2013/2013ND19.md`` is the **Kleinsmith** opinion (Philip M.
                                  Kleinsmith, reprimand and probation).

What the DB says:

  oid 15988  source_path = ``markdown/2013/2013ND18.md`` (Kitchen text)
             case_name   = "Reciprocal Discipline of Kleinsmith"   ✗ wrong
             cites       = 2013 ND 18 ✓, 826 N.W.2d 620 ✓, 2013 ND 19 ✗
             archive     = archive/2013/20130018.htm (Kitchen's HTML, ✓)

  oid 16488  source_path = ``markdown/2013/2013ND19.md`` (Kleinsmith)
             case_name   = "In Re Reciprocal Discipline of Kleinsmith" ✓
             cites       = 2013 ND 19 ✓, 863 N.W.2d 843 ✓, 2013 ND 18 ✗
             archive     = archive/2013/20130018.htm  ✗ (Kitchen's, not Kleinsmith's)

The correct Kleinsmith archive ``archive/2013/20130019.htm`` is on disk
but never linked. Fix:

  - 15988: update case_name to the Kitchen text; drop stray cite ``2013 ND 19``.
  - 16488: detach the wrong archive ``20130018.htm``; insert correct archive
            ``20130019.htm``; drop stray cite ``2013 ND 18``.

Usage:
    python -m ndcourts_mcp.fix_kitchen_kleinsmith_2013 [--db PATH] [--apply]
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from .db import DEFAULT_DB_PATH, log_provenance

DEFAULT_BATCH = "fix-kitchen-kleinsmith-2013-2026-05-04"
KITCHEN_OID = 15988
KLEINSMITH_OID = 16488
NEW_KITCHEN_NAME = "In re Reciprocal Discipline of Kitchen"
KITCHEN_ARCHIVE = "archive/2013/20130018.htm"
KLEINSMITH_ARCHIVE = "archive/2013/20130019.htm"
STRAY_ON_KITCHEN = "2013 ND 19"
STRAY_ON_KLEINSMITH = "2013 ND 18"


def _log(conn, batch, oid, field_name, old, new):
    conn.execute(
        "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
        "VALUES (?, ?, ?, ?, ?)",
        (batch, oid, field_name, old, new),
    )


def fix_kitchen_case_name(conn, batch: str) -> int:
    row = conn.execute(
        "SELECT case_name FROM opinions WHERE id = ?", (KITCHEN_OID,)
    ).fetchone()
    if row is None:
        raise RuntimeError(f"opinion {KITCHEN_OID} not found")
    old = row["case_name"]
    if old == NEW_KITCHEN_NAME:
        return 0
    conn.execute(
        "UPDATE opinions SET case_name = ? WHERE id = ?",
        (NEW_KITCHEN_NAME, KITCHEN_OID),
    )
    _log(conn, batch, KITCHEN_OID, "case_name", old, NEW_KITCHEN_NAME)
    return 1


def drop_stray_cite(conn, batch: str, oid: int, citation: str) -> int:
    row = conn.execute(
        "SELECT id FROM citations WHERE opinion_id = ? AND citation = ?",
        (oid, citation),
    ).fetchone()
    if row is None:
        return 0
    conn.execute("DELETE FROM citations WHERE id = ?", (row["id"],))
    _log(conn, batch, oid, "citations.stray",
         f"{citation!r} removed", None)
    return 1


def detach_archive(conn, batch: str, oid: int, path: str) -> int:
    row = conn.execute(
        "SELECT id FROM opinion_sources "
        "WHERE opinion_id = ? AND source_reporter = 'archive' AND source_path = ?",
        (oid, path),
    ).fetchone()
    if row is None:
        return 0
    conn.execute("DELETE FROM opinion_sources WHERE id = ?", (row["id"],))
    _log(conn, batch, oid, "opinion_sources.archive",
         f"row {row['id']} → {path}", None)
    return 1


def insert_archive(conn, batch: str, oid: int, path: str, refs_dir: Path) -> int:
    full = refs_dir / path
    if not full.exists():
        raise RuntimeError(f"archive file missing: {full}")
    text_length = full.stat().st_size
    cur = conn.execute(
        "INSERT INTO opinion_sources "
        "(opinion_id, source_reporter, source_path, text_length, is_primary, added_at) "
        "VALUES (?, 'archive', ?, ?, 0, datetime('now'))",
        (oid, path, text_length),
    )
    _log(conn, batch, oid, "opinion_sources.archive",
         None, f"row {cur.lastrowid} → {path}")
    return 1


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("--refs", type=Path,
                   default=Path.home() / "refs" / "nd" / "opin")
    p.add_argument("--apply", action="store_true",
                   help="Write changes (default is dry-run)")
    p.add_argument("--batch", default=DEFAULT_BATCH)
    args = p.parse_args()

    print(f"Planned changes:")
    print(f"  oid {KITCHEN_OID}: case_name → {NEW_KITCHEN_NAME!r}")
    print(f"  oid {KITCHEN_OID}: drop stray cite {STRAY_ON_KITCHEN!r}")
    print(f"  oid {KLEINSMITH_OID}: detach archive {KITCHEN_ARCHIVE}")
    print(f"  oid {KLEINSMITH_OID}: insert archive {KLEINSMITH_ARCHIVE}")
    print(f"  oid {KLEINSMITH_OID}: drop stray cite {STRAY_ON_KLEINSMITH!r}")

    if not args.apply:
        print("\n(dry-run; pass --apply to write changes)")
        return

    conn = sqlite3.connect(str(args.db))
    conn.row_factory = sqlite3.Row
    written = 0
    try:
        written += fix_kitchen_case_name(conn, args.batch)
        written += drop_stray_cite(conn, args.batch, KITCHEN_OID, STRAY_ON_KITCHEN)
        written += detach_archive(conn, args.batch, KLEINSMITH_OID, KITCHEN_ARCHIVE)
        written += insert_archive(conn, args.batch, KLEINSMITH_OID,
                                  KLEINSMITH_ARCHIVE, args.refs)
        written += drop_stray_cite(conn, args.batch, KLEINSMITH_OID, STRAY_ON_KLEINSMITH)
        log_provenance(
            conn,
            operation="fix_kitchen_kleinsmith_2013",
            command=" ".join(sys.argv),
            rows_affected=written,
            notes=f"batch={args.batch}",
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    print(f"\nDone. {written} changelog rows written.")


if __name__ == "__main__":
    main()
