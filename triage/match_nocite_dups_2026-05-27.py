"""DRY-RUN matcher for the post-1997 no-neutral-cite NW2d duplicates.

These rows have no neutral cite and never collided (neutral_cite_uniqueness=0),
but the per-year sequence is gap-free, so each is a duplicate of a cited
opinion (the markdown twin that carries the YYYY ND n cite). This finds the
twin for each so a merge_pair pass can fold the NW2d row in (which also adds
the N.W.2d parallel to the survivor). READ-ONLY — proposes, does not merge.

Match: same date_filed (then +/-3 days), best by normalized-name ratio +
text jaccard. Confidence HIGH (name>=.9 or jaccard>=.6), MEDIUM, REVIEW.
"""
from __future__ import annotations

import argparse
import re
from datetime import date, timedelta
from difflib import SequenceMatcher
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection
from ndcourts_mcp.multisource_diff import jaccard, normalize_words, shingles

BATCH = "nocite-dup-match-2026-05-27"


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = ap.parse_args()
    conn = get_connection(args.db)

    nocite = conn.execute(
        "SELECT o.id, o.case_name, o.date_filed, o.text_content "
        "FROM opinions o WHERE o.date_filed>='1997-01-01' "
        "AND NOT EXISTS(SELECT 1 FROM citations c WHERE c.opinion_id=o.id "
        "AND c.reporter='ND-neutral')").fetchall()

    out = ["confidence\tnocite_oid\tnocite_date\tnocite_name\tkeep_oid\tkeep_cite\tkeep_name\tname_ratio\tjaccard"]
    tally = {"HIGH": 0, "MEDIUM": 0, "REVIEW": 0, "NOMATCH": 0}
    for o in nocite:
        d0 = date.fromisoformat(o["date_filed"])
        best = None
        for delta in (0, 1, 2, 3):
            days = {d0} if delta == 0 else {d0 + timedelta(delta), d0 - timedelta(delta)}
            cands = []
            for dd in days:
                cands += conn.execute(
                    "SELECT o2.id, o2.case_name, o2.text_content, "
                    "(SELECT citation FROM citations c WHERE c.opinion_id=o2.id "
                    " AND c.reporter='ND-neutral' LIMIT 1) nd "
                    "FROM opinions o2 WHERE o2.date_filed=? AND o2.id!=? "
                    "AND EXISTS(SELECT 1 FROM citations c WHERE c.opinion_id=o2.id "
                    "AND c.reporter='ND-neutral')", (dd.isoformat(), o["id"])).fetchall()
            for c in cands:
                nr = SequenceMatcher(None, _norm(o["case_name"]), _norm(c["case_name"])).ratio()
                jac = jaccard(shingles(normalize_words(o["text_content"] or "")),
                              shingles(normalize_words(c["text_content"] or "")))
                score = max(nr, jac)
                if best is None or score > best[0]:
                    best = (score, nr, jac, c, delta)
            if best and best[0] >= 0.9:
                break
        if not best:
            tally["NOMATCH"] += 1
            out.append(f"NOMATCH\t{o['id']}\t{o['date_filed']}\t{o['case_name'][:34]}\t\t\t\t\t")
            continue
        _s, nr, jac, c, delta = best
        conf = "HIGH" if (nr >= 0.9 or jac >= 0.6) else ("MEDIUM" if (nr >= 0.6 or jac >= 0.35) else "REVIEW")
        tally[conf] += 1
        out.append(f"{conf}\t{o['id']}\t{o['date_filed']}\t{o['case_name'][:34]}\t{c['id']}\t{c['nd']}\t{c['case_name'][:34]}\t{nr:.2f}\t{jac:.2f}")

    rpt = Path("triage") / f"{BATCH}.tsv"
    rpt.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"=== no-cite dup matcher (DRY RUN, {len(nocite)} rows) ===")
    for k in ("HIGH", "MEDIUM", "REVIEW", "NOMATCH"):
        print(f"  {k:<8} {tally[k]}")
    print(f"  report -> {rpt}")
    conn.close()


if __name__ == "__main__":
    main()
