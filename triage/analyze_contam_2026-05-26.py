"""Read-only adjudication of the §6 DEFER_MODERN DISTINCT_CONTAM tier.

Each pair = two distinct 1997+ opinions sharing one N.W.2d cite; one
owns the reporter page, the other carries it as CL cross-contamination.
Authoritative owner = the case named in NW2d/<vol>/<page>.json (keyed
by reporter page, so it identifies the true occupant by docket).

For each pair, determine the owner (docket match), then classify the
fix for the non-owner:
  SAFE_STRIP    non-owner keeps a primary neutral cite after the strip
  NEEDS_CITE    the shared cite is the non-owner's ONLY cite — stripping
                leaves it citeless; its correct cite must be found first
  NO_JSON       NW2d page file absent — owner undetermined (manual/PDF)
  OWNER_NEITHER json docket matches neither opinion (both contaminated,
                or a third-opinion owner) — manual
Also flags whether the non-owner has an NW2d *source row* pointing at
the contaminated page (a source to detach too).
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB = Path("opinions.db")
NW = Path("/Users/jerod/refs/nd/opin/NW2d")


def ndigits(d):
    return re.sub(r"\D", "", d or "")


def docket_eq(a, b):
    da, db_ = ndigits(a), ndigits(b)
    if not da or not db_:
        return False
    if da == db_:
        return True
    # CL century-prefix tolerance (19970181 vs 970181)
    for x, y in ((da, db_), (db_, da)):
        if len(x) >= 6 and x[:2] in ("19", "20") and x[2:] == y:
            return True
    return False


def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = [l.split("\t") for l in
            open("triage/defer-modern-adjudication-2026-05-26.tsv")
            .read().splitlines()[1:] if l.startswith("DISTINCT_CONTAM")]
    seen = set()
    out = ["bucket\tshared\towner_oid\towner_case\tstrip_oid\tstrip_case\t"
           "strip_fallback_cite\tstrip_has_nw_src\tjson_docket"]
    from collections import Counter
    cnt = Counter()
    for r in rows:
        shared, a, b = r[1], int(r[2]), int(r[3])
        if (a, b) in seen or (b, a) in seen:
            continue
        seen.add((a, b))
        m = re.match(r"(\d+)\s*N\.?W\.?(?:2d|3d)?\s*(\d+)", shared)
        jp = NW / m.group(1) / f"{m.group(2)}.json" if m else None
        oa = conn.execute("SELECT case_name,docket_number FROM opinions "
                          "WHERE id=?", (a,)).fetchone()
        ob = conn.execute("SELECT case_name,docket_number FROM opinions "
                          "WHERE id=?", (b,)).fetchone()
        if not (jp and jp.exists()):
            cnt["NO_JSON"] += 1
            out.append(f"NO_JSON\t{shared}\t\t\t\t\t\t\t")
            continue
        jdoc = json.loads(jp.read_text()).get("docket_number", "")
        if docket_eq(jdoc, oa["docket_number"]):
            owner, strip = a, b
            oc, sc = oa, ob
        elif docket_eq(jdoc, ob["docket_number"]):
            owner, strip = b, a
            oc, sc = ob, oa
        else:
            cnt["OWNER_NEITHER"] += 1
            out.append(f"OWNER_NEITHER\t{shared}\t\t\t\t\t\t\t{jdoc!r}")
            continue
        # non-owner fallback: a primary cite that is NOT the shared one
        fb = conn.execute(
            "SELECT citation FROM citations WHERE opinion_id=? AND "
            "is_primary=1 AND citation<>?", (strip, shared)).fetchone()
        fallback = fb[0] if fb else ""
        # does the non-owner carry an NW2d source for the contaminated page?
        nwsrc = conn.execute(
            "SELECT source_path FROM opinion_sources WHERE opinion_id=? "
            "AND source_reporter='NW2d'", (strip,)).fetchall()
        page = f"NW2d/{m.group(1)}/{m.group(2)}"
        has_nw_src = any(page in (s["source_path"] or "") for s in nwsrc)
        bucket = "SAFE_STRIP" if fallback else "NEEDS_CITE"
        cnt[bucket] += 1
        out.append(
            f"{bucket}\t{shared}\t{owner}\t{oc['case_name']!r}\t{strip}\t"
            f"{sc['case_name']!r}\t{fallback}\t{int(has_nw_src)}\t{jdoc!r}")
    conn.close()
    rpt = Path("triage") / "contam-adjudication-2026-05-26.tsv"
    rpt.write_text("\n".join(out), encoding="utf-8")
    print(f"=== DISTINCT_CONTAM adjudication ({sum(cnt.values())} pairs) ===")
    for b, n in cnt.most_common():
        print(f"  {b:16s} {n}")
    print(f"  report -> {rpt}")


if __name__ == "__main__":
    main()
