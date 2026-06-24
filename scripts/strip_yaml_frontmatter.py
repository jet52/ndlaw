"""Strip leading YAML frontmatter from opinion text_content.

Markdown/reporter-sourced opinions were ingested with their `---\\ntitle: ...\\n---`
frontmatter block embedded at the very start of text_content. That block is pure
METADATA (title, title_full, court, date_filed, citations, judges, cluster_id) —
all of it duplicated in the structured columns/tables — and is NOT the court's
opinion text. It pollutes FTS search, get_opinion_text, and the released DB.

This removes ONLY the single leading frontmatter block (from the opening `---`
through the first closing `---` fence) plus the blank line after it. Per-opinion
gates: (1) text_content starts with `---\\n`; (2) the matched block contains a
`title:` key (it really is frontmatter, not a stray rule); (3) the closing fence
exists; (4) the remaining body is non-trivial (>= 40 chars) so we never blank an
opinion. Any `---` inside the body is untouched (non-greedy match to the FIRST
closing fence only). Dry-run by default; writes a report (md + json).

NOTE: text_content is FTS5-indexed. After --apply, rebuild the FTS index
(the report prints the command) unless triggers keep it in sync.

Usage: strip_yaml_frontmatter.py [--apply] [--db opinions.db]
       [--batch yaml-frontmatter-2026-06-24] [--out triage/yaml-frontmatter]
"""
import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone

FM = re.compile(r"\A---\n.*?\n---\n[ \t]*\n?", re.DOTALL)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--batch", default="yaml-frontmatter-2026-06-24")
    ap.add_argument("--out", default="triage/yaml-frontmatter")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    ids = [r[0] for r in con.execute(
        "SELECT id FROM opinions WHERE text_content LIKE '---'||char(10)||'%'").fetchall()]

    report, applied, skipped = [], 0, 0
    for oid in ids:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        m = FM.match(old)
        reason = None
        if not m:
            reason = "no_closing_fence"
        elif "title:" not in m.group(0):
            reason = "no_title_key"
        else:
            new = old[m.end():]
            if len(new.strip()) < 40:
                reason = "body_too_short"
        if reason:
            skipped += 1
            report.append({"opinion_id": oid, "status": "SKIP", "reason": reason})
            continue
        applied += 1
        report.append({"opinion_id": oid, "status": "OK", "fm_chars": m.end(),
                       "body_starts": new[:60]})
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, args.batch, oid, "text_content.yaml_frontmatter",
                 old[:m.end()][:200], "(removed leading YAML frontmatter block)",
                 "metadata frontmatter duplicated in structured columns; not opinion text"))
    json.dump(report, open(f"{args.out}.json", "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    skips = Counter(r["reason"] for r in report if r["status"] != "OK")
    md = [f"# YAML frontmatter strip — {'APPLIED' if args.apply else 'DRY-RUN'}", "",
          f"{applied} opinions OK, {skipped} skipped.", ""]
    if skips:
        md += ["## Skips", ""] + [f"- {k}: {v}" for k, v in skips.items()] + [""]
    md += ["## Sample (body start after strip)", ""]
    md += [f"- id{r['opinion_id']}: {r['body_starts']!r}" for r in report if r["status"] == "OK"][:15]
    open(f"{args.out}.md", "w").write("\n".join(md))
    print(f"candidates: {len(ids)}  OK: {applied}  skipped: {skipped} {dict(skips)}")
    print(f"report -> {args.out}.md / .json")
    if args.apply:
        con.commit()
        print(f"COMMITTED batch {args.batch}.")
        print("REMEMBER: rebuild FTS index if not trigger-synced "
              "(e.g. INSERT INTO opinions_fts(opinions_fts) VALUES('rebuild');).")


if __name__ == "__main__":
    main()
