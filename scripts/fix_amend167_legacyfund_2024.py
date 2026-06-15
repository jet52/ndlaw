#!/usr/bin/env python3
"""Fix the 2024 Legacy Fund amendment (number 167) mis-mapping.

ndconst.org's :amendments table lists amendment 167 (Legacy Fund, 2023 HCR 3033,
bill 23-3092) as affecting "art. XVI, §§ 1-5" — that cell was copied from amend 165
(the age-limit measure that CREATED art. XVI). The enacted bill amends section 26 of
article X. Effect of the bug: 167 was spliced onto art. XVI §§1-5 (5 spurious rows,
and their effective_start stamped 2024-12-05 instead of the 2024-06-11 create), and
art. X §26 lost its 2024 amendment event entirely.

This script (idempotent) corrects a target DB:
  - delete the 5 wrong amendment-167 rows (linked to art. XVI §§1-5);
  - insert one correct amendment-167 row linked to art. X §26;
  - reset art. XVI §§1-5 current-version effective_start -> 2024-06-11 (the create);
  - set art. X §26 current-version effective_start -> 2024-12-05 (its latest event).
The reproducible upstream fix is AMENDMENT_AFFECTED_CORRECTIONS in
ndcourts_mcp/ingest_constitution.py; this brings already-built DBs into line.

Usage: python scripts/fix_amend167_legacyfund_2024.py <db_path> [--apply]
"""
import argparse
import sqlite3
from pathlib import Path

BATCH = "fix-amend167-legacyfund-2024-06-14"
SRC = "https://ndlegis.gov/assembly/68-2023/regular/documents/23-3092-04000.pdf"
RAW = "Legacy Fund. (2023 HCR 3033)"


def pid_for(con, cite):
    r = con.execute("SELECT id, current_version_id FROM provisions WHERE citation=?", (cite,)).fetchone()
    return r if r else (None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db", type=Path)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)

    x26_pid, x26_vid = pid_for(con, "N.D. Const. art. X, § 26")
    if not x26_pid:
        raise SystemExit("art. X §26 not found")
    xvi = [(c, *pid_for(con, c)) for c in
           [f"N.D. Const. art. XVI, § {n}" for n in range(1, 6)]]

    n_wrong = con.execute("SELECT count(*) FROM amendments WHERE amendment_number='167'").fetchone()[0]
    print(f"DB: {args.db}")
    print(f"  amendment-167 rows currently: {n_wrong} (expect 5 wrong, on art. XVI §§1-5)")
    print(f"  art. X §26 pid={x26_pid}; art. XVI §§1-5 pids={[p for _,p,_ in xvi]}")

    if not args.apply:
        print("  (dry run) re-run with --apply")
        con.close(); return

    has_changelog = con.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='changelog'").fetchone()[0]

    def log(pid, field, old, new):
        if has_changelog:
            con.execute("INSERT INTO changelog (batch, provision_id, field, old_value, new_value, authority) "
                        "VALUES (?,?,?,?,?,?)", (BATCH, pid, field, old, new, "2023 HCR 3033 (bill 23-3092)"))

    # 1. delete the wrong 167 rows
    con.execute("DELETE FROM amendments WHERE amendment_number='167'")
    log(x26_pid, "amendment_167_mislink", "art. XVI §§1-5 (ndconst.org error)", "deleted 5 wrong rows")

    # 2. insert the correct 167 row on art. X §26 (skip if already present)
    exists = con.execute("SELECT count(*) FROM amendments WHERE amendment_number='167' AND provision_id=?",
                         (x26_pid,)).fetchone()[0]
    if not exists:
        con.execute(
            "INSERT INTO amendments (provision_id, action, effective_date, raw_date, election_date, "
            " affected, amendment_number, authority, source_url, raw) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (x26_pid, "amended", "2024-12-05", "2024-11-05", "2024-11-05",
             "art. X, § 26", "167", None, SRC, RAW))
        log(x26_pid, "amendment_event", None, "amend 167 (Legacy Fund) 2024-12-05 -> art. X §26")

    # 3. art. XVI §§1-5 effective_start -> 2024-06-11 (single create, amend 165)
    for c, p, v in xvi:
        if v:
            old = con.execute("SELECT effective_start FROM provision_versions WHERE id=?", (v,)).fetchone()[0]
            if old != "2024-06-11":
                con.execute("UPDATE provision_versions SET effective_start='2024-06-11' WHERE id=?", (v,))
                log(p, "effective_start", old, "2024-06-11")

    # 4. art. X §26 current effective_start -> 2024-12-05 (its latest event)
    old = con.execute("SELECT effective_start FROM provision_versions WHERE id=?", (x26_vid,)).fetchone()[0]
    if old != "2024-12-05":
        con.execute("UPDATE provision_versions SET effective_start='2024-12-05' WHERE id=?", (x26_vid,))
        log(x26_pid, "effective_start", old, "2024-12-05")

    con.commit()
    # report
    print("  AFTER:")
    for c in ["N.D. Const. art. X, § 26", "N.D. Const. art. XVI, § 1", "N.D. Const. art. XVI, § 5"]:
        r = con.execute("SELECT v.effective_start FROM provisions p JOIN provision_versions v "
                        "ON v.id=p.current_version_id WHERE p.citation=?", (c,)).fetchone()
        print(f"    {c:28} effective_start={r[0]}")
    r = con.execute("SELECT provision_id, affected, effective_date FROM amendments WHERE amendment_number='167'").fetchall()
    print(f"    amendment-167 rows now: {r}")
    con.close()


if __name__ == "__main__":
    main()
