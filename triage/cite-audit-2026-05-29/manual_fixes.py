#!/usr/bin/env python3
"""Hand-placed marker fixes the auto-transplant couldn't anchor (§ TODO #4).

Each fix inserts a missing [¶N] at the court-correct paragraph boundary (verified
against the Westlaw paragraph opening), keeping marker's words unchanged. Writes
<slug>.repaired.md. These were OCR forms the normalizer/matcher missed:
  2020 ND 64 ¶3  — opening 'In August 2016, Big Pines' (year split the anchor)
  2023 ND 131 ¶25 — paragraph merged into ¶24 by OCR ('...and we avoid...')
  2023 ND 131 ¶28 — pilcrow misread as '9' -> stored as '[928]'
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import para_markers_lib as L

WORK = "/Users/jerod/code/ndcourts-mcp/triage/cite-audit-2026-05-29/para-markers"

FIXES = {
    # (kind, pattern, value, after_marker) — 'after_marker' constrains the match
    # to occur after that [¶N], for phrases that repeat earlier in the opinion.
    "2020ND64": [("insert", r"(In August 2016, Big Pines)", "[¶3] ", None)],
    # ¶25 now auto-recovered ('[$\quad 25$]'); only the '¶'→'9' misread remains.
    "2023ND131": [("replace", r"\[928\]", "[¶28]", None)],
}

for slug, ops in FIXES.items():
    raw = open(f"{WORK}/marker_out/{slug}/{slug}.md", encoding="utf-8", errors="replace").read()
    text = L.normalize_marker_md(raw)
    for kind, pat, val, after in ops:
        off = text.index(f"[¶{after}]") if after else 0
        head, tail = text[:off], text[off:]
        if kind == "insert":
            tail, n = re.subn(pat, val + r"\1", tail, count=1)
        else:
            tail, n = re.subn(pat, val, tail, count=1)
        text = head + tail
        assert n == 1, f"{slug}: {kind} {pat!r} matched {n} times (expected 1)"
    nums = L.markers(text)
    open(f"{WORK}/marker_out/{slug}/{slug}.repaired.md", "w").write(text)
    print(f"{slug}: markers now {nums[:3]}..{nums[-3:]} seq_ok={L.seq_ok(nums)} ({len(nums)})")
