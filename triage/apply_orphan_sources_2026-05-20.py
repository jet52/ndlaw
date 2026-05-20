"""Register the 7 ORPHAN_SIBLING .docs as non-primary westlaw opinion_sources
rows on their correctly-paired opinion IDs. Same pattern as the
fix-cairncross-source-2026-05-19 micro-fix.

Each row added under batch 'fix-casenames-vol16-79-orphans-2026-05-20'.
Promotion to primary deferred to a future merge_westlaw_text pass.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection  # noqa: E402
from ndcourts_mcp.ingest_westlaw import _doc_to_text  # noqa: E402

BATCH = "fix-casenames-vol16-79-orphans-2026-05-20"
PAIRS = [
    ("/Users/jerod/refs/nd/opin/N.D./20/0372-Fitzmaurice-v-Willis.doc", 680),
    ("/Users/jerod/refs/nd/opin/N.D./20/0412-Stoltze-v-Hurd.doc", 692),
    ("/Users/jerod/refs/nd/opin/N.D./21/0348-Heard-v-Holbrook.doc", 767),
    ("/Users/jerod/refs/nd/opin/N.D./23/0352-Bismarck-Water-Supply-Co-v-City-of-Bismarck.doc", 937),
    ("/Users/jerod/refs/nd/opin/N.D./24/0395-McCarty-v-Kepreta.doc", 1007),
    ("/Users/jerod/refs/nd/opin/N.D./32/0373-Sundahl-v-First-State-Bank-of-Edmunds.doc", 1487),
    ("/Users/jerod/refs/nd/opin/N.D./34/0601-Mercer-County-State-Bank-of-Manhaven-v-Hayes.doc", 1641),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    conn = get_connection(DEFAULT_DB_PATH)
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    added = 0
    for doc_path, oid in PAIRS:
        # Idempotency: skip if already present
        existing = cur.execute(
            "SELECT id FROM opinion_sources WHERE opinion_id = ? "
            "AND source_path = ?",
            (oid, doc_path),
        ).fetchone()
        if existing:
            print(f"  oid {oid}: source already present (id={existing['id']}), skipping")
            continue
        text_length = len(_doc_to_text(Path(doc_path)))
        cluster_id = cur.execute(
            "SELECT cluster_id FROM opinions WHERE id = ?", (oid,)
        ).fetchone()["cluster_id"]
        print(f"  oid {oid:>5}  ADD westlaw is_primary=0 text_length={text_length} "
              f"path={Path(doc_path).name}")
        if args.apply:
            cur.execute(
                """INSERT INTO opinion_sources
                       (opinion_id, source_reporter, source_path, cluster_id,
                        text_length, is_primary, added_at)
                       VALUES (?, 'westlaw', ?, ?, ?, 0, ?)""",
                (oid, doc_path, cluster_id, text_length, now),
            )
            cur.execute(
                """INSERT INTO changelog
                       (batch, opinion_id, field, old_value, new_value)
                       VALUES (?, ?, 'opinion_sources.add', NULL, ?)""",
                (BATCH, oid, f"westlaw is_primary=0 {doc_path}"),
            )
            added += 1
    if args.apply:
        conn.commit()
        print(f"\nApplied {added} opinion_sources row(s) under batch '{BATCH}'.")
    else:
        print(f"\nDry-run: would add {len(PAIRS)} opinion_sources row(s).")
        print(f"  run with --apply to commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
