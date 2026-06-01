#!/usr/bin/env python3
"""§5 — Field validation against the court's official opinions report.

Read-only. Joins input-data/court-opinions-report-2026-05-30.xlsx (the ND
Supreme Court's own cTrack export, ~1965-present, 12,329 rows) to opinions.db
by citation and diffs each field. Produces a categorized mismatch report for
per-item adjudication (data-correction-verification rule: this report is a
strong independent authority, but we adjudicate, not bulk-apply).

Match priority per report row:
  1. ND neutral cite (1997+)   ->  citations.reporter='ND-neutral'
  2. N.W.2d / N.W.3d / N.W.    ->  citations.reporter in ('NW2d','NW3d','NW')
  3. (fallback) cTrack docket  ->  opinions.docket_number  (modern YYYYNNNN only)

Outputs:
  triage/s5-report-diff-2026-06-01/summary.txt
  triage/s5-report-diff-2026-06-01/mismatches.tsv   (one row per field mismatch)
  triage/s5-report-diff-2026-06-01/unmatched.tsv     (report rows w/ no DB match)
"""
import openpyxl, re, sqlite3, os, sys
from collections import defaultdict, Counter

XLSX = "input-data/court-opinions-report-2026-05-30.xlsx"
DB = "opinions.db"
OUT = "triage/s5-report-diff-2026-06-01"
os.makedirs(OUT, exist_ok=True)

# ---------- normalizers ----------
def norm_nd(v):
    """1997ND18 -> '1997 ND 18'; 1998NDApp7 -> '1998 ND App 7'."""
    if not v: return None
    s = str(v).strip()
    m = re.match(r'^(\d{4})ND(App)?(\d+)$', s)
    if not m: return None
    yr, app, n = m.groups()
    return f"{yr} ND {'App ' if app else ''}{int(n)}"

def norm_nw(v):
    """146NW2d159 -> '146 N.W.2d 159'; NW3d/NW handled."""
    if not v: return None
    s = str(v).strip().replace(" ", "")
    m = re.match(r'^(\d+)(NW2d|NW3d|NW)(\d+)$', s)
    if not m: return None
    vol, rep, page = m.groups()
    rmap = {'NW2d': 'N.W.2d', 'NW3d': 'N.W.3d', 'NW': 'N.W.'}
    # report zero-pads pages ('055'); DB stores bare ('55'). Strip leading zeros.
    return f"{int(vol)} {rmap[rep]} {int(page)}"

def norm_date(v):
    """MM/DD/YYYY -> YYYY-MM-DD."""
    if not v: return None
    s = str(v).strip()
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', s)
    if not m: return None
    mo, d, y = m.groups()
    return f"{y}-{int(mo):02d}-{int(d):02d}"

def surname(author):
    """'Strutz, Alvin' -> 'Strutz'."""
    if not author: return None
    return str(author).split(",")[0].strip()

def has(x): return x is not None and str(x).strip() != ''
def g(r, i): return r[i] if i < len(r) else None

# ---------- load report ----------
wb = openpyxl.load_workbook(XLSX, read_only=True)
ws = wb.active
it = ws.iter_rows(values_only=True)
next(it); next(it)  # title + header
report = []
for r in it:
    report.append({
        "casenum": str(r[0]).strip() if has(r[0]) else None,
        "title": g(r, 1),
        "nature": g(r, 2),
        "author": g(r, 3),
        "date_raw": g(r, 4),
        "date": norm_date(g(r, 4)),
        "nd1": norm_nd(g(r, 6)),
        "nd2": norm_nd(g(r, 7)),
        "nw1": norm_nw(g(r, 8)),
        "nw2": norm_nw(g(r, 9)),
        "nd1_raw": g(r, 6), "nw1_raw": g(r, 8),
    })
print(f"report rows: {len(report)}")

# ---------- load DB ----------
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
ops = {row["id"]: row for row in con.execute(
    "SELECT id, case_name, date_filed, author, per_curiam, docket_number FROM opinions")}

# cite -> set(oid) maps
cite2oid = defaultdict(set)   # ND-neutral
nw2oid = defaultdict(set)     # NW family
for row in con.execute("SELECT opinion_id, citation, reporter FROM citations"):
    rep, c = row["reporter"], row["citation"]
    if rep == "ND-neutral":
        cite2oid[c].add(row["opinion_id"])
    elif rep in ("NW2d", "NW3d", "NW"):
        nw2oid[c].add(row["opinion_id"])

# modern docket -> oid (YYYYNNNN)
dock2oid = defaultdict(set)
for oid, o in ops.items():
    d = o["docket_number"]
    if d and re.match(r'^\d{8}$', str(d).strip()):
        dock2oid[str(d).strip()].add(oid)

# ---------- match ----------
match_methods = Counter()
matched = []      # (rep_row, oid, method)
unmatched = []    # rep rows
collisions = []   # rep rows that matched >1 oid

