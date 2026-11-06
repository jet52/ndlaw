"""Court-rule explanatory notes: the court's own changelog, stored verbatim.

Every rule page on ndcourts.gov carries one cumulative "Explanatory Notes"
block: an opening line listing every amendment date, a paragraph per change
("Subdivision (b) was amended, effective March 1, 2011, to ..."), a SOURCES
paragraph (committee minutes by meeting date and page), a STATUTES AFFECTED
block (SUPERSEDED / CONSIDERED), and a CROSS REFERENCE paragraph. The
rules-scraper stores it beside the rule as ``<category>/notes/rule-<n>.md``
(the sidecar, committed at observation time; its git history is the note's
history). This module reads the sidecars into ``rules.db``:

* ``rule_notes`` — the note verbatim, one row per provision (the record);
* ``rule_note_paragraphs`` — the same text classified: kind, affected unit,
  the effective dates each paragraph names;
* ``rule_note_sources`` — the SOURCES paragraph as rows (committee, meeting
  date, pages) — pointers, never summaries;
* ``rule_note_xrefs`` — the CROSS REFERENCE / SUPERSEDED / CONSIDERED /
  "derived from" citations, resolved to canonical cite keys.

It then RESTAMPS ``amendments.authority`` and
``provision_versions.source_authority`` for every dated version from the
note: the paragraphs naming that version's effective date, verbatim, or a
fixed sentence saying the note has none. Until 2026-11-02 those columns held a
Claude Haiku paraphrase of the note written into the mirror's commit bodies
(``ingest_rules.commit_meta``); the paraphrase could not be checked against a
source nobody kept. The sidecar is that source.

Until the scraper has written a sidecar for a rule, the commit-body text
stands (``ingest_rules`` still reads it); a later sync replaces it.

Currency (``--currency``): the opening line names every amendment date the
court knows; diffed against the captured versions it says which dated
amendments the corpus is missing (and which captured versions the note never
mentions). The court's version table lists only superseded versions, so this
is the one place the full date list is printed.

Usage:
    python -m ndlaw_mcp.rule_notes                  # census: sidecars vs DB
    python -m ndlaw_mcp.rule_notes --sync --apply   # (re)load every sidecar
    python -m ndlaw_mcp.rule_notes --currency       # note dates vs versions
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from . import corpus

NOTES_SUBDIR = "notes"

SCHEMA = """
    CREATE TABLE IF NOT EXISTS rule_notes (
        provision_id INTEGER PRIMARY KEY REFERENCES provisions(id),
        text_content TEXT NOT NULL,       -- the court's cumulative note, verbatim
        title TEXT,                       -- the page's H1 as the sidecar recorded it
        source_url TEXT,                  -- the rule page the note was read from
        relpath TEXT NOT NULL,            -- sidecar path in the mirror
        mirror_sha TEXT,                  -- mirror commit that last changed the sidecar
        observed_at TEXT,                 -- that commit's date: when the text was seen
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))
    );
    CREATE TABLE IF NOT EXISTS rule_note_paragraphs (
        id INTEGER PRIMARY KEY,
        provision_id INTEGER NOT NULL REFERENCES provisions(id),
        seq INTEGER NOT NULL,             -- document order, 0-based
        kind TEXT NOT NULL,               -- amendment_list | change | general | label |
                                          -- sources | statutes_affected | superseded |
                                          -- considered | cross_reference | affected_other
        unit TEXT,                        -- 'Subdivision (b)', 'Paragraph (a)(1)', 'Section 2'
        effective_dates TEXT,             -- JSON list: ISO dates (or 'YYYY') the paragraph names
        text TEXT NOT NULL,
        UNIQUE(provision_id, seq)
    );
    CREATE INDEX IF NOT EXISTS idx_rnp_provision ON rule_note_paragraphs(provision_id);
    CREATE TABLE IF NOT EXISTS rule_note_sources (
        id INTEGER PRIMARY KEY,
        provision_id INTEGER NOT NULL REFERENCES provisions(id),
        seq INTEGER NOT NULL,
        kind TEXT NOT NULL,               -- 'minutes' (dated meeting) | 'other'
        committee TEXT,                   -- 'Joint Procedure Committee' (carried forward)
        meeting_date TEXT,                -- ISO, first day
        meeting_end TEXT,                 -- ISO, last day of a multi-day meeting, else NULL
        pages TEXT,                       -- as printed, '30-31'
        raw TEXT NOT NULL,                -- the entry verbatim
        UNIQUE(provision_id, seq)
    );
    CREATE INDEX IF NOT EXISTS idx_rns_provision ON rule_note_sources(provision_id);
    CREATE TABLE IF NOT EXISTS rule_note_xrefs (
        id INTEGER PRIMARY KEY,
        provision_id INTEGER NOT NULL REFERENCES provisions(id),
        kind TEXT NOT NULL,               -- cross_reference | superseded | considered |
                                          -- derived_from | affected_other
        to_corpus TEXT,                   -- ndcc | admin | const | rule; NULL = non-ND
        to_citation TEXT NOT NULL,        -- canonical (jetcite normalized)
        to_cite_key TEXT,                 -- corpus.cite_key(to_citation) for ND targets
        raw_text TEXT NOT NULL,
        UNIQUE(provision_id, kind, to_citation)
    );
    CREATE INDEX IF NOT EXISTS idx_rnx_provision ON rule_note_xrefs(provision_id);
    CREATE INDEX IF NOT EXISTS idx_rnx_target ON rule_note_xrefs(to_corpus, to_cite_key);
