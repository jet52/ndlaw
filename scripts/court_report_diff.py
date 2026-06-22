"""Diff DB metadata against the court's own opinions export (authoritative).

`input-data/court-opinions-report-2026-05-30.xlsx` (Sheet "Opinions", 12,329
cTrack-era rows: Case Number, Title, Nature Of Action, Author, Filing Date,
Document, NDCitNbr1/2, NWCitNbr1/2). Join to DB opinions by citation (ND neutral
preferred, then N.W.), then diff a field.

Phase 1: --field author. Report author is "Surname, First"; DB author is the bare
surname. Surface only SUBSTANTIVE mismatches (different justice), normalizing
spacing/case ("Vande Walle"→"VandeWalle"). PER CURIAM rows (no author in report)
are reported separately so a DB author-vs-None can be checked.

Output: triage/court-report-<field>-diff.csv + console summary. Read-only; no DB writes.
"""
from __future__ import annotations

import argparse
import csv
import re
import sqlite3
from pathlib import Path

import openpyxl

DB = Path(__file__).resolve().parent.parent / "opinions.db"
XLSX = Path(__file__).resolve().parent.parent / "input-data" / "court-opinions-report-2026-05-30.xlsx"


def norm_name(s: str) -> str:
    return re.sub(r"[^a-z]", "", (s or "").lower())


def report_surname(author: str) -> str:
    # "Maring, Mary" -> "Maring"; "Gierke III, H." -> "GierkeIII"->"Gierke"; "Vande Walle, Gerald" -> "VandeWalle"
    if not author:
        return ""
    last = author.split(",")[0].strip()
    last = re.sub(r"\b(III|II|Jr\.?|Sr\.?)\b", "", last).strip()
    return norm_name(last)


def nd_cite(v):
    m = re.match(r"\s*(\d{4})ND(\d+)\s*$", str(v or ""))
    return f"{m.group(1)} ND {m.group(2)}" if m else None


def nw_cite(v):
    m = re.match(r"\s*(\d+)NW(2d|3d)?(\d+)\s*$", str(v or ""))
    if not m:
        return None
    series = f"N.W.{m.group(2)}" if m.group(2) else "N.W."
    return f"{m.group(1)} {series} {m.group(3)}"


def load_report():
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb.active
    rows = []
    for r in ws.iter_rows(min_row=3, values_only=True):
        r = list(r) + [None] * (10 - len(r))
        rows.append(dict(case_number=r[0], title=r[1], nature=r[2], author=r[3],
                         filing_date=r[4], nd1=r[6], nd2=r[7], nw1=r[8], nw2=r[9]))
    return rows


def build_cite_index(conn):
    idx = {}
    for oid, cite, reporter in conn.execute(
            "SELECT opinion_id, citation, reporter FROM citations"):
        idx.setdefault(cite.replace("  ", " ").strip(), oid)
    return idx


def match_oid(rep, idx):
    for v in (nd_cite(rep["nd1"]), nd_cite(rep["nd2"])):
        if v and v in idx:
            return idx[v], v
    for v in (nw_cite(rep["nw1"]), nw_cite(rep["nw2"])):
        if v and v in idx:
            return idx[v], v
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field", default="author", choices=["author"])
    args = ap.parse_args()
    conn = sqlite3.connect(str(DB))
    idx = build_cite_index(conn)
    report = load_report()

    matched = unmatched = agree = 0
    conflict, db_missing, db_overattrib = [], [], []
    for rep in report:
        oid, via = match_oid(rep, idx)
        if not oid:
            unmatched += 1
            continue
        matched += 1
        o = conn.execute("SELECT case_name, author, per_curiam FROM opinions WHERE id=?",
                         (oid,)).fetchone()
        db_author, pc = o[1], o[2]
        db_sn = norm_name(db_author)
        rep_pc = (rep["author"] or "").strip().lower() in ("", "per curiam")
        rep_sn = "" if rep_pc else report_surname(rep["author"])
        row = (oid, via, rep["title"], db_author or "(none)", rep["author"] or "(blank)")
        if rep_pc:
            if db_sn and not pc:
                db_overattrib.append(row)        # report=per curiam, DB names an author
            else:
                agree += 1
        elif not db_sn:
            db_missing.append(row)               # report names an author, DB has none
        elif db_sn == rep_sn or rep_sn in db_sn or db_sn in rep_sn:
            agree += 1
        else:
            conflict.append(row)                 # both name an author, different surnames

    Path("triage").mkdir(exist_ok=True)
    for name, rows in (("conflict", conflict), ("db-missing", db_missing),
                       ("report-percuriam", db_overattrib)):
        out = Path("triage") / f"court-report-author-{name}.csv"
        with out.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["oid", "matched_via", "report_title", "db_author", "report_author"])
            w.writerows(rows)
    print(f"report rows: {len(report)}  matched: {matched}  unmatched: {unmatched}  agree: {agree}")
    print(f"\nCONFLICT (both name an author, different): {len(conflict)}  → triage/court-report-author-conflict.csv")
    print(f"DB-MISSING (report names author, DB none): {len(db_missing)}  → triage/court-report-author-db-missing.csv")
    print(f"REPORT-PERCURIAM (report per curiam, DB names author): {len(db_overattrib)}  → triage/court-report-author-report-percuriam.csv")
    from collections import Counter
    print("\nCONFLICT shapes (db → report):")
    for (dba, ra), n in Counter((m[3], report_surname(m[4])) for m in conflict).most_common(15):
        print(f"   {dba:<18} → {ra:<16} {n}")
    conn.close()


if __name__ == "__main__":
    main()
