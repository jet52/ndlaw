"""Apply ONLY the 23 reporter-window-validated CL-error holds (verified 2026-05-25).

Each was confirmed by reading the opinion's own source: the court-source filing date
falls inside the N.W.2d volume window (independent, from volume-mates' CL dates) while
CL's date_filed is a later rehearing/denial/mandate date. The other 70 holds KEEP CL
(court-source date there is an earlier proceeding date or artifact). Drift-guarded.
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change  # noqa: E402

BATCH = "fix-date-holds-clerror-verified-2026-05-25"
REC = REPO / "triage/date-holds-recommendation-2026-05-25.tsv"
VERIFIED = {7793, 6945, 7196, 7337, 7665, 7714, 7807, 7827, 7882, 8359, 8440, 8465,
            8607, 8638, 8958, 9220, 9722, 9876, 10098, 10196, 10443, 8454, 8677}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)

    rows = []
    with open(REC) as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            oid, action, new_date, cls, cl, court, src, era, name = p[:9]
            if int(oid) in VERIFIED:
                rows.append((int(oid), cl, court, src, name))
    assert len(rows) == len(VERIFIED), f"expected {len(VERIFIED)}, matched {len(rows)}"

    changed = skipped = 0
    for oid, old, new, src, name in rows:
        cur = conn.execute("SELECT date_filed FROM opinions WHERE id=?", (oid,)).fetchone()
        if cur["date_filed"] != old:
            print(f"  SKIP oid {oid}: db={cur['date_filed']} != expected {old}")
            skipped += 1
            continue
        print(f"  oid {oid:>6}  {old} -> {new}  ({name})")
        if args.apply:
            conn.execute("UPDATE opinions SET date_filed=? WHERE id=?", (new, oid))
            log_change(conn, BATCH, oid, "date_filed", old, new,
                       authority=f"CL recorded a later rehearing/denial date; true filing date "
                                 f"= {src} source, reporter-window-validated + source-read 2026-05-25")
            changed += 1
    if args.apply:
        conn.commit()
        print(f"\nApplied {changed} ({skipped} skipped); batch {BATCH}.")
    else:
        print(f"\nDRY-RUN: {len(rows)} verified rows ({skipped} would skip). Re-run with --apply.")


if __name__ == "__main__":
    raise SystemExit(main())
