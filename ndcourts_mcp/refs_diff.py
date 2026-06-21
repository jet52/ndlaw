"""Refs-vs-DB text integrity audit + citation stray-space scan.

Two read-only audits, one tool:

  compare     For every opinion, compare ``opinions.text_content`` against the
              text of its PRIMARY source file under ``~/refs/nd/opin/`` and flag
              any *substantive* deviation (a difference in the actual words /
              numbers of the opinion, after normalizing away whitespace, case,
              punctuation, YAML frontmatter, and HTML markup).

  citespaces  Scan ``text_content`` for stray spaces inside N.D.C.C. / N.D.A.C.
              section numbers — e.g. a space before or after a hyphen, as in
              ``12.1-20- 03`` instead of ``12.1-20-03``.

WHY "substantive only" and not a literal byte diff: ``text_content`` is NOT a
byte-copy of the on-disk source. At ingest it gained synthesized YAML
frontmatter and a reformatted ``# Heading``; HTML sources were tag-stripped;
months of logged OCR / digit-flip / synopsis corrections were applied to the DB
but never written back to disk; and the scraper periodically regenerates the
markdown under ~/refs. A char-for-char diff therefore flags essentially every
opinion on intended/structural differences. This audit normalizes those away so
that what remains is genuine word-level drift worth a human's eyes.

Scope (compare):
  - Primary source only (``opinions.source_path`` / ``source_reporter``).
  - Westlaw ``.doc`` binaries and page-scan ``.pdf`` / ``*-image`` sources are
    reported as NON-COMPARABLE, not extracted (decided 2026-06-20).
  - Comparable reporters: ND (markdown), NW, NW2d (markdown), archive,
    court-archive (HTML).

Output:
  - A CSV with one row per opinion (status + metrics) for the whole corpus.
  - A markdown triage report listing substantive deviations, worst first, with
    sample diff snippets; plus missing/unreadable source files.

Usage:
    python -m ndcourts_mcp.refs_diff compare \
        [--db PATH] [--refs PATH] [--workers N] [--limit N] \
        [--near-sim 0.97] [--major-sim 0.85] \
        [--out triage/refs-diff.md] [--csv triage/refs-diff.csv]

    python -m ndcourts_mcp.refs_diff citespaces \
        [--db PATH] [--out triage/cite-spaces.md] [--csv triage/cite-spaces.csv]
"""

from __future__ import annotations

import argparse
import csv
import difflib
import html
import multiprocessing as mp
import os
import re
import sqlite3
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from .db import DEFAULT_DB_PATH

DEFAULT_REFS_DIR = Path.home() / "refs" / "nd" / "opin"

# Reporters whose primary text we can read off disk and compare.
COMPARABLE_REPORTERS = {"ND", "NW", "NW2d", "archive", "court-archive"}

_WORD_RE = re.compile(r"[^a-z0-9]+")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_FRONTMATTER_RE = re.compile(r"^\s*---\s*\n.*?\n---\s*\n", re.DOTALL)
# Unambiguous navigation chrome in the archive / court-archive HTML that is NOT
# opinion content (it has no counterpart in DB text_content and otherwise trips
# every comparison). Removed element-and-content before the generic tag strip.
_NAV_ELEMENTS_RE = re.compile(
    r"<(script|style|title)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_NAV_SPANS_RE = re.compile(
    r'<span\s+class="(?:annot|filed)">.*?</span>', re.IGNORECASE | re.DOTALL)