"""

TABLES = ("rule_notes", "rule_note_paragraphs", "rule_note_sources", "rule_note_xrefs")


def ensure_schema(conn) -> None:
    conn.executescript(SCHEMA)


def has_notes(conn, alias: str | None = None) -> bool:
    master = f"{alias}.sqlite_master" if alias else "sqlite_master"
    try:
        return conn.execute(
            f"SELECT 1 FROM {master} WHERE type='table' AND name='rule_notes'"
        ).fetchone() is not None
    except Exception:
        return False


# ---- text -------------------------------------------------------------------

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")
_MONTH_ALT = "|".join(MONTHS)
DATE_RE = re.compile(
    rf"\b({_MONTH_ALT})\s+(\d{{1,2}})(?:\s*[-–]\s*\d{{1,2}})?\s*,\s*(\d{{4}})\b")
YEAR_ONLY_RE = re.compile(r"\beffective\s+(?:in\s+)?(\d{4})\b(?!\s*[-–,]\s*\d)")
# A change paragraph's OWN effective date is the one an action word anchors
# ("amended, effective March 1, 2011"; "adopted January 1, 1995"; "renumbered
# effective March 1, 2025"). Other dates in the paragraph are something
# else's — "in response to the December 1, 2007, revision of the Federal
# Rules" — and attributing the paragraph to them put 2007-12-01 on 40
# N.D.R.Civ.P. rules as a missing amendment (first currency run, 2026-11-02).
_ANCHOR = (r"\b(?:effective|adopted|approved|amended|renumbered|rescinded|repealed|"
           r"added|deleted|transferred|superseded|abrogated|revised|reorganized|"
           r"redesignated|moved|relettered)\s+(?:on\s+|in\s+|as\s+of\s+)?")
ANCHORED_DATE_RE = re.compile(_ANCHOR + DATE_RE.pattern)
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")

SOURCES_RE = re.compile(r"^\s*SOURCES?\b", re.I)
STATUTES_AFFECTED_RE = re.compile(r"^\s*STATUTES?\s+AFFECTED\b", re.I)
AFFECTED_SUB_RE = re.compile(r"^\s*(SUPERSEDED|CONSIDERED|REPEALED|AFFECTED|AMENDED)\s*:")
CROSS_REF_RE = re.compile(r"^\s*CROSS[\s-]*REFERENCES?\s*:?", re.I)
LABEL_RE = re.compile(r"^\s*\S[^.:]{0,60}:\s*$")
CHANGE_VERB_RE = re.compile(
    r"\b(amended|added|adopted|revised|reorganized|redesignated|renumbered|"
    r"deleted|repealed|moved|rescinded|transferred|abrogated|changed|approved|"
    r"removed|superseded|replaced|stricken|incorporated|relettered|retitled|"
    r"consolidated|restyled|eliminated|expanded|clarified)\b", re.I)
DERIVED_RE = re.compile(
    r"\b(derived from|based (?:up)?on|adapted from|model(?:l)?ed (?:after|on)|"
    r"patterned (?:after|on)|taken from|identical to|follows|tracks)\b", re.I)
_UNIT_RANK = {"rule": 0, "section": 1, "subdivision": 1, "subsection": 2,
              "paragraph": 2, "subparagraph": 3, "clause": 3, "item": 3}
_UNIT_HEAD_RE = re.compile(
    r"^\s*(?:(?:A\s+)?new\s+|former\s+)?"
    r"(rule|sections?|subdivisions?|subsections?|paragraphs?|subparagraphs?|"
    r"clauses?|items?)\b", re.I)
_UNIT_RE = re.compile(
    r"^\s*(?:(?:A\s+)?new\s+|former\s+)?"
    r"((?:rule|sections?|subdivisions?|subsections?|paragraphs?|subparagraphs?|"
    r"clauses?|items?)\s+[^,]*?)\s+(?:was|were|has|have|is|are|had)\b", re.I)
_LIST_VERB = (r"(?:was|were)?\s*(?:adopted|amended|approved|revised|"
              r"reorganized|rescinded|repealed|effective|was|were|and|in|\d{4}|"
              r"Amended|Adopted|Effective|Approved|The\s+explanatory\s+notes?|"
              r",|;|\.|\s)*")
_LIST_HEAD = (r"(?:(?:Rule|Standard|Canon|Section|Order|Form|Table|Appendix|"
              r"Administrative\s+(?:Rule|Order)|This\s+\w+)\s+\S*\s*)?")
AMENDMENT_LIST_RE = re.compile(rf"^{_LIST_HEAD}{_LIST_VERB}$", re.I)

_SIDECAR_H1 = "# Explanatory Notes — "
_SIDECAR_SOURCE = "Source: "


def normalize(text: str) -> str:
    return re.sub(r"[ \t]+", " ", (text or "").replace("\xa0", " "))


def strip_links(text: str) -> str:
    return _MD_LINK_RE.sub(r"\1", text)


def paragraphs(notes: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", normalize(notes)) if p.strip()]


def parse_sidecar(text: str) -> tuple[str, str, str]:
    """(title, url, notes) from a sidecar file's text."""
    title = url = ""
    lines = text.splitlines()
    i = 0
    if lines and lines[0].startswith(_SIDECAR_H1):
        title = lines[0][len(_SIDECAR_H1):].strip()
        i = 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].startswith(_SIDECAR_SOURCE):
        url = lines[i][len(_SIDECAR_SOURCE):].strip()
        i += 1
    return title, url, "\n".join(lines[i:]).strip()


