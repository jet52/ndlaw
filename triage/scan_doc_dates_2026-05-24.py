"""AUTHORITATIVE date scope scan — compare the Westlaw .doc decision date (the
bound N.D. Reports text, independent of CourtListener metadata) against the
opinions.date_filed COLUMN. Read-only.

.doc structure (textutil -> txt):
    13 N.D. 387
    Supreme Court of North Dakota.
    LOUGH
    v.
    WHITE.
    Oct. 7, 1904.        <- decision date (first standalone Mon D, YYYY line)
    Syllabus by the Court.

Usage:
    --oids 6,45,...   classify a specific list (definitive for given opinions)
    --sample N        random N .doc-sourced opinions (estimate corpus rate)
    --full            every .doc-sourced opinion (slow: ~minutes)
"""
from __future__ import annotations
import argparse
import random
import re
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REFS = Path.home() / "refs" / "nd" / "opin"
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection  # noqa: E402

MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
DATE_LINE = re.compile(r"^((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)\.?\s+(\d{1,2}),\s+(\d{4})\.?\s*$", re.I)


def doc_date(path: Path) -> str | None:
    try:
        txt = subprocess.run(["textutil", "-convert", "txt", "-stdout", str(path)],
                             capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return None
    for line in txt.splitlines()[:25]:          # decision date is near the top
        m = DATE_LINE.match(line.strip())
        if m:
            mon = MONTHS.get(m.group(1)[:3].lower())
            if mon:
                try:
                    return date(int(m.group(3)), mon, int(m.group(2))).isoformat()
                except ValueError:
                    return None
    return None


def resolve(p: str) -> Path:
    return Path(p) if p.startswith("/") else REFS / p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--oids")
    ap.add_argument("--sample", type=int)
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)

    q = ("SELECT o.id, o.date_filed, s.source_path FROM opinions o "
         "JOIN opinion_sources s ON s.opinion_id=o.id "
         "WHERE s.source_path LIKE '%.doc'")
    rows = {r["id"]: (r["date_filed"], r["source_path"]) for r in conn.execute(q)}
    print(f"{len(rows)} opinions have a Westlaw .doc source")

    if args.oids:
        ids = [int(x) for x in args.oids.split(",")]
    elif args.sample:
        ids = random.Random(42).sample(list(rows), min(args.sample, len(rows)))
    elif args.full:
        ids = list(rows)
    else:
        ids = random.Random(42).sample(list(rows), min(400, len(rows)))
    print(f"checking {len(ids)} .docs...\n")

    parsed = mismatch = unparsed = 0
    examples = []
    gaps = Counter()
    for oid in ids:
        col, sp = rows[oid]
        dd = doc_date(resolve(sp))
        if dd is None:
            unparsed += 1
            continue
        parsed += 1
        if dd != col:
            mismatch += 1
            try:
                g = abs((date.fromisoformat(dd) - date.fromisoformat(col)).days)
            except ValueError:
                g = -1
            gaps["<=14d" if 0 < g <= 14 else "15-31d" if g <= 31 else ">31d" if g > 31 else "?"] += 1
            examples.append((oid, col, dd, g))

    print(f"parsed .doc date ... {parsed}")
    print(f"unparsed ........... {unparsed}")
    print(f"COLUMN != .doc ..... {mismatch}  ({100*mismatch/parsed:.1f}% of parsed)")
    print(f"gap buckets: {dict(gaps)}")
    examples.sort(key=lambda e: e[3])
    print("\nexamples (oid | column | .doc-date | days) — small gaps first:")
    for oid, col, dd, g in examples[:25]:
        print(f"  {oid:>6}  {col}  vs .doc {dd}  ({g}d)")


if __name__ == "__main__":
    main()
