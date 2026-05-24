"""Bulk-mark the EQUIV residue rows as keep_db (2026-05-24).

EQUIV = the Phase-2 adjudicator found DB and Westlaw captions party-identical
after normalization (only punctuation/case/abbreviation/apostrophe/ligature
differences). The DB caption is correct as-is, so mark these kept_db (verdict
KEEP_DB_EQUIV) to clear them from the per-volume TUI queue. No case_name change,
no DB write — only triage/casenames-state.json (git-reversible).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from pathlib import Path

# "County of X" (DB) vs West "X County" — a style choice the user prefers to
# adopt toward West, not keep. Held out of the cosmetic keep sweep.
COUNTY_OF = re.compile(r"\bCounty of [A-Z]")

REPO = Path(__file__).resolve().parent.parent
ADJ = REPO / "triage" / "residue-adjudication-2026-05-24.tsv"
STATE = REPO / "triage" / "casenames-state.json"
DB = REPO / "opinions.db"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(ADJ.open(), delimiter="\t") if r["kind"] == "EQUIV"]
    state = json.loads(STATE.read_text())
    kept = state["kept_db"]
    conn = sqlite3.connect(DB)

    todo, skipped = [], 0
    for r in rows:
        oid = r["oid"]
        cur = conn.execute("SELECT case_name FROM opinions WHERE id=?", (int(oid),)).fetchone()
        # still pending: row exists, current name still == the DB name we saw, not already kept
        if not cur or oid in kept or cur[0] != r["db"]:
            skipped += 1
            continue
        # "County of X" rows: user chose 2026-05-24 to KEEP the DB form
        # (the West "X County" preference was situational, not a blanket rule),
        # so they are kept like every other cosmetic EQUIV row.
        todo.append(r)

    print(f"EQUIV rows: {len(rows)}  |  to mark keep_db: {len(todo)}  |  skipped(already resolved): {skipped}")
    for r in todo[:8]:
        print(f"  {r['oid']:>5} v{r['vol']}  {r['db']!r}  ~  {r['wl']!r}")
    if len(todo) > 8:
        print(f"  ... (+{len(todo) - 8} more)")

    if args.apply:
        for r in todo:
            kept[r["oid"]] = {"db_name": r["db"], "source": "keep-equiv-2026-05-24",
                              "verdict": "KEEP_DB_EQUIV", "volume": int(r["vol"]), "wl_raw": r["wl"]}
        STATE.write_text(json.dumps(state, indent=2))
        print(f"\nMarked {len(todo)} keep_db. (revert: remove KEEP_DB_EQUIV entries from {STATE.name}, or git checkout)")
    else:
        print("\nDry-run. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
