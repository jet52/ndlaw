"""Date scope scan for the court-archive era (archive.ndcourts.gov, ~1965-1997).
Extracts the "Filed <Mon D, YYYY>" line from each court-archive .htm (independent
of CourtListener) and compares to the opinions.date_filed COLUMN. Read-only.
Plain-text HTML so this is fast (no textutil)."""
from __future__ import annotations
import re
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
# anchored on the archive's own 'filed">Filed <date>' marker
FILED = re.compile(r"filed\"?>?\s*Filed\s+([A-Za-z]{3,9})\.?\s+(\d{1,2}),\s+(\d{4})", re.I)


def parse(path: Path) -> str | None:
    try:
        txt = path.read_text(errors="ignore")
    except OSError:
        return None
    m = FILED.search(txt)
    if not m:
        return None
    mon = MONTHS.get(m.group(1)[:3].lower())
    if not mon:
        return None
    try:
        return date(int(m.group(3)), mon, int(m.group(2))).isoformat()
    except ValueError:
        return None


def resolve(p: str) -> Path:
    return Path(p) if p.startswith("/") else REFS / p


def main():
    conn = get_connection(DEFAULT_DB_PATH)
    rows = conn.execute(
        "SELECT o.id, o.date_filed, s.source_path FROM opinions o "
        "JOIN opinion_sources s ON s.opinion_id=o.id "
        "WHERE s.source_reporter='court-archive'").fetchall()
    print(f"{len(rows)} court-archive sources")

    parsed = miss = unparsed = 0
    examples = []
    gaps = Counter()
    for r in rows:
        col = r["date_filed"]
        d = parse(resolve(r["source_path"]))
        if d is None:
            unparsed += 1
            continue
        parsed += 1
        if d != col:
            miss += 1
            try:
                g = abs((date.fromisoformat(d) - date.fromisoformat(col)).days)
            except ValueError:
                g = -1
            gaps["<=14d" if 0 < g <= 14 else "15-31d" if g <= 31 else ">31d" if g > 31 else "?"] += 1
            examples.append((r["id"], col, d, g))

    print(f"parsed archive 'Filed' date ... {parsed}")
    print(f"no 'Filed' line ............... {unparsed}")
    print(f"COLUMN != archive ............. {miss}  ({100*miss/parsed:.1f}% of parsed)")
    print(f"gap buckets: {dict(gaps)}")
    examples.sort(key=lambda e: e[3])
    print("\nexamples (oid | column | archive-date | days):")
    for oid, col, d, g in examples[:25]:
        print(f"  {oid:>6}  {col}  vs archive {d}  ({g}d)")


if __name__ == "__main__":
    main()
