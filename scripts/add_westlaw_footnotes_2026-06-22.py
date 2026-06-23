"""Restore the 2 substantive court footnotes dropped by the Westlaw ingest.

`_parse_westlaw_doc` cut opinions at "All Citations", dropping the trailing
Footnotes section (see TODO / audit_westlaw_footnotes). A corpus-wide audit
(triage/westlaw-footnote-audit.tsv) found only TWO genuinely substantive
numbered footnotes lost (the other 104 are West editorial — "Reported in full
in …", bare parallel cites, "Rehearing pending."). Both are pre-1953 (no [¶]
markers), so the value is retention; verbatim from the Westlaw `.doc`.

Appends the footnote body in authentic ` N\n\n<body>` form. Dry-run by default;
``--apply`` writes + logs one ``text_content.footnote_add`` changelog row each.
"""
import argparse
import sqlite3
from datetime import datetime, timezone

BATCH = "westlaw-footnote-restore-2026-06-22"

# (opinion_id, footnote number, verbatim body, .doc authority, call anchor)
FOOTNOTES = [
    (2222, "1",
     "Note.-Appellant states that Ransom county petition for drain was filed "
     "May 28, 1906. Exhibit E, the copy before this court, the original not "
     "being here, shows the date May 28, 1905.",
     "N.D./43/0156", "filed May 28, 1905,1 and another"),
    (4906, "1",
     "In the Senate Chapter 161, Laws of 1937 was passed by a unanimous vote "
     "(Senate Journal, 1937, p. 274), and in the House of Representatives the "
     "measure was passed by a vote of 95 to 1. (House Journal, 1937 pp. 578-579).",
     "N.D./69/0290", "lawmakers, almost unanimously1, determined"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    for oid, num, body, doc, anchor in FOOTNOTES:
        text = con.execute(
            "SELECT text_content FROM opinions WHERE id=?", (oid,)
        ).fetchone()[0]
        if anchor.replace(" ", "") not in text.replace(" ", ""):
            raise SystemExit(f"ABORT {oid}: call anchor not found — wrong opinion?")
        if body[:30].replace(" ", "") in text.replace(" ", ""):
            print(f"  {oid}: body already present — skipping")
            continue
        addition = f"\n\n{num}\n\n{body}"
        new = text + addition
        print(f"  {oid}: +{len(addition)} chars  (footnote {num}: {body[:55]}…)")
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, "
                "old_value, new_value, authority) VALUES (?,?,?,?,?,?,?)",
                (ts, BATCH, oid, "text_content.footnote_add",
                 f"(footnote {num} body absent — dropped at Westlaw ingest)",
                 addition.strip(), f"Westlaw: {doc}.doc"),
            )
    if args.apply:
        con.commit()
        print(f"APPLIED + logged (batch {BATCH}).")
    else:
        print("DRY-RUN — re-run with --apply.")


if __name__ == "__main__":
    main()
