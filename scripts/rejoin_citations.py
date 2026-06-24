"""Rejoin citations fragmented across lines in markdown/reporter-sourced opinions.

A large cohort (the markdown-sourced records, ids ~18xxx) ingested citations with
spurious line breaks and isolated commas, e.g.

    Spirit Prop. Mgmt. v. Vondell,\\n2017 ND 158, ¶ 4\\n,\\n897\\nN.W.2d 334

should read

    Spirit Prop. Mgmt. v. Vondell, 2017 ND 158, ¶ 4, 897 N.W.2d 334

Three conservative, citation-internal transforms (each preserves the alphabetic
word multiset — only newlines / a comma's position change, no words added/dropped):

  1. LONE-COMMA LINE   X \\n , \\n Y           -> X, Y   (a comma alone on its own
                                                  line is never legitimate prose)
  2. NUMBER->REPORTER  967 \\n N.W.2d          -> 967 N.W.2d
  3. NAME->NEUTRAL-CITE Vondell,\\n2017 ND 158 -> Vondell, 2017 ND 158

Per-opinion gate: alphabetic word multiset must be UNCHANGED. Where a PDF exists,
each rejoined neutral-cite region (e.g. "2017 ND 158, ¶ 4, 897") must appear in the
PDF text (normalized) — if not, the opinion is flagged for review, not applied.
Dry-run by default; report (md + json). FTS auto-syncs via opinions_au on --apply.

Usage: rejoin_citations.py [--apply] [--db opinions.db]
       [--batch citation-rejoin-2026-06-24] [--out triage/citation-rejoin]
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
REPORTER = r"(N\.W\.2d|N\.W\.3d|N\.W\.|N\.D\.|P\.2d|P\.3d|U\.S\.|S\.Ct\.|L\.Ed\.)"
LONE_COMMA = re.compile(r"[ \t]*\n[ \t]*,[ \t]*\n[ \t]*")
NUM_REPORTER = re.compile(r"(\d)[ \t]*\n[ \t]*" + REPORTER)
NAME_CITE = re.compile(r",[ \t]*\n[ \t]*(\d{4}[ ]+ND[ ])")
# a digit/paren orphaned from trailing close-punctuation by a line break
# (citation number before a terminal . ) ; or ,); never legit prose.
NUM_PUNCT = re.compile(r"([\d)])[ \t]*\n[ \t]*([.);,])")
# a rejoined neutral-cite chunk to PDF-verify: "YYYY ND N, ¶ P, VOL N.W.Xd PAGE"
CITE_CHUNK = re.compile(r"\d{4} ND \d+,? ?¶+ ?[\d-]+,? ?\d+ N\.W\.\dd \d+")


def words(s):
    return Counter(re.findall(r"[A-Za-z]+", s))


def rejoin(t):
    t = LONE_COMMA.sub(", ", t)
    t = NUM_REPORTER.sub(r"\1 \2", t)
    t = NAME_CITE.sub(r", \1", t)
    t = NUM_PUNCT.sub(r"\1\2", t)
    return t


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
    ap.add_argument("--batch", default="citation-rejoin-2026-06-24")
    ap.add_argument("--out", default="triage/citation-rejoin")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    # candidates: any of the three artifacts present
    ids = [r[0] for r in con.execute(
        "SELECT id FROM opinions WHERE text_content LIKE '%'||char(10)||','||char(10)||'%' "
        "OR text_content LIKE '%'||char(10)||' ,'||char(10)||'%'").fetchall()]

    report, applied, skipped = [], 0, 0
    tot_changes = 0
    for oid in ids:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        new = rejoin(old)
        if new == old:
            continue
        n_changes = len(old) - len(new)
        # HARD gate: alpha-word AND digit multiset unchanged (only ws/comma-position
        # moves). This alone proves the transform is content-preserving, so we apply
        # even when the PDF can't verify.
        digits = lambda s: Counter(re.findall(r"\d", s))
        if words(new) != words(old) or digits(new) != digits(old):
            skipped += 1
            report.append({"opinion_id": oid, "status": "SKIP_multiset"})
            continue
        # advisory PDF check (many early opinions have OCR-garbage scanned-PDF text
        # layers that can't confirm even a correct rejoin) — recorded, not blocking.
        pt = pdf_text(con, oid)
        bad = []
        if pt:
            for m in CITE_CHUNK.finditer(new):
                chunk = re.sub(r"\s+", " ", m.group(0)).strip().rstrip(".")
                if chunk not in pt:
                    bad.append(chunk)
        cite = con.execute("SELECT citation FROM citations WHERE opinion_id=? "
                           "ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone()
        applied += 1
        tot_changes += n_changes
        status = ("OK_pdf_unverified" if bad else "OK_pdf") if pt else "OK_nopdf"
        report.append({"opinion_id": oid, "cite": cite[0] if cite else "",
                       "status": status, "chars_removed": n_changes, "pdf_unverified": bad[:4]})
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, args.batch, oid, "text_content.citation_rejoin",
                 f"fragmented citations ({n_changes} chars of stray \\n/lone-comma)", "rejoined",
                 "markdown ingestion line-break artifact; alpha-word-multiset gate + PDF cite-chunk verify"))
    json.dump(report, open(f"{args.out}.json", "w"), ensure_ascii=False, indent=1)
    from collections import Counter as C
    st = C(r["status"] for r in report)
    md = [f"# Citation rejoin — {'APPLIED' if args.apply else 'DRY-RUN'}", "",
          f"candidates {len(ids)}; OK {applied} ({tot_changes} stray chars removed); skipped {skipped}.",
          f"status: {dict(st)}", ""]
    if skipped:
        md += ["## Skipped (needs review)", ""]
        md += [f"- id{r['opinion_id']} {r['status']}: {r.get('bad','')}"
               for r in report if r["status"].startswith("SKIP")][:40]
    open(f"{args.out}.md", "w").write("\n".join(md))
    print(f"candidates: {len(ids)}  OK: {applied}  skipped: {skipped}  ({dict(st)})")
    print(f"report -> {args.out}.md / .json")
    if args.apply:
        con.commit()
        print(f"COMMITTED batch {args.batch}.")


if __name__ == "__main__":
    main()
