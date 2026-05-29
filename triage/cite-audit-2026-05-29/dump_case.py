#!/usr/bin/env python3
"""Dump everything an auditor needs for one opinion: metadata, full text,
stored forward citations (text_citations), reverse edges (cited_by), and the
opinion's OWN citations (so self-citations are recognizable).

Usage: python dump_case.py <opinion_id>
"""
import sqlite3
import sys

from ndcourts_mcp.db import DEFAULT_DB_PATH

oid = int(sys.argv[1])
c = sqlite3.connect(DEFAULT_DB_PATH)
c.row_factory = sqlite3.Row

o = c.execute("SELECT id, case_name, date_filed, per_curiam, author, court FROM opinions WHERE id=?", (oid,)).fetchone()
own = [r[0] for r in c.execute("SELECT citation FROM citations WHERE opinion_id=? ORDER BY is_primary DESC", (oid,))]

print(f"# OPINION {o['id']}: {o['case_name']} ({o['date_filed']})")
print(f"# author={o['author']!r} per_curiam={o['per_curiam']} court={o['court']}")
print(f"# OWN CITATIONS (a forward cite matching any of these is a SELF-CITATION error): {own}")

print("\n## STORED FORWARD CITATIONS (text_citations) — the 'cases cited' field")
print(f"{'cite_type':12} {'normalized':24} {'juris':6} antecedent_name | raw_text")
for r in c.execute("SELECT normalized, cite_type, jurisdiction, antecedent_name, raw_text "
                   "FROM text_citations WHERE opinion_id=? ORDER BY cite_type, normalized", (oid,)):
    print(f"{r['cite_type']:12} {r['normalized']:24} {str(r['jurisdiction'] or ''):6} {str(r['antecedent_name'])!r:34} | {r['raw_text']!r}")

print("\n## STORED REVERSE EDGES (cited_by) — the 'cited by' field")
rows = c.execute("""SELECT cb.citation, o2.case_name, o2.date_filed, o2.id
                    FROM cited_by cb JOIN opinions o2 ON o2.id=cb.citing_opinion_id
                    WHERE cb.cited_opinion_id=? ORDER BY o2.date_filed DESC""", (oid,)).fetchall()
if not rows:
    print("  (none)")
for r in rows:
    print(f"  cited via {r['citation']!r} by oid {r['id']}: {r['case_name']} ({r['date_filed']})")

txt = c.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0] or ""
print(f"\n## FULL OPINION TEXT ({len(txt)} chars) — extraction ran against THIS text")
print("=" * 80)
print(txt)
