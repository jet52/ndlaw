"""marker_triage.py — unified paragraph-marker anomaly detector + classifier.

Consolidates the per-session one-off marker scripts (despace / fix_marker_garbled /
dedup-storedtwice) into ONE read-only corpus sweep. Finds every `[¶…]` that is not
a clean `[¶N]`, determines the intended number from the paragraph SEQUENCE, and
routes each anomaly to the right gate:

  AUTO  glyph_repair  — malformed marker whose full intended digits are PRESENT;
                        repair only strips bracket/markup/whitespace junk WITHOUT
                        changing or inferring any digit; sequence-confirmed; not a
                        duplicate. Safe to apply via apply_proofing_proposals.py.
  REVIEW dedup        — a malformed marker heading a FIRST copy of a paragraph whose
                        clean `[¶N]` copy is the very next marker and whose text
                        matches; proposes deletion of the garbled copy. Gated for
                        human review (rule 7: never auto-apply dedup).
  PDF   needs_pdf     — the number must be INFERRED (no digit, or a letter stands in
                        for a digit), or the sequence is ambiguous (not a single gap),
                        or a dedup text-match failed. Needs the court PDF / image.
  SKIP  not_marker    — XREF (`[¶N of syllabus`, `[¶N, Decree`) and citation pincites
                        (`[¶]N, 660 N.W.2d`); these are the court's text, not markers.
  FLAG  structural    — (--structural) corpus gaps/dups among CLEAN markers
                        (missing/repeated N). Noisy (quoted-order restarts); worklist
                        only, never a proposal.

Read-only. Writes proposal/worklist JSON to --out-dir; applies nothing.
The AUTO and REVIEW files are drop-in for:
    apply_proofing_proposals.py <file> [--apply] --batch <name>

Usage:
    marker_triage.py [--db opinions.db] [--out-dir triage] [--structural]
                     [--limit N] [--ids 123,456]
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter

CLEAN = re.compile(r"\[¶(\d+)\]")
# any marker-ish anchor: an optional leading '*', then '[¶', possibly with a
# newline/star before the number. We locate every '[¶' (and '*[¶') and inspect it.
ANCHOR = re.compile(r"\*?\[¶")

# XREF / citation forms that are the court's prose, not in-text markers.
XREF = re.compile(r"\[¶\d+(?:\s+of\b|,\s*(?:Decree|H\.B|S\.B|the syllabus)|\s+of\s+(?:the\s+)?syllabus)")
PINCITE = re.compile(r"\[¶\]\s*\d+")  # e.g. "2003 ND 69, [¶]14, 660 N.W.2d"


def norm_para(s: str) -> str:
    """Strip marker TOKENS + markdown + whitespace for duplicate text comparison.

    Removes only the `[¶…]` token itself (clean or garbled, incl. internal-newline
    forms) — never the prose that follows it — so a same-line clean marker and a
    next-line garbled marker compare equal on their paragraph text.
    """
    s = re.sub(r"\*?\[¶[^\]]*\]\*?", "", s)  # [^\]] spans newlines -> catches "[¶\n *2]"
    s = s.replace("*", "")
    return re.sub(r"\s+", " ", s).strip()


def clean_markers(t: str):
    """Ordered list of (pos, number) for well-formed [¶N]."""
    return [(m.start(), int(m.group(1))) for m in CLEAN.finditer(t)]


def parse_anomaly(t: str, i: int):
    """At anchor start i, return (kind, digits, blob, blob_end, inner_text).

    kind ∈ {clean, markup_split, bracket_glyph, letter_num, no_number, unknown}
    digits = the consecutive-digit number found (str) or None.
    blob = the exact malformed marker text to replace (for repairs).
    inner_text = text captured after the number but inside the emphasis (e.g. ' On').
    """
    win = t[i : i + 60]
    # clean (may be preceded by '*' we don't want to treat as anomaly unless markup)
    m = re.match(r"\[¶(\d+)\]", win)
    if m:
        return ("clean", m.group(1), m.group(0), i + m.end(), "")
    # markup-wrap: a CLEAN [¶N] whose only defect is surrounding *…* emphasis
    # (e.g. "*[¶18] We*\n", "*[¶12]*\n"). Number intact -> markup-cohort, not a
    # marker-number defect; route to its own worklist, never propose here.
    m = re.match(r"\*\[¶(\d+)\][^\n*]*\*\n ?", win)
    if m:
        return ("markup_wrap", m.group(1), m.group(0), i + m.end(), "")
    # markup-split: *?[¶*?\n *?N] WORDS*?\n   (the dominant markdown-emphasis form)
    m = re.match(r"\*?\[¶\*?\n ?\*?(\d+)\]([^\n*]*)\*?\n ", win)
    if m:
        return ("markup_split", m.group(1), m.group(0), i + m.end(), m.group(2))
    # *[¶*\n N]  (leading-star variant, 14010)
    m = re.match(r"\*\[¶\*\n ?(\d+)\]", win)
    if m:
        return ("markup_split", m.group(1), m.group(0), i + m.end(), "")
    # bracket-glyph: [¶'N] [¶.N] [¶NJ [¶N} [¶N) [¶N (missing close), with full digits
    m = re.match(r"\[¶['.’]?(\d+)[\]J}\)]?", win)
    if m and m.group(1):
        # is the closer wrong/missing? (clean already returned above)
        return ("bracket_glyph", m.group(1), m.group(0), i + m.end(), "")
    # letter-in-number: [¶1G] [¶IB] [¶15J-style handled above; here digit+letter inside]
    m = re.match(r"\[¶([0-9A-Za-z]*[A-Za-z][0-9A-Za-z]*)\]?", win)
    if m and re.search(r"\d", m.group(1) or "") is None and not m.group(1).isdigit():
        return ("letter_num", None, m.group(0), i + m.end(), m.group(1))
    m = re.match(r"\[¶(\d*[A-Za-z]+\d*)\]?", win)
    if m:
        return ("letter_num", None, m.group(0), i + m.end(), m.group(1))
    # no-number: [¶ Word  (¶, space, capital/prose, no digit)
    m = re.match(r"\[¶ (?=[A-Za-z])", win)
    if m:
        return ("no_number", None, "[¶ ", i + m.end(), "")
    return ("unknown", None, win[:20], i + 2, "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--out-dir", default="triage")
    ap.add_argument("--structural", action="store_true", help="also scan clean markers for missing/duplicate N (noisy worklist)")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--ids")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    q = "SELECT id, text_content FROM opinions WHERE text_content LIKE '%[¶%'"
    params = ()
    if args.ids:
        ids = [int(x) for x in args.ids.split(",")]
        q = f"SELECT id, text_content FROM opinions WHERE id IN ({','.join('?'*len(ids))})"
        params = ids
    elif args.limit:
        q += f" LIMIT {args.limit}"
    rows = con.execute(q, params).fetchall()

    auto, dedup, needs_pdf, not_marker, unknown = [], [], [], [], []
    markup_wrap = []
    structural = []

    for oid, t in rows:
        cm = clean_markers(t)
        clean_nums = [n for _, n in cm]
        clean_pos = {p: n for p, n in cm}
        num_count = Counter(clean_nums)

        # iterate anchors
        for am in ANCHOR.finditer(t):
            i = am.start()
            kind, digits, blob, blob_end, inner = parse_anomaly(t, i)
            if kind == "clean":
                continue
            ctx = t[i : i + 55].replace("\n", "\\n")
            if kind == "markup_wrap":
                markup_wrap.append({"oid": oid, "ctx": ctx, "num": int(digits),
                                    "why": "clean marker wrapped in *…* emphasis (markup cohort)"})
                continue

            # not-a-marker?
            if XREF.match(t[i:]) or PINCITE.match(t[i:]):
                not_marker.append({"oid": oid, "ctx": ctx, "why": "xref/pincite"})
                continue
            if kind == "unknown":
                unknown.append({"oid": oid, "ctx": ctx})
                continue

            # sequence: preceding/following CLEAN number
            prev = [n for p, n in cm if p < i]
            nxt = [n for p, n in cm if p > i]
            P = prev[-1] if prev else 0
            F = nxt[0] if nxt else None
            expected = P + 1

            # intended number
            if digits is not None:
                intended = int(digits)
                digits_present = True
            else:
                intended = expected if (F is None or F == P + 2 or F == P + 1) else None
                digits_present = False

            # --- DEDUP: next marker is a clean [¶intended] heading matching text ---
            if intended is not None and num_count.get(intended, 0) >= 1:
                # find the next clean marker position after this anomaly
                after = [(p, n) for p, n in cm if p > i]
                if after and after[0][1] == intended:
                    cpos = after[0][0]
                    block = t[i:cpos]
                    nb = norm_para(block)
                    cend = after[1][0] if len(after) > 1 else min(cpos + len(block) + 200, len(t))
                    nc = norm_para(t[cpos:cend])
                    if nb and nc and (nb[:60].lower() == nc[:60].lower()):
                        dedup.append({
                            "opinion_id": oid, "class": "dedup_storedtwice",
                            "old_exact": block, "new_exact": "",
                            "source_quote": "", "verified_count": 1,
                            "source": "marker_triage: stored-twice (garbled copy + clean [¶%d])" % intended,
                            "evidence": f"Garbled marker '{ctx[:30]}' heads a first copy; clean [¶{intended}] is the next marker with matching text. {len(block)} chars.",
                            "confidence": "high"})
                        continue
                # number duplicated but not a clean adjacent text-match → needs eyes
                needs_pdf.append({"oid": oid, "ctx": ctx, "kind": kind, "intended": intended,
                                  "prev": prev[-3:], "next": nxt[:3], "why": "number duplicated; verify dedup vs restart"})
                continue

            # --- repair vs needs_pdf ---
            sequence_ok = (intended is not None and intended == expected and
                           (F is None or F == intended + 1))
            digit_inferred = (not digits_present) or kind == "letter_num"

            if digit_inferred or not sequence_ok:
                needs_pdf.append({"oid": oid, "ctx": ctx, "kind": kind,
                                  "intended": intended, "prev": prev[-3:], "next": nxt[:3],
                                  "why": ("infer-digit" if digit_inferred else "ambiguous-sequence")})
                continue

            # safe glyph repair: digits intact, only junk stripped
            new = f"[¶{intended}]{inner} " if (kind == "markup_split") else f"[¶{intended}]"
            # safety invariant: digit multiset unchanged
            if Counter(c for c in blob if c.isdigit()) != Counter(c for c in new if c.isdigit()):
                needs_pdf.append({"oid": oid, "ctx": ctx, "kind": kind, "intended": intended,
                                  "why": "digit-multiset-change (refused auto)"})
                continue
            if t.count(blob) != 1:
                needs_pdf.append({"oid": oid, "ctx": ctx, "kind": kind, "intended": intended,
                                  "why": f"anchor count={t.count(blob)}"})
                continue
            auto.append({
                "opinion_id": oid, "class": "paragraph_seq",
                "old_exact": blob, "new_exact": new,
                "source_quote": "", "verified_count": 1,
                "source": "marker_triage: glyph repair (digits intact, sequence-confirmed)",
                "evidence": f"Malformed marker '{ctx[:30]}' -> [¶{intended}]; digits unchanged, ¶{P} precedes, only bracket/markup junk stripped.",
                "confidence": "high"})

        # --- structural (clean-marker gaps/dups) ---
        if args.structural and len(clean_nums) >= 2:
            dups = [n for n, c in num_count.items() if c > 1]
            mn, mx = min(clean_nums), max(clean_nums)
            missing = [n for n in range(mn, mx + 1) if n not in num_count]
            asc = sum(1 for k in range(len(clean_nums) - 1) if clean_nums[k + 1] >= clean_nums[k])
            mono = asc / (len(clean_nums) - 1)
            if (dups or missing) and mono > 0.85:
                structural.append({"oid": oid, "dups": dups, "missing": missing,
                                   "min": mn, "max": mx, "mono": round(mono, 2),
                                   "n_markers": len(clean_nums)})

    out = args.out_dir.rstrip("/")
    def dump(name, data):
        p = f"{out}/{name}"
        json.dump(data, open(p, "w"), ensure_ascii=False, indent=1)
        return p

    print(f"scanned {len(rows)} opinions\n")
    print(f"  AUTO   glyph_repair : {len(auto):5d}  -> {dump('marker-triage-auto.json', auto)}")
    print(f"  REVIEW dedup        : {len(dedup):5d}  -> {dump('marker-triage-dedup.json', dedup)}")
    print(f"  PDF    needs_pdf    : {len(needs_pdf):5d}  -> {dump('marker-triage-needs-pdf.json', needs_pdf)}")
    print(f"  SKIP   not_marker   : {len(not_marker):5d}  -> {dump('marker-triage-not-marker.json', not_marker)}")
    print(f"  DEFER  markup_wrap  : {len(markup_wrap):5d}  -> {dump('marker-triage-markup-wrap.json', markup_wrap)}")
    print(f"  ?      unknown      : {len(unknown):5d}  -> {dump('marker-triage-unknown.json', unknown)}")
    if args.structural:
        print(f"  FLAG   structural   : {len(structural):5d}  -> {dump('marker-triage-structural.json', structural)}")
    print("\nNext: review + apply with apply_proofing_proposals.py (auto = safe; dedup = verify first).")


if __name__ == "__main__":
    main()
