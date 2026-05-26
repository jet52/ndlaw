"""Receive/ingest the Westlaw Find & Print returns for the gap-era pull.

Closes the manual-Westlaw loop. The worklist (westlaw_worklist) lists
1953-~1965 opinions that have only CL OCR; the user pulls them from
Westlaw (zip of individual .doc files per ~100-cite batch) and drops
the unzipped .doc files into an incoming dir. This tool:

  * textutil -> _parse_westlaw_doc (Westlaw editorial Synopsis already
    stripped inside the parser — mandatory; do not bypass).
  * Resolve the target opinion. The gap era is riddled with shared
    reporter pages (two opinions begin on one N.W.2d page), so the
    N.W. cite ALONE is not a key:
      - candidates = DB opinions carrying any parsed citation.
      - exactly one      -> match.
      - several          -> disambiguate by party name (_case_names_
                            match) + filing date; unique winner -> match,
                            else AMBIGUOUS (reported, skipped).
      - none             -> a returned opinion absent from the corpus
                            (Type-Y companion / genuinely missing) ->
                            CREATE a new row.
  * Matched: promote the Westlaw bound text to the authoritative
    primary (Westlaw bound > CL OCR for this era), preserving any
    existing YAML frontmatter; flip opinion_sources primary; set
    validation_status terminal; stamp westlaw_requests.received_at/path.
  * Created: new opinion (court = ND Court of Appeals if the text says
    so, else ND Supreme Court), citations, court source, validation
    status, all logged.
  * Archive every .doc to ~/refs/nd/opin/N.W.2d/{vol}/{page:04d}-
    {slug}.doc — parallel to the bound N.D./{vol}/{page}-{slug}.doc.

Reversible/audited: pre-batch snapshot, changelog (authority-stamped),
provenance, CHANGELOG-data.md, invariants. Dry-run default.

Usage:
  python -m ndcourts_mcp.receive_westlaw                 # dry-run report
  python -m ndcourts_mcp.receive_westlaw --apply
  python -m ndcourts_mcp.receive_westlaw --incoming PATH --apply
"""

from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from datetime import date
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from .ingest_westlaw import (
    _case_names_match,
    _doc_to_text,
    _parse_date,
    _parse_westlaw_doc,
)
from .ingest import _classify_reporter, recompute_primary
from .ingest_nwcite import _split_frontmatter
from .multisource_diff import jaccard, normalize_words, shingles
from .strip_westlaw_headnotes import _PP, _excise_headnotes
from .strip_westlaw_synopsis import strip_synopsis_editorial
from .validation_status import _era_tier

BATCH = f"westlaw-receive-{date.today().isoformat()}"
INCOMING_DEFAULT = Path.home() / "refs" / "nd" / "opin" / "westlaw-incoming"
REFS_ROOT = Path.home() / "refs" / "nd" / "opin"
NW2D_ARCHIVE = REFS_ROOT / "N.W.2d"
# Reporter-series → archive subtree. The gap-era tool only ever saw
# N.W.2d; PDF-era pulls carry N.W.3d (and, rarely, 1st-series N.W.), so
# route by the parsed series instead of hardcoding N.W.2d.
_NW_ARCHIVE_DIR = {
    "3d": REFS_ROOT / "N.W.3d",
    "2d": REFS_ROOT / "N.W.2d",
    "": REFS_ROOT / "N.W.",
}
_NW_CITE = re.compile(r"\b(\d+)\s+N\.\s?W\.\s?(2d|3d)?\s+(\d+)\b")

# A genuine same-opinion promote, even with heavy NW2d-era OCR drift,
# shared 0.50-0.93 shingle-Jaccard in the dry-run; 0.00 means the
# Westlaw text is a different document than the resolved DB row (a
# wrong shared-page resolution). Below this floor we do NOT overwrite —
# we flag for manual review. Set well under the legit 0.50 floor and
# well over 0.00 so it isolates the wrong-resolution cases only.
JACCARD_FLOOR = 0.20

