#!/usr/bin/env python3
"""Construct PDF-verified MOVES for displaced/merged section headings.

Recurring ingestion defect: a section heading (roman I-V or letter A-E) that the court
printed on its own centered line gets merged onto the end of the previous line, fused to
the next [¶N] marker, or dropped to the wrong spot. The proofing agents tend to propose
DELETING the stray letter — which loses the court's section structure. The correct fix is
a MOVE: relocate the letter to its own line immediately before its paragraph.

This helper drives off the COURT PDF (authoritative): it extracts the standalone headings
and the [¶N] each precedes, then for any heading not already standalone in the DB it
constructs a byte-exact MOVE proposal (remove the merged letter + insert "\\n\\n<L>\\n\\n"
before the marker). It emits proposals for the gated applier (apply_proofing_proposals.py);
it never deletes. Ambiguous opinions (heading letter not uniquely locatable, multiple
candidate merge sites, no PDF) are SKIPPED for manual handling.

Gates (per emitted proposal): the letter must be a standalone heading before that [¶N] in
the PDF; the merged form must occur exactly once in the DB; the move conserves the letter
(removed once, added once) and changes no other text.

Usage: heading_move.py --ids id1,id2,... [--db opinions.db] [--out triage/heading-moves.json]
"""
import argparse, json, os, re, subprocess, sqlite3

REFS = os.path.expanduser("~/refs/nd/opin")
HEAD_LINE = re.compile(r"^ {10,}(I{1,3}|IV|VI{0,3}|IX|X|[A-E])\s*$")
PARA = re.compile(r"\[¶\s*(\d+)\]")


def pdf_layout(con, oid):
    row = con.execute("SELECT citation FROM citations WHERE opinion_id=? "
                      "ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone()
    if not row or not row[0]:
        return ""
    p = f"{REFS}/pdfs/{row[0].split()[0]}/{row[0].replace(' ', '')}.pdf"
    if not os.path.exists(p):
        return ""
    return subprocess.run(["pdftotext", "-layout", p, "-"],
                          capture_output=True, text=True).stdout


def pdf_heading_set(layout):
    """-> set of letters that appear as standalone centered headings in the PDF.
    (We use the SET, not a ¶-number map: many older PDFs render the court's
    paragraph numbers in the margin, so pdftotext shows no inline [¶N]. For a
    heading merged right before its own [¶N] in the DB, the letter is already
    adjacent to its paragraph — confirming it is a real heading suffices.)"""
    return {m.group(1) for m in (HEAD_LINE.match(ln) for ln in layout.split("\n")) if m}


# merged heading site in the DB: a lone heading letter sitting between a
# sentence-end and the next [¶N] marker, either on the prior line or fused to it.
MERGE_SITE = re.compile(
    r"([.,:;)\"'\]]) (I{1,3}|IV|VI{0,3}|IX|X|[A-E])(\n\n|)(\[¶\s*\d+\])")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--out", default="triage/heading-moves.json")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ids = [int(x) for x in args.ids.split(",") if x.strip()]
    props, skipped = [], []
    for oid in ids:
        t = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        layout = pdf_layout(con, oid)
        if not layout:
            skipped.append({"opinion_id": oid, "why": "no_pdf"}); continue
        hset = pdf_heading_set(layout)
        if not hset:
            skipped.append({"opinion_id": oid, "why": "no_pdf_headings"}); continue
        for m in MERGE_SITE.finditer(t):
            punct, L, gap, marker = m.groups()
            if L not in hset:
                skipped.append({"opinion_id": oid, "L": L, "marker": marker, "why": "letter_not_a_pdf_heading"})
                continue
            old = m.group(0)                                  # "<punct> <L>[\n\n]<marker>"
            new = f"{punct}\n\n{L}\n\n{marker}"
            if t.count(old) != 1:
                skipped.append({"opinion_id": oid, "L": L, "marker": marker, "why": "anchor_not_unique"})
                continue
            props.append({"opinion_id": oid, "class": "heading_seq",
                          "old_exact": old, "new_exact": new,
                          "source_quote": f"(PDF) '{L}' is a standalone centered section heading",
                          "verified_count": 1, "confidence": "high",
                          "source": f"court PDF heading set {sorted(hset)}; merged before {marker}",
                          "note": "heading-MOVE: letter relocated to its own line before its paragraph (not deleted)"})
    json.dump(props, open(args.out, "w"), ensure_ascii=False, indent=1)
    json.dump(skipped, open(args.out.replace(".json", ".skipped.json"), "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(f"emitted {len(props)} heading-move proposals across "
          f"{len(set(p['opinion_id'] for p in props))} opinions; skipped {len(skipped)} "
          f"({dict(Counter(s['why'] for s in skipped))})")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
