#!/usr/bin/env python3
"""Reconstruct the pre-repeal text of seven art. XII (Corporations) sections.

ndconst.org gives only the *current* text for art. XII §§ 3, 7, 8, 12, 14, 15, 17 —
a bare "Repealed." stamped (by the ingest default) [1889-10-01, open). That is wrong
across the WHOLE timeline: both the 1981 and the 1989 (Centennial) Blue Books print
full text for all seven. They were repealed only in 2006.

REPEAL FACT (authority: ND Legislative Council, official codifier of the constitution,
codified history note for art. XII): "The repeal of this section, effective July 1,
2006, was approved at the primary election in 2006." The same cleanup measure (S.L.
2005, ch. 623) amended surviving §§ 1, 2, 6 (approved June 13, 2006 primary). We adopt
the codifier's stated effective date, 2006-07-01. (Residual: whether the measure stated
July 1 vs. the 30-day default → a 12-day mid-2006 window, immaterial to point-in-time
correctness; to be confirmed against the measure before live promotion.)

TEXT PROVENANCE (triangulated, three independent witnesses):
  - PRIMARY:  1981 Blue Book (high-res ndbb scan), modern art. XII numbering — clean.
  - WITNESS:  1989 Centennial Blue Book — same words (OCR spacing garble; it dropped
              "be" in §15, corrected here from the 1981 BB + 1925).
  - CROSS:    1925 official constitution, orig. Art. VII (= same content, renumbered by
              the reorg). Confirms verbatim wording and repairs OCR.
  Two modern-era variants where BOTH Blue Books govern over the 1925 reading:
    §12  "franchises" (1925 sing. "franchise"); "...this section, by..." (1925 no comma)
    §14  "...cross any other, and..." (1925 semicolon "other; and")

MODEL (carried→repealed): each section currently has ONE version (the "Repealed." tail).
We (1) move that tail's effective_start 1889-10-01 → 2006-07-01, and (2) insert a prior
full-text version [1981-01-01, 2006-06-30] (the modern-layer head convention, cf. IX §12).
Integrity preserved: 2006-06-30 +1d == 2006-07-01. FTS untouched (current text unchanged).
Idempotent (batch-scoped on the inserted heads). Scratch only.
"""
import difflib
import sqlite3
import sys

DB = "/tmp/const-scratch.db"
BATCH = "modern-xii-corp-repeal-2006-2026-06-15"
REPEAL_START = "2006-07-01"
PRIOR_START = "1981-01-01"
PRIOR_END = "2006-06-30"
REPEAL_AUTH = ("Repealed eff. 2006-07-01 (approved June 13, 2006 primary; S.L. 2005, "
               "ch. 623) — ND Legislative Council codified history note")

# sec: (modern_text [1981 BB, modern-witness governing], orig Art VII §, 1925 cross-check text)
SECTIONS = {
    "3": (
        "All existing charters or grants of special or exclusive privileges, under "
        "which a bona fide organization shall not have taken place and business been "
        "commenced in good faith at the time this constitution takes effect, shall "
        "thereafter have no validity.",
        "132",
        "All existing charters or grants of special or exclusive privileges, under "
        "which a bona fide organization shall not have taken place and business been "
        "commenced in good faith at the time this constitution takes effect, shall "
        "thereafter have no validity.",
    ),
    "7": (
        "No foreign corporation shall do business in this state without having one or "
        "more places of business and an authorized agent or agents in the same, upon "
        "whom process may be served.",
        "136",
        "No foreign corporation shall do business in this state without having one or "
        "more places of business and an authorized agent or agents in the same, upon "
        "whom process may be served.",
    ),
    "8": (
        "No corporation shall engage in any business other than that expressly "
        "authorized in its charter.",
        "137",
        "No corporation shall engage in any business other than that expressly "
        "authorized in its charter.",
    ),
    "12": (
        "No railroad corporation shall consolidate its stock, property or franchises "
        "with any other railroad corporation owning a parallel or competing line; and "
        "in no case shall any consolidation take place except upon public notice given "
        "at least sixty days to all stockholders, in such manner as may be provided by "
        "law. Any attempt to evade the provisions of this section, by any railroad "
        "corporation, by lease or otherwise, shall work a forfeiture of its charter.",
        "141",
        "No railroad corporation shall consolidate its stock, property or franchise "
        "with any other railroad corporation owning a parallel or competing line; and "
        "in no case shall any consolidation take place except upon public notice given "
        "at least sixty days to all stockholders, in such manner as may be provided by "
        "law. Any attempt to evade the provisions of this section by any railroad "
        "corporation, by lease or otherwise, shall work a forfeiture of its charter.",
    ),
    "14": (
        "Any association or corporation organized for the purpose shall have the right "
        "to construct and operate a railroad between any points within this state, and "
        "to connect at the state line with the railroads of other states. Every "
        "railroad company shall have the right with its road to intersect, connect with "
        "or cross any other, and shall receive and transport each other's passengers, "
        "tonnage and cars, loaded or empty, without delay or discrimination.",
        "143",
        "Any association or corporation organized for the purpose shall have the right "
        "to construct and operate a railroad between any points within this state, and "
        "to connect at the state line with the railroads of other states. Every "
        "railroad company shall have the right with its road to intersect, connect with "
        "or cross any other; and shall receive and transport each other's passengers, "
        "tonnage and cars, loaded or empty, without delay or discrimination.",
    ),
    "15": (
        "If a general banking law be enacted, it shall provide for the registry and "
        "countersigning by an officer of the state, of all notes or bills designed for "
        "circulation, and that ample security to the full amount thereof shall be "
        "deposited with the state treasurer for the redemption of such notes or bills.",
        "145",
        "If a general banking law be enacted, it shall provide for the registry and "
        "countersigning by an officer of the state, of all notes or bills designed for "
        "circulation, and that ample security to the full amount thereof shall be "
        "deposited with the state treasurer for the redemption of such notes or bills.",
    ),
    "17": (
        'The exchange of "black lists" between corporations shall be prohibited.',
        "212",
        'The exchange of "black lists" between corporations shall be prohibited.',
    ),
}


