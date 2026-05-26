"""Repair mojibake'd markers in opinion 13240 (Johnson v. Johnson, 2000 ND 170).

text_content had its UTF-8 special characters mis-decoded through a Thai (CP874)
codec at some ingest: the byte sequences for the analyzer's [¶N] markers, § signs,
and em-dashes became Thai glyphs + stray control bytes. The counts match the
pristine on-disk source markdown/2000/2000ND170.md exactly:

  'ถ' (U+0E16) x212  ->  '¶'  (file has 212 ¶)
  'ง' (U+0E07) x75   ->  '§'  (file has 75 §)
  'โ\x80\x94' (U+0E42 U+0080 U+0094) x9 -> '—' em-dash (file has 9 —, = UTF-8 E2 80 94)

After repair every codepoint in text_content is ASCII or in the legit set.

NOTE (separate, NOT fixed here): 13240's text_content is ~237 KB = the ND
markdown (~118 KB, the ¶-marked half repaired here) concatenated with the NW2d
OCR copy (~119 KB). That double-source concatenation is logged as its own TODO;
de-duplicating safely needs a re-ingest, not a blind truncation.

Run with --apply to write; default dry-run. Logged to changelog for revert.
"""
from __future__ import annotations
import argparse, sqlite3

BATCH = "demangle-13240-2026-05-26"
OID = 13240
REPLACEMENTS = [("โ", "—"),  # em-dash sequence first (3->1)
                ("ถ", "¶"),               # ถ -> ¶
                ("ง", "§")]               # ง -> §


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = sqlite3.connect("opinions.db")
    old = conn.execute("SELECT text_content FROM opinions WHERE id=?", (OID,)).fetchone()[0]
    new = old
    for frm, to in REPLACEMENTS:
        n = new.count(frm)
        new = new.replace(frm, to)
        print(f"  {frm!r} -> {to!r}: {n} replaced")
    leftover = sorted({ch for ch in new if ord(ch) > 127
                       and ch not in set("‘’“”—–§¢¶"
                                         " •°«»…")
                       and not (0x00C0 <= ord(ch) < 0x0100)})
    print(f"  leftover non-legit non-ascii chars: {[hex(ord(c)) for c in leftover]}")
    assert old != new, "no change?"
    if args.apply:
        conn.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                     "VALUES (?,?, 'text_content', ?, ?)",
                     (BATCH, OID, f"len={len(old)} (mojibake)", f"len={len(new)} (demangled)"))
        conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, OID))
        conn.commit()
        print("APPLIED")
    else:
        print("DRY RUN")
    conn.close()


if __name__ == "__main__":
    main()