_NAV_PHRASES_RE = re.compile(
    r"Go to Documents|N\.D\. Supreme Court", re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Normalization helpers
# --------------------------------------------------------------------------- #

def strip_frontmatter(text: str) -> str:
    """Drop a leading YAML frontmatter block (``---`` ... ``---``)."""
    return _FRONTMATTER_RE.sub("", text, count=1)


def strip_html(text: str) -> str:
    """De-markup archive HTML: drop nav chrome, tags, entities."""
    text = _NAV_ELEMENTS_RE.sub(" ", text)   # <script>/<style>/<title>…</…>
    text = _NAV_SPANS_RE.sub(" ", text)       # repeated cite annot / "Filed …"
    text = _HTML_TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return _NAV_PHRASES_RE.sub(" ", text)     # "Go to Documents" link text


def normalize_words(text: str) -> list[str]:
    """Lowercase, drop punctuation, split into word/number tokens.

    Substantive-content view: keeps letters and digits (so a wrong digit or a
    dropped word shows up) but ignores case, punctuation, and all whitespace.
    """
    return _WORD_RE.sub(" ", text.lower()).split()


def load_source_text(reporter: str, path: str, refs: Path) -> str | None:
    """Read + de-markup the primary source file. None if it can't be read."""
    full = Path(path) if os.path.isabs(path) else refs / path
    if not full.exists():
        return None
    try:
        raw = full.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if path.endswith((".htm", ".html")) or reporter in ("archive", "court-archive"):
        raw = strip_html(raw)
    return raw


# --------------------------------------------------------------------------- #
# compare mode
# --------------------------------------------------------------------------- #

@dataclass
class CompareResult:
    opinion_id: int
    citation: str
    case_name: str
    date_filed: str
    reporter: str
    source_path: str
    status: str              # identical | near | moderate | major | missing | unreadable | non-comparable
    db_words: int = 0
    src_words: int = 0
    diff_words: int = 0      # total words inserted/deleted/replaced
    similarity: float = 1.0  # difflib ratio over the word sequences
    samples: list[str] = field(default_factory=list)


def _snippet(words: list[str], lo: int, hi: int, pad: int = 4) -> str:
    """A short readable window of words[lo:hi] with a little surrounding context."""
    a = max(0, lo - pad)
    b = min(len(words), hi + pad)
    chunk = words[a:b]
    return " ".join(chunk)


def _compute_diff(db_words: list[str], src_words: list[str],
                  max_samples: int = 6) -> tuple[int, float, list[str]]:
    """Return (total changed words, similarity ratio, sample snippets)."""
    sm = difflib.SequenceMatcher(None, db_words, src_words, autojunk=False)
    diff = 0
    samples: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        diff += max(i2 - i1, j2 - j1)
        if len(samples) < max_samples:
            db_part = _snippet(db_words, i1, i2) if i2 > i1 else "∅"
            src_part = _snippet(src_words, j1, j2) if j2 > j1 else "∅"
            samples.append(f"[{tag}] DB: «{db_part}»  ↔  REFS: «{src_part}»")
    return diff, sm.ratio(), samples


def _compare_one(work: tuple) -> CompareResult:
    db_path, refs_str, oid, near_sim, major_sim = work
    refs = Path(refs_str)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    op = conn.execute(
        "SELECT id, case_name, date_filed, source_reporter, source_path, text_content "
        "FROM opinions WHERE id = ?", (oid,),
    ).fetchone()
    cite_row = conn.execute(
        "SELECT citation FROM citations WHERE opinion_id = ? AND is_primary = 1 "
        "ORDER BY id LIMIT 1", (oid,),
    ).fetchone()
    conn.close()
    citation = cite_row["citation"] if cite_row else f"opinion-{oid}"

    base = dict(
        opinion_id=oid, citation=citation, case_name=op["case_name"] or "",
        date_filed=op["date_filed"] or "", reporter=op["source_reporter"],
        source_path=op["source_path"],
    )

    reporter, spath = op["source_reporter"], op["source_path"]
    if (reporter not in COMPARABLE_REPORTERS
            or spath.lower().endswith((".doc", ".pdf"))
            or reporter.endswith("-image")):
        return CompareResult(status="non-comparable", **base)

    src_raw = load_source_text(reporter, spath, refs)
    if src_raw is None:
        return CompareResult(status="missing", **base)

    db_words = normalize_words(strip_frontmatter(op["text_content"] or ""))
    src_words = normalize_words(strip_frontmatter(src_raw))

    if not db_words or not src_words:
        return CompareResult(status="unreadable", db_words=len(db_words),
                             src_words=len(src_words), **base)

    diff, ratio, samples = _compute_diff(db_words, src_words)
    if diff == 0:
        status = "identical"
    elif ratio >= near_sim:
        status = "near"        # ~boilerplate/marker noise; not real content drift
    elif ratio >= major_sim:
        status = "moderate"    # worth a look
    else:
        status = "major"       # truncation / wrong pairing / large content gap
    return CompareResult(status=status, db_words=len(db_words),
                         src_words=len(src_words), diff_words=diff,
                         similarity=ratio, samples=samples, **base)


def run_compare(args) -> None:
    conn = sqlite3.connect(str(args.db))
    oids = [r[0] for r in conn.execute(
        "SELECT id FROM opinions ORDER BY id").fetchall()]
    conn.close()
    if args.limit:
        oids = oids[:args.limit]
    print(f"Opinions to scan: {len(oids)}  (workers={args.workers})")

    work = [(str(args.db), str(args.refs), oid, args.near_sim, args.major_sim)
            for oid in oids]
    start = time.time()
    results: list[CompareResult] = []
    if args.workers > 1:
        with mp.Pool(args.workers) as pool:
            for i, r in enumerate(pool.imap_unordered(_compare_one, work, chunksize=20), 1):
                results.append(r)
                if i % 1000 == 0:
                    el = time.time() - start
                    rate = i / el if el else 0
                    print(f"  {i}/{len(oids)} ({rate:.0f}/s, ETA {(len(oids)-i)/rate/60:.1f}m)")
    else:
        for w in work:
            results.append(_compare_one(w))

    # Worst-similarity first so genuine divergence floats to the top.
    results.sort(key=lambda r: (r.similarity, -r.diff_words, r.opinion_id))
    _write_compare_csv(results, args.csv)
    _write_compare_report(results, args.out)
    _print_compare_summary(results, args.out, args.csv, time.time() - start)


def _print_compare_summary(results, out, csv_path, elapsed) -> None:
    from collections import Counter
    c = Counter(r.status for r in results)
    print(f"\nDone in {elapsed/60:.1f}m.  {len(results)} opinions.")
    for k in ("identical", "near", "moderate", "major", "missing", "unreadable", "non-comparable"):
        print(f"  {k:16} {c.get(k, 0)}")
    print(f"\nReport: {out}\nCSV:    {csv_path}")


def _write_compare_csv(results, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["opinion_id", "citation", "case_name", "date_filed",
                    "reporter", "status", "db_words", "src_words",
                    "diff_words", "similarity", "source_path"])
        for r in results:
            w.writerow([r.opinion_id, r.citation, r.case_name, r.date_filed,
                        r.reporter, r.status, r.db_words, r.src_words,
                        r.diff_words, f"{r.similarity:.4f}", r.source_path])


def _write_compare_report(results, path: Path) -> None:
    from collections import Counter
    c = Counter(r.status for r in results)
    major = [r for r in results if r.status == "major"]
    moderate = [r for r in results if r.status == "moderate"]
    missing = [r for r in results if r.status == "missing"]
    unread = [r for r in results if r.status == "unreadable"]

    L: list[str] = ["# Refs-vs-DB text comparison (substantive deviations)\n"]
    L.append("DB `text_content` vs the primary `~/refs` source file, normalized "
             "to ignore whitespace, case, punctuation, frontmatter, and HTML "
             "markup. Only word/number-level differences remain; bands are by "
             "difflib similarity over the word sequences.\n")
    L.append(f"- identical:        **{c.get('identical', 0)}**")
    L.append(f"- near (sim ≥ near): **{c.get('near', 0)}**  "
             "(caption/nav/pagination-marker boilerplate, not content drift — CSV only)")
    L.append(f"- moderate:         **{c.get('moderate', 0)}**  (worth a look)")
    L.append(f"- **major:          {c.get('major', 0)}**  "
             "(truncation / wrong pairing / large content gap)")
    L.append(f"- missing source:   {c.get('missing', 0)}")
    L.append(f"- unreadable:       {c.get('unreadable', 0)}")
    L.append(f"- non-comparable (westlaw .doc / image): {c.get('non-comparable', 0)}")
    L.append("")

    for label, bucket in (("Major deviations", major), ("Moderate deviations", moderate)):
        if not bucket:
            continue
        L.append(f"## {label} ({len(bucket)}) — lowest similarity first\n")
        for r in bucket:
            L.append(f"### {r.citation} — {r.case_name}  ")
            L.append(f"opinion {r.opinion_id} · {r.reporter} · sim {r.similarity:.3f} · "
                     f"db {r.db_words}w / refs {r.src_words}w · {r.diff_words} changed · "
                     f"`{r.source_path}`")
            for s in r.samples:
                L.append(f"  - {s}")
            L.append("")

    if missing:
        L.append(f"## Missing source files ({len(missing)})\n")
        for r in missing:
            L.append(f"- {r.citation} — opinion {r.opinion_id} — `{r.source_path}`")
        L.append("")
    if unread:
        L.append(f"## Unreadable / empty after normalization ({len(unread)})\n")
        for r in unread:
            L.append(f"- {r.citation} — opinion {r.opinion_id} "
                     f"(db_words={r.db_words}, src_words={r.src_words}) — `{r.source_path}`")
        L.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L), encoding="utf-8")


