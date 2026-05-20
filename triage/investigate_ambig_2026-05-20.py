"""Investigate the 6 AMBIG entries from the vol-16-79 mispaired adjudication.

Mid-jaccard (0.35-0.50) means the .doc body neither clearly matches nor
clearly diverges from the cite-matched row. For each, check whether the
DB has the opinion the .doc names under a different OID.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from ndcourts_mcp.db import get_connection, DEFAULT_DB_PATH  # noqa: E402
from ndcourts_mcp.ingest_westlaw import (  # noqa: E402
    _doc_to_text,
    _parse_westlaw_doc,
    _normalize_case_name,
)

AMBIGS = [
    ("/Users/jerod/refs/nd/opin/N.D./16/0059-Kerr-v-Herred.doc", 274),
    ("/Users/jerod/refs/nd/opin/N.D./16/0059-Kerr-v-Swanson.doc", 274),
    ("/Users/jerod/refs/nd/opin/N.D./19/0057-State-ex-rel-McCue-v-Great-Northern-R-Co.doc", 499),
    ("/Users/jerod/refs/nd/opin/N.D./27/0458-Bussey-v-Boynton.doc", 1186),
    ("/Users/jerod/refs/nd/opin/N.D./44/0250-Nelson-v-Middlewest-Grain-Co.doc", 2167),
    ("/Users/jerod/refs/nd/opin/N.D./44/0247-Lammadee-v-Middlewest-Grain-Co.doc", 2171),
]

WORD = re.compile(r"[a-z]{4,}")
STOP = {
    "court", "case", "cause", "appeal", "appellant", "appellee", "respondent",
    "plaintiff", "plaintiffs", "defendant", "defendants", "judgment", "order",
    "motion", "trial", "term", "north", "dakota", "supreme", "syllabus",
    "opinion", "filed", "this", "that", "with", "from", "have", "were", "been",
    "their", "they", "such", "which", "upon", "said", "shall", "would", "where",
    "there", "thereof", "therein", "thereto", "wherein", "whether", "before",
    "after", "above", "under", "must", "made", "make", "also", "found", "find",
    "held", "hold",
}


def toks(s: str) -> set[str]:
    return {w for w in WORD.findall((s or "").lower()) if w not in STOP}


def find_by_cite(conn, cite):
    rows = conn.execute(
        """SELECT o.id, o.case_name, o.date_filed
              FROM opinions o JOIN citations c ON c.opinion_id = o.id
              WHERE c.citation = ?""",
        (cite,),
    ).fetchall()
    return [dict(r) for r in rows]


def find_by_name_loose(conn, name):
    norm = _normalize_case_name(name)
    parts = norm.split(" v ")
    if len(parts) != 2:
        return []
    p1 = parts[0].split()
    p2 = parts[1].split()
    if not p1 or not p2:
        return []
    rows = conn.execute(
        """SELECT id, case_name, date_filed FROM opinions
              WHERE LOWER(case_name) LIKE ?
                AND LOWER(case_name) LIKE ?
              LIMIT 20""",
        (f"%{p1[0]}%", f"%{p2[0]}%"),
    ).fetchall()
    return [dict(r) for r in rows]


def find_doc_attachment(conn, path):
    return conn.execute(
        """SELECT s.opinion_id, o.case_name, s.is_primary
              FROM opinion_sources s JOIN opinions o ON o.id = s.opinion_id
              WHERE s.source_path = ?""",
        (path,),
    ).fetchall()


def main() -> int:
    conn = get_connection(DEFAULT_DB_PATH)
    for path, cite_matched_oid in AMBIGS:
        p = Path(path)
        text = _doc_to_text(p)
        parsed = _parse_westlaw_doc(text) or {}
        cites = list(parsed.get("all_citations") or [])
        if parsed.get("primary_citation"):
            cites.insert(0, parsed["primary_citation"])
        cites = list(dict.fromkeys(cites))

        print(f"\n{'='*78}")
        print(f"DOC:   {p.name}")
        print(f"PARSED: cites={cites!r}  date={parsed.get('date_filed')!r}")
        print(f"        case_name={parsed.get('case_name')!r}")

        seen = set()
        for c in cites:
            rows = find_by_cite(conn, c)
            for r in rows:
                seen.add(r["id"])
                print(f"  cite {c!r:<24} -> oid {r['id']:>5} {r['case_name']!r} ({r['date_filed']})")
            if not rows:
                print(f"  cite {c!r:<24} -> NONE")

        if parsed.get("case_name"):
            extras = [r for r in find_by_name_loose(conn, parsed["case_name"])
                      if r["id"] not in seen]
            if extras:
                print(f"  Name-fuzzy (not already cite-matched):")
                for r in extras:
                    print(f"    oid {r['id']:>5}  {r['case_name']!r}  ({r['date_filed']})")

        att = find_doc_attachment(conn, str(p))
        if att:
            for a in att:
                print(f"  .doc attached: oid {a['opinion_id']} {a['case_name']!r} primary={a['is_primary']}")
        else:
            print(f"  .doc NOT in opinion_sources")

        # Compute jaccard to every cite-matched candidate
        if seen:
            print(f"  jaccard vs candidates:")
            doc_tok = toks(text)
            for oid in sorted(seen):
                tc = conn.execute(
                    "SELECT case_name, text_content FROM opinions WHERE id = ?",
                    (oid,),
                ).fetchone()
                j = (len(doc_tok & toks(tc["text_content"] or ""))
                     / max(len(doc_tok | toks(tc["text_content"] or "")), 1))
                print(f"    oid {oid:>5}  jac={j:.3f}  {tc['case_name']!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
