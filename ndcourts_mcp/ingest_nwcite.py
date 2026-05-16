"""Ingest the court-sourced NW-cite mirror with tiered text-promotion.

Approved policy (Tufte, 2026-05-15): the court archive is
court-authoritative and, across a 1965-1998 sample, never shorter than
the CL OCR it would replace — so for opinions whose primary is CL-origin
it is a corpus UPGRADE (recovers official syllabi pre-~1978 and
caption/procedural front-matter throughout, strips OCR artifacts), not
merely a cross-check. The gate is the length ratio
= len(court_body)/len(db_body, frontmatter stripped); jaccard is
informational only (it conflates benign OCR with real problems).

For every fetched/cached opinion HTML matched to exactly one DB opinion,
a 'court-archive' source is attached, then:

  * primary is CL-origin (NW2d/NW):
      ratio in [0.95, 1.60]              -> PROMOTE: swap the body
          (frontmatter preserved verbatim), repoint primary, log full
          prior text_content + source_reporter + source_path to
          changelog (authority-stamped), validation_status='corrected'.
      ratio in [0.80,0.95) or (1.60,2.50] -> review band: flagged.
      ratio <0.80 or >2.50               -> manual outlier: flagged
          (possible truncation / multi-opinion page / wrong content).
  * primary is NOT CL-origin (ndcourts.gov/westlaw, 1997+): the existing
    primary is already authoritative — cross-check only, never demote.
  * MATCHED to several opinions: skipped (ambiguous shared page cite).
  * UNMATCHED: a gap opinion absent from the corpus — written to a
    triage report; bulk new-row creation is still deferred.

Revert path: `cleanup revert <batch>` restores text_content/
source_reporter/source_path on opinions; then `align_primary_source
--apply` re-syncs opinion_sources.is_primary. Pre-batch DB snapshot is
the belt-and-suspenders restore. Snapshot before --apply.

Usage:
  python -m ndcourts_mcp.ingest_nwcite                 # dry-run report
  python -m ndcourts_mcp.ingest_nwcite --apply
"""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import date
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from .multisource_diff import jaccard, normalize_words, shingles
from .scrape_archive import _normalize_author, _parse_date
from .scrape_nwcite import COURT_ARCHIVE_DIR
from .validation_status import _era_tier

BATCH = f"court-archive-promote-{date.today().isoformat()}"
AUTHORITY = "court-archive (archive.ndcourts.gov NW-cite)"
SIM_HIGH = 0.85

# Approved text-promotion policy (Tufte, 2026-05-15). Gate is the
# length ratio = len(court_body) / len(db_body, frontmatter stripped),
# NOT jaccard (jaccard conflates benign OCR with real problems). The
# court source is court-authoritative and was never shorter than the CL
# OCR in a 1965-1998 sample; the genuine failure mode (a truncated/
# garbled court scrape, or a multi-opinion page) shows up as an extreme
# ratio and is routed to humans, never auto-applied.
CL_ORIGIN = {"NW2d", "NW"}        # promote only when these are primary
RATIO_AUTO_LO = 0.95              # >= this (and <= cap) -> auto-promote
RATIO_AUTO_CAP = 1.60             # sanity cap (sampled max was 1.23)
RATIO_REVIEW_LO = 0.80            # [0.80, 0.95) -> manual review band
RATIO_REVIEW_HI = 2.50            # (1.60, 2.50] -> manual review band
                                  # <0.80 or >2.50 -> never-auto manual

REFS_ROOT = Path.home() / "refs" / "nd" / "opin"
TRIAGE = Path("triage") / f"court-archive-gap-candidates-{date.today().isoformat()}.md"


def _match_opinion(conn, nw_cite: str, neutral: str | None) -> list[int]:
    cites = [nw_cite] + ([neutral] if neutral else [])
    ph = ",".join("?" * len(cites))
    rows = conn.execute(
        f"SELECT DISTINCT opinion_id FROM citations WHERE citation IN ({ph})",
        cites,
    ).fetchall()
    return [r[0] for r in rows]


