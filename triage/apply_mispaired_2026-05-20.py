"""Apply the SAME verdicts from casenames-mispaired-adjudication-2026-05-20.tsv.

Only rows with verdict == 'SAME' and suggested_action == 'update_case_name'
are applied. Every change is recorded in the changelog table under batch
'fix-casenames-vol16-79-bound-2026-05-20' and is revertible.

Dry-run by default. Use --apply to write.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection  # noqa: E402

INPUT_TSV = REPO / "triage" / "casenames-mispaired-adjudication-2026-05-20.tsv"
BATCH = "fix-casenames-vol16-79-bound-2026-05-20"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--apply", action="store_true",
                        help="Actually write changes; default is dry-run.")
    parser.add_argument("--skip-oids", default="",
                        help="Comma-separated opinion_ids to exclude.")
    args = parser.parse_args()

    conn = get_connection(args.db)
    skip = {int(x) for x in args.skip_oids.split(",") if x.strip()}
    with INPUT_TSV.open() as fh:
        rows = [r for r in csv.DictReader(fh, delimiter="\t")
                if r["verdict"] == "SAME"
                and r["suggested_action"] == "update_case_name"
                and r["suggested_new_value"]
                and int(r["opinion_id"]) not in skip]
    print(f"{len(rows)} SAME rows to apply"
          f"{' (DRY-RUN)' if not args.apply else ''}")
    cur = conn.cursor()
    changed = skipped = 0
    for r in rows:
        oid = int(r["opinion_id"])
        new = r["suggested_new_value"]
        existing = cur.execute(
            "SELECT case_name FROM opinions WHERE id = ?", (oid,)
        ).fetchone()
        if not existing:
            print(f"  SKIP oid {oid}: not in DB")
            skipped += 1
            continue
        old = existing["case_name"]
        if old == new:
            skipped += 1
            continue
        print(f"  oid {oid:>6}  {old!r}  ->  {new!r}")
        if args.apply:
            cur.execute("UPDATE opinions SET case_name = ? WHERE id = ?",
                        (new, oid))
            cur.execute(
                "INSERT INTO changelog (batch, opinion_id, field, old_value, "
                "new_value) VALUES (?, ?, 'case_name', ?, ?)",
                (BATCH, oid, old, new),
            )
            changed += 1
    if args.apply:
        conn.commit()
        print(f"\nApplied {changed} change(s) under batch '{BATCH}'.")
        print(f"  revert: python -m ndcourts_mcp.cleanup revert {BATCH}")
    else:
        print(f"\nDry-run: would apply {len(rows) - skipped} change(s).")
        print(f"  run with --apply to commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
