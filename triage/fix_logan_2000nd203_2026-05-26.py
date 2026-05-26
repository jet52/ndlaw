"""Resolve the last neutral_cite_uniqueness collision: 2000 ND 203 Logan v. Bush.

13291 = the full real opinion (Maring J., divorce/child-support; body: "December 7,
  2000. Opinion Denying Rehearing January 30, 2001"). Its date_filed 2001-01-30 is
  the rehearing-denial date (CL artifact); the true filing date is 2000-12-07.
13290 = a 1,689-char stub whose text is LEAKED from 2000 ND 199 (State v. Gehring,
  which exists independently as oid 18359) but carries Logan's cite/docket.

Keep 13291 (full text), merge 13290 in, correct the survivor date to 2000-12-07.
Snapshot: opinions.db.bak-pre-logan-2026-05-26. Row deletion not changelog-revertible.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from ndcourts_mcp.merge_opinions import merge_pair

BATCH = "section6-logan-2000nd203-2026-05-26"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")
    plan = merge_pair(conn, 13291, 13290, "Logan v. Bush",
                      apply=args.apply, batch=BATCH)
    print(f"  merge 13290 -> 13291  {plan['name']}; {plan['author']}")
    if args.apply:
        old = conn.execute("SELECT date_filed FROM opinions WHERE id=13291").fetchone()["date_filed"]
        log_change(conn, BATCH, 13291, "date_filed", old, "2000-12-07",
                   authority="opinion body: 'December 7, 2000' filing; "
                             "2001-01-30 was the rehearing-denial date")
        conn.execute("UPDATE opinions SET date_filed='2000-12-07' WHERE id=13291")
        print(f"  date-fix 13291: {old} -> 2000-12-07")
        log_provenance(
            conn, operation="section6_logan_2000nd203",
            command="python -m triage.fix_logan_2000nd203_2026-05-26 --apply",
            rows_affected=1,
            notes=(f"batch {BATCH}; merged leaked-text stub 13290 into full Logan "
                   f"v. Bush 13291 (2000 ND 203), date 2001-01-30->2000-12-07. "
                   f"Snapshot opinions.db.bak-pre-logan-2026-05-26."))
        conn.commit()
        print("  committed.")
    conn.close()


if __name__ == "__main__":
    main()
