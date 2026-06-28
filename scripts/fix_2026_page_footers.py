"""Remove page-footer numbers that leaked inline into 2026-era opinion text.

The 2026 scraper/ingest folded centered page-footer numbers into the body text
(e.g. PDF "...noted\n\n        4\n\nthe statements..." became DB "noted 4 the").
This deterministically locates each leak from the PDF and removes ONLY exact
matches:

  for each centered lone-digit footer line F in pdftotext -layout, take the last
  token (W1) of the preceding text line and the first token (W2) of the following
  text line; if the DB contains exactly one "W1 F W2", rewrite it "W1 W2" (or, when
  W1 ends with a hyphen, "W1W2" — a word split across the page break).

Safe by construction: it never removes a bare digit on value alone; it only edits
where the PDF's actual page break sits between the two specific bracketing words.

Usage: fix_2026_page_footers.py [--apply] [--db opinions.db] [--year 2026]
"""
import argparse, os, re, sqlite3, subprocess
from datetime import datetime, timezone

REFS = os.path.expanduser("~/refs/nd/opin")
FOOTER = re.compile(r"^\s{15,}(\d{1,3})\s*$")
WORD = re.compile(r"[^\s]+")


def pdf_lines(nd):
    p = f"{REFS}/pdfs/{nd[:4]}/{nd}.pdf"
    if not os.path.exists(p):
        return None
    out = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout
    return out.split("\n")


def leaks_for(lines):
    """-> list of (W1, F, W2) from each centered footer line."""
    out = []
    for i, ln in enumerate(lines):
        m = FOOTER.match(ln)
        if not m:
            continue
        F = m.group(1)
        # previous text line (skip blanks / other footer lines)
        j = i - 1
        while j >= 0 and (not lines[j].strip() or FOOTER.match(lines[j])):
            j -= 1
        k = i + 1
        while k < len(lines) and (not lines[k].strip() or FOOTER.match(lines[k])):
            k += 1
        if j < 0 or k >= len(lines):
            continue
        prev_tokens = WORD.findall(lines[j])
        next_tokens = WORD.findall(lines[k])
        if not prev_tokens or not next_tokens:
            continue
        W1, W2 = prev_tokens[-1], next_tokens[0]
        # require alphabetic-ish anchors (avoids cite/number contexts)
        if not re.search(r"[A-Za-z]", W1) or not re.search(r"[A-Za-z]", W2):
            continue
        out.append((W1, F, W2))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--year", default="2026")
    ap.add_argument("--batch", default="fix-2026-page-footers-2026-06-27")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    rows = con.execute("SELECT o.id, o.text_content, "
                       "(SELECT citation FROM citations c WHERE c.opinion_id=o.id ORDER BY is_primary DESC LIMIT 1) "
                       "FROM opinions o WHERE o.date_filed LIKE ? AND o.text_content<>''",
                       (args.year + "%",)).fetchall()
    tot_op = tot_edit = 0
    for oid, text, cite in rows:
        if not cite:
            continue
        nd = cite.replace(" ", "")
        lines = pdf_lines(nd)
        if lines is None:
            continue
        edits = []
        for W1, F, W2 in leaks_for(lines):
            if W1.endswith("-"):
                old, new = f"{W1} {F} {W2}", f"{W1}{W2}"   # word split across break
            else:
                old, new = f"{W1} {F} {W2}", f"{W1} {W2}"
            if text.count(old) == 1:
                edits.append((old, new))
        if not edits:
            continue
        # de-dupe (a footer pair could repeat in leaks list)
        edits = list(dict.fromkeys(edits))
        tot_op += 1
        tot_edit += len(edits)
        print(f"  id{oid} {cite}: {len(edits)} leak(s)")
        for old, new in edits:
            print(f"      {old!r} -> {new!r}")
        if args.apply:
            for old, new in edits:
                if text.count(old) != 1:
                    continue
                text = text.replace(old, new)
                con.execute("INSERT INTO changelog (timestamp,batch,opinion_id,field,old_value,new_value,authority) "
                            "VALUES (?,?,?,?,?,?,?)",
                            (ts, args.batch, oid, "text_content.ocr_digit", old, new,
                             "inline page-footer number removed (PDF centered-footer between these words)"))
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (text, oid))
    print(f"\n{tot_edit} leak(s) across {tot_op} opinions  ({'APPLIED' if args.apply else 'dry-run'})")
    if args.apply:
        con.commit()
        print(f"COMMITTED batch {args.batch}.")


if __name__ == "__main__":
    main()
