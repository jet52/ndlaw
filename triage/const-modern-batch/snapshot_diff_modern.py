#!/usr/bin/env python3
"""Snapshot-diff harness — the MODERN-layer acceptance test.

The historical harness (const-pilot/snapshot_diff.py) validates the 1889-numbering
layer against the 1925/1954/1973 printed compilations. This is its modern-scheme
counterpart: reconstruct each modern provision (`art. ROMAN, § N`) as of date T from
the scratch DB (version effective at T), and diff against a compilation in the modern
art./§ scheme published near T.

Only one post-reorg printed compilation is on disk: the **1981 Blue Book**, which
prints the just-renumbered constitution. So T=1981-01-01 is the anchor test — it
validates:
  • the ~105 unchanged-since-reorg provisions (must match the 1981 BB),
  • every reconstructed chain's [1981, d1) HEAD (the rolled-back prior text), and
  • that created-later provisions are correctly ABSENT at 1981.
(Add more (compilation, T) pairs to COMPS as mid-era sources are acquired.)

OCR tolerance: the 1981 BB has heavy letter-spacing ("p ai d ou t") and scattered
char corruption. norm() strips all non-alphanumerics, which collapses the
letter-spacing automatically; containment + a fuzzy ratio absorb the char errors.
A green diff = the modern point-in-time reconstruction matches the printed text.
"""
import re
import sqlite3
import difflib
from pathlib import Path

PROC = Path.home() / "refs/nd/const/processed"
DB = Path("/tmp/const-scratch.db")

# year -> (filename, T, coverage_ceiling). The 1981 BB markdown on disk is TRUNCATED
# at art. XII § 1 — provisions past that point have no witness (not reconstruction
# errors). coverage_ceiling = (article_roman, last_section) the compilation reaches.
COMPS = {
    "1981": ("1981_blue-book_constitution.md", "1981-01-01", ("XII", 1)),
}

ART_ORDER = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI",
             "XII", "XIII", "XIV", "XV", "XVI"]


def beyond_ceiling(key, ceiling):
    """True if provision (art, sec) is past the compilation's coverage ceiling."""
    art, sec = key
    cart, csec = ceiling
    if art not in ART_ORDER:
        return True
    if ART_ORDER.index(art) > ART_ORDER.index(cart):
        return True
    if art == cart and sec > csec:
        return True
    return False

ROMAN = "IVXLCM"


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def section_num(line):
    """Section number at the start of a line, tolerant of OCR letter-spacing
    ('Sectio n 1 .'), bold (**), and list markers (-). None if not a marker."""
    s = re.sub(r"^[-*\s]+", "", line)          # strip leading list/bold/whitespace
    head = re.sub(r"\s+", "", s[:24])          # squish letter-spacing in the prefix
    m = re.match(r"\*{0,2}Section\*{0,2}(\d+)\b", head)
    return int(m.group(1)) if m else None


def article_of(heading_line):
    """Return the article roman from a heading line, or None. OCR letter-spaces
    'ARTICLE' ('ARTICL E I V'), so squish to letters and match the trailing roman."""
    squished = re.sub(r"[^A-Za-z]", "", heading_line.upper())
    m = re.search(rf"ARTICLE([{ROMAN}]+)$", squished)
    return m.group(1) if m else None


def parse_comp(fname):
    """Parse the compilation into {(article_roman, section_num): text}, tracking the
    current article from heading lines and sections from 'Section N.' markers."""
    secs, art, cur, buf = {}, None, None, []

    def flush():
        if art and cur is not None:
            secs.setdefault((art, cur), " ".join(buf).strip())

    for line in (PROC / fname).read_text().splitlines():
        if line.lstrip().startswith("#"):
            a = article_of(line)
            if a:
                flush(); cur, buf = None, []
                art = a
                continue
        n = section_num(line)
        if n is not None:
            flush()
            cur = n
            buf = [line]   # whole line; the marker text is harmless under containment
        elif cur is not None:
            buf.append(line)
    flush()
    return secs


def db_at(con, T):
    """{(article_roman, section_num): text} for modern reorg provisions effective at T."""
    rows = con.execute("""
        SELECT p.citation, vv.text_content
        FROM provisions p JOIN provision_versions vv ON vv.provision_id=p.id
        WHERE p.corpus='const' AND p.citation LIKE 'N.D. Const. art. %§%'
          AND p.citation NOT LIKE '%amend%'
          AND vv.effective_start<=? AND (vv.effective_end IS NULL OR vv.effective_end=''
              OR vv.effective_end>=?)
    """, (T, T)).fetchall()
    out = {}
    for cite, txt in rows:
        m = re.search(rf"art\.\s+([{ROMAN}]+),\s+§\s+(\d+)", cite)
        if m:
            out[(m.group(1), int(m.group(2)))] = txt
    return out


def best_ratio(dn, cn):
    if not dn or not cn:
        return 0.0
    sm = difflib.SequenceMatcher(None, dn, cn, autojunk=False)
    return sum(b.size for b in sm.get_matching_blocks()) / len(dn)


def run(year):
    fname, T, ceiling = COMPS[year]
    comp = parse_comp(fname)
    con = sqlite3.connect(DB)
    db = db_at(con, T)
    con.close()
    cls = {"MATCH": 0, "NEAR": 0, "MISMATCH": 0, "REPEALED_OK": 0,
           "NOT_IN_COMP": 0, "BEYOND_COVERAGE": 0}
    mism, missing = [], []
    for key, dbtext in sorted(db.items()):
        repealed = dbtext.strip().lower().startswith("[repealed")
        if key not in comp:
            if beyond_ceiling(key, ceiling):
                cls["BEYOND_COVERAGE"] += 1          # truncated witness — not an error
            elif repealed:
                cls["REPEALED_OK"] += 1
            else:
                cls["NOT_IN_COMP"] += 1
                missing.append(key)
            continue
        dn, cn = norm(dbtext), norm(comp[key])
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
                mism.append((key, round(r, 2), dbtext[:60], comp[key][:60]))
    return comp, db, cls, mism, missing


if __name__ == "__main__":
    import sys
    years = sys.argv[1:] or list(COMPS)
    for year in years:
        comp, db, cls, mism, missing = run(year)
        print(f"\n===== MODERN SNAPSHOT-DIFF {year} (T={COMPS[year][1]}) =====")
        print(f"  compilation (art,§) parsed: {len(comp)} (ceiling {COMPS[year][2][0]} §{COMPS[year][2][1]} — BB truncated);"
              f"  DB modern provisions at T: {len(db)}")
        ok = cls["MATCH"] + cls["NEAR"] + cls["REPEALED_OK"]
        witnessed = ok + cls["MISMATCH"] + cls["NOT_IN_COMP"]   # exclude beyond-coverage
        for k in ("MATCH", "NEAR", "REPEALED_OK", "MISMATCH", "NOT_IN_COMP", "BEYOND_COVERAGE"):
            print(f"  {k:<16} {cls[k]}")
        if witnessed:
            print(f"  match-or-near (within BB coverage): {ok}/{witnessed} = {100*ok/witnessed:.1f}%")
        if missing:
            print(f"  --- NOT_IN_COMP within coverage ({len(missing)}) [BB parse miss or real gap] ---")
            print("   ", ", ".join(f"{a}§{n}" for a, n in missing[:40]))
        if mism:
            print(f"  --- MISMATCHES ({len(mism)}) ---")
            for key, r, d, c in mism[:40]:
                print(f"   art {key[0]} §{key[1]:<3} ratio={r}\n       DB:   {d}\n       comp: {c}")