_DOCKET_TAIL = re.compile(
    r"\s*(?:Civ(?:il)?\.?|Crim(?:inal)?\.?)?\s*Nos?\.?\s*[\w-]+\.?\s*\|?\s*$",
    re.IGNORECASE)
_ROLE = re.compile(
    r",?\s*(?:Plaintiffs?|Defendants?|Petitioners?|Respondents?|"
    r"Appellants?|Appellees?|Movants?|Intervenors?|and|the)\b.*$",
    re.IGNORECASE)
_LEAD_PREFIX = re.compile(
    r"^\s*(?:In re|In the Matter of|In the Interest of|"
    r"Matter of|Application of|Estate of)\b[:.]?\s*", re.IGNORECASE)


def _caption_key(name: str) -> str:
    """Reduce a messy Westlaw caption to a 'lead1 v. lead2' key the DB
    case name can match. Westlaw gives the full multi-party block plus a
    'Civ. No. 930122. |' docket tail; DB names are short. Strip the tail,
    the role words, the In-re prefix, and take the lead party each side."""
    if not name:
        return ""
    s = name.replace("|", " ").strip()
    s = _DOCKET_TAIL.sub("", s)
    parts = re.split(r"\s+v\.?\s+", s, maxsplit=1, flags=re.IGNORECASE)
    out = []
    for side in parts:
        side = _LEAD_PREFIX.sub("", side)
        side = side.split(",")[0]          # lead party only
        side = _ROLE.sub("", side).strip(" .")
        out.append(side)
    return " v. ".join(p for p in out if p)


def _strip_editorial(body: str) -> str:
    """Strip leaked Westlaw editorial from a fallback-extracted body —
    the West Headnotes block, the Procedural Posture line, and the
    Synopsis stub — matching what _parse_westlaw_doc removes on the main
    path. Court-authored narrative under a Synopsis header is preserved
    (strip_synopsis_editorial). Reuses the corpus strip tools so the
    fallback can't reintroduce the editorial those tools later remove."""
    nb, _ = _excise_headnotes(body)
    nb = _PP.sub("", nb)
    nb = re.sub(r"\n{3,}", "\n\n", nb).strip()
    nb, _, _ = strip_synopsis_editorial(nb)
    return nb.strip()


def _parse(text: str) -> dict | None:
    """_parse_westlaw_doc, with a memorandum fallback. '(Mem)' orders
    carry the cite/caption/date and an 'All Citations' footer but no
    Opinion/Attorneys header, so the base parser extracts no body. When
    that happens, take the body as everything between the filing date
    and 'All Citations' — then strip any leaked Westlaw editorial
    (the base parser strips it; the fallback must too)."""
    p = _parse_westlaw_doc(text) or {}
    if p.get("full_bound_text") or p.get("opinion_text"):
        # The base parser strips West Headnotes but (for modern memo-format
        # docs) leaves the Synopsis stub and "Procedural Posture(s)" line in
        # the body. Strip them here so neither parse path emits editorial.
        for key in ("full_bound_text", "opinion_text"):
            if p.get(key):
                p[key] = _strip_editorial(p[key])
        return p

    lines = text.splitlines()
    cite = None
    for ln in lines:
        s = ln.strip()
        if re.match(r"\d+\s+N\.\s?W\.", s):
            cite = s
            break
    if not cite:
        return p or None
    all_idx = None
    for j in range(len(lines) - 1, -1, -1):
        if lines[j].strip() == "All Citations":
            all_idx = j
            break
    date_idx = date_val = None
    for i, ln in enumerate(lines[:40]):
        d = _parse_date(ln.strip().rstrip("."))
        if d:
            date_idx, date_val = i, d
            break
    if all_idx is None or date_idx is None:
        return p or None
    body = "\n".join(lines[date_idx + 1:all_idx]).strip()
    if not body:
        return p or None
    body = _strip_editorial(body)
    if not body:
        return p or None
    # caption = the lines between the "Supreme Court..."/cite header and
    # the docket/date block.
    cap = []
    for ln in lines[:date_idx]:
        s = ln.strip()
        if (not s or s == cite or s.startswith("Supreme Court")
                or s.startswith("Court of Appeals")
                or re.match(r"Nos?\.", s) or s == "|"):
            continue
        cap.append(s)
    merged = dict(p)
    merged.setdefault("primary_citation", cite)
    merged.setdefault("all_citations",
                       [c.strip() for c in
                        (lines[all_idx + 1].split(",") if all_idx + 1
                         < len(lines) else []) if c.strip()])
    merged["case_name"] = p.get("case_name") or " ".join(cap)
    merged["date_filed"] = p.get("date_filed") or date_val
    merged["full_bound_text"] = body
    return merged


