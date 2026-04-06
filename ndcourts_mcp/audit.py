"""Audit the opinion database for missing opinions and data anomalies.

Checks:
1. ND neutral citation sequence gaps (should be sequential per year)
2. Phantom citations (cited in opinion text but not in our DB)
3. Multiple citations per reporter on one opinion (expect at most one)
4. NW/NW2d volume coverage gaps

Results are printed and saved to MISSING_OPINIONS.md in the project dir.

Usage:
    python -m ndcourts_mcp.audit [--db PATH] [--save]
"""

import argparse
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection

PROJECT_DIR = Path(__file__).parent.parent
MISSING_FILE = PROJECT_DIR / "MISSING_OPINIONS.md"


def _nd_citation_gaps(conn: sqlite3.Connection) -> list[dict]:
    """Find gaps in the ND neutral citation sequence for each year."""
    rows = conn.execute(
        "SELECT citation FROM citations WHERE reporter = 'ND'"
    ).fetchall()

    by_year: dict[int, list[int]] = defaultdict(list)
    for r in rows:
        m = re.match(r"(\d{4}) ND (\d+)", r["citation"])
        if m:
            by_year[int(m.group(1))].append(int(m.group(2)))

    gaps = []
    for year in sorted(by_year):
        nums = sorted(set(by_year[year]))
        if not nums:
            continue
        expected = set(range(1, max(nums) + 1))
        missing = sorted(expected - set(nums))
        if missing:
            gaps.append({
                "year": year,
                "max": max(nums),
                "have": len(nums),
                "missing": missing,
            })
    return gaps


def _phantom_citations(conn: sqlite3.Connection) -> list[dict]:
    """Find ND citations referenced in opinion text but not in our database."""
    rows = conn.execute("""
        SELECT tc.normalized, COUNT(DISTINCT tc.opinion_id) as citing_count
        FROM text_citations tc
        WHERE tc.cite_type = 'case'
          AND tc.normalized LIKE '% ND %'
          AND tc.normalized NOT LIKE '% N.D. %'
          AND NOT EXISTS (
              SELECT 1 FROM citations c WHERE c.citation = tc.normalized
          )
        GROUP BY tc.normalized
        ORDER BY tc.normalized
    """).fetchall()

    # Classify: within expected range or above max for that year
    max_by_year: dict[int, int] = {}
    for r in conn.execute(
        "SELECT citation FROM citations WHERE reporter = 'ND'"
    ).fetchall():
        m = re.match(r"(\d{4}) ND (\d+)", r["citation"])
        if m:
            yr, num = int(m.group(1)), int(m.group(2))
            max_by_year[yr] = max(max_by_year.get(yr, 0), num)

    phantoms = []
    for r in rows:
        cite = r["normalized"]
        m = re.match(r"(\d{4}) ND (\d+)", cite)
        if not m:
            continue
        yr, num = int(m.group(1)), int(m.group(2))
        max_cite = max_by_year.get(yr, 0)
        phantoms.append({
            "citation": cite,
            "citing_count": r["citing_count"],
            "within_range": num <= max_cite,
            "year_max": max_cite,
        })
    return phantoms


def _duplicate_reporter_citations(conn: sqlite3.Connection) -> dict[str, list[dict]]:
    """Find opinions with multiple citations from the same reporter.

    For NW2d and NW, filters out A.L.R. and L.R.A. cross-citations that
    got bucketed into the wrong reporter — those are a separate data issue.
    Only flags cases where multiple citations match the actual reporter pattern.
    """
    # Reporter-specific citation patterns (to distinguish real cites from cross-refs)
    reporter_patterns = {
        "ND": r"\d{4} ND \d+",
        "NDold": r"\d+ N\.D\. \d+",
        "NW2d": r"\d+ N\.W\.2d \d+",
        "NW": r"\d+ N\.W\. \d+",
    }

    results: dict[str, list[dict]] = {}

    for reporter in ("ND", "NDold", "NW2d", "NW"):
        rows = conn.execute("""
            SELECT o.id, o.case_name, o.date_filed,
                   GROUP_CONCAT(c.citation, '; ') as cites,
                   COUNT(*) as n
            FROM opinions o
            JOIN citations c ON c.opinion_id = o.id AND c.reporter = ?
            GROUP BY o.id
            HAVING n > 1
            ORDER BY o.date_filed
        """, (reporter,)).fetchall()

        pattern = re.compile(reporter_patterns[reporter])
        filtered = []
        for r in rows:
            # Count how many citations actually match the reporter pattern
            cites = r["cites"].split("; ")
            matching = [c for c in cites if pattern.match(c)]
            if len(matching) > 1:
                filtered.append({
                    "id": r["id"],
                    "case_name": r["case_name"],
                    "date_filed": r["date_filed"],
                    "citations": "; ".join(matching),
                    "count": len(matching),
                })

        if filtered:
            results[reporter] = filtered
    return results


