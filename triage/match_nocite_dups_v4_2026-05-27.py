"""Docket-match pass for the last no-cite NW2d dups (anonymized juvenile /
social-services / frequent-litigant). Same docket = same case. For each
remaining no-cite row, extract its 8-digit docket(s) and find a cited
(ND-neutral) opinion sharing one. EXACTLY ONE -> merge. The "CA"-docket
rows are ND Court of Appeals cases (cited 'YYYY ND App n', not 'YYYY ND n')
and are expected to find no ND-neutral twin -> left for per-case.

Cite guard inherent (keep is ND-neutral). Snapshot
opinions.db.bak-pre-nocite-v4-merge-2026-05-27. Dry-run default.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_provenance
from ndcourts_mcp.merge_opinions import merge_pair

BATCH = "section6-nocite-v4-merge-2026-05-27"


def _dockets(s: str):
    return set(re.findall(r"\b(20\d{6})\b", s or ""))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")

    nocite = conn.execute(
        "SELECT o.id, o.case_name, o.date_filed, o.docket_number FROM opinions o "
        "WHERE o.date_filed>='1997-01-01' AND NOT EXISTS(SELECT 1 FROM citations c "
        "WHERE c.opinion_id=o.id AND c.reporter='ND-neutral')").fetchall()

    merged = 0
    leave = []
    for o in nocite:
        ca = "CA" in (o["docket_number"] or "")
        dks = _dockets(o["docket_number"])
        if not dks:
            leave.append((o, "no 8-digit docket")); continue
        # cited (ND-neutral) opinions sharing any docket
        hits = {}
        for dk in dks:
            for c in conn.execute(
                "SELECT o2.id, o2.case_name, "
                "(SELECT citation FROM citations c WHERE c.opinion_id=o2.id AND c.reporter='ND-neutral' LIMIT 1) nd "
                "FROM opinions o2 WHERE o2.docket_number LIKE ? AND o2.id!=? "
                "AND EXISTS(SELECT 1 FROM citations c WHERE c.opinion_id=o2.id AND c.reporter='ND-neutral')",
                (f"%{dk}%", o["id"])):
                hits[c["id"]] = c
        hits = list(hits.values())
        if len(hits) == 1:
            c = hits[0]
            print(f"  merge {o['id']}->{c['id']}  {c['nd']}  {o['case_name'][:28]} -> {c['case_name'][:30]}")
            if args.apply:
                merge_pair(conn, c["id"], o["id"], c["case_name"], apply=True, batch=BATCH)
            merged += 1
        else:
            leave.append((o, f"{'COA(CA)' if ca else ''} docket twins: {len(hits)}"))

    print(f"\n  {'merged' if args.apply else 'would merge'}: {merged}   leave for per-case: {len(leave)}")
    for o, why in leave:
        print(f"    LEAVE {o['id']} {o['date_filed']} {o['docket_number'][:24]:<24} {o['case_name'][:24]:<24} | {why}")

    if args.apply and merged:
        log_provenance(conn, operation="section6_nocite_v4_merge",
                       command="python -m triage.match_nocite_dups_v4_2026-05-27 --apply",
                       rows_affected=merged,
                       notes=f"batch {BATCH}; merged {merged} no-cite NW2d dups by shared docket. "
                             f"Snapshot opinions.db.bak-pre-nocite-v4-merge-2026-05-27. "
                             f"Run align_primary_source --apply after.")
        conn.commit(); print("  committed.")
    conn.close()


if __name__ == "__main__":
    main()
