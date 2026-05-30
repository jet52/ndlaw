#!/usr/bin/env python3
"""Produce the final marker text per opinion (§ TODO #4), in one deterministic
pass: raw OCR fixes -> normalize -> Westlaw gap-fill of any missing markers.

Writes <slug>.final.md (what the write-back will adopt as text_content).

RAW_FIXES are the human-confirmed OCR corrections (verified against the court
PDF + Westlaw): only marker-vs-source divergences, never the court's own typos.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import para_markers_lib as L
from transplant_markers import transplant

WORK = "/Users/jerod/code/ndcourts-mcp/triage/cite-audit-2026-05-29/para-markers"

# Confirmed against the PDFs (2026-05-30). Each: (find, replace, expected_count).
RAW_FIXES = {
    "2024ND40":  [("an invite will proceed", "an invitee will proceed", 1)],   # dropped 'e'
    "2020ND33":  [("affirm.\n\nT\n\n", "affirm.\n\nI\n\n", 1)],                 # §header I read as T
    "2021ND70":  [("appeal.\n\nT\n\n", "appeal.\n\nI\n\n", 1)],
    "2023ND190": [("year.\n\nT\n\n", "year.\n\nI\n\n", 1)],
    "2023ND131": [("[928]", "[¶28]", 1)],                                       # ¶ misread as 9
    "2020ND64":  [("In August 2016, Big Pines", "[¶3] In August 2016, Big Pines", 1)],  # dropped marker
}


def main():
    mapping = json.load(open(f"{WORK}/mapping.json"))
    incomplete = []
    for e in mapping:
        slug = e["slug"]
        raw = open(f"{WORK}/marker_out/{slug}/{slug}.md", encoding="utf-8", errors="replace").read()
        for find, repl, exp in RAW_FIXES.get(slug, []):
            n = raw.count(find)
            assert n == exp, f"{slug}: {find!r} found {n}x (expected {exp})"
            raw = raw.replace(find, repl)
        norm = L.normalize_marker_md(raw)
        wl = open(e["wl_txt"], encoding="utf-8", errors="replace").read()
        if not L.seq_ok(L.markers(norm)):
            norm, ins, unp = transplant(norm, L.westlaw_body(wl))
        nums = L.markers(norm)
        if not L.seq_ok(nums):
            incomplete.append((e["cite"], len(nums), len(L.westlaw_markers(L.westlaw_body(wl)))))
        open(f"{WORK}/marker_out/{slug}/{slug}.final.md", "w").write(norm)
    print(f"wrote {len(mapping)} .final.md files")
    print("incomplete (seq not 1..N):", incomplete or "NONE")


if __name__ == "__main__":
    main()
