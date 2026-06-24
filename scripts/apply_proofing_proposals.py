"""Apply verified corpus-proofing proposals (byte-exact old->new) behind gates.

General text-correction applier for the proofing pipeline (NOT footnote-specific).
Per opinion ATOMIC: every old_exact must occur exactly once; applies the
replacement; logs one changelog row per edit (batch + class + source/evidence as
authority). Dry-run by default. Intended for the AUTO set (already PDF-verified +
whitespace-only) or a human-approved REVIEW set.

Usage: apply_proofing_proposals.py PROPOSALS.json [--apply] [--db opinions.db]
       [--batch NAME]
"""
import argparse
import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("proposals")
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--batch", default="corpus-proofing-2026-06-23")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    rows = json.load(open(args.proposals))

    by_op = defaultdict(list)
    for r in rows:
        by_op[r["opinion_id"]].append(r)

    applied = skipped = 0
    for oid, props in by_op.items():
        row = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        if not row:
            continue
        old = text = row[0]
        ok, reason = True, ""
        for p in props:
            oe, ne = p["old_exact"], p["new_exact"]
            if text.count(oe) != 1:
                ok, reason = False, f"{p.get('class')} anchor count={text.count(oe)}"
                break
            text = text.replace(oe, ne)
        if not ok:
            skipped += 1
            print(f"  skip id{oid}: {reason}")
            continue
        applied += 1
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (text, oid))
            for p in props:
                con.execute(
                    "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (ts, args.batch, oid, f"text_content.{p.get('class')}",
                     p["old_exact"][:200], p["new_exact"][:200],
                     f"{p.get('source','')} | {p.get('evidence', p.get('note',''))[:160]} | conf={p.get('confidence')}"))
        else:
            for p in props:
                print(f"  OK id{oid} [{p.get('class')}]: {p['old_exact'][:50]!r} -> {p['new_exact'][:50]!r}")
    print(f"\napplied: {applied}  skipped: {skipped}")
    if args.apply:
        con.commit()
        print(f"COMMITTED batch {args.batch}.")


if __name__ == "__main__":
    main()
