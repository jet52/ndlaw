#!/usr/bin/env python3
"""Backfill jurisdiction='nd' for in-corpus case cites (§14f).

jetcite tags the N.W./N.W.2d/N.W.3d regional reporter as jurisdiction='us'
(it's regional — ND/MN/SD/NE/IA/WI/MI). But a specific volume+page is one unique
case, so any N.W. cite that resolves to an opinion in THIS (ND-only) corpus is
definitionally a North Dakota case and should be 'nd'.

Deterministic, rule-based reclassification: set jurisdiction='nd' for every
cite_type='case' text_citation whose normalized cite matches a corpus opinion's
citation and is not already 'nd'. ~107k rows (N.W.2d 98,656 / N.W. 8,301 /
N.W.3d 4). Out-of-corpus cites (federal, other-state, ND cases we don't hold)
keep their jetcite jurisdiction.

Reversibility: pre-batch snapshot
opinions.db.bak-pre-jurisdiction-backfill-2026-05-29.zst (the revert path). Not
logged per-row to the changelog: at this scale, and because the changelog keys
on opinion_id (an opinion has many cites) it can't precisely revert an
individual text_citation's jurisdiction anyway — the snapshot + the
CHANGELOG-data.md narrative (rule + count) are the audit trail. The rule is also
baked into cite_extract so re-extraction stays correct.

Usage:
  python backfill_jurisdiction.py            # dry run (count)
  python backfill_jurisdiction.py --apply
"""
import sqlite3
import sys

from ndcourts_mcp.db import DEFAULT_DB_PATH

APPLY = "--apply" in sys.argv
c = sqlite3.connect(DEFAULT_DB_PATH)

WHERE = ("""cite_type='case' AND jurisdiction IS NOT 'nd'
            AND EXISTS (SELECT 1 FROM citations ci WHERE ci.citation = text_citations.normalized)""")

n = c.execute(f"SELECT COUNT(*) FROM text_citations WHERE {WHERE}").fetchone()[0]
print(f"case-cites resolving to corpus but not tagged 'nd': {n}")

if not APPLY:
    print("DRY RUN — re-run with --apply.")
    sys.exit(0)

c.execute(f"UPDATE text_citations SET jurisdiction='nd' WHERE {WHERE}")
c.commit()
remaining = c.execute(f"SELECT COUNT(*) FROM text_citations WHERE {WHERE}").fetchone()[0]
print(f"Updated {n} rows to jurisdiction='nd'. Remaining mis-tagged (should be 0): {remaining}")