def _volume_coverage(conn: sqlite3.Connection) -> dict[str, dict]:
    """Check NW and NW2d volume coverage."""
    results = {}

    for reporter, pattern in [("NW2d", r"(\d+) N\.W\.2d"), ("NW", r"(\d+) N\.W\. ")]:
        rows = conn.execute(
            "SELECT citation FROM citations WHERE reporter = ?", (reporter,)
        ).fetchall()
        vols: set[int] = set()
        for r in rows:
            m = re.match(pattern, r["citation"])
            if m:
                vols.add(int(m.group(1)))
        if vols:
            full_range = set(range(min(vols), max(vols) + 1))
            missing = sorted(full_range - vols)
            results[reporter] = {
                "min": min(vols),
                "max": max(vols),
                "present": len(vols),
                "missing_count": len(missing),
                "missing": missing,
            }
    return results


def run_audit(db_path: Path = DEFAULT_DB_PATH, save: bool = False) -> str:
    """Run all audit checks and return a formatted report."""
    conn = get_connection(db_path)

    total = conn.execute("SELECT COUNT(*) FROM opinions").fetchone()[0]
    date_range = conn.execute(
        "SELECT MIN(date_filed), MAX(date_filed) FROM opinions"
    ).fetchone()

    lines: list[str] = []
    lines.append("# Opinion Database Audit Report")
    lines.append("")
    lines.append(f"**{total:,} opinions** spanning {date_range[0]} to {date_range[1]}")
    lines.append("")

    # 1. ND citation gaps
    lines.append("## ND Neutral Citation Gaps")
    lines.append("")
    gaps = _nd_citation_gaps(conn)
    if gaps:
        for g in gaps:
            missing_str = ", ".join(str(n) for n in g["missing"][:20])
            if len(g["missing"]) > 20:
                missing_str += f" ... ({len(g['missing'])} total)"
            lines.append(
                f"- **{g['year']}**: max={g['max']}, have={g['have']}, "
                f"missing {len(g['missing'])}: {missing_str}"
            )
    else:
        lines.append("No gaps found.")
    lines.append("")

    # 2. Phantom citations
    lines.append("## Phantom Citations")
    lines.append("")
    lines.append("Citations found in opinion text that don't match any opinion in the database.")
    lines.append("")
    phantoms = _phantom_citations(conn)
    within_range = [p for p in phantoms if p["within_range"]]
    above_range = [p for p in phantoms if not p["within_range"]]

    if within_range:
        lines.append("### Likely missing opinions (within expected citation range)")
        lines.append("")
        for p in within_range:
            lines.append(
                f"- **{p['citation']}** — cited by {p['citing_count']} opinion(s), "
                f"year max is {p['year_max']}"
            )
        lines.append("")

    if above_range:
        lines.append("### Likely admin orders (above max opinion citation for year)")
        lines.append("")
        for p in above_range:
            lines.append(
                f"- {p['citation']} — cited by {p['citing_count']}, "
                f"year max is {p['year_max']}"
            )
        lines.append("")

    if not phantoms:
        lines.append("No phantom citations found.")
        lines.append("")

    # 3. Duplicate reporter citations
    lines.append("## Multiple Citations per Reporter")
    lines.append("")
    lines.append("Opinions with more than one citation from the same reporter (potential errors).")
    lines.append("")
    dupes = _duplicate_reporter_citations(conn)
    for reporter, items in dupes.items():
        lines.append(f"### {reporter} ({len(items)} opinions)")
        lines.append("")
        for d in items:
            lines.append(f"- id={d['id']} **{d['case_name']}** ({d['date_filed']}): {d['citations']}")
        lines.append("")

    if not dupes:
        lines.append("No duplicate reporter citations found.")
        lines.append("")

    # 4. Volume coverage
    lines.append("## NW/NW2d Volume Coverage")
    lines.append("")
    vol_cov = _volume_coverage(conn)
    for reporter, info in vol_cov.items():
        lines.append(
            f"- **{reporter}**: volumes {info['min']}–{info['max']}, "
            f"{info['present']} present, {info['missing_count']} missing"
        )
        if info["missing"]:
            missing_str = ", ".join(str(v) for v in info["missing"][:30])
            if len(info["missing"]) > 30:
                missing_str += f" ... ({info['missing_count']} total)"
            lines.append(f"  - Missing: {missing_str}")
    lines.append("")

    conn.close()

    report = "\n".join(lines)
    print(report)

    if save:
        MISSING_FILE.write_text(report + "\n")
        print(f"\nSaved to {MISSING_FILE}")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit opinion database for missing data")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--save", action="store_true", help="Save report to MISSING_OPINIONS.md")
    args = parser.parse_args()
    run_audit(args.db, args.save)


if __name__ == "__main__":
    main()
