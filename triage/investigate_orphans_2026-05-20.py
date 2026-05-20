"""Investigate the 7 ORPHAN_SIBLING entries from the vol-16-79 mispaired
adjudication: are these real corpus gaps, or are the opinions in the DB
under a different cite / case_name pairing?

For each .doc:
  1. Parse metadata (citations, case_name, date, judges).
  2. Look up each citation in the DB.
  3. Look up the case_name in the DB (fuzzy).
  4. Report verdict.
"""
from __future__ import annotations

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

ORPHANS = [
    ("/Users/jerod/refs/nd/opin/N.D./20/0372-Fitzmaurice-v-Willis.doc", 672),
    ("/Users/jerod/refs/nd/opin/N.D./20/0412-Stoltze-v-Hurd.doc", 683),
    ("/Users/jerod/refs/nd/opin/N.D./21/0348-Heard-v-Holbrook.doc", 765),
    ("/Users/jerod/refs/nd/opin/N.D./23/0352-Bismarck-Water-Supply-Co-v-City-of-Bismarck.doc", 929),
    ("/Users/jerod/refs/nd/opin/N.D./24/0395-McCarty-v-Kepreta.doc", 978),
    ("/Users/jerod/refs/nd/opin/N.D./32/0373-Sundahl-v-First-State-Bank-of-Edmunds.doc", 1486),
    ("/Users/jerod/refs/nd/opin/N.D./34/0601-Mercer-County-State-Bank-of-Manhaven-v-Hayes.doc", 1640),
]


def find_by_cite(conn, cite: str) -> list[dict]:
    rows = conn.execute(
        """SELECT o.id, o.case_name, o.date_filed FROM opinions o
              JOIN citations c ON c.opinion_id = o.id
              WHERE c.citation = ?""",
        (cite,),
    ).fetchall()
    return [dict(r) for r in rows]


def find_by_name(conn, name: str, date_filed: str | None) -> list[dict]:
    """Find DB opinions whose case_name fuzzily matches the parsed .doc name."""
    norm_target = _normalize_case_name(name)
    parts = norm_target.split(" v ")
    if len(parts) != 2:
        return []
    plaintiff_first = parts[0].split()[0]
    defendant_first = parts[1].split()[0]
    if not plaintiff_first or not defendant_first:
        return []
    rows = conn.execute(
        """SELECT id, case_name, date_filed FROM opinions
              WHERE LOWER(case_name) LIKE ?
                AND LOWER(case_name) LIKE ?
              LIMIT 20""",
        (f"%{plaintiff_first}%", f"%{defendant_first}%"),
    ).fetchall()
    return [dict(r) for r in rows]


def find_doc_attached_anywhere(conn, doc_path: str) -> list[dict]:
    rows = conn.execute(
        """SELECT s.opinion_id, o.case_name, s.source_reporter, s.is_primary
              FROM opinion_sources s JOIN opinions o ON o.id = s.opinion_id
              WHERE s.source_path = ? OR s.source_path = ?""",
        (doc_path, doc_path.replace("/Users/jerod/refs/", "")),
    ).fetchall()
    return [dict(r) for r in rows]


def main() -> int:
    conn = get_connection(DEFAULT_DB_PATH)
    for doc_path_s, cite_matched_oid in ORPHANS:
        doc_path = Path(doc_path_s)
        text = _doc_to_text(doc_path)
        parsed = _parse_westlaw_doc(text) or {}
        cites = list(parsed.get("all_citations") or [])
        if parsed.get("primary_citation"):
            cites.insert(0, parsed["primary_citation"])
        cites = list(dict.fromkeys(cites))

        print(f"\n{'='*78}")
        print(f"DOC:   {doc_path.name}")
        print(f"PARSED: cites={cites!r}")
        print(f"        case_name={parsed.get('case_name')!r}")
        print(f"        date={parsed.get('date_filed')!r}  per_curiam={parsed.get('per_curiam')!r}")

        # 1) check every citation
        print(f"  DB lookup by citation:")
        seen_oids = set()
        for c in cites:
            rows = find_by_cite(conn, c)
            for r in rows:
                seen_oids.add(r["id"])
                print(f"    cite {c!r} -> oid {r['id']} {r['case_name']!r} ({r['date_filed']})")
            if not rows:
                print(f"    cite {c!r} -> NONE")

        # 2) fuzzy by name
        if parsed.get("case_name"):
            print(f"  DB fuzzy by case_name {parsed['case_name']!r}:")
            for r in find_by_name(conn, parsed["case_name"], parsed.get("date_filed")):
                if r["id"] in seen_oids:
                    continue
                print(f"    oid {r['id']} {r['case_name']!r} ({r['date_filed']})")

        # 3) is the .doc registered anywhere?
        attached = find_doc_attached_anywhere(conn, str(doc_path))
        if attached:
            print(f"  .doc opinion_sources rows:")
            for a in attached:
                print(f"    oid {a['opinion_id']} ({a['source_reporter']}, primary={a['is_primary']}) {a['case_name']!r}")
        else:
            print(f"  .doc NOT attached to any opinion_sources row")

        # 4) cite-matched OID for context
        cm = conn.execute(
            "SELECT case_name, date_filed FROM opinions WHERE id = ?",
            (cite_matched_oid,),
        ).fetchone()
        print(f"  (cite-matched in mispaired TSV: oid {cite_matched_oid} = "
              f"{cm['case_name']!r} {cm['date_filed']})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
