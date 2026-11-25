"""Historical codes corpus (``codes_hist.db``, alias ``hist``): the codes before the Century
Code, as sections and the derivation references printed under them.

PLAN-session-laws.md Stage 6; schema rulings 1-5 (JT 2026-11-23). Built whole by
``scripts/build_codes_hist.py`` from ``data/codes_hist/``; nothing here writes to it. LOCAL
ONLY for now (ruling 5): the file is not in the release list, so a public server answers
"not installed".

What it serves: a section's catchline, where it sits in the scan, the line of descent its
derivation note prints, and the later sections whose notes name it. NOT its text (tables
first). Every reference came from OCR and carries its witnesses: `confirmed` where two
agree, `conflict` where two readers of the page give different numbers.

Canonical citations (ruling 1, the Court's traditional abbreviations, normalized):
``N.D.R.C. 1943 § 35-1304`` · ``N.D.C.L. 1913 § 6877`` · ``N.D.C.L. Supp. 1925 § 6877a1`` ·
``N.D.R.C. 1905 § 6295`` (1899, 1895 likewise) · ``Dakota C.L. 1887 § 3669``.
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

from platformdirs import user_data_path

HIST_CORPUS = {"file": "codes_hist.db", "alias": "hist", "label": "N.D. historical codes (1887-1943)"}

_NUM = r"(?P<num>\d{1,2}-\d{4,5}|\d{1,5}[a-z]?\d*)"
_SEC = r"(?:§+|[Ss]ecs?\.|[Ss]ections?|s\.)"
_CODES = [
    # (prefix, pattern for the code's name as opinions and the codes themselves write it)
    ("N.D.C.L. Supp. 1925", r"(?:N\.\s?D\.\s?)?(?:C\.\s?L\.\s?Supp\.\s?1925|1925\s+Supp(?:\.|lement)(?:\s+to\s+(?:the\s+)?(?:C\.\s?L\.|Comp(?:\.|iled)\s+Laws)(?:\s+(?:of\s+)?1913)?)?|Supp\.\s?(?:to\s+)?(?:C\.\s?L\.|Comp\.\s+Laws)\s?1925)"),
    ("N.D.R.C. 1943", r"(?:N\.\s?D\.\s?)?(?:R\.\s?C\.|Rev(?:\.|ised)\s+Codes?)\s*(?:of\s+)?1943"),
    ("N.D.C.L. 1913", r"(?:N\.\s?D\.\s?)?(?:C\.\s?L\.|Comp(?:\.|iled)\s+Laws)\s*(?:of\s+)?1913"),
    ("N.D.R.C. 1905", r"(?:N\.\s?D\.\s?)?(?:R\.\s?C\.|Rev(?:\.|ised)\s+Codes?)\s*(?:of\s+)?1905"),
    ("N.D.R.C. 1899", r"(?:N\.\s?D\.\s?)?(?:R\.\s?C\.|Rev(?:\.|ised)\s+Codes?)\s*(?:of\s+)?1899"),
    ("N.D.R.C. 1895", r"(?:N\.\s?D\.\s?)?(?:R\.\s?C\.|Rev(?:\.|ised)\s+Codes?)\s*(?:of\s+)?1895"),
    ("Dakota C.L. 1887", r"(?:Dakota\s+)?(?:C\.\s?L\.|Comp(?:\.|iled)\s+Laws)\s*(?:of\s+)?1887"),
]
_FORMS = [(p, re.compile(rf"^(?:{c}),?\s*(?:{_SEC}\s*)?{_NUM}$"), re.compile(rf"^{_SEC}\s*{_NUM},?\s*(?:of\s+(?:the\s+)?)?(?:{c})$"))
          for p, c in _CODES]


def parse_cite(citation: str) -> dict | None:
    """Parse one historical-code citation to ``{"prefix", "number", "citation"}``; None when
    the string is not one. A lookup parser for a whole string a caller hands it (as
    sl_corpus.parse_cite is); extraction from running text is jetcite's job."""
    s = re.sub(r"\s+", " ", (citation or "").strip().rstrip("."))
    for prefix, lead, trail in _FORMS:
        m = lead.match(s) or trail.match(s)
        if m:
            return {"prefix": prefix, "number": m.group("num"), "citation": f"{prefix} § {m.group('num')}"}
    return None


def resolve_hist_db_path() -> Path:
    """Locate codes_hist.db (mirrors sl_corpus.resolve_sl_db_path)."""
    env = os.environ.get("NDLAW_HIST_DB")
    if env:
        return Path(env).expanduser()
    bundled = Path(__file__).resolve().parent.parent / HIST_CORPUS["file"]
    if bundled.exists():
        return bundled
    return user_data_path("ndcourts-mcp", appauthor=False) / HIST_CORPUS["file"]


def attach_hist(conn: sqlite3.Connection, *, read_only: bool = False) -> bool:
    """ATTACH codes_hist.db under alias 'hist' (mirrors attach_sl)."""
    alias = HIST_CORPUS["alias"]
    if alias in {r[1] for r in conn.execute("PRAGMA database_list")}:
        return True
    path = resolve_hist_db_path()
    if not path.exists():
        return False
    conn.execute(f"ATTACH DATABASE ? AS {alias}", (f"file:{path}?mode=ro" if read_only else str(path),))
    return True


