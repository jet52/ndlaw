"""TRUE_TRUNCATION one-offs — explicit, PDF-verified panel restorations.

The 7 cases the general phase-4 fixer correctly skipped (dateline-in-source,
surrogate D.J./S.J. not in the modern-surname roster, roman-numeral section
heading fused into the panel). Each plan below is hand-built and every justice
name is verified against the court PDF
(`~/refs/nd/opin/pdfs/<year>/<year>NDn.pdf`); see the per-case PDF signature
block captured 2026-06-22.

Two shapes:
  - APPEND  : DB body ends at the dateline `[¶N] Dated at Bismarck…`; the panel
              paragraph `[¶N+1]` was dropped. Append it.
  - INSERT  : DB kept a trailing participation/surrogate note but dropped the
              `[¶N]` majority panel that belongs immediately before it. Insert.

16311 (Rustad, 2014 ND 148) is deliberately NOT here — its DB "Sandstrom concurs"
vs the PDF text layer's "Crothers concurs" is a genuine divergence pending an
independent read.

Dry-run by default. `--apply` backs up the DB, writes, and logs changelog batch
`restore-sig-truncation-oneoffs-2026-06-22` (revertible via `cleanup revert`).
"""
from __future__ import annotations

import argparse
import re
import shutil
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "opinions.db"
BATCH = "restore-sig-truncation-oneoffs-2026-06-22"

# Each plan: oid, mode, anchor (exact unique substring in text_content), panel
# lines (PDF-verified), and for 16366 a note repair (garbled marker + OCR split).
PLANS = [
    # ---- APPENDS (panel after the dateline; no trailing note) ----
    dict(oid=12600, cite="1998 ND 58", mode="append",
         anchor="[¶ 15] Dated at Bismarck, North Dakota, this 10th day of March, 1998.",
         marker="[¶ 16]",
         panel=["Gerald W. VandeWalle, C.J.", "Herbert L. Meschke",
                "William A. Neumann", "Dale V. Sandstrom", "Mary Muehlen Maring"]),
    dict(oid=12657, cite="1998 ND 98", mode="append",
         anchor="[¶ 12] Dated at Bismarck, North Dakota, this 29th day of April, 1998.",
         marker="[¶ 13]",
         panel=["Gerald W. VandeWalle, C.J.", "Dale V. Sandstrom",
                "William A. Neumann", "Mary Muehlen Maring", "Herbert L. Meschke"]),
    dict(oid=12722, cite="1998 ND 136", mode="append",
         anchor="[¶ 8] Dated at Bismarck, North Dakota, this 1st day of July, 1998.",
         marker="[¶ 9]",
         panel=["Gerald W. VandeWalle, Chief Justice", "Herbert L. Meschke, Justice",
                "Mary Muehlen Maring, Justice", "William A. Neumann, Justice",
                "Dale V. Sandstrom, Justice"]),
    # ---- INSERTS (panel before the surviving trailing note) ----
    dict(oid=12726, cite="1998 ND 143", mode="insert_before",
         anchor="RICHARD W. GROSZ, District Judge, sitting in place of MESCHKE, J., disqualified.",
         marker="[¶ 10]",
         panel=["Dale V. Sandstrom", "William A. Neumann", "Mary Muehlen Maring",
                "Richard W. Grosz, D.J.", "Gerald W. VandeWalle, C.J."]),
    dict(oid=13127, cite="2000 ND 79", mode="insert_before",
         anchor="The Honorable CAROL RONNING KAPSNER disqualified herself subsequent to oral argument and did not participate in this decision.",
         marker="[¶ 27]",
         panel=["Gerald W. VandeWalle, C.J.", "Dale V. Sandstrom",
                "William A. Neumann", "Mary Muehlen Maring"]),
    dict(oid=13288, cite="2000 ND 225", mode="insert_before",
         anchor="The Honorable RICHARD W. GROSZ, D.J., sitting in place of KAPSNER, J., disqualified.",
         marker="[¶ 27]",
         panel=["Gerald W. VandeWalle, C.J.", "Dale V. Sandstrom", "William A. Neumann",
                "Mary Muehlen Maring", "Richard W. Grosz, D.J."]),
    dict(oid=16366, cite="2014 ND 201", mode="insert_before",
         anchor="[1126] The Honorable BENNY A. GRAFF, S.J., sitting in place of KAPS-NER, J., disqualified.",
         note_fix="[¶ 26] The Honorable BENNY A. GRAFF, S.J., sitting in place of KAPSNER, J., disqualified.",
         marker="[¶ 25]",
         panel=["Dale V. Sandstrom", "Daniel J. Crothers", "Lisa Fair McEvers",
                "Benny A. Graff, S.J.", "Gerald W. VandeWalle, C.J."]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = sqlite3.connect(str(DB))

    planned, errors = [], []
    for p in PLANS:
        tc = conn.execute("SELECT text_content FROM opinions WHERE id=?", (p["oid"],)).fetchone()[0]
        if tc.count(p["anchor"]) != 1:
            errors.append((p["oid"], f"anchor count = {tc.count(p['anchor'])} (need 1)")); continue
        block = p["marker"] + " " + "\n".join(p["panel"])
        if p["mode"] == "append":
            new = tc.replace(p["anchor"], p["anchor"] + "\n\n" + block)
        else:  # insert_before — optionally repair the trailing note text too
            tail = p.get("note_fix", p["anchor"])
            new = tc.replace(p["anchor"], block + "\n\n" + tail)
        # sanity: every panel surname must now be present; length grew sensibly
        if new == tc or len(new) <= len(tc):
            errors.append((p["oid"], "no-op splice")); continue
        planned.append((p, tc, new))

    print(f"=== {'APPLY' if args.apply else 'DRY-RUN'} — planned {len(planned)} / errors {len(errors)} ===\n")
    for p, tc, new in planned:
        print(f"--- {p['cite']} (oid {p['oid']}) [{p['mode']}] ---")
        print("  insert:", " | ".join(p["panel"]))
        if "note_fix" in p:
            print("  note repaired:", p["note_fix"])
        # show the new tail
        print("  new tail:")
        for ln in new.rstrip().splitlines()[-(len(p["panel"]) + 3):]:
            print("    ", ln)
        print()
    for oid, why in errors:
        print(f"  ERROR oid {oid}: {why}")

    if args.apply:
        if errors:
            print("\nABORT: errors present; fix before applying."); conn.close(); return
        bak = DB.with_name(DB.name + ".bak-sig-oneoffs-2026-06-22")
        if not bak.exists():
            shutil.copy2(DB, bak); print(f"backup → {bak.name}")
        for p, tc, new in planned:
            conn.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                         "VALUES (?,?,?,?,?)", (BATCH, p["oid"], "text_content", tc, new))
            conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, p["oid"]))
        conn.commit()
        print(f"\nAPPLIED {len(planned)}; logged batch {BATCH}")
    conn.close()


if __name__ == "__main__":
    main()