def _iso(m: re.Match) -> str | None:
    try:
        return date(int(m.group(3)), MONTHS.index(m.group(1)) + 1,
                    int(m.group(2))).isoformat()
    except ValueError:
        return None


def dates_in(text: str, *, anchored: bool = False) -> list[str]:
    """ISO dates named in the text (a range counts its first day), then any
    year-only 'effective YYYY', in order, deduplicated. ``anchored`` keeps
    only dates an action word introduces (see ANCHORED_DATE_RE)."""
    text = strip_links(text)
    out: list[str] = []
    for m in (ANCHORED_DATE_RE if anchored else DATE_RE).finditer(text):
        d = _iso(m)
        if d and d not in out:
            out.append(d)
    for m in YEAR_ONLY_RE.finditer(text):
        if m.group(1) not in out:
            out.append(m.group(1))
    return out


def is_amendment_list(para: str) -> bool:
    para = strip_links(para)
    if not DATE_RE.search(para) and not YEAR_ONLY_RE.search(para):
        return False
    return bool(AMENDMENT_LIST_RE.match(DATE_RE.sub(" ", para).strip()))


def unit_rank(para: str) -> int | None:
    m = _UNIT_HEAD_RE.match(strip_links(para))
    return _UNIT_RANK[m.group(1).lower().rstrip("s")] if m else None


def unit_of(para: str) -> str | None:
    m = _UNIT_RE.match(strip_links(para))
    if not m:
        return None
    unit = re.sub(r"\s+", " ", m.group(1)).strip()
    return unit[:1].upper() + unit[1:]


@dataclass
class Para:
    seq: int
    kind: str
    text: str
    unit: str | None = None
    dates: list[str] = field(default_factory=list)


def classify(notes: str) -> list[Para]:
    out: list[Para] = []
    for i, p in enumerate(paragraphs(notes)):
        if SOURCES_RE.match(p):
            kind = "sources"
        elif STATUTES_AFFECTED_RE.match(p):
            kind = "statutes_affected"
        elif AFFECTED_SUB_RE.match(p):
            kind = AFFECTED_SUB_RE.match(p).group(1).lower()
            if kind not in ("superseded", "considered"):
                kind = "affected_other"
        elif CROSS_REF_RE.match(p):
            kind = "cross_reference"
        elif i == 0 and is_amendment_list(p):
            kind = "amendment_list"
        elif LABEL_RE.match(p) and not DATE_RE.search(p):
            kind = "label"
        else:
            ds = dates_in(p, anchored=True)
            kind = "change" if ds and CHANGE_VERB_RE.search(strip_links(p)) else "general"
        para = Para(seq=i, kind=kind, text=p)
        if kind == "amendment_list":
            para.dates = dates_in(p)
        elif kind in ("change", "general"):
            para.dates = dates_in(p, anchored=True)
        if kind == "change":
            para.unit = unit_of(p)
        out.append(para)
    return out


