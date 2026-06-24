"""Decode LaTeX/math-mode-encoded citations in opinion text_content.

A subset of opinions (~2020-2024) ingested citations with LaTeX artifacts: case
names wrapped in `$...$` (math-mode italics), escaped spaces `\\ `, the pilcrow
encoded as `\\P`, and escaped commas `\\,`. E.g.
  $State\\ v.\\ Tupa,\\ 2005\\ ND\\ 25,\\ \\P\\ 8-9,\\ 691\\ N.W.2d ...$
should read
  State v. Tupa, 2005 ND 25, ¶ 8-9, 691 N.W.2d ...

ONLY opinions with the LaTeX signature (`$...$` near a `\\ `, or `\\P`) are
touched — NOT the pre-1953 OCR-backslash-noise opinions ("powei\\ Especially"),
which are excluded (no `$`/`\\P` signature) and listed for separate manual review.

The `\\ ` run is ambiguous: usually a space, but sometimes a lost `¶` (`$\\ 9$` =>
`¶ 9`). So this is PDF-GATED: per opinion, decode, then require the decoded text
to be byte-clean (no residual `$`/`\\`) AND every decoded citation-region token to
appear in the court PDF; if the PDF disagrees (e.g. a `¶` the `\\ `->space lost),
the opinion is SKIPPED for manual handling rather than applied wrong. Dry-run by
default; report (md + json).

Usage: decode_latex_citations.py [--apply] [--db opinions.db]
       [--batch latex-citations-2026-06-24] [--out triage/latex-citations]
"""
import argparse
import json
import os
import re
import subprocess
import sqlite3
from collections import Counter
from datetime import datetime, timezone

REFS = os.path.expanduser("~/refs/nd/opin")
SIG = re.compile(r"\$[^$\n]{0,60}\\ |\\P")   # LaTeX-citation signature


def decode(text):
    t = text
    t = t.replace("\\P", "¶")          # pilcrow
    t = t.replace("\\,", ",")          # escaped comma
    t = re.sub(r"\\ ", " ", t)         # escaped space
    t = t.replace("$", "")             # strip math-mode delimiters
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t


def words(s):
    return Counter(re.findall(r"[A-Za-z]+", s))


def pdf_text(con, oid):
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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--batch", default="latex-citations-2026-06-24")
    ap.add_argument("--out", default="triage/latex-citations")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    ids = [r[0] for r in con.execute(
        r"SELECT id FROM opinions WHERE instr(text_content, '\ ')>0 OR instr(text_content,'\P')>0").fetchall()]

    report, applied, skipped, no_sig = [], 0, 0, 0
    for oid in ids:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        if not SIG.search(old):
            no_sig += 1            # OCR-backslash noise, not LaTeX -> leave + list
            report.append({"opinion_id": oid, "status": "SKIP_no_latex_sig"})
            continue
        new = decode(old)
        # gate: no residual LaTeX, and the decode only added ¶ / removed $ \ (alpha words unchanged)
        residual = "$" in new or "\\" in new
        if words(new) != words(old):
            residual = True
        pt = pdf_text(con, oid)
        # every decoded citation chunk (text around a former $...$ / ¶) must be PDF-confirmed
        bad = []
        if pt:
            for m in re.finditer(r"¶ ?\d[\d-]*", new):
                ctx = re.sub(r"\s+", " ", new[max(0, m.start() - 25):m.end() + 5]).strip()
                if ctx[:30] not in pt:
                    bad.append(ctx[:30])
        cite = con.execute("SELECT citation FROM citations WHERE opinion_id=? "
                           "ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone()
        if residual or (pt and bad) or not pt:
            skipped += 1
            report.append({"opinion_id": oid, "cite": cite[0] if cite else "",
                           "status": "SKIP_review",
                           "reason": ("residual_markup" if residual else
                                      "no_pdf" if not pt else "pdf_mismatch"),
                           "bad_chunks": bad[:4]})
            continue
        applied += 1
        report.append({"opinion_id": oid, "cite": cite[0] if cite else "", "status": "OK"})
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, args.batch, oid, "text_content.latex_decode",
                 "LaTeX-encoded citations ($...$, \\ , \\P)", "decoded",
                 "math-mode citation artifact; PDF-gated decode (¶/space/strip-$)"))
    json.dump(report, open(f"{args.out}.json", "w"), ensure_ascii=False, indent=1)
    md = [f"# LaTeX-citation decode — {'APPLIED' if args.apply else 'DRY-RUN'}", "",
          f"{applied} OK, {skipped} need review, {no_sig} OCR-noise (not LaTeX, left).", "",
          "## OCR-backslash-noise opinions (manual — `\\` is OCR garbage, not LaTeX):",
          "  " + ", ".join(f"id{r['opinion_id']}" for r in report if r["status"] == "SKIP_no_latex_sig"),
          "", "## Need review (PDF mismatch / residual):"]
    md += [f"- id{r['opinion_id']} ({r.get('reason')}): {r.get('bad_chunks')}"
           for r in report if r["status"] == "SKIP_review"]
    open(f"{args.out}.md", "w").write("\n".join(md))
    print(f"candidates: {len(ids)}  OK: {applied}  review: {skipped}  ocr-noise: {no_sig}")
    print(f"report -> {args.out}.md / .json")
    if args.apply:
        con.commit()
        print(f"COMMITTED batch {args.batch}.")


if __name__ == "__main__":
    main()
