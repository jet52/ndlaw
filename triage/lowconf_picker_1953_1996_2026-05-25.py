"""§2 low-confidence batch picker for 1953-1996 opinions.

Ranks the era's opinions by metadata-anomaly + importance signals to prioritize
targeted Westlaw Quick Checks. `quality_score` is deliberately NOT used (it is
empty signal for this NW2d-era OCR — every opinion scores >=0.9). Signals:

  NO_AUTHOR     author empty and not per_curiam            (wt 4)
  JUNK_AUTHOR   author is a 1-letter / non-name fragment   (wt 4)  (OCR truncation)
  DATE_OUTLIER  date_filed >60d outside its N.W.2d volume's date window
                (window from >=3 volume-mates; volumes run ~weeks)  (wt 3)
  NAME_ANOMALY  case_name truncated/garbled (trailing 'and'/'v.', 'Unknown',
                no ' v. ' and not an In-re/Application/Estate caption)  (wt 2)
  importance    + min(cited_by / 15, 3)   (heavily-cited opinions are worth
                                            getting right even if not anomalous)

Outputs a ranked CSV (highest score first) + a per-decade RANDOM_SAMPLE baseline
(8/decade) so Quick Check yield can be compared against a non-flagged baseline.
Read-only; produces a worklist only.
"""
import csv
import re
import sys
import random
from collections import defaultdict
from pathlib import Path
from statistics import median

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import sqlite3  # noqa: E402

DB = REPO / "opinions.db"
OUT = REPO / "triage/lowconf-1953-1996-2026-05-25.csv"
NW2D = re.compile(r"^(\d+)\s+N\.W\.2d\s+(\d+)")
NW = re.compile(r"^(\d+)\s+N\.W\.\s+(\d+)")
NAME_OK_PREFIX = ("in re", "in the matter", "in the interest", "matter of",
                  "application of", "estate of", "petition of")


def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    # N.W.2d volume date windows (>=3 opinions) for the DATE_OUTLIER check.
    vol_dates = defaultdict(list)
    for r in conn.execute(
        "SELECT o.date_filed d, c.citation cit FROM opinions o "
        "JOIN citations c ON c.opinion_id=o.id WHERE c.reporter='NW2d'"):
        m = NW2D.match(r["cit"])
        if m:
            vol_dates[int(m.group(1))].append(r["d"])
    win = {v: (min(ds), max(ds)) for v, ds in vol_dates.items() if len(ds) >= 3}

    import datetime
    def days_outside(d, lo, hi):
        dd = datetime.date.fromisoformat
        x = dd(d)
        if x < dd(lo):
            return (dd(lo) - x).days
        if x > dd(hi):
            return (x - dd(hi)).days
        return 0

    rows = conn.execute(
        "SELECT id, case_name, date_filed, author, per_curiam FROM opinions "
        "WHERE date_filed>='1953-01-01' AND date_filed<'1997-01-01'").fetchall()

    out = []
    for r in rows:
        oid, name = r["id"], (r["case_name"] or "")
        author = (r["author"] or "").strip()
        cb = conn.execute("SELECT COUNT(*) FROM cited_by WHERE cited_opinion_id=?",
                          (oid,)).fetchone()[0]
        cites = conn.execute(
            "SELECT citation, reporter FROM citations WHERE opinion_id=? "
            "AND reporter IN ('NW','NW2d') ORDER BY is_primary DESC", (oid,)).fetchall()
        nwcite = cites[0]["citation"] if cites else ""

        flags, score = [], 0.0
        if not author and not r["per_curiam"]:
            flags.append("NO_AUTHOR"); score += 4
        elif author and (len(author) < 3 or re.search(r"[^A-Za-z .,'\-]", author)):
            flags.append("JUNK_AUTHOR"); score += 4

        m = NW2D.match(nwcite)
        if m and int(m.group(1)) in win:
            lo, hi = win[int(m.group(1))]
            d = days_outside(r["date_filed"], lo, hi)
            if d > 60:
                flags.append(f"DATE_OUTLIER({d}d)"); score += 3

        low = name.lower()
        # High-precision caption-garble signals: a trailing dangling connective
        # ("…, and" / "… v." — a CL parse truncation), an explicit "Unknown", or
        # an implausibly short name. (A plain absence of " v. " is NOT flagged —
        # too many valid ND captions are non-versus, e.g. "Disciplinary Action
        # Against X", "Petition of Y".)
        name_bad = (re.search(r"(,\s*and|\band|\bv\.?)\s*$", name)
                    or "unknown" in low or len(name.strip()) < 6)
        if name_bad:
            flags.append("NAME_ANOMALY"); score += 2

        score += min(cb / 15.0, 3)
        if cb >= 41:
            flags.append(f"HICITE({cb})")
        out.append((round(score, 2), oid, r["date_filed"], nwcite, name[:60],
                    author, cb, "|".join(flags)))

    out.sort(key=lambda x: -x[0])

    # per-decade random baseline (8/decade), excluding already-flagged rows
    flagged_ids = {row[1] for row in out if row[7]}
    by_dec = defaultdict(list)
    for row in out:
        if row[1] not in flagged_ids:
            by_dec[row[2][:3] + "0s"].append(row)
    random.seed(20260525)
    sample = []
    for dec, rws in sorted(by_dec.items()):
        sample += random.sample(rws, min(8, len(rws)))

    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["score", "oid", "date_filed", "nw_cite", "case_name",
                    "author", "cited_by", "flags"])
        for row in out:
            w.writerow(row)
        w.writerow([])
        w.writerow(["# per-decade RANDOM baseline (unflagged) below"])
        for row in sample:
            w.writerow(list(row[:7]) + ["RANDOM_SAMPLE"])

    flagged = [r for r in out if r[7] and "HICITE" not in r[7] or
               (r[7] and r[7] != f"HICITE({r[6]})")]
    n_anom = sum(1 for r in out if any(t in r[7] for t in
                 ("NO_AUTHOR", "JUNK_AUTHOR", "DATE_OUTLIER", "NAME_ANOMALY")))
    print(f"ranked {len(out)} opinions -> {OUT}")
    print(f"  with an anomaly flag: {n_anom}")
    from collections import Counter
    fc = Counter()
    for r in out:
        for t in r[7].split("|"):
            if t:
                fc[t.split("(")[0]] += 1
    print("  flag counts:", dict(fc))
    print("  random baseline rows:", len(sample))
    print("\n  top 15 by score:")
    for r in out[:15]:
        print(f"    {r[0]:5}  {r[1]:>6}  {r[2]}  {r[3]:14}  cb={r[6]:>3}  {r[7]:30}  {r[4][:34]}")


if __name__ == "__main__":
    raise SystemExit(main())
