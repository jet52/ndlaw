#!/usr/bin/env python3
"""art V [1981,1997) crosswalk — the 10 single-step shared sections (Group B).

The 1997 measure (#135, eff 1997-07-01) REPLACED/reorganized the executive article, reusing
the §-numbers for new content. For [1981-01-01, 1997-06-30] each "art V § N" denoted the OLD
(pre-1997) section. This prepends that prior version for the 10 sections whose only modern-era
change is the 1997 replacement: §§ 2, 3, 4, 5, 6, 7, 8, 9, 10, 11.

(NOT here: §1 and §12 also carry a 1986 amendment → 3-version chains, handled separately;
§13 existed pre-1997 with no post-1997 citation → orphan, handled separately.)

Text: the pre-1997 sections transcribed+reconciled from the 1989 Blue Book (the [1981,1997)
witness) cross-checked vs the 1973 BB (subagent 2026-06-15), stored in artv_pre1997.json.
Gate (here): current earliest == 1997-07-01; old != new (replacement); the prior text matches
the 1989 BB executive-article section at despaced ratio >= 0.95. Idempotent. Scratch only.
"""
import re
import json
import sqlite3
import sys
import difflib
from pathlib import Path

DB = "/tmp/const-scratch.db"
BATCH = "modern-artv-pre1997-2026-06-15"
PRIOR_START, PRIOR_END, CUR_START = "1981-01-01", "1997-06-30", "1997-07-01"
DATA = Path(__file__).parent / "artv_pre1997.json"
SECTIONS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]


def dn(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def bb_exec_sections():
    """Parse the 1989 BB executive article into {sec_num: text}."""
    lines = Path.home().joinpath("refs/nd/const/processed/1989_blue-book_constitution.md").read_text().splitlines()
    st = next(i for i, l in enumerate(lines) if "executive power shall be vested" in l.lower())
    out, cur, buf = {}, None, []
    for j in range(st, st + 160):
        m = re.match(r"\*{0,2}Section\s*(\d+)\s*\.", lines[j].strip())
        if re.search(r"the judicial power of the state|^Section 1\. The judicial", lines[j], re.I):
            break
        if m:
            if cur is not None:
                out[cur] = " ".join(buf)
            cur = m.group(1); buf = [lines[j]]
        elif cur is not None:
            buf.append(lines[j])
    if cur is not None:
        out[cur] = " ".join(buf)
    return out


def main(apply=False):
    data = json.loads(DATA.read_text())
    bb = bb_exec_sections()
    con = sqlite3.connect(DB)
    plan, problems = [], []
    for s in SECTIONS:
        cite = f"N.D. Const. art. V, § {s}"
        prov = con.execute("SELECT id FROM provisions WHERE citation=?", (cite,)).fetchone()
        if not prov:
            problems.append(f"{cite}: no provision"); continue
        pid = prov[0]
        earliest, newtext = con.execute("SELECT effective_start, text_content FROM provision_versions "
                                        "WHERE provision_id=? ORDER BY effective_start LIMIT 1", (pid,)).fetchone()
        oldtext = data[s]
        # overlap = fraction of old text found in the BB section (robust to BB-side section
        # markers / injected page headers, which a positional .ratio() penalizes)
        sm = difflib.SequenceMatcher(None, dn(oldtext), dn(bb.get(s, "")), autojunk=False)
        r_bb = sum(b.size for b in sm.get_matching_blocks()) / max(1, len(dn(oldtext)))
        if earliest == PRIOR_START:
            print(f"{cite}: already spliced (skip)"); continue
        if earliest != CUR_START:
            problems.append(f"{cite}: earliest {earliest} != {CUR_START}")
        if dn(oldtext) == dn(newtext):
            problems.append(f"{cite}: old == new")
        if r_bb < 0.97:
            problems.append(f"{cite}: 1989-BB witness overlap {r_bb:.3f} < 0.97")
        plan.append((cite, pid, oldtext, r_bb))
        print(f"{cite:24} 1989-BB-witness={r_bb:.3f}  old={len(dn(oldtext))}c new={len(dn(newtext))}c")

    if problems:
        print("\nGATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    print(f"\nGATES PASS ({len(plan)}).")
    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    for cite, pid, oldtext, r_bb in plan:
        con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, BATCH))
        nvid = con.execute(
            "INSERT INTO provision_versions (provision_id, effective_start, effective_end, "
            "text_content, source_authority, source_path, batch) VALUES (?,?,?,?,?,?,?)",
            (pid, PRIOR_START, PRIOR_END, oldtext,
             f"pre-1997 executive-article section ([1981,1997)); 1989 Blue Book witness "
             f"(ratio {r_bb:.3f}) cross-checked vs 1973 BB; replaced/reorganized 1997-07-01 (#135)",
             "1989 Blue Book + 1973 BB", BATCH)).lastrowid
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                    "VALUES (?,?,?,?,?,?)", (BATCH, pid, nvid, "version_splice_artv_prior",
                    f"[{PRIOR_START} -> {PRIOR_END}] pre-1997 executive article",
                    "1989 Blue Book + 1973 BB"))
    con.commit()
    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions) SELECT count(*) FROM v WHERE nxt IS NOT NULL
      AND effective_end IS NOT NULL AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    print(f"\nSPLICED {len(plan)}. integrity gaps={g}")
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
