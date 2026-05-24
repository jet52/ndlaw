"""SCOPE SCAN (read-only) — estimate how widespread the date_filed discrepancy is.

Signal: the text_content YAML frontmatter carries a `date_filed:` that was
populated from the source document (e.g. the Westlaw .doc's "Mon D, YYYY" line),
which can diverge from the `opinions.date_filed` COLUMN (often a stale CourtListener
cluster-level date). Example proven by hand: oid 6 Lough — frontmatter 1904-10-07
(matches the bound/.doc) vs column 1904-10-10 (wrong).

This compares frontmatter date vs column for every opinion, buckets by era, and
lists the worst offenders. Read-only — no DB writes. (Frontmatter is a strong but
not perfect proxy: it misses cases where BOTH are the same wrong CL date.)
"""
from __future__ import annotations
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection  # noqa: E402

FM_DATE = re.compile(r"date_filed:\s*\"?(\d{4}-\d{2}-\d{2})\"?")


def era(d: str) -> str:
    y = int(d[:4])
    if y < 1925: return "1890-1924"
    if y < 1953: return "1925-1952"
    if y < 1997: return "1953-1996"
    return "1997+"


def main():
    conn = get_connection(DEFAULT_DB_PATH)
    rows = conn.execute(
        "SELECT id, date_filed, substr(text_content,1,600) AS head FROM opinions"
    ).fetchall()

    checked = Counter()       # era -> opinions with a frontmatter date
    mismatch = Counter()      # era -> mismatches
    no_fm = 0
    diffs = []                # (oid, col_date, fm_date, day_gap)
    for r in rows:
        col = r["date_filed"]
        m = FM_DATE.search(r["head"] or "")
        if not m:
            no_fm += 1
            continue
        fm = m.group(1)
        checked[era(col)] += 1
        if fm != col:
            mismatch[era(col)] += 1
            from datetime import date
            try:
                gap = abs((date.fromisoformat(fm) - date.fromisoformat(col)).days)
            except ValueError:
                gap = -1
            diffs.append((r["id"], col, fm, gap))

    total_chk = sum(checked.values())
    total_mm = sum(mismatch.values())
    print(f"opinions total ............ {len(rows)}")
    print(f"  no frontmatter date ..... {no_fm}")
    print(f"  with frontmatter date ... {total_chk}")
    print(f"  COLUMN != FRONTMATTER ... {total_mm}  ({100*total_mm/total_chk:.1f}% of checked)\n")
    print(f"{'era':<12}{'checked':>9}{'mismatch':>10}{'rate':>8}")
    for e in ("1890-1924", "1925-1952", "1953-1996", "1997+"):
        c, mm = checked[e], mismatch[e]
        print(f"{e:<12}{c:>9}{mm:>10}{(100*mm/c if c else 0):>7.1f}%")

    # day-gap distribution
    gaps = Counter()
    for _o, _c, _f, g in diffs:
        gaps["same-year, <=7d" if 0 < g <= 7 else
             "8-31d" if 8 <= g <= 31 else
             ">31d" if g > 31 else "unknown"] += 1
    print("\nday-gap of mismatches:", dict(gaps))

    diffs.sort(key=lambda d: -d[3])
    print("\nlargest gaps (oid | column | frontmatter | days):")
    for oid, col, fm, g in diffs[:15]:
        print(f"  {oid:>6}  {col}  ->fm {fm}  ({g}d)")
    print("\nsmall same-month gaps (likely the bound-vs-CL pattern):")
    for oid, col, fm, g in [d for d in diffs if 0 < d[3] <= 14][:15]:
        print(f"  {oid:>6}  {col}  ->fm {fm}  ({g}d)")


if __name__ == "__main__":
    main()