def _authority(cite: str) -> str:
    return f"Westlaw bound (Find&Print, {cite})"


def _slug(name: str) -> str:
    s = re.sub(r"[.,;:'\"]", "", name)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return s[:90] or "Unknown"


def _archive_doc(doc_path: Path, primary_cite: str, case_name: str) -> str:
    """Copy the .doc to N.W.2d/{vol}/{page:04d}-{slug}.doc, parallel to
    the bound N.D./{vol}/{page}-{slug}.doc layout. Returns refs-relative
    path, or '' if the cite has no parseable N.W. vol/page."""
    m = _NW_CITE.search(primary_cite or "")
    if not m:
        return ""
    vol, series, page = m.group(1), (m.group(2) or ""), int(m.group(3))
    dest_dir = _NW_ARCHIVE_DIR.get(series, NW2D_ARCHIVE) / vol
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{page:04d}-{_slug(case_name)}.doc"
    shutil.copy2(doc_path, dest)
    return str(dest.relative_to(REFS_ROOT))


def _clean_cite(cite: str) -> str:
    """Strip the trailing Westlaw reporter suffix — '(Mem)', '(Table)',
    '(Unpublished Disposition)', etc. The memorandum parser carries the
    literal cite line '516 N.W.2d 278 (Mem)'; the DB stores the bare
    '516 N.W.2d 278', so an exact match silently fails and the doc
    duplicates an existing opinion. Normalize before matching, and store
    the bare form on create so the corpus isn't polluted with variants."""
    return re.sub(r"\s*\([^)]*\)\s*$", "",
                  re.sub(r"\s+", " ", cite.strip())).strip()


def _candidates(conn, citations: list[str]) -> list[dict]:
    seen, out = set(), []
    for cite in citations:
        c = _clean_cite(cite)
        if not c:
            continue
        for r in conn.execute(
            "SELECT o.* FROM opinions o JOIN citations ci "
            "ON ci.opinion_id=o.id WHERE ci.citation=?", (c,)
        ):
            if r["id"] not in seen:
                seen.add(r["id"])
                out.append(dict(r))
    return out


_TEXT_SAME = 0.45   # text-jaccard above this = same opinion despite a
                    # messy/non-matching parsed caption


def _agreement(parsed: dict, cand: dict) -> tuple[float, bool, bool]:
    """(score, name_ok, strong) for a doc against a candidate opinion.

    A genuine same-opinion match agrees on at least one strong signal —
    cleaned caption, OR filing date, OR substantial text overlap. A
    shared-page COMPANION that merely collides on the (cleaned) reporter
    cite agrees on none. score ranks competing docs for the same row."""
    wl_key = _caption_key(parsed.get("case_name", ""))
    name_ok = bool(wl_key and _case_names_match(wl_key, cand["case_name"]))
    date_ok = bool(parsed.get("date_filed")
                   and parsed["date_filed"] == cand["date_filed"])
    wl_text = parsed.get("full_bound_text") or parsed.get("opinion_text") or ""
    sim = jaccard(shingles(normalize_words(wl_text)),
                  shingles(normalize_words(cand.get("text_content", ""))))
    strong = name_ok or date_ok or sim >= _TEXT_SAME
    score = (2.0 if name_ok else 0.0) + (1.0 if date_ok else 0.0) + sim
    return score, name_ok, strong


