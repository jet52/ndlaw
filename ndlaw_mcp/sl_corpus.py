"""North Dakota Session Laws corpus (``sessionlaws.db``, alias ``sl``).

Stage 3 of PLAN-session-laws.md. An act is a dated event, not a provision with
versions, so this corpus has its own tables (CORPUS-SCHEMA.md § sessionlaws)
and, like the AG and JEAC corpora, its own attach and lookup. The file is
built whole by ``scripts/build_sessionlaws.py``; nothing here writes to it.

Canonical citation (JT 2026-11-18): the Bluebook form the Court prints,
``2019 N.D. Sess. Laws ch. 404`` (``, § 2`` for an act section). The Century
Code's ``S.L. 2019, ch. 404`` and ``S.L. 2021 (sp.), ch. 553`` resolve too.
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

from platformdirs import user_data_path

SL_CORPUS = {"file": "sessionlaws.db", "alias": "sl", "label": "N.D. Session Laws"}

_YEAR = r"(?P<year>1[89]\d\d(?:-\d\d)?|20\d\d)"
_CH = r"[Cc]h(?:\.|apter)\s*(?P<ch>\d{1,4})"
_SEC = r"(?:,?\s*(?:§|[Ss]ec(?:\.|tion))\s*(?P<sec>\d{1,3}))?"
_FORMS = [
    # 2019 N.D. Sess. Laws ch. 404, § 2   |   1919 N.D. Sess. Laws Spec. Sess. ch. 4   |   1987 N.D. Laws ch. 194
    re.compile(rf"^{_YEAR}\s+N\.\s?D\.\s?(?:Sess\.\s?)?Laws,?\s*(?P<sp>Spec\.\s?Sess\.,?\s*)?{_CH}{_SEC}$"),
    # 1883 Dakota Terr. Sess. Laws ch. 5
    re.compile(rf"^{_YEAR}\s+Dakota\s+Terr\.\s?(?:Sess\.\s?)?Laws,?\s*(?P<terr>){_CH}{_SEC}$"),
    # S.L. 2019, ch. 404, § 2   |   S.L. 2021 (sp.), ch. 553
    re.compile(rf"^S\.\s?L\.\s?{_YEAR}\s*(?P<sp>\(sp\.\))?,?\s*{_CH}{_SEC}$"),
]


def parse_cite(citation: str) -> dict | None:
    """Parse one session-law citation; None when the string is not one.

    A lookup parser, not an extractor: it reads a whole string a caller hands
    it. Extraction from running text is jetcite's job (ruling 2)."""
    s = re.sub(r"\s+", " ", (citation or "").strip().rstrip("."))
    for rx in _FORMS:
        m = rx.match(s)
        if m:
            g = m.groupdict()
            return {"year": g["year"], "chapter": int(g["ch"]),
                    "section": int(g["sec"]) if g.get("sec") else None,
                    "special": bool(g.get("sp")), "territorial": "terr" in g}
    return None


def resolve_sl_db_path() -> Path:
    """Locate sessionlaws.db (mirrors jeac_corpus.resolve_jeac_db_path)."""
    env = os.environ.get("NDLAW_SL_DB")
    if env:
        return Path(env).expanduser()
    bundled = Path(__file__).resolve().parent.parent / SL_CORPUS["file"]
    if bundled.exists():
        return bundled
    return user_data_path("ndcourts-mcp", appauthor=False) / SL_CORPUS["file"]


def attach_sl(conn: sqlite3.Connection, *, read_only: bool = False) -> bool:
    """ATTACH sessionlaws.db under alias 'sl' (mirrors attach_jeac)."""
    alias = SL_CORPUS["alias"]
    if alias in {r[1] for r in conn.execute("PRAGMA database_list")}:
        return True
    path = resolve_sl_db_path()
    if not path.exists():
        return False
    conn.execute(f"ATTACH DATABASE ? AS {alias}", (f"file:{path}?mode=ro" if read_only else str(path),))
    return True


