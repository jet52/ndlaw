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
    dict(oid=12737, num=2, call_para=21,
         call_old="32-12.2-04(1)2.", call_new="32-12.2-04(1)[2].",
         orphan_anchor="The trial court ruled Messiha",
         authority="archive/1998/980007.htm (court HTML: call <sup>(2)</sup> after § 32-12.2-04(1) in ¶21)"),
    dict(oid=13029, num=3, call_para=15,
         call_old=").3\n\n[¶ 16]", call_new=").[3]\n\n[¶ 16]",
         orphan_anchor="Although not applicable retroactively here",
         authority="archive/1999/990104.htm (court HTML: call <sup>(3)</sup> at end of ¶15)"),
    # 1999 ND 154: 8 footnotes, all number-dropped (period orphans) with call
    # digits surviving attached. orphan-i == fn-i verified vs archive FN_N_ bodies.
    # fn4 & fn8 are citation-confirmed; the rest restored for contiguity (1-8).
    dict(oid=12949, num=1, call_para=3,
         call_old="administrative proceeding.1", call_new="administrative proceeding.[1]",
         orphan_anchor="On May 29, 1998, the Bureau rejected the ALJ",
         authority="archive/1999/980354.htm FN_1_ (call <sup>(1)</sup> ¶3)"),
    dict(oid=12949, num=2, call_para=4,
         call_old="Alford*plea2 to", call_new="Alford*plea[2] to",
         orphan_anchor="*See North Carolina v. Alford",
         authority="archive/1999/980354.htm FN_2_ (call <sup>(2)</sup> ¶4)"),
    dict(oid=12949, num=3, call_para=4,
         call_old="and Stewart appealed.3", call_new="and Stewart appealed.[3]",
         orphan_anchor="In *State v. Van Beek",
         authority="archive/1999/980354.htm FN_3_ (call <sup>(3)</sup> ¶4)"),
    dict(oid=12949, num=4, call_para=8,
         call_old="interviewed him in December 1996.4", call_new="interviewed him in December 1996.[4]",
         orphan_anchor="Insofar as Steward",
         authority="archive/1999/980354.htm FN_4_ (call <sup>(4)</sup> ¶8) [citation-confirmed]"),
    dict(oid=12949, num=5, call_para=10,
         call_old="his right to counsel.5", call_new="his right to counsel.[5]",
         orphan_anchor="We express no opinion about whether the circumstances",
         authority="archive/1999/980354.htm FN_5_ (call <sup>(5)</sup> ¶10)"),
    dict(oid=12949, num=6, call_para=15,
         call_old="N.D.C.C.,6 provides", call_new="N.D.C.C.,[6] provides",
         orphan_anchor="The Stale alleged Stewart violated N.D.C.C.",
         authority="archive/1999/980354.htm FN_6_ (call <sup>(6)</sup> ¶15)"),
    dict(oid=12949, num=7, call_para=16,
         call_old="§ 673.7", call_new="§ 673.[7]",
         orphan_anchor="1975 N.D. Sess. Laws ch. 106, § 673 repealed",
         authority="archive/1999/980354.htm FN_7_ (call <sup>(7)</sup> ¶16)"),
    dict(oid=12949, num=8, call_para=25,
         call_old="prosecution of Stewart.8", call_new="prosecution of Stewart.[8]",
         orphan_anchor="Stewart has not marshaled a separate double jeopardy",
         authority="archive/1999/980354.htm FN_8_ (call <sup>(8)</sup> ¶25) [citation-confirmed]"),
    # 1999 ND 156: 3 number-dropped orphans, call digits attached. orphan-i==fn-i
    # vs archive FN_N_. fn1 citation-confirmed (call ¶ was unknown -> ¶8 from the
    # surviving attached digit); fns 2-3 restored for contiguity.
    dict(oid=12945, num=1, call_para=8,
         call_old="to enforce the first order.1", call_new="to enforce the first order.[1]",
         orphan_anchor="In 1995, the legislature enacted UIFSA",
         authority="archive/1999/990023.htm FN_1_ (call <sup>(1)</sup> ¶8) [citation-confirmed]"),
    dict(oid=12945, num=2, call_para=8,
         call_old="§ 14-12.1-312 to", call_new="§ 14-12.1-31[2] to",
         orphan_anchor="Section 14-12.1-31, N.D.C.C., provided",
         authority="archive/1999/990023.htm FN_2_ (call <sup>(2)</sup> ¶8)"),
    dict(oid=12945, num=3, call_para=11,
         call_old="per month on his arrearages.3", call_new="per month on his arrearages.[3]",
         orphan_anchor="This record also includes an August 31, 1988, letter",
         authority="archive/1999/990023.htm FN_3_ (call <sup>(3)</sup> ¶11)"),
    # Contiguity pass: sibling fn1/fn2 orphans in opinions where only the cited
    # footnote was restored earlier (user's "no skipped footnote numbers" rule).
    # Each call digit survives attached; orphan-i==fn-i by sequence + archive.
    dict(oid=12353, num=1, call_para=10,
         call_old="through available programs.1", call_new="through available programs.[1]",
         orphan_anchor="It should be noted that there was some confusion",
         authority="archive/1997/960079.htm FN1 (call <sup>(1)</sup> ¶10) [contiguity]"),
    dict(oid=12955, num=1, call_para=28,
         call_old="and prior caselaw.1", call_new="and prior caselaw.[1]",
         orphan_anchor="We recognize the difficulty presented to the trial court",
         authority="archive/1999/980268.htm FN1 (call <sup>(1)</sup> ¶28) [contiguity]"),
    dict(oid=12737, num=1, call_para=1,
         call_old="and Sally Page.1", call_new="and Sally Page.[1]",
         orphan_anchor="Clifford and Baker each served as UND",
         authority="archive/1998/980007.htm FN1 (call <sup>(1)</sup> ¶1) [contiguity]"),
    dict(oid=13029, num=1, call_para=8,
         call_old="and March 5, 1999.1", call_new="and March 5, 1999.[1]",
         orphan_anchor="After the proceedings on November 20, 1998",
         authority="archive/1999/990104.htm FN1 (call <sup>(1)</sup> ¶8) [contiguity]"),
    dict(oid=13029, num=2, call_para=10,
         call_old="(1991),2 N.D.C", call_new="(1991),[2] N.D.C",
         orphan_anchor="The Legislature amended N.D.C.C. ch. 27-20 effective",
         authority="archive/1999/990104.htm FN2 (call <sup>(2)</sup> ¶10) [contiguity]"),
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
