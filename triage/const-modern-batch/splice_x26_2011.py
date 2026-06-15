#!/usr/bin/env python3
"""Reconstruct art. X § 26 (Legacy Fund) point-in-time chain into scratch.

§26 was CREATED in 2011 (amend 152, HCR 3054 / S.L. 2011 ch. 518) and AMENDED in
2024 (amend 167, HCR 3033 / bill 23-3092). Because it is a created provision, the
[2011, 2024) head version IS the text the 2011 measure enacted (a clean CREATE
reprint — no redline reversal needed). Transcribed verbatim from the on-disk 2011
CAA.PDF (chapter 518), and every 2024 change was cross-validated against the 2024
redline (bill 23-3092):
  fifteen->five percent · "may not be expended until after June 30, 2017"->
  "may be expended, but" · "principal of the North Dakota legacy fund"->"moneys in
  the legacy fund" · subsec 4./5. numbers added 2024 · subsec 3 unchanged.

Gate (this script): subsection 3 (the unchanged "Statutory programs" paragraph)
must be byte-identical between the 2011 text and current DB text; the 2011 text
must carry the pre-2024 diagnostics and current must carry the post-2024 ones.
Idempotent (batch-scoped). Scratch only.
"""
import re, sqlite3, sys
from pathlib import Path

DB = "/tmp/const-scratch.db"
BATCH = "modern-x26-legacyfund-2026-06-14"
CITE = "N.D. Const. art. X, § 26"

TEXT_2011 = (
    "1. Thirty percent of total revenue derived from taxes on oil and gas production "
    "or extraction must be transferred by the state treasurer to a special fund in the "
    "state treasury known as the legacy fund. The legislative assembly may transfer "
    "funds from any source into the legacy fund and such transfers become part of the "
    "principal of the legacy fund. "
    "2. The principal and earnings of the legacy fund may not be expended until after "
    "June 30, 2017, and an expenditure of principal after that date requires a vote of "
    "at least two-thirds of the members elected to each house of the legislative "
    "assembly. Not more than fifteen percent of the principal of the legacy fund may "
    "be expended during a biennium. "
    "3. Statutory programs, in existence as a result of legislation enacted through "
    "2009, providing for impact grants, direct revenue allocations to political "
    "subdivisions, and deposits in the oil and gas research fund must remain in effect "
    "but the legislative assembly may adjust statutory allocations for those purposes. "
    "The state investment board shall invest the principal of the North Dakota legacy "
    "fund. The state treasurer shall transfer earnings of the North Dakota legacy fund "
    "accruing after June 30, 2017, to the state general fund at the end of each biennium."
)


def norm(s):
    return " ".join((s or "").split())


def subsec3(t):
    m = re.search(r"Statutory programs.*?for those purposes\.", t)
    return norm(m.group(0)) if m else None


def main(apply=False):
    con = sqlite3.connect(DB)
    r = con.execute("SELECT p.id, p.current_version_id, v.text_content, v.effective_start "
                    "FROM provisions p JOIN provision_versions v ON v.id=p.current_version_id "
                    "WHERE p.citation=?", (CITE,)).fetchone()
    pid, vid, current, vstart = r
    current = norm(current)
    prior = norm(TEXT_2011)

    # --- gates ---
    problems = []
    s3c, s3p = subsec3(current), subsec3(prior)
    if not s3c or s3c != s3p:
        problems.append("subsec-3 (unchanged) mismatch between 2011 and current")
    for diag in ["fifteen percent", "may not be expended until after June 30, 2017",
                 "principal of the North Dakota legacy fund"]:
        if diag not in prior:
            problems.append(f"2011 text missing pre-2024 diagnostic: {diag!r}")
    for diag in ["five percent", "moneys in the legacy fund"]:
        if diag not in current:
            problems.append(f"current missing post-2024 diagnostic: {diag!r}")
    if vstart != "2024-12-05":
        problems.append(f"current effective_start is {vstart}, expected 2024-12-05 (run the amend-167 fix first)")

    print(f"art X §26: current_start={vstart}  prior={len(prior)}c  current={len(current)}c")
    print("subsec-3 identical:", s3c == s3p)
    if problems:
        print("GATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    print("GATES PASS (subsec-3 identical; pre/post-2024 diagnostics present).")

    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, BATCH))
    nvid = con.execute(
        "INSERT INTO provision_versions (provision_id, effective_start, effective_end, "
        "text_content, source_authority, source_url, batch) VALUES (?,?,?,?,?,?,?)",
        (pid, "2011-07-01", "2024-12-04", prior,
         "2011 creation measure (HCR 3054; S.L. 2011 ch. 518) — verbatim CREATE reprint",
         "https://www.legis.nd.gov/assembly/62-2011/session-laws/documents/CAA.PDF#page=1",
         BATCH)).lastrowid
    con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                "VALUES (?,?,?,?,?,?)", (BATCH, pid, nvid, "version_splice_create_head",
                "[2011-07-01 -> 2024-12-04] amend 152 create; gated vs 2024 redline (amend 167)",
                "2011 HCR 3054 / S.L. 2011 ch. 518"))
    con.commit()
    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt FROM provision_versions)
      SELECT count(*) FROM v WHERE nxt IS NOT NULL AND effective_end IS NOT NULL AND effective_end!=''
      AND date(effective_end)!=date(nxt) AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    print(f"SPLICED [2011-07-01 -> 2024-12-04]. integrity gaps={g}")
    for s, e in con.execute("SELECT effective_start, COALESCE(effective_end,'open') FROM provision_versions "
                            "WHERE provision_id=? ORDER BY effective_start", (pid,)):
        print(f"  [{s} -> {e}]")
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
