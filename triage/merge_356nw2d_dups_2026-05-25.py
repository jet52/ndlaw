"""§6 dedup: merge the 4 wrong-cite single-source duplicates in 356 N.W.2d into
their correct-cite, court-archive-sourced twins (verified 2026-05-25; user-ratified).

Each pull-list "single-source" opinion was a CL double-ingest carrying a WRONG
N.W.2d page (the page of a neighboring Nebraska/Bauer case); its twin already has
the correct cite + a 2nd source. All drops have inbound cited_by = 0.

  keep (twin)              <- drop (dup)            case
  20486 356 N.W.2d 893     <- 9235 889              State v. Lawson      (j=0.83)
  9239  356 N.W.2d 894     <- 9237 890              First Federal/Scherle(j=0.83)
  9243  356 N.W.2d 901     <- 9240 897              Calavera v. Vix      (j=0.79)
  9244  356 N.W.2d 903     <- 9242 899              State v. Ronngren    (j=0.84)

merge_pair re-points all referencing tables + deletes the drop, but carries the
drop's (wrong) cite, synthetic cite, and wrong-page NW2d markdown source onto the
survivor — so we delete those after. Re-run §10 resequence + align_primary_source
+ invariants afterward. Snapshot before --apply.
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change  # noqa: E402
from ndcourts_mcp.merge_opinions import merge_pair  # noqa: E402
from ndcourts_mcp.ingest import recompute_primary  # noqa: E402

BATCH = "merge-356nw2d-dups-2026-05-25"
# keep, drop, canonical_name, drop_nw2d_cite, drop_synth_cite, drop_nw2d_source
PAIRS = [
    (20486, 9235, "State v. Lawson", "356 N.W.2d 889", "1984 ND 184", "NW2d/356/889.md"),
    (9239, 9237, "First Federal Sav. and Loan Ass'n v. Scherle", "356 N.W.2d 890", "1984 ND 186", "NW2d/356/890.md"),
    (9243, 9240, "Calavera v. Vix", "356 N.W.2d 897", "1984 ND 188", "NW2d/356/897.md"),
    (9244, 9242, "State v. Ronngren", "356 N.W.2d 899", "1984 ND 190", "NW2d/356/899.md"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)
    for keep, drop, canon, bad_nw, bad_synth, bad_src in PAIRS:
        plan = merge_pair(conn, keep, drop, canon, apply=args.apply, batch=BATCH)
        print(f"  merge {drop} -> {keep}: {plan['name']}")
        if not args.apply:
            continue
        for cite in (bad_nw, bad_synth):
            n = conn.execute("DELETE FROM citations WHERE opinion_id=? AND citation=?",
                             (keep, cite)).rowcount
            if n:
                log_change(conn, BATCH, keep, "citation.delete", cite, None,
                           authority=f"§6 merge {drop}->{keep}: remove dup's wrong/duplicate cite")
        n = conn.execute("DELETE FROM opinion_sources WHERE opinion_id=? AND source_path=?",
                         (keep, bad_src)).rowcount
        if n:
            log_change(conn, BATCH, keep, "opinion_source.delete", bad_src, None,
                       authority=f"§6 merge {drop}->{keep}: remove dup's wrong-page NW2d source")
        recompute_primary(conn, keep)
    if args.apply:
        conn.commit()
        print(f"\nApplied batch {BATCH}.")
    else:
        print("\nDRY-RUN (plans only). Re-run with --apply.")


if __name__ == "__main__":
    raise SystemExit(main())
