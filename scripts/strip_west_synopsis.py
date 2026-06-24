#!/usr/bin/env python3
"""Strip residual West editorial 'Synopsis' blocks from West-sourced opinions.

A West .doc 'Synopsis' is West's copyrightable editorial note (case summary, procedural
posture, or separate-opinion list) sitting in the West header before 'Attorneys and Law
Firms'. It is NOT the court's 'Syllabus by the Court' (which is separately preserved).

Conservative, hard-gated: strips ONLY when the Synopsis block is
  - immediately bounded by 'Attorneys and Law Firms' (the West header position),
  - <= 400 chars,
  - contains no 'Syllabus by the Court' and no opinion-body marker ([¶N] / '\n N. ').
Anything else (long/unbounded blocks, Synopsis-before-Syllabus, no clean boundary) is
SKIPPED for individual handling. The court Syllabus and the opinion body are never touched.

Per-opinion safety re-check before write: the court 'Syllabus by the Court' block (if any)
and the opinion body must be byte-identical after the strip. Dry-run by default.

Usage: strip_west_synopsis.py IDS.json [--apply] [--batch NAME] [--db opinions.db]
"""
import sqlite3, re, json, sys, datetime

LABEL = re.compile(r'(\n)?[ \t]*Synopsis[ \t]*\n')

def plan(t):
    m = LABEL.search(t)
    if not m:
        return None, "no-label"
    syn_start = m.start() + (1 if m.group(1) else 0)   # keep preceding newline(s)
    body = t[m.end():]
    ai = body.find('Attorneys and Law Firms')
    if ai < 0:
        return None, "no-Attorneys-boundary"
    block = body[:ai]
    if len(block) > 400:
        return None, "block>400"
    if re.search(r'(?i)s[uy]ll?ab[uo]s', block) or 'by the Court' in block:
        return None, "syllabus-in-block"   # incl. OCR variants e.g. 'Sullabus by the Court'
    if re.search(r'\[¶|\n\s*\d+\.\s', block):
        return None, "body-marker-in-block"
    removed = t[syn_start:m.end() + ai]
    new = t[:syn_start] + t[m.end() + ai:]
    return (new, removed), None

def body_fingerprint(t):
    """Syllabus block + body paragraphs — must be invariant across the strip."""
    syll = ""
    i = t.find('Syllabus by the Court')
    if i >= 0:
        syll = t[i:i+4000]
    paras = "".join(re.findall(r'\[¶\s*\d+\][^\[]{0,40}', t))
    return syll + "||" + paras

def main():
    path = sys.argv[1]
    apply = "--apply" in sys.argv
    batch = sys.argv[sys.argv.index("--batch")+1] if "--batch" in sys.argv else "west-synopsis-strip"
    db = sys.argv[sys.argv.index("--db")+1] if "--db" in sys.argv else "opinions.db"
    ids = json.load(open(path))
    con = sqlite3.connect(db)
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    applied = 0; skip = {}
    for oid in ids:
        row = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        if not row:
            skip["not-found"] = skip.get("not-found", 0)+1; continue
        old = row[0]
        res, reason = plan(old)
        if res is None:
            skip[reason] = skip.get(reason, 0)+1; continue
        new, removed = res
        # hard gate: Syllabus + body fingerprint unchanged
        if body_fingerprint(old) != body_fingerprint(new):
            skip["fingerprint-changed"] = skip.get("fingerprint-changed", 0)+1
            print(f"  SKIP id{oid}: body/syllabus fingerprint changed"); continue
        applied += 1
        if apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, batch, oid, "text_content.west_synopsis_strip",
                 removed[:200], "",
                 "West .doc editorial Synopsis block (Attorneys-bounded, <=400 chars); court Syllabus + body preserved (fingerprint-gated); conf=high"))
        else:
            print(f"  OK id{oid}: -{len(removed)} chars: {removed.strip()[:90]!r}")
    if apply:
        con.commit()
    print(f"\napplied: {applied}  skipped: {skip}  ({'APPLIED' if apply else 'dry-run'})")

if __name__ == "__main__":
    main()