def human_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{MONTHS[d.month - 1]} {d.day}, {d.year}"


def names_date(para: Para, iso: str) -> bool:
    if iso in para.dates:
        return True
    # a year-only 'effective 1971' can only be claimed by a January-1 version
    return iso.endswith("-01-01") and iso[:4] in para.dates


def slice_for_date(paras: list[Para], iso: str | None) -> str:
    """The paragraphs naming ``iso``, verbatim, with any grouping label they
    sit under; fixed sentences when the note cannot speak to the date.
    Mirrors rules-scraper ``explanatory_notes.slice_for_date``."""
    if not paras:
        return "The court's page carries no explanatory note."
    if iso is None:
        return ("The court publishes no effective date for this version, so no "
                "paragraph of the explanatory note can be attributed to it.")
    hits: list[str] = []
    label: Para | None = None
    label_rank: int | None = None
    label_used = False
    listed = False
    for p in paras:
        if p.kind == "amendment_list":
            listed = names_date(p, iso)
            continue
        if p.kind in ("sources", "statutes_affected", "superseded", "considered",
                      "cross_reference", "affected_other"):
            label = None
            continue
        if p.kind == "label":
            label, label_used, label_rank = p, False, unit_rank(p.text)
            continue
        if label is not None:
            r = unit_rank(p.text)
            if r is not None and label_rank is not None and r <= label_rank:
                label = None
        if names_date(p, iso):
            if label and not label_used:
                hits.append(label.text)
                label_used = True
            hits.append(p.text)
    if hits:
        return "\n\n".join(hits)
    if listed:
        return (f"The court's explanatory note lists {human_date(iso)} as an "
                "amendment date but describes no change for it.")
    return f"No paragraph in the court's explanatory note is dated {human_date(iso)}."


# ---- SOURCES ------------------------------------------------------------------

_PAGES_RE = re.compile(r"\bpages?\s+([\dA-Za-z]+(?:\s*[-–]\s*[\dA-Za-z]+)?)", re.I)
_MINUTES_OF_RE = re.compile(r"\bminutes\s+of\b(?:\s+the\b)?", re.I)


def sources(paras: list[Para]) -> list[dict]:
    out: list[dict] = []
    for p in paras:
        if p.kind != "sources":
            continue
        body = re.sub(r"^\s*SOURCES?\s*:?\s*", "", strip_links(p.text), flags=re.I)
        committee: str | None = None
        for raw in re.split(r"\s*;\s*", body):
            raw = raw.strip(" .")
            if not raw:
                continue
            m = DATE_RE.search(raw)
            if not m or _iso(m) is None:
                out.append({"kind": "other", "committee": None, "meeting_date": None,
                            "meeting_end": None, "pages": None, "raw": raw})
                continue
            lead = raw[:m.start()]
            if _MINUTES_OF_RE.search(lead):
                name = _MINUTES_OF_RE.sub(" ", lead)
                name = re.sub(r"\s+of\s*$", "", name.strip(" ,"), flags=re.I).strip(" ,")
                committee = name or committee
            end = None
            rng = re.match(rf"{m.group(1)}\s+{m.group(2)}\s*[-–]\s*(\d{{1,2}})", m.group(0))
            if rng:
                try:
                    end = date(int(m.group(3)), MONTHS.index(m.group(1)) + 1,
                               int(rng.group(1))).isoformat()
                except ValueError:
                    end = None
            pages = _PAGES_RE.search(raw)
            out.append({"kind": "minutes", "committee": committee,
                        "meeting_date": _iso(m), "meeting_end": end,
                        "pages": pages.group(1).replace(" ", "") if pages else None,
                        "raw": raw})
    return out


# ---- cross references -----------------------------------------------------------

CITE_TYPE_TO_CORPUS = {"statute": "ndcc", "regulation": "admin",
                       "constitution": "const", "court_rule": "rule"}
_NDCC_LIST_RE = re.compile(r"N\.D\.C\.C\.\s*§§?\s*([^.;]*?(?:\d[^.;]*?))(?=\.\s|\.$|;|$)")
_NDCC_SECTION_RE = re.compile(r"\b(\d{1,2}(?:\.\d)?-\d{2}(?:\.\d)?-\d{2}(?:\.\d+)?)\b")


