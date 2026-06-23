"""Apply edit-pair footnote proposals behind hard gates.

The refined agent contract emits, per footnote, exact ``old_exact -> new_exact``
edit pairs (each self-verified unique in the DB), plus an optional verbatim
``append_body`` for genuinely-absent footnotes with a ``body_present_in_db``
self-check. This applier just replaces + gates; it trusts NO claim it can't
re-verify.

Per opinion (atomic): apply every edit pair (each old_exact must occur exactly
once); append bodies only when the contiguous-window false-absent gate agrees
they're absent. Then GATE: alphabetic-token multiset == old (+ appended body
words); footnote_structure detects each proposed num; call_para matches where
given. Commit only if all gates pass; else skip + report. Dry-run by default.
"""
import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone

BATCH = "footnote-editpair-apply-2026-06-23"


def words(s):
    return sorted(re.findall(r"[A-Za-z]+", s))


def marker_only(old, new):
    """An edit may only change footnote-marker mechanism: brackets, the digit,
    periods, and whitespace. Letters and other punctuation (commas, dashes,
    quotes, parens, §) must be IDENTICAL — catches agent over-corrections like
    turning a comma into a period."""
    k = lambda s: re.sub(r"[\[\]\d.\s]", "", s)
    return k(old) == k(new)


def body_present(text, body):
    tn = " ".join(re.findall(r"[a-z0-9]+", text.lower()))
    w = re.findall(r"[a-z0-9]+", body.lower())
    return any(len(g) > 40 and g in tn
               for g in (" ".join(w[i:i + 12]) for i in range(0, max(1, len(w) - 12), 6)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("proposals")
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    import ndcourts_mcp.proofread as pr
    data = json.load(open(args.proposals))
    if isinstance(data, dict):
        data = data.get("result", data)
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    applied = skipped = 0
    skips = []
    for o in data:
        oid = o["opinion_id"]
        row = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        if not row:
            continue
        old = row[0]
        text = old
        fns = [f for f in o.get("footnotes", []) if f.get("action") not in ("already_clean", "not_a_footnote")]
        if not fns:
            continue
        ok, reason, added = True, "", []
        want_nums, want_cp = [], {}
        for f in fns:
            num = f["num"]
            want_nums.append(num)
            if f.get("call_para") is not None:
                want_cp[num] = f["call_para"]
            for ed in f.get("edits", []) or []:
                oe, ne = ed.get("old_exact", ""), ed.get("new_exact", "")
                if not oe or text.count(oe) != 1:
                    ok, reason = False, f"fn{num} edit old_exact count={text.count(oe) if oe else 'empty'}"
                    break
                if not marker_only(oe, ne):
                    ok, reason = False, f"fn{num} edit changes non-marker chars: {oe!r}->{ne!r}"
                    break
                text = text.replace(oe, ne)
            if not ok:
                break
            ab = f.get("append_body", "") or ""
            if ab:
                if f.get("body_present_in_db") or body_present(text, ab):
                    ok, reason = False, f"fn{num} append_body but body present (false-absent)"
                    break
                text = text.rstrip("\n") + f"\n\n{num}\n\n. {ab.strip()}"
                added += words(ab)
        if ok and words(text) != sorted(words(old) + added):
            ok, reason = False, "word-multiset gate"
        if ok:
            st = pr.footnote_structure(text)
            det = {n for n, _, _ in st["bodies"]}
            if not set(want_nums) <= det:
                ok, reason = False, f"parser gate (det={sorted(det)} want={sorted(set(want_nums))})"
            else:
                for n, cp in want_cp.items():
                    got = st["call_para"].get(n)
                    if got is not None and got != cp:
                        ok, reason = False, f"call_para gate fn{n} got{got}!=want{cp}"
                        break
        if not ok:
            skipped += 1
            skips.append((oid, o.get("cite", "")[:40], reason))
            continue
        applied += 1
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (text, oid))
            for f in fns:
                con.execute(
                    "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (ts, BATCH, oid, "text_content.footnote_editpair",
                     f"footnote {f['num']} {f.get('action')}",
                     f"applied edit-pairs/append; call_para {f.get('call_para')}",
                     "agent edit-pair proposal + deterministic gate"))
        else:
            print(f"  OK id{oid} {o.get('cite','')[:34]}: fns {want_nums}")
    print(f"\napplied: {applied}  skipped: {skipped}")
    for s in skips[:50]:
        print("  skip", s)
    if args.apply:
        con.commit()
        print(f"COMMITTED batch {BATCH}.")


if __name__ == "__main__":
    main()
