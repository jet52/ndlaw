#!/usr/bin/env python3
"""Snapshot-diff harness — the historical-layer acceptance test (#5).

Reconstruct the constitution as of date T from the DB (1889-numbering historical
layer, version-effective-at-T), and diff each section against the printed
compilation published near T (1925 official / 1954 / 1973 Blue Books, on disk).

A green diff = the point-in-time reconstruction matches the official printed text.
Mismatches surface wrong effective dates, missed amendments, or text errors.

Comparison is OCR/annotation tolerant: the DB's clean section text must be a
normalized substring of the compilation's section text (which may carry inline
case-citation annotations, esp. 1925), else a high fuzzy ratio on the best window.
"""
import re
import sqlite3
import difflib
from pathlib import Path

PROC = Path.home() / "refs/nd/const/processed"
DB = Path("/tmp/const-scratch.db")

COMPS = {
    "1925": ("1925_official_constitution.md", r"^[-*\s]*§\s*(\d+)\s*[.,]", "1925-07-01"),
    "1954": ("1954_blue-book_constitution.md", r"^[-*\s]*Section\s+(\d+)\s*[.,]", "1954-07-01"),
    "1973": ("1973_blue-book_constitution.md", r"^[-*\s]*Section\s+(\d+)\s*[.,]", "1973-07-01"),
}


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def parse_comp(fname, secre):
    """Accumulate each section from its '§ N.'/'Section N.' marker until the next
    one (sections span multiple lines). Extra text (article headers, inline case
    annotations) is harmless — the DB-text-⊆-compilation containment check tolerates
    a longer compilation section."""
    pat = re.compile(secre)
    secs, cur, buf = {}, None, []
    for line in (PROC / fname).read_text().splitlines():
        m = pat.match(line)
        if m:
            if cur is not None:
                secs.setdefault(cur, " ".join(buf).strip())
            cur, buf = int(m.group(1)), [pat.sub("", line, count=1)]
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        secs.setdefault(cur, " ".join(buf).strip())
    return secs


def db_at(con, T):
    rows = con.execute("""
        SELECT p.citation, p.status, vv.text_content
        FROM provisions p JOIN provision_versions vv ON vv.provision_id=p.id
        WHERE p.corpus='const' AND p.citation GLOB 'N.D. Const. § [0-9]*'
          AND vv.effective_start<=? AND (vv.effective_end IS NULL OR vv.effective_end=''
              OR vv.effective_end>=?)
    """, (T, T)).fetchall()
    out = {}
    for cite, status, txt in rows:
        m = re.search(r"§ (\d+)\b", cite)
        if m:
            out[int(m.group(1))] = txt
    return out


def best_ratio(dn, cn):
    """Coverage: fraction of the DB section text found in the compilation section.
    Robust to the compilation being longer (annotations) and to scattered OCR
    char errors — what we want is 'is our text present in the printed text'."""
    if not dn or not cn:
        return 0.0
    # autojunk=False: the default discards common chars on long strings, which
    # destroys matching on 200+ char constitutional sections.
    sm = difflib.SequenceMatcher(None, dn, cn, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    return matched / len(dn)


def run(year):
    fname, secre, T = COMPS[year]
    comp = parse_comp(fname, secre)
    con = sqlite3.connect(DB)
    db = db_at(con, T)
    con.close()

    cls = {"MATCH": 0, "NEAR": 0, "MISMATCH": 0, "REPEALED_OK": 0, "NOT_IN_COMP": 0}
    mism = []
    for n, dbtext in sorted(db.items()):
        repealed = dbtext.strip().lower().startswith("[repealed")
        if n not in comp:
            if repealed:
                cls["REPEALED_OK"] += 1            # gone from print, repealed in DB — consistent
            else:
                cls["NOT_IN_COMP"] += 1
            continue
        comp_repealed = bool(re.search(r"repeal|supersed", comp[n], re.I))
        if repealed and comp_repealed:
            cls["REPEALED_OK"] += 1                # both agree the section is gone
            continue
        dn, cn = norm(dbtext), norm(comp[n])
        if not dn:
            continue
        if dn in cn:
            cls["MATCH"] += 1
        else:
            r = best_ratio(dn, cn)
            if r >= 0.92:
                cls["NEAR"] += 1
            else:
                cls["MISMATCH"] += 1
                mism.append((n, round(r, 2), dbtext[:55], comp[n][:55]))
    return comp, db, cls, mism


if __name__ == "__main__":
    import sys
    years = sys.argv[1:] or ["1925", "1954", "1973"]
    for year in years:
        comp, db, cls, mism = run(year)
        print(f"\n===== SNAPSHOT-DIFF {year} (T={COMPS[year][2]}) =====")
        print(f"  compilation sections parsed: {len(comp)};  DB sections at T: {len(db)}")
        for k in ("MATCH", "NEAR", "REPEALED_OK", "MISMATCH", "NOT_IN_COMP"):
            print(f"  {k:<12} {cls[k]}")
        if mism:
            print(f"  --- MISMATCHES ({len(mism)}) ---")
            for n, r, d, c in mism[:30]:
                print(f"   §{n:<4} ratio={r}\n       DB:   {d}\n       comp: {c}")