def _court_html_to_text(raw: str) -> str:
    """Extract opinion text from a court NW-cite page.

    These pages differ from the 1997+ year-index pages
    scrape_archive._html_to_text was built for: the markup is
    UNTERMINATED (no closing </body> or </html>), so that function's
    `<body>(.*)</body>` regex returns '' and silently drops ~1,229
    opinions. Here we take from <body> to end-of-string when the close
    tag is absent, drop the nav chrome (header script/noscript, the
    'Go to Documents' table, the <span class="annot"> cite echo), and
    flatten the rest to text."""
    m = re.search(r"<body[^>]*>(.*?)(?:</body>|\Z)", raw,
                   re.DOTALL | re.IGNORECASE)
    if not m:
        return ""
    b = m.group(1)
    b = re.sub(r"<script[^>]*>.*?</script>", " ", b,
               flags=re.DOTALL | re.IGNORECASE)
    b = re.sub(r"<noscript[^>]*>.*?</noscript>", " ", b,
               flags=re.DOTALL | re.IGNORECASE)
    b = re.sub(r"<style[^>]*>.*?</style>", " ", b,
               flags=re.DOTALL | re.IGNORECASE)
    # Drop the citation-echo span and the nav table (first table only).
    b = re.sub(r'<span class="annot">.*?</span>', " ", b,
               flags=re.DOTALL | re.IGNORECASE)
    b = re.sub(r"<table.*?</table>", " ", b, count=1,
               flags=re.DOTALL | re.IGNORECASE)
    b = re.sub(r"\[&#182;<a name=\"P\d+\"></a>(\d+)\]", r"[¶\1]", b)
    b = re.sub(r"<br\s*/?>", "\n", b, flags=re.IGNORECASE)
    b = re.sub(r"</?(p|blockquote|div|h\d)[^>]*>", "\n\n", b,
               flags=re.IGNORECASE)
    b = re.sub(r"<[^>]+>", "", b)
    b = html.unescape(b)
    b = re.sub(r"[ \t]+", " ", b)
    b = re.sub(r"\n{3,}", "\n\n", b)
    return b.strip()


def _split_frontmatter(text: str) -> tuple[str, str]:
    """(frontmatter_block, body). CL NW2d/NW text_content is a `---`
    delimited YAML block (title/citations/judges/docket/cluster_id) then
    the opinion body. Promotion swaps ONLY the body so no structured
    metadata field is ever lost. Returns ('', text) if no frontmatter."""
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    fm = text[: end + 5]               # through the closing '---\n'
    body = text[end + 5:].lstrip("\n")
    return fm, body


def _set_status(conn, oid: int, state: str, note: str) -> None:
    conn.execute(
        "UPDATE validation_status SET crosscheck_state=?, "
        "authority_source=?, batch=?, "
        "validated_at=strftime('%Y-%m-%dT%H:%M:%S','now'), "
        "note=? WHERE opinion_id=?",
        (state, AUTHORITY, BATCH, note, oid),
    )


def _flag(conn, oid: int, note: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO review_flags (opinion_id, note) "
        "VALUES (?, ?)", (oid, f"[{BATCH}] {note}"),
    )


