"""MARKER_GARBLED cohort — final 8, resolved 2026-06-22.

Heterogeneous despite the shared label. Each plan is a list of exact-string
replacements (asserted unique), verified against the court PDF and, where the
PDF text layer was itself wrong/ambiguous, against West / CourtListener
(sourced from the court .wpd):

  13182  2000 ND 121  garbled marker `[¶ *11]` → `[¶ 11]` (page-break `*`). text complete.
  13881  2003 ND 156  garbled marker `[1123]` → `[¶ 23]`. text complete (double-Neumann is in source).
  15214  2009 ND 111  participation note lacks its `[¶ 8]` marker — add it. text complete.
  17102  2017 ND 289  dissent signature dropped "VandeWalle, C.J." + `[¶36]` marker — prepend.
  15060  2008 ND 184  dropped the `[¶27]` MAJORITY block (kept the separate `[¶15]` block).
                       West/CL op 898372: "[¶27] VANDE WALLE C.J., MARING, SANDSTROM and KAPSNER, JJ., concur."
  13580  2002 ND 86   dropped the `[¶40]` panel; note mislabeled `[¶40]` → renumber `[¶41]`, insert panel.
  15550  2010 ND 236  dropped the `[¶32]` panel; note mislabeled `[¶32]` → renumber `[¶33]`, insert panel.

NOT fixed: 17858 (2021 ND 144) — FALSE POSITIVE. DB has the complete `[¶14]`
panel (Jensen C.J./VandeWalle/Crothers/McEvers/Tufte); its paragraph numbering
just runs one behind the PDF (PDF `[¶15]`). No signature is missing. Flag it on
the sigscan baseline when promoting the invariant.

Dry-run by default. `--apply` backs up the DB, writes, logs batch
`fix-marker-garbled-2026-06-22`.
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "opinions.db"
BATCH = "fix-marker-garbled-2026-06-22"

# oid -> (note, [(old, new), ...]); each old must occur exactly once.
PLANS = {
    13182: ("garbled marker [¶ *11]*→[¶ 11] (two stray page-break asterisks)",
            [("[¶ *11]*DALE V. SANDSTROM", "[¶ 11] DALE V. SANDSTROM")]),
    13881: ("garbled marker [1123]→[¶ 23]",
            [("[1123]", "[¶ 23]")]),
    15214: ("add [¶ 8] marker to participation note",
            [("\n\nThe Honorable DALE V. SANDSTROM, being unavoidably absent",
              "\n\n[¶ 8] The Honorable DALE V. SANDSTROM, being unavoidably absent")]),
    17102: ("dissent sig: prepend [¶ 36] VandeWalle, C.J.",
            [("goals of ICWA.\n\nLisa Fair McEvers",
              "goals of ICWA.\n\n[¶ 36] Gerald W. VandeWalle, C.J.\nLisa Fair McEvers")]),
    15060: ("insert dropped [¶ 27] majority block (West/CL-verified)",
            [("affirmed.\n\n*775\n\n [¶ 15] GERALD",
              "affirmed.\n\n[¶ 27] GERALD W. VANDE WALLE, C.J., MARY MUEHLEN MARING, "
              "DALE V. SANDSTROM and CAROL RONNING KAPSNER, JJ., concur.\n\n*775\n\n [¶ 15] GERALD")]),
    13580: ("insert dropped [¶ 40] panel; renumber note →[¶ 41]",
            [("[¶ 40] The Honorable WILLIAM F. HODNY",
              "[¶ 40] Mary Muehlen Maring\nWilliam A. Neumann\nDale V. Sandstrom\n"
              "William F. Hodny, S.J.\nGerald W. VandeWalle, C.J.\n\n"
              "[¶ 41] The Honorable WILLIAM F. HODNY")]),
    15550: ("insert dropped [¶ 32] panel; renumber note →[¶ 33]",
            [("[¶ 32] The Honorable DONOVAN JOHN FOUGHTY",
              "[¶ 32] Daniel J. Crothers\nMary Muehlen Maring\nRichard L. Hagar, D.J.\n"
              "Donovan John Foughty, D.J.\nGerald W. VandeWalle, C.J.\n\n"
              "[¶ 33] The Honorable DONOVAN JOHN FOUGHTY")]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = sqlite3.connect(str(DB))

    planned, errors = [], []
    for oid, (note, reps) in PLANS.items():
        tc = conn.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        new = tc
        ok = True
        for old, repl in reps:
            if new.count(old) != 1:
                errors.append((oid, f"anchor {old[:30]!r} count={new.count(old)}")); ok = False; break
            new = new.replace(old, repl)
        if not ok:
            continue
        if new == tc:
            errors.append((oid, "no-op")); continue
        planned.append((oid, note, tc, new))

    print(f"=== {'APPLY' if args.apply else 'DRY-RUN'} — planned {len(planned)} / errors {len(errors)} ===\n")
    for oid, note, tc, new in planned:
        print(f"--- {oid}: {note} ---")
        print("  new tail:")
        for ln in new.rstrip().splitlines()[-7:]:
            print("    ", ln)
        print()
    for oid, why in errors:
        print(f"  ERROR {oid}: {why}")

    if args.apply:
        if errors:
            print("\nABORT: errors present."); conn.close(); return
        bak = DB.with_name(DB.name + ".bak-marker-garbled-2026-06-22")
        if not bak.exists():
            shutil.copy2(DB, bak); print(f"backup → {bak.name}")
        for oid, note, tc, new in planned:
            conn.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value, authority) "
                         "VALUES (?,?,?,?,?,?)", (BATCH, oid, "text_content", tc, new, note))
            conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
        conn.commit()
        print(f"\nAPPLIED {len(planned)}; logged batch {BATCH}")
    conn.close()


if __name__ == "__main__":
    main()
