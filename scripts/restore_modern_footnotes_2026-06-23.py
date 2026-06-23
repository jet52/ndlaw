"""Restore modern (1997+) footnotes that the analyzer mashed INLINE into the
running text instead of detaching them (upstream pdf_processor regression; see
TODO-footnotes.md Phase 2d). Each is citation-graph-confirmed (another opinion
pincites ``<cite>, ¶ X n.N``).

Pattern: the footnote BODY sits inline in (or split across) the call paragraph,
and the call superscript was OCR'd to an attached ASCII digit. Recovery, per the
ratified convention (2026-06-23):

1. Denote the inline call by bracketing the surviving digit -> ``[N]`` (kept in
   the prose where the court placed it; the standalone parser resolves call_para
   from a unique inline ``[N]``).
2. Excise the inline body from the prose (rejoining any split sentence).
3. Append the body, verbatim from the ND PDF, at the END of the opinion in
   period form ``\\n\\n{N}\\n\\n. {body}`` (1999 ND 2 convention).

Word MULTISET is asserted unchanged (body words are relocated, not altered; the
only prose edit is wrapping a non-alphabetic digit in brackets). Dry-run by
default; ``--apply`` writes + logs one ``text_content.footnote_recover`` row each.
"""
import argparse
import re
import sqlite3
from datetime import datetime, timezone

BATCH = "modern-footnote-recover-2026-06-23"

# Each entry restructures one opinion. Fields:
#   oid, num, call_para, call_old, call_new, body_old (excised verbatim),
#   body_text (appended verbatim, period form), pdf (authority)
ENTRIES = [
    dict(
        oid=20075, num=1, call_para=6,
        call_old="§ 29-32.1-09,1 which",
        call_new="§ 29-32.1-09,[1] which",
        body_old=(
            " 1 Section 29-32.1-09, N.D.C.C., was amended effective Aug. 1, 2023, "
            "to codify summary disposition (akin to summary judgment) at N.D.C.C. "
            "§ 29-32.1-09.1 and retain summary dismissal, akin to dismissal for "
            "failure to state a claim, at N.D.C.C. § 29-32.1-09. 2023 N.D. Sess. "
            "Laws ch. 307."),
        body_text=(
            "Section 29-32.1-09, N.D.C.C., was amended effective Aug. 1, 2023, to "
            "codify summary disposition (akin to summary judgment) at N.D.C.C. "
            "§ 29-32.1-09.1 and retain summary dismissal, akin to dismissal for "
            "failure to state a claim, at N.D.C.C. § 29-32.1-09. 2023 N.D. Sess. "
            "Laws ch. 307."),
        pdf="pdfs/2024/2024ND99.pdf",
    ),
]


def words(s):
    return sorted(re.findall(r"[A-Za-z]+", s))


def restore(text, e):
    if text.count(e["call_old"]) != 1:
        raise SystemExit(f"{e['oid']}: call_old not unique ({text.count(e['call_old'])})")
    if text.count(e["body_old"]) != 1:
        raise SystemExit(f"{e['oid']}: body_old not unique ({text.count(e['body_old'])})")
    text = text.replace(e["call_old"], e["call_new"])
    text = text.replace(e["body_old"], "")
    text = text.rstrip("\n") + f"\n\n{e['num']}\n\n. {e['body_text']}"
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    import ndcourts_mcp.proofread as pr
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    for e in ENTRIES:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (e["oid"],)).fetchone()[0]
        new = restore(old, e)
        assert words(new) == words(old), f"{e['oid']}: word multiset changed!"
        st = pr.footnote_structure(new)
        cpar = st["call_para"].get(e["num"])
        has_body = any(n == e["num"] for n, _, _ in st["bodies"])
        ok = cpar == e["call_para"] and has_body
        print(f"  id{e['oid']} n.{e['num']}: parser -> call ¶{cpar}, body={has_body}  {'OK' if ok else 'FAIL'}")
        if args.apply and ok:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, e["oid"]))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, BATCH, e["oid"], "text_content.footnote_recover",
                 f"footnote {e['num']} body mashed inline at ¶{e['call_para']}; call OCR'd to attached digit",
                 f"call denoted [{e['num']}]; body relocated verbatim to opinion end (period form); call_para ¶{e['call_para']}",
                 f"ND PDF: {e['pdf']}"))
        elif args.apply:
            raise SystemExit(f"{e['oid']}: parser check FAILED — not applying")
    if args.apply:
        con.commit(); print(f"APPLIED + logged (batch {BATCH}).")
    else:
        print("DRY-RUN — re-run with --apply.")


if __name__ == "__main__":
    main()