def _resolve(conn, parsed: dict) -> tuple[str, dict | None, float]:
    """(kind, opinion, score). kind ∈ match | create | ambiguous.

    A candidate is accepted only if it AGREES on name/date/text — a lone
    cite candidate is NOT enough (shared reporter pages put a different
    opinion at the same cleaned cite; blindly matching dog-piles or
    duplicates it). Non-agreeing → create (it is a genuine distinct
    opinion sharing the page)."""
    cites = list(parsed.get("all_citations", []))
    if parsed.get("primary_citation"):
        cites.insert(0, parsed["primary_citation"])
    cands = _candidates(conn, cites)
    if not cands:
        return "create", None, 0.0
    scored = sorted(
        ((_agreement(parsed, c), c) for c in cands),
        key=lambda t: t[0][0], reverse=True)
    (best_score, _, best_strong), best = scored[0]
    if not best_strong:
        # No candidate is plausibly this doc's opinion → it is the
        # shared-page companion of opinions we already have → create.
        return "create", None, 0.0
    strong = [(s, c) for (s, _n, st), c in scored if st]
    if len(strong) == 1:
        return "match", best, best_score
    # >1 candidate plausibly matches — only safe if one clearly wins.
    if strong[0][0] - strong[1][0] >= 1.0:
        return "match", best, best_score
    return "ambiguous", None, 0.0


