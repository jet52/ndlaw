#!/usr/bin/env python3
"""Locate the genuine OCR-error divergences and report where to look in the PDF."""
import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import para_markers_lib as L

WORK = "/Users/jerod/code/ndcourts-mcp/triage/cite-audit-2026-05-29/para-markers"
TARGETS = {  # cite -> (marker_word, correct_word)
    "2024 ND 40": ("invite", "invitee"),
    "2020 ND 33": ("t", "i"),
    "2021 ND 70": ("t", "i"),
    "2023 ND 190": ("t", "i"),
}
mapping = {e["cite"]: e for e in json.load(open(f"{WORK}/mapping.json"))}


def marker_with_pos(text):
    """tokens + their char offsets, and a function to find the ¶N before an offset."""
    toks, pos = [], []
    for m in re.finditer(r"[A-Za-z0-9]+", L._ANY_PARA.sub(lambda x: " " * len(x.group()), L.marker_body(text))):
        toks.append(m.group().lower())
        pos.append(m.start())
    markers = [(int(mm.group(1)), mm.start()) for mm in re.finditer(r"\[¶(\d+)\]", text)]
    return toks, pos, markers


def para_at(markers, off):
    cur = "?"
    for n, p in markers:
        if p <= off:
            cur = n
        else:
            break
    return cur


for cite, (mw, cw) in TARGETS.items():
    e = mapping[cite]
    slug = e["slug"]
    rep = f"{WORK}/marker_out/{slug}/{slug}.repaired.md"
    src = rep if os.path.exists(rep) else f"{WORK}/marker_out/{slug}/{slug}.md"
    norm = L.normalize_marker_md(open(src, encoding="utf-8", errors="replace").read())
    mt, mp, markers = marker_with_pos(norm)
    wt = re.findall(r"[a-z0-9]+", re.sub(r"\*\d+", " ", L._ANY_PARA.sub(" ", L.westlaw_body(
        open(e["wl_txt"], encoding="utf-8", errors="replace").read()))).lower())
    print(f"\n=== {cite}  ({slug}.pdf) — marker {mw!r} vs court/Westlaw {cw!r} ===")
    sm = difflib.SequenceMatcher(None, mt, wt, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace" and mt[i1:i2] == [mw] and wt[j1:j2] == [cw]:
            para = para_at(markers, mp[i1])
            mctx = " ".join(mt[max(0, i1 - 6):i2 + 6])
            wctx = " ".join(wt[max(0, j1 - 6):j2 + 6])
            print(f"  PARAGRAPH ¶{para}")
            print(f"    marker reads : ...{mctx}...")
            print(f"    should read  : ...{wctx}...   (confirm PDF shows {cw!r})")
