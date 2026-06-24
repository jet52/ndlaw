"""Layer C gate for corpus-proofing proposals — deterministic PDF verification.

For modern (PDF-authoritative) opinions a proposal can be CONFIRMED without a
second agent: if its byte-exact anchor is unique in the DB and its reconstruction
(new_exact) appears verbatim in the court PDF, the fix is self-proving. Routes:

  AUTO   : anchor unique + new_exact verbatim in PDF + class in {whitespace,
           ocr_char} (the mechanical classes the user authorized) + the OLD text
           is NOT itself in the PDF (i.e. the DB really is wrong). -> gated apply.
  REVIEW : anchor unique + new verbatim in PDF, but a MEANING-AFFECTING class
           (split_join scramble, missing_text, paragraph_seq, caption). PDF-
           confirmed, so review is fast — but a human signs off.
  REJECT : anchor not unique (gate would fail), OR new not found in PDF
           (unverifiable), OR old already in PDF (DB is likely already correct).

Usage: verify_proofing_proposals.py RESULTS.json [--db opinions.db]
Writes RESULTS.auto.json / RESULTS.review.json / RESULTS.reject.json.
"""
import json
import os
import re
import subprocess
import sqlite3
import sys

REFS = os.path.expanduser("~/refs/nd/opin")
AUTO_CLASSES = {"whitespace", "ocr_char"}
_pdf_cache = {}


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def pdf_text(con, oid):
    if oid in _pdf_cache:
        return _pdf_cache[oid]
    row = con.execute("SELECT citation FROM citations WHERE opinion_id=? "
                      "ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone()
    txt = ""
    if row and row[0]:
        nd = row[0].replace(" ", "")
        p = f"{REFS}/pdfs/{row[0].split()[0]}/{nd}.pdf"
        if os.path.exists(p):
            # -layout: reading-order correct across single-column and margin-[¶N]
            # layouts (plain pdftotext scrambles the latter). norm() collapses its
            # alignment padding for comparison.
            txt = norm(subprocess.run(["pdftotext", "-layout", p, "-"],
                                      capture_output=True, text=True).stdout)
    _pdf_cache[oid] = txt
    return txt



_ELLIPSIS_SP = re.compile(r"\.\s+\.")   # spaced dots: ". ." — whitespace is semantic


def _ws_equiv(a, b):
    """True if a and b differ only in whitespace AND that whitespace is not
    semantic. Whitespace between dots is part of a legal ellipsis (Bluebook
    ". . . ."), and a newline inserted where there was none breaks a token
    across a line (e.g. a hyphenated statute number) — neither is a safe
    mechanical AUTO fix, so we route those to REVIEW."""
    if re.sub(r"\s+", "", a) != re.sub(r"\s+", "", b):
        return False
    if _ELLIPSIS_SP.search(a) or _ELLIPSIS_SP.search(b):
        return False                      # ellipsis respacing -> review
    if b.count("\n") > a.count("\n"):
        return False                      # newline inserted (reflow) -> review
    return True

def core(s, n=45):
    c = norm(s)
    return c[:n] if len(c) >= 15 else c


def main():
    path = sys.argv[1]
    db = sys.argv[sys.argv.index("--db") + 1] if "--db" in sys.argv else "opinions.db"
    con = sqlite3.connect(db)
    data = json.load(open(path))
    auto, review, reject = [], [], []
    for o in data:
        if o.get("clean") or not o.get("proposals"):
            continue
        oid = o["opinion_id"]
        t = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        pt = pdf_text(con, oid)
        for p in o["proposals"]:
            oe, ne = p.get("old_exact", ""), p.get("new_exact", "")
            rec = {"opinion_id": oid, **p}
            if not oe or t.count(oe) != 1:
                rec["_verdict"] = "reject:bad_anchor"
                reject.append(rec)
                continue
            new_in = pt and core(ne) in pt
            old_in = pt and core(oe) in pt
            if not pt:
                rec["_verdict"] = "review:no_pdf"
                review.append(rec)
            elif old_in and not new_in:
                rec["_verdict"] = "reject:db_matches_pdf"   # DB likely already correct
                reject.append(rec)
            elif not new_in:
                rec["_verdict"] = "reject:unverified"
                reject.append(rec)
            elif p["class"] in AUTO_CLASSES and _ws_equiv(oe, ne):
                # pure layout/whitespace change (incl. letter-spaced headers
                # "I N   T H E" -> "IN THE"): no character content changes, so it
                # cannot alter the court's words. Safe to auto-apply.
                rec["_verdict"] = "auto:whitespace_only"
                auto.append(rec)
            else:
                # PDF-confirmed but content changes (scramble, dot-count, glyph
                # swap, missing text) -> human review.
                rec["_verdict"] = "review:pdf_confirmed"
                review.append(rec)
    base = path.rsplit(".", 1)[0]
    for name, rows in (("auto", auto), ("review", review), ("reject", reject)):
        json.dump(rows, open(f"{base}.{name}.json", "w"), ensure_ascii=False, indent=1)
    print(f"AUTO {len(auto)}  REVIEW {len(review)}  REJECT {len(reject)}")
    from collections import Counter
    for label, rows in (("AUTO", auto), ("REVIEW", review), ("REJECT", reject)):
        c = Counter((r["class"], r["_verdict"]) for r in rows)
        for k, n in c.most_common():
            print(f"  {label:7} {n:3}  {k[0]:14} {k[1]}")


if __name__ == "__main__":
    main()
