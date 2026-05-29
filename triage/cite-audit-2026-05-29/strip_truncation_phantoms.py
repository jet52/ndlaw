#!/usr/bin/env python3
"""Strip stale reporter-truncation phantoms from text_citations (§14c).

An older jetcite tokenized "419 F.2d 1197" / "892 So. 2d 1075" / "43 F.4th 100"
as reporter "F."/"So." + the SERIES digit as the page, producing phantom rows
like "419 F. 2" (page lost). jetcite 2.1.0 no longer does this (verified), but
the old phantoms persist because cite_extract uses INSERT OR IGNORE and never
deletes superseded rows.

Scope (conservative, sibling-gated): delete a candidate "VOL BASE. D"
(cite_type='case', D in {2,3,4}) ONLY IF the same opinion also has the correct
full cite "VOL BASE.Dd|th ..." (either spacing). That guarantees it's a
truncation artifact, not a genuine first-series cite. Rows without such a
sibling are LEFT untouched (they include real S. Ct./1st-series cites and
separate garbage-volume defects).

These are out-of-corpus cites (no cited_by edges), so this is forward-display
only. Each deletion is logged to changelog. Pre-batch snapshot:
opinions.db.bak-pre-strip-truncation-phantoms-2026-05-29.zst.

Usage:
  python strip_truncation_phantoms.py            # dry run
  python strip_truncation_phantoms.py --apply
"""
import re
import sqlite3
import sys

from ndcourts_mcp.db import DEFAULT_DB_PATH

BATCH = "strip-truncation-phantoms-2026-05-29"
AUTHORITY = "reporter-series truncation artifact from pre-2.1.0 jetcite (F.2d->'F. 2'); full cite present in same opinion (§14c)"
APPLY = "--apply" in sys.argv

c = sqlite3.connect(DEFAULT_DB_PATH)
c.row_factory = sqlite3.Row

cands = c.execute(
    r"""SELECT id, opinion_id, normalized FROM text_citations
        WHERE cite_type='case' AND normalized GLOB '* [234]'
          AND normalized GLOB '*[A-Za-z]. [234]'"""
).fetchall()

to_delete, held = [], 0
for r in cands:
    m = re.match(r"^(\d+)\s+(.+?)\.\s+([234])$", r["normalized"])
    if not m:
        held += 1
        continue
    vol, base, dig = m.groups()
    sib = c.execute(
        """SELECT COUNT(*) FROM text_citations
           WHERE opinion_id=? AND cite_type='case' AND (
             normalized GLOB ? OR normalized GLOB ? OR normalized GLOB ? OR normalized GLOB ?)""",
        (r["opinion_id"], f"{vol} {base}.{dig}d *", f"{vol} {base}. {dig}d *",
         f"{vol} {base}.{dig}th *", f"{vol} {base}. {dig}th *"),
    ).fetchone()[0]
    if sib:
        to_delete.append(r)
    else:
        held += 1

print(f"candidates: {len(cands)}")
print(f"sibling-confirmed phantoms to delete: {len(to_delete)}")
print(f"held (no full-cite sibling — genuine cites / other defects): {held}")

if not APPLY:
    print("\nDRY RUN — re-run with --apply.")
    sys.exit(0)

for r in to_delete:
    c.execute(
        """INSERT INTO changelog (batch, opinion_id, field, old_value, new_value, authority)
           VALUES (?, ?, 'text_citations.reporter_truncation', ?, NULL, ?)""",
        (BATCH, r["opinion_id"], r["normalized"], AUTHORITY),
    )
    c.execute("DELETE FROM text_citations WHERE id = ?", (r["id"],))

c.commit()
print(f"\nDeleted {len(to_delete)}; {len(to_delete)} changelog rows under {BATCH}.")
