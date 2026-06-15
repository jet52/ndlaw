#!/usr/bin/env python3
"""art VIII § 6 (State Board of Higher Education) — 4-version chain (Group B, final item).

The DB has only [2000-07-13, open); all of [1981,2000) was uncovered. Three modern amendments:
  #130 (eff 1994-12-08)  added the student member (7->8 board), rewrote subsec 2 + 4
  #133 (eff 1996-12-05)  one-graduate -> one bachelor's; 3->5 nominating committee; 7yr->4yr
                         terms + two-term limit; "balanced and representative" sentence
  #139 (eff 2000-07-13)  bachelor's-degree cap one person -> two persons

Anchors are INDEPENDENT: BASE = the marker 1989 BB ([1981,1994)); CURRENT = the DB text
([2000,)). The two intermediates are built by REVERSE-applying the localized #139 then #133
edits to the (whitespace-normalized) clean current text — so the unchanged ~90% stays
byte-identical to current and only the amended clauses differ.

Redline reading by subagent (1995 CAA p5 / 1997 SL7CNSTM p10 / 2001 CAA p1, rendered 450dpi);
the subagent verified base+#130+#133+#139==current forward (ratio 1.0). Gates HERE (independent):
  (a) v1996 differs from current by ONLY the #139 cap change
  (b) v1994 differs from v1996 by ONLY the #133 changes
  (c) v1994's #130-untouched subsections (1,3,5,6,7,8) match the BASE (1989 BB) despaced
Idempotent. Scratch only.
"""
import re
import sqlite3
import sys
import difflib
from pathlib import Path

DB = "/tmp/const-scratch.db"
BATCH = "modern-artviii6-chain-2026-06-15"
CITE = "N.D. Const. art. VIII, § 6"


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def dn(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def sub1(text, old, new, label):
    """Replace exactly one occurrence of `old` in `text`; raise if count != 1."""
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"GATE FAIL [{label}]: anchor occurs {n}x (need 1): {old[:60]!r}")
    return text.replace(old, new)


