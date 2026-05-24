"""Apply the two data-quality corrections surfaced while reading the bound N.D.
volumes for §10 cluster verification (see CHANGELOG fix-section10-cluster-order-
ndverify-2026-05-24 flags). Authoritative source = the bound N.D. Reports scans.

  - 9 N.D. 615 date_filed: bound shows distinct filing dates, DB had both 12-08.
      5747 Emmons County v. Wilson  : 1900-12-08 -> 1900-11-13  (Nov-13 Emmons block)
      5774 Douglas v. Glazier       : 1900-12-08 -> 1900-11-24
  - 44 N.D. 250 N.W. cite: bound shows Nelson at 173 N.W. 475 (Olson at 474).
      2169 Nelson v. Middlewest Grain Co.: 173 N.W. 474 -> 173 N.W. 475
        (2169 was mis-set to 474 by ingest-emmons-additions; the 472/473/474
         run belongs to the page-247 companions, not this page-250 Nelson.)

NOTE: the date changes reorder the 1900 synthetic sequence — run
section10_resequence_2026-05-24.py afterward to bring YYYY ND nnn back into order.

Modes: --apply (default --dry-run). Revertible via changelog batch.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change  # noqa: E402

BATCH = "fix-bound-discrepancies-2026-05-24"
AUTH = "bound N.D. Reports scan: vol 9 p.615 (pdf 725); vol 44 p.250 (pdf 267)"

# (oid, field, old, new) — date_filed on opinions; citation on a citations row.
DATE_FIXES = [
    (5747, "1900-12-08", "1900-11-13"),
    (5774, "1900-12-08", "1900-11-24"),
]
CITE_FIXES = [
    (2169, "173 N.W. 474", "173 N.W. 475"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)

    print("date_filed:")
    for oid, old, new in DATE_FIXES:
        cur = conn.execute("SELECT date_filed FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        ok = "ok" if cur == old else f"!! DB has {cur!r}, expected {old!r}"
        print(f"  oid {oid}: {cur} -> {new}  [{ok}]")
    print("citation:")
    for oid, old, new in CITE_FIXES:
        row = conn.execute(
            "SELECT id, citation FROM citations WHERE opinion_id=? AND citation=?",
            (oid, old)).fetchone()
        ok = "ok" if row else f"!! no citations row {old!r} on oid {oid}"
        print(f"  oid {oid}: {old} -> {new}  [{ok}]")

    if not args.apply:
        print("\nDRY-RUN. re-run with --apply.")
        return 0

    for oid, old, new in DATE_FIXES:
        cur = conn.execute("SELECT date_filed FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        if cur != old:
            raise SystemExit(f"oid {oid}: date guard failed ({cur!r} != {old!r})")
        conn.execute("UPDATE opinions SET date_filed=? WHERE id=?", (new, oid))
        log_change(conn, BATCH, oid, "date_filed", old, new, authority=AUTH)
    for oid, old, new in CITE_FIXES:
        row = conn.execute(
            "SELECT id FROM citations WHERE opinion_id=? AND citation=?",
            (oid, old)).fetchone()
        if not row:
            raise SystemExit(f"oid {oid}: cite guard failed (no {old!r})")
        conn.execute("UPDATE citations SET citation=? WHERE id=?", (new, row["id"]))
        log_change(conn, BATCH, oid, "citation", old, new, authority=AUTH)
    conn.commit()
    print(f"\nApplied {len(DATE_FIXES)} date + {len(CITE_FIXES)} cite fix; batch {BATCH}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
