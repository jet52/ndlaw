#!/usr/bin/env python3
"""art V §1 and §12 — the 3-version chains (Group B).

These two executive-article sections changed TWICE in the modern era: a 1986 amendment
(#121 §1 / #122 §12, eff 1986-12-04) then the 1997 replacement (#135). So each needs:
  [1981-01-01, 1986-12-03]  pre-1986  (from the validated historical layer: §1<-§71, §12<-§82)
  [1986-12-04, 1997-06-30]  post-1986 (the 1989 Blue Book text — the [1986,1997) witness)
  [1997-07-01, open)        current   (already in the DB)

1986 transitions (confirmed): §1 "year 1965"->"year 1988", "his office"->"office", + the
"term begins on December fifteenth" sentence; §12 drops "The tax commissioner shall be
elected on a no party ballot…" (1986 #122 put the tax commissioner on the party ballot).

Gates: pre-1986 (historical) != post-1986 (the 1986 change is present); post-1986 matches the
1989 BB §1/§12 at overlap >=0.97; current starts 1997-07-01. Idempotent. Scratch only.
"""
import re
import sqlite3
import sys
import difflib
from pathlib import Path

DB = "/tmp/const-scratch.db"
BATCH = "modern-artv-chains-1986-2026-06-15"
HIST = {"1": 71, "12": 82}
PRE_END, POST_START, POST_END, CUR_START = "1986-12-03", "1986-12-04", "1997-06-30", "1997-07-01"

POST1986 = {
    "1": ("The executive power shall be vested in a governor, who shall reside at the seat of "
          "government and shall hold office for the term of four years beginning in the year 1988, "
          "and until a successor is elected and duly qualified. The term begins on December "
          "fifteenth following the governor's election."),
    "12": ("There shall be chosen by the qualified electors of the state at the times and places of "
           "choosing members of the legislative assembly, a secretary of state, auditor, treasurer, "
           "superintendent of public instruction, commissioner of insurance, an attorney general, a "
           "commissioner of agriculture and labor, and a tax commissioner, who shall have attained "
           "the age of twenty-five years and shall have the qualifications of state electors. They "
           "shall severally hold their offices at the seat of government for the term of four years "
           "beginning with the year 1965, and until their successors are elected and duly qualified; "
           "but no person shall be eligible for the office of treasurer for more than two consecutive "
           "terms.\n\nThe board of railroad commissioners shall hereafter be known as the public "
           "service commission and the members of the board of railroad commissioners as public "
           "service commissioners and the powers and duties now or hereafter granted to and conferred "
           "upon the board of railroad commissioners are hereby transferred to the public service "
           "commission.\n\nThe public service commissioners shall have the qualifications of state "
           "electors, have attained the age of twenty-five years, be chosen by the qualified electors "
           "of the state at the times and places of choosing members of the legislative assembly, "
           "hold office at the seat of government and until their successors are elected and duly "
           "qualified. As each of the three public service commissioners now holding office completes "
           "his term, his successor shall be elected for a term of six years.\n\nThe legislative "
           "assembly may by law provide for a department of labor, which, if provided for, shall be "
           "separate and distinct from the department of agriculture, and shall be administered by a "
           "public official who may be either elected or appointed, whichever the legislative "
           "assembly shall declare; and if such a department is established the commissioner of "
           "agriculture and labor provided for above shall become the commissioner of agriculture."),
}