def _reading(witnesses: str, confirmed: int, conflict: int) -> str:
    if conflict:
        return "CONFLICT: two readers of the page give different numbers for this reference; neither is established"
    if confirmed:
        return "confirmed by two witnesses"
    return "read by one OCR pass, not confirmed"


def section_answer(conn: sqlite3.Connection, spec: dict, requested: str) -> dict:
    """The lookup_authority answer for a historical-code section."""
    cite = spec["citation"]
    code = conn.execute("SELECT code, name, year, parsed FROM hist.hc_codes WHERE cite_prefix = ?", (spec["prefix"],)).fetchone()
    row = conn.execute("SELECT id, catchline, scan_file, scan_page, number_basis FROM hist.hc_sections WHERE citation = ?",
                       (cite,)).fetchone()
    into = conn.execute(
        "SELECT u.to_citation, u.confirmed, s.catchline FROM hist.hc_successors u "
        "LEFT JOIN hist.hc_sections s ON s.citation = u.to_citation "
        "WHERE u.from_citation = ? AND u.served = 1 ORDER BY u.to_citation", (cite,)).fetchall()
    if row is None and not into:
        return {"found": False, "citation": requested, "corpus": "hist", "canonical": cite,
                "error": (f"{cite} is not among the sections held, and no later code's derivation note names it. "
                          + ("Its code has not been parsed; only references to it are held." if code and not code[3] else
                             "The section may not exist, or its heading could not be read from the scan."))}
    out: dict = {"found": True, "corpus": "hist", "citation": cite, "requested_citation": requested,
                 "code": code[1] if code else spec["prefix"], "code_year": code[2] if code else None,
                 "held": row is not None, "text": None,
                 "text_note": "The text of this section is not served. Derivation tables only; read the scan for the text."}
    warnings = ["Compiled from OCR of scanned books. Every reference states how it was read; an unconfirmed one "
                "may carry a wrong digit. Check the scan before relying on a number."]
    if row is not None:
        out.update(catchline=row[1], scan={"file": row[2], "pdf_page_index": row[3]})
        if row[4] == "sequence":
            warnings.append("This section's NUMBER was not read from the page: its digits were illegible and it was "
                            "numbered from its place between the sections before and after it.")
        elif row[4] == "head":
            warnings.append("This section's NUMBER was misread on the page (one digit off) and was corrected from "
                            "its place between the sections before and after it and the page's running head "
                            "(e.g. '§§ 7581-7584').")
        chain = []
        for d_id, seq, line, rel, raw, to_code, yr, ch, secs, subs, wit, conf, confl in conn.execute(
                "SELECT id, seq, line, relation, raw, to_code, to_year, to_chapter, to_sections, subsections, witnesses, confirmed, conflict "
                "FROM hist.hc_derivations WHERE section_id = ? ORDER BY seq", (row[0],)):
            targets = [{"citation": c, "kind": k, "in_corpus": bool(r)} for c, k, r in conn.execute(
                "SELECT to_citation, to_kind, resolved FROM hist.hc_targets WHERE derivation_id = ? ORDER BY rowid", (d_id,))]
            chain.append({"seq": seq, "line_of_descent": line, "relation": rel, "cites": targets,
                          **({"subsections": subs} if subs else {}), **({"as_printed": raw} if raw else {}),
                          "witnesses": wit.split("+"), "reading": _reading(wit, conf, confl)})
        out["derivation"] = chain
        out["derivation_note"] = [{"reader": r, "note": n} for r, n in conn.execute(
            "SELECT reader, note FROM hist.hc_notes WHERE section_id = ? ORDER BY reader", (row[0],))]
        if not chain:
            warnings.append("No derivation reference could be read under this section (it may have none, or the note was illegible).")
    else:
        warnings.append(f"{cite} is known only through later codes' derivation notes"
                        + ("; its own code has not been parsed." if code and not code[3] else "."))
    out["derived_into"] = [{"citation": c, "catchline": cl,
                            "reading": "confirmed by two witnesses" if conf else "read by one OCR pass, not confirmed"}
                           for c, conf, cl in into]
    if into:
        out["derived_into_note"] = ("Later sections whose printed derivation notes name this one: each derives from it "
                                    "in whole or part, and may have been amended on the way.")
    if spec["prefix"] == "N.D.R.C. 1943":
        warnings.append("No link from the Revised Code of 1943 to the Century Code is served: the published parallel "
                        "tables are not held, and a matching section number is not proof of the same law.")
    n = conn.execute("SELECT COUNT(DISTINCT opinion_id) FROM text_citations WHERE normalized = ?", (cite,)).fetchone()[0]
    out["opinions_citing"] = n
    if not n:
        out["opinions_citing_note"] = "Opinion citations to the historical codes are not yet extracted; 0 is not a finding."
    out["warning"] = " ".join(warnings)
    return out
