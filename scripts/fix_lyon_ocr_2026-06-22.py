"""Surgical OCR fix for Lyon v. Ford Motor Co., 2000 ND 12 (opinion id 13068).

Nine character-level OCR garbles in the stored CL/West-OCR text, each verified
against the clean Westlaw `.doc` (Lyon v Ford Motor Co.doc, 604 N.W.2d 453) and
each a unique single occurrence. Preserves the opinion's structure — notably the
standalone ` 1` footnote-call line that the pinpoint parser uses to link
footnote 1 back to ¶ 7 (do NOT collapse it to `judgment.1`).

Dry-run by default; ``--apply`` writes and logs one changelog row per token.
Revertible via ``python -m ndcourts_mcp.cleanup revert lyon-ocr-2026-06-22``.
"""
import argparse
import sqlite3
from datetime import datetime, timezone

OPINION_ID = 13068
BATCH = "lyon-ocr-2026-06-22"
AUTHORITY = "Westlaw: Lyon v Ford Motor Co.doc (604 N.W.2d 453)"

# (garbled, correct) — each must occur exactly once in text_content.
FIXES = [
    ("satisfaclion", "satisfaction"),
    ("aecrudble", "accruable"),
    ("supersede-as", "supersedeas"),
    ("Scholl-meyer", "Schollmeyer"),
    ("Cla'rys", "Clarys"),
    ("N.D.RApp.P.", "N.D.R.App.P."),
    ("$10,-360.84", "$10,360.84"),
    ("be- enforced", "be enforced"),
    ("\n\nIll\n\n", "\n\nIII\n\n"),  # section heading III (between ¶17 and ¶18)
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    text = con.execute(
        "SELECT text_content FROM opinions WHERE id=?", (OPINION_ID,)
    ).fetchone()[0]

    new = text
    rows = []
    for garbled, correct in FIXES:
        n = new.count(garbled)
        if n != 1:
            raise SystemExit(f"ABORT: {garbled!r} occurs {n} times (expected 1) — not safe.")
        new = new.replace(garbled, correct)
        rows.append((garbled, correct))
        label = garbled.replace("\n", "\\n")
        print(f"  {label!r:24} -> {correct!r}")

    print(f"\n{len(rows)} corrections; text {len(text)} -> {len(new)} chars")
    if not args.apply:
        print("DRY-RUN — re-run with --apply to write.")
        return

    ts = datetime.now(timezone.utc).isoformat()
    con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, OPINION_ID))
    con.executemany(
        "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, "
        "new_value, authority) VALUES (?,?,?,?,?,?,?)",
        [(ts, BATCH, OPINION_ID, "text_content", g, c, AUTHORITY) for g, c in rows],
    )
    con.commit()
    print(f"APPLIED + logged {len(rows)} changelog rows (batch {BATCH}).")


if __name__ == "__main__":
    main()
