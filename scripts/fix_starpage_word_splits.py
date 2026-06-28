"""Rejoin words split across an N.W./N.W.2d star-page marker (pre-1953 corpus).

A correct star-page is rendered inline between WHOLE words ("permission *709 to
file"). The defect: a single word was split across the marker
("re\\n\\n *287\\n\\n demption" for "redemption"). This rejoins ONLY genuine splits
and preserves the star-page marker, placing it immediately before the rejoined
word (the corpus convention: the marker precedes the first content of the new
page; pincite-safe — over-inclusion, never skips page-NNN content).

  re\\n\\n *287\\n\\n demption   ->   *287 redemption

Genuine-split test (all required), to avoid touching the ~6,660 correct
word-boundary star-pages:
  1. the joined token (frag1+frag2) appears as a whole word elsewhere in the
     SAME opinion (proves it is a real word that got split);
  2. neither fragment is itself a common English word (excludes legit boundaries
     like "in *214 forming" = "engaged in forming").

Usage: fix_starpage_word_splits.py [--apply] [--db opinions.db]
"""
import argparse, re, sqlite3
from datetime import datetime, timezone

COMMON = set("a an and as at be by do for go he in is it my no of on or so the to up us we".split())
SPLIT = re.compile(r'([A-Za-z]+)\n+ ?\\?\*(\d{2,4})\n+ ?([a-z]{2,})')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--batch", default="fix-starpage-word-splits-2026-06-27")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    rows = con.execute("SELECT id, text_content FROM opinions WHERE text_content LIKE '%*%'").fetchall()
    tot_op = tot = 0
    for oid, text in rows:
        edits = []
        for m in SPLIT.finditer(text):
            f1, N, f2 = m.groups()
            joined = f1 + f2
            if f1.lower() in COMMON or f2.lower() in COMMON:
                continue
            if not re.search(r'\b' + re.escape(joined) + r'\b', text, re.IGNORECASE):
                continue
            old = m.group(0)
            new = f"*{N} {joined}"
            if text.count(old) == 1:
                edits.append((old, new))
        edits = list(dict.fromkeys(edits))
        if not edits:
            continue
        tot_op += 1
        tot += len(edits)
        for old, new in edits:
            print(f"  id{oid}: {old.replace(chr(10),'/')!r} -> {new!r}")
        if args.apply:
            for old, new in edits:
                if text.count(old) != 1:
                    continue
                text = text.replace(old, new)
                con.execute("INSERT INTO changelog (timestamp,batch,opinion_id,field,old_value,new_value,authority) "
                            "VALUES (?,?,?,?,?,?,?)",
                            (ts, args.batch, oid, "text_content.split_join", old[:200], new,
                             "word split across star-page rejoined; marker placed before word (corpus convention); "
                             "joined word verified whole elsewhere in opinion; neither fragment a common word"))
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (text, oid))
    print(f"\n{tot} split(s) across {tot_op} opinions  ({'APPLIED' if args.apply else 'dry-run'})")
    if args.apply:
        con.commit()
        print(f"COMMITTED batch {args.batch}.")


if __name__ == "__main__":
    main()
