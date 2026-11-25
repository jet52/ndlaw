"""North Dakota Pattern Jury Instructions corpus (``ndji.db``, alias ``ndji``).

The civil (C-) and criminal (K-) instructions of the Pattern Jury Instruction Commission, one
edition (2026), each with its text, its notes and authorities, the authorities those notes cite
(resolved against the other corpora), the other instructions it refers to, and the opinions
that cite it by number.

Built whole by ``scripts/build_ndji.py`` from the Commission's instruction files; nothing here
writes to it. Not distributed: the file is not in the release list, so a server without it
answers "not installed" (and its web page 404s).

Canonical citations (JT 2026-11-24): ``NDJI-Civil C-2.05`` · ``NDJI-Criminal K-18.01``. The
letter alone fixes the series, so every form the opinions and the instructions themselves use
("N.D.J.I.—Civil C-74.40", "NDJI C - 2.80", "Pattern Jury Instruction K 21.10") resolves.
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

from platformdirs import user_data_path

NDJI_CORPUS = {"file": "ndji.db", "alias": "ndji",
               "label": "N.D. Pattern Jury Instructions (2026 edition; local only)"}

SERIES = {"C": "Civil", "K": "Criminal"}

# The charter's required statement (Charter of the North Dakota Pattern Jury Instruction
# Commission § 5), served with every instruction.
NOTICE = ("Published by the North Dakota Pattern Jury Instruction Commission only for the "
          "benefit of the bench and bar; publication does not imply either approval or "
          "authoritative construction by the North Dakota Supreme Court.")

# "NDJI", "N.D.J.I.", "N. D. J. I.", "Pattern Jury Instruction(s)", "North Dakota Pattern
# Jury Instruction(s)" -- the name that must precede a number for it to count as one.
ANCHOR = r"(?:N\.?\s?D\.?\s?J\.?\s?I\.?|(?:North\s+Dakota\s+)?Pattern\s+Jury\s+Instructions?)"
_SER_WORD = r"(?:\s*[-–—,]?\s*(?P<word>Civil|Criminal|Civ\.?|Crim\.?))?"
NUMBER = r"(?P<letter>[CK])\s?[-–—]?\s?(?P<num>\d{1,3}\.\d{1,3})"
# After 2003 opinions also write the current number without its letter, the series word
# standing for it ("N.D.J.I. Civ. No. 17.05", "NDJI-Civil 50.32"). A whole number with the
# series word ("NDJI-Civil 1660", "N.D.J.I.Crim. No. 2001") is the numbering used before the
# C-/K- scheme (opinions through 1998) and does not map onto it.
_BARE = r"(?P<bare>\d{1,3}\.\d{1,3})"
_OLD = r"(?P<old>\d{1,4})"
_WHOLE = re.compile(rf"^(?:{ANCHOR}){_SER_WORD}\s*[-–—,:]?\s*(?:No\.?\s*)?"
                    rf"(?:{NUMBER}|{_BARE}|{_OLD})$", re.I)
NUMBER_RX = re.compile(rf"(?<![A-Za-z0-9]){NUMBER}(?![\d])")


def canonical(letter: str, num: str) -> str:
    letter = letter.upper()
    return f"NDJI-{SERIES[letter]} {letter}-{num}"


def _word_letter(word: str) -> str | None:
    w = (word or "")[:3].lower()
    return {"civ": "C", "cri": "K"}.get(w)


def parse_cite(citation: str) -> dict | None:
    """Parse one whole-string NDJI citation to ``{"letter", "number", "citation"}``; None when
    the string is not one. A series word that contradicts the letter ("NDJI-Civil K-1.10") is
    not a citation; a number with no letter needs the series word. A whole number under the
    series word is the pre-C-/K- numbering and comes back with ``old`` set."""
    s = re.sub(r"\s+", " ", (citation or "").strip().rstrip("."))
    m = _WHOLE.match(s)
    if not m:
        return None
    wl = _word_letter(m.group("word"))
    if m.group("letter"):
        letter, num = m.group("letter").upper(), m.group("num")
        if wl and wl != letter:
            return None
    elif wl and m.group("bare"):
        letter, num = wl, m.group("bare")
    elif wl and m.group("old"):
        return {"letter": wl, "number": None, "old": m.group("old"),
                "citation": f"NDJI-{SERIES[wl]} {m.group('old')}"}
    else:
        return None
    return {"letter": letter, "number": f"{letter}-{num}", "citation": canonical(letter, num)}


# Mentions in running text ("NDJI-Civil C-74.25 and C-74.40" in an opinion) are read by
# jetcite's jury_instruction matcher (>= 3.0.0), the one reader for the citation graph and
# for this corpus's cited-by table; parse_cite above reads only a whole-string citation.


def resolve_ndji_db_path() -> Path:
    """Locate ndji.db (mirrors hist_corpus.resolve_hist_db_path)."""
    env = os.environ.get("NDLAW_NDJI_DB")
    if env:
        return Path(env).expanduser()
    bundled = Path(__file__).resolve().parent.parent / NDJI_CORPUS["file"]
    if bundled.exists():
        return bundled
    return user_data_path("ndcourts-mcp", appauthor=False) / NDJI_CORPUS["file"]


def attach_ndji(conn: sqlite3.Connection, *, read_only: bool = False) -> bool:
    """ATTACH ndji.db under alias 'ndji' (mirrors attach_hist)."""
    alias = NDJI_CORPUS["alias"]
    if alias in {r[1] for r in conn.execute("PRAGMA database_list")}:
        return True
    path = resolve_ndji_db_path()
    if not path.exists():
        return False
    conn.execute(f"ATTACH DATABASE ? AS {alias}", (f"file:{path}?mode=ro" if read_only else str(path),))
    return True


def _meta(conn) -> dict:
    return {r[0]: r[1] for r in conn.execute("SELECT key, value FROM ndji.ndji_meta")}


def instruction_answer(conn: sqlite3.Connection, spec: dict, citation: str) -> dict:
    """The lookup_authority answer for one instruction."""
    conn.row_factory = sqlite3.Row
    meta = _meta(conn)
    if spec.get("old"):
        return {"found": False, "corpus": "ndji", "citation": spec["citation"],
                "requested_citation": citation, "edition": meta.get("edition"),
                "error": f"{spec['citation']} is in the numbering used before the C-/K- scheme "
                         f"(opinions through the late 1990s); it does not map onto the "
                         f"{meta.get('edition')} numbers, and that edition is the only one held."}
    r = conn.execute("SELECT * FROM ndji.ndji_instructions WHERE number = ?", (spec["number"],)).fetchone()
    if r is None:
        letter, num = spec["number"].split("-", 1)
        chapter = num.split(".")[0]
        near = [x[0] for x in conn.execute(
            "SELECT citation FROM ndji.ndji_instructions WHERE number LIKE ? ORDER BY ord",
            (f"{letter}-{chapter}.%",))]
        return {"found": False, "corpus": "ndji", "citation": spec["citation"],
                "requested_citation": citation, "edition": meta.get("edition"),
                "error": f"{spec['citation']} is not in the {meta.get('edition')} "
                         f"(an older opinion may cite a number since withdrawn or renumbered).",
                "same_chapter": near}
    iid = r["id"]
    cites = [dict(x) for x in conn.execute(
        "SELECT normalized AS citation, cite_type, raw_text, part, resolved_corpus "
        "FROM ndji.ndji_citations WHERE instruction_id = ? ORDER BY seq", (iid,))]
    for c in cites:
        c["resolved"] = c["resolved_corpus"] is not None
    refers_to = [dict(x) for x in conn.execute(
        "SELECT x.target_citation AS citation, t.title, x.raw_text FROM ndji.ndji_xrefs x "
        "LEFT JOIN ndji.ndji_instructions t ON t.id = x.target_id "
        "WHERE x.instruction_id = ? ORDER BY x.seq", (iid,))]
    referred_by = [dict(x) for x in conn.execute(
        "SELECT DISTINCT s.citation, s.title FROM ndji.ndji_xrefs x "
        "JOIN ndji.ndji_instructions s ON s.id = x.instruction_id "
        "WHERE x.target_id = ? ORDER BY s.ord", (iid,))]
    cited_by = [dict(x) for x in conn.execute(
        "SELECT opinion_citation AS citation, case_name, date_filed, raw_text, context, "
        "predates_revision FROM ndji.ndji_cited_by WHERE instruction_id = ? "
        "ORDER BY date_filed DESC", (iid,))]
    for c in cited_by:
        c["predates_revision"] = bool(c["predates_revision"])
    warnings = []
    if any(c["predates_revision"] for c in cited_by):
        warnings.append(f"Opinions marked predates_revision were decided before this instruction's "
                        f"{r['revision_year']} revision and applied an earlier text; this corpus "
                        f"holds only the {meta.get('edition')} edition.")
    if r["status"] != "current":
        warnings.append(f"The Commission lists this instruction as {r['status'].upper()} in the "
                        f"{meta.get('edition')}"
                        + (f"; see {r['successor']}." if r["successor"] else "."))
    if r["images"] and r["images_transcribed"]:
        warnings.append(f"The form text from the source's image ({r['images']}: caption and form) is a "
                        f"transcription, read off the image and checked against an OCR read; the "
                        f"layout is flattened (caption columns joined by ' | ').")
    elif r["images"]:
        warnings.append(f"This instruction prints an image not held here: {r['images']}.")
    return {
        "found": True, "corpus": "ndji", "citation": r["citation"], "requested_citation": citation,
        "title": r["title"], "status": r["status"], "successor": r["successor"],
        "revision_year": r["revision_year"], "section": r["section_path"],
        "edition": meta.get("edition"), "text": r["text"], "notes": r["notes"],
        "cites": cites, "refers_to": refers_to, "referred_by": referred_by,
        "cited_by_opinions": cited_by, "notice": NOTICE,
        "source": meta.get("source"),
        **({"warning": " ".join(warnings)} if warnings else {}),
    }


def search(conn: sqlite3.Connection, fts_query: str, limit: int) -> list[dict]:
    """Full-text hits for search_authority(corpus_name='ndji')."""
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT i.citation, i.title, i.revision_year, "
        "snippet(f.ndji_fts, 2, '>>>', '<<<', '…', 40) AS excerpt, "
        "snippet(f.ndji_fts, -1, '>>>', '<<<', '…', 40) AS excerpt_any "
        "FROM ndji.ndji_fts f JOIN ndji.ndji_instructions i ON i.id = f.rowid "
        "WHERE f.ndji_fts MATCH ? ORDER BY rank LIMIT ?", (fts_query, limit)).fetchall()
    return [{"corpus": "ndji", "citation": r["citation"], "heading": r["title"],
             "revision_year": r["revision_year"], "effective_start": None, "is_current": True,
             "excerpt": r["excerpt"] if ">>>" in (r["excerpt"] or "") else r["excerpt_any"]}
            for r in rows]
