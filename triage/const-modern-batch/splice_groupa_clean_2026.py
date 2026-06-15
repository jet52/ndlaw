#!/usr/bin/env python3
"""needs-base-source Group A — the clean single-amendment splices.

The "needs-base-source" bucket was classified before the 1989 Blue Book was acquired;
most of it is in fact reconstructable from the 1981/1989 BBs + the validated historical
layer. This handles the two TRIVIAL single-amendment members (art XIII §1 — a 3-subsection
1996 drop — is handled separately):

- **art I § 1** (inalienable rights): amendment #116 (eff 1984-12-06, "Establishes the
  right to bear arms") was a full restatement that added the keep-and-bear-arms clause and
  modernized "men"->"individuals". Prior [1981, 1984-12-05] = the pre-1984 text = historical
  § 1 (1889 numbering, in force 1980; == 1981 BB at ratio 1.0).

- **art X § 6** (poll tax): amendment #154 (eff 2012-12-06, "Elimination of annual poll
  tax") repealed it. The current "Repealed." version already starts 2012-12-06. Prepend the
  pre-2012 full text = historical § 180 (== 1989 BB witness). [1981, 2012-12-05].

Clean source = the validated historical layer (snapshot-diff green vs 1925/54/73); each
confirmed against the modern-scheme BB witness. Idempotent (batch-scoped). Scratch only.
"""
import re
import sqlite3
import sys
import difflib
from pathlib import Path

DB = "/tmp/const-scratch.db"
BATCH = "modern-groupa-clean-2026-06-15"
PROC = Path.home() / "refs/nd/const/processed"

# modern cite : (hist 1889 §, prior_start, prior_end, expected current start, BB file, remove)
# `remove` = an editorial substring in the historical text that the modern-era BB witnesses
# omit (modern witnesses govern the modern-era version, cf. art XII §12/§14).
JOBS = {
    "N.D. Const. art. I, § 1": (1, "1981-01-01", "1984-12-05", "1984-12-06",
                                "1981_blue-book_constitution.md", None),
    "N.D. Const. art. X, § 6": (180, "1981-01-01", "2012-12-05", "2012-12-06",
                                "1989_blue-book_constitution.md", " ($1.50)"),
}


def dn(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main(apply=False):
    con = sqlite3.connect(DB)
    plan, problems = [], []
    bbcache = {}
    for cite, (m, ps, pe, cstart, bbf, remove) in JOBS.items():
        prov = con.execute("SELECT id FROM provisions WHERE citation=?", (cite,)).fetchone()
        if not prov:
            problems.append(f"{cite}: no provision"); continue
        pid = prov[0]
        earliest, newtext = con.execute(
            "SELECT effective_start, text_content FROM provision_versions WHERE provision_id=? "
            "ORDER BY effective_start LIMIT 1", (pid,)).fetchone()
        hist = con.execute("SELECT pv.text_content FROM provisions p JOIN provision_versions pv "
                           "ON pv.provision_id=p.id WHERE p.citation=? ORDER BY pv.effective_start DESC "
                           "LIMIT 1", (f"N.D. Const. § {m}",)).fetchone()
        if not hist:
            problems.append(f"{cite}: historical § {m} not found"); continue
        oldtext = hist[0].replace(remove, "") if remove else hist[0]
        if bbf not in bbcache:
            bbcache[bbf] = dn((PROC / bbf).read_text())
        bb = bbcache[bbf]
        # witness: the (modern-era) old text must appear in the modern-scheme BB (despaced
        # containment — robust to position/section-prefix; the OCR is light enough for these two)
        contained = dn(oldtext) in bb
        # gates
        if earliest == ps:
            print(f"{cite}: already has {ps} version (idempotent skip)"); continue
        if earliest != cstart:
            problems.append(f"{cite}: earliest starts {earliest}, expected {cstart}")
        if dn(oldtext) == dn(newtext):
            problems.append(f"{cite}: old == new")
        if not contained:
            problems.append(f"{cite}: old text NOT contained in {bbf} (witness fail)")
        plan.append((cite, pid, m, oldtext, ps, pe, contained))
        print(f"{cite:24} <- hist §{m:<4} BB-contained={contained}  prior=[{ps}->{pe}]  old={len(dn(oldtext))}c")

    if problems:
        print("\nGATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    if not plan:
        print("nothing to do"); con.close(); return
    print(f"\nGATES PASS ({len(plan)}).")
    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    for cite, pid, m, oldtext, ps, pe, contained in plan:
        con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, BATCH))
        nvid = con.execute(
            "INSERT INTO provision_versions (provision_id, effective_start, effective_end, "
            "text_content, source_authority, source_path, batch) VALUES (?,?,?,?,?,?,?)",
            (pid, ps, pe, oldtext,
             f"pre-amendment text from validated historical layer § {m} (1889 numbering, in force "
             f"1980 = the [1981, change) content); confirmed present in the modern-scheme Blue Book",
             f"crosswalk: -> 1889 § {m}", BATCH)).lastrowid
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                    "VALUES (?,?,?,?,?,?)", (BATCH, pid, nvid, "version_splice_groupa_prior",
                    f"[{ps} -> {pe}] pre-amendment (= 1889 § {m})",
                    "historical layer + Blue Book witness"))
    con.commit()
    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions) SELECT count(*) FROM v WHERE nxt IS NOT NULL
      AND effective_end IS NOT NULL AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    print(f"\nSPLICED {len(plan)}. integrity gaps={g}")
    for cite, pid, *_ in plan:
        spans = con.execute("SELECT effective_start, COALESCE(effective_end,'open') FROM provision_versions "
                            "WHERE provision_id=? ORDER BY effective_start", (pid,)).fetchall()
        print(f"  {cite}: " + "  ".join(f"[{s}->{e}]" for s, e in spans))
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
