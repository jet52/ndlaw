"""Widened matcher + merger for the remaining post-1997 no-neutral-cite dups.

The first pass keyed on a narrow date window; some real dups are off by months
(the NW2d 'memorandum decisions' page carries a later publication date than the
opinion). This pass searches SAME-YEAR cited opinions and scores by best of
normalized-name ratio / text jaccard. HIGH (name>=0.9 or jaccard>=0.6) is
merged into the cited twin (drop=no-cite NW2d row); the rest are reported for
per-case review (anonymized-juvenile twins, ambiguous COA, mismatches).

Cite guard (essential): drop must lack an ND-neutral cite, keep must have one.
Snapshot opinions.db.bak-pre-nocite-v2-merge-2026-05-27. Dry-run default.
"""
from __future__ import annotations

import argparse
import re
from difflib import SequenceMatcher
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_provenance
from ndcourts_mcp.merge_opinions import merge_pair
from ndcourts_mcp.multisource_diff import jaccard, normalize_words, shingles

BATCH = "section6-nocite-v2-merge-2026-05-27"


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")

    nocite = conn.execute(
        "SELECT o.id, o.case_name, o.date_filed, o.text_content "
        "FROM opinions o WHERE o.date_filed>='1997-01-01' "
        "AND NOT EXISTS(SELECT 1 FROM citations c WHERE c.opinion_id=o.id "
        "AND c.reporter='ND-neutral')").fetchall()

    out = ["status\tdrop\tdate\tdrop_name\tkeep\tkeep_cite\tkeep_name\tnr\tjac"]
    high = []
    review = 0
    for o in nocite:
        yr = o["date_filed"][:4]
        cands = conn.execute(
            "SELECT o2.id, o2.case_name, o2.text_content, "
            "(SELECT citation FROM citations c WHERE c.opinion_id=o2.id AND c.reporter='ND-neutral' LIMIT 1) nd "
            "FROM opinions o2 WHERE substr(o2.date_filed,1,4)=? AND o2.id!=? "
            "AND EXISTS(SELECT 1 FROM citations c WHERE c.opinion_id=o2.id AND c.reporter='ND-neutral')",
            (yr, o["id"])).fetchall()
        kn = _norm(o["case_name"])
        scored = sorted(cands, key=lambda c: SequenceMatcher(None, kn, _norm(c["case_name"])).ratio(), reverse=True)[:5]
        best = None
        for c in scored:
            nr = SequenceMatcher(None, kn, _norm(c["case_name"])).ratio()
            jac = jaccard(shingles(normalize_words(o["text_content"] or "")),
                          shingles(normalize_words(c["text_content"] or "")))
            if best is None or max(nr, jac) > max(best[1], best[2]):
                best = (c, nr, jac)
        if not best:
            out.append(f"NOMATCH\t{o['id']}\t{o['date_filed']}\t{o['case_name'][:32]}\t\t\t\t\t"); review += 1; continue
        c, nr, jac = best
        if (nr >= 0.9 or jac >= 0.6) and c["nd"] is not None:
            high.append((o["id"], c["id"], c["case_name"], c["nd"], nr, jac))
            out.append(f"HIGH\t{o['id']}\t{o['date_filed']}\t{o['case_name'][:32]}\t{c['id']}\t{c['nd']}\t{c['case_name'][:32]}\t{nr:.2f}\t{jac:.2f}")
        else:
            review += 1
            out.append(f"REVIEW\t{o['id']}\t{o['date_filed']}\t{o['case_name'][:32]}\t{c['id']}\t{c['nd']}\t{c['case_name'][:32]}\t{nr:.2f}\t{jac:.2f}")

    Path("triage/nocite-dup-match-v2-2026-05-27.tsv").write_text("\n".join(out) + "\n")
    print(f"  HIGH (mergeable): {len(high)}   REVIEW/NOMATCH (per-case): {review}")
    for drop, keep, kname, kcite, nr, jac in high:
        print(f"    {drop}->{keep}  {kcite}  {kname[:30]}  (nr={nr:.2f} jac={jac:.2f})")
        if args.apply:
            kd = conn.execute("SELECT case_name FROM opinions WHERE id=?", (keep,)).fetchone()
            merge_pair(conn, keep, drop, kd["case_name"], apply=True, batch=BATCH)

    if args.apply and high:
        log_provenance(conn, operation="section6_nocite_v2_merge",
                       command="python -m triage.match_nocite_dups_v2_2026-05-27 --apply",
                       rows_affected=len(high),
                       notes=f"batch {BATCH}; merged {len(high)} same-year no-cite NW2d dups. "
                             f"Snapshot opinions.db.bak-pre-nocite-v2-merge-2026-05-27. "
                             f"Run align_primary_source --apply after.")
        conn.commit(); print("  committed.")
    conn.close()


if __name__ == "__main__":
    main()
