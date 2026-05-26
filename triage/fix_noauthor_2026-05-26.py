"""Resolve the no-author / non-per-curiam queue (79 opinions), verified per item.

Two verified actions (everything else — 40 authorless summary dispositions —
is left untouched: they carry no byline and no per-curiam label, and CL records
them author:null / per_curiam:false):

  AUTHOR (5): a real authoring byline exists in the opinion body that the empty
  author field missed (page-image markers / post-syllabus byline / separately
  published concurrence). Each confirmed by reading the byline line.

  PER_CURIAM (34): a genuine 'PER CURIAM.' disposition line (pre-1953 + modern
  Rule 35.1/discipline per curiams) or a multi-justice signed institutional
  ORDER (12570, /s/ by all five justices). per_curiam=1; empty author correct.

Run with --apply to write; default dry-run. Logged to changelog for revert.
"""
from __future__ import annotations
import argparse, sqlite3

BATCH = "fix-noauthor-2026-05-26"
DB = "opinions.db"

AUTHORS = {            # oid -> authoring justice (verified byline)
    441:   "Morgan",        # *1052 MORGAN, C. J. (post-syllabus lead byline)
    20388: "Christianson",  # CHRISTIANSON, J. (concurring) — separately published
    20390: "Robinson",      # ROBINSON, J. (concurring specially) — separately published
    20391: "Gronna",        # A. J. *247 GRONNA, District Judge (rehearing)
    15216: "Sandstrom",     # SANDSTROM, Justice. [¶1] (2009 ND 113)
}
PER_CURIAM = [
    152, 443, 20386, 499, 650, 658, 665, 733, 1207, 1505,
    1668, 1669, 1667, 2425, 2427, 20389,          # pre-1953 PER CURIAM.
    12570,                                          # 5-justice signed ORDER OF SUSPENSION
    15976, 17128, 17139, 17196, 17199, 17200, 17207, 17239, 17286, 17289,
    17290, 17293, 17334, 17338, 17369, 17555, 20006,  # modern Per Curiam.
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row

    n_au = n_pc = 0
    for oid, name in AUTHORS.items():
        cur = conn.execute("SELECT author, per_curiam FROM opinions WHERE id=?", (oid,)).fetchone()
        assert cur is not None, oid
        assert not (cur["author"] or "").strip(), f"{oid} already has author {cur['author']!r}"
        print(f"AUTHOR    {oid}: '' -> {name}")
        if args.apply:
            conn.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                         "VALUES (?,?, 'author', ?, ?)", (BATCH, oid, cur["author"], name))
            conn.execute("UPDATE opinions SET author=? WHERE id=?", (name, oid))
        n_au += 1

    for oid in PER_CURIAM:
        cur = conn.execute("SELECT author, per_curiam FROM opinions WHERE id=?", (oid,)).fetchone()
        assert cur is not None, oid
        assert not (cur["author"] or "").strip(), f"{oid} has author {cur['author']!r} — not per curiam?"
        if cur["per_curiam"] == 1:
            print(f"PERCURIAM {oid}: already per_curiam=1 (skip)"); continue
        print(f"PERCURIAM {oid}: per_curiam {cur['per_curiam']} -> 1")
        if args.apply:
            conn.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                         "VALUES (?,?, 'per_curiam', ?, '1')", (BATCH, oid, str(cur["per_curiam"])))
            conn.execute("UPDATE opinions SET per_curiam=1 WHERE id=?", (oid,))
        n_pc += 1

    if args.apply:
        conn.commit()
    print(f"\n{'APPLIED' if args.apply else 'DRY RUN'}: authors={n_au}, per_curiam={n_pc}")
    conn.close()


if __name__ == "__main__":
    main()