def run(conn, apply: bool) -> dict:
    stats = {
        "manifests": 0, "entries": 0, "skipped_status": 0,
        "matched_one": 0, "matched_many": 0, "unmatched": 0,
        "source_attached": 0, "source_existed": 0,
        "promoted": 0, "review_band": 0, "manual_outlier": 0,
        "noncl_cross_checked": 0, "noncl_flagged": 0,
        "shared_cite_ambiguous": 0,
    }
    gap_candidates: list[dict] = []

    manifests = sorted(COURT_ARCHIVE_DIR.glob("*/_manifest.json"))
    stats["manifests"] = len(manifests)

    # Pre-pass: an opinion reachable from >1 court-archive entry means two
    # distinct archive pages share one N.W. cite (lead + per-curiam/
    # companion published at the same reporter page — the Type-Y /
    # shared-page family). Promoting is ambiguous (which page is THIS
    # row's authoritative full text?), and processing the oid twice would
    # double-overwrite. Flag the whole set, never auto-promote.
    claims: dict[int, int] = {}
    for mf in manifests:
        for e in json.loads(mf.read_text(encoding="utf-8"))["entries"]:
            if e.get("status") not in ("fetched", "cached"):
                continue
            os_ = _match_opinion(conn, e["nw_cite"], e.get("neutral_cite"))
            if len(os_) == 1:
                claims[os_[0]] = claims.get(os_[0], 0) + 1
    ambiguous_oids = {o for o, n in claims.items() if n > 1}
    seen_oids: set[int] = set()

    for mf in manifests:
        man = json.loads(mf.read_text(encoding="utf-8"))
        for e in man["entries"]:
            stats["entries"] += 1
            if e.get("status") not in ("fetched", "cached"):
                stats["skipped_status"] += 1
                continue

            oids = _match_opinion(conn, e["nw_cite"], e.get("neutral_cite"))
            if len(oids) == 0:
                stats["unmatched"] += 1
                gap_candidates.append(e)
                continue
            if len(oids) > 1:
                stats["matched_many"] += 1
                continue
            stats["matched_one"] += 1
            oid = oids[0]

            if oid in ambiguous_oids:
                # Count once per oid; flag, attach no primary, no overwrite.
                if oid not in seen_oids:
                    seen_oids.add(oid)
                    stats["shared_cite_ambiguous"] += 1
                    note = (f"{claims[oid]} court-archive pages share "
                            f"{e['nw_cite']} — Type-Y/shared-page; manual "
                            f"disambiguation before any text promotion")
                    if apply:
                        _set_status(conn, oid, "flagged", note)
                        _flag(conn, oid, note)
                continue

            src_path = e.get("source_path")
            html_file = REFS_ROOT / src_path if src_path else None
            if not html_file or not html_file.exists():
                continue
            ca_text = _court_html_to_text(
                html_file.read_text(encoding="utf-8", errors="replace")
            )

            existing = conn.execute(
                "SELECT id FROM opinion_sources WHERE opinion_id=? "
                "AND source_reporter='court-archive'",
                (oid,),
            ).fetchone()
            if existing:
                stats["source_existed"] += 1
            else:
                stats["source_attached"] += 1
                if apply:
                    conn.execute(
                        "INSERT INTO opinion_sources "
                        "(opinion_id, source_reporter, source_path, "
                        " text_length, is_primary, added_at) "
                        "VALUES (?, 'court-archive', ?, ?, 0, "
                        " strftime('%Y-%m-%dT%H:%M:%S','now'))",
                        (oid, src_path, len(ca_text)),
                    )
                    log_change(
                        conn, BATCH, oid, "opinion_sources.court-archive",
                        None, src_path, authority=AUTHORITY,
                    )

            orow = conn.execute(
                "SELECT source_reporter, source_path, text_content "
                "FROM opinions WHERE id=?", (oid,)
            ).fetchone()
            cur_reporter, cur_path, cur_text = (
                orow["source_reporter"], orow["source_path"],
                orow["text_content"],
            )
            fm, db_body = _split_frontmatter(cur_text)
            sim = jaccard(
                shingles(normalize_words(db_body)),
                shingles(normalize_words(ca_text)),
            )

            # Non-CL primary (ndcourts.gov/westlaw, 1997+): the existing
            # primary is already authoritative — attach court-archive as a
            # cross-check only, never demote it to a court-archive body.
            if cur_reporter not in CL_ORIGIN:
                if sim >= SIM_HIGH:
                    state = "cross_checked"
                    note = f"jaccard={sim:.3f}; non-CL primary, cross-check only"
                    stats["noncl_cross_checked"] += 1
                else:
                    state = "flagged"
                    note = (f"jaccard={sim:.3f}; non-CL primary "
                            f"({cur_reporter}) diverges from court-archive")
                    stats["noncl_flagged"] += 1
                if apply:
                    _set_status(conn, oid, state, note)
                    if state == "flagged":
                        _flag(conn, oid, note)
                continue

            # CL primary -> promotion path. Gate on length ratio.
            ratio = len(ca_text) / max(1, len(db_body))
            if RATIO_AUTO_LO <= ratio <= RATIO_AUTO_CAP:
                tier = "promote"
            elif (RATIO_REVIEW_LO <= ratio < RATIO_AUTO_LO
                  or RATIO_AUTO_CAP < ratio <= RATIO_REVIEW_HI):
                tier = "review"
            else:
                tier = "manual"

            if tier == "promote":
                stats["promoted"] += 1
                note = (f"promoted text_content to court-archive "
                        f"(ratio={ratio:.2f}, jaccard={sim:.3f})")
                if apply:
                    new_text = (fm.rstrip() + "\n\n" + ca_text) if fm else ca_text
                    log_change(conn, BATCH, oid, "text_content",
                               cur_text, f"court-archive:{src_path}",
                               authority=AUTHORITY)
                    log_change(conn, BATCH, oid, "source_reporter",
                               cur_reporter, "court-archive",
                               authority=AUTHORITY)
                    log_change(conn, BATCH, oid, "source_path",
                               cur_path, src_path, authority=AUTHORITY)
                    conn.execute(
                        "UPDATE opinions SET text_content=?, "
                        "source_reporter='court-archive', source_path=? "
                        "WHERE id=?", (new_text, src_path, oid),
                    )
                    conn.execute(
                        "UPDATE opinion_sources SET is_primary=0 "
                        "WHERE opinion_id=?", (oid,),
                    )
                    conn.execute(
                        "UPDATE opinion_sources SET is_primary=1 "
                        "WHERE opinion_id=? AND source_reporter='court-archive' "
                        "AND source_path=?",
                        (oid, src_path),
                    )
                    _set_status(conn, oid, "corrected", note)
            elif tier == "review":
                stats["review_band"] += 1
                note = (f"court-archive promotion candidate, REVIEW BAND "
                        f"(ratio={ratio:.2f}, jaccard={sim:.3f})")
                if apply:
                    _set_status(conn, oid, "flagged", note)
                    _flag(conn, oid, note)
            else:
                stats["manual_outlier"] += 1
                note = (f"court-archive ratio={ratio:.2f} OUTSIDE bounds "
                        f"(jaccard={sim:.3f}) — possible truncation / "
                        f"multi-opinion page / wrong content; manual only")
                if apply:
                    _set_status(conn, oid, "flagged", note)
                    _flag(conn, oid, note)

    if apply:
        conn.commit()

    TRIAGE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Court-archive gap candidates ({date.today().isoformat()})",
        "",
        f"Opinions present in the court-sourced NW-cite archive but NOT "
        f"matched to any DB row by parallel/neutral cite. These are the "
        f"§2 gap prizes — candidates for new opinion rows. NOT auto-created "
        f"(deferred to post-review grind per the agreed plan).",
        "",
        f"**{len(gap_candidates)} unmatched.**",
        "",
        "| nw_cite | neutral | year | case_name | archive_oid |",
        "|---------|---------|-----:|-----------|-------------|",
    ]
    for g in gap_candidates[:1000]:
        lines.append(
            f"| {g['nw_cite']} | {g.get('neutral_cite') or '—'} | "
            f"{g.get('year') or '—'} | {g['case_name']} | {g['archive_oid']} |"
        )
    if len(gap_candidates) > 1000:
        lines.append(f"\n_… and {len(gap_candidates) - 1000} more_")
    TRIAGE.write_text("\n".join(lines), encoding="utf-8")

    if apply:
        log_provenance(
            conn,
            operation="ingest_nwcite",
            command="python -m ndcourts_mcp.ingest_nwcite --apply",
            source_paths=str(COURT_ARCHIVE_DIR),
            rows_affected=stats["promoted"] + stats["source_attached"],
            notes=(f"batch {BATCH}; tiered text-promotion (approved policy "
                   f"2026-05-15): promoted={stats['promoted']} "
                   f"review_band={stats['review_band']} "
                   f"manual_outlier={stats['manual_outlier']} "
                   f"noncl_xcheck={stats['noncl_cross_checked']} "
                   f"noncl_flagged={stats['noncl_flagged']} "
                   f"src_attached={stats['source_attached']} "
                   f"unmatched(gap)={stats['unmatched']}; revert via "
                   f"`cleanup revert {BATCH}` then `align_primary_source "
                   f"--apply`; new-row creation for gap candidates deferred"),
        )
        conn.commit()

    return stats