def norm(s):
    return " ".join((s or "").split())


def word_ratio(a, b):
    # word-level (char-level SequenceMatcher thrashes on repeated legal phrasing)
    return difflib.SequenceMatcher(None, norm(a).split(), norm(b).split()).ratio()


def main(apply=False):
    con = sqlite3.connect(DB)
    problems, plan = [], []
    for sec, (text, orig, cross) in SECTIONS.items():
        cite = f"N.D. Const. art. XII, § {sec}"
        row = con.execute(
            "SELECT p.id, p.current_version_id, v.text_content, v.effective_start "
            "FROM provisions p JOIN provision_versions v ON v.id=p.current_version_id "
            "WHERE p.citation=?", (cite,)).fetchone()
        if not row:
            problems.append(f"{cite}: not found"); continue
        pid, vid, cur, vstart = row
        ratio = word_ratio(text, cross)
        # gate 1: we must be replacing a bare "Repealed." tail, not real text
        if norm(cur) != "Repealed.":
            problems.append(f"{cite}: current text is not 'Repealed.' ({cur[:40]!r})")
        # gate 2: reconstruction must closely match the 1925 clean cross-check
        if ratio < 0.95:
            problems.append(f"{cite}: 1925 cross-check ratio {ratio:.3f} < 0.95")
        plan.append((cite, pid, vid, vstart, orig, ratio, text))
        print(f"{cite:28s} orig Art VII §{orig:>3s}  1925-ratio={ratio:.3f}  "
              f"cur_start={vstart}  len={len(norm(text))}")

    if problems:
        print("\nGATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    print("\nGATES PASS (all 7: current=='Repealed.'; 1925 cross-check >= 0.95).")
    print("  §12/§14 ratios <1.0 are the documented modern-witness variants "
          "(franchises; comma/semicolon).")

    if not apply:
        print("\n(dry run) re-run with --apply"); con.close(); return

    for cite, pid, vid, vstart, orig, ratio, text in plan:
        # clear any prior run of this batch (idempotent)
        con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, BATCH))
        # (1) move the existing "Repealed." tail to its true effective date
        con.execute("UPDATE provision_versions SET effective_start=?, source_authority=? WHERE id=?",
                    (REPEAL_START, REPEAL_AUTH, vid))
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                    "VALUES (?,?,?,?,?,?)",
                    (BATCH, pid, vid, "repeal_tail_effective_start",
                     f"1889-10-01 -> {REPEAL_START} (repealed, not original)",
                     "ND Legislative Council codified history note (art. XII)"))
        # (2) insert the prior full-text head
        nvid = con.execute(
            "INSERT INTO provision_versions (provision_id, effective_start, effective_end, "
            "text_content, source_authority, source_url, source_path, batch) VALUES (?,?,?,?,?,?,?,?)",
            (pid, PRIOR_START, PRIOR_END, text,
             f"1981 & 1989 Blue Books (dual witness, modern art. XII numbering); "
             f"1925 official Art. VII § {orig} cross-check (ratio {ratio:.3f})",
             "https://www.ndcourts.gov/legal-resources/nd-constitution/"
             "article-xii-corporations-other-than-municipal",
             "~/refs/nd/const/processed/1981_blue-book-ndbb_constitution.md",
             BATCH)).lastrowid
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                    "VALUES (?,?,?,?,?,?)",
                    (BATCH, pid, nvid, "version_splice_prior_head",
                     f"[{PRIOR_START} -> {PRIOR_END}] pre-repeal full text",
                     "1981 & 1989 Blue Books; 1925 official Art. VII cross-check"))
    con.commit()

    # integrity: no gaps between consecutive versions
    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions)
      SELECT count(*) FROM v WHERE nxt IS NOT NULL AND effective_end IS NOT NULL
      AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    print(f"\nSPLICED 7 sections. integrity gaps={g}")
    for sec in SECTIONS:
        pid = con.execute("SELECT id FROM provisions WHERE citation=?",
                          (f"N.D. Const. art. XII, § {sec}",)).fetchone()[0]
        spans = con.execute("SELECT effective_start, COALESCE(effective_end,'open') "
                            "FROM provision_versions WHERE provision_id=? ORDER BY effective_start",
                            (pid,)).fetchall()
        print(f"  §{sec:>2s}: " + "  ".join(f"[{s}->{e}]" for s, e in spans))
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