def _promote(conn, oid: int, parsed: dict, archive_path: str,
             apply: bool) -> str:
    cite = parsed.get("primary_citation", "")

    # Safety gate: an empty archive_path means _archive_doc could not derive
    # an N.W. destination from the primary cite (e.g. an N.D.-only cite). The
    # writes below would otherwise overwrite opinions.source_path AND the
    # westlaw opinion_sources row with '' and then flag that empty row primary
    # — the exact corruption repaired in restore-phantom-westlaw-paths-2026-05-26.
    # Refuse: leave the row untouched, flag it for manual archiving.
    if not archive_path:
        if apply:
            conn.execute(
                "INSERT OR REPLACE INTO review_flags (opinion_id, note) "
                "VALUES (?, ?)",
                (oid, f"[{BATCH}] westlaw match but _archive_doc returned no "
                 f"path (cite {cite!r} has no parseable N.W. vol/page); not "
                 f"promoted to avoid blanking source_path"))
        return "NO_ARCHIVE_PATH — not promoted (cite has no N.W. vol/page)"

    row = conn.execute(
        "SELECT source_reporter, source_path, text_content "
        "FROM opinions WHERE id=?", (oid,)
    ).fetchone()
    fm, body = _split_frontmatter(row["text_content"])
    wl_text = parsed.get("full_bound_text") or parsed.get("opinion_text") or ""
    sim = jaccard(shingles(normalize_words(body)),
                  shingles(normalize_words(wl_text)))
    auth = _authority(cite)

    # Safety gate: at jaccard < floor the Westlaw text is a different
    # document than the resolved DB row (a wrong shared-page resolution,
    # or a DB stub we can't verify against). Do NOT overwrite — flag for
    # manual review, leave the row and westlaw_requests untouched.
    if sim < JACCARD_FLOOR:
        if apply:
            conn.execute(
                "UPDATE validation_status SET crosscheck_state='flagged', "
                "authority_source=?, batch=?, "
                "validated_at=strftime('%Y-%m-%dT%H:%M:%S','now'), note=? "
                "WHERE opinion_id=?",
                (auth, BATCH,
                 f"Westlaw MATCH but jaccard={sim:.3f} < {JACCARD_FLOOR} "
                 f"vs DB text — likely wrong shared-page resolution or DB "
                 f"stub; manual disambiguation before any promote", oid))
            conn.execute(
                "INSERT OR REPLACE INTO review_flags (opinion_id, note) "
                "VALUES (?, ?)",
                (oid, f"[{BATCH}] low-similarity westlaw match "
                 f"(jaccard={sim:.3f}); doc at {archive_path}"))
        return f"LOW_SIM (jaccard={sim:.2f}) — flagged, NOT promoted"

    new_text = (fm.rstrip() + "\n\n" + wl_text) if fm else wl_text
    if apply:
        log_change(conn, BATCH, oid, "text_content", row["text_content"],
                   f"westlaw:{archive_path}", authority=auth)
        log_change(conn, BATCH, oid, "source_reporter",
                   row["source_reporter"], "westlaw", authority=auth)
        log_change(conn, BATCH, oid, "source_path", row["source_path"],
                   archive_path, authority=auth)
        conn.execute(
            "UPDATE opinions SET text_content=?, source_reporter='westlaw', "
            "source_path=? WHERE id=?", (new_text, archive_path, oid))
        existing = conn.execute(
            "SELECT id FROM opinion_sources WHERE opinion_id=? "
            "AND source_reporter='westlaw'", (oid,)).fetchone()
        if existing:
            conn.execute("UPDATE opinion_sources SET source_path=?, "
                         "text_length=? WHERE id=?",
                         (archive_path, len(wl_text), existing["id"]))
        else:
            conn.execute(
                "INSERT INTO opinion_sources (opinion_id, source_reporter, "
                "source_path, text_length, is_primary, added_at) VALUES "
                "(?, 'westlaw', ?, ?, 0, "
                "strftime('%Y-%m-%dT%H:%M:%S','now'))",
                (oid, archive_path, len(wl_text)))
        conn.execute("UPDATE opinion_sources SET is_primary=0 "
                     "WHERE opinion_id=?", (oid,))
        conn.execute("UPDATE opinion_sources SET is_primary=1 WHERE "
                     "opinion_id=? AND source_reporter='westlaw' "
                     "AND source_path=?", (oid, archive_path))
        conn.execute(
            "UPDATE validation_status SET crosscheck_state='corrected', "
            "authority_source=?, batch=?, "
            "validated_at=strftime('%Y-%m-%dT%H:%M:%S','now'), note=? "
            "WHERE opinion_id=?",
            (auth, BATCH,
             f"Westlaw bound promoted to primary (jaccard vs prior "
             f"text={sim:.3f})", oid))
        conn.execute("DELETE FROM review_flags WHERE opinion_id=?", (oid,))
        conn.execute(
            "UPDATE westlaw_requests SET received_at="
            "strftime('%Y-%m-%dT%H:%M:%S','now'), received_path=? "
            "WHERE opinion_id=?", (archive_path, oid))
    return f"promoted (jaccard={sim:.2f})"


