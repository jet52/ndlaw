"""Dry-run / apply the 'keep full West caption' jurisdiction policy (2026-05-24).

Policy (user-ratified 2026-05-24): for governmental respondents where Westlaw
adds a geographic jurisdiction ("v. District Court of Ward County",
"Board of Com'rs of Dunn County"), the full West caption is authoritative.
Strip only reporter annotations: "(N cases)", "Cr./Civ. NNN", judicial-district
tails. Exclude Group 3 (person + official capacity) and Group 4 (entity proper
names) — those were correctly applied. Defer multi-case / garbage captions.

Dispositions:
  REVERSE_KEPT   row currently bare (TUI keep_db) -> apply West, drop keep_db
  STRIP_APPLIED  row already has West caption but carries an annotation -> clean
  APPLY_PENDING  pending row, clean single-case -> apply West
  DEFER          multi-case / garbage WL caption -> leave for TUI
  SKIP_OK        already-applied, no annotation -> no change
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "apply_adds_detail",
    Path(__file__).resolve().parent / "apply_adds_detail_2026-05-20.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
smart_titlecase = _mod.smart_titlecase
clean_residue = _mod.clean_residue

CLASSIFIED = REPO / "triage" / "casenames-ambig-review-classified-2026-05-20.tsv"
STATE = REPO / "triage" / "casenames-state.json"
DB = REPO / "opinions.db"
BATCH = "fix-casenames-jurisdiction-2026-05-24"

GEO = re.compile(
    r"\bIN AND FOR\b|\b(?:OF|FOR)\s+[A-Z][\w.'-]*\s+COUNTY\b|\bOF\s+CITY OF\b|"
    r"\bJUDICIAL DIST|\bSCHOOL DIST|\bTOWNSHIP\b|"
    r"\bOF\s+(?:VILLAGE|TOWN|CITY|PARK DISTRICT|TP\.)\b",
    re.I,
)
COURT = re.compile(r"\b(?:DISTRICT|COUNTY|MAGISTRATE'?S|POLICE MAGISTRATE'?S)\s+COURT\b", re.I)
# Group 3: person + official capacity appositive ", <Title> of <County>"
CAPACITY = re.compile(
    r",\s+(?:[A-Z][\w'.&-]*\s+)*"
    r"(?:Sheriff|Treasurer|Auditor|Superintendent|Drain\s+Com'?rs?|"
    r"Com'?r|Commissioner|Atty\.?\s*Gen|Sup'?rs?|President of)",
    re.I,
)
# Group 4: "of <County>" is part of a proper Bank/Insurance/Co. name
ENTITY = re.compile(r"\b(?:Bank|Ins\.?|Insurance|Co\.|Company)\b.*\bOF\s+[A-Z]", re.I)

# Annotation tails to strip from a kept caption.
ANNOT = re.compile(
    r"\s*[(\[]\s*(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+cases?\s*[)\]]"
    r"|\s*\bCr\.?\s*\d+|\s*\bCiv\.?\s*\d+"
    r"|\s*,?\s*(?:in\s+)?[A-Z][\w]*\s+Judicial\s+Dist(?:rict)?\.?"
    r"|\s*,?\s*(?:Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\s+District\b",
    re.I,
)

# Multi-case / garbage signatures -> defer. The negative lookbehind keeps
# "ex rel. <Name> v." from being mistaken for a second case.
MULTICASE = re.compile(
    r"(?<!rel)\.\s+[A-Z][\w'.& ]+\s+v\.|"  # a genuine second "X v." after a period
    r"\bPetition of\b|"
    r"\bv\.\s*$|"                            # trailing dangling "v."
    r"as\s+Attorney\s+General",               # the 11544 paragraph-caption monster
    re.I,
)
REL = re.compile(r"\bex\.?\s*rel\b", re.I)


def strip_annot(s: str) -> str:
    prev = None
    while prev != s:
        prev = s
        s = ANNOT.sub("", s).rstrip(" ,")
    return s


def propose(wl_norm: str) -> str:
    cleaned = clean_residue(wl_norm)
    titled = smart_titlecase(cleaned)
    titled = strip_annot(titled)
    # Drop a comma left dangling after "Court" when a mid-caption judicial-dist
    # phrase was stripped (e.g. "District Court, in and for Pierce County").
    titled = re.sub(r"(\bCourt),(\s+(?:in and for|for)\b)", r"\1\2", titled)
    titled = re.sub(r"\s{2,}", " ", titled).strip().rstrip(",")
    return titled


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
        wl, db, oid = r["wl_norm"], r["db_name"], r["opinion_id"]
        if not GEO.search(wl) or GEO.search(db):
            continue
        # Exclude Groups 3 & 4 (legit detail already applied).
        if CAPACITY.search(wl) and not COURT.search(wl):
            continue
        if ENTITY.search(wl):
            continue
        cur = conn.execute("SELECT case_name FROM opinions WHERE id=?", (int(oid),)).fetchone()
        curname = cur[0] if cur else None
        is_kept = oid in kept

        proposed = propose(wl)
        # Relator-loss guard: never reverse a row whose DB caption preserves an
        # "ex rel." relator that the West caption drops (KEEP_DB_HAS_REL rows).
        if REL.search(db) and not REL.search(proposed):
            continue
        defer = bool(MULTICASE.search(wl)) or len(proposed) > 90
        if defer:
            disp = "DEFER"
        elif is_kept:
            disp = "REVERSE_KEPT"
        elif curname != db:
            disp = "STRIP_APPLIED" if curname != proposed else "SKIP_OK"
        else:
            disp = "APPLY_PENDING"
        plan.append(dict(oid=oid, vol=int(r["volume"]), disp=disp,
                         db=db, cur=curname, proposed=proposed, wl=wl))

    order = ["REVERSE_KEPT", "APPLY_PENDING", "STRIP_APPLIED", "DEFER", "SKIP_OK"]
    plan.sort(key=lambda p: (order.index(p["disp"]), p["vol"]))
    counts = Counter(p["disp"] for p in plan)
    print(f"Jurisdiction sweep plan ({sum(counts.values())} rows): "
          + ", ".join(f"{k}={counts[k]}" for k in order if counts[k]))
    print()
    for p in plan:
        if p["disp"] == "SKIP_OK":
            continue
        print(f"[{p['disp']:<14}] oid {p['oid']:>5} v{p['vol']}")
        base = p["cur"] if p["disp"] == "STRIP_APPLIED" else p["db"]
        print(f"     from: {base}")
        if p["disp"] != "DEFER":
            print(f"       to: {p['proposed']}")
        else:
            print(f"       wl: {p['wl'][:120]}")
        print()

    if args.apply:
        cur = conn.cursor()
        applied = 0
        unkept = 0
        for p in plan:
            if p["disp"] in ("DEFER", "SKIP_OK"):
                continue
            base = p["cur"] if p["disp"] == "STRIP_APPLIED" else p["db"]
            if base == p["proposed"]:
                continue
            cur.execute("UPDATE opinions SET case_name=? WHERE id=?",
                        (p["proposed"], int(p["oid"])))
            cur.execute(
                "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value)"
                " VALUES (?,?, 'case_name', ?, ?)",
                (BATCH, int(p["oid"]), base, p["proposed"]),
            )
            applied += 1
            if p["disp"] == "REVERSE_KEPT" and p["oid"] in kept:
                del kept[p["oid"]]
                unkept += 1
        conn.commit()
        STATE.write_text(json.dumps(state, indent=2))
        print(f"Applied {applied} case_name update(s); removed {unkept} keep_db entr(ies).")
        print(f"  revert: python -m ndcourts_mcp.cleanup revert {BATCH}")
    else:
        print("Dry-run only. Re-run with --apply to commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
