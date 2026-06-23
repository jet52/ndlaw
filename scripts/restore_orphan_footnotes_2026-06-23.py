"""Restore citation-graph-confirmed footnotes whose BODY is present as a
number-less period orphan (``\\n\\n. body``) — the ndcourts-markdown lineage
dropped the body's number, and the call superscript survived either attached to
the prose (``past.2``) or not at all.

Per the ratified convention (2026-06-23) the call is denoted inline ``[N]`` at
the exact call site (located from an authoritative source: the ND PDF, the court
archive HTML, or the West N.W.2d text), and the orphan body is numbered in place
so the standalone parser links body -> ¶ (resolving call_para from the unique
inline ``[N]``). The body stays where it is (already in the footnote cluster);
only structure markers are added — asserted: identical alphabetic-token sequence.

Restores ONLY the citation-confirmed footnote in each opinion (siblings without
external confirmation are left for the separate hand-verified backlog pass).
Idempotent (skips an entry whose call is already bracketed). Dry-run by default;
``--apply`` writes + logs one ``text_content.footnote_number`` row each.
"""
import argparse
import re
import sqlite3
from datetime import datetime, timezone

BATCH = "orphan-footnote-restore-2026-06-23"

# Each entry: oid, num, call_para
#   call_old / call_new : bracket (or insert) the inline [N] call (call_old unique)
#   orphan_anchor       : body text right after "\n\n. " (unique); number inserted
#   authority           : source that fixed the call site + confirms the body
ENTRIES = [
    dict(oid=12353, num=2, call_para=17,
         call_old="arrested in the past.2", call_new="arrested in the past.[2]",
         orphan_anchor="A.E. did not raise a due process argument",
         authority="archive/1997/960079.htm (court HTML: call <sup>(2)</sup> at end of ¶17)"),
    dict(oid=12955, num=2, call_para=32,
         call_old="finding on visitation is not clearly erroneous.2",
         call_new="finding on visitation is not clearly erroneous.[2]",
         orphan_anchor="Ame asserted on appeal the visitation provisions",
         authority="archive/1999/980268.htm (court HTML: call <sup>(2)</sup> at end of ¶32)"),
]


def words(s):
    return sorted(re.findall(r"[A-Za-z]+", s))


def restore(text, e):
    if text.count(e["call_old"]) != 1:
        raise SystemExit(f"{e['oid']}: call_old not unique ({text.count(e['call_old'])})")
    orphan = f"\n\n. {e['orphan_anchor']}"
    if text.count(orphan) != 1:
        raise SystemExit(f"{e['oid']}: orphan anchor not unique ({text.count(orphan)})")
    new = text.replace(e["call_old"], e["call_new"])
    new = new.replace(orphan, f"\n\n{e['num']}\n\n. {e['orphan_anchor']}")
    return new


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
        if e["call_new"] in old and e["call_old"] not in old:
            print(f"  id{e['oid']} n.{e['num']}: already applied — skipping")
            continue
        new = restore(old, e)
        assert words(new) == words(old), f"{e['oid']}: alphabetic-token sequence changed!"
        if new.count(e["call_new"][-4:]) and new.count("[%d]" % e["num"]) != 1:
            raise SystemExit(f"{e['oid']}: inline [{e['num']}] not unique after edit")
        st = pr.footnote_structure(new)
        cpar = st["call_para"].get(e["num"])
        has_body = any(n == e["num"] for n, _, _ in st["bodies"])
        ok = cpar == e["call_para"] and has_body
        print(f"  id{e['oid']} n.{e['num']}: parser -> call ¶{cpar}, body={has_body}  {'OK' if ok else 'FAIL'}")
        if not ok and args.apply:
            raise SystemExit(f"{e['oid']}: parser check FAILED — not applying")
        if args.apply and ok:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, e["oid"]))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, BATCH, e["oid"], "text_content.footnote_number",
                 f"footnote {e['num']} body present as number-less period orphan; call survived attached",
                 f"numbered the orphan body + denoted call [{e['num']}] inline at ¶{e['call_para']}",
                 e["authority"]))
    if args.apply:
        con.commit(); print(f"APPLIED + logged (batch {BATCH}).")
    else:
        print("DRY-RUN — re-run with --apply.")


if __name__ == "__main__":
    main()
