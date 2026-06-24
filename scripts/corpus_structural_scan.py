"""Layer A — deterministic structural pre-pass over the whole corpus.

Zero-token detectors that flag suspicious structure per opinion. Output is a
per-opinion *structural report* (JSONL) handed to the proofing read-agents so they
never burn tokens re-deriving what code can find exhaustively, plus a corpus-level
summary of flag counts by class.

Detectors (each is a LEAD, not a verdict — agents/source confirm):
  paragraph_seq : [¶N] markers not contiguous 1..K (gap / dup / decrease)
  starpage_seq  : reporter *NNN star-pages that decrease (possible OCR digit error)
  heading_seq   : roman-numeral section headings out of order / missing a step
  whitespace    : 3+ blank lines, mid-sentence hard breaks, doubled spaces
  ocr_glyph     : characters that should never appear in clean opinion text

Read-only. Usage:
  python scripts/corpus_structural_scan.py [--db opinions.db] [--out PATH]
"""
import argparse
import json
import re
import sqlite3
import sys
from collections import Counter

import ndcourts_mcp.proofread as pr

# characters that should not appear in clean ND opinion text (legal text uses
# § ¶ — those are fine; \x0c form-feed = benign page break, excluded; flag debris)
_BAD_GLYPH = re.compile(r"[£■¤�\x00-\x08\x0e-\x1f\x7f]|�")
_ROMAN_LINE = re.compile(r"(?m)^\s*([IVXL]{1,5})\.?\s*$")
_STAR_PAGE = re.compile(r"(?<![\d/])\*(\d{2,4})\b")
_DOUBLE_SPACE = re.compile(r"\S  +\S")
_MIDSENT_BREAK = re.compile(r"[a-z,;]\n[a-z]")
_BLANKRUN = re.compile(r"\n[ \t\xa0]*\n[ \t\xa0]*\n")

_ROMAN_VAL = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
              "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13,
              "XIV": 14, "XV": 15}


def para_seq_flags(text):
    nums = [n for n, _ in pr.paragraph_markers(text)]
    if len(nums) < 2:
        return []
    out = []
    seen = set()
    prev = None
    for n in nums:
        if n in seen:
            out.append(f"dup ¶{n}")
        seen.add(n)
        if prev is not None and n != prev + 1 and n not in (prev,):
            if n < prev:
                out.append(f"decrease ¶{prev}->¶{n}")
            elif n > prev + 1:
                out.append(f"gap ¶{prev}->¶{n}")
        prev = n
    return out[:8]


def starpage_seq_flags(text):
    """A single star-page lower than BOTH neighbours = a local dip, i.e. one
    transposed/wrong digit in a page number (e.g. *74 *47 *75). Plain backward
    steps are usually a different reporter or a cited case's pagination — skip."""
    pages = [int(m.group(1)) for m in _STAR_PAGE.finditer(text)]
    out = []
    for a, b, c in zip(pages, pages[1:], pages[2:]):
        if b < a and b < c and (a - b) < 400:  # local dip, not a reporter switch
            out.append(f"*{a} *{b} *{c}")
    return out[:6]


def heading_seq_flags(text):
    """Flag a SKIPPED step in an increasing roman-numeral run (I, II, IV -> no
    III). Ignore decreases — a lone 'I' on a line is almost always the pronoun,
    not a heading, so 'V -> I' is noise, not a real out-of-order heading."""
    seq = [_ROMAN_VAL[m.group(1)] for m in _ROMAN_LINE.finditer(text)
           if m.group(1) in _ROMAN_VAL]
    if len(seq) < 2:
        return []
    out = []
    for a, b in zip(seq, seq[1:]):
        if b > a + 1:  # a step was skipped in an ascending run
            out.append(f"{a}->{b}")
    return out[:6]


def whitespace_flags(text):
    """Only the high-precision signal: runs of 3+ blank lines (the paragraph norm
    is one blank line). Double-spaces / mid-sentence breaks are too noisy as a
    flag — agents see them when they read the text anyway."""
    nb = len(_BLANKRUN.findall(text))
    return [f"{nb} blank-runs(3+)"] if nb else []


def glyph_flags(text):
    hits = Counter(m.group(0) for m in _BAD_GLYPH.finditer(text))
    return [f"{c!r}x{n}" for c, n in hits.most_common(6)]


def scan_one(text):
    flags = {}
    for name, fn in (("paragraph_seq", para_seq_flags),
                     ("starpage_seq", starpage_seq_flags),
                     ("heading_seq", heading_seq_flags),
                     ("whitespace", whitespace_flags),
                     ("ocr_glyph", glyph_flags)):
        f = fn(text)
        if f:
            flags[name] = f
    return flags


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--out", default="triage/corpus-structural-report.jsonl")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    rows = con.execute(
        "SELECT o.id, "
        "  (SELECT citation FROM citations c WHERE c.opinion_id=o.id "
        "   ORDER BY c.is_primary DESC LIMIT 1) AS cite, "
        "  o.date_filed, o.text_content "
        "FROM opinions o ORDER BY o.date_filed DESC").fetchall()
    summary = Counter()
    flagged = 0
    with open(args.out, "w") as fh:
        for oid, cite, date, text in rows:
            if not text:
                continue
            flags = scan_one(text)
            if not flags:
                continue
            flagged += 1
            for k in flags:
                summary[k] += 1
            era = (date or "")[:4]
            fh.write(json.dumps({"id": oid, "cite": cite, "era": era,
                                 "flags": flags}, ensure_ascii=False) + "\n")
    print(f"scanned {len(rows)} opinions; {flagged} flagged -> {args.out}", file=sys.stderr)
    for k, n in summary.most_common():
        print(f"  {k}\t{n}", file=sys.stderr)


if __name__ == "__main__":
    main()
