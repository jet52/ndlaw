#!/usr/bin/env python3
"""Crosswalk-by-alignment prototype (#1 of TODO-const-history-validation.md).

Read-only. Derives the 1981 reorganization crosswalk (original 1889 §1-§217 +
Schedule  ->  modern art./§) by TEXT SIMILARITY between clean DB text on both
sides, instead of sourcing the official disposition table (Replacement Vol 13,
not on disk).

  SOURCE (old): constitution_history.db provisions, each provision's last
                historical version (text as it stood ~1980, pre-reorg).
  TARGET (new): constitution.db modern reorg provisions (art. ROMAN, § N;
                excludes 'amend. art.' historical articles), current text.

Reorg was a pure rearrangement, so unchanged provisions match near-1.0;
post-1981 amendments lower the score but the match is usually still top-1.
Low-confidence rows are the split/merge/repealed/new residue for manual review.

Output: triage/const-crosswalk-2026-06-14.tsv
        old_cite, new_cite, jaccard, status, alt2, alt3
"""
import sqlite3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HIST = ROOT / "constitution_history.db"
SERVED = ROOT / "constitution.db"
OUT = ROOT / "triage" / "const-crosswalk-2026-06-14.tsv"

WORD = re.compile(r"[a-z0-9]+")


def shingles(text, n=5):
    toks = WORD.findall(text.lower())
    if len(toks) < n:
        return frozenset(toks)
    return frozenset(" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / (len(a) + len(b) - inter)


def load_source():
    """Old provisions: last historical version text, keyed by old citation."""
    con = sqlite3.connect(HIST)
    rows = con.execute("""
        SELECT p.citation, v.text_content, v.effective_start
        FROM provisions p JOIN provision_versions v ON v.provision_id=p.id
        ORDER BY p.id, v.effective_start
    """).fetchall()
    con.close()
    latest = {}
    for cite, text, start in rows:
        latest[cite] = (text, start)  # ordered, so last wins
    return [(c, t) for c, (t, s) in latest.items() if t and len(t) > 40]


def load_target():
    """Modern reorg provisions, current text."""
    con = sqlite3.connect(SERVED)
    rows = con.execute("""
        SELECT p.citation, v.text_content
        FROM provisions p JOIN provision_versions v ON v.provision_id=p.id
        WHERE p.corpus='const' AND p.citation LIKE '%art.%'
              AND p.citation NOT LIKE '%amend%'
    """).fetchall()
    con.close()
    return [(c, t) for c, t in rows if t and len(t) > 40]


def main():
    src = load_source()
    tgt = load_target()
    tgt_sh = [(c, shingles(t)) for c, t in tgt]

    CONF, REVIEW = 0.55, 0.25
    rows = []
    counts = {"CONFIDENT": 0, "REVIEW": 0, "NOMATCH": 0}
    for oc, otext in src:
        osh = shingles(otext)
        scored = sorted(
            ((jaccard(osh, tsh), nc) for nc, tsh in tgt_sh),
            reverse=True,
        )[:3]
        best_j, best_c = scored[0]
        status = ("CONFIDENT" if best_j >= CONF
                  else "REVIEW" if best_j >= REVIEW else "NOMATCH")
        counts[status] += 1
        alts = "; ".join(f"{c}={j:.2f}" for j, c in scored[1:])
        rows.append((oc, best_c if best_j >= REVIEW else "", round(best_j, 3),
                     status, alts))

    rows.sort(key=lambda r: (-r[2]))
    with open(OUT, "w") as f:
        f.write("old_cite\tnew_cite\tjaccard\tstatus\talternates\n")
        for oc, nc, j, st, alts in rows:
            f.write(f"{oc}\t{nc}\t{j}\t{st}\t{alts}\n")

    print("=== Crosswalk-by-alignment prototype ===")
    print(f"source (old) provisions: {len(src)}   target (modern) provisions: {len(tgt)}")
    print(f"thresholds: CONFIDENT>={CONF}  REVIEW>={REVIEW}")
    for k in ("CONFIDENT", "REVIEW", "NOMATCH"):
        print(f"  {k:<10} {counts[k]}")
    print()
    print("=== sample CONFIDENT matches (high jaccard = clean rearrangement) ===")
    for oc, nc, j, st, alts in [r for r in rows if r[3] == "CONFIDENT"][:12]:
        print(f"  {j:.2f}  {oc:<28} -> {nc}")
    print()
    print("=== sample REVIEW (amended/split/merged — needs a human) ===")
    for oc, nc, j, st, alts in [r for r in rows if r[3] == "REVIEW"][:10]:
        print(f"  {j:.2f}  {oc:<28} -> {nc}   [{alts}]")
    print()
    print("=== NOMATCH (likely repealed-before-1981 or heavily rewritten) ===")
    for oc, nc, j, st, alts in [r for r in rows if r[3] == "NOMATCH"][:15]:
        print(f"  {j:.2f}  {oc}")
    print()
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
