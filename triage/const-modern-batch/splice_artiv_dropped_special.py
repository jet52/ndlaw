#!/usr/bin/env python3
"""art IV dropped-section orphans — the two special-sourced sections §18 and §43.

Companion to splice_artiv_dropped_1981.py, which created the 27 dropped sections whose text
carries cleanly from a single 1889 §M in force at the 1980 boundary. §18 and §43 were initially
DEFERRED there because the simple crosswalk failed; both are now resolved with authoritative
sources (2026-06-15):

§18 — anti-patronage (officer side): "The governor or any officer of this state … shall not
  appoint a member of the legislative assembly to any civil office … during the term …". This is
  NOT in the 1889-numbered historical layer (it was added by amendment in 1938). It IS stored as
  **N.D. Const. amend. art. LI** (1938-07-28 → 1980-12-31) — clean, verbatim, ratio 0.991 vs the
  (space-garbled) 1981 BB §18. Source = amend. art. LI. (Companion to §17 = 1889 §39, the
  legislator-side bar already created in the main dropped batch.)

§43 — enumerated special-legislation prohibition. My main-batch deferral assumed 1889 §69 was
  fully repealed in 1980; the session law proves otherwise. S.L. 1981 ch. 655 (SCR 4006, eff
  1980-10-02) "SECTION 2. REPEAL. Subsection 6 of section 69 … is hereby repealed." — ONLY
  subsection 6 (justices-of-the-peace/police-magistrate jurisdiction), collateral to abolishing
  county judges (§173). The rest of the 35-item list SURVIVED into [1981,1986) and was repealed
  only by the 1986 art IV recreation. Source = the validated historical layer 1889 §69 pre-repeal
  text MINUS subsection 6 (DokuWiki <WRAP> markers stripped; remaining subsections keep their
  original numbers — the session law renumbered nothing, so a gap at 6 is the faithful state).
  Gate: full §69 (with sub 6) vs 1981 BB §43 ≥ 0.90 (crosswalk confirmation; the BB is a
  pre-repeal snapshot that still prints sub 6).

  NOTE — pre-existing historical-layer error (flagged, NOT fixed here): 1889 § 69's version
  [1980-10-02, 1980-12-31] is stored as "[Repealed effective 1980-10-02 …]" (FULL repeal), which
  overstates SCR 4006. The correct post-1980 § 69 is the list minus subsection 6. That belongs in
  the history pipeline (ingest_constitution_history / a const_history correction), separate from
  this scratch modern-orphan work.

Both created as repealed provisions [1981-01-01, 1986-11-30] + "Repealed." [1986-12-01, open),
matching the main dropped batch. Idempotent (batch-scoped). Scratch only.
"""
import re
import sqlite3
import sys
import difflib
from pathlib import Path

from ndcourts_mcp.corpus import cite_key

DB = "/tmp/const-scratch.db"
BATCH = "modern-artiv-dropped-special-2026-06-15"
CONTENT_END, REPEALED_START = "1986-11-30", "1986-12-01"


