"""Normalize malformed footnote-body markers so present-but-undetected footnotes
parse. The analyzer's period-form body marker is ``\\nN\\n\\n. body`` (period +
SPACE); some bodies lost the space (``.In``) or the whole marker (``\\n body``),
leaving the footnote text present but invisible to the parser. This inserts only
the missing punctuation/space — asserted: identical alphabetic-token sequence.

Used to fill footnote-number gaps in opinions whose other footnotes are intact
(footnotes run 1..N with no skips); each fixed body is verified verbatim against
an authoritative source (court archive HTML / West) before listing here.

Idempotent (skips an entry already in good form). Dry-run by default; ``--apply``
writes + logs one ``text_content.footnote_marker`` row each.
"""
import argparse
import re
import sqlite3
from datetime import datetime, timezone

BATCH = "footnote-body-marker-fix-2026-06-23"

# (oid, num, bad_substr, good_substr, authority)  -- bad must be unique
ENTRIES = [
    (12659, 1, "\n\n In 1985 the Bureau ordered", "\n\n. In 1985 the Bureau ordered",
     "archive/1998/970243.htm FN_1_ (body present, period marker dropped)"),
    (12659, 6, "\n\n.In addition to the retirement offset", "\n\n. In addition to the retirement offset",
     "archive/1998/970243.htm FN_6_ (body present, space after period dropped)"),
    (12659, 11, "\n\n.Social security old age insurance", "\n\n. Social security old age insurance",
     "archive/1998/970243.htm FN_11_ (body present, space after period dropped)"),
    (12790, 4, "\n\n.The Second Restatement", "\n\n. The Second Restatement",
     "archive/1998/980171.htm FN_4_ (body present, space after period dropped)"),
]


def words(s):
    return sorted(re.findall(r"[A-Za-z]+", s))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    import ndcourts_mcp.proofread as pr
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    for oid, num, bad, good, auth in ENTRIES:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        if good in old and bad not in old:
            print(f"  id{oid} n.{num}: already good — skipping"); continue
        if old.count(bad) != 1:
            raise SystemExit(f"id{oid} n.{num}: bad substr not unique ({old.count(bad)})")
        new = old.replace(bad, good)
        assert words(new) == words(old), f"id{oid} n.{num}: alphabetic-token sequence changed!"
        st = pr.footnote_structure(new)
        cpar = st["call_para"].get(num)
        has_body = any(n == num for n, _, _ in st["bodies"])
        print(f"  id{oid} n.{num}: body={has_body}, call ¶{cpar}  {'OK' if has_body else 'FAIL'}")
        if not has_body and args.apply:
            raise SystemExit(f"id{oid} n.{num}: body still not detected — not applying")
        if args.apply and has_body:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, BATCH, oid, "text_content.footnote_marker",
                 f"footnote {num} body present but marker malformed (parser-invisible)",
                 f"normalized period-form marker for footnote {num}; body verbatim",
                 auth))
    if args.apply:
        con.commit(); print(f"APPLIED + logged (batch {BATCH}).")
    else:
        print("DRY-RUN — re-run with --apply.")


if __name__ == "__main__":
    main()