def dn(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def bb_exec_sections():
    lines = Path.home().joinpath("refs/nd/const/processed/1989_blue-book_constitution.md").read_text().splitlines()
    st = next(i for i, l in enumerate(lines) if "executive power shall be vested" in l.lower())
    out, cur, buf = {}, None, []
    for j in range(st, st + 160):
        if re.search(r"the judicial power of the state", lines[j], re.I):
            break
        m = re.match(r"\*{0,2}Section\s*(\d+)\s*\.", lines[j].strip())
        if m:
            if cur is not None:
                out[cur] = " ".join(buf)
            cur = m.group(1); buf = [lines[j]]
        elif cur is not None:
            buf.append(lines[j])
    if cur is not None:
        out[cur] = " ".join(buf)
    return out


def overlap(a, b):
    sm = difflib.SequenceMatcher(None, dn(a), dn(b), autojunk=False)
    return sum(x.size for x in sm.get_matching_blocks()) / max(1, len(dn(a)))


def main(apply=False):
    con = sqlite3.connect(DB)
    bb = bb_exec_sections()
    plan, problems = [], []
    for s, m in HIST.items():
        cite = f"N.D. Const. art. V, § {s}"
        pid = con.execute("SELECT id FROM provisions WHERE citation=?", (cite,)).fetchone()[0]
        rows = con.execute("SELECT effective_start, text_content FROM provision_versions "
                           "WHERE provision_id=? ORDER BY effective_start", (pid,)).fetchall()
        earliest, curtext = rows[0]
        pre = con.execute("SELECT pv.text_content FROM provisions p JOIN provision_versions pv "
                          "ON pv.provision_id=p.id WHERE p.citation=? ORDER BY pv.effective_start DESC "
                          "LIMIT 1", (f"N.D. Const. § {m}",)).fetchone()[0]
        pre = re.sub(r"^\s*Section\s+\d+\.\s*", "", pre)
        post = POST1986[s]
        ov_bb = overlap(post, bb.get(s, ""))
        if earliest == "1981-01-01":
            print(f"{cite}: already chained (skip)"); continue
        if earliest != CUR_START:
            problems.append(f"{cite}: earliest {earliest} != {CUR_START}")
        if dn(pre) == dn(post):
            problems.append(f"{cite}: pre-1986 == post-1986 (1986 change missing)")
        if dn(post) == dn(curtext):
            problems.append(f"{cite}: post-1986 == current (1997 change missing)")
        if ov_bb < 0.97:
            problems.append(f"{cite}: post-1986 vs 1989 BB overlap {ov_bb:.3f} < 0.97")
        plan.append((cite, pid, m, pre, post, ov_bb))
        print(f"{cite}: pre-1986(hist §{m})={len(dn(pre))}c  post-1986={len(dn(post))}c  "
              f"1989BB-overlap={ov_bb:.3f}  pre!=post={dn(pre)!=dn(post)}")

    if problems:
        print("\nGATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    print(f"\nGATES PASS ({len(plan)}).")
    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    for cite, pid, m, pre, post, ov_bb in plan:
        con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, BATCH))
        for (s0, e0, txt, auth) in [
            ("1981-01-01", PRE_END, pre,
             f"pre-1986 ([1981,1986)); validated historical layer § {m}; amended 1986-12-04 (#12{'1' if m==71 else '2'})"),
            (POST_START, POST_END, post,
             f"post-1986 ([1986,1997)); 1989 Blue Book (overlap {ov_bb:.3f}); replaced 1997-07-01 (#135)"),
        ]:
            nvid = con.execute(
                "INSERT INTO provision_versions (provision_id, effective_start, effective_end, "
                "text_content, source_authority, batch) VALUES (?,?,?,?,?,?)",
                (pid, s0, e0, txt, auth, BATCH)).lastrowid
            con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                        "VALUES (?,?,?,?,?,?)", (BATCH, pid, nvid, "version_splice_artv_chain",
                        f"[{s0} -> {e0}]", "historical layer + 1989 BB"))
    con.commit()
    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions) SELECT count(*) FROM v WHERE nxt IS NOT NULL
      AND effective_end IS NOT NULL AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    print(f"\nSPLICED {len(plan)} chains. integrity gaps={g}")
    for cite, pid, *_ in plan:
        spans = con.execute("SELECT effective_start, COALESCE(effective_end,'open') FROM provision_versions "
                            "WHERE provision_id=? ORDER BY effective_start", (pid,)).fetchall()
        print(f"  {cite}: " + "  ".join(f"[{s}->{e}]" for s, e in spans))
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
