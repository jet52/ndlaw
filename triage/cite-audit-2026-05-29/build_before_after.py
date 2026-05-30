#!/usr/bin/env python3
"""Build before/ (current DB text_content) vs after/ (new marker text) for meld.

Files are named <NN>_<cite>_<status>.txt so the review list sorts by the
validation status (review cases surface first) and the cite is visible.
"""
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(__file__))
import para_markers_lib as L
from ndcourts_mcp.db import DEFAULT_DB_PATH

WORK = "/Users/jerod/code/ndcourts-mcp/triage/cite-audit-2026-05-29/para-markers"
for d in ("before", "after"):
    os.makedirs(f"{WORK}/{d}", exist_ok=True)

mapping = json.load(open(f"{WORK}/mapping.json"))
rep = {r["slug"]: r for r in json.load(open(f"{WORK}/validation_report.json"))}
conn = sqlite3.connect(DEFAULT_DB_PATH)

for e in mapping:
    slug, cite = e["slug"], e["cite"]
    r = rep[slug]
    status = "ACCEPT" if r["status"] == "accept" else "REVIEW"
    before = conn.execute(
        "SELECT text_content FROM opinions o JOIN citations c ON c.opinion_id=o.id "
        "WHERE c.citation=? LIMIT 1", (cite,)).fetchone()[0] or ""
    repaired = f"{WORK}/marker_out/{slug}/{slug}.final.md"
    src = repaired if os.path.exists(repaired) else f"{WORK}/marker_out/{slug}/{slug}.md"
    after = L.normalize_marker_md(open(src, encoding="utf-8", errors="replace").read())
    name = f"{e['idx']:02d}_{slug}_{status}.txt"
    open(f"{WORK}/before/{name}", "w").write(before)
    open(f"{WORK}/after/{name}", "w").write(after)

print(f"built {len(mapping)} before/after pairs in {WORK}/before and {WORK}/after")
