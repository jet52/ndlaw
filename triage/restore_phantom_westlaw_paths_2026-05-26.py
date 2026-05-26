"""Restore the 35 vol-79 westlaw source_paths blanked by westlaw-receive-2026-05-16.

Root cause: receive_westlaw._promote wrote an empty archive_path over the good
N.D./79/<page>-<slug>.doc path (set by backfill-westlaw-source-paths on
2026-04-27) onto both opinions.source_path and the westlaw opinion_sources row,
then set is_primary=1 on that now-empty row. text_content was correctly promoted
to the Westlaw bound text; only the file pointer was lost.

This restores each path from the backfill changelog's recorded new_value (all 35
verified: citation page == filename page, file exists on disk, content matches
caption). For the 34 source_reporter='westlaw' opinions we restore both
opinions.source_path and the westlaw opinion_sources row. For 12705 (NW2d
primary) we restore only the westlaw opinion_sources row — it stays NW2d-primary
with westlaw as a verified second source.

Run with --apply to write; default is dry-run.
"""

from __future__ import annotations

import argparse
import os
import sqlite3

BATCH = "restore-phantom-westlaw-paths-2026-05-26"
DB = "opinions.db"

OIDS = [12377, 12378, 12379, 12380, 12381, 12382, 12383, 12384, 12543, 12544,
        12547, 12548, 12549, 12550, 12694, 12696, 12697, 12698, 12699, 12700,
        12701, 12702, 12703, 12705, 12828, 12829, 12830, 12831, 12832, 12833,
        12834, 12835, 12836, 12994, 12995]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    n_os = n_op = 0
    for oid in OIDS:
        path = conn.execute(
            "SELECT new_value FROM changelog WHERE batch='backfill-westlaw-source-paths' "
            "AND opinion_id=? LIMIT 1", (oid,)).fetchone()
        assert path and path[0], f"no backfill path for {oid}"
        path = path[0]
        assert os.path.isfile(path), f"file missing: {path}"

        wl = conn.execute(
            "SELECT id, source_path FROM opinion_sources "
            "WHERE opinion_id=? AND source_reporter='westlaw'", (oid,)).fetchone()
        assert wl, f"no westlaw opinion_sources row for {oid}"
        assert not wl["source_path"], f"{oid} westlaw path not empty: {wl['source_path']!r}"

        op = conn.execute(
            "SELECT source_reporter, source_path FROM opinions WHERE id=?",
            (oid,)).fetchone()

        # 1. restore opinion_sources.source_path on the westlaw row
        if args.apply:
            conn.execute(
                "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                "VALUES (?,?, 'opinion_sources.source_path', ?, ?)",
                (BATCH, oid, wl["source_path"], path))
            conn.execute("UPDATE opinion_sources SET source_path=? WHERE id=?",
                         (path, wl["id"]))
        n_os += 1

        # 2. restore opinions.source_path ONLY when westlaw is the authoritative
        #    reporter (34 of 35). 12705 stays NW2d-primary -> leave untouched.
        if op["source_reporter"] == "westlaw" and not op["source_path"]:
            if args.apply:
                conn.execute(
                    "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                    "VALUES (?,?, 'source_path', ?, ?)",
                    (BATCH, oid, op["source_path"], path))
                conn.execute("UPDATE opinions SET source_path=? WHERE id=?",
                             (path, oid))
            n_op += 1
            tag = "westlaw-primary"
        else:
            tag = f"{op['source_reporter']}-primary (os-row only)"
        print(f"{oid}  {tag:32s}  {os.path.basename(path)}")

    if args.apply:
        conn.commit()
    print(f"\n{'APPLIED' if args.apply else 'DRY RUN'}: "
          f"opinion_sources rows restored={n_os}, opinions.source_path restored={n_op}")
    conn.close()


if __name__ == "__main__":
    main()
