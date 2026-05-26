"""Resolve the 2 remaining neutral_cite_uniqueness collisions — both are
cross-cite DUPLICATES of an already-correct row, not mere contamination.

2011 ND 161: oid 15703 *Holkesvig v. Welte* is the true owner. oid 15904 is a
  NW2d-sourced copy of *Disciplinary Board v. Lawler* (the real Lawler is
  oid 18870 = 2012 ND 161, markdown) that CL mislabeled with Holkesvig's
  "2011 ND 161" + Holkesvig's markdown source (the page-json NW2d/820/134.json
  carries the same bad parallel). Lawler is PER CURIAM (18870 body confirms);
  15904's "Kapsner" author is a misattribution.

2018 ND 140: oid 17188 *Pettinger v. Carroll* is the true owner. oid 17469 is a
  NW2d-sourced copy of *State v. Peterson* (the real Peterson is oid 19355 =
  2019 ND 140, markdown) mislabeled with Pettinger's "2018 ND 140" + Pettinger's
  markdown source.

Fix per pair: (1) strip the contaminant neutral cite from the NW2d copy, (2)
detach the wrong markdown source (it belongs to the owner), (3) merge the copy
into the correctly-cited markdown row (transfers the correct N.W.2d parallel),
(4) post-merge metadata fixes. Keep = the correct-cite markdown row.

Snapshot: opinions.db.bak-pre-contam-dup-2026-05-26. Row deletions NOT
changelog-revertible — revert via snapshot restore.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from ndcourts_mcp.merge_opinions import merge_pair

BATCH = "section6-contam-dup-2026-05-26"


def strip_and_detach(conn, oid, bad_cite, bad_src, apply):
    print(f"  strip cite {bad_cite!r} + detach src {bad_src!r} from {oid}")
    if not apply:
        return
    log_change(conn, BATCH, oid, "citation.strip", bad_cite, None,
               authority="contaminant neutral cite (belongs to the cite owner)")
    conn.execute("DELETE FROM citations WHERE opinion_id=? AND citation=?",
                 (oid, bad_cite))
    log_change(conn, BATCH, oid, "source.detach", bad_src, None,
               authority="wrong markdown source (belongs to the cite owner)")
    conn.execute("DELETE FROM opinion_sources WHERE opinion_id=? AND source_path=?",
                 (oid, bad_src))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")

    # --- 2011 ND 161 / Lawler ---
    print("Lawler 2012 ND 161 (merge 15904 -> 18870):")
    strip_and_detach(conn, 15904, "2011 ND 161",
                     "markdown/2011/2011ND161.md", args.apply)
    if args.apply:
        # Lawler is per curiam; clear 15904's misattributed author so the
        # merge does not propagate it onto the per-curiam survivor.
        a = conn.execute("SELECT author FROM opinions WHERE id=15904").fetchone()["author"]
        if a:
            log_change(conn, BATCH, 15904, "author", a, None,
                       authority="Lawler 2012 ND 161 is per curiam (18870 body)")
            conn.execute("UPDATE opinions SET author=NULL WHERE id=15904")
    merge_pair(conn, 18870, 15904, "Disciplinary Board v. Lawler",
               apply=args.apply, batch=BATCH)

    # --- 2018 ND 140 / Peterson ---
    print("Peterson 2019 ND 140 (merge 17469 -> 19355):")
    strip_and_detach(conn, 17469, "2018 ND 140",
                     "markdown/2018/2018ND140.md", args.apply)
    merge_pair(conn, 19355, 17469, "State v. Peterson",
               apply=args.apply, batch=BATCH)
    if args.apply:
        # 19355 had no docket; take Peterson's real docket from the merged copy.
        old = conn.execute("SELECT docket_number FROM opinions WHERE id=19355").fetchone()["docket_number"]
        if not old:
            log_change(conn, BATCH, 19355, "docket_number", old, "20180422",
                       authority="Peterson docket from merged copy 17469")
            conn.execute("UPDATE opinions SET docket_number='20180422' WHERE id=19355")
            print("  docket-fix 19355 -> 20180422")

    if args.apply:
        log_provenance(
            conn, operation="section6_contam_dup",
            command="python -m triage.fix_contam_dups_2026-05-26 --apply",
            rows_affected=2,
            notes=(f"batch {BATCH}; resolved the last 2 neutral_cite_uniqueness "
                   f"collisions as cross-cite dups: Lawler 15904->18870 (2012 ND 161), "
                   f"Peterson 17469->19355 (2019 ND 140); stripped contaminant cites "
                   f"2011 ND 161 / 2018 ND 140 + wrong markdown sources first. "
                   f"Snapshot opinions.db.bak-pre-contam-dup-2026-05-26."))
        conn.commit()
        print("  committed.")
    conn.close()


if __name__ == "__main__":
    main()
