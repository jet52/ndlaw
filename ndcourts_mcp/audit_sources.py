"""Audit opinion_sources completeness.

For every opinion, determine which source files *should* be available on
disk based on its citations and docket number, then check whether each
one is recorded in opinion_sources. Reports the gap by decade and by
source_reporter.

Read-only. No writes to the DB.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection

REFS_DIR = Path.home() / "refs" / "opin"


def _decade(date_filed: str) -> str:
    if not date_filed or len(date_filed) < 4:
        return "unknown"
    return date_filed[:3] + "0s"


def _expected_paths(
    citations: list[tuple[str, str]],
    docket_number: str | None,
    date_filed: str,
) -> dict[str, Path]:
    """Return {source_reporter: expected_path} for every citation and docket that
    maps to a deterministic filesystem location under REFS_DIR.
    """
    paths: dict[str, Path] = {}

    for reporter, citation in citations:
        if reporter == "ND":
            # "2020 ND 8" -> ND/2020/2020ND8.md
            m = re.match(r"(\d{4})\s+ND\s+(\d+)", citation)
            if m:
                year, num = m.group(1), m.group(2)
                paths["ND"] = REFS_DIR / "ND" / year / f"{year}ND{num}.md"
        elif reporter in ("NW", "NW2d"):
            # "937 N.W.2d 279" -> NW2d/937/279.md
            m = re.match(r"(\d+)\s+N\.?\s*W\.?(?:\s*2d)?\s+(\d+)", citation)
            if m:
                vol, page = m.group(1), m.group(2)
                paths[reporter] = REFS_DIR / reporter / vol / f"{page}.md"

    if docket_number and date_filed and len(date_filed) >= 4:
        year = date_filed[:4]
        archive_path = REFS_DIR / "archive" / year / f"{docket_number}.htm"
        paths["archive"] = archive_path

    return paths


def audit(conn: sqlite3.Connection) -> dict:
    cur = conn.cursor()
    cur.execute("""
        SELECT id, date_filed, docket_number, source_reporter
        FROM opinions
    """)
    opinions = cur.fetchall()

    cur.execute("SELECT opinion_id, reporter, citation FROM citations")
    cits_by_op: dict[int, list[tuple[str, str]]] = defaultdict(list)
    for oid, rep, cit in cur.fetchall():
        cits_by_op[oid].append((rep, cit))

    cur.execute("SELECT opinion_id, source_reporter FROM opinion_sources")
    sources_by_op: dict[int, set[str]] = defaultdict(set)
    for oid, rep in cur.fetchall():
        sources_by_op[oid].add(rep)

    report: dict[str, dict] = defaultdict(lambda: {
        "total": 0,
        "missing_by_reporter": defaultdict(int),
        "file_exists_but_unlinked": defaultdict(int),
        "multi_source_already": 0,
    })
    example_gaps: dict[str, list] = defaultdict(list)

    for op_row in opinions:
        oid = op_row["id"]
        date_filed = op_row["date_filed"] or ""
        docket = op_row["docket_number"]
        primary = op_row["source_reporter"]
        dec = _decade(date_filed)

        expected = _expected_paths(cits_by_op.get(oid, []), docket, date_filed)
        linked = sources_by_op.get(oid, set())

        report[dec]["total"] += 1
        if len(linked) >= 2:
            report[dec]["multi_source_already"] += 1

        for reporter, path in expected.items():
            if reporter in linked:
                continue
            report[dec]["missing_by_reporter"][reporter] += 1
            if path.is_file():
                report[dec]["file_exists_but_unlinked"][reporter] += 1
                if len(example_gaps[reporter]) < 5:
                    example_gaps[reporter].append({
                        "opinion_id": oid,
                        "date_filed": date_filed,
                        "primary": primary,
                        "missing_source": reporter,
                        "expected_path": str(path.relative_to(REFS_DIR)),
                    })

    return {"report": report, "examples": example_gaps}


def print_report(result: dict) -> None:
    report = result["report"]
    examples = result["examples"]

    decades = sorted(report.keys())
    reporters = ["ND", "NW", "NW2d", "archive"]

    print(f"{'Decade':<10} {'Total':>6} {'Multi':>6} " + " ".join(f"{r:>14}" for r in reporters))
    print(f"{'':<10} {'':>6} {'':>6} " + " ".join(f"{'miss/unlinked':>14}" for _ in reporters))
    print("-" * (10 + 7 + 7 + 15 * len(reporters)))

    grand = {
        "total": 0,
        "multi": 0,
        "missing": {r: 0 for r in reporters},
        "unlinked": {r: 0 for r in reporters},
    }

    for dec in decades:
        row = report[dec]
        cells = [f"{dec:<10}", f"{row['total']:>6}", f"{row['multi_source_already']:>6}"]
        for r in reporters:
            miss = row["missing_by_reporter"].get(r, 0)
            unlinked = row["file_exists_but_unlinked"].get(r, 0)
            cells.append(f"{miss:>6}/{unlinked:>6}")
            grand["missing"][r] += miss
            grand["unlinked"][r] += unlinked
        grand["total"] += row["total"]
        grand["multi"] += row["multi_source_already"]
        print(" ".join(cells))

    print("-" * (10 + 7 + 7 + 15 * len(reporters)))
    cells = [f"{'TOTAL':<10}", f"{grand['total']:>6}", f"{grand['multi']:>6}"]
    for r in reporters:
        cells.append(f"{grand['missing'][r]:>6}/{grand['unlinked'][r]:>6}")
    print(" ".join(cells))

    print()
    print("Legend: 'miss' = citation or docket exists but source_reporter not in opinion_sources;")
    print("        'unlinked' = subset where the file is actually on disk (ready to backfill).")
    print()

    if any(examples.get(r) for r in reporters):
        print("Example unlinked files (first 5 per reporter):")
        for r in reporters:
            if not examples.get(r):
                continue
            print(f"\n  {r}:")
            for e in examples[r]:
                print(f"    opinion {e['opinion_id']} ({e['date_filed']}, primary={e['primary']}) → {e['expected_path']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = ap.parse_args()

    conn = get_connection(args.db)
    try:
        result = audit(conn)
        print_report(result)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