# --------------------------------------------------------------------------- #
# citespaces mode
# --------------------------------------------------------------------------- #
#
# N.D.C.C. / N.D.A.C. section numbers are hyphen-joined numeric groups, e.g.
# 12.1-20-03  or  75-02-01.2-01.  A stray space around an internal hyphen
# (12.1-20- 03) breaks the cite.  We anchor on a Century-Code/Admin-Code signal
# to avoid flagging ordinary hyphenated prose or numeric ranges, then look for
# whitespace adjacent to a hyphen inside the following section number.

# Section number with at least two hyphen groups, allowing stray spaces around
# the hyphens. Two+ groups (a-b-c…) is the NDCC/NDAC shape; ordinary ranges are
# a single hyphen and won't anchor to the signal below.
_SECNUM = r"\d{1,3}(?:\.\d+)?(?:\s*-\s*\d{1,3}(?:\.\d+)?){1,}"
_SIGNAL = r"(?:N\.?\s*D\.?\s*C\.?\s*C\.?|N\.?\s*D\.?\s*A\.?\s*C\.?|NDCC|NDAC|§{1,2})"
# signal, then up to a little filler ("§", "ch.", "section", spaces), then the number
_CITE_RE = re.compile(
    rf"{_SIGNAL}[\s§]*(?:ch\.?\s*|sec(?:tion|\.)?\s*|chapter\s*)?(?P<num>{_SECNUM})",
    re.IGNORECASE,
)
_HYPHEN_SPACE_RE = re.compile(r"\s-|-\s")


