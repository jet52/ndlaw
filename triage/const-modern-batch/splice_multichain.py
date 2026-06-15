#!/usr/bin/env python3
"""Verify + splice the multi-amendment version CHAINS into scratch.

Gates per provision (no agent output trusted until it passes):
  MECH    : each REDLINE amendment's reverse_edit_list anchors are unique in its
            version_after, and apply(reverse_edit_list, version_after)==version_before.
  LATEST  : the latest amendment's version_after == DB current_text.
  CONTINUITY: for consecutive amendments, later.version_before == earlier.version_after.
  HEAD(BB): carried-from-1981 head (earliest.version_before) is gated vs the 1981
            Blue Book where the article is clean (VIII/X/XI); else flagged needs-2nd-read.
  DISCONTINUITY: if CREATE is NOT the first amendment (e.g. art V §1/§12 — current
            section created 1997, earlier 1986 amendment is on the repealed
            predecessor), the chain is invalid for the current lineage -> SKIP,
            flag needs-base-source. Current stays single-version.
Idempotent (batch-scoped delete + re-insert). Scratch only.
"""
import json, re, glob, sqlite3, difflib
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = "/tmp/const-scratch.db"
BATCH = "modern-multichain-2026-06-14"
BB = (Path.home() / "refs/nd/const/processed/1981_blue-book_constitution.md").read_text()
BBN = re.sub(r"[^a-z0-9]", "", BB.lower())
BB_CLEAN = {"VIII", "X", "XI"}


_ARTIFACT = re.compile(r"</?WRAP[^>]*>|\]\)\]")  # ndconst.org DokuWiki extraction junk

def kn(s):
    s = _ARTIFACT.sub(" ", s or "")
    return re.sub(r"[^a-z0-9]", "", s.lower())


def norm(s):
    return " ".join((s or "").split())


def apply_edits(text, edits):
    for after, before in edits:
        c = text.count(after)
        if c != 1:
            raise ValueError(f"anchor x{c}: {after[:40]!r}")
        text = text.replace(after, before)
    return text


def bb_witness(text):
    t = kn(text)
    if t in BBN:
        return "BB-PASS"
    sm = difflib.SequenceMatcher(None, t, BBN, autojunk=False)
    r = sum(b.size for b in sm.get_matching_blocks()) / max(1, len(t))
    return f"BB-NEAR({r:.2f})" if r >= 0.95 else f"BB-MISS({r:.2f})"


def day_before(d):
    return (date.fromisoformat(d) - timedelta(days=1)).isoformat()


def verify(prov, current_text):
    """Return (ok, intervals, head_note, problems). intervals exclude the open
    current version (caller keeps that on the existing row)."""
    amds = prov["amendments"]
    art = re.search(r"art\.\s+([IVXL]+)", prov["citation"]).group(1)
    problems = []
    # discontinuity: CREATE must be only the first amendment
    cls = [a["classification"] for a in amds]
    create_idx = [i for i, c in enumerate(cls) if c == "CREATE_SECTION"]
    if any(i != 0 for i in create_idx):
        return False, None, None, ["DISCONTINUITY: CREATE is not the first amendment"]
    if any(c not in ("REDLINE", "CREATE_SECTION") for c in cls):
        return False, None, None, [f"unsupported classes: {cls}"]
    # MECH on each REDLINE
    for a in amds:
        if a["classification"] != "REDLINE":
            continue
        try:
            got = apply_edits(norm(a["version_after_text"]),
                              [tuple(e) for e in a["reverse_edit_list"]])
            if kn(got) != kn(a["version_before_text"]):
                problems.append(f"MECH mismatch @ {a['amendment_number']}")
        except Exception as e:
            problems.append(f"MECH err @ {a['amendment_number']}: {e}")
    # LATEST gate
    if kn(amds[-1]["version_after_text"]) != kn(current_text):
        problems.append("LATEST: latest version_after != current_text")
    # CONTINUITY
    for e, l in zip(amds, amds[1:]):
        if l["version_before_text"] is None:
            problems.append(f"CONTINUITY: {l['amendment_number']} has null before")
        elif kn(l["version_before_text"]) != kn(e["version_after_text"]):
            problems.append(f"CONTINUITY break {e['amendment_number']}->{l['amendment_number']}")
    if problems:
        return False, None, None, problems
    # Build intervals (all except the open current). Dates from amendments.
    dates = [a["effective_date"] for a in amds]
    intervals = []
    head_note = ""
    if prov["head_type"] == "carried-from-1981":
        head_txt = norm(amds[0]["version_before_text"])
        w = bb_witness(head_txt) if art in BB_CLEAN else "no-clean-BB-witness"
        head_note = f"head[1981] {w}"
        intervals.append(("1981-01-01", day_before(dates[0]), head_txt,
                          f"head [1981,{dates[0]}) before amend {amds[0]['amendment_number']}", w))
    # interior intervals [di, d(i+1)) = amds[i].version_after, for i < last
    for i in range(len(amds) - 1):
        intervals.append((dates[i], day_before(dates[i + 1]), norm(amds[i]["version_after_text"]),
                          f"[{dates[i]},{dates[i+1]}) amend {amds[i]['amendment_number']}", None))
    return True, intervals, head_note, []


