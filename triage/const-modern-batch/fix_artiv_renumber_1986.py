#!/usr/bin/env python3
"""Correct the effective-start dates of art. IV §§ 9-11 (the 1986 renumber gap).

Article IV (Legislative Branch) was repealed-and-recreated effective 1986-12-01
(approved at the June 12 & Nov 6, 1984 elections; S.L. 1983 ch. 728/730, 1985 ch.
706/707). Per the ND Legislative Council codified note at the beginning of art. IV:
"Sections 14, 15 and 19 of Article IV, which were not repealed, have been renumbered
as sections 9 to 11, inclusive." So:
    former § 14 (bribery)         -> § 9   "Bribery of Member"
    former § 15 (disqualification) -> § 10  "Disqualification by Conviction ..."
    former § 19 (writs/vacancy)    -> § 11  "Vacancy to be Filled ..."
The renumbered text was unchanged by the renumber. These citations therefore BEGAN
1986-12-01 — they did NOT exist as §§ 9-11 before then (former §§ 9-13 were repealed).

THE BUG: ndconst.org / ingest stamped § 9 and § 10 at the default 1889-10-01 (claiming
they existed since statehood), and the earlier §11 markup reconstruction used the modern
floor 1981-01-01 for its head. All three falsely place the §9/§10/§11 *citation* before
its 1986-12-01 origin. Fix = move each earliest version's start to 1986-12-01. No text
changes (the renumber preserved text; current text matches the 1981 BB former §§14/15/19).

WITNESS: each section's text confirmed present (despaced, to defeat the microfilm OCR
space-garble) in the 1981 Blue Book under its FORMER number — §14 bribery, §15
disqualification, §19 writs. Dual-source: codifier note + 1981 BB.

NOTE (scope/limitation): this removes the false pre-1986 claims; it does NOT add a
[1981,1986) layer for the old art IV numbering. Querying "art IV § 9 as of 1983" then
correctly returns nothing (the citation did not exist; the text was former § 14). Full
pre-1986 art IV coverage under the old numbers is the separate PL-CONST-CROSSWALK task.
Idempotent (guarded on the expected current stamps). Scratch only.
"""
import re
import sqlite3
import sys
from pathlib import Path

DB = "/tmp/const-scratch.db"
BATCH = "modern-artiv-renumber-1986-2026-06-15"
RENUMBER = "1986-12-01"
BB1981 = Path("~/refs/nd/const/processed/1981_blue-book_constitution.md").expanduser()

# modern §: (former §, old_start_expected, despaced witness fragment from 1981 BB)
FIX = {
    "9":  ("14", "1889-10-01", "deemedguiltyofsolicitationofbribery"),
    "10": ("15", "1889-10-01", "expelledforcorruption"),
    "11": ("19", "1981-01-01", "governorshallissuewritsofelection"),
}
AUTH = ("Renumbered from former art. IV § {f} eff. 1986-12-01 (art. IV recreation; "
        "S.L. 1983 ch. 728/730, 1985 ch. 706/707) — ND Legislative Council codified "
        "note; text unchanged, confirmed vs 1981 Blue Book former § {f}")


def despace(s):
    return re.sub(r"\s+", "", (s or "")).lower()


def main(apply=False):
    bb = despace(BB1981.read_text())
    con = sqlite3.connect(DB)
    problems, plan = [], []
    for sec, (former, old_start, frag) in FIX.items():
        cite = f"N.D. Const. art. IV, § {sec}"
        # earliest version of this provision (the one whose start is wrong)
        row = con.execute(
            "SELECT v.id, v.effective_start, v.effective_end, v.text_content "
            "FROM provisions p JOIN provision_versions v ON v.provision_id=p.id "
            "WHERE p.citation=? ORDER BY v.effective_start LIMIT 1", (cite,)).fetchone()
        if not row:
            problems.append(f"{cite}: not found"); continue
        vid, start, end, text = row
        if start == RENUMBER:
            print(f"{cite}: already {RENUMBER} (idempotent skip)"); continue
        if start != old_start:
            problems.append(f"{cite}: earliest start {start}, expected {old_start}")
        if frag not in bb:
            problems.append(f"{cite}: witness fragment {frag!r} not found in 1981 BB")
        present = "ok" if frag in bb else "MISSING"
        plan.append((cite, vid, former, start, end))
        print(f"{cite:26s} <- former § {former:>2s}  start {start} -> {RENUMBER}  "
              f"end={end or 'open'}  1981-BB witness={present}")

    if problems:
        print("\nGATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    if not plan:
        print("\nNothing to do."); con.close(); return
    print("\nGATES PASS (expected stamps; all three witnessed in 1981 BB under former #).")
    if not apply:
        print("\n(dry run) re-run with --apply"); con.close(); return

    for cite, vid, former, start, end in plan:
        con.execute("UPDATE provision_versions SET effective_start=?, "
                    "source_authority=COALESCE(NULLIF(source_authority,''),'')||' | '||? WHERE id=?",
                    (RENUMBER, AUTH.format(f=former), vid))
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                    "SELECT ?, provision_id, id, 'renumber_effective_start', "
                    "?, ? FROM provision_versions WHERE id=?",
                    (BATCH, f"{start} -> {RENUMBER} (renumbered from former § {former})",
                     "ND Legislative Council codified note (art. IV) + 1981 Blue Book", vid))
    con.commit()

    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions)
      SELECT count(*) FROM v WHERE nxt IS NOT NULL AND effective_end IS NOT NULL
      AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    print(f"\nFIXED {len(plan)} sections. integrity gaps={g}")
    for sec in FIX:
        pid = con.execute("SELECT id FROM provisions WHERE citation=?",
                          (f"N.D. Const. art. IV, § {sec}",)).fetchone()[0]
        spans = con.execute("SELECT effective_start, COALESCE(effective_end,'open') "
                            "FROM provision_versions WHERE provision_id=? ORDER BY effective_start",
                            (pid,)).fetchall()
        print(f"  §{sec:>2s}: " + "  ".join(f"[{s}->{e}]" for s, e in spans))
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