def find_chapter(conn: sqlite3.Connection, spec: dict):
    """The sl_chapters row a parsed citation names, or None."""
    q = ("SELECT c.* FROM sl.sl_chapters c JOIN sl.sl_sessions s ON s.session = c.session "
         "WHERE s.year_label = ? AND c.chapter = ? AND s.kind {} ORDER BY s.session")
    if spec["territorial"]:
        rows = conn.execute(q.format("= 'territorial'"), (spec["year"], spec["chapter"])).fetchall()
    elif spec["special"]:
        rows = conn.execute(q.format("= 'special'"), (spec["year"], spec["chapter"])).fetchall()
    else:
        # the regular session's chapter; a special session's where its numbers do not collide
        rows = conn.execute(q.format("= 'regular'"), (spec["year"], spec["chapter"])).fetchall() \
            or conn.execute(q.format("= 'special'"), (spec["year"], spec["chapter"])).fetchall()
    if not rows and not spec["special"] and not spec["territorial"]:
        # a year the volume does not carry as its label: `S.L. 1890` (the first session,
        # 1889-90) and a territorial act cited in the State's form (`S.L. 1883`)
        rows = conn.execute(
            "SELECT c.* FROM sl.sl_chapter_aliases a JOIN sl.sl_chapters c ON c.id = a.chapter_id WHERE a.alias = ?",
            (f"{spec['year']} n.d. sess. laws ch. {spec['chapter']}",)).fetchall()
    return rows[0] if rows else None


_REDLINE_NOTE = ("The text of an amending, creating or repealing section is not served: the volume "
                 "prints struck and added words together, and the redline is not yet captured. "
                 "Read the act at source_url, or the section in the Code.")


def chapter_answer(conn: sqlite3.Connection, spec: dict, requested: str, *, row=None) -> dict:
    """lookup_authority's answer for a session-law chapter or act section.
    ``row`` is an sl_chapters row the caller already holds (the web page)."""
    ch = row if row is not None else find_chapter(conn, spec)
    if ch is None:
        return {"found": False, "corpus": "sl", "citation": requested,
                "error": "No session-law chapter by that citation is indexed. The chapter index is "
                         "incomplete before 1953."}
    ch = dict(ch)
    out = {"found": True, "corpus": "sl", "unit": "chapter", "citation": ch["citation"],
           "also_cited_as": [r[0] for r in conn.execute(
               "SELECT alias FROM sl.sl_chapter_aliases WHERE chapter_id = ? AND form <> 'canonical' ORDER BY form",
               (ch["id"],))],
           "session": ch["session"], "bill": ch["bill"], "title": ch["title"], "status": ch["status"],
           "approved_date": ch["approved_date"], "filed_date": ch["filed_date"],
           "effective_date": ch["effective_date"], "effective_basis": ch["effective_basis"],
           "effective_note": ch["effective_note"], "source_url": ch["source_url"],
           "web_path": f"/sl/{ch['session']}/{ch['chapter']}",
           "source_file": ch["source_file"], "pdf_page": ch["pdf_page"], "detail": ch["detail"]}
    warnings = []
    if ch["detail"] == "index":
        warnings.append("Index-only entry: sessions before 1997 carry the chapter's title, bill and PDF page, "
                        "not its effective date or sections.")
        if ch["title_truncated"]:
            warnings.append("The title is truncated in the index.")
        if ch["index_quality"] and ch["index_quality"] != "good":
            warnings.append(f"The index builder graded this entry '{ch['index_quality']}'.")
    if ch["status"] and ch["status"] not in ("enacted", "initiated-measure"):
        warnings.append({"vetoed": "This chapter prints a vetoed measure; it is not law.",
                         "resolution": "This chapter is a concurrent resolution, not a law.",
                         "back-matter": "This chapter is printed with the volume's constitutional amendments "
                                        "and measures, after the acts."}[ch["status"]])
    if ch["effective_basis"] == "varies":
        warnings.append("The act's sections take effect on different dates; see sections_affected.")
    if ch["parse_flag"]:
        warnings.append("The act-section list is incomplete: the parse missed a section heading.")
    secs = conn.execute("SELECT * FROM sl.sl_sections WHERE chapter_id = ? ORDER BY section_no", (ch["id"],)).fetchall()
    tg = {}
    for sid, target in conn.execute(
            "SELECT t.section_id, t.target FROM sl.sl_section_targets t JOIN sl.sl_sections s ON s.id = t.section_id "
            "WHERE s.chapter_id = ? ORDER BY t.rowid", (ch["id"],)):
        tg.setdefault(sid, []).append(target)
    if spec["section"] is not None:
        row = next((dict(s) for s in secs if s["section_no"] == spec["section"]), None)
        if row is None:
            out.update(found=False, unit="act-section",
                       error=f"{ch['citation']} has no section {spec['section']} in the parsed act "
                             f"({len(secs)} sections parsed).")
            return out
        out.update(unit="act-section", chapter_citation=ch["citation"], citation=row["citation"],
                   caption=row["caption"], action=row["action"], lead=row["lead"],
                   targets=tg.get(row["id"], []), text=row["text"], text_basis=row["text_basis"])
        if row["text"] is None:
            warnings.append(_REDLINE_NOTE)
        elif row["text_basis"] == "pdftotext-flowed-table":
            warnings.append("This section holds a table of amounts; its columns are run together in the text.")
    else:
        out["act_sections"] = [{"section": s["section_no"], "caption": s["caption"], "action": s["action"],
                                "targets": tg.get(s["id"], []), "has_text": s["text"] is not None} for s in secs]
        out["sections_affected"] = [dict(r) for r in conn.execute(
            "SELECT ndcc_section, action, sub, source, effective_date, effective_basis, rule FROM sl.sl_affected "
            "WHERE chapter_id = ? ORDER BY ndcc_section, action", (ch["id"],))]
        if any(s["text"] is None for s in secs):
            warnings.append(_REDLINE_NOTE)
    out.update(citing(conn, ch["id"]))
    if warnings:
        out["warnings"] = warnings
    return out