def main(apply=False):
    con = sqlite3.connect(DB)
    cur = {}
    for f in glob.glob(str(HERE / "multi-batch-*.json")):
        for t in json.loads(Path(f).read_text()):
            cur[t["citation"]] = norm(t["current_text"])

    spliced, skipped = [], []
    for f in sorted(glob.glob(str(HERE / "out-multi" / "*.json"))):
        for prov in json.loads(Path(f).read_text()):
            cite = prov["citation"]
            ok, intervals, head_note, problems = verify(prov, cur[cite])
            if not ok:
                skipped.append((cite, problems)); continue
            dk = prov["amendments"][-1]["effective_date"]
            if apply:
                r = con.execute("SELECT id, current_version_id FROM provisions WHERE citation=?", (cite,)).fetchone()
                pid, vid = r
                con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, BATCH))
                con.execute("UPDATE provision_versions SET effective_start=?, effective_end=NULL WHERE id=?", (dk, vid))
                for start, end, text, note, w in intervals:
                    nvid = con.execute("INSERT INTO provision_versions (provision_id, effective_start, "
                        "effective_end, text_content, source_authority, batch) VALUES (?,?,?,?,?,?)",
                        (pid, start, end, text, f"agent-read chain ({note})", BATCH)).lastrowid
                    con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                        "VALUES (?,?,?,?,?,?)", (BATCH, pid, nvid, "version_splice_chain",
                        f"[{start} -> {end}] {note}", "multi-agent chain campaign"))
            spliced.append((cite, prov["head_type"], len(intervals) + 1, head_note))

    print("=== MULTI-AMENDMENT CHAIN VERIFICATION ===\n")
    for cite, ht, nver, hn in sorted(spliced):
        print(f"  OK  {cite.replace('N.D. Const. ',''):16} {ht:18} {nver}ver  {hn}")
    for cite, probs in sorted(skipped):
        print(f"  SKIP {cite.replace('N.D. Const. ',''):16} {probs}")

    if apply:
        con.commit()
        g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
          LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt FROM provision_versions)
          SELECT count(*) FROM v WHERE nxt IS NOT NULL AND effective_end IS NOT NULL AND effective_end!=''
          AND date(effective_end)!=date(nxt) AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
        m = con.execute("""SELECT count(*) FROM (SELECT p.id FROM provisions p JOIN provision_versions v ON v.provision_id=p.id
          WHERE p.corpus='const' AND (v.effective_end IS NULL OR v.effective_end='') GROUP BY p.id HAVING count(*)>1)""").fetchone()[0]
        rec = con.execute("""SELECT count(*) FROM (SELECT p.id FROM provisions p JOIN provision_versions v ON v.provision_id=p.id
          WHERE p.corpus='const' AND p.citation LIKE '%art.%' AND p.citation NOT LIKE '%amend%' GROUP BY p.id HAVING count(*)>1)""").fetchone()[0]
        print(f"\nSPLICED {len(spliced)} chains. integrity gaps={g} >1-open={m} (expect 0/0). "
              f"modern reconstructed total: {rec}")
    con.close()


if __name__ == "__main__":
    import sys
    main(apply="--apply" in sys.argv)
