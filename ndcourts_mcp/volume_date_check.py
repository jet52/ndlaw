"""Flag opinions whose ``date_filed`` is inconsistent with the date range of
the reporter volume they are cited in.

A bound reporter volume (N.W.2d, N.W. 1st, N.D. Reports) collects opinions
spanning at most ~1-1.5 years, so an opinion's ``date_filed`` should sit
within a couple years of its volume's central date. A large gap means a
contaminated date, a contaminated/typo'd cite, or a mis-paired source --
e.g. *Disciplinary Action Against McKinnon* carried ``date_filed`` 1972 while
cited at 264 N.W.2d 449, a 1978 volume.

The volume->year mapping is derived from the corpus itself: the MEDIAN
``date_filed`` year of opinions in each volume (robust to a few contaminated
outliers), with monotonic linear interpolation across sparsely-populated
volumes. The reporter cite is independent of ``date_filed``, so the median is
not circular for catching per-opinion date contamination.

Report-only: a flag needs human / second-source judgment (wrong date vs wrong
cite vs mis-pairing), so nothing is mutated.

Usage: python -m ndcourts_mcp.volume_date_check [--db PATH] [--threshold N]
       [--report PATH]
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import statistics
from collections import defaultdict
from pathlib import Path

from .db import DEFAULT_DB_PATH

_NW2D = re.compile(r"\b(\d+)\s+N\.\s*W\.\s*2d\s+(\d+)\b")
_NW1 = re.compile(r"\b(\d+)\s+N\.\s*W\.\s+(\d+)\b")        # N.W. 1st (no 2d)
_NDR = re.compile(r"\b(\d+)\s+N\.\s*D\.\s+(\d+)\b")        # N.D. Reports (periods)
_NEUTRAL = re.compile(r"\b((?:18|19|20)\d\d)\s+ND\s+(\d+)\b")  # YYYY ND n (no periods)

SERIES = ("NW2d", "NW", "NDR")
MIN_POP = 4          # volumes with >= this many opinions get a trusted median
DEFAULT_THRESHOLD = 3  # |year - expected| >= this is flagged


def parse_reporter_vols(cite: str) -> list[tuple[str, int]]:
    """Return [(series, volume)] for the reporter cites in a citation string."""
    out: list[tuple[str, int]] = []
    for m in _NW2D.finditer(cite):
        out.append(("NW2d", int(m.group(1))))
    masked = _NW2D.sub("  ", cite)            # so N.W.2d isn't re-read as N.W.
    for m in _NW1.finditer(masked):
        out.append(("NW", int(m.group(1))))
    for m in _NDR.finditer(cite):
        v = int(m.group(1))
        if v <= 120:                          # N.D. Reports ended at vol 79
            out.append(("NDR", v))
    return out


def neutral_year(cite: str) -> int | None:
    m = _NEUTRAL.search(cite)
    return int(m.group(1)) if m else None


def build_volume_years(conn) -> dict[tuple[str, int], float]:
    """(series, vol) -> expected filing year (median, sparse vols interpolated)."""
    years: dict[tuple[str, int], list[int]] = defaultdict(list)
    rows = conn.execute(
        "SELECT o.id, o.date_filed, c.citation FROM citations c "
        "JOIN opinions o ON o.id = c.opinion_id WHERE o.date_filed IS NOT NULL"
    ).fetchall()
    for oid, date_filed, citation in rows:
        yr = int(date_filed[:4])
        for series, vol in parse_reporter_vols(citation):
            years[(series, vol)].append(yr)

    trusted: dict[str, dict[int, float]] = {s: {} for s in SERIES}
    for (series, vol), ys in years.items():
        if len(ys) >= MIN_POP:
            trusted[series][vol] = statistics.median(ys)

    expected: dict[tuple[str, int], float] = {}
    for series in SERIES:
        tv = sorted(trusted[series])
        for (s, vol), ys in years.items():
            if s != series:
                continue
            if vol in trusted[series]:
                expected[(s, vol)] = trusted[series][vol]
                continue
            # interpolate from nearest trusted volumes (monotonic vol->year)
            lo = max((v for v in tv if v < vol), default=None)
            hi = min((v for v in tv if v > vol), default=None)
            if lo is not None and hi is not None:
                y0, y1 = trusted[series][lo], trusted[series][hi]
                expected[(s, vol)] = y0 + (y1 - y0) * (vol - lo) / (hi - lo)
            elif lo is not None:
                expected[(s, vol)] = trusted[series][lo]
            elif hi is not None:
                expected[(s, vol)] = trusted[series][hi]
            else:
                expected[(s, vol)] = statistics.median(ys)  # series too sparse
    return expected


def scan(conn, threshold: int):
    expected = build_volume_years(conn)
    cites_by_oid: dict[int, list[str]] = defaultdict(list)
    for oid, citation in conn.execute("SELECT opinion_id, citation FROM citations"):
        cites_by_oid[oid].append(citation)

    flags = []
    for oid, date_filed, case_name in conn.execute(
            "SELECT id, date_filed, case_name FROM opinions WHERE date_filed IS NOT NULL"):
        yr = int(date_filed[:4])
        cites = cites_by_oid.get(oid, [])
        worst = None
        for cite in cites:
            for series, vol in parse_reporter_vols(cite):
                exp = expected.get((series, vol))
                if exp is None:
                    continue
                diff = abs(yr - exp)
                if diff >= threshold and (worst is None or diff > worst[0]):
                    worst = (diff, series, vol, exp, cite)
        # neutral-year vs date-year (cheap exact sanity check)
        for cite in cites:
            ny = neutral_year(cite)
            if ny is not None and ny != yr:
                d = abs(ny - yr)
                if worst is None or d > worst[0]:
                    worst = (d, "NEUTRAL", ny, float(ny), cite)
        if worst:
            diff, series, vol, exp, cite = worst
            flags.append({
                "oid": oid, "date_filed": date_filed, "year": yr,
                "series": series, "vol": vol, "expected": round(exp, 1),
                "diff": round(diff, 1), "cite": cite, "cites": cites,
                "case_name": case_name,
            })
    flags.sort(key=lambda f: -f["diff"])
    return flags


def write_report(flags, out_path: Path, threshold: int):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    hi = [f for f in flags if f["diff"] >= 6]
    md = [f for f in flags if 3 <= f["diff"] < 6 and f["series"] != "NEUTRAL"]
    neu = [f for f in flags if f["series"] == "NEUTRAL"]
    lines = ["# Volume vs date_filed consistency audit (report-only)", ""]
    lines.append(f"Flagged when |date_filed year - reporter-volume median year| >= {threshold} "
                 "(volume year derived from the corpus median per volume).")
    lines.append("")
    lines.append(f"- HIGH confidence (>=6y off): {len(hi)}")
    lines.append(f"- MEDIUM (3-6y off, reporter): {len(md)}")
    lines.append(f"- neutral-cite year != date year: {len(neu)}")
    for label, group in (("HIGH (>=6y)", hi), ("MEDIUM (3-6y)", md),
                          ("NEUTRAL-cite year mismatch", neu)):
        if not group:
            continue
        lines += ["", f"## {label} ({len(group)})",
                  "| oid | date_filed | cite (series vol) | vol median yr | off | case_name |",
                  "|----:|-----------|-------------------|--------------:|----:|-----------|"]
        for f in group:
            lines.append(
                f"| {f['oid']} | {f['date_filed']} | {f['cite']} "
                f"({f['series']} {f['vol']}) | {f['expected']} | {f['diff']} | "
                f"{(f['case_name'] or '')[:46]} |")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    p.add_argument("--report", type=Path,
                   default=Path("triage") / "volume-date-audit-2026-05-27.md")
    args = p.parse_args()
    conn = sqlite3.connect(str(args.db))
    flags = scan(conn, args.threshold)
    hi = sum(1 for f in flags if f["diff"] >= 6)
    md = sum(1 for f in flags if 3 <= f["diff"] < 6 and f["series"] != "NEUTRAL")
    neu = sum(1 for f in flags if f["series"] == "NEUTRAL")
    print(f"volume-date flags: {len(flags)}  (HIGH>=6y: {hi}, MEDIUM 3-6y: {md}, "
          f"neutral-mismatch: {neu})")
    for f in flags[:25]:
        print(f"  off {f['diff']:>4} | oid {f['oid']} {f['date_filed']} | "
              f"{f['cite']} ({f['series']} {f['vol']} ~{f['expected']}) | "
              f"{(f['case_name'] or '')[:42]}")
    write_report(flags, args.report, args.threshold)
    print(f"\nReport: {args.report}")


if __name__ == "__main__":
    main()