def citing(conn: sqlite3.Connection, chapter_id: int, limit: int = 25) -> dict:
    """Court and AG opinions that cite the chapter (jetcite `session_law` rows).

    Matches on every canonical-form alias, since an opinion may write a
    special session's chapter with or without "Spec. Sess.". Only the
    reporter-style forms are extracted (PLAN-session-laws § 4a, Stage 3
    ruling 2), so prose cites ("chapter 67 of the Session Laws of 1897") are
    not counted here."""
    forms = [r[0] for r in conn.execute(
        "SELECT alias FROM sl.sl_chapter_aliases WHERE chapter_id = ? AND form = 'canonical'", (chapter_id,))]
    marks = ",".join("?" * len(forms))
    out = {}
    rows = conn.execute(
        f"SELECT DISTINCT o.id, o.case_name, o.date_filed, "
        f"(SELECT citation FROM citations c WHERE c.opinion_id = o.id ORDER BY (citation GLOB '[0-9][0-9][0-9][0-9] ND *') DESC, c.id LIMIT 1) "
        f"FROM text_citations t JOIN opinions o ON o.id = t.opinion_id "
        f"WHERE t.cite_type = 'session_law' AND lower(t.normalized) IN ({marks}) ORDER BY o.date_filed DESC", forms).fetchall()
    out["opinions_citing"] = len(rows)
    out["citing_opinions"] = [{"citation": r[3], "case_name": r[1], "date_filed": r[2]} for r in rows[:limit]]
    if "ag" in {r[1] for r in conn.execute("PRAGMA database_list")}:
        ag = conn.execute(
            f"SELECT DISTINCT a.ag_cite, a.date_issued FROM ag.ag_text_citations t JOIN ag.ag_opinions a ON a.id = t.ag_opinion_id "
            f"WHERE t.cite_type = 'session_law' AND lower(t.normalized) IN ({marks}) ORDER BY a.date_issued DESC", forms).fetchall()
        out["ag_opinions_citing"] = len(ag)
        out["citing_ag_opinions"] = [{"citation": r[0], "date_issued": r[1]} for r in ag[:limit]]
    return out
