"""Invariants dashboard — read-only health check for the opinions DB.

Runs a battery of invariant checks and reports any violations. Designed
to chain after the weekly ingest pipeline so regressions surface before
they accumulate.

Two kinds of checks:
  must-be-zero:    pure invariants — any violation is a regression.
  baseline-tracked: aggregate observations with a documented current
                    count; an increase signals a regression even though
                    the steady-state count is non-zero.

Exit code is 0 when every check is at or below its expected count, 1
when any check exceeds its expected count.

Usage:
    python -m ndcourts_mcp.invariants [--db PATH] [--refs PATH] [--json]
                                       [--verbose] [--update-baseline]
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .db import DEFAULT_DB_PATH

DEFAULT_REFS_DIR = Path.home() / "refs" / "nd" / "opin"

# Baselines for checks that have known non-zero counts in the current
# corpus. An increase past the baseline is a regression. Reduce these
# numbers as the underlying issues are resolved (or run with
# --update-baseline to refresh).
BASELINES: dict[str, int] = {
    "neutral_cite_uniqueness":     258,      # 258 known dup pairs (§6 queue)
    "nd_modern_paragraph_markers": 85,       # 85 short orders w/o markers (§4)
}

SAMPLE_LIMIT = 5


@dataclass
class CheckResult:
    name: str
    description: str
    count: int
    expected: int
    samples: list = field(default_factory=list)

    @property
    def delta(self) -> int:
        return self.count - self.expected

    @property
    def status(self) -> str:
        if self.count == 0 and self.expected == 0:
            return "ok"
        if self.delta > 0:
            return "fail"
        return "known"


_CHECKS: list[tuple[str, str, callable]] = []


def _check(name: str, description: str):
    def deco(fn):
        _CHECKS.append((name, description, fn))
        return fn
    return deco


# ---- referential integrity --------------------------------------------------

@_check("orphan_opinion_sources",
        "opinion_sources rows reference a real opinion")
def _orphan_opinion_sources(conn, refs):
    return conn.execute(
        "SELECT t.id, t.opinion_id, t.source_reporter, t.source_path "
        "FROM opinion_sources t LEFT JOIN opinions o ON o.id = t.opinion_id "
        "WHERE o.id IS NULL"
    ).fetchall()


@_check("orphan_citations",
        "citations rows reference a real opinion")
def _orphan_citations(conn, refs):
    return conn.execute(
        "SELECT t.id, t.opinion_id, t.citation "
        "FROM citations t LEFT JOIN opinions o ON o.id = t.opinion_id "
        "WHERE o.id IS NULL"
    ).fetchall()


@_check("orphan_text_citations",
        "text_citations rows reference a real opinion")
def _orphan_text_citations(conn, refs):
    return conn.execute(
        "SELECT t.id, t.opinion_id, t.normalized "
        "FROM text_citations t LEFT JOIN opinions o ON o.id = t.opinion_id "
        "WHERE o.id IS NULL"
    ).fetchall()


@_check("orphan_cited_by",
        "cited_by rows reference real opinions on both sides")
def _orphan_cited_by(conn, refs):
    return conn.execute(
        "SELECT t.id, t.cited_opinion_id, t.citing_opinion_id, t.citation "
        "FROM cited_by t "
        "LEFT JOIN opinions oc ON oc.id = t.cited_opinion_id "
        "LEFT JOIN opinions ov ON ov.id = t.citing_opinion_id "
        "WHERE oc.id IS NULL OR ov.id IS NULL"
    ).fetchall()


# ---- source consistency -----------------------------------------------------

@_check("primary_source_unique",
        "every opinion has exactly one primary source row")
def _primary_source_unique(conn, refs):
    return conn.execute("""
        SELECT id, case_name, n FROM (
            SELECT o.id, o.case_name,
                   (SELECT COUNT(*) FROM opinion_sources os
                    WHERE os.opinion_id = o.id AND os.is_primary = 1) AS n
            FROM opinions o
        ) WHERE n != 1
    """).fetchall()


@_check("source_reporter_matches_primary",
        "opinions.source_reporter matches the primary opinion_sources row")
def _source_reporter_match(conn, refs):
    return conn.execute("""
        SELECT o.id, o.case_name, o.source_reporter AS o_rep,
               os.source_reporter AS os_rep
        FROM opinions o
        LEFT JOIN opinion_sources os
               ON os.opinion_id = o.id AND os.is_primary = 1
        WHERE o.source_reporter != os.source_reporter
    """).fetchall()


@_check("source_path_matches_primary",
        "opinions.source_path matches the primary opinion_sources row")
def _source_path_match(conn, refs):
    return conn.execute("""
        SELECT o.id, o.case_name, o.source_path AS o_path,
               os.source_path AS os_path
        FROM opinions o
        LEFT JOIN opinion_sources os
               ON os.opinion_id = o.id AND os.is_primary = 1
        WHERE o.source_path != os.source_path
    """).fetchall()


@_check("source_files_on_disk",
        "every opinions.source_path resolves to an extant file")
def _source_files_on_disk(conn, refs):
    rows = conn.execute(
        "SELECT id, case_name, source_path FROM opinions"
    ).fetchall()
    missing = []
    for r in rows:
        sp = r["source_path"]
        full = Path(sp) if os.path.isabs(sp) else refs / sp
        if not full.exists():
            missing.append(r)
    return missing


@_check("opinion_source_files_on_disk",
        "every opinion_sources.source_path resolves to an extant file")
def _opinion_source_files(conn, refs):
    rows = conn.execute(
        "SELECT id, opinion_id, source_reporter, source_path "
        "FROM opinion_sources"
    ).fetchall()
    missing = []
    for r in rows:
        sp = r["source_path"]
        full = Path(sp) if os.path.isabs(sp) else refs / sp
        if not full.exists():
            missing.append(r)
    return missing


# ---- citation invariants ----------------------------------------------------

@_check("neutral_cite_uniqueness",
        "each `<year> ND <n>` neutral citation belongs to one opinion "
        "(currently 258 known duplicate pairs — §6 dup-queue overlap)")
def _neutral_cite_uniqueness(conn, refs):
    return conn.execute("""
        SELECT citation, COUNT(*) AS n
        FROM citations
        WHERE citation GLOB '[0-9][0-9][0-9][0-9] ND [0-9]*'
        GROUP BY citation HAVING COUNT(*) > 1
        ORDER BY n DESC, citation
    """).fetchall()


@_check("citations_non_empty",
        "no empty or whitespace-only citation strings")
def _citations_non_empty(conn, refs):
    return conn.execute(
        "SELECT id, opinion_id, citation FROM citations "
        "WHERE citation IS NULL OR trim(citation) = ''"
    ).fetchall()


@_check("citation_row_unique_per_opinion",
        "no opinion carries the same citation in more than one row "
        "(distinct opinions MAY share a cite — key is (opinion_id, "
        "citation); guards the merge_pair re-point dedup)")
def _citation_row_unique_per_opinion(conn, refs):
    return conn.execute(
        "SELECT opinion_id, citation, COUNT(*) AS n FROM citations "
        "GROUP BY opinion_id, citation HAVING COUNT(*) > 1 ORDER BY n DESC"
    ).fetchall()


@_check("source_row_unique_per_opinion",
        "no opinion carries the same source_path in more than one "
        "opinion_sources row (key is (opinion_id, source_path))")
def _source_row_unique_per_opinion(conn, refs):
    return conn.execute(
        "SELECT opinion_id, source_path, COUNT(*) AS n FROM opinion_sources "
        "GROUP BY opinion_id, source_path HAVING COUNT(*) > 1 ORDER BY n DESC"
    ).fetchall()


# ---- date sanity ------------------------------------------------------------

@_check("date_filed_not_future",
        "no opinion claims a filing date later than today")
def _date_not_future(conn, refs):
    return conn.execute(
        "SELECT id, case_name, date_filed FROM opinions "
        "WHERE date_filed > date('now')"
    ).fetchall()


@_check("date_filed_after_statehood",
        "no opinion predates ND statehood (1889-11-02)")
def _date_after_statehood(conn, refs):
    return conn.execute(
        "SELECT id, case_name, date_filed FROM opinions "
        "WHERE date_filed < '1889-01-01'"
    ).fetchall()


# ---- content invariants -----------------------------------------------------

@_check("text_content_non_empty",
        "every opinion has non-empty text_content")
def _text_non_empty(conn, refs):
    return conn.execute(
        "SELECT id, case_name, source_reporter, source_path FROM opinions "
        "WHERE text_content IS NULL OR text_content = ''"
    ).fetchall()


@_check("nd_modern_paragraph_markers",
        "ND-primary opinions filed >= 1997-01-01 carry [¶N] markers "
        "(currently 85 known short orders — §4)")
def _nd_modern_para(conn, refs):
    return conn.execute(
        "SELECT id, case_name, date_filed, source_path FROM opinions "
        "WHERE source_reporter = 'ND' "
        "  AND date_filed >= '1997-01-01' "
        "  AND text_content NOT LIKE '%[¶%'"
    ).fetchall()


# -----------------------------------------------------------------------------


def run_checks(db_path: Path, refs_dir: Path) -> list[CheckResult]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    results: list[CheckResult] = []
    for name, description, fn in _CHECKS:
        rows = fn(conn, refs_dir)
        results.append(CheckResult(
            name=name,
            description=description,
            count=len(rows),
            expected=BASELINES.get(name, 0),
            samples=[dict(r) for r in rows[:SAMPLE_LIMIT]],
        ))
    conn.close()
    return results


def render_text(results: list[CheckResult], verbose: bool) -> tuple[str, int]:
    lines = []
    fails = sum(1 for r in results if r.status == "fail")
    known = sum(1 for r in results if r.status == "known")
    ok = sum(1 for r in results if r.status == "ok")

    lines.append(f"Invariants: {ok} ok, {known} at known baseline, {fails} regressed")
    lines.append("")
    icon = {"ok": "  OK ", "known": " known", "fail": " FAIL"}
    for r in results:
        if r.expected:
            tail = f"  ({r.count} / {r.expected} expected, Δ={r.delta:+d})"
        else:
            tail = f"  ({r.count})" if r.count else ""
        lines.append(f"  [{icon[r.status]}] {r.name}{tail}")
        lines.append(f"          {r.description}")
        if verbose and r.samples:
            for s in r.samples:
                pretty = ", ".join(f"{k}={v!r}" for k, v in s.items() if v is not None)
                lines.append(f"            · {pretty}")
            if r.count > len(r.samples):
                lines.append(f"            … and {r.count - len(r.samples)} more")
        lines.append("")
    return "\n".join(lines), 1 if fails else 0


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("--refs", type=Path, default=DEFAULT_REFS_DIR)
    p.add_argument("--json", action="store_true",
                   help="emit a JSON report instead of human text")
    p.add_argument("--verbose", action="store_true",
                   help="include sample offending rows for each check")
    p.add_argument("--update-baseline", action="store_true",
                   help="print a BASELINES dict reflecting current counts; "
                        "intended to be pasted into invariants.py after a "
                        "deliberate corpus-state shift")
    args = p.parse_args()

    results = run_checks(args.db, args.refs)

    if args.update_baseline:
        print("BASELINES = {")
        for r in results:
            if r.count:
                print(f"    {r.name!r:<40}: {r.count},")
        print("}")
        return 0

    if args.json:
        payload = {
            "results": [
                {
                    "name": r.name,
                    "description": r.description,
                    "count": r.count,
                    "expected": r.expected,
                    "delta": r.delta,
                    "status": r.status,
                    "samples": r.samples,
                }
                for r in results
            ],
            "regressions": sum(1 for r in results if r.status == "fail"),
        }
        print(json.dumps(payload, indent=2, default=str))
        return 1 if any(r.status == "fail" for r in results) else 0

    text, exit_code = render_text(results, args.verbose)
    print(text)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
