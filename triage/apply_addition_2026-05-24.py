"""Apply the 38 clean ADDITION dispositions (2026-05-24).

From triage/addition-subclassified-2026-05-24.tsv:
  LOCALITY_OF / ROLE_APPOSITIVE -> apply the proposed (capacity/locality) rename
                                   (user-ratified accept buckets, 2026-05-20).
  DOCKET_METADATA / LONG_PLEADING -> keep DB (Westlaw adds only dates/pipes/full
                                     pleading recitations; the DB caption is the
                                     correct short name) -> mark state.json kept_db.
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TSV = REPO / "triage" / "addition-subclassified-2026-05-24.tsv"
STATE = REPO / "triage" / "casenames-state.json"
DB = REPO / "opinions.db"
BATCH = "fix-casenames-addition-2026-05-24"

RENAME = {"LOCALITY_OF", "ROLE_APPOSITIVE"}
KEEP = {"DOCKET_METADATA", "LONG_PLEADING"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows = list(csv.DictReader(TSV.open(), delimiter="\t"))
    state = json.loads(STATE.read_text())
    kept = state["kept_db"]
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    renames = [r for r in rows if r["sub"] in RENAME and r["proposed"] != r["db"]]
    keeps = [r for r in rows if r["sub"] in KEEP and r["oid"] not in kept]
    print(f"RENAME {len(renames)} | KEEP_DB {len(keeps)}")
    for r in renames:
        print(f"  [rename] {r['oid']:>5}  {r['db']!r} -> {r['proposed']!r}")
    for r in keeps:
        print(f"  [keep]   {r['oid']:>5}  {r['db']!r}  (rej: {r['wl'][:60]!r})")

    if args.apply:
        for r in renames:
            cur.execute("UPDATE opinions SET case_name=? WHERE id=?", (r["proposed"], int(r["oid"])))
            cur.execute("INSERT INTO changelog (batch,opinion_id,field,old_value,new_value)"
                        " VALUES (?,?, 'case_name', ?, ?)", (BATCH, int(r["oid"]), r["db"], r["proposed"]))
        for r in keeps:
            kept[r["oid"]] = {"db_name": r["db"], "source": BATCH,
                              "verdict": "KEEP_DB_ADDITION_NOISE", "volume": int(r["vol"]), "wl_raw": r["wl"]}
        conn.commit()
        STATE.write_text(json.dumps(state, indent=2))
        print(f"\nApplied {len(renames)} rename(s); added {len(keeps)} keep_db.")
        print(f"  revert renames: python -m ndcourts_mcp.cleanup revert {BATCH}")
    else:
        print("\nDry-run. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
