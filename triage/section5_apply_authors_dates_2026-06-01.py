#!/usr/bin/env python3
"""§5 apply — two verified batches from the court-report diff.

Batch A  fix-author-courtreport-byline-2026-06-01
  95 author corrections where the court's official report AND the opinion-body
  byline ("Opinion of the Court by X") BOTH disagree with opinions.author.
  Re-derives the byline here (does not trust the diff TSV). Only applies when
  body-author == report-surname and != db-author. Clears per_curiam if set.

Batch B  fix-date-courtreport-le31d-pre1997-2026-06-01
  153 date_filed corrections, pre-1997, where report (court filing date) and
  DB (CourtListener) differ by <=31 days. Ratified policy: court date governs.

Usage: --apply to write; default dry-run.
"""
import sqlite3, re, csv, sys
from datetime import date

DB = "/Users/jerod/code/ndcourts-mcp/opinions.db"
MM = "/Users/jerod/code/ndcourts-mcp/triage/s5-report-diff-2026-06-01/mismatches.tsv"
APPLY = "--apply" in sys.argv

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
mm = list(csv.DictReader(open(MM), delimiter="\t"))

BYLINE = re.compile(r'Opinion of the [Cc]ourt[^.\n]{0,50}?by\s+([A-Z][A-Za-z.\']+)', re.I)
def body_author(txt):
    m = BYLINE.search(txt)
    return m.group(1).rstrip(".") if m else None

def pd(s):
    try:
        y, m, d = map(int, s.split("-")); return date(y, m, d)
    except Exception:
        return None

# ---------- Batch A: authors ----------
A_BATCH = "fix-author-courtreport-byline-2026-06-01"
a_apply = []   # (oid, old, new, per_curiam_clear)
a_skip = []
for x in mm:
    if x["field"] != "author":
        continue
    oid = int(x["oid"]); dbv = x["db_value"].strip(); rep = x["report_value"].strip()
    rep_norm = rep.replace(" III", "").replace(" Jr.", "").strip()
    row = con.execute("SELECT text_content, author, per_curiam FROM opinions WHERE id=?", (oid,)).fetchone()
    ba = body_author(row["text_content"])
    if ba is None:
        a_skip.append((oid, "no_byline")); continue
    if ba.lower() == rep_norm.lower() and ba.lower() != dbv.lower():
        a_apply.append((oid, row["author"], ba, bool(row["per_curiam"])))
    else:
        a_skip.append((oid, f"body={ba} db={dbv} rep={rep}"))

# ---------- Batch B: dates pre-1997 <=31d ----------
B_BATCH = "fix-date-courtreport-le31d-pre1997-2026-06-01"
b_apply = []   # (oid, old, new)
b_skip = []
for x in mm:
    if x["field"] != "date_filed":
        continue
    oid = int(x["oid"]); dbv = x["db_value"].strip(); rep = x["report_value"].strip()
    a, b = pd(dbv), pd(rep)
    if not (a and b):
        b_skip.append((oid, "unparsable")); continue
    if b.year >= 1997:
        b_skip.append((oid, "modern")); continue
    if abs((a - b).days) <= 31:
        b_apply.append((oid, dbv, rep))
    else:
        b_skip.append((oid, ">31d"))

print(f"BATCH A authors: apply {len(a_apply)}, skip {len(a_skip)}")
print(f"BATCH B dates  : apply {len(b_apply)}, skip {len(b_skip)}")
pc_clears = sum(1 for _,_,_,pc in a_apply if pc)
print(f"  (author batch also clears per_curiam on {pc_clears} rows that had it set)")

if not APPLY:
    print("\nDRY RUN — rerun with --apply to write.")
    print("sample authors:", [(o, f"{old}->{new}") for o, old, new, _ in a_apply[:8]])
    print("sample dates  :", [(o, f"{old}->{new}") for o, old, new in b_apply[:8]])
    sys.exit(0)

cur = con.cursor()
for oid, old, new, pc in a_apply:
    cur.execute("UPDATE opinions SET author=? WHERE id=?", (new, oid))
    cur.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value, authority) VALUES (?,?,?,?,?,?)",
                (A_BATCH, oid, "author", old, new,
                 "court opinions report 2026-05-30 + opinion-body byline ('Opinion of the Court by X')"))
    if pc:
        cur.execute("UPDATE opinions SET per_curiam=0 WHERE id=?", (oid,))
        cur.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value, authority) VALUES (?,?,?,?,?,?)",
                    (A_BATCH, oid, "per_curiam", "1", "0",
                     "body byline names an authoring justice -> not per curiam"))
for oid, old, new in b_apply:
    cur.execute("UPDATE opinions SET date_filed=? WHERE id=?", (new, oid))
    cur.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value, authority) VALUES (?,?,?,?,?,?)",
                (B_BATCH, oid, "date_filed", old, new,
                 "court opinions report 2026-05-30 Filing Date (court date governs, <=31d, ratified 2026-05-24)"))
con.commit()
print(f"\nAPPLIED. Batch A: {len(a_apply)} authors (+{pc_clears} per_curiam clears). Batch B: {len(b_apply)} dates.")
print("changelog rows:", con.execute("SELECT COUNT(*) FROM changelog WHERE batch IN (?,?)", (A_BATCH, B_BATCH)).fetchone()[0])