def _create(conn, parsed: dict, archive_path: str, apply: bool) -> str:
    wl_text = parsed.get("full_bound_text") or parsed.get("opinion_text") or ""
    date_filed = parsed.get("date_filed")
    raw_name = parsed.get("case_name") or "Unknown"
    # Strip the docket/pipe tail but keep the descriptive "In the Matter
    # of …" wording (more useful than a reduced key for these orders).
    case_name = _DOCKET_TAIL.sub("", raw_name).replace("|", " ").strip() \
        or raw_name
    if not date_filed or not wl_text:
        return "skipped (no date/text)"
    is_coa = "COURT OF APPEALS" in wl_text[:160].upper()
    court = ("North Dakota Court of Appeals" if is_coa
             else "North Dakota Supreme Court")
    cites = list(parsed.get("all_citations", []))
    if parsed.get("primary_citation"):
        cites.insert(0, parsed["primary_citation"])
    # Store the bare cite (no '(Mem)'/'(Table)') so the corpus stays
    # clean and future runs can match these rows.
    cites = list(dict.fromkeys(
        cc for cc in (_clean_cite(c) for c in cites) if cc))
    auth = _authority(parsed.get("primary_citation", ""))
    if not apply:
        return f"would create ({court})"
    fm = (f'---\ntitle: "{case_name}"\ncourt: "{court}"\n'
          f'date_filed: {date_filed}\ncitations:\n'
          + "".join(f' - "{c}"\n' for c in cites) + "---\n\n")
    cur = conn.execute(
        "INSERT INTO opinions (case_name, date_filed, court, author, "
        "per_curiam, source_reporter, source_path, text_content) VALUES "
        "(?, ?, ?, ?, 0, 'westlaw', ?, ?)",
        (case_name, date_filed, court, parsed.get("author"),
         archive_path, fm + wl_text))
    oid = cur.lastrowid
    log_change(conn, BATCH, oid, "opinions.insert", None,
               f'{court} | {cites[0] if cites else "?"} | {date_filed} | '
               f'westlaw {archive_path}', authority=auth)
    for c in cites:
        conn.execute("INSERT INTO citations (opinion_id, citation, "
                     "reporter, is_primary) VALUES (?, ?, ?, 0)",
                     (oid, c, _classify_reporter(c)))
        log_change(conn, BATCH, oid, "citation", None, c, authority=auth)
    recompute_primary(conn, oid)
    conn.execute(
        "INSERT INTO opinion_sources (opinion_id, source_reporter, "
        "source_path, text_length, is_primary, added_at) VALUES "
        "(?, 'westlaw', ?, ?, 1, strftime('%Y-%m-%dT%H:%M:%S','now'))",
        (oid, archive_path, len(wl_text)))
    conn.execute(
        "INSERT INTO validation_status (opinion_id, era_tier, "
        "crosscheck_state, authority_source, sources_seen, batch, "
        "validated_at, note) VALUES (?, ?, 'single_source_accepted', ?, "
        "'[\"westlaw\"]', ?, strftime('%Y-%m-%dT%H:%M:%S','now'), ?)",
        (oid, _era_tier(date_filed), auth, BATCH,
         "created from Westlaw bound (Type-Y companion / gap missing)"))
    return f"created oid={oid} ({court})"


def _iter_docs(incoming: Path):
    for z in sorted(incoming.rglob("*.zip")):
        with zipfile.ZipFile(z) as zf:
            zf.extractall(z.with_suffix(""))
    yield from sorted(incoming.rglob("*.doc"))