RESCUE_BATCH = f"court-archive-containment-rescue-{date.today().isoformat()}"
PRIOR_PROMOTE_BATCH = "court-archive-promote-2026-05-15"
CONTAIN_MIN = 0.85
# Court text ending in a signoff/disposition — used to identify the
# genuinely court-truncated cases (court NOT contained AND ends abruptly).
_ENDS_CLEAN = re.compile(
    r"(concur|dissent|J\.|JJ\.|C\.\s?J\.|Surrogate Judge|"
    r"affirmed\.|reversed\.|remanded\.)\s*\W*$", re.I)


def rescue_flagged(conn, apply: bool) -> dict:
    """Containment-rule rescue of the prior batch's manual_outlier flags
    (approved 2026-05-15). Promote a flagged low-ratio CL-primary opinion
    when the court text's shingle-containment in the DB body >= 0.85 AND
    the DB shows the caption-duplication signature (first-8-words recur
    >= 2x, unique-extra fraction < 0.55): containment guarantees the
    court text is neither truncated nor a distinct second opinion, so
    the DB 'extra' is duplicated content and swapping loses nothing
    unique. Genuinely court-truncated cases keep their flag with a
    sharpened note."""
    srcmap: dict[str, list[str]] = {}
    for mf in COURT_ARCHIVE_DIR.glob("*/_manifest.json"):
        for e in json.loads(mf.read_text(encoding="utf-8"))["entries"]:
            if e.get("status") in ("fetched", "cached"):
                srcmap.setdefault(e["nw_cite"], []).append(e["source_path"])

    oids = [r[0] for r in conn.execute(
        "SELECT opinion_id FROM validation_status WHERE batch=? "
        "AND crosscheck_state='flagged' AND note LIKE '%OUTSIDE bounds%'",
        (PRIOR_PROMOTE_BATCH,),
    )]
    st = {"candidates": len(oids), "promoted": 0, "truncated": 0, "left": 0}

    for oid in oids:
        o = conn.execute(
            "SELECT source_reporter, source_path, text_content "
            "FROM opinions WHERE id=?", (oid,)
        ).fetchone()
        if o["source_reporter"] not in CL_ORIGIN:
            st["left"] += 1
            continue
        fm, body = _split_frontmatter(o["text_content"])
        nw = [r[0] for r in conn.execute(
            "SELECT citation FROM citations WHERE opinion_id=? "
            "AND citation LIKE '% N.W.%'", (oid,))]
        if not nw or nw[0] not in srcmap:
            st["left"] += 1
            continue
        src_path = srcmap[nw[0]][0]
        ca = _court_html_to_text(
            (REFS_ROOT / src_path).read_text(encoding="utf-8",
                                             errors="replace"))
        cs = shingles(normalize_words(ca))
        ds = shingles(normalize_words(body))
        contain = len(cs & ds) / max(1, len(cs))
        nb = normalize_words(body)
        head = " ".join(nb[:8])
        reps = sum(1 for i in range(len(nb) - 7)
                   if " ".join(nb[i:i + 8]) == head)
        extra = len(ds - cs) / max(1, len(ds))

        if contain >= CONTAIN_MIN and reps >= 2 and extra < 0.55:
            st["promoted"] += 1
            note = (f"promoted via containment rule "
                    f"(contain={contain:.2f}, db caption x{reps}, "
                    f"unique-extra={extra:.2f}); CL self-duplication")
            if apply:
                new_text = (fm.rstrip() + "\n\n" + ca) if fm else ca
                log_change(conn, RESCUE_BATCH, oid, "text_content",
                           o["text_content"], f"court-archive:{src_path}",
                           authority=AUTHORITY)
                log_change(conn, RESCUE_BATCH, oid, "source_reporter",
                           o["source_reporter"], "court-archive",
                           authority=AUTHORITY)
                log_change(conn, RESCUE_BATCH, oid, "source_path",
                           o["source_path"], src_path, authority=AUTHORITY)
                conn.execute(
                    "UPDATE opinions SET text_content=?, "
                    "source_reporter='court-archive', source_path=? "
                    "WHERE id=?", (new_text, src_path, oid))
                conn.execute("UPDATE opinion_sources SET is_primary=0 "
                             "WHERE opinion_id=?", (oid,))
                conn.execute(
                    "UPDATE opinion_sources SET is_primary=1 WHERE "
                    "opinion_id=? AND source_reporter='court-archive' "
                    "AND source_path=?", (oid, src_path))
                _set_status(conn, oid, "corrected", note)
        elif contain < CONTAIN_MIN and not _ENDS_CLEAN.search(ca[-120:]):
            st["truncated"] += 1
            if apply:
                _set_status(conn, oid, "flagged",
                            f"court-source-truncated (contain={contain:.2f}, "
                            f"court ends abruptly); DB is the full opinion — "
                            f"do not promote; court-archive re-scrape item")
        else:
            st["left"] += 1

    if apply:
        log_provenance(
            conn, operation="ingest_nwcite-containment-rescue",
            command="python -m ndcourts_mcp.ingest_nwcite --rescue-flagged "
                    "--apply",
            rows_affected=st["promoted"],
            notes=(f"batch {RESCUE_BATCH}; containment-rule promotion of "
                   f"prior-batch manual_outlier flags: "
                   f"promoted={st['promoted']} truncated={st['truncated']} "
                   f"left={st['left']} of {st['candidates']}; revert via "
                   f"`cleanup revert {RESCUE_BATCH}` then "
                   f"`align_primary_source --apply`"),
        )
        conn.commit()
    return st


