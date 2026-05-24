"""§10 cluster-order fix (round 2) — N.D.-bound-volume verification.

Verified the on-page publication order for every shared-page cluster that falls
in an on-disk bound N.D. Reports volume (vols 9, 19, 20, 34, 44) by reading the
bound scan. Most matched the provisional order; two did not and are corrected
here. Same within-cluster-permutation mechanism as
fix_section10_cluster_order_2026-05-24.py (each cluster keeps its number set;
only the oid->number mapping changes).

  - 9 N.D. 615 (vol 9 pdf 725): Emmons County v. Wilson (top) then Douglas v.
    Glazier — provisional had Douglas first (NW 552 < 1119). True order Wilson→Douglas.
  - 44 N.D. 250 (vol 44 pdf 267): N. M. Nelson v. Middlewest Grain (top) then
    Henry Olson v. Middlewest Grain — provisional had Olson first (DB lists both at
    173 N.W. 474, oid tiebreak). N.D. Reports order (Nelson→Olson) governs the ND
    synthetic cite per the reporter-order guard.

Clusters verified CORRECT (no change): 19 N.D. 57, 20 N.D. 370/372/412, 34 N.D. 601.

Modes: --apply (default --dry-run). Revertible via changelog (old cite stored).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change  # noqa: E402

BATCH = "fix-section10-cluster-order-ndverify-2026-05-24"
SYNTH = "ND-neutral-synthetic"

# oids in TRUE published on-page order (top to bottom).
ORDERED_CLUSTERS = [
    [5747, 5774],   # 9 N.D. 615: Wilson, Douglas
    [2169, 2167],   # 44 N.D. 250: Nelson, Olson
]
AUTHORITY = "N.D. bound order: vol 9 p.615 (pdf 725); vol 44 p.250 (pdf 267)"


def synth_cite(conn, oid: int) -> tuple[int, str]:
    rows = conn.execute(
        "SELECT id, citation FROM citations WHERE opinion_id=? AND reporter=?",
        (oid, SYNTH),
    ).fetchall()
    if len(rows) != 1:
        raise SystemExit(f"oid {oid}: expected 1 synthetic cite, found {len(rows)}")
    return rows[0]["id"], rows[0]["citation"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)

    plan = []  # (cite_row_id, oid, old_cite, new_cite)
    n_changed = 0
    for cluster in ORDERED_CLUSTERS:
        current = [synth_cite(conn, oid) for oid in cluster]  # in true order
        numbers = sorted((c for _, c in current),
                         key=lambda s: int(s.rsplit(" ", 1)[1]))
        years = {c.rsplit(" ", 2)[0] for _, c in current}
        if len(years) != 1:
            raise SystemExit(f"cluster {cluster}: mixed years {years}")
        for oid, (row_id, old_cite), new_cite in zip(cluster, current, numbers):
            tag = "  (same)" if old_cite == new_cite else "  <-- CHANGE"
            print(f"  oid {oid:>6}  {old_cite:>11} -> {new_cite:<11}{tag}")
            if old_cite != new_cite:
                n_changed += 1
            plan.append((row_id, oid, old_cite, new_cite))
        print()

    print(f"{'APPLY' if args.apply else 'DRY-RUN'}: {n_changed} cite strings change "
          f"across {len(ORDERED_CLUSTERS)} clusters.")
    if not args.apply:
        print("re-run with --apply to write.")
        return 0

    for row_id, _oid, _old, _new in plan:
        conn.execute("UPDATE citations SET citation = citation || '#tmp' WHERE id=?",
                     (row_id,))
    for row_id, oid, old_cite, new_cite in plan:
        conn.execute("UPDATE citations SET citation=? WHERE id=?", (new_cite, row_id))
        if old_cite != new_cite:
            log_change(conn, BATCH, oid, "citation_synthetic_order",
                       old_cite, new_cite, authority=AUTHORITY)
    conn.commit()
    print(f"Applied. Logged {n_changed} changes to batch {BATCH}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
