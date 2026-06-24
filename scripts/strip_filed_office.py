"""Strip "FILED IN THE OFFICE OF THE CLERK OF SUPREME COURT <date> STATE OF NORTH
DAKOTA" page-header stamps fused into opinion text_content.

A clerk filing-header variant the earlier strip_clerk_stamps pass did not match.
Administrative page furniture (not the court's authored opinion); often leads
text_content or is fused (leading docket number "20200122FILED..." / trailing
running header "...DAKOTAKuntz v. Leitner").

Same gate model as strip_clerk_stamps: per opinion, remove every occurrence, then
require the removed alpha-word multiset to be ONLY stamp vocabulary; mid-word
fusion cases that fail the strict gate are accepted only when the PDF confirms
every rejoined token is real. Dry-run by default; report (md + json).

Usage: strip_filed_office.py [--apply] [--db opinions.db]
       [--batch filed-office-2026-06-24] [--out triage/filed-office]
"""
import argparse
import json
import os
import re
import subprocess
import sqlite3
from collections import Counter
from datetime import datetime, timezone

REFS = os.path.expanduser("~/refs/nd/opin")
_MONTHS = ("January February March April May June July August September October "
           "November December")
_DATE = (r"(?:(?:" + "|".join(_MONTHS.split()) + r")\s+\d{1,2},?\s+\d{4}"
         r"|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})")
STAMP = re.compile(
    r"FILED IN THE OFFICE OF THE CLERK OF (?:THE )?SUPREME COURT\s+"
    + _DATE + r"\s*\d?\s*STATE OF NORTH DAKOTA", re.I)
VOCAB = set("FILED IN THE OFFICE OF CLERK SUPREME COURT STATE NORTH DAKOTA".split()) | \
    set(_MONTHS.split()) | set(_MONTHS.upper().split()) | set(_MONTHS.lower().split())
VOCAB = {w.lower() for w in VOCAB}


def words(s):
    return Counter(re.findall(r"[A-Za-z]+", s))


def pdf_text(con, oid):
    row = con.execute("SELECT citation FROM citations WHERE opinion_id=? "
                      "ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone()
    if not row or not row[0]:
        return ""
    nd = row[0].replace(" ", "")
    p = f"{REFS}/pdfs/{row[0].split()[0]}/{nd}.pdf"
    if not os.path.exists(p):
        return ""
    return re.sub(r"\s+", " ", subprocess.run(
        ["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--batch", default="filed-office-2026-06-24")
    ap.add_argument("--out", default="triage/filed-office")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    ids = [r[0] for r in con.execute(
        "SELECT id FROM opinions WHERE text_content LIKE '%FILED IN THE OFFICE OF THE CLERK%'").fetchall()]

    report, applied, skipped, tot = [], 0, 0, 0
    for oid in ids:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        n = len(STAMP.findall(old))
        if not n:
            continue
        new = STAMP.sub("", old)
        new = re.sub(r"[ \t]{2,}", " ", new)
        new = re.sub(r"\n{3,}", "\n\n", new)
        removed = words(old) - words(new)
        extra = {w: c for w, c in removed.items() if w.lower() not in VOCAB}
        added = words(new) - words(old)
        verdict = "OK"
        if extra or added:
            pt = pdf_text(con, oid)
            unconfirmed = [w for w in (+ (words(new) - words(old))) if not pt or w not in pt]
            if unconfirmed:
                skipped += 1
                report.append({"opinion_id": oid, "status": "SKIP", "n": n,
                               "bad_removed": extra, "bad_added": dict(+added),
                               "unconfirmed": unconfirmed})
                continue
            verdict = "OK_fusion_pdf"
        cite = con.execute("SELECT citation FROM citations WHERE opinion_id=? "
                           "ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone()
        applied += 1
        tot += n
        report.append({"opinion_id": oid, "cite": cite[0] if cite else "",
                       "status": verdict, "n": n})
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, args.batch, oid, "text_content.filed_office_header",
                 f"{n} FILED-IN-OFFICE header(s)", "removed",
                 "clerk filing page-header (not authored opinion); stamp-vocab word-multiset gate + PDF fusion fallback"))
    json.dump(report, open(f"{args.out}.json", "w"), ensure_ascii=False, indent=1)
    md = [f"# FILED-IN-OFFICE header strip — {'APPLIED' if args.apply else 'DRY-RUN'}", "",
          f"{applied} opinions OK ({tot} headers), {skipped} skipped (word-gate).", ""]
    if skipped:
        md += ["## Skipped (needs manual review)", ""]
        md += [f"- id{r['opinion_id']}: bad_removed={r.get('bad_removed')} unconfirmed={r.get('unconfirmed')}"
               for r in report if r["status"] == "SKIP"] + [""]
    open(f"{args.out}.md", "w").write("\n".join(md))
    print(f"candidates: {len(ids)}  OK: {applied}  skipped: {skipped}  headers: {tot}")
    print(f"report -> {args.out}.md / .json")
    if args.apply:
        con.commit()
        print(f"COMMITTED batch {args.batch}.")


if __name__ == "__main__":
    main()
