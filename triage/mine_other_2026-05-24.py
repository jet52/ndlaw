"""Mine the clean capacity / jurisdiction adds out of the 178 OTHER residue.

The OTHER rows are all ADDITION-kind (Westlaw only adds tokens to the DB
caption — verified by the Phase-2 adjudicator). Here we bucket what is added:
  CAPACITY      a party's official-capacity appositive (", Tax Commission",
                ", State's Atty.", ", Com'r")
  JURISDICTION  a geographic jurisdiction ("Ward County Court", "of X County")
  OTHER_REMAIN  everything else -> TUI

Dry-run by default; --apply commits CAPACITY + JURISDICTION renames.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, REPO / "triage" / path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_rs = _load("residue_sweep", "sweep_residue_patterns_2026-05-24.py")
_js = _load("jsweep", "sweep_jurisdiction_2026-05-24.py")
propose = _rs.propose
CAPACITY = _rs.CAPACITY
GEO = _js.GEO

TSV = REPO / "triage" / "addition-subclassified-2026-05-24.tsv"
STATE = REPO / "triage" / "casenames-state.json"
DB = REPO / "opinions.db"
OUT = REPO / "triage" / "other-mined-2026-05-24.tsv"
BATCH = "fix-casenames-other-mined-2026-05-24"

ESTATE = re.compile(r"\bIn re\b|\bEstate\b|\bAppeal of\b", re.I)
MULTI = re.compile(r"(?<!rel)\.\s+[A-Z][\w'.& ]+\s+v\.|\bPetition of\b", re.I)
# "<County> County Court/Com'rs" jurisdiction the DB renders bare ("County Court").
JURIS_CC = re.compile(r"\b[A-Z][a-z]+\s+County\s+(?:Court|Com)", re.I)


def _fold(s: str) -> str:
    return s.replace("’", "'").replace("‘", "'")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(TSV.open(), delimiter="\t") if r["sub"] == "OTHER"]
    state = json.loads(STATE.read_text())
    kept = state["kept_db"]
    conn = sqlite3.connect(DB)

    out = []
    for r in rows:
        db, wl = r["db"], _fold(r["wl"])
        dbf = _fold(db)
        if ESTATE.search(wl) or MULTI.search(wl):
            bucket = "OTHER_REMAIN"
        elif (GEO.search(wl) and not GEO.search(dbf)) or (JURIS_CC.search(wl) and not JURIS_CC.search(dbf)):
            bucket = "JURISDICTION"
        elif CAPACITY.search(wl) and not CAPACITY.search(dbf):
            bucket = "CAPACITY"
        else:
            bucket = "OTHER_REMAIN"
        out.append(dict(oid=r["oid"], vol=r["vol"], bucket=bucket,
                        db=db, proposed=propose(wl) if bucket != "OTHER_REMAIN" else "", wl=wl))

    cols = ["oid", "vol", "bucket", "db", "proposed", "wl"]
    with OUT.open("w") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    counts = Counter(r["bucket"] for r in out)
    print(f"OTHER rows: {len(out)}  ->  {OUT.relative_to(REPO)}")
    for k in ("CAPACITY", "JURISDICTION", "OTHER_REMAIN"):
        print(f"  {k:<14} {counts[k]}")
    mineable = [r for r in out if r["bucket"] in ("CAPACITY", "JURISDICTION") and r["proposed"] != r["db"]]
    print(f"\n  mineable (clean capacity/jurisdiction adds): {len(mineable)}")
    by = defaultdict(list)
    for r in out:
        by[r["bucket"]].append(r)
    for b in ("CAPACITY", "JURISDICTION"):
        print(f"\n[{b}] ({len(by[b])})")
        for r in by[b]:
            print(f"  {r['oid']:>5} v{r['vol']}  {r['db']}")
            print(f"        => {r['proposed']}")

    if args.apply:
        cur = conn.cursor()
        n = 0
        for r in mineable:
            cur.execute("UPDATE opinions SET case_name=? WHERE id=?", (r["proposed"], int(r["oid"])))
            cur.execute("INSERT INTO changelog (batch,opinion_id,field,old_value,new_value)"
                        " VALUES (?,?, 'case_name', ?, ?)", (BATCH, int(r["oid"]), r["db"], r["proposed"]))
            n += 1
        conn.commit()
        print(f"\nApplied {n} rename(s). revert: python -m ndcourts_mcp.cleanup revert {BATCH}")
    else:
        print("\nDry-run. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
