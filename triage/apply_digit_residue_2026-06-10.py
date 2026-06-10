"""Residual digit fixes flagged by verifiers during the corpus batch —
context-anchored replacements, each print-verified (crops on file):

* 15869 ¶8 (2012 ND 138): print reads "State v. Jones, 2011 ND 234, ¶ 8,
  812 N.W.2d 484" (/tmp/jones_hit0.png; the court's print itself miscites
  Jones, whose true parallel is 817 N.W.2d 313 — preserve the print
  verbatim). DB read "817. N.W.2d 313"; the corpus batch fixed 817->812;
  this completes 313->484 and drops the stray analyzer period.
* 15864 ¶29 (2012 ND 144): print "Wentz, 103 N.W.2d at 253-54"
  (spot-check crop 382); DB volume read 108. Single flip the pass-2
  pairing missed (token-presence guard).
* 16283 ¶7 (2014 ND 37): print "N.D.C.C. § 39-20-05(3)" (crop 459);
  DB section read 89-20-05.

Dry-run default; --apply writes text_content + markdown, changelog batch
digit-flips-residue-2026-06-10."""
import re, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.db import log_change, log_provenance

BATCH = "digit-flips-residue-2026-06-10"
REFS = Path.home() / "refs/nd/opin"
apply = "--apply" in sys.argv
conn = sqlite3.connect("opinions.db")

FIXES = [  # (oid, old_fragment, new_fragment, authority)
    (15869, "812. N.W.2d 313 (quotation omitted)", "812 N.W.2d 484 (quotation omitted)",
     "print verified (/tmp/jones_hit0 crop): court miscites Jones as 812 N.W.2d 484 (true 817 N.W.2d 313); preserved verbatim"),
    (15864, "*Wentz,* 108 N.W.2d at", "*Wentz,* 103 N.W.2d at",
     "print verified (crop 382): Wentz, 103 N.W.2d at 253-54"),
    (16283, "89-20-05(", "39-20-05(",
     "print verified (crop 459): N.D.C.C. § 39-20-05(3)"),
]

n = 0
for oid, old, new, auth in FIXES:
    text, sp = conn.execute("SELECT text_content, source_path FROM opinions WHERE id=?", (oid,)).fetchone()
    c = text.count(old)
    print(f"oid{oid}: fragment count={c} | {old!r}")
    if c != 1:
        print("  SKIP (count != 1)")
        continue
    n += 1
    if apply:
        conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (text.replace(old, new), oid))
        log_change(conn, BATCH, oid, "text_content.digit_flip", old, new, authority=auth)
        p = REFS / sp
        if p.exists():
            md = p.read_text()
            if md.count(old) == 1:
                p.write_text(md.replace(old, new))
print(f"{'APPLIED' if apply else 'DRY RUN'}: {n} fixes")
if apply:
    log_provenance(conn, "digit-flips-residue", command="triage/apply_digit_residue_2026-06-10.py --apply",
                   rows_affected=n, notes=f"batch {BATCH}; verifier-flagged residue, print-verified")
    conn.commit()
