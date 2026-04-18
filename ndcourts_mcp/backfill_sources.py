"""Backfill opinion_sources rows for files that exist on disk but were never linked.

Companion to audit_sources.py. The audit identifies opinions where a citation
or docket number implies a source file that exists on disk but is absent from
opinion_sources; this script inserts the missing rows.

With --promote, for 1997+ opinions whose primary source is something other
than ND but whose ndcourts.gov markdown is now linked, the ND row is marked
is_primary=1 and opinions.source_reporter is updated to 'ND'. Per project
policy, ndcourts.gov text is authoritative for 1997+. No changes to
text_content or source_path on the opinions row — those are a separate,
more invasive migration.

Every insert and update is logged to the changelog table for revertibility.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection

REFS_DIR = Path.home() / "refs" / "opin"
DEFAULT_BATCH = "backfill-sources"


def _expected_paths(
    citations: list[tuple[str, str]],
    docket_number: str | None,
    date_filed: str,
) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for reporter, citation in citations:
        if reporter == "ND":
            m = re.match(r"(\d{4})\s+ND\s+(\d+)", citation)
            if m:
                year, num = m.group(1), m.group(2)
                paths["ND"] = REFS_DIR / "ND" / year / f"{year}ND{num}.md"
        elif reporter in ("NW", "NW2d"):
            m = re.match(r"(\d+)\s+N\.?\s*W\.?(?:\s*2d)?\s+(\d+)", citation)
            if m:
                vol, page = m.group(1), m.group(2)
                paths[reporter] = REFS_DIR / reporter / vol / f"{page}.md"
    if docket_number and date_filed and len(date_filed) >= 4:
        year = date_filed[:4]
        paths["archive"] = REFS_DIR / "archive" / year / f"{docket_number}.htm"
    return paths


def _load_opinions(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, date_filed, docket_number, source_reporter, source_path
        FROM opinions
    """)
    opinions = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT opinion_id, reporter, citation FROM citations")
    cits_by_op: dict[int, list[tuple[str, str]]] = defaultdict(list)
    for oid, rep, cit in cur.fetchall():
        cits_by_op[oid].append((rep, cit))

    cur.execute(
        "SELECT opinion_id, source_reporter, source_path, is_primary FROM opinion_sources"
    )
    sources_by_op: dict[int, dict[str, dict]] = defaultdict(dict)
    for oid, rep, path, is_primary in cur.fetchall():
        sources_by_op[oid][rep] = {"path": path, "is_primary": is_primary}

    return opinions, cits_by_op, sources_by_op


def backfill(
    conn: sqlite3.Connection,
    batch: str,
    apply: bool,
    promote: bool,
) -> dict:
    opinions, cits_by_op, sources_by_op = _load_opinions(conn)

    stats = {
        "scanned": len(opinions),
        "inserted": defaultdict(int),
        "promoted": 0,
        "skipped_no_file": defaultdict(int),
    }

    for op in opinions:
        oid = op["id"]
        date_filed = op["date_filed"] or ""
        docket = op["docket_number"]
        primary_reporter = op["source_reporter"]
        existing_sources = sources_by_op.get(oid, {})

        expected = _expected_paths(cits_by_op.get(oid, []), docket, date_filed)

        for reporter, path in expected.items():
            if reporter in existing_sources:
                continue
            if not path.is_file():
                stats["skipped_no_file"][reporter] += 1
                continue

            try:
                text_length = len(path.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                stats["skipped_no_file"][reporter] += 1
                continue

            rel_path = str(path.relative_to(REFS_DIR))
            stats["inserted"][reporter] += 1
            existing_sources[reporter] = {
                "path": rel_path,
                "is_primary": 0,
            }

            if not apply:
                continue

            conn.execute(
                """INSERT INTO opinion_sources
                   (opinion_id, source_reporter, source_path, text_length, is_primary,
                    added_at)
                   VALUES (?, ?, ?, ?, 0,
                    strftime('%Y-%m-%dT%H:%M:%S', 'now'))""",
                (oid, reporter, rel_path, text_length),
            )
            conn.execute(
                "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                "VALUES (?, ?, ?, NULL, ?)",
                (batch, oid, f"source.{reporter}", rel_path),
            )

        if promote and date_filed >= "1997-01-01":
            if "ND" in existing_sources and primary_reporter != "ND":
                stats["promoted"] += 1
                if apply:
                    conn.execute(
                        "UPDATE opinion_sources SET is_primary = 0 WHERE opinion_id = ?",
                        (oid,),
                    )
                    conn.execute(
                        "UPDATE opinion_sources SET is_primary = 1 "
                        "WHERE opinion_id = ? AND source_reporter = 'ND'",
                        (oid,),
                    )
                    conn.execute(
                        "UPDATE opinions SET source_reporter = 'ND' WHERE id = ?",
                        (oid,),
                    )
                    conn.execute(
                        "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                        "VALUES (?, ?, 'source_reporter', ?, 'ND')",
                        (batch, oid, primary_reporter),
                    )

    if apply:
        conn.commit()

    return stats


def print_summary(stats: dict, apply: bool, promote: bool) -> None:
    mode = "APPLIED" if apply else "DRY RUN"
    print(f"=== Backfill sources: {mode} ===")
    print(f"Opinions scanned: {stats['scanned']}")
    print()
    print("Source rows inserted (by reporter):")
    for r in ("ND", "NW", "NW2d", "archive"):
        n = stats["inserted"].get(r, 0)
        print(f"  {r:<8} {n:>6}")
    total_inserts = sum(stats["inserted"].values())
    print(f"  {'TOTAL':<8} {total_inserts:>6}")
    print()
    if promote:
        print(f"Opinions promoted to ND primary: {stats['promoted']}")
        print()
    skipped_total = sum(stats["skipped_no_file"].values())
    if skipped_total:
        print(f"Skipped (expected file not on disk): {skipped_total}")
        for r, n in sorted(stats["skipped_no_file"].items()):
            print(f"  {r:<8} {n:>6}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true",
                    help="Write changes to the DB (default is dry-run)")
    ap.add_argument("--promote", action="store_true",
                    help="For 1997+ opinions with ND source, set ND as primary")
    ap.add_argument("--batch", default=DEFAULT_BATCH,
                    help=f"Changelog batch name (default: {DEFAULT_BATCH})")
    args = ap.parse_args()

    conn = get_connection(args.db)
    try:
        stats = backfill(conn, args.batch, apply=args.apply, promote=args.promote)
        print_summary(stats, apply=args.apply, promote=args.promote)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
