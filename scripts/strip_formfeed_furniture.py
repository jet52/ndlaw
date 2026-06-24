"""Strip pdftotext form-feed (0x0C) page-break artifacts + running-header furniture.

`pdftotext` emits a 0x0C at every page break; ingestion preserved it. Two cases:

  FURNITURE  — 0x0C followed by a running header `<short case name>\\n\\n<docket>`
               that repeats the page-1 caption (appellate page furniture, not
               published text). We remove the whole block, but ONLY when the
               docket number is independently confirmed in the caption region
               (first occurrence precedes this one) — else we leave the header
               and just drop the control byte, and FLAG it.
  BARE       — a lone 0x0C at a paragraph/line boundary (`\\n\\n\\x0c[¶N`, mid-
               sentence wraps, etc.). The byte is a non-text control char; we
               drop it and keep the surrounding whitespace verbatim.

Per opinion ATOMIC + verified: the resulting alphabetic-word multiset must equal
the original MINUS exactly the words in the removed furniture headers (nothing
else may change). Dry-run by default; --apply commits + logs one changelog row
per opinion. Writes a REVIEW report (md + json) for sign-off.

Usage: strip_formfeed_furniture.py [--apply] [--db opinions.db]
       [--batch formfeed-furniture-2026-06-24] [--out triage/formfeed-furniture]
"""
import argparse
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone

FF = "\x0c"
# 0x0C, then a non-empty header line, then a docket line (Civil No. 970178 /
# No. 20250426 / Nos. 20010283 & 20010284), then a blank line. The header/docket
# separator is one OR two newlines (older N.D. uses a blank line; 2026 uses one).
FURNITURE = re.compile(
    r"\x0c[ \t]*([^\n]+?)[ \t]*\n\s*((?:Civil )?Nos?\.\s*[0-9][0-9 &]*)[ \t]*\n\s*\n")
DOCKET_NUM = re.compile(r"\d{3,}")   # individual docket numbers (consolidated: X & Y)


def words(s):
    return Counter(re.findall(r"[A-Za-z]+", s))


def process(text):
    """-> (new_text, removed_headers:list[str], n_bare, flags:list[str])."""
    removed, flags = [], []

    def repl(m):
        header, docket = m.group(1), m.group(2)
        nums = DOCKET_NUM.findall(docket)
        # confirm the docket number appears BEFORE this furniture block (caption)
        before = text[:m.start()]
        if nums and any(n.strip() and n.strip() in before for n in nums):
            removed.append(f"{header} | {docket}")
            # the preceding text already ends with a paragraph break (\n\n);
            # drop the whole block. Guard the rare case of no preceding newline.
            return "" if text[m.start() - 1:m.start()] == "\n" else "\n\n"
        flags.append(f"unverified docket, header kept: {header!r} {docket!r}")
        return "\n\n" + m.group(1) + "\n\n" + m.group(2) + "\n\n"  # drop 0x0C only

    t = FURNITURE.sub(repl, text)
    n_bare = t.count(FF)
    t = t.replace(FF, "")            # remaining lone control bytes
    return t, removed, n_bare, flags


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--batch", default="formfeed-furniture-2026-06-24")
    ap.add_argument("--out", default="triage/formfeed-furniture")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    ids = [r[0] for r in con.execute(
        "SELECT id FROM opinions WHERE text_content LIKE '%'||char(12)||'%'").fetchall()]

    report, applied, skipped = [], 0, 0
    tot_furn = tot_bare = 0
    for oid in ids:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        new, removed, n_bare, flags = process(old)
        # verify: only the removed-header words may differ from the original
        wd_removed = Counter()
        for h in removed:
            wd_removed += words(h)
        if words(new) + wd_removed != words(old):
            skipped += 1
            report.append({"opinion_id": oid, "status": "SKIP_wordgate",
                           "removed": removed, "n_bare": n_bare, "flags": flags})
            continue
        cite = con.execute("SELECT citation FROM citations WHERE opinion_id=? "
                           "ORDER BY is_primary DESC LIMIT 1", (oid,)).fetchone()
        tot_furn += len(removed)
        tot_bare += n_bare
        applied += 1
        report.append({"opinion_id": oid, "cite": cite[0] if cite else "",
                       "status": "OK", "n_furniture": len(removed),
                       "removed": removed, "n_bare_stripped": n_bare, "flags": flags})
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, args.batch, oid, "text_content.formfeed_furniture",
                 f"{len(removed)} running-header block(s) + {n_bare} bare 0x0C",
                 "; ".join(removed)[:200] or "bare control-byte strip only",
                 "pdftotext page-furniture removal; docket-in-caption verified; word-multiset gate"))
    json.dump(report, open(f"{args.out}.json", "w"), ensure_ascii=False, indent=1)
    # readable md
    md = [f"# Form-feed furniture removal — {'APPLIED' if args.apply else 'DRY-RUN'}", "",
          f"{applied} opinions OK, {skipped} skipped (word-gate). "
          f"Removed {tot_furn} running-header blocks + {tot_bare} bare 0x0C bytes.", ""]
    allflags = [(r["opinion_id"], f) for r in report for f in r.get("flags", [])]
    if allflags:
        md += ["## Flags (header kept — docket NOT confirmed in caption)", ""]
        md += [f"- id{oid}: {f}" for oid, f in allflags] + [""]
    md += ["## Removed running headers (by opinion)", ""]
    for r in report:
        if r["status"] == "OK" and r["removed"]:
            md.append(f"### {r.get('cite','')} (id {r['opinion_id']}) — {r['n_bare_stripped']} bare bytes")
            md += [f"- ~~{h}~~" for h in r["removed"]] + [""]
    open(f"{args.out}.md", "w").write("\n".join(md))
    print(f"opinions: {len(ids)}  OK: {applied}  skipped: {skipped}")
    print(f"furniture blocks removed: {tot_furn}  bare 0x0C stripped: {tot_bare}  flags: {len(allflags)}")
    print(f"report -> {args.out}.md / .json")
    if args.apply:
        con.commit()
        print(f"COMMITTED batch {args.batch}.")


if __name__ == "__main__":
    main()
