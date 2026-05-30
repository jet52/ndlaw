#!/usr/bin/env python3
"""Validate marker re-OCR output against Westlaw, word-for-word (§ TODO #4).

For each opinion with a completed marker .md:
  - normalize marker md, extract [¶N] sequence (must be 1..N)
  - compare paragraph count to Westlaw's
  - WORD-FOR-WORD body comparison (markers + Westlaw editorial stripped):
    difflib ratio + a sample of differing tokens
Classifies each: accept (seq ok, counts match, ratio >= THRESHOLD) or review.
Writes report.json; prints a summary table.
"""
import difflib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import para_markers_lib as L

WORK = "/Users/jerod/code/ndcourts-mcp/triage/cite-audit-2026-05-29/para-markers"
THRESHOLD = float(sys.argv[sys.argv.index("--threshold") + 1]) if "--threshold" in sys.argv else 0.985

mapping = json.load(open(f"{WORK}/mapping.json"))
report = []
for e in mapping:
    slug = e["slug"]
    fin = f"{WORK}/marker_out/{slug}/{slug}.final.md"
    rep = fin if os.path.exists(fin) else f"{WORK}/marker_out/{slug}/{slug}.repaired.md"
    md_path = rep if os.path.exists(rep) else f"{WORK}/marker_out/{slug}/{slug}.md"
    rec = {"cite": e["cite"], "slug": slug}
    if not os.path.exists(md_path):
        rec["status"] = "pending"
        report.append(rec)
        continue
    norm = L.normalize_marker_md(open(md_path, encoding="utf-8", errors="replace").read())
    wl = open(e["wl_txt"], encoding="utf-8", errors="replace").read()
    m_nums, w_nums = L.markers(norm), L.westlaw_markers(L.westlaw_body(wl))
    m_tok = L.tokenize(L.marker_body(norm))
    w_tok = L.tokenize(L.westlaw_body(wl))
    ratio = difflib.SequenceMatcher(None, m_tok, w_tok, autojunk=False).ratio()
    # sample a few differing tokens for review
    diffs = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, m_tok, w_tok, autojunk=False).get_opcodes():
        if tag != "equal" and len(diffs) < 6:
            diffs.append(f"{tag}: marker={m_tok[i1:i2][:4]} westlaw={w_tok[j1:j2][:4]}")
    rec.update({
        "marker_paras": len(m_nums), "westlaw_paras": len(w_nums),
        "seq_ok": L.seq_ok(m_nums), "counts_match": len(m_nums) == len(w_nums),
        "word_ratio": round(ratio, 4), "marker_words": len(m_tok), "westlaw_words": len(w_tok),
        "diffs": diffs,
    })
    rec["status"] = ("accept" if rec["seq_ok"] and rec["counts_match"]
                     and ratio >= THRESHOLD else "review")
    report.append(rec)

json.dump(report, open(f"{WORK}/validation_report.json", "w"), indent=2)
done = [r for r in report if r.get("status") != "pending"]
acc = [r for r in done if r["status"] == "accept"]
print(f"validated {len(done)}/{len(report)} (threshold {THRESHOLD}); accept {len(acc)}, review {len(done)-len(acc)}, pending {len(report)-len(done)}")
print(f"{'cite':14} {'mPar':4} {'wPar':4} seq cnt {'ratio':6} status")
for r in done:
    print(f"{r['cite']:14} {r['marker_paras']:4} {r['westlaw_paras']:4} "
          f"{'Y' if r['seq_ok'] else 'n':3} {'Y' if r['counts_match'] else 'n':3} "
          f"{r['word_ratio']:.4f} {r['status']}"
          + (f"  | {r['diffs'][0]}" if r["status"] == "review" and r["diffs"] else ""))
