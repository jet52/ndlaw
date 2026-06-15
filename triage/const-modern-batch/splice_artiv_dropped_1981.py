#!/usr/bin/env python3
"""art IV dropped-section orphans — old §§17-46 with no modern citation.

Article IV (Legislative Branch) was repealed-and-recreated 1986-12-01 with a SHORTER article
(§§1-16). The old §§17-46 were repealed and NOT recreated, so no modern provision resolves to
"art IV § N" for N in 17..46. This creates each as a repealed provision whose only content version
covers the [1981-01-01, 1986-11-30] window it actually denoted (BB-witness = the 1981 Blue Book),
mirroring the existing repealed-provision convention (heading 'Repealed', status 'repealed', a
final "Repealed." sentinel version as current_version_id — cf. art X §6, art XII §§3-9).

Included (29 sections minus the two defers = 27 created): old §§17,19-25,27-46 (NOT §26 — it did
not exist at 1981; the 1981 art IV jumps 25->27). §19 IS included: although its CONTENT survived
by renumbering to new §11 (so the writs text reappears at §11 from 1986-12-01), the CITATION
"art IV §19" held that text only during [1981,1986) and resolves to nothing today — exactly
parallel to §17/§18/§20+. (§14/§15 citations are already covered: new §14/§15 provisions exist
and got [1981,1986) crosswalk prepends.)

Text source: the validated historical layer (1889 numbering) via the derived crosswalk
(ARTIV-CROSSWALK-PLAN.md), confirmed per section against the 1981 BB. Each mapped 1889 §M's
version in force at the 1980 layer boundary == the [1981,1986) text (no art IV amendments
1981-86 except the §46 repeal).

Special cases:
  - §45 (legislative proposal of amendments): the 1981 renumbering SPLIT 1889 §202 — only its
    first (legislative-proposal) paragraph became art IV §45; the initiative-petition paragraph
    went elsewhere. Source = §202 ¶1 ONLY (ratio 0.985 vs BB §45; full §202 was 0.49).
  - §46 (member compensation): repealed earlier — 1982 (S.L. 1981 ch. 668), its content moving to
    art XI §26 (eff 1982-07-08). So §46's content window is [1981-01-01, 1982-07-07], Repealed
    from 1982-07-08.

DEFERRED (no clean source — documented, NOT created):
  - §18 (governor/officer/manager interest in contracts): no clean 1889 §M carryover (the matcher's
    §75 is the Governor's commander-in-chief powers — wrong); likely a post-1889 addition whose
    [1981,1986) text would have to come from the heavily space-garbled 1981 BB OCR. Defer rather
    than risk fabricated text in an authoritative DB.
  - §43 (enumerated special-legislation prohibition): its apparent 1889 source §69 was REPEALED
    effective 1980-10-02 (SCR 4006, 1979 SL), so it has no clean in-force 1980 carryover; the BB
    list ("granting divorces...") is long and OCR-garbled. Defer pending a clean witness.

Idempotent (batch-scoped). Scratch only.
"""
import re
import sqlite3
import sys
import difflib
from pathlib import Path

from ndcourts_mcp.corpus import cite_key

DB = "/tmp/const-scratch.db"
BATCH = "modern-artiv-dropped-1981-2026-06-15"
DEFAULT_END, RECREATE = "1986-11-30", "1986-12-01"

# new art IV §N (1981 numbering) -> 1889 §M (full-text source), verified vs 1981 BB.
MAP = {17: 39, 19: 44, 20: 42, 21: 43, 22: 53, 23: 56, 24: 51, 25: 46, 27: 48, 28: 50,
       29: 49, 30: 54, 31: 57, 32: 58, 33: 61, 34: 59, 35: 60, 36: 62, 37: 63, 38: 64,
       39: 65, 40: 66, 41: 67, 42: 68, 44: 70, 45: 202, 46: 45}
