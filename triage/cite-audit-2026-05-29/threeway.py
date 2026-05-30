#!/usr/bin/env python3
"""Three-way classification of marker↔Westlaw divergences using the court PDF
text-layer as tiebreaker (§ TODO #4 / preserve-source-typos rule).

For each review opinion, diff marker(OCR) vs Westlaw word tokens. At each
divergence, consult the court PDF text-layer (the authoritative words; only its
¶ glyph + kerning are unreliable, so we match kerning-robustly on a context
window). Classify:
  KEEP  — marker matches the court PDF (faithful; e.g. a court typo) -> do nothing
  FIX   — Westlaw matches the court PDF, marker doesn't (real OCR misread)
  MOVED — words Westlaw inlines that marker placed elsewhere (footnotes) -> benign
  AMBIG — neither/both match in context -> needs a human look
"""
import difflib
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import para_markers_lib as L

WORK = "/Users/jerod/code/ndcourts-mcp/triage/cite-audit-2026-05-29/para-markers"
TOKEN = re.compile(r"[a-z0-9]+")


def nospace(toks):
    return "".join(toks)


def pdf_text(path):
    out = subprocess.run(["pdftotext", path, "-"], capture_output=True, text=True).stdout
    return re.sub(r"[^a-z0-9]", "", out.lower())


def ctx(tokens, a, b, pad=3):
    return tokens[max(0, a - pad):b + pad]


def main():
    mapping = {e["slug"]: e for e in json.load(open(f"{WORK}/mapping.json"))}
    report = json.load(open(f"{WORK}/validation_report.json"))
    grand = {"KEEP": 0, "FIX": 0, "MOVED": 0, "AMBIG": 0}
    for r in report:
        if r["status"] != "review":
            continue
        e = mapping[r["slug"]]
        rep = f"{WORK}/marker_out/{r['slug']}/{r['slug']}.repaired.md"
        src = rep if os.path.exists(rep) else f"{WORK}/marker_out/{r['slug']}/{r['slug']}.md"
        m = L.normalize_marker_md(open(src, encoding="utf-8", errors="replace").read())
        wl = open(e["wl_txt"], encoding="utf-8", errors="replace").read()
        mt = TOKEN.findall(L._ANY_PARA.sub(" ", L.marker_body(m)).lower())
        wt = TOKEN.findall(re.sub(r"\*\d+", " ", L._ANY_PARA.sub(" ", L.westlaw_body(wl))).lower())
        pdf = pdf_text(e["pdf"])
        m_all = nospace(mt)
        fixes = []
        cnt = {"KEEP": 0, "FIX": 0, "MOVED": 0, "AMBIG": 0}
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, mt, wt, autojunk=False).get_opcodes():
            if tag == "equal":
                continue
            mw, ww = mt[i1:i2], wt[j1:j2]
            if tag == "insert":   # Westlaw has words marker lacks
                if nospace(ww) in m_all:
                    cnt["MOVED"] += 1            # appears elsewhere in marker (footnote)
                elif nospace(ww) in pdf:
                    cnt["FIX"] += 1; fixes.append(f"marker DROPPED: {' '.join(ww)[:40]}")
                else:
                    cnt["MOVED"] += 1            # Westlaw-only editorial / star-page
                continue
            # replace or delete: compare context windows against the PDF
            mc = nospace(ctx(mt, i1, i2)); wc = nospace(ctx(wt, j1, j2))
            m_in, w_in = mc in pdf, wc in pdf
            if m_in and not w_in:
                cnt["KEEP"] += 1
            elif w_in and not m_in:
                cnt["FIX"] += 1
                fixes.append(f"marker={' '.join(mw)[:24]!r} -> court/WL={' '.join(ww)[:24]!r}")
            elif tag == "delete" and nospace(mw) in pdf:
                cnt["KEEP"] += 1                 # marker has court text Westlaw omitted
            else:
                cnt["AMBIG"] += 1
        for k in grand:
            grand[k] += cnt[k]
        flag = "CLEAN" if cnt["FIX"] == 0 and cnt["AMBIG"] == 0 else "NEEDS FIX/LOOK"
        print(f"{r['cite']:12} ratio={r['word_ratio']}  KEEP={cnt['KEEP']} FIX={cnt['FIX']} "
              f"MOVED={cnt['MOVED']} AMBIG={cnt['AMBIG']}  [{flag}]")
        for f in fixes[:4]:
            print(f"        FIX> {f}")
    print(f"\nTOTAL across 11: {grand}")


if __name__ == "__main__":
    main()