GAP_BATCH = f"court-archive-gap-create-{date.today().isoformat()}"
_META_DESC = re.compile(
    r'<meta name="Description" content="([^"]*)"', re.IGNORECASE)
_TITLE = re.compile(r"<title>([^<]+)</title>", re.IGNORECASE)
_DOCKET = re.compile(
    r"\b((?:Civil|Criminal)?\s*Nos?\.\s*[\d,]+(?:[A-Z]+)?"
    r"(?:\s+and\s+[\d,]+)?)", re.IGNORECASE)


def _gap_unique_candidates(conn) -> list[dict]:
    """Unmatched court-archive entries whose N.W. cite is unique among
    the unmatched set (shared-cite entries are disposition/table pages,
    not opinions — they go to the manual queue, not creation)."""
    import collections
    cands = []
    for mf in COURT_ARCHIVE_DIR.glob("*/_manifest.json"):
        for e in json.loads(mf.read_text(encoding="utf-8"))["entries"]:
            if e.get("status") not in ("fetched", "cached"):
                continue
            cites = [e["nw_cite"]] + (
                [e["neutral_cite"]] if e.get("neutral_cite") else [])
            ph = ",".join("?" * len(cites))
            if conn.execute(
                f"SELECT 1 FROM citations WHERE citation IN ({ph}) LIMIT 1",
                cites,
            ).fetchone():
                continue
            cands.append(e)
    by = collections.Counter(e["nw_cite"] for e in cands)
    return [e for e in cands if by[e["nw_cite"]] == 1]


