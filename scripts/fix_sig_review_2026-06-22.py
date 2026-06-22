"""REVIEW cohort — multi-opinion signature restorations, 2026-06-22.

Classified REVIEW (not auto-fixed) because the DB kept a SEPARATE writing (a
"concur in the result" notation, or an orphan name) while dropping the `[¶N]`
MAJORITY panel that precedes it — so phase-4's divergence guard
(DB-trailing-justice ⊆ source-panel) correctly refused them: the surviving
concurring justices are DISJOINT from the dropped majority.

With every court PDF signature block in hand the structure is unambiguous. Two
plan types:
  INS  (label, marker, [panel lines], anchor):  insert "[¶ marker] " + panel
        immediately before `anchor` (the surviving concurrence, which starts
        with "\\n\\n"). anchor is preserved.
  REPL (label, old, new):  explicit replacement (orphan last-name → full panel;
        or a case where the concurrence notation was itself dropped).

A guard verifies every inserted surname appears in the court PDF and each anchor
is unique; a transcription error fails the dry-run.

NOT here: 13291 (false positive — DB already complete, source `[¶478]` is a
garbled dup marker); 13109 / 15475 (partial-panel anomalies — DB holds a 2–3
name West-style fragment of a fuller panel; need a REPLACE + independent check).

Dry-run by default. `--apply` backs up the DB, writes, logs `restore-sig-review-2026-06-22`.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sqlite3
import subprocess
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "opinions.db"
REFS = Path.home() / "refs" / "nd" / "opin"
BATCH = "restore-sig-review-2026-06-22"

# INS: oid -> (label, marker, [panel lines], anchor-starting-with-\n\n)
INS = {
    12743: ("1998 ND 161", "12",
            ["Mary Muehlen Maring", "Herbert L. Meschke", "Georgia Dawson, D.J.", "Gerald W. VandeWalle, C.J."],
            "\n\nGEORGIA DAWSON, District Judge, sitting in place of SANDSTROM"),
    13665: ("2002 ND 170", "14",
            ["William A. Neumann", "Mary Muehlen Maring", "Carol Ronning Kapsner", "Gerald W. VandeWalle, C.J."],
            "\n\nI concur in the result.\n\nDALE V. SANDSTROM, J."),
    14152: ("2004 ND 226", "20",
            ["Carol Ronning Kapsner", "Mary Muehlen Maring", "William A. Neumann", "Gerald W. VandeWalle, C.J."],
            "\n\nI concur in the result. DALE V. SANDSTROM."),
    14816: ("2007 ND 139", "36",
            ["Mary Muehlen Maring", "Carol Ronning Kapsner", "Gerald W. VandeWalle, C.J."],
            "\n\nDALE V. SANDSTROM and DANIEL J. CROTHERS, JJ., concur in the result."),
    15371: ("2010 ND 38", "35",
            ["Carol Ronning Kapsner", "Dale V. Sandstrom", "Gerald W. VandeWalle, C.J."],
            "\n\nDANIEL J. CROTHERS and MARY MUEHLEN MARING, JJ., concur in the result."),
    15570: ("2011 ND 20", "29",
            ["Carol Ronning Kapsner", "Mary Muehlen Maring", "Gerald W. VandeWalle, C.J."],
            "\n\nDALE V. SANDSTROM and DANIEL J. CROTHERS, JJ., concur in the result."),
    15689: ("2011 ND 142", "18",
            ["Mary Muehlen Maring", "Dale V. Sandstrom", "Carol Ronning Kapsner", "Gerald W. VandeWalle, C.J."],
            "\n\nDANIEL J..CROTHERS, J., concurs in the result."),
    15739: ("2011 ND 216", "24",
            ["Mary Muehlen Maring", "Carol Ronning Kapsner", "Dale V. Sandstrom", "Gerald W. VandeWalle, C.J."],
            "\n\nDANIEL J. CROTHERS, J., concurs in the result."),
    15911: ("2012 ND 167", "30",
            ["Mary Muehlen Maring", "Carol Ronning Kapsner", "Gerald W. VandeWalle, C.J."],
            "\n\nDALE V. SANDSTROM and DANIEL J. CROTHERS, JJ., concur."),
    15913: ("2012 ND 168", "18",
            ["Mary Muehlen Maring", "Carol Ronning Kapsner", "Gerald W. VandeWalle, C.J."],
            "\n\nWe concur in the result. DALE V. SANDSTROM, and DANIEL J. CROTHERS, JJ., concur."),
    15951: ("2012 ND 228", "33",
            ["Mary Muehlen Maring", "Daniel J. Crothers", "Carol Ronning Kapsner", "Gerald W. VandeWalle, C.J."],
            "\n\nDALE V. SANDSTROM, J., concurs in the result."),
    16377: ("2014 ND 229", "28",
            ["Lisa Fair McEvers", "Daniel J. Crothers", "Carol Ronning Kapsner"],
            "\n\nWe concur in the result. GERALD W. VANDE WALLE, C.J., and DALE SANDSTROM, J."),
    16574: ("2015 ND 229", "21",
            ["Dale V. Sandstrom", "Lisa Fair McEvers", "Gerald W. VandeWalle, C.J."],
            "\n\nWe concur in the result, CAROL RONNING KAPSNER and DANIEL J. CROTHERS, JJ."),
}

# REPL: oid -> (label, old, new)
REPL = {
    15736: ("2011 ND 200",
            "ch. 234, § 5.\n\nDale V. Sandstrom",
            "ch. 234, § 5.\n\n[¶ 14] Daniel J. Crothers\nMary Muehlen Maring\nCarol Ronning Kapsner\n"
            "Gerald W. VandeWalle, C.J.\n\nI concur in the result.\nDale V. Sandstrom"),
    16901: ("2017 ND 107",
            "Gerald'W. VandeWalle, C.J.",
            "[¶ 17] Lisa Fair McEvers\nDaniel J. Crothers\nJerod E. Tufte\nCarol Ronning Kapsner\nGerald W. VandeWalle, C.J."),
    16927: ("2017 ND 119",
            "is reversed.\n\nGerald W. VandeWalle, C. J.",
            "is reversed.\n\n[¶ 18] Daniel J. Crothers\nLisa Fair McEvers\nCarol Ronning Kapsner\nJerod E. Tufte\nGerald W. VandeWalle, C.J."),
    16938: ("2017 ND 131",
            "35.1(a)(3).\n\nCarol Ronning Kapsner",
            "35.1(a)(3).\n\n[¶ 2] Gerald W. VandeWalle, C.J.\nJerod E. Tufte\nDaniel J. Crothers\nLisa Fair McEvers\nCarol Ronning Kapsner"),
}


def pdf_text(label):
    yr, n = re.match(r"(\d{4}) ND (\d+)", label).groups()
    p = REFS / "pdfs" / yr / f"{yr}ND{n}.pdf"
    if not p.exists():
        return None
    out = subprocess.run(["mutool", "draw", "-F", "txt", str(p)],
                         capture_output=True, text=True, timeout=60).stdout
    return re.sub(r"\s+", " ", out).lower()


def surname(line):
    # last token group that isn't a role suffix; used for PDF verification
    s = re.sub(r",?\s*(C\.J\.|D\.J\.|S\.J\.|J\.)$", "", line).strip()
    return s.split()[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = sqlite3.connect(str(DB))
    planned, errors = [], []

    def verify(oid, label, names, tc):
        pt = pdf_text(label)
        if pt is None:
            return "no PDF"
        miss = [s for s in names if s.lower() not in pt]
        return f"PDF missing {miss}" if miss else None

    for oid, (label, marker, panel, anchor) in INS.items():
        tc = conn.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        if tc.count(anchor) != 1:
            errors.append((oid, f"anchor count={tc.count(anchor)}")); continue
        names = [surname(l) for l in panel]
        v = verify(oid, label, names, tc)
        if v:
            errors.append((oid, v)); continue
        new = tc.replace(anchor, "\n\n[¶ " + marker + "] " + "\n".join(panel) + anchor)
        planned.append((oid, label, tc, new))

    for oid, (label, old, new_) in REPL.items():
        tc = conn.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        if tc.count(old) != 1:
            errors.append((oid, f"anchor count={tc.count(old)}")); continue
        names = [surname(l) for l in new_.splitlines() if re.search(r"[A-Z]\.|, C\.J\.|VandeWalle|McEvers|Tufte|Crothers|Kapsner|Sandstrom|Maring|Neumann", l) and "concur" not in l.lower() and "reversed" not in l and "35.1" not in l and "§" not in l]
        v = verify(oid, label, names, tc)
        if v:
            errors.append((oid, v)); continue
        new = tc.replace(old, new_)
        planned.append((oid, label, tc, new))

    print(f"=== {'APPLY' if args.apply else 'DRY-RUN'} — planned {len(planned)} / errors {len(errors)} ===\n")
    for oid, label, tc, new in sorted(planned):
        print(f"--- {oid} {label} ---")
        for ln in new.rstrip().splitlines()[-9:]:
            print("    ", ln)
        print()
    for oid, why in sorted(errors):
        print(f"  ERROR {oid}: {why}")

    if args.apply:
        if errors:
            print("\nABORT: errors present."); conn.close(); return
        bak = DB.with_name(DB.name + ".bak-sig-review-2026-06-22")
        if not bak.exists():
            shutil.copy2(DB, bak); print(f"backup → {bak.name}")
        for oid, label, tc, new in planned:
            conn.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value, authority) "
                         "VALUES (?,?,?,?,?,?)", (BATCH, oid, "text_content", tc, new,
                         f"court PDF {label} signature block"))
            conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
        conn.commit()
        print(f"\nAPPLIED {len(planned)}; logged batch {BATCH}")
    conn.close()


if __name__ == "__main__":
    main()