def run(conn, incoming: Path, apply: bool) -> dict:
    st = {"docs": 0, "promoted": 0, "low_sim": 0, "created": 0,
          "ambiguous": 0, "skipped": 0, "parse_error": 0, "no_archive": 0}
    report: list[str] = []

    # PHASE 1 — classify every doc read-only against the ORIGINAL DB.
    # Resolution must not see rows created earlier in this same run: a
    # shared-page Type-Y pair where neither side is in the DB must yield
    # two independent CREATEs, not one CREATE then a sibling promoting
    # onto it. _resolve only reads, so doing all resolution before any
    # write makes the batch order-independent (== the dry-run truth).
    decisions = []  # [doc, parsed, kind, op, score]
    for doc in _iter_docs(incoming):
        st["docs"] += 1
        try:
            parsed = _parse(_doc_to_text(doc))
        except Exception as e:  # noqa: BLE001
            parsed = None
            report.append(f"PARSE_ERROR\t{doc.name}\t\t{e}")
        if not parsed:
            st["parse_error"] += 1
            continue
        kind, op, score = _resolve(conn, parsed)
        decisions.append([doc, parsed, kind, op, score])

    # RECONCILE — at most one doc may promote a given existing row. When
    # several docs resolve "match" to the same opinion (two short
    # formulaic shared-page orders both clearing the cite+agreement bar),
    # keep the highest-scoring as the match; the rest are distinct
    # companion opinions → demote to "create" so they get their own row
    # instead of dog-piling/overwriting one.
    best_for: dict[int, float] = {}
    for _d, _p, kind, op, score in decisions:
        if kind == "match":
            oid = op["id"]
            if score > best_for.get(oid, -1.0):
                best_for[oid] = score
    claimed: set[int] = set()
    for dec in decisions:
        _d, _p, kind, op, score = dec
        if kind != "match":
            continue
        oid = op["id"]
        if score == best_for[oid] and oid not in claimed:
            claimed.add(oid)            # this doc wins the row
        else:
            dec[2], dec[3] = "create", None   # companion → create

    # PHASE 2 — apply writes from the frozen, reconciled classification.
    for doc, parsed, kind, op, score in decisions:
        cite = parsed.get("primary_citation", "")
        name = parsed.get("case_name", "?")
        # In dry-run, mirror _archive_doc's empty return for cites with no
        # parseable N.W. vol/page so the NO_ARCHIVE_PATH gate surfaces in the
        # dry-run report instead of only at apply time.
        archive_path = _archive_doc(doc, cite, name) if apply else (
            f"N.W.2d/(dry)/{doc.name}" if _NW_CITE.search(cite or "") else "")
        if kind == "match":
            msg = _promote(conn, op["id"], parsed, archive_path, apply)
            if msg.startswith("LOW_SIM"):
                st["low_sim"] += 1
                report.append(f"LOW_SIM\t{cite}\t{name}\toid={op['id']}\t{msg}")
            elif msg.startswith("NO_ARCHIVE_PATH"):
                st["no_archive"] += 1
                report.append(
                    f"NO_ARCHIVE_PATH\t{cite}\t{name}\toid={op['id']}\t{msg}")
            else:
                st["promoted"] += 1
                report.append(
                    f"MATCH\t{cite}\t{name}\toid={op['id']}\t{msg}")
        elif kind == "create":
            r = _create(conn, parsed, archive_path, apply)
            if r.startswith("skipped"):
                st["skipped"] += 1
            else:
                st["created"] += 1
            report.append(f"CREATE\t{cite}\t{name}\t{r}")
        else:
            st["ambiguous"] += 1
            report.append(f"AMBIGUOUS\t{cite}\t{name}\t"
                          f"(cite non-unique; name+date did not resolve)")

    rpt = Path("triage") / f"{BATCH}.tsv"
    rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("kind\tcite\tcase\tdetail\n" + "\n".join(report),
                   encoding="utf-8")
    if apply:
        log_provenance(
            conn, operation="receive_westlaw",
            command="python -m ndcourts_mcp.receive_westlaw --apply",
            source_paths=str(incoming),
            rows_affected=st["promoted"] + st["created"],
            notes=(f"batch {BATCH}; promoted={st['promoted']} "
                   f"created={st['created']} ambiguous={st['ambiguous']} "
                   f"parse_error={st['parse_error']} of {st['docs']} docs; "
                   f"revert via `cleanup revert {BATCH}` then "
                   f"`align_primary_source --apply` (creations need manual "
                   f"DELETE)"),
        )
        conn.commit()
    return st, rpt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--incoming", type=Path, default=INCOMING_DEFAULT)
    ap.add_argument("--apply", action="store_true",
                    help="Write changes (default: dry-run report only)")
    args = ap.parse_args()

    if not args.incoming.exists():
        raise SystemExit(f"incoming dir not found: {args.incoming}\n"
                         f"Create it and drop the unzipped Westlaw .doc "
                         f"files (or the .zip) there.")
    conn = get_connection(args.db)
    try:
        st, rpt = run(conn, args.incoming, apply=args.apply)
    finally:
        conn.close()
    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"=== receive_westlaw: {mode} (batch {BATCH}) ===")
    for k, v in st.items():
        print(f"  {k:<14} {v}")
    print(f"  report -> {rpt}")


if __name__ == "__main__":
    main()
