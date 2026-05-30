#!/usr/bin/env python3
"""Write-back for the paragraph-marker re-OCR (§ TODO #4).

For each of the 57 opinions:
  1. overwrite markdown/<year>/<slug>.md with the final marker text
  2. UPDATE opinions.text_content (logged)
  3. store the Westlaw .doc as a second source under NW2d|NW3d/<vol>/<page>-slug.doc
     and register opinion_sources(source_reporter='westlaw'); recover + add the
     N.W. parallel citation where missing (logged)

Snapshot: opinions.db.bak-pre-para-markers-2026-05-30.zst
Usage: write_back.py            # dry run
       write_back.py --apply
"""
import json
import os
import re
import shutil
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(__file__))
import para_markers_lib as L
from ndcourts_mcp.db import DEFAULT_DB_PATH

WORK = "/Users/jerod/code/ndcourts-mcp/triage/cite-audit-2026-05-29/para-markers"
REFS = "/Users/jerod/refs/nd/opin"
BATCH = "para-markers-reocr-2026-05-30"
APPLY = "--apply" in sys.argv

c = sqlite3.connect(DEFAULT_DB_PATH)
c.row_factory = sqlite3.Row


def slugify(name):
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-")[:70] or "opinion"


def log(oid, field, new, authority):
    c.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value, authority) "
              "VALUES (?,?,?,?,?,?)", (BATCH, oid, field, None, new, authority))


mapping = json.load(open(f"{WORK}/mapping.json"))
n_md = n_txt = n_cite = n_src = 0
for e in mapping:
    slug, cite, yr = e["slug"], e["cite"], e["year"]
    o = c.execute("SELECT o.id, o.case_name FROM opinions o JOIN citations ci ON ci.opinion_id=o.id "
                  "WHERE ci.citation=? LIMIT 1", (cite,)).fetchone()
    oid, name = o["id"], o["case_name"]
    final = open(f"{WORK}/marker_out/{slug}/{slug}.final.md", encoding="utf-8").read()
    wl_txt = open(e["wl_txt"], encoding="utf-8", errors="replace").read()

    md_path = f"{REFS}/markdown/{yr}/{slug}.md"
    n_md += 1; n_txt += 1

    # N.W. parallel (DB or recover from Westlaw)
    nwrow = c.execute("SELECT citation FROM citations WHERE opinion_id=? AND "
                      "(citation LIKE '%N.W.2d%' OR citation LIKE '%N.W.3d%') LIMIT 1", (oid,)).fetchone()
    recovered = None
    nwcite = nwrow["citation"] if nwrow else (recovered := L.nw_parallel_from_westlaw(wl_txt))
    m = re.match(r"(\d+)\s+N\.W\.(\d)d\s+(\d+)", nwcite or "")
    if not m:
        print(f"  !! {cite}: cannot parse N.W. parallel {nwcite!r} — skipping westlaw source")
        repdir = dst = None
    else:
        vol, series, page = m.group(1), m.group(2), int(m.group(3))
        repdir = "NW3d" if series == "3" else "NW2d"
        dst = f"{REFS}/{repdir}/{vol}/{page:04d}-{slugify(name)}.doc"

    have_src = c.execute("SELECT 1 FROM opinion_sources WHERE opinion_id=? AND source_reporter='westlaw'",
                         (oid,)).fetchone()
    action = f"  {cite:12} md+text_content"
    if recovered:
        action += f" | +cite {recovered}"; n_cite += 1
    if dst and not have_src:
        action += f" | +westlaw {repdir}/{vol}/{page:04d}-*.doc"; n_src += 1
    print(action)

    if not APPLY:
        continue
    open(md_path, "w").write(final)
    c.execute("UPDATE opinions SET text_content=? WHERE id=?", (final, oid))
    log(oid, "text_content", "re-OCR via marker (paragraph markers recovered)",
        "marker --force_ocr of court PDF; [¶N] validated vs Westlaw (§14 TODO #4)")
    if recovered:
        rep = "NW3d" if "N.W.3d" in recovered else "NW2d"   # canonical reporter code (citation text keeps dots)
        c.execute("INSERT INTO citations (opinion_id, citation, reporter, is_primary) VALUES (?,?,?,0)",
                  (oid, recovered, rep))
        log(oid, "citation", recovered, "N.W. parallel recovered from Westlaw 'All Citations'")
    if dst and not have_src:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(e["wl_doc"], dst)
        c.execute("INSERT INTO opinion_sources (opinion_id, source_reporter, source_path, text_length, is_primary) "
                  "VALUES (?, 'westlaw', ?, ?, 0)", (oid, dst, len(wl_txt)))
        log(oid, "opinion_source", dst, "Westlaw .doc stored as second source (paragraph-marker cross-check)")

if APPLY:
    c.commit()
print(f"\n{'APPLIED' if APPLY else 'DRY RUN'}: markdown {n_md}, text_content {n_txt}, "
      f"recovered cites {n_cite}, westlaw sources {n_src}")
