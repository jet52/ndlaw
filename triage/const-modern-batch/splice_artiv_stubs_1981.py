#!/usr/bin/env python3
"""art IV [1981,1986) crosswalk splice — the three "[Unconstitutional.]" stubs (§§2, 5, 11).

Companion to splice_artiv_crosswalk_1981.py (the 13 clean shared sections). Article IV was
repealed-and-recreated 1986-12-01, REUSING the §1-16 citation numbers for new content. The
1981 Blue Book — the authoritative [1981,1986) witness — retained three apportionment sections
ONLY as renumbered placeholders, printing each as `Section N. [Unconstitutional.]` with no text
(BB editorial note, L37: "sections that have been declared unconstitutional have been retained
and renumbered"). Those three are new §§2, 5, 11.

User decision (2026-06-15): represent the [1981,1986) window with the ORIGINAL section text plus
a void note (not the bare marker, and not an uncovered gap). The text physically in force at 1981
is the 1960-amended version of each section (the frozen-senatorial-district scheme that drew the
unconstitutionality); it is recovered verbatim from the validated historical layer.

Crosswalk (positional — the matcher had no text to match on the stubs; pinned by the surrounding
clean sections, whose 1889 mapping is consecutive §27..§37):
    new §3->1889 §27, §4->§28, [§5->§29], §6->§30, §7->§31, §8->§32, §9->§33, §10->§34,
    [§11->§35], §12->§36, §13->§37 ; and §2->§26 (sits before §3=§27).
    => stub map: §2->§26 (senate composition), §5->§29 (senatorial districts), §11->§35 (house apportionment).
Confirmed: the 1981 BB prints exactly §2/§5/§11 as "[Unconstitutional.]" at those positions.

text_content = a bracketed void note (resting on the BB's own "[Unconstitutional.]" designation +
the 1986-12-01 recreation/repeal — no unverified case named) followed by the verbatim 1960 text.
source_authority carries full provenance. Boundary: [1981-01-01, 1986-11-30], contiguous with the
historical layer (ends 1980-12-31) and the modern recreation (starts 1986-12-01); no gaps.

Idempotent (batch-scoped). Scratch only.
"""
import re
import sqlite3
import sys
from pathlib import Path

DB = "/tmp/const-scratch.db"
BATCH = "modern-artiv-stubs-1981-1986-2026-06-15"
PRIOR_START, PRIOR_END = "1981-01-01", "1986-11-30"
XMAP = {2: 26, 5: 29, 11: 35}

VOID_NOTE = (
    'As renumbered in the 1981 compilation of the constitution, former article IV, section {n}, '
    'a legislative-apportionment provision, was designated "[Unconstitutional.]" and retained in '
    'the constitutional text only as a placeholder; it was not textually repealed until article IV '
    'was recreated effective December 1, 1986. The section, as last amended in 1960 and in force '
    '(though judicially void) during this period, read as follows.'
)


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
        earliest, newtext = con.execute(
            "SELECT effective_start, text_content FROM provision_versions WHERE provision_id=? "
            "ORDER BY effective_start LIMIT 1", (pid,)).fetchone()
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
        if "unconstitutional" not in sq(bb.get(n, "")):
            problems.append(f"{cite}: 1981 BB § {n} is not '[Unconstitutional.]' (got {bb.get(n)!r})")
        if sq(oldtext) == sq(newtext):
            problems.append(f"{cite}: old == new (unexpected for a stub)")
        body = f"[{VOID_NOTE.format(n=n)}]\n\n{oldtext}"
        plan.append((cite, pid, m, body))
        print(f"{cite:26} <- 1889 §{m:<3} BB='[Unconstitutional.]' OK  text={len(sq(oldtext))}c")

    if problems:
        print("\nGATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    if not plan:
        print("\nnothing to do"); con.close(); return
    print(f"\nGATES PASS ({len(plan)} stubs: earliest==1986-12-01; BB=='[Unconstitutional.]'; old!=new).")
    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    for cite, pid, m, body in plan:
        con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, BATCH))
        nvid = con.execute(
            "INSERT INTO provision_versions (provision_id, effective_start, effective_end, "
            "text_content, source_authority, source_path, batch) VALUES (?,?,?,?,?,?,?)",
            (pid, PRIOR_START, PRIOR_END, body,
             f"art IV § (1981 numbering) pre-1986 content = 1889 § {m} as amended 1960, in force at "
             f"1981; legislative-apportionment section designated '[Unconstitutional.]' in the 1981 "
             f"Blue Book (positional crosswalk confirmed), not textually repealed until the art IV "
             f"recreation effective 1986-12-01; clean text from the validated historical layer (§ {m})",
             f"crosswalk: art IV § (stub) -> 1889 § {m}", BATCH)).lastrowid
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                    "VALUES (?,?,?,?,?,?)", (BATCH, pid, nvid, "version_splice_unconstitutional_stub_prior",
                    f"[{PRIOR_START} -> {PRIOR_END}] pre-1986 art IV §-stub (= 1889 § {m}, void)",
                    "historical layer + 1981 Blue Book; user decision 2026-06-15 (original text + void note)"))
    con.commit()

    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions) SELECT count(*) FROM v WHERE nxt IS NOT NULL
      AND effective_end IS NOT NULL AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    print(f"\nSPLICED {len(plan)} stubs. integrity gaps={g}")
    for cite, pid, *_ in plan:
        spans = con.execute("SELECT effective_start, COALESCE(effective_end,'open') FROM provision_versions "
                            "WHERE provision_id=? ORDER BY effective_start", (pid,)).fetchall()
        print(f"  {cite.split('art. ')[1]}: " + "  ".join(f"[{s}->{e}]" for s, e in spans))
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