def _cites(text: str) -> list[tuple[str | None, str, str | None, str]]:
    """(to_corpus, to_citation, to_cite_key, raw) for every citation jetcite
    finds, plus each section of an ``N.D.C.C. §§ a, b, and c`` list — the
    court's ``(in part)`` tails stop jetcite's list expansion."""
    from jetcite import scan_text  # ingest-time dependency

    out: list[tuple[str | None, str, str | None, str]] = []
    seen: set[str] = set()
    text = strip_links(text)
    for c in scan_text(text, resolve=False):
        to_corpus = CITE_TYPE_TO_CORPUS.get(c.cite_type.value)
        if to_corpus is None:
            continue
        if c.jurisdiction != "nd":
            to_corpus = None
        norm = c.normalized
        if norm in seen:
            continue
        seen.add(norm)
        out.append((to_corpus, norm, corpus.cite_key(norm) if to_corpus else None,
                    c.raw_text.strip()))
    for lst in _NDCC_LIST_RE.finditer(text):
        for sec in _NDCC_SECTION_RE.findall(lst.group(1)):
            norm = f"N.D.C.C. § {sec}"
            if norm in seen:
                continue
            seen.add(norm)
            out.append(("ndcc", norm, corpus.cite_key(norm), sec))
    return out


def xrefs(paras: list[Para], self_key: str) -> list[dict]:
    out: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for p in paras:
        if p.kind in ("cross_reference", "superseded", "considered", "affected_other"):
            kind = p.kind
        elif p.kind == "general" and DERIVED_RE.search(p.text):
            kind = "derived_from"
        elif p.kind == "sources":
            kind = "derived_from"      # the undated tail: 'Fed.R.Ev. 702'
        else:
            continue
        text = p.text
        if p.kind == "sources":
            text = " ; ".join(s["raw"] for s in sources([p]) if s["kind"] == "other")
            if not text:
                continue
        for to_corpus, norm, key, raw in _cites(text):
            if key == self_key or (kind, norm) in seen:
                continue
            seen.add((kind, norm))
            out.append({"kind": kind, "to_corpus": to_corpus, "to_citation": norm,
                        "to_cite_key": key, "raw_text": raw})
    return out


# ---- mirror → DB ------------------------------------------------------------------

def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=True).stdout


def _is_sidecar(relpath: str) -> bool:
    parts = relpath.split("/")
    return (len(parts) == 3 and parts[1] == NOTES_SUBDIR
            and parts[2].startswith("rule-") and parts[2].endswith(".md"))


def sidecar_files(repo: Path) -> list[str]:
    return sorted(f for f in _git(repo, "ls-files").split("\n") if _is_sidecar(f))


def changed_sidecars(repo: Path, rev_range: str) -> list[str]:
    files = _git(repo, "log", "--name-only", "--format=", rev_range).split()
    return sorted({f for f in files if _is_sidecar(f)})


def provision_for(conn, relpath: str):
    """The rules.db provision a sidecar belongs to, or None."""
    cat, _notes, fname = relpath.split("/")
    prefix = corpus.RULE_SET_DIRS.get(cat)
    if prefix is None:
        return None
    citation = f"{prefix} {corpus.rule_number_from_filename(fname)}"
    return conn.execute(
        "SELECT id, citation FROM provisions WHERE corpus='rule' AND cite_key = ?",
        (corpus.cite_key(citation),)).fetchone()


def _last_commit(repo: Path, relpath: str) -> tuple[str | None, str | None]:
    out = _git(repo, "log", "-1", "--format=%H%x1f%aI", "--", relpath).strip()
    if not out:
        return None, None
    sha, iso = out.split("\x1f")
    return sha, iso[:10]


def restamp(conn, pid: int, paras: list[Para], *, apply: bool) -> int:
    """Set every dated version's authority text from the note. Returns the
    number of versions whose text changed."""
    changed = 0
    for v in conn.execute(
            "SELECT id, effective_start, source_authority FROM provision_versions "
            "WHERE provision_id = ? AND effective_start IS NOT NULL", (pid,)):
        text = slice_for_date(paras, v["effective_start"])
        cur_am = conn.execute(
            "SELECT authority FROM amendments WHERE version_id = ?", (v["id"],)).fetchone()
        if (v["source_authority"] or "") == text and (
                cur_am is None or (cur_am["authority"] or "") == text):
            continue
        changed += 1
        if apply:
            conn.execute("UPDATE provision_versions SET source_authority = ? WHERE id = ?",
                         (text, v["id"]))
            conn.execute("UPDATE amendments SET authority = ? WHERE version_id = ?",
                         (text, v["id"]))
    return changed


