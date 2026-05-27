"""Surname-containment pass for the last no-cite NW2d dups.

For named (non-anonymized) parties the dup and its cited twin share a
distinctive surname even when 'et al.'/abbreviations drop the name-ratio
below 0.9. For each remaining no-cite row, take the lead distinctive token
(len>=5, not a stopword) and find same-year cited opinions whose name
contains it. EXACTLY ONE such twin -> confident dup -> merge into it.
0 or >1 -> leave for per-case (anonymized-juvenile / ambiguous).

Cite guard: drop lacks ND-neutral, keep has one. Snapshot
opinions.db.bak-pre-nocite-v3-merge-2026-05-27. Dry-run default.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_provenance
from ndcourts_mcp.merge_opinions import merge_pair

BATCH = "section6-nocite-v3-merge-2026-05-27"
STOP = {"state", "city", "county", "of", "the", "and", "et", "al", "inc", "llc",
        "north", "dakota", "department", "dept", "transportation", "workforce",
        "safety", "insurance", "fund", "social", "services", "service", "interest",
        "matter", "estate", "director", "commission", "board", "joint", "water",
        "resource", "resources", "human", "zone", "town", "township"}


def _toks(name: str):
    return [t for t in re.findall(r"[a-z]+", (name or "").lower())
            if len(t) >= 5 and t not in STOP]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")

    nocite = conn.execute(
        "SELECT o.id, o.case_name, o.date_filed FROM opinions o "
        "WHERE o.date_filed>='1997-01-01' AND NOT EXISTS(SELECT 1 FROM citations c "
        "WHERE c.opinion_id=o.id AND c.reporter='ND-neutral')").fetchall()

    merged = 0
    leave = []
    for o in nocite:
        toks = _toks(o["case_name"])
        if not toks:
            leave.append((o, "no distinctive token (anonymized)")); continue
        lead = toks[0]
        yr = o["date_filed"][:4]
        cands = conn.execute(
            "SELECT o2.id, o2.case_name, "
            "(SELECT citation FROM citations c WHERE c.opinion_id=o2.id AND c.reporter='ND-neutral' LIMIT 1) nd "
            "FROM opinions o2 WHERE substr(o2.date_filed,1,4)=? AND o2.id!=? "
            "AND EXISTS(SELECT 1 FROM citations c WHERE c.opinion_id=o2.id AND c.reporter='ND-neutral')",
            (yr, o["id"])).fetchall()
        hits = [c for c in cands if lead in c["case_name"].lower() and c["nd"]]
        if len(hits) == 1:
            c = hits[0]
            print(f"  merge {o['id']}->{c['id']}  {c['nd']}  {o['case_name'][:28]} -> {c['case_name'][:30]}  (lead '{lead}')")
            if args.apply:
                merge_pair(conn, c["id"], o["id"], c["case_name"], apply=True, batch=BATCH)
            merged += 1
        else:
            leave.append((o, f"lead '{lead}': {len(hits)} same-year twins"))

    print(f"\n  {'merged' if args.apply else 'would merge'}: {merged}   leave for per-case: {len(leave)}")
    for o, why in leave:
        print(f"    LEAVE {o['id']} {o['date_filed']} {o['case_name'][:36]:<36} | {why}")

    if args.apply and merged:
        log_provenance(conn, operation="section6_nocite_v3_merge",
                       command="python -m triage.match_nocite_dups_v3_2026-05-27 --apply",
                       rows_affected=merged,
                       notes=f"batch {BATCH}; merged {merged} no-cite NW2d dups by distinctive-surname "
                             f"+ same-year match. Snapshot opinions.db.bak-pre-nocite-v3-merge-2026-05-27. "
                             f"Run align_primary_source --apply after.")
        conn.commit(); print("  committed.")
    conn.close()


if __name__ == "__main__":
    main()
