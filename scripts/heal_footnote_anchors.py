"""Heal single-glyph byte-anchor misses in edit-pair footnote proposals.

Agents reliably reason about footnote structure but unreliably reproduce the
DB's Unicode glyphs: they emit ASCII " ' - and a plain space where the DB holds
curly “ ” ‘ ’, en/em dashes – —, or a non-breaking space (\\xa0). When an
``old_exact`` matches the DB ZERO times, this rebuilds it as a glyph-tolerant
regex and, IFF that matches the DB text EXACTLY ONCE, rewrites the edit to the
real bytes.

Correctness rests on one fact: every substituted glyph is a SINGLE character in
both forms (“=1 char, "=1 char, \\xa0=1 char, space=1 char), so the true match
``real`` has the SAME LENGTH as the agent's ``old_exact``. The marker change
(old->new) only touches brackets/digits/periods/whitespace and lives in a
contiguous span; the glyph swaps live at OTHER positions. So:

    p = len(common_prefix(old, new));  s = len(common_suffix(old, new))
    real_new = real[:p] + new[p : len(new)-s] + real[len(old)-s:]

takes the prefix/suffix (which may carry glyph swaps) from the REAL bytes and the
marker-bearing middle from the agent's ``new`` (pure ASCII markers). The gated
applier re-verifies marker_only, word-multiset, parser, and call_para after this,
so a bad heal cannot reach the DB — it just turns back into a skip.
"""
import argparse
import json
import re
import sqlite3


def tolerant(s):
    out = []
    for ch in s:
        if ch in '"“”':
            out.append('["“”]')
        elif ch in "'‘’":
            out.append("['‘’]")
        elif ch in "-–—":
            out.append('[-–—]')
        elif ch in " \xa0":
            out.append('[ \xa0]')
        else:
            out.append(re.escape(ch))
    return "".join(out)


def unique_match(text, oe):
    try:
        ms = list(re.finditer(tolerant(oe), text, re.DOTALL))
    except re.error:
        return None
    return ms[0].group(0) if len(ms) == 1 else None


def heal_edit(text, oe, ne):
    real = unique_match(text, oe)
    if real is None or len(real) != len(oe):
        return None
    p = 0
    while p < min(len(oe), len(ne)) and oe[p] == ne[p]:
        p += 1
    s = 0
    while s < min(len(oe), len(ne)) - p and oe[-1 - s] == ne[-1 - s]:
        s += 1
    real_new = real[:p] + ne[p:len(ne) - s] + real[len(oe) - s:]
    return real, real_new


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("proposals")
    ap.add_argument("out")
    ap.add_argument("--db", default="opinions.db")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    data = json.load(open(args.proposals))
    healed = miss = ok = 0
    for o in data:
        row = con.execute("SELECT text_content FROM opinions WHERE id=?", (o["opinion_id"],)).fetchone()
        if not row:
            continue
        text = row[0]
        for f in o.get("footnotes", []):
            for ed in f.get("edits", []) or []:
                oe, ne = ed.get("old_exact", ""), ed.get("new_exact", "")
                if not oe:
                    continue
                if text.count(oe) == 1:
                    ok += 1
                    continue
                if text.count(oe) > 1:
                    continue
                r = heal_edit(text, oe, ne)
                if r is None:
                    miss += 1
                    print(f"  MISS id{o['opinion_id']} fn{f['num']}: {oe[:50]!r}")
                    continue
                ed["old_exact"], ed["new_exact"] = r
                ed["verified_count"] = 1
                ed["_healed"] = True
                healed += 1
                print(f"  HEAL id{o['opinion_id']} fn{f['num']}: {oe[:34]!r} -> {r[0][:34]!r}")
    json.dump(data, open(args.out, "w"), ensure_ascii=False, indent=1)
    print(f"\nhealed: {healed}  already-unique: {ok}  unhealed: {miss}  -> {args.out}")


if __name__ == "__main__":
    main()
