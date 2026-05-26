"""Classify the 29 residual §6 DEFER_MODERN review pairs into actions.

Buckets:
  MERGE_CLEAN   same primary neutral cite, no N.W.2d conflict -> dup
                (one side usually a CL summary stub); merge stub->full.
  MERGE_FIX_NW  same neutral cite but the two rows carry DIFFERENT N.W.2d
                cites -> dup whose stub has a wrong/contaminated N.W.2d;
                resolve the correct page via NW2d/<vol>/<page>.json docket,
                keep the full row + correct N.W.2d, drop the other N.W.2d.
  STRIP_CONTAM  different neutral cites (distinct cases) sharing one N.W.2d
                cite; page-json names the owner -> strip from the non-owner.
  INVESTIGATE   page-json owner matches neither / ambiguous -> manual+PDF.

keep = the longer-text row (the full opinion; the stub is the short one).
Read-only: prints the plan; writes nothing.
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DB = Path("opinions.db")
NW = Path("/Users/jerod/refs/nd/opin/NW2d")
TSV = "triage/defer-modern-adjudication-2026-05-26.tsv"


def ndig(d):
    return re.sub(r"\D", "", d or "")


def dock_match(a, b):
    """tolerant: equal digits, century-prefix, or one is a member of the
    other's consolidated list."""
    da, dbb = ndig(a), ndig(b)
    if da and da == dbb:
        return True
    aset = {ndig(x) for x in re.split(r"[,;]", a or "") if ndig(x)}
    bset = {ndig(x) for x in re.split(r"[,;]", b or "") if ndig(x)}
    if aset & bset:
        return True
    for x in list(aset):
        for y in list(bset):
            if len(x) >= 6 and x[:2] in ("19", "20") and x[2:] == y:
                return True
            if len(y) >= 6 and y[:2] in ("19", "20") and y[2:] == x:
                return True
    return False


def page_owner_docket(nwcite):
    m = re.match(r"(\d+)\s*N\.?W\.?(?:2d|3d)?\s*(\d+)", nwcite)
    if not m:
        return None
    jp = NW / m.group(1) / f"{m.group(2)}.json"
    if not jp.exists():
        return None
    return json.loads(jp.read_text()).get("docket_number")


def main():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    rows = [l.split("\t") for l in open(TSV).read().splitlines()[1:]
            if l.split("\t")[0] in ("LOWJAC_REVIEW", "DOCKET_CONFLICT_MIDJAC")]
    seen = set()
    from collections import Counter
    cnt = Counter()
    plan = []
    for r in rows:
        a, b = int(r[2]), int(r[3])
        if (a, b) in seen or (b, a) in seen:
            continue
        seen.add((a, b))

        def get(oid):
            o = db.execute("SELECT case_name,docket_number,date_filed,"
                           "length(text_content) tl FROM opinions WHERE id=?",
                           (oid,)).fetchone()
            neu = db.execute("SELECT citation FROM citations WHERE opinion_id=?"
                             " AND reporter='ND-neutral' AND is_primary=1",
                             (oid,)).fetchone()
            nws = [c[0] for c in db.execute(
                "SELECT citation FROM citations WHERE opinion_id=? AND "
                "reporter IN ('NW2d','NW3d')", (oid,))]
            return o, (neu[0] if neu else None), nws
        oa, na, nwa = get(a)
        ob, nb, nwb = get(b)
        # keep = longer text (full opinion); drop = shorter (stub)
        if oa["tl"] >= ob["tl"]:
            keep, drop, nk, nd_, nwk, nwd, ok, od = a, b, na, nb, nwa, nwb, oa, ob
        else:
            keep, drop, nk, nd_, nwk, nwd, ok, od = b, a, nb, na, nwb, nwa, ob, oa

        same_neutral = nk and nd_ and re.sub(r"\W", "", nk.lower()) == \
            re.sub(r"\W", "", nd_.lower())
        if same_neutral:
            allnw = set(nwk) | set(nwd)
            if len(allnw) <= 1:
                bucket = "MERGE_CLEAN"
                detail = f"neutral={nk}; nw={allnw}"
            else:
                # resolve which NW is correct via page-json docket
                correct = []
                for c in allnw:
                    od_ = page_owner_docket(c)
                    if od_ and (dock_match(od_, ok["docket_number"]) or
                                dock_match(od_, od["docket_number"])):
                        correct.append(c)
                wrong = [c for c in allnw if c not in correct]
                bucket = "MERGE_FIX_NW"
                detail = f"neutral={nk}; correct_nw={correct}; drop_nw={wrong}"
        else:
            # distinct cases sharing an NW cite -> contamination
            shared = (set(nwk) & set(nwd))
            if not shared:
                bucket = "INVESTIGATE"
                detail = f"distinct neutrals {nk!r}/{nd_!r}, no shared NW?"
            else:
                sc = list(shared)[0]
                od_ = page_owner_docket(sc)
                if od_ and dock_match(od_, ok["docket_number"]):
                    bucket = "STRIP_CONTAM"
                    detail = f"owner={keep}; strip {sc} from {drop}"
                elif od_ and dock_match(od_, od["docket_number"]):
                    bucket = "STRIP_CONTAM"
                    detail = f"owner={drop}; strip {sc} from {keep}"
                else:
                    bucket = "INVESTIGATE"
                    detail = f"page-owner dk={od_!r} matches neither ({sc})"
        cnt[bucket] += 1
        plan.append((bucket, keep, drop, ok["case_name"], od["case_name"],
                     detail))
    db.close()
    for b, k, d, kn, dn, det in sorted(plan):
        print(f"[{b}] keep {k} {kn!r} <- drop {d} {dn!r}")
        print(f"      {det}")
    print("\n=== buckets ===")
    for b, n in cnt.most_common():
        print(f"  {b:14s} {n}")


if __name__ == "__main__":
    main()
