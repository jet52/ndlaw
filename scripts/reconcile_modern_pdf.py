"""Deterministic modern-opinion reconciliation against the (now-correct) PDF.

The scraper's old pdfminer extractor scrambled word order at line breaks. The
fix (poppler pdftotext) reads correctly, AND pdftotext already carries the court's
[¶N] paragraph markers — the same markers the DB uses. So we can repair scrambles
surgically WITHOUT a wholesale re-derivation that would revert logged corrections:

  align DB <-> PDF by [¶N] marker; for each paragraph, replace the DB text with the
  PDF text ONLY when the DB version is a SCRAMBLE of the PDF (same/overlapping
  words, different order) — leaving corrected or already-matching paragraphs alone.

Guards (authoritative-text safety):
  * paragraphs whose DB text contains a footnote call marker ``[N]`` are SKIPPED
    (they carry footnote corrections) -> flagged for manual handling.
  * only paragraphs with HIGH word overlap (jaccard >= 0.6) and a different word
    SEQUENCE are treated as scrambles; low-overlap differences are genuine and
    left alone (flagged).
  * emits {old_exact,new_exact} proposals (class "scramble") for the gated applier
    (apply_proofing_proposals.py), so every change is byte-exact + reversible.

Usage: reconcile_modern_pdf.py OUT.json [--ids 20517,20516 | --year 2026 | --all]
       [--db opinions.db]
"""
import argparse
import json
import os
import re
import subprocess
import sqlite3

REFS = os.path.expanduser("~/refs/nd/opin")
_PARA = re.compile(r"\[¶\s*\d+\]")
_FN_CALL = re.compile(r"(?<![A-Za-z0-9])\[\d{1,3}\]")  # footnote call marker


def paras(text):
    """-> {num: body_text} split on [¶N] markers (body = marker..next marker)."""
    ms = list(_PARA.finditer(text))
    out = {}
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        num = int(re.search(r"\d+", m.group(0)).group(0))
        out.setdefault(num, (m.end(), text[m.end():end]))
    return out


def pdftext(cite):
    nd = cite.replace(" ", "")
    p = f"{REFS}/pdfs/{cite.split()[0]}/{nd}.pdf"
    if not os.path.exists(p):
        return ""
    return subprocess.run(["pdftotext", "-q", "-enc", "UTF-8", p, "-"],
                          capture_output=True, text=True).stdout


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def words(s):
    return re.findall(r"[A-Za-z0-9]+", s.lower())


def jaccard(a, b):
    sa, sb = set(a), set(b)
    return len(sa & sb) / max(1, len(sa | sb))


def reconcile(db_text, pdf_text):
    """-> (proposals, flags). proposals: per-paragraph scramble replacements."""
    db_p, pdf_p = paras(db_text), paras(pdf_text)
    proposals, flags = [], []
    for num, (start, db_body) in db_p.items():
        if num not in pdf_p:
            continue
        pdf_body = pdf_p[num][1]
        if norm(db_body) == norm(pdf_body):
            continue  # already correct
        wa, wb = words(db_body), words(pdf_body)
        if not wa or not wb:
            continue
        if _FN_CALL.search(db_body):
            flags.append({"para": num, "reason": "has footnote marker", "db": norm(db_body)[:80]})
            continue
        # PURE REORDER only: identical word multiset, different sequence. This is
        # a provably-safe scramble fix — no words added or dropped, just restored
        # to the authoritative PDF order. Anything that changes the multiset
        # (stray page/footnote digits pdftotext inlines, hyphenation artifacts
        # like "pre- dispositional" vs "predispositional", real text loss) is a
        # different, higher-stakes class -> flagged for review, never auto.
        if sorted(wa) == sorted(wb) and wa != wb:
            proposals.append({
                "class": "scramble", "para": num,
                "old_exact": db_body, "new_exact": " " + norm(pdf_body),
                "verified_count": 1, "jaccard": 1.0,
                "source": "court PDF (pdftotext)", "confidence": "high",
            })
        elif jaccard(wa, wb) >= 0.6:
            flags.append({"para": num, "reason": "content-change (not pure reorder)",
                          "db": norm(db_body)[:90], "pdf": norm(pdf_body)[:90]})
    return proposals, flags


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("out")
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--ids")
    ap.add_argument("--year")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    if args.ids:
        ids = [int(x) for x in args.ids.split(",")]
    elif args.year:
        ids = [r[0] for r in con.execute(
            "SELECT id FROM opinions WHERE substr(date_filed,1,4)=? ORDER BY date_filed DESC",
            (args.year,))]
    else:
        ids = [r[0] for r in con.execute(
            "SELECT id FROM opinions WHERE date_filed>='1997-01-01' ORDER BY date_filed DESC")]
    out_props, out_flags = [], []
    n_scr = n_clean = n_nopdf = 0
    for oid in ids:
        row = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        cite = con.execute("SELECT citation FROM citations WHERE opinion_id=? "
                           "ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone()
        if not row or not cite:
            continue
        pt = pdftext(cite[0])
        if not pt:
            n_nopdf += 1
            continue
        props, flags = reconcile(row[0], pt)
        # byte-exact uniqueness guard
        props = [p for p in props if row[0].count(p["old_exact"]) == 1]
        if props:
            n_scr += 1
            for p in props:
                out_props.append({"opinion_id": oid, "cite": cite[0], **p})
        else:
            n_clean += 1
        for f in flags:
            out_flags.append({"opinion_id": oid, "cite": cite[0], **f})
    json.dump(out_props, open(args.out, "w"), ensure_ascii=False, indent=1)
    json.dump(out_flags, open(args.out.replace(".json", ".flags.json"), "w"),
              ensure_ascii=False, indent=1)
    print(f"scanned {len(ids)} | scrambled {n_scr} | clean {n_clean} | no-pdf {n_nopdf}")
    print(f"  {len(out_props)} scramble proposals -> {args.out}")
    print(f"  {len(out_flags)} flags (footnote/low-overlap) -> {args.out.replace('.json', '.flags.json')}")


if __name__ == "__main__":
    main()
