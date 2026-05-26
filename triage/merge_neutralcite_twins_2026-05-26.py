"""Merge the 14 verified native-neutral-cite double-ingest twins.

Each is the recurring CL double-ingest: an ndcourts.gov markdown row ("X v. Y"
/ "Interest of X", correct early date, ¶-marked) + a CourtListener row ("In re X",
date_filed on the "-25th of a later month" = CL/WL processing artifact). Verified
read-only via triage/verify_neutralcite_twins_2026-05-26.py: same docket per pair,
text jaccard 0.74-0.96, and the "amended/supplemental/superseded" markers appear
SYMMETRICALLY in both rows (opinion text, not an asymmetric rehearing event).
Keep = the markdown row (merge_pair leaves text_content untouched).

NOT in this batch (handled separately):
  * 2000 ND 203 Logan v. Bush (13290/13291) — 13290's stub text is leaked from
    2000 ND 199 (State v. Gehring, oid 18359, which exists independently); the
    full real Logan is 13291. A tangle, not a clean twin.
  * 2011 ND 161, 2018 ND 140 — cite contamination (distinct cases), not dups.

Survivor captions: fuller/period style, annotations stripped (modern-dedup
caption policy; dedup never de-anonymizes confidential juvenile matters).
Two malformed survivor dockets (the neutral cite stuffed into docket) fixed
from the CL row's real docket.

Snapshot: opinions.db.bak-pre-neutralcite-twins-2026-05-26.
Row deletions NOT changelog-revertible — revert via snapshot restore.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from ndcourts_mcp.merge_opinions import merge_pair

BATCH = "section6-neutralcite-twins-2026-05-26"

# (keep, drop, canonical_name)
PAIRS = [
    (12365, 12366, "Estate of Brown"),
    (12353, 12354, "Interest of A.E."),
    (12808, 12809, "Allied Mutual Insurance Company v. Director of the "
                   "North Dakota Department of Transportation"),
    (13303, 13304, "Interest of J.S."),
    (13299, 13300, "Disciplinary Board v. Howe"),
    (13499, 13500, "Disciplinary Board v. Swanson"),
    (13497, 13498, "Disciplinary Board v. Crary"),
    (13714, 13715, "Disciplinary Board v. Lee"),
    (13931, 13932, "Interest of W.O."),
    (13938, 13939, "Disciplinary Board v. Wilkes"),
    (14391, 14392, "Disciplinary Board v. McKechnie"),
    (14685, 14686, "ND State Board of Medical Examiners v. Hsu"),
    (14888, 14889, "Interest of J.S., et al."),
    (15325, 15326, "Interest of B.B."),
]

# survivor docket fixes (keep's docket was the neutral cite; real docket from CL row)
DOCKET_FIXES = {
    12353: "Criminal No. 960079",
    12365: "Civil No. 960023",
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")
    for keep, drop, canon in PAIRS:
        plan = merge_pair(conn, keep, drop, canon, apply=args.apply, batch=BATCH)
        print(f"  {drop:>6} -> {keep:<6}  {plan['name']}")

    for kid, real_docket in DOCKET_FIXES.items():
        old = conn.execute("SELECT docket_number FROM opinions WHERE id=?",
                           (kid,)).fetchone()["docket_number"]
        print(f"  docket-fix {kid}: {old!r} -> {real_docket!r}")
        if args.apply:
            log_change(conn, BATCH, kid, "docket_number", old, real_docket,
                       authority="real docket from merged CL twin (keep row "
                                 "had the neutral cite stuffed in docket field)")
            conn.execute("UPDATE opinions SET docket_number=? WHERE id=?",
                         (real_docket, kid))

    if args.apply:
        log_provenance(
            conn, operation="section6_neutralcite_twins_merge",
            command="python -m triage.merge_neutralcite_twins_2026-05-26 --apply",
            rows_affected=len(PAIRS),
            notes=(f"batch {BATCH}; merged 14 verified native-neutral-cite CL "
                   f"double-ingest twins (keep markdown row) + 2 docket fixes. "
                   f"Snapshot opinions.db.bak-pre-neutralcite-twins-2026-05-26; "
                   f"row deletions not changelog-revertible."))
        conn.commit()
        print("  committed.")
    conn.close()


if __name__ == "__main__":
    main()