PARA1_ONLY = {45}                 # source = 1889 §M first paragraph only
END_OVERRIDE = {46: ("1982-07-07", "1982-07-08")}  # §N: (content_end, repealed_start)
MIN_RATIO = 0.80                  # OCR-depressed; §25/§46 verified clean at 0.80/0.94


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
    for n in sorted(MAP):
        m = MAP[n]
        cite = f"N.D. Const. art. IV, § {n}"
        existing = con.execute("SELECT id, status FROM provisions WHERE citation=?", (cite,)).fetchone()
        if existing and existing[1] != "repealed":
            problems.append(f"{cite}: a non-repealed provision already exists (id {existing[0]}) — abort")
            continue
        hist = con.execute("SELECT pv.text_content FROM provisions p JOIN provision_versions pv "
                           "ON pv.provision_id=p.id WHERE p.citation=? ORDER BY pv.effective_start DESC "
                           "LIMIT 1", (f"N.D. Const. § {m}",)).fetchone()
        if not hist:
            problems.append(f"{cite}: historical § {m} not found"); continue
        oldtext = strip_prefix(hist[0])
        if oldtext.strip().startswith("[Repealed"):
            problems.append(f"{cite}: source § {m} is itself repealed at the boundary"); continue
        if n in PARA1_ONLY:
            oldtext = oldtext.split("\n\n")[0].strip()
        r_bb = difflib.SequenceMatcher(None, sq(oldtext), sq(bb.get(n, "")), autojunk=False).ratio()
        if r_bb < MIN_RATIO:
            problems.append(f"{cite}: 1981-BB witness ratio {r_bb:.2f} < {MIN_RATIO} (verify source)")
        c_end, r_start = END_OVERRIDE.get(n, (DEFAULT_END, RECREATE))
        plan.append((cite, n, m, oldtext, r_bb, c_end, r_start))
        print(f"{cite:26} <- 1889 §{m:<3} BB={r_bb:.2f}  content[1981->{c_end}] repealed[{r_start}->]  {len(sq(oldtext))}c")

    print(f"\nSEPARATE (created by splice_artiv_dropped_special.py): art IV §18 (= amend. art. LI, 1938) "
          f"and §43 (= 1889 §69 minus subsection 6 — SCR 4006 repealed only sub 6, not the whole list).")
    if problems:
        print("\nGATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    print(f"\nGATES PASS ({len(plan)} dropped sections to create).")
    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    # idempotency: drop our prior batch rows + any provisions we created that are now empty
    con.execute("DELETE FROM changelog WHERE batch=?", (BATCH,))
    con.execute("DELETE FROM provision_versions WHERE batch=?", (BATCH,))
    con.execute("DELETE FROM provisions WHERE corpus='const' AND citation LIKE 'N.D. Const. art. IV, %' "
                "AND id NOT IN (SELECT DISTINCT provision_id FROM provision_versions)")

    created = 0
    for cite, n, m, oldtext, r_bb, c_end, r_start in plan:
        prov = con.execute("SELECT id FROM provisions WHERE citation=?", (cite,)).fetchone()
        if prov:
            pid = prov[0]
            con.execute("UPDATE provisions SET status='repealed', heading='Repealed', hierarchy=NULL WHERE id=?", (pid,))
        else:
            pid = con.execute(
                "INSERT INTO provisions (corpus, citation, cite_key, hierarchy, heading, status, current_version_id) "
                "VALUES ('const', ?, ?, NULL, 'Repealed', 'repealed', NULL)",
                (cite, cite_key(cite))).lastrowid
        auth = (f"art IV § {n} (1981 numbering), pre-1986 content = 1889 § {m}"
                f"{' ¶1 (legislative-proposal clause only; §202 was split in the 1981 renumbering)' if n in PARA1_ONLY else ''}, "
                f"in force at 1980; text from the validated historical layer; confirmed vs 1981 Blue Book "
                f"(ratio {r_bb:.2f}). Old § {n} was repealed "
                f"{'1982 (S.L. 1981 ch. 668; content moved to art XI § 26)' if n in END_OVERRIDE else 'by the art IV recreation effective 1986-12-01'}; "
                f"the citation has no counterpart in the recreated (shorter) article IV.")
        cvid = con.execute(
            "INSERT INTO provision_versions (provision_id, effective_start, effective_end, text_content, "
            "source_authority, source_path, batch) VALUES (?,?,?,?,?,?,?)",
            (pid, "1981-01-01", c_end, oldtext, auth, f"crosswalk: art IV § {n} (dropped) -> 1889 § {m}", BATCH)).lastrowid
        rvid = con.execute(
            "INSERT INTO provision_versions (provision_id, effective_start, effective_end, text_content, "
            "source_authority, source_path, batch) VALUES (?,?,?,?,?,?,?)",
            (pid, r_start, None, "Repealed.",
             f"art IV § {n} repealed {'1982 (S.L. 1981 ch. 668)' if n in END_OVERRIDE else 'by the recreation of article IV effective 1986-12-01'}",
             f"crosswalk: art IV § {n} (dropped)", BATCH)).lastrowid
        con.execute("UPDATE provisions SET current_version_id=? WHERE id=?", (rvid, pid))
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                    "VALUES (?,?,?,?,?,?)", (BATCH, pid, cvid, "dropped_section_orphan_created",
                    f"art IV § {n} [1981-01-01 -> {c_end}] (= 1889 § {m}); repealed [{r_start} -> open]",
                    "historical layer + 1981 Blue Book; ARTIV-CROSSWALK-PLAN.md"))
        created += 1
    con.commit()

    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions) SELECT count(*) FROM v WHERE nxt IS NOT NULL
      AND effective_end IS NOT NULL AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    qc = con.execute("PRAGMA quick_check").fetchone()[0]
    print(f"\nCREATED {created} dropped-section orphans. integrity gaps={g}  quick_check={qc}")
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
