"""Merge the 18 shared-page 'Re X' / 'In the Matter of X' duplicate twins (2026-05-24).

Each pair shares the same N.D. page, N.W. page, and DOCKET number: one row
captions the case as "X v. Y" (Westlaw-bound source), the other as "Re X" /
"In the Matter of ..." (CL re-ingest). Text-read 2026-05-24 confirmed all 18
are one opinion double-ingested (the "Re X" full caption names the same parties
+ same docket). Keep the Westlaw-bound "X v. Y" row, drop the CL twin.

Distinct from the Emmons per curiams (different defendants / separate suits) —
these are the SAME case.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection  # noqa: E402
from ndcourts_mcp.merge_opinions import merge_pair  # noqa: E402

BATCH = "section6-rex-twins-2026-05-24"
# (keep = Westlaw-bound "X v. Y", drop = CL "Re X" twin)
PAIRS = [(2994, 2995), (3269, 3270), (3588, 3589), (3685, 3686), (4110, 4111),
         (4205, 4206), (4271, 4272), (4286, 4287), (4448, 4449), (4894, 4895),
         (5030, 5031), (5038, 5039), (7177, 7178), (7520, 7521), (7646, 7647),
         (8814, 8815), (9805, 9806), (9816, 9817)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)

    for keep, drop in PAIRS:
        kn = conn.execute("SELECT case_name FROM opinions WHERE id=?", (keep,)).fetchone()
        dn = conn.execute("SELECT case_name FROM opinions WHERE id=?", (drop,)).fetchone()
        if not kn or not dn:
            print(f"  SKIP {keep}/{drop}: missing row")
            continue
        # canonical = keep's existing (proper party) caption; no rename.
        plan = merge_pair(conn, keep, drop, kn[0], apply=args.apply, batch=BATCH)
        print(f"  {'merged' if args.apply else 'would merge'} drop {drop} {dn[0]!r} -> keep {keep} {kn[0]!r}")

    if args.apply:
        conn.commit()
        print(f"\nApplied {len(PAIRS)} merges. revert: python -m ndcourts_mcp.cleanup revert {BATCH}")
    else:
        print(f"\nDry-run ({len(PAIRS)} pairs). Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