@dataclass
class CiteSpaceHit:
    opinion_id: int
    citation: str
    bad: str
    context: str


def _scan_citespaces_text(oid: int, citation: str, text: str) -> list[CiteSpaceHit]:
    hits: list[CiteSpaceHit] = []
    for m in _CITE_RE.finditer(text):
        num = m.group("num")
        if _HYPHEN_SPACE_RE.search(num):
            s = max(0, m.start() - 25)
            e = min(len(text), m.end() + 15)
            ctx = re.sub(r"\s+", " ", text[s:e]).strip()
            hits.append(CiteSpaceHit(oid, citation, m.group(0).strip(), ctx))
    return hits


def run_citespaces(args) -> None:
    conn = sqlite3.connect(str(args.db))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, text_content FROM opinions").fetchall()
    cites = {}
    for cid, cit in conn.execute(
        "SELECT opinion_id, citation FROM citations WHERE is_primary = 1"):
        cites.setdefault(cid, cit)
    conn.close()

    hits: list[CiteSpaceHit] = []
    for row in rows:
        cit = cites.get(row["id"], f"opinion-{row['id']}")
        hits.extend(_scan_citespaces_text(row["id"], cit, row["text_content"] or ""))

    # CSV
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["opinion_id", "citation", "bad_cite", "context"])
        for h in hits:
            w.writerow([h.opinion_id, h.citation, h.bad, h.context])

    # Markdown
    L = ["# Stray spaces inside N.D.C.C. / N.D.A.C. citations\n",
         f"Hits: **{len(hits)}** across {len({h.opinion_id for h in hits})} opinions.\n"]
    if hits:
        L.append("| opinion | primary cite | bad citation | context |")
        L.append("|---------|--------------|--------------|---------|")
        for h in hits:
            bad = h.bad.replace("|", "\\|")
            ctx = h.context.replace("|", "\\|")
            L.append(f"| {h.opinion_id} | {h.citation} | `{bad}` | …{ctx}… |")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(L), encoding="utf-8")

    print(f"Stray-space citation hits: {len(hits)} "
          f"across {len({h.opinion_id for h in hits})} opinions.")
    print(f"Report: {args.out}\nCSV:    {args.csv}")


# --------------------------------------------------------------------------- #
# selfcheck mode — triage the `major` bucket by DB self-consistency
# --------------------------------------------------------------------------- #
#
# `compare` flags DB-vs-markdown divergence, but the markdown source is a poor
# oracle: it gets renamed/misfiled, regenerated stale, or bloated with duplicate
# CL copies. This mode re-judges each major-bucket opinion by signals that point
# at the DB itself rather than at the disk file:
#
#   * does the DB body state its OWN neutral cite? (1997+)        — swap/contam
#   * do the case_name's distinctive party surnames appear in it? — contamination
#   * the PDF as authoritative oracle (where one exists), but only after
#     confirming the PDF is not itself misfiled (its in-body cite == label).
#   * does the source_path FILE actually contain this opinion?    — crossed ptr
#
# Categories (priority order): DB_CONTENT_BUG > DB_TRUNCATED > DISK_PDF_MISFILED
# > DISK_SOURCE_MISFILED > DISK_SOURCE_NOISE > REVIEW.