def create_gap_opinions(conn, apply: bool) -> dict:
    """Create the unique-cite genuine-missing opinions as new rows
    (scope approved 2026-05-15: Supreme substantive + Supreme short +
    Court of Appeals as a distinct court). Shared-cite table pages are
    NOT created here — see queue_shared_cite_pages."""
    st = {"candidates": 0, "supreme": 0, "court_of_appeals": 0,
          "skipped_no_text": 0, "skipped_no_date": 0}
    for e in _gap_unique_candidates(conn):
        st["candidates"] += 1
        raw = (REFS_ROOT / e["source_path"]).read_text(
            encoding="utf-8", errors="replace")
        body = _court_html_to_text(raw)
        if not body:
            st["skipped_no_text"] += 1
            continue
        dm = _META_DESC.search(raw)
        desc = dm.group(1) if dm else ""
        date_m = re.search(
            r"Filed\s+([A-Za-z]+\.?\s+\d{1,2},?\s+\d{4})", desc)
        date_filed = _parse_date(date_m.group(1)) if date_m else None
        if not date_filed:
            st["skipped_no_date"] += 1
            continue
        is_coa = "COURT OF APPEALS" in body[:120].upper()
        court = ("North Dakota Court of Appeals" if is_coa
                 else "North Dakota Supreme Court")
        tm = _TITLE.search(raw)
        case_name_full = (tm.group(1).split(",")[0].strip()
                          if tm else e["case_name"])
        author_m = re.search(r"Author:\s*([^.]+?)\.", desc)
        author_raw = author_m.group(1).strip() if author_m else None
        per_curiam = 1 if (author_raw
                           and "per curiam" in author_raw.lower()) else 0
        author = (None if per_curiam else
                  (_normalize_author(author_raw) if author_raw else None))
        dk = _DOCKET.search(body[:400])
        docket = dk.group(1).strip() if dk else None
        cites = [e["nw_cite"]] + (
            [e["neutral_cite"]] if e.get("neutral_cite") else [])

        fm = (f'---\ntitle: "{e["case_name"]}"\n'
              f'case_name_full: "{case_name_full}"\n'
              f'court: "{court}"\ndate_filed: {date_filed}\n'
              f'citations:\n' + "".join(f' - "{c}"\n' for c in cites)
              + (f'docket_number: "{docket}"\n' if docket else "")
              + "---\n\n")
        text_content = fm + body
        st["court_of_appeals" if is_coa else "supreme"] += 1
        if not apply:
            continue

        cur = conn.execute(
            "INSERT INTO opinions (case_name, case_name_full, date_filed, "
            "court, per_curiam, author, source_reporter, source_path, "
            "text_content) VALUES (?, ?, ?, ?, ?, ?, 'court-archive', ?, ?)",
            (e["case_name"], case_name_full, date_filed, court,
             per_curiam, author, e["source_path"], text_content),
        )
        oid = cur.lastrowid
        log_change(conn, GAP_BATCH, oid, "opinions.insert", None,
                   f'{court} | {e["nw_cite"]} | {date_filed} | '
                   f'court-archive {e["source_path"]}', authority=AUTHORITY)
        for i, c in enumerate(cites):
            conn.execute(
                "INSERT INTO citations (opinion_id, citation, is_primary) "
                "VALUES (?, ?, ?)", (oid, c, 1 if i == 0 else 0))
            log_change(conn, GAP_BATCH, oid, "citation", None, c,
                       authority=AUTHORITY)
        conn.execute(
            "INSERT INTO opinion_sources (opinion_id, source_reporter, "
            "source_path, text_length, is_primary, added_at) VALUES "
            "(?, 'court-archive', ?, ?, 1, "
            "strftime('%Y-%m-%dT%H:%M:%S','now'))",
            (oid, e["source_path"], len(text_content)))
        conn.execute(
            "INSERT INTO validation_status (opinion_id, era_tier, "
            "crosscheck_state, authority_source, sources_seen, batch, "
            "validated_at, note) VALUES (?, ?, 'single_source_accepted', "
            "?, '[\"court-archive\"]', ?, "
            "strftime('%Y-%m-%dT%H:%M:%S','now'), ?)",
            (oid, _era_tier(date_filed), AUTHORITY, GAP_BATCH,
             "created from court-sourced NW-cite archive; "
             "single court-authoritative source"))

    if apply:
        log_provenance(
            conn, operation="ingest_nwcite-gap-create",
            command="python -m ndcourts_mcp.ingest_nwcite --create-gap "
                    "--apply",
            source_paths=str(COURT_ARCHIVE_DIR),
            rows_affected=st["supreme"] + st["court_of_appeals"],
            notes=(f"batch {GAP_BATCH}; created {st['supreme']} Supreme + "
                   f"{st['court_of_appeals']} Court of Appeals opinions "
                   f"from unique-cite court-archive pages; revert via "
                   f"`cleanup revert {GAP_BATCH}` (rows then need manual "
                   f"DELETE — creations aren't auto-undone by revert)"),
        )
        conn.commit()
    return st


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true",
                    help="Attach sources + write validation_status "
                         "(default: dry-run report only)")
    ap.add_argument("--rescue-flagged", action="store_true",
                    help="Run the containment-rule rescue over the prior "
                         "batch's manual_outlier flags instead of the "
                         "manifest walk")
    ap.add_argument("--create-gap", action="store_true",
                    help="Create the unique-cite genuine-missing opinions "
                         "(Supreme + Court of Appeals) as new rows")
    args = ap.parse_args()

    conn = get_connection(args.db)
    try:
        if args.rescue_flagged:
            st = rescue_flagged(conn, apply=args.apply)
            mode = "APPLIED" if args.apply else "DRY RUN"
            print(f"=== containment rescue: {mode} "
                  f"(batch {RESCUE_BATCH}) ===")
            for k, v in st.items():
                print(f"  {k:<12} {v}")
            return
        if args.create_gap:
            st = create_gap_opinions(conn, apply=args.apply)
            mode = "APPLIED" if args.apply else "DRY RUN"
            print(f"=== gap-opinion creation: {mode} "
                  f"(batch {GAP_BATCH}) ===")
            for k, v in st.items():
                print(f"  {k:<18} {v}")
            return
        stats = run(conn, apply=args.apply)
    finally:
        conn.close()

    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"=== ingest_nwcite: {mode} (batch {BATCH}) ===")
    for k, v in stats.items():
        print(f"  {k:<18} {v}")
    print(f"  gap report -> {TRIAGE}")


if __name__ == "__main__":
    main()
