#!/usr/bin/env python3
"""Strip residual West editorial furniture from West-.doc-sourced modern opinions.

Removes ONLY West editorial artifacts, preserving all curated content (footnote [N]
resolution, self-cite/keynote stripping, quote-norm, paragraph structure):
  - star-page markers (*NNN) inserted into the body for N.W. reporter pagination
  - the "Attorneys and Law Firms" section label (counsel names are kept)
  - the standalone "Opinion" section label before the justice byline

Header labels are stripped only in the header region (before the first [¶1]) to avoid
catching the word "Opinion" or a quoted "Attorneys and Law Firms" in the body.

Safety gates (per opinion): the [¶N] marker count and the [N] footnote-call count MUST be
unchanged; no star-page / label may remain. Any failure -> skip that opinion.

Dry-run by default. Usage: strip_west_furniture.py IDS.json [--apply] [--batch NAME]
"""
import sqlite3, re, json, sys, datetime

def strip_furniture(s):
    head_end = s.find("[¶1]")
    if head_end < 0:
        head_end = min(len(s), 600)
    head, body = s[:head_end], s[head_end:]
    head = re.sub(r'^\s*Attorneys and Law Firms\n', '', head)
    head = re.sub(r'\nOpinion\n', '\n', head)
    s = head + body
    # West Synopsis / reporter-caption block sitting BEFORE the counsel block:
    # remove everything up to and including the "Attorneys and Law Firms" label,
    # but ONLY when that prefix is unmistakably West editorial (a Synopsis block or a
    # West reporter caption) and contains no opinion-body paragraph marker. This never
    # fires on court text such as a leading "Appeal from ..." jurisdiction line.
    m = re.search(r'Attorneys and Law Firms\n', s)
    if m:
        prefix = s[:m.start()]
        west_prefix = re.match(r'\s*(Synopsis\b|\d+\s+N\.W\.|West\b)', prefix) or \
                      'Supreme Court of North Dakota.' in prefix
        if west_prefix and not re.search(r'\[¶\s*\d+\]', prefix):
            s = s[m.end():]
    # star-pages: line/paragraph-start (consume trailing space), inline, residual
    s = re.sub(r'(\n+)\*\d+ ?', r'\1', s)   # at start of a line (any run of newlines)
    s = re.sub(r'^\*\d+ ?', '', s)          # at very start of the text
    s = re.sub(r' \*\d+ ', ' ', s)          # inline, space-bounded
    s = re.sub(r'\*\d+\n', '\n', s)
    s = re.sub(r' ?\*\d+', '', s)           # any residual (consume a leading space if present)
    return s

def main():
    path = sys.argv[1]
    apply = "--apply" in sys.argv
    batch = sys.argv[sys.argv.index("--batch")+1] if "--batch" in sys.argv else "west-furniture-strip"
    db = sys.argv[sys.argv.index("--db")+1] if "--db" in sys.argv else "opinions.db"
    ids = json.load(open(path))
    con = sqlite3.connect(db)
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    nmark = lambda t: len(re.findall(r'\[¶\s*\d+\]', t))  # [¶N] and [¶ N]
    nfn = lambda t: len(re.findall(r'(?<!¶)\[\d+\]', t))  # footnote calls [N], not [¶N]
    applied = skipped = 0
    for oid in ids:
        row = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        if not row:
            print(f"  skip id{oid}: not found"); skipped += 1; continue
        old = row[0]; new = strip_furniture(old)
        if new == old:
            print(f"  id{oid}: no furniture found (noop)"); continue
        # safety gates
        problems = []
        if nmark(old) != nmark(new): problems.append(f"¶-count {nmark(old)}->{nmark(new)}")
        if nfn(old) != nfn(new): problems.append(f"fn[N]-count {nfn(old)}->{nfn(new)}")
        if re.search(r'\*\d+', new): problems.append("star-page remains")
        if re.search(r'^\s*Attorneys and Law Firms', new): problems.append("atty-label remains")
        if problems:
            print(f"  SKIP id{oid}: {'; '.join(problems)}"); skipped += 1; continue
        applied += 1
        removed = len(old) - len(new)
        if apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, batch, oid, "text_content.west_furniture_strip",
                 f"[{removed} chars of West furniture: star-pages/labels]",
                 "[stripped; curation + ¶/footnote structure preserved]",
                 "West .doc editorial furniture removal; star-pages + 'Attorneys and Law Firms'/'Opinion' labels; PDF-class verified; conf=high"))
        print(f"  OK id{oid}: -{removed} chars  (¶={nmark(new)}, fn[N]={nfn(new)})")
    if apply:
        con.commit()
    print(f"\napplied: {applied}  skipped: {skipped}  ({'APPLIED' if apply else 'dry-run'})")

if __name__ == "__main__":
    main()
