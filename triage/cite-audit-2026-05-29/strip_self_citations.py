#!/usr/bin/env python3
"""Strip self-citations from text_citations (§14b).

A case cannot be an authority it cites. The extractor scans the whole
text_content including the caption/header block, which prints the opinion's own
neutral (and often N.W.) cite, so every opinion ended up "citing" itself
(31,331 rows across ~all opinions). cited_by already excludes these (0 self-
edges); this cleans the forward table to match.

Scope: delete only UNAMBIGUOUS self-cites — rows whose normalized cite is unique
to the opinion (definitionally the caption). Rows whose cite is shared with
another opinion (shared-page twins, ~619) are LEFT for the shared-page
disambiguation pass, since the text might reference the companion.

Each deletion is logged to the changelog table. A pre-batch snapshot exists at
opinions.db.bak-pre-strip-self-cites-2026-05-29.zst.

Usage:
  python strip_self_citations.py            # dry run (counts only)
  python strip_self_citations.py --apply    # delete + log
"""
import sqlite3
import sys

from ndcourts_mcp.db import DEFAULT_DB_PATH

BATCH = "strip-self-citations-2026-05-29"
AUTHORITY = "self-citation: opinion's own caption cite is not an authority it cites (§14b)"
APPLY = "--apply" in sys.argv

c = sqlite3.connect(DEFAULT_DB_PATH)
c.row_factory = sqlite3.Row

# Unambiguous self-cite rows: text_citation matches one of the opinion's own
# citations AND that citation maps to no other opinion.
rows = c.execute(
    """SELECT tc.id, tc.opinion_id, tc.normalized
       FROM text_citations tc
       JOIN citations ci ON ci.opinion_id = tc.opinion_id AND ci.citation = tc.normalized
       WHERE tc.normalized NOT IN (
           SELECT citation FROM citations GROUP BY citation HAVING COUNT(DISTINCT opinion_id) > 1
       )"""
).fetchall()

shared = c.execute(
    """SELECT COUNT(*) FROM text_citations tc
       JOIN citations ci ON ci.opinion_id = tc.opinion_id AND ci.citation = tc.normalized
       WHERE tc.normalized IN (
           SELECT citation FROM citations GROUP BY citation HAVING COUNT(DISTINCT opinion_id) > 1
       )"""
).fetchone()[0]

print(f"unambiguous self-cite rows to delete: {len(rows)}")
print(f"shared-cite self-cites LEFT for shared-page review: {shared}")

if not APPLY:
    print("\nDRY RUN — re-run with --apply to delete + log.")
    sys.exit(0)

for r in rows:
    c.execute(
        """INSERT INTO changelog (batch, opinion_id, field, old_value, new_value, authority)
           VALUES (?, ?, 'text_citations.self_cite', ?, NULL, ?)""",
        (BATCH, r["opinion_id"], r["normalized"], AUTHORITY),
    )
    c.execute("DELETE FROM text_citations WHERE id = ?", (r["id"],))

c.commit()
remaining = c.execute(
    """SELECT COUNT(*) FROM text_citations tc
       JOIN citations ci ON ci.opinion_id = tc.opinion_id AND ci.citation = tc.normalized"""
).fetchone()[0]
print(f"\nDeleted {len(rows)} rows; {len(rows)} changelog entries under {BATCH}.")
print(f"self-cite rows remaining (should equal shared count {shared}): {remaining}")