def sync(conn, repo: Path, relpaths: list[str], *, batch: str, apply: bool,
         restamp_all: bool = False, reparse: bool = False) -> dict:
    """Load the named sidecars (mirror HEAD) into rules.db and restamp the
    authority columns of the provisions they belong to."""
    ensure_schema(conn)
    stats = {"sidecars": len(relpaths), "loaded": 0, "unchanged": 0,
             "unmatched": [], "restamped_versions": 0, "paragraphs": 0,
             "sources": 0, "xrefs": 0}
    for relpath in relpaths:
        prov = provision_for(conn, relpath)
        if prov is None:
            stats["unmatched"].append(relpath)
            continue
        pid = prov["id"]
        try:
            content = _git(repo, "show", f"HEAD:{relpath}")
        except subprocess.CalledProcessError:
            stats["unmatched"].append(relpath + " (deleted)")
            continue
        title, url, notes = parse_sidecar(content)
        sha, observed = _last_commit(repo, relpath)
        cur = conn.execute("SELECT text_content, mirror_sha FROM rule_notes "
                           "WHERE provision_id = ?", (pid,)).fetchone()
        paras = classify(notes)
        if (cur is not None and cur["text_content"] == notes
                and cur["mirror_sha"] == sha and not reparse):
            stats["unchanged"] += 1
            if restamp_all:
                stats["restamped_versions"] += restamp(conn, pid, paras, apply=apply)
            continue
        srcs = sources(paras)
        xr = xrefs(paras, corpus.cite_key(prov["citation"]))
        stats["loaded"] += 1
        stats["paragraphs"] += len(paras)
        stats["sources"] += len(srcs)
        stats["xrefs"] += len(xr)
        if apply:
            conn.execute(
                "INSERT INTO rule_notes (provision_id, text_content, title, source_url, "
                "relpath, mirror_sha, observed_at) VALUES (?,?,?,?,?,?,?) "
                "ON CONFLICT(provision_id) DO UPDATE SET text_content=excluded.text_content, "
                "title=excluded.title, source_url=excluded.source_url, "
                "relpath=excluded.relpath, mirror_sha=excluded.mirror_sha, "
                "observed_at=excluded.observed_at, "
                "updated_at=strftime('%Y-%m-%dT%H:%M:%S','now')",
                (pid, notes, title or None, url or None, relpath, sha, observed))
            for t in ("rule_note_paragraphs", "rule_note_sources", "rule_note_xrefs"):
                conn.execute(f"DELETE FROM {t} WHERE provision_id = ?", (pid,))
            conn.executemany(
                "INSERT INTO rule_note_paragraphs (provision_id, seq, kind, unit, "
                "effective_dates, text) VALUES (?,?,?,?,?,?)",
                [(pid, p.seq, p.kind, p.unit, json.dumps(p.dates) if p.dates else None,
                  p.text) for p in paras])
            conn.executemany(
                "INSERT INTO rule_note_sources (provision_id, seq, kind, committee, "
                "meeting_date, meeting_end, pages, raw) VALUES (?,?,?,?,?,?,?,?)",
                [(pid, i, s["kind"], s["committee"], s["meeting_date"], s["meeting_end"],
                  s["pages"], s["raw"]) for i, s in enumerate(srcs)])
            conn.executemany(
                "INSERT OR IGNORE INTO rule_note_xrefs (provision_id, kind, to_corpus, "
                "to_citation, to_cite_key, raw_text) VALUES (?,?,?,?,?,?)",
                [(pid, x["kind"], x["to_corpus"], x["to_citation"], x["to_cite_key"],
                  x["raw_text"]) for x in xr])
            conn.execute(
                "INSERT INTO changelog (batch, provision_id, version_id, field, "
                "old_value, new_value, authority) VALUES (?,?,NULL,?,?,?,?)",
                (batch, pid, "explanatory_note.synced",
                 cur["mirror_sha"] if cur else None, sha,
                 f"rules-scraper sidecar {relpath} (observed {observed})"))
        stats["restamped_versions"] += restamp(conn, pid, paras, apply=apply)
    if apply:
        conn.commit()
    return stats


# ---- serving ---------------------------------------------------------------------