for rr in report:
    oid = None; method = None; cands = set()
    if rr["nd1"] and rr["nd1"] in cite2oid:
        cands = cite2oid[rr["nd1"]]; method = "nd-cite"
    if not cands and rr["nw1"] and rr["nw1"] in nw2oid:
        cands = nw2oid[rr["nw1"]]; method = "nw-cite"
    if not cands and rr["casenum"] and rr["casenum"] in dock2oid:
        cands = dock2oid[rr["casenum"]]; method = "docket"
    if not cands:
        unmatched.append(rr); match_methods["UNMATCHED"] += 1; continue
    if len(cands) > 1:
        collisions.append((rr, sorted(cands), method))
        match_methods[method + "-COLLISION"] += 1
        # still record diffs against each? skip diffing ambiguous; just log
        continue
    oid = next(iter(cands))
    matched.append((rr, oid, method))
    match_methods[method] += 1

# ---------- diff matched ----------
fields = Counter()
mismatch_rows = []  # (oid, casenum, field, db_val, report_val, method)

def norm_name(s):
    if not s: return ""
    s = str(s).lower()
    s = re.sub(r'\([^)]*\)', '', s)          # drop (CONFIDENTIAL) etc
    s = s.replace("&", "and")
    s = re.sub(r'\bet al\.?', '', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

for rr, oid, method in matched:
    o = ops[oid]
    # author (surname)
    rep_sn = surname(rr["author"])
    db_au = o["author"]
    if has(rep_sn) and rep_sn not in ("Per Curiam", "Not Available"):
        if not has(db_au) or db_au in ("Not Available",):
            if not o["per_curiam"]:
                fields["author_missing_in_db"] += 1
                mismatch_rows.append((oid, rr["casenum"], "author_missing", db_au or "", rep_sn, method))
        elif rep_sn.lower() != str(db_au).strip().lower():
            fields["author_diff"] += 1
            mismatch_rows.append((oid, rr["casenum"], "author", db_au, rep_sn, method))
    # date_filed
    if rr["date"] and rr["date"] != o["date_filed"]:
        # measure gap in days
        fields["date_diff"] += 1
        mismatch_rows.append((oid, rr["casenum"], "date_filed", o["date_filed"], rr["date"], method))
    # case_name vs title
    if has(rr["title"]) and norm_name(rr["title"]) != norm_name(o["case_name"]):
        fields["casename_diff"] += 1
        mismatch_rows.append((oid, rr["casenum"], "case_name", o["case_name"], rr["title"], method))

# ---------- write ----------
with open(f"{OUT}/summary.txt", "w") as f:
    f.write(f"§5 court-report field validation — {len(report)} report rows\n\n")
    f.write("MATCH METHODS:\n")
    for k, v in match_methods.most_common():
        f.write(f"  {k:24s} {v}\n")
    f.write(f"\n  matched (1:1): {len(matched)}\n")
    f.write(f"  collisions (>1 oid): {len(collisions)}\n")
    f.write(f"  unmatched: {len(unmatched)}\n\n")
    f.write("FIELD MISMATCHES (among 1:1 matched):\n")
    for k, v in fields.most_common():
        f.write(f"  {k:24s} {v}\n")

# date-gap histogram for matched date diffs
from datetime import date
def parse(d):
    try:
        y,m,dd = map(int, d.split("-")); return date(y,m,dd)
    except: return None
gaps = []
for oid, cn, fld, dbv, rv, meth in mismatch_rows:
    if fld == "date_filed":
        a, b = parse(dbv), parse(rv)
        if a and b: gaps.append(abs((a-b).days))
gapc = Counter()
for gp in gaps:
    if gp <= 7: gapc["<=7d"] += 1
    elif gp <= 31: gapc["8-31d"] += 1
    elif gp <= 90: gapc["32-90d"] += 1
    else: gapc[">90d"] += 1
with open(f"{OUT}/summary.txt", "a") as f:
    f.write("\nDATE-DIFF GAP DISTRIBUTION:\n")
    for k in ["<=7d","8-31d","32-90d",">90d"]:
        f.write(f"  {k:8s} {gapc.get(k,0)}\n")

with open(f"{OUT}/mismatches.tsv", "w") as f:
    f.write("oid\tcasenum\tfield\tdb_value\treport_value\tmethod\n")
    for oid, cn, fld, dbv, rv, meth in mismatch_rows:
        f.write(f"{oid}\t{cn}\t{fld}\t{dbv}\t{rv}\t{meth}\n")

with open(f"{OUT}/unmatched.tsv", "w") as f:
    f.write("casenum\ttitle\tdate\tnd1\tnw1\tauthor\n")
    for rr in unmatched:
        f.write(f"{rr['casenum']}\t{rr['title']}\t{rr['date_raw']}\t{rr['nd1_raw']}\t{rr['nw1_raw']}\t{rr['author']}\n")

with open(f"{OUT}/collisions.tsv", "w") as f:
    f.write("casenum\ttitle\tnd1\tnw1\tmethod\toids\n")
    for rr, oids, method in collisions:
        f.write(f"{rr['casenum']}\t{rr['title']}\t{rr['nd1_raw']}\t{rr['nw1_raw']}\t{method}\t{','.join(map(str,oids))}\n")

print(open(f"{OUT}/summary.txt").read())