def sq(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def bb_artiv_section(n):
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
    return re.sub(r"^\s*Section\s+\d+\.\s*", "", out.get(n, ""))


def s69_minus_sub6(con):
    t = con.execute("SELECT pv.text_content FROM provisions p JOIN provision_versions pv "
                    "ON pv.provision_id=p.id WHERE p.citation='N.D. Const. § 69' "
                    "ORDER BY pv.effective_start LIMIT 1").fetchone()[0]
    lines = [l for l in t.splitlines() if l.strip() not in ("<WRAP indent>", "</WRAP>")]
    joined = "\n".join(lines)
    parts = re.split(r"(?m)^(?=\d+\.\s)", joined)
    intro = parts[0].strip()
    subs = {}
    for p in parts[1:]:
        m = re.match(r"(\d+)\.\s", p)
        if m:
            subs[int(m.group(1))] = p.strip()
    assert 6 in subs and "justices of the peace" in subs[6], "sub 6 not located"
    kept = [intro] + [subs[n] for n in sorted(subs) if n != 6]
    return "\n\n".join(kept), t  # (minus-6 text, full pre-repeal text for gating)


def build_plan(con):
    plan, problems = [], []
    # §18 <- amend. art. LI
    li = con.execute("SELECT pv.text_content FROM provisions p JOIN provision_versions pv "
                     "ON pv.provision_id=p.id WHERE p.citation='N.D. Const. amend. art. LI' "
                     "ORDER BY pv.effective_start DESC LIMIT 1").fetchone()
    if not li:
        problems.append("§18: amend. art. LI not found")
    else:
        r = difflib.SequenceMatcher(None, sq(li[0]), sq(bb_artiv_section(18)), autojunk=False).ratio()
        if r < 0.95:
            problems.append(f"§18: amend.LI vs BB ratio {r:.2f} < 0.95")
        plan.append(("N.D. Const. art. IV, § 18", li[0], r,
                     "art IV § 18 (1981 numbering), anti-patronage (officer side); pre-1986 content = "
                     "N.D. Const. amend. art. LI (1938), in force at 1980; confirmed vs 1981 Blue Book "
                     f"(ratio {r:.2f}); repealed by the art IV recreation effective 1986-12-01",
                     "source: N.D. Const. amend. art. LI (1938)"))
    # §43 <- 1889 §69 minus subsection 6
    minus6, full = s69_minus_sub6(con)
    r = difflib.SequenceMatcher(None, sq(full), sq(bb_artiv_section(43)), autojunk=False).ratio()
    if r < 0.90:
        problems.append(f"§43: full §69 vs BB ratio {r:.2f} < 0.90")
    plan.append(("N.D. Const. art. IV, § 43", minus6, r,
                 "art IV § 43 (1981 numbering), enumerated special-legislation prohibition; pre-1986 "
                 "content = 1889 § 69 MINUS subsection 6 (S.L. 1981 ch. 655 / SCR 4006 repealed only "
                 "subsection 6, eff 1980-10-02; the rest of the list survived until the 1986 art IV "
                 f"recreation); clean text from the validated historical layer; full §69 vs 1981 Blue "
                 f"Book ratio {r:.2f} (BB is a pre-repeal snapshot still printing sub 6)",
                 "source: 1889 § 69 minus subsection 6 (SCR 4006, eff 1980-10-02)"))
    return plan, problems


def main(apply=False):
    con = sqlite3.connect(DB)
    plan, problems = build_plan(con)
    for cite, text, r, *_ in plan:
        exist = con.execute("SELECT status FROM provisions WHERE citation=?", (cite,)).fetchone()
        if exist and exist[0] != "repealed":
            problems.append(f"{cite}: non-repealed provision already exists")
        print(f"{cite:26} BB-witness={r:.2f}  text={len(sq(text))}c")
    if problems:
        print("\nGATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    print(f"\nGATES PASS ({len(plan)} sections).")
    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    con.execute("DELETE FROM changelog WHERE batch=?", (BATCH,))
    con.execute("DELETE FROM provision_versions WHERE batch=?", (BATCH,))
    con.execute("DELETE FROM provisions WHERE corpus='const' AND citation IN ('N.D. Const. art. IV, § 18',"
                "'N.D. Const. art. IV, § 43') AND id NOT IN (SELECT DISTINCT provision_id FROM provision_versions)")
    for cite, text, r, auth, src in plan:
        prov = con.execute("SELECT id FROM provisions WHERE citation=?", (cite,)).fetchone()
        if prov:
            pid = prov[0]
            con.execute("UPDATE provisions SET status='repealed', heading='Repealed', hierarchy=NULL WHERE id=?", (pid,))
        else:
            pid = con.execute(
                "INSERT INTO provisions (corpus, citation, cite_key, hierarchy, heading, status, current_version_id) "
                "VALUES ('const', ?, ?, NULL, 'Repealed', 'repealed', NULL)", (cite, cite_key(cite))).lastrowid
        cvid = con.execute(
            "INSERT INTO provision_versions (provision_id, effective_start, effective_end, text_content, "
            "source_authority, source_path, batch) VALUES (?,?,?,?,?,?,?)",
            (pid, "1981-01-01", CONTENT_END, text, auth, src, BATCH)).lastrowid
        rvid = con.execute(
            "INSERT INTO provision_versions (provision_id, effective_start, effective_end, text_content, "
            "source_authority, source_path, batch) VALUES (?,?,?,?,?,?,?)",
            (pid, REPEALED_START, None, "Repealed.",
             "repealed by the recreation of article IV effective 1986-12-01", src, BATCH)).lastrowid
        con.execute("UPDATE provisions SET current_version_id=? WHERE id=?", (rvid, pid))
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                    "VALUES (?,?,?,?,?,?)", (BATCH, pid, cvid, "dropped_section_orphan_created",
                    f"{cite} [1981-01-01 -> {CONTENT_END}]; repealed [{REPEALED_START} -> open]", src))
    con.commit()

    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions) SELECT count(*) FROM v WHERE nxt IS NOT NULL
      AND effective_end IS NOT NULL AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    print(f"\nCREATED {len(plan)} special dropped orphans (§18, §43). integrity gaps={g}  "
          f"quick_check={con.execute('PRAGMA quick_check').fetchone()[0]}")
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