def fetch(conn, alias: str | None, pid: int) -> dict | None:
    """The note for one provision as get_authority_history serves it, or None
    when the table or the row is absent."""
    if not has_notes(conn, alias):
        return None
    q = f"{alias}." if alias else ""
    row = conn.execute(
        f"SELECT text_content, source_url, observed_at FROM {q}rule_notes "
        f"WHERE provision_id = ?", (pid,)).fetchone()
    if row is None:
        return None
    paras = conn.execute(
        f"SELECT seq, kind, unit, effective_dates, text FROM {q}rule_note_paragraphs "
        f"WHERE provision_id = ? ORDER BY seq", (pid,)).fetchall()
    srcs = conn.execute(
        f"SELECT kind, committee, meeting_date, meeting_end, pages, raw "
        f"FROM {q}rule_note_sources WHERE provision_id = ? ORDER BY seq", (pid,)).fetchall()
    xr = conn.execute(
        f"SELECT kind, to_corpus, to_citation, raw_text FROM {q}rule_note_xrefs "
        f"WHERE provision_id = ? ORDER BY id", (pid,)).fetchall()
    changes = [
        {"effective_dates": json.loads(p["effective_dates"] or "[]"),
         "unit": p["unit"], "text": p["text"]}
        for p in paras if p["kind"] == "change"]
    listed = next((json.loads(p["effective_dates"] or "[]")
                   for p in paras if p["kind"] == "amendment_list"), [])
    return {
        "text": row["text_content"],
        "source_url": row["source_url"],
        "observed_at": row["observed_at"],
        "amendment_dates_listed": listed,
        "changes": changes,
        "sources": [dict(s) for s in srcs],
        "cross_references": [dict(x) for x in xr],
        "note": ("The court's cumulative explanatory note, verbatim, as published on "
                 "the rule's page; 'changes' are its dated paragraphs, each attributed "
                 "to the effective date(s) it names. Each captured version's "
                 "source_authority is the slice of this note for its date."),
    }


