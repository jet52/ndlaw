#!/usr/bin/env python3
"""Forward-sync the §69 partial-repeal correction into the served constitution.db.

Root cause (fixed at source in data/constitution_amendments.json, Amendment CVII): the §69
change was coded action:"repeal" (FULL repeal) when S.L. 1981 ch. 655 (SCR 4006, eff 1980-10-02)
repealed ONLY subsection 6 (jurisdiction of justices of the peace, police magistrates, constables),
collateral to abolishing county judges (§173). The remaining 34 enumerated cases survived until
the 1986 art IV recreation.

The JSON fix is the canonical correction: a full rebuild (ingest_constitution -> ingest_constitution
_history -> merge_const_history) regenerates §69 correctly. constitution_history.db has already been
regenerated from the fixed JSON (diff confirmed ONLY §69 changed). But re-running ingest_constitution
re-fetches ndconst.org (drift risk) and merge refuses to run on an already-merged DB, so this script
forward-syncs §69 in the EXISTING served constitution.db from the corrected constitution_history.db —
exactly what a clean re-merge would produce, with minimal blast radius (one provision).

What it changes in constitution.db:
  - § 69 provision status: 'repealed' -> 'active'
  - § 69 version [1980-10-02, 1980-12-31]: text "[Repealed effective 1980-10-02 …]" -> the surviving
    34-item list (subsections 1-5, 7-35; sub 6 removed), sourced verbatim from constitution_history.db
  - provisions_fts: re-index that version (external-content FTS5)

Idempotent. Run AFTER ingest_constitution_history --apply (so the source history DB is corrected).
"""
import argparse
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = "fix-s69-partial-repeal-2026-06-15"
CITE = "N.D. Const. § 69"
WINDOW = ("1980-10-02", "1980-12-31")


def fetch_correct_text(hist_db):
    c = sqlite3.connect(f"file:{hist_db}?mode=ro", uri=True)
    row = c.execute(
        "SELECT pv.text_content, p.status FROM provisions p JOIN provision_versions pv "
        "ON pv.provision_id=p.id WHERE p.citation=? AND pv.effective_start=? AND pv.effective_end=?",
        (CITE, *WINDOW)).fetchone()
    c.close()
    if not row:
        sys.exit(f"ABORT: corrected {CITE} [{WINDOW[0]},{WINDOW[1]}] not found in {hist_db} "
                 "(run ingest_constitution_history --apply first)")
    return row[0], row[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=Path, default=ROOT / "constitution.db")
    ap.add_argument("--source", type=Path, default=ROOT / "constitution_history.db")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    new_text, new_status = fetch_correct_text(args.source)
    if new_text.strip().lower().startswith("[repealed"):
        sys.exit("ABORT: source history still shows §69 as repealed — fix the JSON + re-ingest first")

    con = sqlite3.connect(args.target)
    con.row_factory = sqlite3.Row
    prov = con.execute("SELECT id, status FROM provisions WHERE citation=?", (CITE,)).fetchone()
    if not prov:
        sys.exit(f"ABORT: {CITE} not present in {args.target.name}")
    pid = prov["id"]
    ver = con.execute("SELECT id, text_content FROM provision_versions WHERE provision_id=? "
                      "AND effective_start=? AND effective_end=?", (pid, *WINDOW)).fetchone()
    if not ver:
        sys.exit(f"ABORT: {CITE} [{WINDOW[0]},{WINDOW[1]}] version not found in target")
    vid, old_text = ver["id"], ver["text_content"]

    if old_text == new_text and prov["status"] == new_status:
        print("already corrected (idempotent no-op)"); con.close(); return
    print(f"{CITE}: status {prov['status']}->{new_status}; version {vid} text "
          f"{len(old_text)}c -> {len(new_text)}c (surviving 34-item list)")
    if not args.apply:
        print("(dry run) re-run with --apply"); con.close(); return

    heading = con.execute("SELECT heading FROM provisions WHERE id=?", (pid,)).fetchone()["heading"] or ""
    # external-content FTS5: delete the stale row (must supply the indexed values), then re-insert.
    con.execute("INSERT INTO provisions_fts(provisions_fts, rowid, citation, heading, text_content) "
                "VALUES('delete', ?, ?, ?, ?)", (vid, CITE, heading, old_text))
    con.execute("UPDATE provision_versions SET text_content=? WHERE id=?", (new_text, vid))
    con.execute("UPDATE provisions SET status=? WHERE id=?", (new_status, pid))
    con.execute("INSERT INTO provisions_fts(rowid, citation, heading, text_content) VALUES(?,?,?,?)",
                (vid, CITE, heading, new_text))
    con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                "VALUES (?,?,?,?,?,?)", (BATCH, pid, vid, "s69_partial_repeal_correction",
                f"§69 [{WINDOW[0]},{WINDOW[1]}] = surviving 34-item list (sub 6 only repealed); status->active",
                "S.L. 1981 ch. 655 (SCR 4006); data/constitution_amendments.json CVII corrected 2026-06-15"))
    con.commit()

    # verify FTS round-trips and no stray repeal tombstone remains
    chk = con.execute("SELECT text_content FROM provision_versions WHERE id=?", (vid,)).fetchone()[0]
    hits = con.execute("SELECT COUNT(*) FROM provisions_fts WHERE provisions_fts MATCH "
                       "'\"granting divorces\"'").fetchone()[0]
    print(f"APPLIED. §69 version now {len(chk)}c; FTS match 'granting divorces' rows={hits}")
    con.close()


if __name__ == "__main__":
    main()
