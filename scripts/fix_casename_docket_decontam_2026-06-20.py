"""Decontaminate 11 1997-cohort opinions whose case_name (and cite-shaped
docket placeholder) did not match the opinion text.

Found by `refs_diff selfcheck` (DB self-consistency), narrowed from 25 to 11 by
cross-checking the court's opinion-report spreadsheet (which confirmed the 14
"Interest of X (CONFIDENTIAL)" cases were correctly named — classifier false
positives on anonymized captions). Each correct name is triple-sourced: the
court's own published caption in the opinion body, AND CourtListener, AND the
opinion's in-body neutral cite matching its label. Dockets are the real
court file numbers recovered from the opinion body (8-digit 19YYNNNN form,
matching the reverted `docket-cite-shaped-2026-06-10` values); Herrick's
consolidated range is comma-joined per the established convention.

Revertible via `python -m ndcourts_mcp.cleanup revert <batch>`.
"""
from __future__ import annotations
import argparse, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.db import get_connection, log_change  # noqa: E402

BATCH = "casename-docket-decontam-1997-2026-06-20"

# oid, neutral, correct case_name, correct docket, authority
FIXES = [
    (12346, "1997 ND 16",  "Frafjord v. Ell",                                       "19960097", "caption+CL 1997 ND 16"),
    (12388, "1997 ND 30",  "Borr v. McKenzie County Public School District No. 1",   "19960157", "caption+CL 1997 ND 30"),
    (12389, "1997 ND 33",  "Huesers v. Huesers",                                    "19960218", "caption+CL+Westlaw 1997 ND 33"),
    (12392, "1997 ND 40",  "Sickler v. Kirkwood",                                   "19960226", "caption+CL 1997 ND 40"),
    (12397, "1997 ND 59",  "Austin v. Towne",                                       "19960215", "caption+CL 1997 ND 59"),
    (12398, "1997 ND 50",  "Owan v. Owan",                                          "19960235", "caption+CL 1997 ND 50"),
    (12403, "1997 ND 62",  "Sumra v. Sumra",                                        "19960129", "caption+CL 1997 ND 62"),
    (12415, "1997 ND 72",  "Mosbrucker v. Mosbrucker",                              "19960329", "caption+CL 1997 ND 72"),
    (12418, "1997 ND 71",  "State v. Breiner",                                      "19960298", "caption+CL 1997 ND 71"),
    (12486, "1997 ND 138", "Reimche v. Reimche",                                    "19960239", "caption+CL 1997 ND 138"),
    (12500, "1997 ND 155", "State v. Herrick",                  "19970019, 19970020, 19970021", "caption+CL 1997 ND 155 (consolidated)"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--db", default="opinions.db")
    args = ap.parse_args()
    conn = get_connection(Path(args.db)); conn.row_factory = sqlite3.Row
    for oid, cite, name, docket, basis in FIXES:
        cur = conn.execute("SELECT case_name, docket_number FROM opinions WHERE id=?", (oid,)).fetchone()
        print(f"[{cite:<11}] oid {oid}")
        print(f"    case_name : {cur['case_name']!r}  ->  {name!r}")
        print(f"    docket    : {cur['docket_number']!r}  ->  {docket!r}")
        if args.apply:
            if cur["case_name"] != name:
                log_change(conn, BATCH, oid, "case_name", cur["case_name"], name, authority=basis)
            if cur["docket_number"] != docket:
                log_change(conn, BATCH, oid, "docket_number", cur["docket_number"], docket, authority=basis)
            conn.execute("UPDATE opinions SET case_name=?, docket_number=? WHERE id=?", (name, docket, oid))
    if args.apply:
        conn.commit(); print(f"\nAPPLIED {len(FIXES)} opinions (batch {BATCH}).")
    else:
        print(f"\nDRY-RUN ({len(FIXES)} opinions). Re-run with --apply.")
    conn.close()


if __name__ == "__main__":
    main()