def authority_cell(text: str | None, limit: int = 240) -> tuple[str, str]:
    """The History table's authority cell: ``(short, full)``.

    `source_authority` is the verbatim slice of the explanatory note for the
    version's date (2026-11-02), which can run to several paragraphs with
    markdown links — too long for a table cell. `short` is the first paragraph
    with the links reduced to their label text, cut at a word boundary after
    `limit` characters with an ellipsis; `full` is the whole slice, links
    stripped, for a `title` attribute. The note itself is printed in full
    further down the page, so nothing is lost to the reader.
    """
    full = strip_links(normalize(text or "")).strip()
    paras = [p for p in re.split(r"\n\s*\n", full) if p.strip()]
    if not paras:
        return "", ""
    short = paras[0].strip()
    more = len(paras) > 1
    if len(short) > limit:
        cut = short.rfind(" ", 0, limit)
        short = short[: cut if cut > limit // 2 else limit].rstrip(" ,;") + " …"
    elif more:
        short += " …"
    return short, full


def note_xrefs(conn, alias: str | None, pid: int) -> list[dict]:
    """Outbound: every authority this rule's explanatory note cites
    (CROSS REFERENCE, STATUTES AFFECTED, derivation), with its kind."""
    if not has_notes(conn, alias):
        return []
    q = f"{alias}." if alias else ""
    return [dict(r) for r in conn.execute(
        f"SELECT kind, to_corpus, to_citation, to_cite_key, raw_text "
        f"FROM {q}rule_note_xrefs WHERE provision_id = ? ORDER BY kind, to_citation",
        (pid,)).fetchall()]


def notes_citing(conn, alias: str | None, to_corpus: str, cite_key: str) -> list[dict]:
    """Inbound: the rules whose explanatory notes cite the provision
    ``(to_corpus, cite_key)`` — a statute a rule superseded or considered, a
    rule another rule's CROSS REFERENCE names."""
    if not has_notes(conn, alias):
        return []
    q = f"{alias}." if alias else ""
    return [dict(r) for r in conn.execute(
        f"""SELECT DISTINCT p.citation, p.heading, p.status, x.kind, x.raw_text
            FROM {q}rule_note_xrefs x JOIN {q}provisions p ON p.id = x.provision_id
            WHERE x.to_corpus = ? AND x.to_cite_key = ?
            ORDER BY p.citation, x.kind""", (to_corpus, cite_key)).fetchall()]


def paragraph_count(conn, alias: str | None, pid: int) -> int | None:
    if not has_notes(conn, alias):
        return None
    q = f"{alias}." if alias else ""
    row = conn.execute(
        f"SELECT COUNT(*) AS n FROM {q}rule_note_paragraphs WHERE provision_id = ?",
        (pid,)).fetchone()
    has_row = conn.execute(
        f"SELECT 1 FROM {q}rule_notes WHERE provision_id = ?", (pid,)).fetchone()
    return row["n"] if has_row else None


def fetch_text(conn, alias: str | None, pid: int) -> dict | None:
    """Text + provenance only, for the web page."""
    if not has_notes(conn, alias):
        return None
    q = f"{alias}." if alias else ""
    row = conn.execute(
        f"SELECT text_content, source_url, observed_at FROM {q}rule_notes "
        f"WHERE provision_id = ?", (pid,)).fetchone()
    return dict(row) if row else None


# ---- currency -----------------------------------------------------------------------

def currency(conn) -> dict:
    """Note-named amendment dates vs captured versions, per provision.

    ``gaps``: dates the note names, later than the provision's earliest
    captured version, with no version — amendments the corpus is missing.
    ``pre_capture``: note dates before the first captured version (expected:
    the court's version table does not reach back that far).
    ``unexplained``: captured version dates the note never names."""
    if not has_notes(conn):
        return {"provisions": 0, "gaps": [], "pre_capture": 0, "unexplained": []}
    gaps: list[dict] = []
    unexplained: list[dict] = []
    pre_capture = 0
    n = 0
    for prov in conn.execute(
            "SELECT p.id, p.citation FROM rule_notes n JOIN provisions p ON p.id = n.provision_id "
            "ORDER BY p.citation"):
        n += 1
        note_dates: set[str] = set()
        for r in conn.execute(
                "SELECT kind, effective_dates FROM rule_note_paragraphs "
                "WHERE provision_id = ? AND kind IN ('amendment_list','change')", (prov["id"],)):
            for d in json.loads(r["effective_dates"] or "[]"):
                if len(d) == 10:
                    note_dates.add(d)
        versions = {r["effective_start"] for r in conn.execute(
            "SELECT effective_start FROM provision_versions WHERE provision_id = ? "
            "AND effective_start IS NOT NULL", (prov["id"],))}
        if not versions or not note_dates:
            continue
        first = min(versions)
        missing_after = sorted(d for d in note_dates - versions if d > first)
        pre_capture += sum(1 for d in note_dates - versions if d < first)
        if missing_after:
            gaps.append({"citation": prov["citation"], "dates": missing_after})
        silent = sorted(versions - note_dates)
        if silent:
            unexplained.append({"citation": prov["citation"], "dates": silent})
    return {"provisions": n, "gaps": gaps, "pre_capture": pre_capture,
            "unexplained": unexplained}


# ---- CLI -----------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Court-rule explanatory notes → rules.db")
    ap.add_argument("--repo", type=Path, default=Path.home() / "refs" / "rule",
                    help="the rules git mirror (default: refs/rule under the home directory)")
    ap.add_argument("--db", type=Path, default=None)
    ap.add_argument("--sync", action="store_true",
                    help="load every sidecar at mirror HEAD (dry run unless --apply)")
    ap.add_argument("--restamp-all", action="store_true",
                    help="with --sync: restamp authority text even for unchanged notes")
    ap.add_argument("--reparse", action="store_true",
                    help="with --sync: re-derive paragraphs/sources/xrefs and restamp "
                         "for every sidecar (after a parser change)")
    ap.add_argument("--currency", action="store_true",
                    help="note-named amendment dates vs captured versions")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    db_path = args.db or corpus.resolve_corpus_db_path("rule")
    conn = corpus.get_corpus_connection(db_path, read_only=not args.apply)
    if args.currency:
        rep = currency(conn)
        print(f"{rep['provisions']} rules with notes; {len(rep['gaps'])} with note-dated "
              f"amendments missing after first capture; {rep['pre_capture']} note dates "
              f"before first capture; {len(rep['unexplained'])} with versions the note "
              f"never names")
        for g in rep["gaps"]:
            print(f"  GAP  {g['citation']}: {', '.join(g['dates'])}")
        for u in rep["unexplained"][:40]:
            print(f"  silent {u['citation']}: {', '.join(u['dates'])}")
        if len(rep["unexplained"]) > 40:
            print(f"  ... {len(rep['unexplained']) - 40} more")
        return
    files = sidecar_files(args.repo)
    if not args.sync:
        have = conn.execute("SELECT COUNT(*) FROM rule_notes").fetchone()[0] \
            if has_notes(conn) else 0
        print(f"{len(files)} sidecars in {args.repo}; {have} notes in {db_path}")
        return
    from datetime import datetime, timezone
    batch = f"rule-notes-sync-{datetime.now(timezone.utc):%Y-%m-%d}"
    st = sync(conn, args.repo, files, batch=batch, apply=args.apply,
              restamp_all=args.restamp_all, reparse=args.reparse)
    mode = "applied" if args.apply else "planned (dry run — pass --apply)"
    print(f"rule-notes {mode}: {st['loaded']} loaded, {st['unchanged']} unchanged, "
          f"{st['restamped_versions']} versions restamped, {st['paragraphs']} paragraphs, "
          f"{st['sources']} sources, {st['xrefs']} xrefs, {len(st['unmatched'])} unmatched")
    for u in st["unmatched"]:
        print(f"  UNMATCHED {u}")
    conn.close()


if __name__ == "__main__":
    main()