_NEUTRAL_RE = re.compile(r"\b(?:18|19|20)\d{2} ND \d+\b")
_CAPTION_STOP = {
    "state", "north", "dakota", "interest", "matter", "estate", "city",
    "county", "disciplinary", "board", "application", "reinstatement", "the",
    "and", "et", "al", "inc", "co", "company", "corp", "llc", "llp", "ltd",
    "life", "insurance", "group", "trust", "bank", "department", "commission",
    "petition", "discipline", "against", "member", "bar", "supreme", "court",
}


def _distinctive_surnames(case_name: str) -> list[str]:
    toks = re.findall(r"[A-Z][A-Za-z'’-]{3,}", case_name or "")
    return [t for t in toks if t.lower() not in _CAPTION_STOP]


def _pdf_text(year: str, num: str, cache: dict, refs: Path) -> str | None:
    key = (year, num)
    if key in cache:
        return cache[key]
    import subprocess
    pdf = refs / "pdfs" / year / f"{year}ND{num}.pdf"
    txt = None
    if pdf.exists():
        try:
            txt = subprocess.run(["pdftotext", str(pdf), "-"],
                                 capture_output=True, text=True, timeout=60).stdout
        except (OSError, subprocess.SubprocessError):
            txt = None
    cache[key] = txt
    return txt


