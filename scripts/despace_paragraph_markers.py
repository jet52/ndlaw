#!/usr/bin/env python3
"""Normalize in-text paragraph markers '[¶ N]' -> '[¶N]' corpus-wide.

The North Dakota Supreme Court prints paragraph markers with NO space inside the brackets
('[¶1]'), verified against the bound PDFs (e.g. 1997 ND 7, 2008 ND 115). The spaced form
'[¶ N]' is an extraction artifact — proven by 1,360 opinions that carry BOTH forms within a
single document (no one mixes the two deliberately). This collapses the space(s) between ¶ and
the paragraph number.

Only touches markers where a DIGIT follows (r'\\[¶ +\\d'), so OCR-garbled forms ('[¶ IB]',
'[¶ ll]', '[¶ l]' — digit misreads) are left for the separate OCR-digit pass. Marker COUNT is
invariant (only spaces removed). Dry-run by default.

Usage: despace_paragraph_markers.py [--apply] [--db opinions.db]
"""
import sqlite3, re, sys, datetime

PAT = re.compile(r'\[¶ +(\d)')
BATCH = "despace-paragraph-markers-2026-06-25"


def main():
    apply = "--apply" in sys.argv
    db = sys.argv[sys.argv.index("--db") + 1] if "--db" in sys.argv else "opinions.db"
    con = sqlite3.connect(db)
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    rows = con.execute("SELECT id, text_content FROM opinions WHERE text_content LIKE '%[¶ %'").fetchall()
    changed = 0
    total_markers = 0
    for oid, t in rows:
        new, n = PAT.subn(r'[¶\1', t)
        if n == 0:
            continue
        # invariant: only spaces removed; every paragraph marker preserved, length shrinks
        assert len(re.findall(r'\[¶\s*\d', t)) == len(re.findall(r'\[¶\s*\d', new))
        assert new.replace(' ', '') == t.replace(' ', '') and len(new) < len(t)
        changed += 1
        total_markers += n
        if apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, BATCH, oid, "text_content.paragraph_marker_despace",
                 f"{n} '[¶ N]' markers", f"{n} '[¶N]' markers",
                 "normalize in-text paragraph markers '[¶ N]'->'[¶N]'; court prints no-space "
                 "(image-verified 1997 ND 7, 2008 ND 115); spacing was an extraction artifact; conf=high"))
        elif changed <= 5:
            print(f"  id{oid}: {n} markers despaced")
    if apply:
        con.commit()
    print(f"\n{changed} opinions, {total_markers} markers despaced ({'APPLIED' if apply else 'dry-run'})")


if __name__ == "__main__":
    main()
