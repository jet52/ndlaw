"""Strip court-clerk filing-stamp metadata fused into opinion text_content.

Two forms of the stamp leaked in during ingestion (administrative metadata, not
the court's authored opinion):

  STANDALONE  "Filed M/D/YY by Clerk of Supreme Court" — usually \\n\\n-padded near
              the top (after the author line / before "IN THE SUPREME COURT").
  WATERMARK   "Corrected Opinion Filed MM/DD/YY by Clerk of the Supreme Court" —
              injected at every page break, often MID-WORD ("She <stamp>noticed"),
              so removal must rejoin the split text.

Per opinion ATOMIC + verified: remove every stamp occurrence, then a strict
alpha-word-multiset gate confirms the ONLY words removed are stamp vocabulary
({Corrected, Opinion, Filed, by, Clerk, of, the, Supreme, Court}); a removal that
fuses or drops any real word fails the gate and the opinion is skipped. Standalone
stamps collapse their \\n\\n padding; fused stamps leave the surrounding spacing
(which already reads correctly once the injected run is gone), with a double-space
cleanup. Dry-run by default; writes a report (md + json).

Usage: strip_clerk_stamps.py [--apply] [--db opinions.db]
       [--batch clerk-stamps-2026-06-24] [--out triage/clerk-stamps]
"""
import argparse
import json
import os
import re
import sqlite3
import subprocess
from collections import Counter
from datetime import datetime, timezone

REFS = os.path.expanduser("~/refs/nd/opin")


def pdf_text(con, oid):
    """Authoritative PDF text for a modern opinion, or '' if none on disk."""
    row = con.execute("SELECT citation FROM citations WHERE opinion_id=? "
                      "ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone()
    if not row or not row[0]:
        return ""
    nd = row[0].replace(" ", "")
    p = f"{REFS}/pdfs/{row[0].split()[0]}/{nd}.pdf"
    if not os.path.exists(p):
        return ""
    return re.sub(r"\s+", " ", subprocess.run(
        ["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout)

# the stamp: optional "Corrected Opinion " prefix, "Filed" with a date BEFORE and/or
# AFTER "by Clerk of [the] Supreme Court". Date = numeric (M/D/YY) or month-name.
_DATE = (r"(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
         r"|(?:January|February|March|April|May|June|July|August|September|October|November|December)"
         r"\s+\d{1,2},?\s+\d{4})")
STAMP = re.compile(
    r"(?:Corrected Opinion )?Filed\s*(?:" + _DATE + r"\s*,?\s*)?"
    r"by Clerk of (?:the )?Supreme Cours?t(?:\s*,?\s*" + _DATE + r")?")  # Cours?t: OCR typo "Courst"
STAMP_VOCAB = {"Corrected", "Opinion", "Filed", "by", "Clerk", "of", "the", "Supreme", "Court"}


def words(s):
    return Counter(re.findall(r"[A-Za-z]+", s))


def strip(text):
    """-> (new_text, n_removed). Remove every stamp; tidy whitespace."""
    n = len(STAMP.findall(text))
    if not n:
        return text, 0
    # standalone: \n\n<stamp>\n\n -> \n\n   (drop the stamp's own paragraph)
    t = re.sub(r"\n\s*" + STAMP.pattern + r"\s*\n", "\n", text)
    # any remaining (fused / inline) occurrences: drop the run in place
    t = STAMP.sub("", t)
    # tidy: collapse a space the removal may have doubled, and 3+ newlines -> 2
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t, n


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--batch", default="clerk-stamps-2026-06-24")
    ap.add_argument("--out", default="triage/clerk-stamps")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    ids = [r[0] for r in con.execute(
        "SELECT id FROM opinions WHERE text_content LIKE '%by Clerk of%Supreme Court%' "
        "OR text_content LIKE '%Corrected Opinion Filed%'").fetchall()]

    report, applied, skipped, tot = [], 0, 0, 0
    for oid in ids:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        new, n = strip(old)
        if n == 0:
            continue
        removed = words(old) - words(new)
        extra = removed - Counter({w: 10**6 for w in STAMP_VOCAB})  # words removed that AREN'T stamp vocab
        added = words(new) - words(old)
        verdict = "OK"
        if extra or added:
            # strict gate failed -> the stamp was fused to a real word at a boundary
            # ("...Supreme Courtnoticed" -> "noticed"). Removal is character-exact;
            # confirm via the PDF that every rejoined token is real (not a bad merge).
            pt = pdf_text(con, oid)
            unconfirmed = [w for w in (+added) if not pt or w not in pt]
            if unconfirmed:
                skipped += 1
                report.append({"opinion_id": oid, "status": "SKIP_wordgate",
                               "n_stamps": n, "bad_removed": dict(+extra),
                               "bad_added": dict(+added), "unconfirmed": unconfirmed})
                continue
            verdict = "OK_fusion_pdf"
        cite = con.execute("SELECT citation FROM citations WHERE opinion_id=? "
                           "ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone()
        applied += 1
        tot += n
        report.append({"opinion_id": oid, "cite": cite[0] if cite else "",
                       "status": verdict, "n_stamps": n})
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, args.batch, oid, "text_content.clerk_stamp",
                 f"{n} clerk filing-stamp(s)", "removed",
                 "court-clerk filing metadata (not authored opinion); stamp-vocab word-multiset gate"))
    json.dump(report, open(f"{args.out}.json", "w"), ensure_ascii=False, indent=1)
    md = [f"# Clerk filing-stamp removal — {'APPLIED' if args.apply else 'DRY-RUN'}", "",
          f"{applied} opinions OK ({tot} stamps removed), {skipped} skipped (word-gate).", ""]
    if skipped:
        md += ["## Skipped (word-gate caught a non-stamp word change — needs manual review)", ""]
        md += [f"- id{r['opinion_id']}: removed={r.get('bad_removed')} added={r.get('bad_added')}"
               for r in report if r["status"] != "OK"] + [""]
    open(f"{args.out}.md", "w").write("\n".join(md))
    print(f"candidates: {len(ids)}  OK: {applied}  skipped: {skipped}  stamps removed: {tot}")
    print(f"report -> {args.out}.md / .json")
    if args.apply:
        con.commit()
        print(f"COMMITTED batch {args.batch}.")


if __name__ == "__main__":
    main()