def run_selfcheck(args) -> None:
    # major-bucket oids come from a prior `compare` CSV
    rows = [r for r in csv.DictReader(open(args.in_csv))
            if r["status"] in (args.bucket.split(","))]
    conn = sqlite3.connect(str(args.db))
    conn.row_factory = sqlite3.Row
    refs = args.refs
    pdfcache: dict = {}
    out = []
    for r in rows:
        oid = int(r["opinion_id"])
        op = conn.execute(
            "SELECT case_name, date_filed, source_path, text_content FROM opinions WHERE id=?",
            (oid,)).fetchone()
        neutral = conn.execute(
            "SELECT citation FROM citations WHERE opinion_id=? AND reporter='ND-neutral' LIMIT 1",
            (oid,)).fetchone()
        label = neutral["citation"] if neutral else None  # native neutral (1997+)
        body = strip_frontmatter(op["text_content"] or "")
        body_cites = set(_NEUTRAL_RE.findall(body))

        # --- DB self-consistency ---
        db_states_own = (label in body_cites) if label else None
        surnames = _distinctive_surnames(op["case_name"])
        name_in_body = (any(s.lower() in body.lower() for s in surnames)
                        if surnames else None)

        # --- source_path file identity (1997+) ---
        src = load_source_text(r["reporter"], op["source_path"], refs)
        src_states_label = (label in set(_NEUTRAL_RE.findall(src))) if (src and label) else None

        # --- PDF oracle (1997+) ---
        pdf_words = pdf_states_label = db_pdf_ratio = None
        if label:
            m = re.match(r"(\d{4}) ND (\d+)", label)
            if m:
                pt = _pdf_text(m.group(1), m.group(2), pdfcache, refs)
                if pt is not None:
                    pdf_words = len(normalize_words(pt))
                    pdf_states_label = label in set(_NEUTRAL_RE.findall(pt))
                    dbw = int(r["db_words"]) or 1
                    db_pdf_ratio = round(dbw / pdf_words, 3) if pdf_words else None

        # --- categorize ---
        if (db_states_own is False) or (name_in_body is False):
            cat = "DB_CONTENT_BUG"          # DB text is the wrong/contaminated opinion
        elif pdf_states_label and db_pdf_ratio is not None and db_pdf_ratio < 0.7:
            cat = "DB_TRUNCATED"            # PDF is the right case; DB is much shorter
        elif pdf_states_label is False:
            cat = "DISK_PDF_MISFILED"       # PDF on disk is a different opinion
        elif src_states_label is False:
            cat = "DISK_SOURCE_MISFILED"    # source_path points at the wrong file
        elif label is None:
            cat = "PRE1997_NO_NEUTRAL"      # can't cite-check; mostly CL-fulltext/dedup noise
        else:
            cat = "DISK_SOURCE_NOISE"       # DB self-consistent; markdown stale/bloated
        out.append(dict(
            oid=oid, label=label or r["citation"], case_name=op["case_name"][:42],
            cat=cat, db_states_own=db_states_own, name_in_body=name_in_body,
            src_states_label=src_states_label, pdf_states_label=pdf_states_label,
            db_words=r["db_words"], pdf_words=pdf_words, db_pdf_ratio=db_pdf_ratio,
            sim=r["similarity"], source_path=op["source_path"]))
    conn.close()

    from collections import Counter
    order = ["DB_CONTENT_BUG", "DB_TRUNCATED", "DISK_PDF_MISFILED",
             "DISK_SOURCE_MISFILED", "PRE1997_NO_NEUTRAL", "DISK_SOURCE_NOISE", "REVIEW"]
    counts = Counter(o["cat"] for o in out)
    out.sort(key=lambda o: (order.index(o["cat"]) if o["cat"] in order else 99, str(o["label"])))

    # CSV
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)

    # report
    L = [f"# Major-bucket self-consistency triage ({len(out)} opinions)\n",
         "Re-judged by DB self-consistency + PDF oracle, not the markdown source.\n"]
    for c in order:
        if counts.get(c):
            L.append(f"- **{c}**: {counts[c]}")
    L.append("")
    real = [o for o in out if o["cat"] in ("DB_CONTENT_BUG", "DB_TRUNCATED")]
    if real:
        L.append(f"## Genuine DB bugs ({len(real)})\n")
        L.append("| oid | label | case_name | category | db/pdf words | ratio | states own cite | name in body |")
        L.append("|--|--|--|--|--|--|--|--|")
        for o in real:
            L.append(f"| {o['oid']} | {o['label']} | {o['case_name']} | {o['cat']} | "
                     f"{o['db_words']}/{o['pdf_words']} | {o['db_pdf_ratio']} | "
                     f"{o['db_states_own']} | {o['name_in_body']} |")
        L.append("")
    for c in ("DISK_PDF_MISFILED", "DISK_SOURCE_MISFILED"):
        items = [o for o in out if o["cat"] == c]
        if items:
            L.append(f"## {c} ({len(items)}) — DB is correct; ~/refs file is wrong\n")
            L.append("| oid | label | case_name | source_path |")
            L.append("|--|--|--|--|")
            for o in items:
                L.append(f"| {o['oid']} | {o['label']} | {o['case_name']} | `{o['source_path']}` |")
            L.append("")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(L), encoding="utf-8")

    print(f"Self-consistency triage of {len(out)} opinions:")
    for c in order:
        if counts.get(c):
            print(f"  {c:24} {counts[c]}")
    print(f"\nReport: {args.out}\nCSV:    {args.csv}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="mode", required=True)

    pc = sub.add_parser("compare", help="DB text_content vs ~/refs primary source")
    pc.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    pc.add_argument("--refs", type=Path, default=DEFAULT_REFS_DIR)
    pc.add_argument("--workers", type=int, default=max(1, mp.cpu_count() - 1))
    pc.add_argument("--limit", type=int)
    pc.add_argument("--near-sim", type=float, default=0.97,
                    help="sim ≥ this → 'near' (boilerplate noise), not listed (default 0.97)")
    pc.add_argument("--major-sim", type=float, default=0.85,
                    help="sim < this → 'major' (real divergence) (default 0.85)")
    pc.add_argument("--out", type=Path, default=Path("triage") / "refs-diff.md")
    pc.add_argument("--csv", type=Path, default=Path("triage") / "refs-diff.csv")
    pc.set_defaults(func=run_compare)

    ps = sub.add_parser("citespaces", help="stray spaces in N.D.C.C./N.D.A.C. cites")
    ps.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ps.add_argument("--out", type=Path, default=Path("triage") / "cite-spaces.md")
    ps.add_argument("--csv", type=Path, default=Path("triage") / "cite-spaces.csv")
    ps.set_defaults(func=run_citespaces)

    pk = sub.add_parser("selfcheck",
                        help="re-triage compare's major bucket by DB self-consistency + PDF oracle")
    pk.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    pk.add_argument("--refs", type=Path, default=DEFAULT_REFS_DIR)
    pk.add_argument("--in-csv", type=Path, default=Path("triage") / "refs-diff.csv",
                    help="a prior `compare` CSV to draw bucket oids from")
    pk.add_argument("--bucket", default="major",
                    help="comma-separated statuses to triage (default: major)")
    pk.add_argument("--out", type=Path, default=Path("triage") / "refs-diff-selfcheck.md")
    pk.add_argument("--csv", type=Path, default=Path("triage") / "refs-diff-selfcheck.csv")
    pk.set_defaults(func=run_selfcheck)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
