"""Phase-1 residue pattern sweeps (2026-05-24).

Three high-precision, user-ratified patterns mined from the 505-item pending
case-name residue. Strict gate: for the APPLY buckets, norm(DB) must be a clean
subset of norm(WL) — i.e. Westlaw only *adds* material, never changes a party
surname (those spelling-direction calls are routed to the Phase-2 .doc-body
adjudicator instead).

Buckets:
  ANNOT_KEEP   WL = DB + reporter annotation only ("(two cases)", "Nos. N-N",
               "Cr. N", "Rehearing Denied") -> keep DB, mark state.json kept_db.
  CAPACITY     WL adds a party's official-capacity appositive (", Sheriff",
               ", Treas.", ", Building Inspector") -> apply title-cased WL.
  SUFFIX       WL adds a corporate suffix ("Co., Limited", "Co., Inc.")
               -> apply title-cased WL.

Excluded: "In re ...'s Estate." multi-matter prefixes (Phase-2/TUI).
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sqlite3
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    "apply_adds_detail", REPO / "triage" / "apply_adds_detail_2026-05-20.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
smart_titlecase = _mod.smart_titlecase
clean_residue = _mod.clean_residue

CLASSIFIED = REPO / "triage" / "casenames-ambig-review-classified-2026-05-20.tsv"
STATE = REPO / "triage" / "casenames-state.json"
DB = REPO / "opinions.db"
BATCH = "fix-casenames-residue-patterns-2026-05-24"

# Each alternative consumes an optional preceding separator period so that
# stripping a trailing docket annotation also removes the "." that divided it
# from the caption (e.g. "Sheriff. Cr. 176" -> "Sheriff"), while a real
# abbreviation period with no annotation after it (e.g. "Treas.") is preserved.
ANNOT = re.compile(
    r"\s*[(\[]\s*(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+cases?\s*[)\]]"
    r"|\s*\.?\s*\bCr\.?\s*\d+[A-Za-z]?"
    r"|\s*\.?\s*\bCiv\.?\s*\d+"
    r"|\s*\.?\s*\bNos?\.\s*\d+(?:\s*[-–]\s*\d+)?"
    r"|\s*,?\s*(?:in\s+)?[A-Z]\w*\s+Judicial\s+Dist(?:rict)?\.?"
    r"|\s*\.?\s*\bRehearing\s+Denied.*$",
    re.I,
)
CAPACITY = re.compile(
    r",\s*(?:[A-Z][\w'.&-]*\s+)*"
    r"(?:Treas|Atty|Gen|Sheriff|Auditor|Com'?rs?|Commission(?:er)?|Mayor|"
    r"Sup'?t|Sup'?rs?|Clerk|Warden|Director|Examiner|Receiver|Inspector|"
    r"Superintendent|State's\s+Atty)\b\.?",
    re.I,
)
SUFFIX = re.compile(r",?\s*(?:Limited|Inc\.?|Ltd\.?|& Sons?|Corp\.?)\b", re.I)
ESTATE_PREFIX = re.compile(r"\bIn re\b.*\bEstate\b\.", re.I)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).replace("’", "'")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def strip_annot(s: str) -> str:
    prev = None
    while prev != s:
        prev = s
        s = ANNOT.sub("", s).rstrip()
    return s


def propose(wl_norm: str) -> str:
    titled = smart_titlecase(clean_residue(wl_norm))
    titled = strip_annot(titled)
    titled = re.sub(r"(\bCourt),(\s+(?:in and for|for)\b)", r"\1\2", titled)
    return re.sub(r"\s{2,}", " ", titled).strip().rstrip(",")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows = list(csv.DictReader(CLASSIFIED.open(), delimiter="\t"))
    state = json.loads(STATE.read_text())
    kept = state["kept_db"]
    conn = sqlite3.connect(DB)

    plan = []
    for r in rows:
        oid, db, wl = r["opinion_id"], r["db_name"], r["wl_norm"]
        cur = conn.execute("SELECT case_name FROM opinions WHERE id=?", (int(oid),)).fetchone()
        if not cur or oid in kept or cur[0] != db:
            continue  # already resolved / kept / edited
        ndb = norm(db)
        disp = proposed = None
        if ANNOT.search(wl) and norm(strip_annot(wl)) == ndb:
            disp = "ANNOT_KEEP"
        elif ndb in norm(wl) and ndb != norm(wl) and not ESTATE_PREFIX.search(wl):
            if CAPACITY.search(wl) and not CAPACITY.search(db):
                disp, proposed = "CAPACITY", propose(wl)
            elif SUFFIX.search(wl) and not SUFFIX.search(db):
                disp, proposed = "SUFFIX", propose(wl)
        if disp:
            plan.append(dict(oid=oid, vol=int(r["volume"]), disp=disp,
                             db=db, proposed=proposed, wl=wl))

    order = ["ANNOT_KEEP", "CAPACITY", "SUFFIX"]
    plan.sort(key=lambda p: (order.index(p["disp"]), p["vol"]))
    counts = Counter(p["disp"] for p in plan)
    print(f"Residue pattern sweep ({len(plan)} rows): "
          + ", ".join(f"{k}={counts[k]}" for k in order if counts[k]))
    print()
    for p in plan:
        print(f"[{p['disp']:<11}] oid {p['oid']:>5} v{p['vol']}")
        print(f"     DB: {p['db']}")
        print(f"     WL: {p['wl']}")
        print(f"     => {'KEEP DB' if p['disp']=='ANNOT_KEEP' else p['proposed']}")
        print()

    if args.apply:
        cur = conn.cursor()
        renamed = keeps = 0
        for p in plan:
            if p["disp"] == "ANNOT_KEEP":
                kept[p["oid"]] = {
                    "db_name": p["db"], "source": BATCH,
                    "verdict": "KEEP_DB_ANNOTATION", "volume": p["vol"],
                    "wl_raw": p["wl"],
                }
                keeps += 1
            else:
                if p["proposed"] == p["db"]:
                    continue
                cur.execute("UPDATE opinions SET case_name=? WHERE id=?",
                            (p["proposed"], int(p["oid"])))
                cur.execute(
                    "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value)"
                    " VALUES (?,?, 'case_name', ?, ?)",
                    (BATCH, int(p["oid"]), p["db"], p["proposed"]),
                )
                renamed += 1
        conn.commit()
        STATE.write_text(json.dumps(state, indent=2))
        print(f"Applied {renamed} rename(s); added {keeps} keep_db entr(ies).")
        print(f"  revert renames: python -m ndcourts_mcp.cleanup revert {BATCH}")
    else:
        print("Dry-run only. Re-run with --apply to commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
