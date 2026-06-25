#!/usr/bin/env python3
"""Consolidate a proofing trio's verifier output into apply / route / defer buckets.

Reads the .auto.json + .review.json the verifier emits for each batch and routes every
proposal:

  APPLY (autosafe)  = AUTO (whitespace_only) + REVIEW(pdf_confirmed) that ALSO passes the
                      triple-evidence autosafe gate:
                        class in {ocr_char, ocr_digit, missing_text, split_join, whitespace,
                                  other}  AND  net-word-removal <= 2  AND  not ellipsis-spacing
                        AND not a 'Filed .../by Clerk' filing-stamp restoration (those were
                        intentionally stripped — strip_clerk_stamps.py / strip_filed_office.py).
  HEADING (paragraph_seq) -> heading_move.py / manual move review (the delete-vs-move trap).
  CAPTION                 -> caption triple-evidence check.
  DEFER                   -> filing-stamp restorations, ellipsis-spacing, net-removal>2, no_pdf.

Writes triage/proofing-trio-{apply,heading,caption,defer}.json. Pure analysis — no DB writes.
Usage: consolidate_proofing_trio.py p34 p35 p36
"""
import json, re, sys

SAFE = {"ocr_char", "ocr_digit", "missing_text", "split_join", "whitespace", "other"}
ELLIPSIS = re.compile(r'\.\s*\.\s*\.')
STARPAGE = re.compile(r'\*\d+')


def toks(s):
    return re.findall(r'\S+', s or "")


def touches_starpage(p):
    """Proposal adds or removes a *NNN pincite marker -> defer to the star-page-aware pass."""
    return STARPAGE.findall(p.get("old_exact", "")) != STARPAGE.findall(p.get("new_exact", ""))


def is_ellipsis_spacing(p):
    o, n = p.get("old_exact", ""), p.get("new_exact", "")
    return (re.sub(r'\s', '', o) == re.sub(r'\s', '', n)) and bool(ELLIPSIS.search(o + n))


def is_filing_stamp(p):
    n = p.get("new_exact", "")
    return "Filed" in n and "Clerk" in n and p.get("class") == "missing_text"


def main():
    batches = sys.argv[1:]
    apply_set, heading, caption, defer = [], [], [], []
    for b in batches:
        auto = json.load(open(f"triage/proofing-{b}-results.auto.json"))
        review = json.load(open(f"triage/proofing-{b}-results.review.json"))
        for p in auto:
            bad = is_ellipsis_spacing(p) or is_filing_stamp(p) or touches_starpage(p)
            (defer if bad else apply_set).append(p)
        for p in review:
            cls = p.get("class")
            if cls == "paragraph_seq":
                heading.append(p); continue
            if cls == "caption":
                caption.append(p); continue
            if is_filing_stamp(p) or is_ellipsis_spacing(p) or touches_starpage(p):
                defer.append(p); continue
            if "no_pdf" in p.get("_verdict", ""):
                defer.append(p); continue
            net_removal = len(toks(p.get("old_exact"))) - len(toks(p.get("new_exact")))
            if cls in SAFE and net_removal <= 2:
                apply_set.append(p)
            else:
                defer.append(p)
    for name, bucket in [("apply", apply_set), ("heading", heading),
                         ("caption", caption), ("defer", defer)]:
        json.dump(bucket, open(f"triage/proofing-trio-{name}.json", "w"), indent=1)
    from collections import Counter
    print(f"APPLY  {len(apply_set):4}  classes={dict(Counter(p['class'] for p in apply_set))}")
    print(f"HEADING{len(heading):4}  (paragraph_seq -> heading_move/manual)")
    print(f"CAPTION{len(caption):4}")
    print(f"DEFER  {len(defer):4}  classes={dict(Counter(p['class'] for p in defer))}")
    print(f"  defer reasons: filing-stamp/ellipsis/net-removal>2/no_pdf")
    print(f"\napply opinions: {len(set(p['opinion_id'] for p in apply_set))}")


if __name__ == "__main__":
    main()
