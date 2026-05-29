#!/usr/bin/env python3
"""Reproducibly select 50 opinions decided in the last 3 years for a cite audit.

Seed is fixed so the sample is auditable/repeatable. Window: 2023-05-29..2026-05-29.
"""
import json
import random
import sqlite3

from ndcourts_mcp.db import DEFAULT_DB_PATH

SEED = 20260529
N = 50
WINDOW = ("2023-05-29", "2026-05-29")

c = sqlite3.connect(DEFAULT_DB_PATH)
c.row_factory = sqlite3.Row
ids = [r[0] for r in c.execute(
    "SELECT id FROM opinions WHERE date_filed BETWEEN ? AND ? ORDER BY id",
    WINDOW,
)]
random.seed(SEED)
picked = sorted(random.sample(ids, N))

sample = []
for oid in picked:
    o = c.execute("SELECT id, case_name, date_filed FROM opinions WHERE id=?", (oid,)).fetchone()
    nd = c.execute(
        "SELECT citation FROM citations WHERE opinion_id=? AND citation GLOB '20[0-9][0-9] ND *' "
        "ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone()
    cite = nd[0] if nd else (
        c.execute("SELECT citation FROM citations WHERE opinion_id=? ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone() or ["(none)"])[0]
    sample.append({"id": o["id"], "cite": cite, "name": o["case_name"], "date": o["date_filed"]})

print(json.dumps(sample, indent=2))
