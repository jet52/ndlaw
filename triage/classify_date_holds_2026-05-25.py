"""Classify the 93 date-discrepancy holds (read-only, produces a recommendation TSV).

Independent year signal = the opinion's N.W./N.W.2d reporter volume, mapped to its
median filing year across the whole corpus. That distinguishes a genuine
filed-vs-released gap (same era, keep/adopt by policy) from a parse artifact
(court year way off the volume era → keep CL).

Policy (ratified 2026-05-24): the court's *filing* date governs over CL. Holds were
the >31d gaps set aside for review. Output classes:
  KEEP_CL_later          court date is LATER (rehearing/supplemental or later artifact)
  KEEP_CL_cluster        court date is a value repeated across many holds (parse artifact)
  KEEP_CL_year_artifact  court YEAR is off the volume era (CL matches) — esp. same MM-DD
  ADOPT_COURT_sameyear   same calendar year, court earlier → filed-vs-released, adopt court
  ADOPT_COURT_clyear     CL year is off the era, court matches → CL year typo, adopt court
  FLAG                   ambiguous (both plausible / no era / both off) — manual
"""
import re
import sqlite3
from collections import Counter, defaultdict
from statistics import median

DB = "/Users/jerod/code/ndcourts-mcp/opinions.db"
HOLDS = "/Users/jerod/code/ndcourts-mcp/triage/date-discrepancy-holds-2026-05-24.tsv"
NW2D = re.compile(r"(\d+)\s+N\.W\.2d\s+(\d+)")
NW = re.compile(r"(\d+)\s+N\.W\.\s+(\d+)")

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# --- volume -> median filing year (whole corpus) ---
vol2d, vol1 = defaultdict(list), defaultdict(list)
for r in conn.execute(
    "SELECT o.date_filed d, c.citation cit, c.reporter rep FROM opinions o "
    "JOIN citations c ON c.opinion_id=o.id WHERE c.reporter IN ('NW','NW2d')"):
    y = int(r["d"][:4])
    if r["rep"] == "NW2d":
        m = NW2D.search(r["cit"])
        if m:
            vol2d[int(m.group(1))].append(y)
    else:
        m = NW.search(r["cit"])
        if m:
            vol1[int(m.group(1))].append(y)
era2d = {v: int(median(ys)) for v, ys in vol2d.items()}
era1 = {v: int(median(ys)) for v, ys in vol1.items()}


def opinion_era(oid):
    cites = conn.execute(
        "SELECT citation, reporter FROM citations WHERE opinion_id=? AND reporter IN ('NW','NW2d') "
        "ORDER BY is_primary DESC", (oid,)).fetchall()
    for c in cites:
        if c["reporter"] == "NW2d":
            m = NW2D.search(c["citation"])
            if m and int(m.group(1)) in era2d:
                return era2d[int(m.group(1))], f"{m.group(1)} N.W.2d"
        else:
            m = NW.search(c["citation"])
            if m and int(m.group(1)) in era1:
                return era1[int(m.group(1))], f"{m.group(1)} N.W."
    return None, "-"


# --- load holds ---
holds = []
with open(HOLDS) as f:
    next(f)
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 5:
            continue
        oid, cl, court, src, gap = parts[:5]
        holds.append((int(oid), cl, court, src, int(gap)))

court_counts = Counter(h[2] for h in holds)


def classify(oid, cl, court, src, gap, era):
    cl_y, court_y = int(cl[:4]), int(court[:4])
    if gap > 0:  # court date LATER
        if era is not None and era == court_y and era != cl_y:
            return "FLAG_later_eramatch"   # later court date matches era better than CL
        return "KEEP_CL_later"
    if court_counts[court] >= 3:
        return "KEEP_CL_cluster"
    if cl_y == court_y:
        return "ADOPT_COURT_sameyear"      # same year, court earlier → filed-vs-released
    # different year, court earlier
    if era is not None and abs(cl_y - era) <= 1 and abs(court_y - era) > 1:
        return "KEEP_CL_year_artifact"     # court YEAR off the volume era; CL matches
    if abs(gap) > 150:
        return "FLAG_xyear_largegap"       # cross-year gap >5mo: implausible filed-vs-released
    if era is not None and abs(court_y - era) <= 1:
        return "ADOPT_COURT_adjacent"      # year-boundary, court Nov/Dec → CL early next yr
    return "FLAG_other"


rows = []
for oid, cl, court, src, gap in holds:
    era, repname = opinion_era(oid)
    cls = classify(oid, cl, court, src, gap, era)
    o = conn.execute("SELECT case_name FROM opinions WHERE id=?", (oid,)).fetchone()
    rows.append((cls, oid, cl, court, src, gap, era if era else "-", repname,
                 cl[5:] == court[5:], o["case_name"][:42] if o else "?"))

rows.sort(key=lambda r: (r[0], r[1]))
print(f"{'class':24} {'oid':>6} {'CL':10} {'court':10} {'src':7} {'gap':>6} {'era':>5} {'rep':10} mmdd name")
for cls, oid, cl, court, src, gap, era, rep, mmdd, name in rows:
    print(f"{cls:24} {oid:>6} {cl} {court} {src:7} {gap:>6} {str(era):>5} {rep:10} {'Y' if mmdd else ' '}   {name}")

print("\n=== counts ===")
for cls, n in Counter(r[0] for r in rows).most_common():
    print(f"  {cls:24} {n}")

# recommendation TSV: action + new_date (court for ADOPT, blank for KEEP/FLAG)
OUT = "/Users/jerod/code/ndcourts-mcp/triage/date-holds-recommendation-2026-05-25.tsv"
with open(OUT, "w") as f:
    f.write("oid\taction\tnew_date\tclass\tcl_date\tcourt_date\tsource\tera\tcase_name\n")
    for cls, oid, cl, court, src, gap, era, rep, mmdd, name in rows:
        action = "ADOPT" if cls.startswith("ADOPT") else ("FLAG" if cls.startswith("FLAG") else "KEEP")
        new = court if action == "ADOPT" else ""
        f.write(f"{oid}\t{action}\t{new}\t{cls}\t{cl}\t{court}\t{src}\t{era}\t{name}\n")
print(f"\nwrote {OUT}")
adopt = sum(1 for r in rows if r[0].startswith("ADOPT"))
keep = sum(1 for r in rows if r[0].startswith("KEEP"))
flag = sum(1 for r in rows if r[0].startswith("FLAG"))
print(f"ACTION TOTALS: ADOPT {adopt}  KEEP {keep}  FLAG {flag}")
