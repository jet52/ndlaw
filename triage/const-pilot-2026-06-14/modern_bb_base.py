#!/usr/bin/env python3
"""Modern reconstruction via 1981 Blue Book as base (the high-leverage path).

74 of 96 amended modern provisions have exactly ONE post-1981 amendment. For
those, the [1981, d1) prior version IS the 1981 text — and the 1981 Blue Book
(modern art./§ numbering, stable since the reorg) carries it. So we reconstruct
the prior from the BB directly: no redline read, no CAA PDF.

  prior   [1981-01-01, d1-1] = 1981 BB (art ROMAN, § N)
  current [d1, open]         = DB text (authoritative)

Guard: skip if the BB section is OCR-degraded (ocr_quality>0.15) -> redline path.
A provision CREATED post-1981 has no BB entry -> single version already correct.
"""
import re
import sqlite3
import difflib
from pathlib import Path
from datetime import date, timedelta

BB = (Path.home() / "refs/nd/const/processed/1981_blue-book_constitution.md").read_text()
DB = "/tmp/const-scratch.db"
REORG = "1981-01-01"

ROMANS = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI","XVII"]
# article title -> roman, for headers that print the title without a number
TITLE2ART = {
    "DECLARATIONOFRIGHTS":"I", "POWERSRESERVEDTOTHEPEOPLE":"III",
    "LEGISLATIVEBRANCH":"IV", "EXECUTIVEBRANCH":"V", "JUDICIALBRANCH":"VI",
    "POLITICALSUBDIVISIONS":"VII", "EDUCATION":"VIII", "TRUSTLANDS":"IX",
    "FINANCEANDPUBLICDEBT":"X", "GENERALPROVISIONS":"XI",
}


def squash(s):
    return re.sub(r"[^A-Za-z]", "", s).upper()


def parse_bb():
    """{(art_roman, secnum): text} from the 1981 BB, tolerant of OCR letter-spacing."""
    secs, art, cur, buf = {}, None, None, []
    art_hdr = re.compile(r"^[#*\s]*ARTICL\s*E\s+([IVXL ]+?)\s*$", re.I)
    sec_hdr = re.compile(r"^[-*#\s]*Section\s+([0-9]+)\s*[.,]", re.I)
    for line in BB.splitlines():
        sq = squash(line)
        m = art_hdr.match(line)
        if m and squash(m.group(1)) in ROMANS:
            if cur and art:
                secs.setdefault((art, cur), " ".join(buf).strip())
            art, cur, buf = squash(m.group(1)), None, []
            continue
        # title-only article header (e.g. "JUDICIAL BRANCH")
        if sq in TITLE2ART:
            if cur and art:
                secs.setdefault((art, cur), " ".join(buf).strip())
            art, cur, buf = TITLE2ART[sq], None, []
            continue
        sm = sec_hdr.match(line)
        if sm and art:
            if cur:
                secs.setdefault((art, cur), " ".join(buf).strip())
            cur = int(sm.group(1))
            buf = [sec_hdr.sub("", line, count=1)]
        elif cur:
            buf.append(line)
    if cur and art:
        secs.setdefault((art, cur), " ".join(buf).strip())
    return secs


def ocrq(t):
    toks = re.findall(r"[A-Za-z]+", t)
    return sum(1 for x in toks if len(x) == 1) / max(len(toks), 1)


def main():
    bb = parse_bb()
    con = sqlite3.connect(DB)
    # single-amendment modern provisions
    rows = con.execute("""
        SELECT p.id, p.citation, v.id, v.effective_start, v.text_content,
               (SELECT min(a.effective_date) FROM amendments a WHERE a.provision_id=p.id AND a.effective_date>=?),
               (SELECT count(*) FROM amendments a WHERE a.provision_id=p.id AND a.effective_date>=?)
        FROM provisions p JOIN provision_versions v ON v.id=p.current_version_id
        WHERE p.corpus='const' AND p.citation LIKE '%art.%' AND p.citation NOT LIKE '%amend%'
    """, (REORG, REORG)).fetchall()
    con.close()

    cls = {"BB_CLEAN": [], "BB_DEGRADED": [], "NO_BB_CREATED": [], "MULTI": [], "NOPARSE": []}
    for pid, cite, vid, vstart, cur, d1, namd in rows:
        if not namd:
            continue
        if namd > 1:
            cls["MULTI"].append(cite); continue
        m = re.search(r"art\.\s+([IVXL]+),\s+§\s+(\d+)", cite)
        if not m:
            cls["NOPARSE"].append(cite); continue
        key = (m.group(1), int(m.group(2)))
        if key not in bb:
            cls["NO_BB_CREATED"].append((cite, d1)); continue
        prior = bb[key]
        q = ocrq(prior)
        if q > 0.15:
            cls["BB_DEGRADED"].append((cite, round(q, 2))); continue
        sim = difflib.SequenceMatcher(None, re.sub(r"[^a-z0-9]","",cur.lower()),
                                      re.sub(r"[^a-z0-9]","",prior.lower()), autojunk=False).ratio()
        cls["BB_CLEAN"].append((cite, d1, vid, pid, vstart, prior, sim))

    print(f"single-amendment modern provisions, BB-as-base triage:")
    print(f"  BB_CLEAN (reconstructable now): {len(cls['BB_CLEAN'])}")
    print(f"  BB_DEGRADED (OCR>0.15 -> redline/native): {len(cls['BB_DEGRADED'])}")
    print(f"  NO_BB_CREATED (created post-1981, single ver correct): {len(cls['NO_BB_CREATED'])}")
    print(f"  MULTI (2-3 amendments, need intermediates): {len(cls['MULTI'])}")
    print(f"  NOPARSE: {len(cls['NOPARSE'])}")
    print("\n  BB_DEGRADED:", cls["BB_DEGRADED"][:20])
    print("\n  sample BB_CLEAN (cite, d1, similarity-to-current):")
    for cite, d1, vid, pid, vstart, prior, sim in cls["BB_CLEAN"][:15]:
        print(f"    {cite:<26} d1={d1}  sim={sim:.2f}")
    return cls


if __name__ == "__main__":
    main()
