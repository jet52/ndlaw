"""Restore dropped footnote numbers to citation-graph-confirmed footnotes whose
BODY is already present in the text as a number-less orphan (`\\n\\n. body`).

Each entry is externally confirmed by another opinion's pincite (`<cite>, ¶ X
n.N`), which establishes that the footnote exists, its number N, and its call
paragraph X. The body text is the court's verbatim words (already stored); we
only restore structure: insert N before the body (period form) and a standalone
N call marker at the confirmed call paragraph, so the parser links body -> ¶ X.

ONLY single-orphan opinions are handled here — where there is exactly one
number-less body, so the orphan<->number match is unambiguous. Multi-footnote
opinions require per-PDF verification and are handled separately.

Dry-run by default; ``--apply`` writes + logs one `text_content.footnote_number`
changelog row per opinion. Body prose asserted unchanged.
"""
import argparse
import re
import sqlite3
from datetime import datetime, timezone

BATCH = "footnote-number-restore-2026-06-23"

# (cite, opinion_id, footnote_num, call_paragraph, orphan_body_anchor, citing_cite)
ENTRIES = [
    ("1999 ND 2", 12808, 1, 5, "The district court concluded the Department of Transpor",
     "1999 ND 196 / 2001 ND 192 / 2004 ND 21 / 2020 ND 192 (¶ 5 n.1)"),
    ("2011 ND 122", 15640, 1, 1, "Zink and Keller's notice of appeal attempts to appeal f",
     "(¶ 1 n.1)"),
]


def restore(text, num, call_para, anchor):
    # 1) insert the number before the orphan body: "\n\n. <anchor>" -> "\n\n{num}\n\n. <anchor>"
    om = f"\n\n. {anchor}"
    if text.count(om) != 1:
        raise SystemExit(f"orphan anchor not unique ({text.count(om)})")
    text = text.replace(om, f"\n\n{num}\n\n. {anchor}")
    # 2) insert a standalone call marker at the end of the call paragraph
    nxt = None
    for cand in (f"[¶ {call_para + 1}]", f"[¶{call_para + 1}]"):
        if cand in text:
            nxt = cand; break
    if nxt is None:
        raise SystemExit(f"next paragraph marker for ¶{call_para} not found")
    i = text.find(nxt)
    # text[:i] already ends with the blank line before the marker; insert the
    # standalone call number without disturbing existing whitespace.
    text = text[:i] + f"{num}\n\n" + text[i:]
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    import ndcourts_mcp.proofread as pr
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    for cite, oid, num, cp, anchor, citing in ENTRIES:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        new = restore(old, num, cp, anchor)
        # the court's words must be unchanged — we only inserted bare-number
        # marker lines, which add no alphabetic tokens.
        words = lambda s: re.findall(r"[A-Za-z]+", s)
        assert words(new) == words(old), f"{cite}: prose changed beyond marker insertion!"
        st = pr.footnote_structure(new)
        cpar = st["call_para"].get(num)
        ok = cpar == cp and any(n == num for n, _, _ in st["bodies"])
        print(f"  {cite} n.{num}: parser -> ¶{cpar} n.{num}  {'OK' if ok else 'FAIL'}")
        if args.apply and ok:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, BATCH, oid, "text_content.footnote_number",
                 f"footnote {num} body present but number dropped (orphan period body)",
                 f"restored number {num} + call marker at ¶{cp}; body verbatim",
                 f"citation graph: {citing}"))
    if args.apply:
        con.commit(); print(f"APPLIED + logged (batch {BATCH}).")
    else:
        print("DRY-RUN — re-run with --apply.")


if __name__ == "__main__":
    main()
