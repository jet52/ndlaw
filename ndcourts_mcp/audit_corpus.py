"""Cross-corpus systematic-error audit (read-only triage detectors).

Complements ``invariants.py``: invariants are pass/fail health gates on the
opinions DB; these are *triage detectors* for the kinds of errors that creep
into a multi-source collection (OCR drift, dropped text, stale dates, broken
cross-references). Each check prints a summary line and writes a detail TSV
under ``triage/`` for human review. Nothing here writes to any database.
(``audit.py`` is the older missing-opinions audit; this module is the
TODO-audit.md Tier-1 check suite.)

Checks:
  cite_temporal       an opinion cannot cite a case decided after it
  pinpoint_range      a cite to "YYYY ND n, ¶ P" where our copy of that
                      opinion has fewer than P paragraphs = truncation signal
  para_continuity     [¶1]..[¶N] body markers ascending without gaps
  xref_resolve        NDCC/NDAC/rule/const cites in opinions resolve to a
                      provision in the matching corpus DB
  version_intervals   provision_versions timelines are well-formed
  changelog_doc_sync  every DB changelog batch is narrated in CHANGELOG-data*.md

Usage:
    python -m ndcourts_mcp.audit_corpus [--db PATH] [--checks a,b,c]
                                         [--tsv-dir DIR] [--json]
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path

from . import corpus as corpus_mod
from .db import DEFAULT_DB_PATH
from .justices import KNOWN_LAST_NAMES

REPO_ROOT = Path(__file__).resolve().parent.parent

# Body paragraph markers: the analyzer writes [¶1]; some sources render [¶ 1].
_MARKER_RE = re.compile(r"\[¶\s*(\d+)\]")
# Neutral-cite pincite inside a raw cite string: "2024 ND 8, ¶ 6" / "¶¶ 7-9".
_PIN_RE = re.compile(r"(\d{4} ND \d+)\s*,\s*¶¶?\s*(\d+)(?:\s*[-–—]\s*(\d+))?")
_NEUTRAL_GLOB = "[0-9][0-9][0-9][0-9] ND *"

# Known court typos, preserved verbatim per feedback_preserve_source_typos —
# the citing opinion's own PDF prints this (cite, pincite) pair. Keyed
# (citing_oid, cited_cite, pincite). Audited 2026-06-09.
_KNOWN_COURT_PINCITES = {
    (16446, "2004 ND 87", 18),  # PDF prints "Jaste v. Gailfus, 2004 ND 87, ¶ 18" — Jaste is 2004 ND 94
    (14777, "2006 ND 6", 25),   # print: "2006 ND 6, ¶ 25, 604 N.W.2d 445" — Dvorak is 2000 ND 6 (verified 2026-06-10)
    (13063, "1999 ND 141", 22), # print: "Henry, 1999 ND 141, ¶ 22" — Henry is 1998 ND 141 (verified 2026-06-10)
    (15011, "2003 ND 133", 15), # print: "Rist ..., 2003 ND 133, ¶ 15, 665 N.W.2d 45" — Rist is 2003 ND 113 (verified 2026-06-10)
    (15834, "1998 ND 155", 28), # print: "Clark, 1998 ND 155, ¶ 28, 583 N.W.2d 377" — Clark is 1998 ND 153 (verified 2026-06-10)
}

SAMPLE_LIMIT = 5


@dataclass
class AuditResult:
    name: str
    description: str
    flagged: int
    detail_path: Path | None = None
    notes: list[str] = field(default_factory=list)
    samples: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "flagged": self.flagged,
            "detail": str(self.detail_path) if self.detail_path else None,
            "notes": self.notes,
            "samples": self.samples,
        }


def _write_tsv(path: Path, header: list[str], rows: list[tuple]) -> Path | None:
    if not rows:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return path


# ---------------------------------------------------------------- checks


def check_cite_temporal(conn: sqlite3.Connection, tsv_dir: Path, tag: str) -> AuditResult:
    """Flag cited_by edges where the citing opinion predates the cited one.

    Same-day edges are fine (lead + companion released together). A wrong
    date on a much-cited opinion violates many edges at once, so sorting by
    cited oid surfaces the offender quickly.
    """
    rows = conn.execute(
        """
        SELECT cb.citing_opinion_id, co.case_name, co.date_filed,
               cb.cited_opinion_id, cd.case_name, cd.date_filed,
               cb.citation,
               CAST(julianday(cd.date_filed) - julianday(co.date_filed) AS INTEGER) AS gap_days
        FROM cited_by cb
        JOIN opinions co ON co.id = cb.citing_opinion_id
        JOIN opinions cd ON cd.id = cb.cited_opinion_id
        WHERE co.date_filed < cd.date_filed
        ORDER BY gap_days DESC
        """
    ).fetchall()
    buckets = {"1-30d": 0, "31-365d": 0, ">365d": 0}
    for r in rows:
        g = r[7]
        buckets["1-30d" if g <= 30 else "31-365d" if g <= 365 else ">365d"] += 1
    detail = _write_tsv(
        tsv_dir / f"audit-cite-temporal-{tag}.tsv",
        ["citing_oid", "citing_name", "citing_date", "cited_oid", "cited_name",
         "cited_date", "edge_citation", "gap_days"],
        [tuple(r) for r in rows],
    )
    return AuditResult(
        "cite_temporal",
        "cited_by edges where citing opinion predates the cited opinion",
        len(rows),
        detail,
        notes=[f"gap buckets: {buckets}",
               "1-30d gaps are often advance-sheet/rehearing artifacts; "
               ">365d gaps usually mean one side's date_filed is wrong"],
        samples=[f"oid{r[0]} ({r[2]}) cites oid{r[3]} ({r[5]}) via {r[6]}"
                 for r in rows[:SAMPLE_LIMIT]],
    )


def _max_marker_cache(conn: sqlite3.Connection):
    cache: dict[int, int | None] = {}

    def max_marker(oid: int) -> int | None:
        if oid not in cache:
            row = conn.execute(
                "SELECT text_content FROM opinions WHERE id = ?", (oid,)
            ).fetchone()
            if row is None or not row[0]:
                cache[oid] = None
            else:
                nums = [int(m) for m in _MARKER_RE.findall(row[0])]
                cache[oid] = max(nums) if nums else None
        return cache[oid]

    return max_marker


def check_pinpoint_range(conn: sqlite3.Connection, tsv_dir: Path, tag: str) -> AuditResult:
    """Flag pincites (¶ P) that exceed the cited opinion's highest [¶N] marker.

    The citing court read a paragraph we don't have: either our copy of the
    cited opinion is truncated / lost its markers, or the pincite was
    garbled in extraction. Either way it's worth a look.
    """
    # neutral cite -> oid (skip the cites that map to more than one opinion)
    neutral: dict[str, int] = {}
    ambiguous: set[str] = set()
    for cite, oid in conn.execute(
        "SELECT citation, opinion_id FROM citations WHERE citation GLOB ?",
        (_NEUTRAL_GLOB,),
    ):
        if cite in neutral and neutral[cite] != oid:
            ambiguous.add(cite)
        neutral[cite] = oid
    max_marker = _max_marker_cache(conn)

    flagged_rows: list[tuple] = []
    checked = skipped_no_markers = 0
    for citing_oid, raw in conn.execute(
        "SELECT opinion_id, raw_text FROM text_citations "
        "WHERE cite_type = 'case' AND raw_text LIKE '%¶%'"
    ):
        for cite, p1, p2 in _PIN_RE.findall(raw):
            if cite in ambiguous or cite not in neutral:
                continue
            cited_oid = neutral[cite]
            if cited_oid == citing_oid:
                continue
            pin = max(int(p1), int(p2) if p2 else 0)
            top = max_marker(cited_oid)
            if top is None:
                skipped_no_markers += 1
                continue
            checked += 1
            if pin > top and (citing_oid, cite, pin) not in _KNOWN_COURT_PINCITES:
                flagged_rows.append((citing_oid, cite, cited_oid, pin, top, raw.strip()))
    flagged_rows.sort(key=lambda r: r[3] - r[4], reverse=True)
    detail = _write_tsv(
        tsv_dir / f"audit-pinpoint-range-{tag}.tsv",
        ["citing_oid", "cited_neutral_cite", "cited_oid", "pincite_para",
         "max_marker_in_db", "raw_cite_text"],
        flagged_rows,
    )
    return AuditResult(
        "pinpoint_range",
        "pincites ¶P beyond the cited opinion's highest [¶N] marker",
        len(flagged_rows),
        detail,
        notes=[f"{checked} pincites checked; {skipped_no_markers} skipped "
               f"(cited opinion has no markers); {len(ambiguous)} ambiguous neutral cites"],
        samples=[f"oid{r[0]} cites {r[1]} ¶{r[3]} but oid{r[2]} tops out at ¶{r[4]}"
                 for r in flagged_rows[:SAMPLE_LIMIT]],
    )


# Opinions whose marker "defects" are verbatim quotations of ANOTHER
# document's numbered paragraphs (per-item verified against the court PDF /
# archive HTML) — the court's own text, not extraction loss. Do not flag.
_KNOWN_QUOTED_DOC_MARKERS = {
    17357,  # Helbling, 2019 ND 27 — quotes the divorce settlement agreement's
            # ¶15/¶21/¶33; opinion itself is ¶1-21 complete (verified 2026-06-10)
    12605,  # Wodrich, 1998 ND 9 — out-of-order ¶38/39/45 are a block quote;
            # matches the archive HTML (verified 2026-06-09)
    20124,  # Anne Carlsen Center — court PDF prints embedded quoted order with
            # its own ¶ numbering (verified 2026-06-09)
    20408,  # Simpson — same embedded-quoted-order class (verified 2026-06-09)
}


def check_para_continuity(conn: sqlite3.Connection, tsv_dir: Path, tag: str) -> AuditResult:
    """Flag opinions whose [¶N] sequence has gaps, restarts, or a bad start.

    A gap means a body paragraph went missing (extraction drop or source
    defect). Non-monotonic markers are usually a block quote of another
    modern opinion's markers — real but lower-signal; gaps are the find.
    Per-item-verified quoted-document cases are baselined in
    _KNOWN_QUOTED_DOC_MARKERS.
    """
    rows: list[tuple] = []
    n_checked = 0
    cur = conn.execute(
        "SELECT id, case_name, date_filed, text_content FROM opinions "
        "WHERE text_content LIKE '%[¶%'"
    )
    for oid, name, date, text in cur:
        if oid in _KNOWN_QUOTED_DOC_MARKERS:
            continue
        nums = [int(m) for m in _MARKER_RE.findall(text)]
        if not nums:
            continue
        n_checked += 1
        issues: list[str] = []
        if nums[0] != 1:
            issues.append(f"START_AT_{nums[0]}")
        gaps: list[str] = []
        nonmono = 0
        prev = nums[0]
        for n in nums[1:]:
            if n == prev + 1:
                prev = n
            elif n <= prev:
                nonmono += 1  # likely a quoted marker; don't advance prev
            else:
                gaps.append(f"{prev + 1}-{n - 1}" if n - prev > 2 else str(prev + 1))
                prev = n
        if gaps:
            issues.append("GAP:" + ",".join(gaps[:10]))
        if nonmono:
            issues.append(f"NONMONO:{nonmono}")
        if issues:
            rows.append((oid, name, date, max(nums), ";".join(issues)))
    gap_count = sum(1 for r in rows if "GAP:" in r[4])
    rows.sort(key=lambda r: ("GAP:" not in r[4], r[2]))
    detail = _write_tsv(
        tsv_dir / f"audit-para-continuity-{tag}.tsv",
        ["oid", "case_name", "date_filed", "max_marker", "issues"],
        rows,
    )
    return AuditResult(
        "para_continuity",
        "[¶N] marker sequences with gaps / restarts / bad start",
        len(rows),
        detail,
        notes=[f"{n_checked} marked opinions scanned; {gap_count} have GAPs "
               "(the high-signal subset — NONMONO alone is usually a block quote)"],
        samples=[f"oid{r[0]} {r[1]} ({r[2]}): {r[4][:80]}" for r in rows[:SAMPLE_LIMIT]],
    )


# A neutral cite and its adjacent N.W.2d/3d parallel inside one citation string.
_PAIR_RE = re.compile(
    r"(\d{4} ND \d+)\s*,\s*(?:¶¶?\s*[\d\s,–—-]{1,16},\s*)?(\d+\s*N\.W\.[23]d\s*\d+)")
# Known court typos (the court's own PDF prints the inconsistent pair) —
# preserved verbatim per feedback_preserve_source_typos. (citing_oid, nd, nw).
_KNOWN_COURT_PAIRS = {
    (16446, "2004 ND 87", "679 N.W.2d 257"),   # "Jaste v. Gailfus, 2004 ND 87" (Jaste is 2004 ND 94)
    (14127, "2004 ND 46", "674 N.W.2d 402"),   # Muhammed parallel is 675 N.W.2d 402
    (16894, "2006 ND 98", "716 N.W.2d 535"),   # Pace parallel is 713 N.W.2d 535
    (16184, "2013 ND 137", "835 N.W.2d 836"),  # Hoffman parallel is 834 N.W.2d 636; print verified 2026-06-09
    (16917, "2011 ND 64", "795 N.W.2d 194"),   # Johnson v. Hovland parallel is 795 N.W.2d 294; print verified 2026-06-09
    (14777, "2006 ND 6", "604 N.W.2d 445"),    # Dvorak is 2000 ND 6; print verified 2026-06-10
    (13063, "1999 ND 141", "581 N.W.2d 921"),  # Henry is 1998 ND 141; print verified 2026-06-10
    (15011, "2003 ND 133", "665 N.W.2d 45"),   # Rist is 2003 ND 113; print verified 2026-06-10
    (15834, "1998 ND 155", "583 N.W.2d 377"),  # Ohio Cas. v. Clark is 1998 ND 153; print verified 2026-06-10
    # pass-3 court typos, every one print-verified 2026-06-10 (crops in triage/flipverify-corpus/pass3/):
    (12875, "1998 ND 7", "574 N.W.2d 801"),    # Paulson is 1998 ND 17
    (12920, "1997 ND 76", "652 N.W.2d 750"),   # Dakutak is 562 N.W.2d 750
    (13927, "2002 ND 44", "640 N.W.2d 617"),   # Henderson is 640 N.W.2d 714
    (14719, "1997 ND 61", "506 N.W.2d 903"),   # Stout is 560 N.W.2d 903
    (15087, "2006 ND 146", "718 N.W.2d 01"),   # print literally reads "718 N.W.2d 01"
    (15308, "1999 ND 125", "579 N.W.2d 406"),  # Rockwell is 597 N.W.2d 406
    (15869, "2011 ND 234", "812 N.W.2d 484"),  # Jones is 817 N.W.2d 313 (court miscites vol+page)
    (16413, "2000 ND 12", "604 N.W.2d 543"),   # Lyon is 604 N.W.2d 453
    (16533, "2014 ND 17", "842 N.W.2d 64"),    # Howe is 842 N.W.2d 646 (truncated in print)
    # parallel-pair triage, print-verified 2026-06-10:
    (13031, "1999 ND 218", "587 N.W.2d 423"),  # Lee is 1998 ND 218
    (13124, "1999 ND 5", "689 N.W.2d 566"),    # Ebach is 589 N.W.2d 566
    (16816, "2014 ND 102", "346 N.W.2d 724"),  # Datz is 846 N.W.2d 724
    (14391, "1997 ND 223", "575 N.W.2d 635"),  # Harmon is 1997 ND 233
    (13208, "1998 ND 89", "578 N.W.2d 129"),   # Gibson; printed parallel belongs to Moch (578 N.W.2d 129)
    (15948, "1999 ND 181", "599 N.W.3d 323"),  # Svedberg; print genuinely reads N.W.3d (impossible series, glyph-verified)
}
# NOTE: every entry above (and in _KNOWN_COURT_PINCITES) is also registered in
# opinions.db's `print_anomalies` table — the authoritative, shipped registry of
# verified typos in the court's print, with intended readings, graph overrides
# (cite_extract.apply_print_anomaly_overrides), and West-corrected-page
# follow-up notes. Keep the two in sync when adding entries.


def check_parallel_pair(conn: sqlite3.Connection, tsv_dir: Path, tag: str) -> AuditResult:
    """Neutral + N.W. parallel in one citation string must co-resolve.

    The detector that exposed the OCR digit-flip class (3<->8, 5<->6) and the
    missing-parallel backfill (2026-06-09). A mismatch is one of: digit flip in
    the citing text, a missing/cross-wired parallel on the cited row, or a
    court typo (baseline-listed). Worked queues live in
    triage/backfill-parallel-candidates-*.tsv and class3-clusters-*.tsv.
    """
    def build(globpat):
        m, ambig = {}, set()
        for cite, oid in conn.execute(
            "SELECT citation, opinion_id FROM citations WHERE citation GLOB ?", (globpat,)
        ):
            if cite in m and m[cite] != oid:
                ambig.add(cite)
            m[cite] = oid
        return m, ambig

    nd_map, nd_ambig = build(_NEUTRAL_GLOB)
    nw_map, nw_ambig = {}, set()
    for pat in ("* N.W.2d *", "* N.W.3d *"):
        m, a = build(pat)
        nw_map.update(m)
        nw_ambig.update(a)

    rows: list[tuple] = []
    n_pairs = n_ok = 0
    for oid, name, date, text in conn.execute(
        "SELECT id, case_name, date_filed, text_content FROM opinions "
        "WHERE date_filed >= '1997-01-01'"
    ):
        if not text:
            continue
        for m in _PAIR_RE.finditer(text):
            nd, nw = m.group(1), " ".join(m.group(2).split())
            if nd in nd_ambig or nw in nw_ambig:
                continue
            nd_oid, nw_oid = nd_map.get(nd), nw_map.get(nw)
            if nd_oid is None and nw_oid is None:
                continue
            n_pairs += 1
            if nd_oid == nw_oid or (oid, nd, nw) in _KNOWN_COURT_PAIRS:
                n_ok += 1
                continue
            ctx = " ".join(text[max(0, m.start() - 80):m.end() + 10].split())
            rows.append((oid, name[:40], date, nd, nd_oid or "", nw, nw_oid or "", ctx[:160]))
    detail = _write_tsv(
        tsv_dir / f"audit-parallel-pair-{tag}.tsv",
        ["citing_oid", "citing_name", "citing_date", "nd_cite", "nd_oid",
         "nw_cite", "nw_oid", "context"],
        rows,
    )
    cross = sum(1 for r in rows if r[4] and r[6])
    return AuditResult(
        "parallel_pair",
        "neutral + N.W. parallel in one citation string resolving to different opinions",
        len(rows),
        detail,
        notes=[f"{n_pairs} pairs checked, {n_ok} consistent "
               f"({100 * n_ok / n_pairs:.1f}%); {cross} cross-wired (both resolve), "
               f"{len(rows) - cross} one-side-unresolved",
               "worked queues: triage/backfill-parallel-candidates-*.tsv (singles/"
               "conflicts/window) + class3-clusters-*.tsv (unverified sibling pairs)"],
        samples=[f"oid{r[0]}: {r[3]} vs {r[5]}" for r in rows[:SAMPLE_LIMIT]],
    )


# cite_type -> (corpus name, normalized-prefix filter)
_XREF_CORPORA = {
    "statute": ("ndcc", "N.D.C.C."),
    "regulation": ("admin", "N.D.A.C."),
    "court_rule": ("rule", "N.D."),
    "constitution": ("const", "N.D. Const."),
}
_CHAPTER_RE = re.compile(r"\bch\.?\s+([\d.\-]+)")


def check_xref_resolve(conn: sqlite3.Connection, tsv_dir: Path, tag: str) -> AuditResult:
    """Resolve opinion statute/rule/const/admin cites against the corpus DBs.

    Two corpora witnessing each other: an unresolved cite is either a garbled
    extraction on the opinions side or a missing/renumbered provision on the
    corpus side. Old opinions legitimately cite repealed or renumbered law,
    so the modern-citer count is the high-signal column.
    """
    keysets: dict[str, set[str]] = {}
    missing_dbs: list[str] = []
    for cname in ("ndcc", "admin", "rule", "const"):
        try:
            path = corpus_mod.resolve_corpus_db_path(cname)
            cconn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            keysets[cname] = {k for (k,) in cconn.execute("SELECT cite_key FROM provisions")}
            cconn.close()
        except Exception:
            missing_dbs.append(cname)
    if not keysets:
        return AuditResult("xref_resolve", "corpus cross-reference resolution", 0,
                           notes=["no corpus DBs found — skipped"])

    # chapter-existence stems precomputed per corpus for speed
    chapter_stems: dict[str, set[str]] = {
        c: {k.rsplit("-", 1)[0] for k in keys if "-" in k}
        for c, keys in keysets.items()
    }

    unresolved: dict[tuple[str, str], list] = {}
    stats = {c: {"checked": 0, "resolved": 0, "unchecked_form": 0} for c in keysets}
    for norm, ctype, citing_oid, date in conn.execute(
        """
        SELECT tc.normalized, tc.cite_type, tc.opinion_id, o.date_filed
        FROM text_citations tc JOIN opinions o ON o.id = tc.opinion_id
        WHERE tc.cite_type IN ('statute', 'regulation', 'court_rule', 'constitution')
        """
    ):
        cname, prefix = _XREF_CORPORA[ctype]
        if cname not in keysets or not norm.startswith(prefix):
            continue  # foreign authority (C.F.R., U.S. Const., other states)
        stats[cname]["checked"] += 1
        keys = keysets[cname]
        chap = _CHAPTER_RE.search(norm)
        resolved = False
        if chap:
            # chapter cite: resolved if any section of that chapter exists
            key_prefix = "ndac" if cname == "admin" else cname
            resolved = f"{key_prefix} {chap.group(1)}" in chapter_stems[cname]
        elif "tit." in norm:
            stats[cname]["unchecked_form"] += 1
            continue
        else:
            base = re.sub(r"\(.*$", "", norm).strip().rstrip(",;. ")
            resolved = corpus_mod.cite_key(base) in keys
        if resolved:
            stats[cname]["resolved"] += 1
            continue
        ent = unresolved.setdefault((cname, norm), [0, 0, []])
        ent[0] += 1
        if date and date >= "1997-01-01":
            ent[1] += 1
        if len(ent[2]) < 3:
            ent[2].append(str(citing_oid))

    rows = sorted(
        ((c, n, v[0], v[1], ",".join(v[2])) for (c, n), v in unresolved.items()),
        key=lambda r: (-r[3], -r[2]),
    )
    detail = _write_tsv(
        tsv_dir / f"audit-xref-unresolved-{tag}.tsv",
        ["corpus", "normalized_cite", "n_citing_opinions", "n_modern_citers",
         "sample_oids"],
        rows,
    )
    modern_flagged = sum(1 for r in rows if r[3] > 0)
    notes = [
        f"{c}: {s['checked']} checked, {s['resolved']} resolved, "
        f"{s['checked'] - s['resolved'] - s['unchecked_form']} unresolved"
        + (f", {s['unchecked_form']} unchecked title-form" if s["unchecked_form"] else "")
        for c, s in stats.items()
    ]
    if missing_dbs:
        notes.append(f"corpus DBs not found, skipped: {missing_dbs}")
    notes.append(f"{len(rows)} distinct unresolved cites total; "
                 f"{modern_flagged} have a 1997+ citer (high-signal)")
    return AuditResult(
        "xref_resolve",
        "opinion cites to ND statutes/rules/const/admin resolving to no provision",
        modern_flagged,
        detail,
        notes=notes,
        samples=[f"{r[0]}: {r[1]} (cited by {r[2]}, modern {r[3]})"
                 for r in rows[:SAMPLE_LIMIT]],
    )


def check_version_intervals(tsv_dir: Path, tag: str) -> AuditResult:
    """Validate provision_versions timelines in every corpus DB.

    Flags: effective_start >= effective_end; more than one open (NULL-end)
    version per provision; overlapping version intervals; a
    current_version_id that dangles or points at a closed version while an
    open one exists.
    """
    rows: list[tuple] = []
    scanned: list[str] = []
    for cname in ("const", "rule", "ndcc", "admin"):
        try:
            path = corpus_mod.resolve_corpus_db_path(cname)
            cconn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            cconn.execute("SELECT 1 FROM provisions LIMIT 1")
        except Exception:
            continue
        scanned.append(cname)
        versions: dict[int, list[tuple]] = {}
        for pid, vid, start, end in cconn.execute(
            "SELECT provision_id, id, effective_start, effective_end "
            "FROM provision_versions"
        ):
            versions.setdefault(pid, []).append((vid, start, end))
        cites = dict(cconn.execute("SELECT id, citation FROM provisions"))
        current = dict(cconn.execute("SELECT id, current_version_id FROM provisions"))
        for pid, vers in versions.items():
            cite = cites.get(pid, f"pid{pid}")
            open_vers = [v for v in vers if v[2] is None]
            if len(open_vers) > 1:
                rows.append((cname, cite, "MULTI_OPEN",
                             f"{len(open_vers)} versions with NULL effective_end"))
            for vid, start, end in vers:
                if start and end and start >= end:
                    rows.append((cname, cite, "START_GE_END", f"v{vid}: {start} >= {end}"))
            ordered = sorted(vers, key=lambda v: v[1] or "0000-01-01")
            for (v1, s1, e1), (v2, s2, e2) in zip(ordered, ordered[1:]):
                if (e1 or corpus_mod.OPEN_ENDED) > (s2 or "0000-01-01"):
                    rows.append((cname, cite, "OVERLAP",
                                 f"v{v1}[{s1}..{e1}] overlaps v{v2}[{s2}..{e2}]"))
            cvid = current.get(pid)
            vids = {v[0] for v in vers}
            if cvid is not None and cvid not in vids:
                rows.append((cname, cite, "DANGLING_CURRENT", f"current_version_id={cvid}"))
            elif cvid is not None and open_vers and cvid not in {v[0] for v in open_vers}:
                rows.append((cname, cite, "CURRENT_NOT_OPEN",
                             f"current_version_id={cvid} but an open version exists"))
        cconn.close()
    detail = _write_tsv(
        tsv_dir / f"audit-version-intervals-{tag}.tsv",
        ["corpus", "citation", "issue", "detail"],
        rows,
    )
    return AuditResult(
        "version_intervals",
        "malformed provision_versions timelines in the primary-law DBs",
        len(rows),
        detail,
        notes=[f"scanned: {scanned}"],
        samples=[f"{r[0]} {r[1]}: {r[2]} ({r[3]})" for r in rows[:SAMPLE_LIMIT]],
    )


_BATCH_STEM_RE = re.compile(r"[-_]20\d{2}[-_]?\d{2}[-_]?\d{2}.*$")

# Known-baseline: batches that predate the dual-logging policy or are narrated
# under a different name/doc (audited 2026-06-09; all opinions.db). New
# unnarrated batches flag; these are grandfathered. Shrink this list as
# narratives are backfilled — never grow it without checking the batch really
# is documented elsewhere.
_KNOWN_UNNARRATED_RE = re.compile(
    # April 2026 per-volume Westlaw Quick Check + per-volume casename passes
    # (narrated in aggregate / as ranges, not per batch name)
    r"^westlaw-nd-vol\d+(-\d+)?(-casenames|-fix)?$"
    # 2026-04-05 justice-name OCR normalization series (pre-policy)
    r"|^0\d[a-c]?-[a-z-]+$"
)
_KNOWN_UNNARRATED = frozenset({
    # pre-policy / documented under other names or in TODO-validation.md:
    "fix-neutral-cite-invert-2026-05-24",
    "fix-timm-cite",
    "fix-westlaw-pairings-round2-text-rerun",
    "section6-dedup-2026-05-16",
    "section6-dedup-corpus-2026-05-16",   # narrated in TODO-validation.md §6
    "section6-nocite-brekhus-2026-05-27",  # narrated as "Brekhus text 1" in §6
    "section6-nocite-v2-merge-2026-05-27", # narrated as "widened passes v2/v3/v4"
    "section6-nocite-v3-merge-2026-05-27",
    "section6-nocite-v4-merge-2026-05-27",
    "web-ui",
    "westlaw-low-quality",
})


def _grandfathered(batch: str) -> bool:
    return batch in _KNOWN_UNNARRATED or bool(_KNOWN_UNNARRATED_RE.match(batch))


def check_changelog_doc_sync(conn: sqlite3.Connection, tsv_dir: Path, tag: str) -> AuditResult:
    """Every DB changelog batch should be narrated in CHANGELOG-data*.md.

    Policy (feedback_log_changes): corrections are logged in both the
    changelog table and the markdown narrative. A batch name is matched as a
    substring; a date-stripped stem match also counts (the docs sometimes
    glob a family of batches, e.g. ``fix-casenames-*-2026-05-24``).
    """
    docs = {}
    for fname in ("CHANGELOG-data.md", "CHANGELOG-data-primarylaw.md"):
        p = REPO_ROOT / fname
        docs[fname] = p.read_text() if p.exists() else ""
    all_text = "\n".join(docs.values())

    targets: list[tuple[str, str, sqlite3.Connection]] = [
        ("opinions.db", "CHANGELOG-data.md", conn)
    ]
    extra_conns = []
    for cname in ("const", "rule", "ndcc", "admin"):
        try:
            path = corpus_mod.resolve_corpus_db_path(cname)
            cconn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            cconn.execute("SELECT 1 FROM changelog LIMIT 1")
            targets.append((path.name, "CHANGELOG-data-primarylaw.md", cconn))
            extra_conns.append(cconn)
        except Exception:
            continue

    rows: list[tuple] = []
    total_batches = 0
    for dbname, docname, c in targets:
        for batch, n, first_ts in c.execute(
            "SELECT batch, COUNT(*), MIN(timestamp) FROM changelog GROUP BY batch"
        ):
            total_batches += 1
            if batch in all_text:
                continue
            stem = _BATCH_STEM_RE.sub("", batch)
            if len(stem) > 6 and stem in all_text:
                rows.append((dbname, docname, batch, n, first_ts, "stem-only"))
            elif _grandfathered(batch):
                rows.append((dbname, docname, batch, n, first_ts, "known-baseline"))
            else:
                rows.append((dbname, docname, batch, n, first_ts, "missing"))
    for c in extra_conns:
        c.close()
    missing = [r for r in rows if r[5] == "missing"]
    baseline = sum(1 for r in rows if r[5] == "known-baseline")
    rows.sort(key=lambda r: (r[5] != "missing", r[4] or ""))
    detail = _write_tsv(
        tsv_dir / f"audit-changelog-doc-sync-{tag}.tsv",
        ["db", "expected_doc", "batch", "rows", "first_timestamp", "match"],
        rows,
    )
    return AuditResult(
        "changelog_doc_sync",
        "changelog batches with no CHANGELOG-data*.md narrative",
        len(missing),
        detail,
        notes=[f"{total_batches} batches across {len(targets)} DBs; "
               f"{len(rows) - len(missing) - baseline} matched on date-stripped stem only; "
               f"{baseline} at known baseline (pre-policy / narrated elsewhere)"],
        samples=[f"{r[0]}: {r[2]} ({r[3]} rows, {r[4]})" for r in missing[:SAMPLE_LIMIT]],
    )


# roster fuzzy-match (catalog #11) ------------------------------------------

# Role/suffix tokens that ride along in author/judges and are not names.
_ROLE_TOKENS = {"j", "cj", "sj", "dj", "jr", "sr", "ii", "iii", "iv",
                "chief justice", "justice", "judge", "per curiam"}
# Surrogate/district-judge tokens already split off by the comma-splitter.
_ROLE_RE = re.compile(r"\b(C\.?J\.?|S\.?J\.?|D\.?J\.?|J\.?|Jr\.?|Sr\.?|I{2,3})\b", re.I)


def _lev(a: str, b: str, maxd: int = 2) -> int:
    """Levenshtein distance, early-exiting at maxd+1 (cheap for short names)."""
    if abs(len(a) - len(b)) > maxd:
        return maxd + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        row_best = i
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (0 if ca == cb else 1)))
            row_best = min(row_best, cur[j])
        if row_best > maxd:
            return maxd + 1
        prev = cur
    return prev[-1]


def _name_tokens(author, judges):
    """Yield (field, raw_token, norm) for each candidate name in the two fields."""
    if author and author.strip():
        yield "author", author.strip(), author.strip().lower()
    for tok in (judges or "").split(","):
        raw = tok.strip()
        norm = _ROLE_RE.sub("", raw).strip(" .,").lower()
        if norm:
            yield "judges", raw, norm


# Sorted once so tie-breaking (multiple roster names at equal distance) is
# deterministic across runs — KNOWN_LAST_NAMES is an unordered set.
_ROSTER_SORTED = sorted(KNOWN_LAST_NAMES)


def _nearest_roster(norm: str):
    """(canonical, distance) of the closest roster surname within edit distance 2.
    Ties resolve to the alphabetically-first surname (deterministic)."""
    best, bestd = None, 99
    for name in _ROSTER_SORTED:
        d = _lev(norm, name, 2)
        if d < bestd:
            best, bestd = name, d
            if d == 1:
                break
    return best, bestd


def check_roster_fuzzy(conn: sqlite3.Connection, tsv_dir: Path, tag: str) -> AuditResult:
    """author/judges names within edit distance 1–2 of a roster justice — probable
    OCR typo / formatting garble (NEU-MANN, McEYERS, KAPS-NER, YANDE WALLE).

    Per the surrogate-judges rule we hunt NEAR-MISSES, not tenure: an exact roster
    surname is left alone; a name far from every roster surname is treated as a
    legitimate non-roster (surrogate/district) judge, not flagged. dist-2 is gated
    to names >=6 chars to avoid short-surname noise.
    """
    rows = []
    by_garble: dict[tuple, int] = {}
    for oid, author, judges in conn.execute("SELECT id, author, judges FROM opinions"):
        for field_name, raw, norm in _name_tokens(author, judges):
            if len(norm) < 4 or norm in _ROLE_TOKENS or norm in KNOWN_LAST_NAMES:
                continue
            cand, dist = _nearest_roster(norm)
            if cand is None:
                continue
            if dist == 1 or (dist == 2 and len(norm) >= 6):
                rows.append((oid, field_name, raw, cand, dist))
                by_garble[(norm, cand)] = by_garble.get((norm, cand), 0) + 1
    detail = _write_tsv(
        tsv_dir / f"audit-roster-fuzzy-{tag}.tsv",
        ["opinion_id", "field", "garbled_token", "nearest_roster", "edit_distance"],
        rows,
    )
    top = sorted(by_garble.items(), key=lambda kv: -kv[1])
    d1 = sum(1 for o in rows if o[4] == 1)
    d2 = len(rows) - d1
    return AuditResult(
        "roster_fuzzy",
        "author/judges names within edit distance 1-2 of a roster justice (probable typo/garble)",
        len(rows),
        detail,
        notes=[f"{len(by_garble)} distinct garbled spellings over {len(rows)} occurrences "
               f"({d1} at edit-distance 1, {d2} at distance 2)",
               "distance-1 hits are almost all genuine OCR garbles (Burice→Bruce, "
               "Bueke→Burke, Sature→Sathre); distance-2 needs closer review — a "
               "consistently-spelled name near a roster surname (Anderson, Geiger) may be a "
               "real surrogate/district judge, and stray words (Hearing, Having) are field junk",
               "fix path: normalize each confirmed garble to its canonical surname"],
        samples=[f"{g!r}→{c} (d{_lev(g, c)}, ×{n})"
                 for (g, c), n in top[:SAMPLE_LIMIT]],
    )


# ---------------------------------------------------------------- driver

CHECKS = {
    "cite_temporal": lambda conn, d, t: check_cite_temporal(conn, d, t),
    "pinpoint_range": lambda conn, d, t: check_pinpoint_range(conn, d, t),
    "parallel_pair": lambda conn, d, t: check_parallel_pair(conn, d, t),
    "para_continuity": lambda conn, d, t: check_para_continuity(conn, d, t),
    "xref_resolve": lambda conn, d, t: check_xref_resolve(conn, d, t),
    "roster_fuzzy": lambda conn, d, t: check_roster_fuzzy(conn, d, t),
    "version_intervals": lambda conn, d, t: check_version_intervals(d, t),
    "changelog_doc_sync": lambda conn, d, t: check_changelog_doc_sync(conn, d, t),
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("--checks", help="comma-separated subset of: " + ",".join(CHECKS))
    p.add_argument("--tsv-dir", type=Path, default=REPO_ROOT / "triage")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    names = list(CHECKS) if not args.checks else [c.strip() for c in args.checks.split(",")]
    unknown = [n for n in names if n not in CHECKS]
    if unknown:
        p.error(f"unknown checks: {unknown}")

    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    tag = datetime.date.today().isoformat()
    results = [CHECKS[n](conn, args.tsv_dir, tag) for n in names]
    conn.close()

    if args.json:
        print(json.dumps([r.to_json() for r in results], indent=2))
        return 0

    print(f"Audit ({args.db.name}, {tag}) — triage detectors, not pass/fail gates\n")
    for r in results:
        flag = " ok " if r.flagged == 0 else "FLAG"
        print(f"[{flag}] {r.name:<20} {r.flagged:>6}  {r.description}")
        for note in r.notes:
            print(f"         {note}")
        for s in r.samples:
            print(f"           · {s}")
        if r.detail_path:
            rel = (r.detail_path.relative_to(REPO_ROOT)
                   if r.detail_path.is_relative_to(REPO_ROOT) else r.detail_path)
            print(f"         detail: {rel}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
