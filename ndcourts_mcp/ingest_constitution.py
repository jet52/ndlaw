"""Ingest the ND Constitution from ndconst.org into a versioned corpus DB.

ndconst.org is a DokuWiki (CC0) whose pages carry the *current* text of each
constitutional provision plus amendment annotations of the form::

    [{{laws:1985-sl-ima.pdf|Amended Nov. 6, 1984}} (S.L. 1985, ch. 702)]

We therefore capture, for each section: the current text (as one
``provision_version`` effective from the most recent amendment, or original
adoption) and the full amendment *chronology* (one ``amendments`` row per
annotation, with date + enacting authority + source PDF). Full prior-version
*text* is not on the section pages; ``get_authority_history`` reports the
amendment events even where the older text has not yet been captured.

Usage:
    python -m ndcourts_mcp.ingest_constitution            # dry run (parse, report)
    python -m ndcourts_mcp.ingest_constitution --apply    # build constitution.db
    python -m ndcourts_mcp.ingest_constitution --apply --limit 2   # first 2 articles
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from . import corpus

BASE = "https://ndconst.org"
MEDIA_BASE = f"{BASE}/_media"
USER_AGENT = "ndcourts-mcp constitution ingest (personal CC0 corpus build)"
ORIGINAL_ADOPTION = "1889-10-01"  # ND Constitution ratified Oct. 1, 1889

_ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}


def roman_to_int(s: str) -> int | None:
    s = s.lower().strip()
    if not s or any(ch not in _ROMAN for ch in s):
        return None
    total, prev = 0, 0
    for ch in reversed(s):
        val = _ROMAN[ch]
        total += -val if val < prev else val
        prev = max(prev, val)
    return total


def fetch_raw(page_path: str, *, delay: float = 0.4) -> str | None:
    """Fetch a DokuWiki page's raw source. ``page_path`` is a slash path
    (e.g. 'arti/sec8/start'). Returns None on 404/empty."""
    url = f"{BASE}/{page_path}?do=export_raw"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", "replace")
    except Exception:
        return None
    finally:
        time.sleep(delay)
    body = body.strip()
    return body or None


def resolve_section_raw(link_id: str, *, delay: float = 0.4) -> tuple[str, str] | None:
    """Given a DokuWiki link id ('arti:sec8:', 'artiv:sec1', 'artiv:sec13:start'),
    fetch the section's raw source. Returns (page_path, raw) or None.

    DokuWiki ids vary: a trailing colon means a namespace (→ :start), a bare id
    may be a page or a namespace, and some already end in 'start'. Try the
    plausible forms in order."""
    base = link_id.strip().rstrip(":").replace(":", "/")
    candidates = []
    if base.endswith("/start"):
        candidates = [base]
    else:
        candidates = [f"{base}/start", base]
    for path in candidates:
        raw = fetch_raw(path, delay=delay)
        if raw:
            return path, raw
    return None


# --- parsing ---------------------------------------------------------------

# Lenient: any DokuWiki link [[id|text]] (text non-greedy up to ']]'). Section
# number + heading are parsed from the link text afterward, because the source
# format varies ("Section 8. [Heading]", "1. HEADING", and occasionally an
# unclosed heading bracket).
_LINK_RE = re.compile(r"\[\[([^|\]]+)\|(.*?)\]\]", re.S)
# Leading "Section 8." / "8." / "8.1." section number in the link text.
_LINK_SECNUM_RE = re.compile(r"^\s*(?:Section\s+)?([0-9]+(?:\.[0-9]+)?[A-Za-z]?)\.", re.I)

# [{{laws:FILE|Amended Nov. 6, 1984}} (S.L. 1985, ch. 702)]
_AMEND_LAWS_RE = re.compile(
    r"\[\{\{laws:([^|}\s]+)(?:\?[^|}]*)?\s*\|\s*([^}]+?)\s*\}\}\s*(?:\(([^)]*)\))?\s*\]"
)
# Annotations without a media link: [Amended Nov. 8, 1960 (S.L. ...)] etc.
_AMEND_PLAIN_RE = re.compile(
    r"\[(Amended|Adopted|Added|Initiated|Repealed|Approved)\b([^\]]*)\]", re.I
)

_DATE_FORMATS = ("%b. %d, %Y", "%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b. %d %Y")
_DATE_IN_TEXT_RE = re.compile(
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})"
)
_ACTION_RE = re.compile(r"\b(Amended|Adopted|Added|Initiated|Repealed|Approved)\b", re.I)
_LEADING_SECNUM_RE = re.compile(r"^\s*Sec(?:tion|\.)?\s+[0-9A-Za-z.\-]+\.\s*", re.I)


def parse_date(label: str) -> tuple[str | None, str | None]:
    """Extract (iso_date, raw_date_string) from an amendment label."""
    m = _DATE_IN_TEXT_RE.search(label)
    if not m:
        return None, None
    raw = m.group(1).strip()
    norm = raw.replace(",", "")
    for fmt in (f.replace(",", "") for f in _DATE_FORMATS):
        try:
            return datetime.strptime(norm, fmt).strftime("%Y-%m-%d"), raw
        except ValueError:
            continue
    return None, raw


def parse_amendments(raw: str) -> tuple[str, list[dict]]:
    """Return (clean_text, amendments). Strips amendment annotations from the
    body and returns each as a dict with action/date/authority/source/raw."""
    events: list[dict] = []
    spans: list[tuple[int, int]] = []

    for m in _AMEND_LAWS_RE.finditer(raw):
        file_, label, authority = m.group(1), m.group(2).strip(), (m.group(3) or "").strip()
        action_m = _ACTION_RE.search(label)
        iso, rawdate = parse_date(label)
        events.append({
            "action": action_m.group(1).lower() if action_m else None,
            "effective_date": iso,
            "raw_date": rawdate,
            "authority": authority or None,
            "source_url": f"{MEDIA_BASE}/laws/{file_}",
            "raw": m.group(0).strip(),
        })
        spans.append(m.span())

    for m in _AMEND_PLAIN_RE.finditer(raw):
        # skip if this span overlaps a laws-annotation already captured
        if any(s <= m.start() < e for s, e in spans):
            continue
        action, rest = m.group(1).lower(), m.group(2)
        iso, rawdate = parse_date(rest)
        auth_m = re.search(r"\(([^)]*)\)", rest)
        events.append({
            "action": action,
            "effective_date": iso,
            "raw_date": rawdate,
            "authority": auth_m.group(1).strip() if auth_m else None,
            "source_url": None,
            "raw": m.group(0).strip(),
        })
        spans.append(m.span())

    # Build clean text by removing annotation spans.
    keep, last = [], 0
    for s, e in sorted(spans):
        keep.append(raw[last:s])
        last = e
    keep.append(raw[last:])
    text = "".join(keep)
    text = _LEADING_SECNUM_RE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, events


def article_citation(roman: str) -> str:
    return f"N.D. Const. art. {roman.upper()}"


# --- enumeration -----------------------------------------------------------

# [[arti|Article I. Declaration of Rights]]
_ARTICLE_LINK_RE = re.compile(
    r"\[\[(art[ivxlcdm]+)\|\s*Article\s+([IVXLCDM]+)\.\s*([^\]]+?)\s*\]\]", re.I
)


def enumerate_articles() -> list[dict]:
    raw = fetch_raw("start")
    if not raw:
        raise RuntimeError("could not fetch ndconst.org start page")
    arts = []
    for m in _ARTICLE_LINK_RE.finditer(raw):
        arts.append({"id": m.group(1).lower(), "roman": m.group(2).upper(),
                     "title": m.group(3).strip()})
    return arts


def enumerate_sections(article_id: str, *, delay: float) -> list[dict]:
    raw = fetch_raw(article_id, delay=delay)
    if not raw:
        return []
    secs = []
    for m in _LINK_RE.finditer(raw):
        link_id, text = m.group(1).strip(), m.group(2).strip()
        # Only links into this article's namespace (skip footer/URL links).
        if not link_id.lower().startswith(article_id.lower() + ":"):
            continue
        num_m = _LINK_SECNUM_RE.match(text)
        if not num_m:
            continue
        secnum = num_m.group(1)
        rest = text[num_m.end():].strip()
        # Heading is the bracketed phrase if present, else the trailing text.
        hm = re.search(r"\[([^\]]*)\]?", rest)
        heading = (hm.group(1) if hm else rest).strip().rstrip(".]").strip()
        secs.append({"link_id": link_id, "secnum": secnum, "heading": heading})
    return secs


# --- amendment chronology (the :amendments table) --------------------------

_ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
# Modern, current-numbering targets: "art. XI, § 29", "art. XV, §§ 1-6",
# "art. IX, §§ 12&13". (Pre-1996 rows use bare historical section numbers and
# are intentionally left unlinked.)
_TARGET_RE = re.compile(
    r"art\.\s*([IVXLCDM]+)\s*,\s*§+\s*([0-9]+(?:\.[0-9]+)?)"
    r"(?:\s*([-&])\s*([0-9]+(?:\.[0-9]+)?))?",
    re.I,
)


def _protect_links(s: str) -> str:
    """Replace '|' inside [[...]] / {{...}} so a row can be split on '|'."""
    def repl(m):
        return m.group(0).replace("|", "\x00")
    return re.sub(r"\[\[[^\]]*\]\]|\{\{[^}]*\}\}", repl, s)


def wiki_plain(s: str) -> str:
    """DokuWiki markup -> readable text. [[t|x]]->x, [[t]]->t, {{m|x}}->x."""
    s = s.replace("\x00", "|")
    s = re.sub(r"\[\[[^|\]]*\|([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^|}]*\|([^}]*)\}\}", r"\1", s)
    s = re.sub(r"\{\{([^}]*)\}\}", r"\1", s)
    return s.strip()


def first_url(cell: str) -> str | None:
    m = re.search(r"\[\[(https?://[^|\]\x00]+)", cell)
    return m.group(1) if m else None


def parse_amendment_rows(raw: str) -> list[dict]:
    """Parse the :amendments wiki table into chronology rows."""
    rows: list[dict] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue  # skip header (^...^) and prose
        protected = _protect_links(line)
        cells = [c.strip() for c in protected.split("|")]
        cells = [c for c in cells[1:] if c != ""] if cells and cells[0] == "" else cells
        # need at least election, effective, sections, subject, number
        if len(cells) < 4:
            continue
        election, effective, sections, subject = cells[0], cells[1], cells[2], cells[3]
        number = cells[4] if len(cells) > 4 else None
        eff_m = _ISO_DATE_RE.search(effective.replace("\x00", "|"))
        el_m = _ISO_DATE_RE.search(election.replace("\x00", "|"))
        rows.append({
            "election_date": el_m.group(0) if el_m else None,
            "effective_date": eff_m.group(0) if eff_m else None,
            "affected": wiki_plain(sections),
            "affected_raw": sections,
            "subject": wiki_plain(subject),
            "source_url": first_url(subject),
            "number": wiki_plain(number) if number else None,
        })
    return rows


# ndconst.org :amendments source-data errors, corrected here (we can't edit
# ndconst.org) so a clean rebuild reproduces the fix. Keyed by amendment number ->
# corrected `affected` cell. Each correction is verified against the enacted measure.
#   167: ndconst.org lists "art. XVI, §§ 1-5" for the Legacy Fund measure (2023
#        HCR 3033, bill 23-3092) — that cell was copied from amend 165 (the age-limit
#        measure that created art. XVI). HCR 3033 amends section 26 of article X
#        (verified against the enacted bill text). Without this, the Legacy Fund
#        amendment is mislinked to art. XVI §§1-5 and art. X §26 loses its 2024 event.
AMENDMENT_AFFECTED_CORRECTIONS = {
    "167": "art. X, § 26",
}

# ndconst.org links some INITIATED-measure rows to the wrong session-law file
# (CAA = Constitutional Amendments Approved = legislative referrals; IMA = Initiated
# Measures Approved = citizen initiatives). Corrected source_url keyed by amendment #.
#   164: art. XV (2022 term limits) is an INITIATED measure — ndconst.org points to
#        .../68-2023/.../caa.pdf (404); the measure is in .../ima.pdf (S.L. 2023 ch. 594).
AMENDMENT_SOURCE_URL_CORRECTIONS = {
    "164": "https://www.legis.nd.gov/assembly/68-2023/session-laws/documents/ima.pdf",
}

# Effective-date corrections. The default for an approved measure is "the thirtieth
# day after the election, unless otherwise specified in the measure" (N.D. Const.
# art. III § 8; rule established 1918 — before 1918 it was the date of the official
# canvass). A measure that states its own effective date controls. ndconst.org's
# effective-date column is correct for nearly all rows; corrected exceptions:
#   164: art. XV (term limits) Section 5 states "effective on the first day of
#        January immediately following approval" -> 2023-01-01. ndconst.org used the
#        2022-11-08 election date.
AMENDMENT_EFFECTIVE_DATE_CORRECTIONS = {
    "164": "2023-01-01",
}


def amendment_targets(affected: str) -> list[str]:
    """Current-numbering citations an amendment touches, expanding §§ ranges.
    Returns [] for pre-1996 rows that use only historical section numbers."""
    targets: list[str] = []
    for m in _TARGET_RE.finditer(affected):
        roman = m.group(1).upper()
        start, sep, end = m.group(2), m.group(3), m.group(4)
        nums = [start]
        if sep and end:
            if sep == "&":
                nums = [start, end]
            elif sep == "-" and start.isdigit() and end.isdigit():
                nums = [str(n) for n in range(int(start), int(end) + 1)]
            else:
                nums = [start, end]
        for n in nums:
            targets.append(f"N.D. Const. art. {roman}, § {n}")
    return targets


def ingest_amendments(conn, prov_index: dict, *, batch: str) -> tuple[int, int]:
    """Load the authoritative :amendments chronology. Modern rows link to
    current provisions; pre-1996 rows are stored unlinked with their original
    section reference preserved. Returns (rows, linked_rows)."""
    raw = fetch_raw("amendments")
    if not raw:
        print("  WARN: could not fetch :amendments page", file=sys.stderr)
        return 0, 0
    rows = parse_amendment_rows(raw)
    n_rows = n_linked = 0
    latest: dict[int, str] = {}  # pid -> latest linked effective_date
    for r in rows:
        n_rows += 1
        num = (r["number"] or "").strip()
        corrected = AMENDMENT_AFFECTED_CORRECTIONS.get(num)
        if corrected:
            r["affected"] = corrected
        url_fix = AMENDMENT_SOURCE_URL_CORRECTIONS.get(num)
        if url_fix:
            r["source_url"] = url_fix
        eff_fix = AMENDMENT_EFFECTIVE_DATE_CORRECTIONS.get(num)
        if eff_fix:
            r["effective_date"] = eff_fix  # provision effective_start follows via the latest-date recompute
        action = "repealed" if "repeal" in r["subject"].lower() else "amended"
        targets = amendment_targets(r["affected"])
        linked_pids = []
        for cite in targets:
            hit = prov_index.get(corpus.cite_key(cite))
            if hit:
                linked_pids.append(hit[0])
        if linked_pids:
            for pid in linked_pids:
                conn.execute(
                    "INSERT OR IGNORE INTO amendments "
                    "(provision_id, action, effective_date, raw_date, election_date, "
                    " affected, amendment_number, authority, source_url, raw) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (pid, action, r["effective_date"], r["election_date"],
                     r["election_date"], r["affected"], r["number"], None,
                     r["source_url"], r["subject"]),
                )
                if r["effective_date"]:
                    cur = latest.get(pid)
                    if not cur or r["effective_date"] > cur:
                        latest[pid] = r["effective_date"]
            n_linked += 1
        else:
            conn.execute(
                "INSERT OR IGNORE INTO amendments "
                "(provision_id, action, effective_date, raw_date, election_date, "
                " affected, amendment_number, authority, source_url, raw) "
                "VALUES (NULL,?,?,?,?,?,?,?,?,?)",
                (action, r["effective_date"], r["election_date"], r["election_date"],
                 r["affected"], r["number"], None, r["source_url"], r["subject"]),
            )
    # Recompute each linked provision's current-version effective_start from the
    # authoritative chronology (more accurate than the inline annotations).
    for pid, eff in latest.items():
        vid = prov_index_by_pid(prov_index, pid)
        if vid:
            conn.execute(
                "UPDATE provision_versions SET effective_start=? WHERE id=?", (eff, vid)
            )
    conn.commit()
    return n_rows, n_linked


def prov_index_by_pid(prov_index: dict, pid: int) -> int | None:
    for (p, v) in prov_index.values():
        if p == pid:
            return v
    return None


# --- stale-current-text corrections ----------------------------------------

TEXT_CORRECTIONS_JSON = Path(__file__).resolve().parent.parent / "data" / "const_modern_text_corrections.json"


def apply_text_corrections(conn, prov_index: dict) -> int:
    """Override the current-version text where the ndconst.org snapshot is STALE
    (recorded an amendment but never applied its text). Data + provenance live in
    data/const_modern_text_corrections.json; each correction's text is the enacted
    post-amendment text verified against the session-law measure. Remove an entry
    once ndconst.org reflects the amendment."""
    if not TEXT_CORRECTIONS_JSON.exists():
        return 0
    data = json.loads(TEXT_CORRECTIONS_JSON.read_text())
    n = 0
    for c in data.get("corrections", []):
        hit = prov_index.get(corpus.cite_key(c["citation"]))
        if not hit:
            print(f"  WARN text-correction: {c['citation']} not found", file=sys.stderr)
            continue
        pid, vid = hit
        old = conn.execute("SELECT text_content FROM provision_versions WHERE id=?", (vid,)).fetchone()[0]
        head = conn.execute("SELECT heading FROM provisions WHERE id=?", (pid,)).fetchone()
        head = (head[0] if head else None) or ""
        # provisions_fts is external-content FTS5 (manually managed): remove the old
        # row with the 'delete' command (needs the originally-indexed values).
        conn.execute("INSERT INTO provisions_fts(provisions_fts, rowid, citation, heading, text_content) "
                     "VALUES('delete', ?, ?, ?, ?)", (vid, c["citation"], head, old))
        auth = (f"current text (ndconst.org, corrected for amend {c['applies_amendment']})"
                if c.get("applies_amendment") else "current text (corrected — ndconst.org source defect)")
        conn.execute("UPDATE provision_versions SET text_content=?, source_authority=? WHERE id=?",
                     (c["text"], auth, vid))
        corpus.index_version_fts(conn, vid, c["citation"], head, c["text"])
        n += 1
    conn.commit()
    return n


# --- DB build --------------------------------------------------------------

def build(db_path: Path, *, limit: int | None, delay: float, batch: str) -> dict:
    conn = corpus.get_corpus_connection(db_path, must_exist=False)
    corpus.create_corpus_schema(conn)
    articles = enumerate_articles()
    if limit:
        articles = articles[:limit]

    n_prov = n_ver = 0
    prov_index: dict[str, tuple[int, int]] = {}  # cite_key -> (provision_id, current_version_id)
    for art in articles:
        secs = enumerate_sections(art["id"], delay=delay)
        for sec in secs:
            got = resolve_section_raw(sec["link_id"], delay=delay)
            if not got:
                print(f"  WARN: no page for {sec['link_id']}", file=sys.stderr)
                continue
            _path, raw = got
            text, events = parse_amendments(raw)  # events used only for status/cleanup
            if not text:
                print(f"  WARN: empty text for {sec['link_id']}", file=sys.stderr)
                continue
            citation = f"{article_citation(art['roman'])}, § {sec['secnum']}"
            # Provisional effective_start; overwritten below from the
            # authoritative amendment chronology for amended sections.
            repealed = bool(re.match(r"(?i)^\s*repealed\b", text)) or any(
                e["action"] == "repealed" for e in events
            )
            status = "repealed" if repealed else "active"
            key = corpus.cite_key(citation)
            pid = conn.execute(
                "INSERT INTO provisions (corpus, citation, cite_key, heading, status) "
                "VALUES (?,?,?,?,?)",
                ("const", citation, key, sec["heading"] or None, status),
            ).lastrowid
            n_prov += 1
            vid = conn.execute(
                "INSERT INTO provision_versions "
                "(provision_id, effective_start, effective_end, text_content, "
                " source_authority, source_url, batch) VALUES (?,?,?,?,?,?,?)",
                (pid, ORIGINAL_ADOPTION, None, text,
                 "current text (ndconst.org)", f"{BASE}/{_path}", batch),
            ).lastrowid
            conn.execute("UPDATE provisions SET current_version_id=? WHERE id=?", (vid, pid))
            corpus.index_version_fts(conn, vid, citation, sec["heading"], text)
            prov_index[key] = (pid, vid)
            n_ver += 1
        conn.commit()
        print(f"  art {art['roman']}: {len(secs)} sections")

    # Authoritative amendment chronology (ndconst.org :amendments — 167 rows).
    n_amend, n_linked = ingest_amendments(conn, prov_index, batch=batch)
    print(f"  amendments: {n_amend} rows ({n_linked} linked to current provisions)")

    n_textfix = apply_text_corrections(conn, prov_index)
    if n_textfix:
        print(f"  stale-current-text corrections applied: {n_textfix}")

    conn.execute(
        "INSERT INTO provenance (operation, command, source_paths, rows_affected, notes) "
        "VALUES (?,?,?,?,?)",
        ("ingest_constitution", batch, BASE, n_prov,
         f"{n_prov} provisions, {n_ver} versions, {n_amend} amendment rows "
         f"({n_linked} linked)"),
    )
    conn.commit()
    conn.close()
    return {"provisions": n_prov, "versions": n_ver,
            "amendment_rows": n_amend, "linked": n_linked}


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest ND Constitution from ndconst.org")
    ap.add_argument("--apply", action="store_true", help="write the DB (default: dry run)")
    ap.add_argument("--db", type=Path, default=None, help="output DB path")
    ap.add_argument("--limit", type=int, default=None, help="first N articles only")
    ap.add_argument("--delay", type=float, default=0.4, help="seconds between requests")
    args = ap.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    batch = f"const-ingest-{stamp}"

    if not args.apply:
        # dry run: enumerate + parse a couple sections, report, write nothing
        arts = enumerate_articles()
        print(f"Found {len(arts)} articles: {', '.join(a['roman'] for a in arts)}")
        sample = enumerate_sections(arts[0]["id"], delay=args.delay)
        print(f"Article {arts[0]['roman']} has {len(sample)} sections; sample:")
        for sec in sample[:3]:
            got = resolve_section_raw(sec["link_id"], delay=args.delay)
            if not got:
                print(f"  {sec['secnum']}: <no page>")
                continue
            text, events = parse_amendments(got[1])
            print(f"  § {sec['secnum']} [{sec['heading']}] — {len(text)} chars, "
                  f"{len(events)} amendment(s): {[e['effective_date'] for e in events]}")
        print("\nDry run only. Re-run with --apply to build the DB.")
        return

    db_path = args.db or corpus.resolve_corpus_db_path("const")
    print(f"Building Constitution corpus → {db_path}")
    stats = build(db_path, limit=args.limit, delay=args.delay, batch=batch)
    print(f"Done: {stats}")


if __name__ == "__main__":
    main()
