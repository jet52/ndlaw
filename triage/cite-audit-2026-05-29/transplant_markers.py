#!/usr/bin/env python3
"""Transplant missing [¶N] markers from Westlaw into marker's OCR text (§ TODO #4).

For review cases where marker dropped paragraph markers (count < Westlaw), insert
ONLY the missing [¶N] at the correct paragraph boundary in marker's authoritative
text — located by matching Westlaw paragraph N's distinctive opening phrase. The
court's words stay; only the numbering is completed. Re-validate afterward.

Writes repaired markdown to marker_out/<slug>/<slug>.repaired.md (non-destructive).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import para_markers_lib as L

WORK = "/Users/jerod/code/ndcourts-mcp/triage/cite-audit-2026-05-29/para-markers"


def _wl_paragraphs(wl_body):
    """Yield (N, opening_phrase_tokens) for each Westlaw paragraph."""
    for pat in L._WL_FORMS:
        marks = list(pat.finditer(wl_body))
        if marks:
            break
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(wl_body)
        para = L._ANY_PARA.sub(" ", wl_body[start:end])
        para = re.sub(r"\*\d+", " ", para)
        toks = re.findall(r"[A-Za-z]+", para)[:7]
        yield int(m.group(1)), toks


def transplant(marker_norm, wl_body):
    text = marker_norm
    have = set(L.markers(text))
    wl = dict(_wl_paragraphs(wl_body))
    total = max(wl) if wl else 0
    missing = [n for n in range(1, total + 1) if n not in have]
    inserted, unplaced = [], []
    for n in missing:
        toks = wl.get(n, [])
        if len(toks) < 3:
            unplaced.append(n)
            continue
        # flexible phrase regex from the first few words
        phrase = r"\W+".join(re.escape(t) for t in toks[:5])
        # search window: after marker n-1, before marker n+1 (if present)
        lo = 0
        mprev = re.search(rf"\[¶{n-1}\]", text)
        if mprev:
            lo = mprev.end()
        hi = len(text)
        for k in range(n + 1, total + 1):
            mnext = re.search(rf"\[¶{k}\]", text)
            if mnext:
                hi = mnext.start()
                break
        hits = list(re.finditer(phrase, text[lo:hi], re.IGNORECASE))
        if len(hits) == 1:                 # unique in window — safe to place
            pos = lo + hits[0].start()
            text = text[:pos] + f"[¶{n}] " + text[pos:]
            inserted.append(n)
        else:
            unplaced.append(n)
    return text, inserted, unplaced


def main():
    mapping = {e["slug"]: e for e in json.load(open(f"{WORK}/mapping.json"))}
    report = json.load(open(f"{WORK}/validation_report.json"))
    resolved = stillbad = 0
    for r in report:
        if r.get("status") != "review" or r.get("counts_match"):
            continue  # only count-mismatch reviews need transplant
        slug = r["slug"]
        md = f"{WORK}/marker_out/{slug}/{slug}.md"
        norm = L.normalize_marker_md(open(md, encoding="utf-8", errors="replace").read())
        wl = open(mapping[slug]["wl_txt"], encoding="utf-8", errors="replace").read()
        new, ins, unp = transplant(norm, L.westlaw_body(wl))
        ok = L.seq_ok(L.markers(new))
        open(f"{WORK}/marker_out/{slug}/{slug}.repaired.md", "w").write(new)
        print(f"  {r['cite']:12} inserted {ins} unplaced {unp} -> seq_ok={ok}")
        if ok and not unp:
            resolved += 1
        else:
            stillbad += 1
    print(f"\ntransplant: {resolved} resolved, {stillbad} still need manual review")


if __name__ == "__main__":
    main()
