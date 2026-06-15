#!/usr/bin/env python3
"""art V § 13 dropped-section orphan — the pre-1997 executive-officers powers/duties section.

art V (Executive Branch) was repealed-and-recreated effective 1997-07-01 (measure #135), reusing
§§1-12 for new content; the recreated article has NO § 13. So "art V § 13" denoted real text only
during [1981-01-01, 1997-06-30] and resolves to nothing today. Same orphan class as the art IV
§§17-46 dropped sections; modeled on the repealed-provision convention (heading 'Repealed',
status 'repealed', a final "Repealed." sentinel version as current_version_id).

Text source: the validated historical layer 1889 § 83 (its version in force at the 1980 boundary —
officers' powers/duties "prescribed by law"), which is clean; confirmed against the marker 1989
Blue Book executive-article § 13 (the [1981,1997) witness; despaced ratio 0.982). The 1989 BB OCR
has noise ("tudUor" for auditor) — the historical layer is the cleaner authority, the BB the
numbering/era witness, same method as the art IV crosswalk.

Idempotent (batch-scoped). Scratch only.
"""
import re
import sqlite3
import sys
import difflib
from pathlib import Path

from ndcourts_mcp.corpus import cite_key

DB = "/tmp/const-scratch.db"
BATCH = "modern-artv13-orphan-2026-06-15"
CITE = "N.D. Const. art. V, § 13"
HIST = "N.D. Const. § 83"
CONTENT_END, REPEALED_START = "1997-06-30", "1997-07-01"


def dn(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def bb_marker_exec13():
    lines = Path.home().joinpath("refs/nd/const/processed/1989_blue-book-marker_constitution.md").read_text().splitlines()
    st = next(i for i, l in enumerate(lines) if "executive power shall be vested" in l.lower())
    out, cur, buf = {}, None, []
    for j in range(st, min(st + 200, len(lines))):
        if re.search(r"judicial power of the state", lines[j], re.I):
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
    return re.split(r"##\s*ARTICL", out.get("13", ""))[0]


def main(apply=False):
    con = sqlite3.connect(DB)
    problems = []
    existing = con.execute("SELECT id, status FROM provisions WHERE citation=?", (CITE,)).fetchone()
    if existing and existing[1] != "repealed":
        problems.append(f"{CITE}: a non-repealed provision already exists (id {existing[0]})")
    hist = con.execute("SELECT pv.text_content FROM provisions p JOIN provision_versions pv "
                       "ON pv.provision_id=p.id WHERE p.citation=? ORDER BY pv.effective_start DESC LIMIT 1",
                       (HIST,)).fetchone()
    if not hist:
        problems.append(f"historical {HIST} not found")
    else:
        clean = hist[0]
        r_bb = difflib.SequenceMatcher(None, dn(clean), dn(bb_marker_exec13()), autojunk=False).ratio()
        if r_bb < 0.95:
            problems.append(f"witness ratio {r_bb:.2f} < 0.95")
    if problems:
        print("GATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    print(f"{CITE} <- {HIST}  marker-1989-BB witness ratio={r_bb:.3f}  text={len(dn(clean))}c")
    print(f"  content[1981-01-01 -> {CONTENT_END}]  repealed[{REPEALED_START} -> open]")
    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    con.execute("DELETE FROM changelog WHERE batch=?", (BATCH,))
    con.execute("DELETE FROM provision_versions WHERE batch=?", (BATCH,))
    con.execute("DELETE FROM provisions WHERE corpus='const' AND citation=? "
                "AND id NOT IN (SELECT DISTINCT provision_id FROM provision_versions)", (CITE,))
    prov = con.execute("SELECT id FROM provisions WHERE citation=?", (CITE,)).fetchone()
    if prov:
        pid = prov[0]
        con.execute("UPDATE provisions SET status='repealed', heading='Repealed', hierarchy=NULL WHERE id=?", (pid,))
    else:
        pid = con.execute(
            "INSERT INTO provisions (corpus, citation, cite_key, hierarchy, heading, status, current_version_id) "
            "VALUES ('const', ?, ?, NULL, 'Repealed', 'repealed', NULL)", (CITE, cite_key(CITE))).lastrowid
    cvid = con.execute(
        "INSERT INTO provision_versions (provision_id, effective_start, effective_end, text_content, "
        "source_authority, source_path, batch) VALUES (?,?,?,?,?,?,?)",
        (pid, "1981-01-01", CONTENT_END, clean,
         f"art V § 13 (pre-1997), officers' powers/duties = 1889 § 83 (historical layer, in force at 1980); "
         f"confirmed vs marker 1989 Blue Book executive § 13 (ratio {r_bb:.2f}); art V recreated effective "
         f"1997-07-01 (measure #135) with no § 13", "crosswalk: art V § 13 (dropped) -> 1889 § 83", BATCH)).lastrowid
    rvid = con.execute(
        "INSERT INTO provision_versions (provision_id, effective_start, effective_end, text_content, "
        "source_authority, source_path, batch) VALUES (?,?,?,?,?,?,?)",
        (pid, REPEALED_START, None, "Repealed.",
         "art V § 13 repealed by the recreation of article V effective 1997-07-01 (measure #135)",
         "crosswalk: art V § 13 (dropped)", BATCH)).lastrowid
    con.execute("UPDATE provisions SET current_version_id=? WHERE id=?", (rvid, pid))
    con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                "VALUES (?,?,?,?,?,?)", (BATCH, pid, cvid, "dropped_section_orphan_created",
                f"art V § 13 [1981-01-01 -> {CONTENT_END}] (= 1889 § 83); repealed [{REPEALED_START} -> open]",
                "historical layer + marker 1989 Blue Book"))
    con.commit()

    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions) SELECT count(*) FROM v WHERE nxt IS NOT NULL
      AND effective_end IS NOT NULL AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    print(f"CREATED art V § 13 orphan. integrity gaps={g}  quick_check={con.execute('PRAGMA quick_check').fetchone()[0]}")
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
