"""Apply the ADOPT rows from date-holds-recommendation-2026-05-25.tsv.

Adopts the court source's filing date (court date governs, ratified 2026-05-24) for
the 69 reviewed >31d holds classified ADOPT. KEEP/FLAG rows are untouched.
Skips any row whose current DB date no longer matches the expected CL date (drift
guard). Re-run the §10 resequencer afterward (dates drive the synthetic order).
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change  # noqa: E402

BATCH = "fix-date-holds-adopt-court-2026-05-25"
REC = REPO / "triage/date-holds-recommendation-2026-05-25.tsv"


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
            if action == "ADOPT":
                rows.append((int(oid), cl, new_date, src, name))

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
                       authority=f"court filing date governs ({src}); >31d hold reviewed 2026-05-25")
            changed += 1
    if args.apply:
        conn.commit()
        print(f"\nApplied {changed} ({skipped} skipped); batch {BATCH}.")
    else:
        print(f"\nDRY-RUN: {len(rows)} ADOPT rows ({skipped} would skip). Re-run with --apply.")


if __name__ == "__main__":
    raise SystemExit(main())
