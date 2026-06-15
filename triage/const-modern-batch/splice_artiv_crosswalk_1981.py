#!/usr/bin/env python3
"""art IV [1981,1986) crosswalk splice — the 13 clean shared sections (§§1-16).

Article IV was repealed-and-recreated 1986-12-01, REUSING the §1-16 citation numbers for
new content. So for [1981-01-01, 1986-11-30] the citation "art IV § N" denoted the OLD §N.
This prepends that prior version to each modern §N, with the OLD text sourced from the
validated historical layer (1889 numbering) via the derived crosswalk (ARTIV-CROSSWALK-PLAN.md):

    art IV §N(1981) -> 1889 §M : 1->52 3->27 4->28 6->30 7->31 8->32 9->33 10->34
                                 12->36 13->37 14->40 15->38 16->41

The [1981,1986) text == the 1889 §M version in force at 1980 (no art IV amendments 1981-86
except the §46 repeal); historical layer is validated (snapshot-diff green vs 1925/54/73).
Each match was confirmed against the 1981 Blue Book (the right-numbering witness, ratio>=0.92).

DEFERRED (not in this splice): §§ 2, 5, 11 — "[Unconstitutional.]" stubs in the 1981 BB
(judicially void, not textually repealed; representation is a separate judgment call). §§17-46
(repealed-only, no modern citation) are a separate optional pass.

Note on §§9/10/11: their [1981,1986) content is the OLD §9/§10 (representatives' term /
qualifications) — DISTINCT from the renumbered survivors (bribery/disqualification) that the
2026-06-15 renumber fix dated from 1986-12-01. So §9/§10 get: [1981,1986)=old → [1986-12-01,)=survivor.
(§11's [1981,1986) is a stub -> deferred.)

Idempotent (batch-scoped). Scratch only.
"""
import re
import sqlite3
import sys
import difflib
from pathlib import Path

DB = "/tmp/const-scratch.db"
BATCH = "modern-artiv-crosswalk-1981-1986-2026-06-15"
PRIOR_START, PRIOR_END = "1981-01-01", "1986-11-30"
XMAP = {1: 52, 3: 27, 4: 28, 6: 30, 7: 31, 8: 32, 9: 33, 10: 34,
        12: 36, 13: 37, 14: 40, 15: 38, 16: 41}


def sq(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def strip_prefix(t):
    return re.sub(r"^\s*Section\s+\d+(?:\.\d+)?\.\s*", "", t or "")


def bb_artiv():
    P = Path.home() / "refs/nd/const/processed/1981_blue-book_constitution.md"
    lines = P.read_text().splitlines()
    out, cur, buf = {}, None, []
    for i in range(142, 299):
        m = re.match(r"\*{0,2}Sectio?n(\d+)", re.sub(r"\s+", "", lines[i])[:12])
        if m:
            if cur is not None:
                out[cur] = " ".join(buf)
            cur = int(m.group(1)); buf = [lines[i]]
        elif cur is not None:
            buf.append(lines[i])
    if cur is not None:
        out[cur] = " ".join(buf)
    return out


def main(apply=False):
    con = sqlite3.connect(DB)
    bb = bb_artiv()
    plan, problems = [], []
    for n in sorted(XMAP):
        m = XMAP[n]
        cite = f"N.D. Const. art. IV, § {n}"
        prov = con.execute("SELECT id FROM provisions WHERE citation=?", (cite,)).fetchone()
        if not prov:
            problems.append(f"{cite}: no modern provision"); continue
        pid = prov[0]
        earliest = con.execute("SELECT effective_start FROM provision_versions WHERE provision_id=? "
                               "ORDER BY effective_start LIMIT 1", (pid,)).fetchone()[0]
        newtext = con.execute("SELECT text_content FROM provision_versions WHERE provision_id=? "
                              "ORDER BY effective_start LIMIT 1", (pid,)).fetchone()[0]
        hist = con.execute("SELECT pv.text_content FROM provisions p JOIN provision_versions pv "
                           "ON pv.provision_id=p.id WHERE p.citation=? ORDER BY pv.effective_start DESC "
                           "LIMIT 1", (f"N.D. Const. § {m}",)).fetchone()
        if not hist:
            problems.append(f"{cite}: historical § {m} not found"); continue
        oldtext = strip_prefix(hist[0])
        # gates
        if earliest == PRIOR_START:
            print(f"{cite}: already has a {PRIOR_START} version (idempotent skip)"); continue
        if earliest != "1986-12-01":
            problems.append(f"{cite}: earliest version starts {earliest}, expected 1986-12-01")
        if sq(oldtext) == sq(newtext):
            problems.append(f"{cite}: old == new (no prior version needed?)")
        r_bb = difflib.SequenceMatcher(None, sq(oldtext), sq(bb.get(n, "")), autojunk=False).ratio()
        if r_bb < 0.90:
            problems.append(f"{cite}: 1981-BB witness ratio {r_bb:.2f} < 0.90")
        plan.append((cite, pid, m, oldtext, r_bb))
        print(f"{cite:26} <- 1889 §{m:<3} BB-witness={r_bb:.2f}  old={len(sq(oldtext))}c new={len(sq(newtext))}c")

    if problems:
        print("\nGATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    if not plan:
        print("\nnothing to do"); con.close(); return
    print(f"\nGATES PASS ({len(plan)} sections: earliest==1986-12-01; old!=new; BB witness>=0.90).")
    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    for cite, pid, m, oldtext, r_bb in plan:
        con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, BATCH))
        nvid = con.execute(
            "INSERT INTO provision_versions (provision_id, effective_start, effective_end, "
            "text_content, source_authority, source_path, batch) VALUES (?,?,?,?,?,?,?)",
            (pid, PRIOR_START, PRIOR_END, oldtext,
             f"art IV § (1981 numbering) pre-1986 content; text from validated historical layer "
             f"§ {m} (1889 numbering, in force at 1980); confirmed vs 1981 Blue Book (ratio {r_bb:.2f}); "
             f"recreated/renumbered 1986-12-01",
             f"crosswalk: art IV § -> 1889 § {m}", BATCH)).lastrowid
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                    "VALUES (?,?,?,?,?,?)", (BATCH, pid, nvid, "version_splice_crosswalk_prior",
                    f"[{PRIOR_START} -> {PRIOR_END}] pre-1986 art IV (= 1889 § {m})",
                    "historical layer + 1981 Blue Book; ARTIV-CROSSWALK-PLAN.md"))
    con.commit()

    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions) SELECT count(*) FROM v WHERE nxt IS NOT NULL
      AND effective_end IS NOT NULL AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    print(f"\nSPLICED {len(plan)} sections. integrity gaps={g}")
    for cite, pid, *_ in plan:
        spans = con.execute("SELECT effective_start, COALESCE(effective_end,'open') FROM provision_versions "
                            "WHERE provision_id=? ORDER BY effective_start", (pid,)).fetchall()
        print(f"  {cite.split('art. ')[1]}: " + "  ".join(f"[{s}->{e}]" for s, e in spans))
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
