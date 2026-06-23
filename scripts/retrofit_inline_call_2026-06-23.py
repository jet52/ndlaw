"""Retrofit the two footnotes restored earlier this arc (1999 ND 2, 2011 ND 122)
from the bare-line call marker to the ratified inline-[N] convention.

Both opinions' call digits actually survived attached in the prose (`fact1`,
`costs.1`); the earlier Route A restore added a redundant bare-line call marker.
This brackets the attached digit -> `[N]` (the standalone parser resolves
call_para from the unique inline [N]) and removes the now-redundant bare-line
marker. Body numbering is unchanged. Asserted: identical alphabetic-token
sequence (only a digit bracketed + a bare-digit line removed). Idempotent.
"""
import argparse
import re
import sqlite3
from datetime import datetime, timezone

BATCH = "footnote-inline-call-retrofit-2026-06-23"

# oid, num, call_para, call_old/new (bracket attached digit), bare_old/new (drop marker)
ENTRIES = [
    dict(oid=12808, num=1, call_para=5,
         call_old="material fact1 and:", call_new="material fact[1] and:",
         bare_old="Insurance Company.\n1\n\n[¶ 6]", bare_new="Insurance Company.\n\n[¶ 6]"),
    dict(oid=15640, num=1, call_para=1,
         call_old="costs.1 We", call_new="costs.[1] We",
         bare_old="Enzminger Steel.\n\nI\n\n1\n\n[¶ 2]", bare_new="Enzminger Steel.\n\nI\n\n[¶ 2]"),
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
    for e in ENTRIES:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (e["oid"],)).fetchone()[0]
        if e["call_new"] in old and e["call_old"] not in old:
            print(f"  id{e['oid']} n.{e['num']}: already retrofit — skipping"); continue
        for key in ("call_old", "bare_old"):
            if old.count(e[key]) != 1:
                raise SystemExit(f"id{e['oid']}: {key} not unique ({old.count(e[key])})")
        new = old.replace(e["call_old"], e["call_new"]).replace(e["bare_old"], e["bare_new"])
        assert words(new) == words(old), f"id{e['oid']}: alphabetic-token sequence changed!"
        st = pr.footnote_structure(new)
        cpar = st["call_para"].get(e["num"])
        has_body = any(n == e["num"] for n, _, _ in st["bodies"])
        nbr = new.count(f"[{e['num']}]")
        ok = cpar == e["call_para"] and has_body and nbr == 1
        print(f"  id{e['oid']} n.{e['num']}: call ¶{cpar}, body={has_body}, [{e['num']}]x{nbr}  {'OK' if ok else 'FAIL'}")
        if not ok and args.apply:
            raise SystemExit(f"id{e['oid']}: check FAILED")
        if args.apply and ok:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, e["oid"]))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, BATCH, e["oid"], "text_content.footnote_marker",
                 f"footnote {e['num']} call as bare-line marker (Route A)",
                 f"retrofit to inline [{e['num']}] at attached call site ¶{e['call_para']}; redundant bare-line removed",
                 "convention alignment (inline-[N], 2026-06-23)"))
    if args.apply:
        con.commit(); print(f"APPLIED + logged (batch {BATCH}).")
    else:
        print("DRY-RUN — re-run with --apply.")


if __name__ == "__main__":
    main()