def main(apply=False):
    con = sqlite3.connect(DB)
    cur_raw = con.execute("SELECT text_content FROM provisions p JOIN provision_versions pv "
                          "ON pv.provision_id=p.id WHERE p.citation=? ORDER BY pv.effective_start "
                          "LIMIT 1", (CITE,)).fetchone()[0]
    cur = norm(cur_raw)

    # ---- reverse #139 (2000): two persons -> one person (bachelor's-degree cap) ----
    v1996 = sub1(cur,
                 "no more than two persons holding a bachelor's degree from a particular institution",
                 "no more than one person holding a bachelor's degree from a particular institution",
                 "#139 cap")

    # ---- reverse #133 (1996): five edits, all in subsec 2.a ----
    v1994 = v1996
    # (1) one bachelor's -> one graduate of any one institution
    v1994 = sub1(v1994,
                 "no more than one person holding a bachelor's degree from a particular institution",
                 "no more than one graduate of any one institution",
                 "#133 cap")
    # (2) nominating committee: 5-member (4-of-5) -> original 3-member unanimous
    v1994 = sub1(v1994,
                 "selected by action of four of the following five persons: the president of the North "
                 "Dakota education association, the chief justice of the supreme court, the "
                 "superintendent of public instruction, the president pro tempore of the senate, and "
                 "the speaker of the house of representatives and, with the consent of a",
                 "selected by the unanimous action of the president of the North Dakota educational "
                 "association, the chief justice of the supreme court, and the superintendent of "
                 "public instruction, and, with the consent of a",
                 "#133 committee")
    # (3) remove the "balanced and representative" sentence (added 1996)
    v1994 = sub1(v1994,
                 " The governor shall ensure that the board membership is maintained in a balanced "
                 "and representative manner.",
                 "",
                 "#133 balanced")
    # (4) term length four -> seven years
    v1994 = sub1(v1994, "said terms shall be for four years", "said terms shall be for seven years",
                 "#133 term")
    # (5) remove the two-term-limit sentences (added 1996)
    v1994 = sub1(v1994,
                 " A member may not be appointed to serve for more than two terms. If a member is "
                 "appointed to fill a vacancy and serves two or more years of that term, the member "
                 "is deemed to have served one full term.",
                 "",
                 "#133 twoterm")

    # ---- gates ----
    # (a) v1996 vs current: only the #139 change
    da, db_ = dn(cur), dn(v1996)
    diff_139 = [(o, n) for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, db_, da).get_opcodes()
                if t != "equal" for o, n in [(db_[i1:i2], da[j1:j2])]]
    # (b) v1994 vs v1996: the #133 changes
    ov_133 = sum(b.size for b in difflib.SequenceMatcher(None, dn(v1994), dn(v1996),
                 autojunk=False).get_matching_blocks()) / len(dn(v1994))
    # (c) cross-check v1994 #130-untouched subsections vs BASE (1989 BB)
    M = Path.home().joinpath("refs/nd/const/processed/1989_blue-book-marker_constitution.md").read_text().splitlines()
    bstart = next(i for i, l in enumerate(M) if "board of higher education, to be officially known" in l.lower())
    bend = len(M)
    for j in range(bstart + 1, len(M)):
        if re.search(r"ARTICLE IX|Section 7\.|Section 8\.", M[j]):
            bend = j; break
    base = norm(" ".join(x.strip().lstrip("-* ").strip() for x in M[bstart:bend] if x.strip()))
    # subsections 3 & 5 (single-para, #130-untouched) make a clean cross-check anchor
    def subsec(text, n):
        m = re.search(rf"(?:^|\s){n}\.\s+(.*?)(?=\s+{n+1}\.\s)", text, re.S)
        return dn(m.group(1)) if m else ""
    s3_match = subsec(v1994, 3) and subsec(v1994, 3) == subsec(base, 3)
    s5_match = subsec(v1994, 5) and subsec(v1994, 5) == subsec(base, 5)

    print(f"{CITE}")
    print(f"  base(1989BB)={len(dn(base))}c  v1994={len(dn(v1994))}c  v1996={len(dn(v1996))}c  current={len(dn(cur))}c")
    print(f"  (a) v1996 vs current diffs (should be 1, the cap): {diff_139}")
    print(f"  (b) v1994 vs v1996 overlap (133 changed): {ov_133:.3f}")
    print(f"  (c) subsec 3 matches base: {bool(s3_match)};  subsec 5 matches base: {bool(s5_match)}")

    problems = []
    if not (len(diff_139) == 1 and "one" in diff_139[0][0] and "two" in diff_139[0][1]):
        problems.append("v1996 vs current is not exactly the #139 one<->two cap change")
    if not (0.90 < ov_133 < 0.999):
        problems.append(f"v1994 vs v1996 overlap {ov_133:.3f} outside expected band (133 should be a moderate change)")
    if not (s3_match and s5_match):
        problems.append("v1994 #130-untouched subsections (3,5) do NOT match the 1989 BB base")
    if problems:
        print("GATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    print("GATES PASS.")
    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    pid = con.execute("SELECT id FROM provisions WHERE citation=?", (CITE,)).fetchone()[0]
    con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, BATCH))
    for s0, e0, txt, auth in [
        ("1981-01-01", "1994-12-07", base,
         "pre-1994 base; marker-OCR 1989 Blue Book (complete re-extraction)"),
        ("1994-12-08", "1996-12-04", v1994,
         "after amend #130 (1994 student member); current text reverse-applied (#139,#133); "
         "redlines 1995 CAA p5 etc.; #130-untouched subsections match 1989 BB"),
        ("1996-12-05", "2000-07-12", v1996,
         "after amend #133 (1996 terms 7->4yr, bachelor's cap, 5-member committee); "
         "current text reverse-applied (#139); redline 1997 SL7CNSTM p10"),
    ]:
        nvid = con.execute(
            "INSERT INTO provision_versions (provision_id, effective_start, effective_end, "
            "text_content, source_authority, batch) VALUES (?,?,?,?,?,?)",
            (pid, s0, e0, txt, auth, BATCH)).lastrowid
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                    "VALUES (?,?,?,?,?,?)", (BATCH, pid, nvid, "version_splice_artviii6_chain",
                    f"[{s0} -> {e0}]", "1989 BB base + redline reverse-walk (#130/#133/#139)"))
    con.commit()
    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions) SELECT count(*) FROM v WHERE nxt IS NOT NULL
      AND effective_end IS NOT NULL AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    spans = con.execute("SELECT effective_start, COALESCE(effective_end,'open') FROM provision_versions "
                        "WHERE provision_id=? ORDER BY effective_start", (pid,)).fetchall()
    print(f"\nSPLICED 4-version chain. integrity gaps={g}")
    print("  " + "  ".join(f"[{s}->{e}]" for s, e in spans))
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
