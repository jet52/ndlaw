#!/usr/bin/env python3
"""Cross-reference resolver for the NDCC / NDAC primary-law corpora (PL-VALIDATE #1).

Parses every internal "section/chapter/article/title NN-NN-NN" reference in the
current text of each provision and checks that the target exists in the corpus.

Rationale: the PL-1 (dropped-line) and PL-2 (phantom-header) bugs were caught by a
seam-detector, but that only finds drops that leave an *ungrammatical* seam
("under section guilty of..."). A clean substitution of one valid-looking section
number for a wrong one leaves no seam. This resolver closes that blind spot: it
flags a cross-reference whose number points to a section that does not exist.

READ-ONLY. Emits a TSV of unresolved references plus a stdout summary. It does NOT
mutate any DB. Each unresolved hit is classified by suspicion so the high-value
candidates (a real chapter, but the exact section is missing) float to the top;
known false-positive classes (federal/out-of-state law, cross-corpus refs that
resolve in the sibling corpus) are labeled, not silently dropped.

Usage:
    python3 triage/xref_resolver_2026-06-13.py            # both corpora
    python3 triage/xref_resolver_2026-06-13.py ndcc       # one corpus
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# corpus -> (db file, max segment count for a *section*)
CORPORA = {
    "ndcc": ("statutes.db", 3),   # title-chapter-section
    "ndac": ("admincode.db", 4),  # title-article-chapter-section
}

# A code number: 2..4 segments joined by '-', each an integer with an optional
# decimal suffix (e.g. 12.1, 03.2). 1-segment ("title 33") is excluded on purpose:
# it almost always resolves and a bare integer collides with land descriptions,
# dates, and money. The leading boundary keeps us from biting into a longer token.
_SEG = r"\d{1,3}(?:\.\d+)?"
NUM_RE = re.compile(rf"(?<![\d.\-]){_SEG}(?:-{_SEG}){{1,3}}(?![\d])")

# Reference keywords that introduce a code number. We only treat a dash-number as a
# cross-reference when it is introduced this way (or chained in a list off one that
# was) — that is the standard statutory grammar and it excludes the bulk of FPs.
KEYWORD_RE = re.compile(
    r"\b(sections?|chapters?|articles?|titles?|N\.D\.C\.C\.|N\.D\.A\.C\.)\b",
    re.IGNORECASE,
)

# Connectors that continue a list after a reference keyword:
#   "sections 11-09.1-01, 11-09.1-02, and 11-09.1-05"
#   "sections 4-01-01 through 4-01-09"
CONNECT_RE = re.compile(r"\s*(?:,|;|\band\b|\bor\b|\bthrough\b|\bto\b)\s*", re.IGNORECASE)

# A federal / out-of-jurisdiction marker appearing right after a number — these are
# never NDCC/NDAC targets. (USC sections are bare integers and won't match NUM_RE,
# but a reference like "section 7-01 of the Uniform Commercial Code" can.)
FOREIGN_RE = re.compile(
    r"\b(U\.?S\.?C\.?|United States Code|C\.?F\.?R\.?|Code of Federal Regulations|"
    r"Public Law|Stat\.|Uniform Commercial Code)\b",
    re.IGNORECASE,
)


def norm(num: str) -> str:
    """Normalize a code number for comparison: strip leading zeros from the integer
    part of each segment, preserve decimal suffixes. '01-03-19' -> '1-3-19';
    '05-02-10.1' -> '5-2-10.1'; '12.1-06-01' -> '12.1-6-1'."""
    out = []
    for seg in num.split("-"):
        if "." in seg:
            head, _, tail = seg.partition(".")
            out.append(f"{int(head)}.{tail}")
        else:
            out.append(str(int(seg)))
    return "-".join(out)


def truncate(norm_key: str, n: int) -> str:
    return "-".join(norm_key.split("-")[:n])


def load_corpus(db_path: Path):
    """Return (sections, prefixes, status_by_section) where:
    sections = set of normalized full section keys,
    prefixes = dict {segcount: set of normalized truncated keys} for chapter/article/title,
    status_by_section = {normalized_key: status}."""
    con = sqlite3.connect(db_path)
    rows = con.execute("SELECT cite_key, status FROM provisions").fetchall()
    con.close()
    sections, status = set(), {}
    prefixes = {1: set(), 2: set(), 3: set()}
    for cite_key, st in rows:
        raw = cite_key.split(" ", 1)[1]  # drop 'ndcc '/'ndac ' prefix
        nk = norm(raw)
        sections.add(nk)
        status[nk] = st
        for n in (1, 2, 3):
            if len(nk.split("-")) > n:
                prefixes[n].add(truncate(nk, n))
    return sections, prefixes, status


def classify(num: str, segcount: int, max_seg: int, own, other) -> tuple[str, str]:
    """Return (verdict, note). verdict in RESOLVED / CROSS_CORPUS / FOREIGN_SHAPE /
    UNRESOLVED_*."""
    nk = norm(num)
    own_sec, own_pref, own_status = own
    other_sec, _, _ = other

    # Section-level reference (full segment count for this corpus).
    if segcount == max_seg:
        if nk in own_sec:
            return "RESOLVED", own_status.get(nk, "active")
        if nk in other_sec:
            return "CROSS_CORPUS", "resolves in sibling corpus"
        # Does the parent chapter exist? That is the high-suspicion signal: a real
        # chapter with a non-existent section in it.
        chap_segs = max_seg - 1
        if truncate(nk, chap_segs) in own_pref[chap_segs]:
            return "UNRESOLVED_CHAPTER_EXISTS", f"chapter {truncate(nk, chap_segs)} present"
        return "UNRESOLVED_NO_PARENT", "chapter absent in-corpus"

    # Sub-section-level reference: chapter / article / title.
    if nk in own_pref.get(segcount, set()):
        return "RESOLVED", "container"
    if nk in other_sec or any(truncate(s, segcount) == nk for s in []):
        return "CROSS_CORPUS", "container in sibling"
    # Could be a container in the sibling corpus.
    if any(s.startswith(nk + "-") or s == nk for s in other_sec):
        return "CROSS_CORPUS", "container in sibling corpus"
    return "UNRESOLVED_CONTAINER", f"{segcount}-segment container absent"


def extract_refs(text: str):
    """Yield (keyword, raw_number, start_offset) for each cross-reference, including
    list continuations chained off a keyword."""
    for kw in KEYWORD_RE.finditer(text):
        pos = kw.end()
        # Pull the first number after the keyword, then chain through a list.
        while True:
            # The number must follow closely; "section of this chapter" (no number,
            # or a far-off one) stops the chain. Allow a short lead ("section 4",
            # "section number 4", "§ 4") of a few chars.
            window = text[pos:pos + 40]
            wm = NUM_RE.search(window)
            if not wm or wm.start() > 4:
                break
            num = wm.group(0)
            abs_start = pos + wm.start()
            yield kw.group(1), num, abs_start
            # continue only if a connector immediately follows this number
            after = text[abs_start + len(num):]
            cm = CONNECT_RE.match(after)
            if not cm:
                break
            pos = abs_start + len(num) + cm.end()


def run(corpus: str):
    db_path, max_seg = ROOT / CORPORA[corpus][0], CORPORA[corpus][1]
    other_name = "ndac" if corpus == "ndcc" else "ndcc"
    own = load_corpus(db_path)
    other = load_corpus(ROOT / CORPORA[other_name][0])

    con = sqlite3.connect(db_path)
    rows = con.execute(
        """SELECT p.citation, v.text_content
           FROM provisions p JOIN provision_versions v ON v.id = p.current_version_id"""
    ).fetchall()
    con.close()

    counts = {}
    unresolved = []  # (verdict, src_citation, keyword, raw, normalized, note, context)
    total_refs = 0

    for citation, text in rows:
        if not text:
            continue
        for kw, num, off in extract_refs(text):
            segcount = len(num.split("-"))
            if segcount < 2 or segcount > max_seg:
                continue
            total_refs += 1
            # foreign-marker guard: look just past the number
            tail = text[off + len(num): off + len(num) + 40]
            if FOREIGN_RE.search(tail) or FOREIGN_RE.search(text[max(0, off - 40):off]):
                counts["FOREIGN_SHAPE"] = counts.get("FOREIGN_SHAPE", 0) + 1
                continue
            verdict, note = classify(num, segcount, max_seg, own, other)
            counts[verdict] = counts.get(verdict, 0) + 1
            if verdict.startswith("UNRESOLVED"):
                ctx = re.sub(r"\s+", " ", text[max(0, off - 50):off + len(num) + 50]).strip()
                unresolved.append((verdict, citation, kw, num, norm(num), note, ctx))

    # write TSV
    out = ROOT / "triage" / f"xref-unresolved-{corpus}-2026-06-13.tsv"
    # high-suspicion first
    order = {"UNRESOLVED_CHAPTER_EXISTS": 0, "UNRESOLVED_CONTAINER": 1, "UNRESOLVED_NO_PARENT": 2}
    unresolved.sort(key=lambda r: (order.get(r[0], 9), r[1]))
    with out.open("w") as fh:
        fh.write("verdict\tsource_citation\tkeyword\traw_number\tnormalized\tnote\tcontext\n")
        for r in unresolved:
            fh.write("\t".join(r) + "\n")

    print(f"\n=== {corpus.upper()} ({db_path.name}) ===")
    print(f"  references parsed: {total_refs}")
    for v in sorted(counts, key=lambda k: -counts[k]):
        print(f"  {v:30s} {counts[v]:>6d}")
    print(f"  unresolved written: {len(unresolved)} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    targets = sys.argv[1:] or list(CORPORA)
    for c in targets:
        if c not in CORPORA:
            sys.exit(f"unknown corpus: {c}")
        run(c)
