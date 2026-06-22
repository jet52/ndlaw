"""Backfill empty docket_number from the court's opinions report (authoritative).

Join `input-data/court-opinions-report-2026-05-30.xlsx` `Case Number` (cTrack ID)
to empty-docket DB opinions by citation, and propose the published docket form:

  - Modern `YYYYNNNN` (1997+, and recent admin matters) → stored verbatim; cross-
    checked against the body `No. YYYYNNNN` line where present.
  - cTrack `1860`-prefixed pre-1989 IDs → the published form is `Cr./Civ. <file>`
    (strip the synthetic `1860` prefix; the `1860`+4-digit mapping is documented
    only for ≤4-digit files — see [[project_ctrack_docket_scheme]]). The Cr./Civ.
    nature is taken from the body/case_name; if it can't be determined the row is
    left for manual handling rather than guessed.

Scope note: the report covers the cTrack era (~1965+), so it CANNOT supply dockets
for the ~5,072 pre-1953 empties (incl. pre-1931) — those need the N.D. Reports
volumes / a historical court index, tracked separately.

Dry-run by default. `--apply` backs up the DB, writes, logs `docket-backfill-court-report-<date>`.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sqlite3
from pathlib import Path

import openpyxl

DB = Path(__file__).resolve().parent.parent / "opinions.db"
XLSX = Path(__file__).resolve().parent.parent / "input-data" / "court-opinions-report-2026-05-30.xlsx"
BATCH = "docket-backfill-court-report-2026-06-22"


def nd_cite(v):
    m = re.match(r"\s*(\d{4})ND(\d+)\s*$", str(v or ""))
    return f"{m.group(1)} ND {m.group(2)}" if m else None


def nw_cite(v):
    m = re.match(r"\s*(\d+)NW(2d|3d)?(\d+)\s*$", str(v or ""))
    return f"{m.group(1)} N.W.{m.group(2) or ''} {m.group(3)}" if m else None


def published_form(case_number, body, case_name):
    """Return (docket, confidence, note) or (None, ...) if not derivable."""
    cn = str(case_number or "").strip()
    if not re.fullmatch(r"\d{8}", cn):
        return None, "low", f"non-8-digit Case Number {cn!r}"
    if not cn.startswith("1860"):
        # modern YYYYNNNN — verify against body 'No.' line if present
        body_has = re.search(rf"No\.?\s*{cn}\b", body or "")
        return cn, ("high" if body_has else "moderate"), ("body-confirmed" if body_has else "report-only (modern format)")
    # cTrack 1860-prefixed → published file = trailing digits sans leading zeros
    file_no = str(int(cn[4:]))
    text = ((case_name or "") + " " + (body[:400] if body else "")).lower()
    if re.search(r"\bcr\.|criminal|state of north dakota,? plaintiff", text):
        nature = "Cr."
    elif re.search(r"\bciv\.|civil", text):
        nature = "Civ."
    else:
        return None, "low", f"1860-prefixed but Cr./Civ. nature undetermined (file {file_no})"
    return f"{nature} {file_no}", "moderate", f"cTrack {cn}→{nature} {file_no} (number cTrack-only; nature from body)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row

    empty = {r["id"] for r in conn.execute(
        "SELECT id FROM opinions WHERE docket_number IS NULL OR docket_number=''")}
    idx = {}
    for oid, cite in conn.execute("SELECT opinion_id, citation FROM citations"):
        idx.setdefault(cite.strip(), oid)

    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb.active
    planned, manual = [], []
    for r in ws.iter_rows(min_row=3, values_only=True):
        r = list(r) + [None] * (10 - len(r))
        cn, title = r[0], r[1]
        oid = None
        for v in (nd_cite(r[6]), nd_cite(r[7]), nw_cite(r[8]), nw_cite(r[9])):
            if v and v in idx:
                oid = idx[v]; break
        if oid not in empty:
            continue
        o = conn.execute("SELECT case_name, text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        docket, conf, note = published_form(cn, o["text_content"], o["case_name"])
        if docket is None:
            manual.append((oid, cn, note)); continue
        planned.append((oid, docket, conf, note, o["case_name"]))

    print(f"=== {'APPLY' if args.apply else 'DRY-RUN'} — backfillable {len(planned)} / manual {len(manual)} ===\n")
    for oid, docket, conf, note, name in planned:
        print(f"  oid {oid} [{conf}] docket→{docket!r}  ({note})  {str(name)[:34]}")
    for oid, cn, note in manual:
        print(f"  MANUAL oid {oid}: {note}")

    if args.apply and planned:
        bak = DB.with_name(DB.name + ".bak-docket-backfill-2026-06-22")
        if not bak.exists():
            shutil.copy2(DB, bak); print(f"\nbackup → {bak.name}")
        for oid, docket, conf, note, name in planned:
            cur = conn.execute("SELECT docket_number FROM opinions WHERE id=?", (oid,)).fetchone()[0]
            conn.execute("INSERT INTO changelog (batch,opinion_id,field,old_value,new_value,authority) "
                         "VALUES (?,?,?,?,?,?)", (BATCH, oid, "docket_number", cur, docket,
                         f"court opinions report Case Number; {note}"))
            conn.execute("UPDATE opinions SET docket_number=? WHERE id=?", (docket, oid))
        conn.commit()
        print(f"APPLIED {len(planned)}; logged {BATCH}")
    conn.close()


if __name__ == "__main__":
    main()
