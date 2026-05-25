"""§10 resequence — recompute the synthetic YYYY ND nnn cites from the CURRENT
DB state and apply ONLY the cites that changed (minimal, clean, re-runnable).

Run after any data correction that affects pre-1997 ordering (date_filed change,
de-dup, new ingest). It reproduces the Phase-1A ordering — default sort
(date_filed, ND-page, NW-page, oid) — and then re-deals the within-cluster numbers
for the shared-page clusters whose true on-page order has been verified from the
bound volumes (encoded in KNOWN_ORDER, deviating from the default oid/NW tiebreak).
Numbers stay PROVISIONAL until the publish freeze.

This SUPERSEDES the one-shot fix_section10_cluster_order / _ndverify scripts as the
canonical ordering tool (their effect is folded into KNOWN_ORDER here).

Modes: --apply (default --dry-run).
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change  # noqa: E402

BATCH = "section10-resequence-2026-05-25d"
SYNTH = "ND-neutral-synthetic"
INF = 10**9
ND_RE = re.compile(r"^(\d+)\s+N\.D\.\s+(\d+)")
NW2D_RE = re.compile(r"^(\d+)\s+N\.W\.2d\s+(\d+)")
NW_RE = re.compile(r"^(\d+)\s+N\.W\.\s+(\d+)")

# Verified on-page publication order (oids top-to-bottom) for shared-page clusters
# whose true order deviates from the default (date, ND-page, NW-page, oid) sort.
# Sources: bound N.D. Reports scans, vols 3/9/44 (CHANGELOG 2026-05-24 batches).
#
# CONVENTION (ruled 2026-05-25): for a lead opinion and its SAME-DAY dependent
# per curiam that share a page, order the LEAD first even when the reporter prints
# the short companion ABOVE it (e.g. 17 N.D. 266 Skeffington/Ross; 18 N.D. 76
# Willis). Top-of-page placement of a short companion is a typesetting/space-fill
# artifact, not decision sequence. Do NOT add a KNOWN_ORDER flip for these — the
# default NW-page tiebreak already puts the lead first. KNOWN_ORDER is only for
# genuine same-day ties whose verified bound order differs from the default sort.
KNOWN_ORDER = [
    [152, 146],              # 14 N.D. 557: Murphy (writ denied, top), Poull
    [5275, 5274],            # 3 N.D. 538: Globe, Kellogg
    [20489, 5754],           # 9 N.D. 608: Cranmer, Davidson
    [20491, 20490, 5753],    # 9 N.D. 609: Davidson, Baker, Couch
    [20492, 20493, 5752],    # 9 N.D. 610: Cranmer, Ganger, Kelly
    [5751, 20494, 20500],    # 9 N.D. 611: Lilly, McKenzie, McKenzie
    [20495, 20496, 5750],    # 9 N.D. 612: McKenzie, McLain, Mellon
    [20497, 20501, 5749],    # 9 N.D. 613: Mellon, Mellon, Robinson
    [5748, 20502],           # 9 N.D. 614: Thistlewaite, Thistlewaite
    [2169, 2167],            # 44 N.D. 250: Nelson, Olson (ND governs over NW tie)
    [4484, 4482],            # 64 N.D. 367: Ott v. Kelley (per curiam, File 6233) above
                             # Thorvaldson-Johnson (File 6234) — ND bound order by file
                             # no. governs the NW tie (Ott 271 prints above Thorv. 268)
]


class Op:
    __slots__ = ("oid", "date", "year", "nd", "nw")

    def __init__(self, oid, date):
        self.oid, self.date, self.year = oid, date, date[:4]
        self.nd = self.nw = None

    @property
    def sort_key(self):
        return (self.date, self.nd or (INF, INF), self.nw or (INF, INF), self.oid)


def load(conn):
    rows = conn.execute(
        "SELECT id, date_filed FROM opinions WHERE date_filed < '1997-01-01'").fetchall()
    ops = {r["id"]: Op(r["id"], r["date_filed"]) for r in rows}
    cites = conn.execute(
        "SELECT opinion_id, citation, reporter FROM citations c "
        "WHERE opinion_id IN (SELECT id FROM opinions WHERE date_filed < '1997-01-01') "
        "ORDER BY is_primary DESC, id").fetchall()
    for c in cites:
        op = ops[c["opinion_id"]]
        rep, cite = c["reporter"], c["citation"]
        if rep == "ND" and op.nd is None:
            m = ND_RE.match(cite)
            if m:
                op.nd = (int(m.group(1)), int(m.group(2)))
        elif rep in ("NW2d", "NW") and op.nw is None:
            m = (NW2D_RE if rep == "NW2d" else NW_RE).match(cite)
            if m:
                op.nw = (int(m.group(1)), int(m.group(2)))
    return list(ops.values())


def desired_cites(ops):
    ordered = sorted(ops, key=lambda o: o.sort_key)
    counter = defaultdict(int)
    cite = {}
    for op in ordered:
        counter[op.year] += 1
        cite[op.oid] = f"{op.year} ND {counter[op.year]}"
    # re-deal within each verified cluster (keep the number set, reorder oids)
    for cluster in KNOWN_ORDER:
        nums = sorted((cite[o] for o in cluster),
                      key=lambda s: int(s.rsplit(" ", 1)[1]))
        for oid, new in zip(cluster, nums):
            cite[oid] = new
    return cite


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)

    want = desired_cites(load(conn))
    have = {r["opinion_id"]: (r["id"], r["citation"]) for r in conn.execute(
        "SELECT id, opinion_id, citation FROM citations WHERE reporter=?", (SYNTH,))}

    if set(want) != set(have):
        raise SystemExit(f"coverage mismatch: want {len(want)} vs have {len(have)} synthetic rows")

    diffs = [(have[o][0], o, have[o][1], want[o]) for o in want if have[o][1] != want[o]]
    diffs.sort(key=lambda d: (len(d[3]), d[3]))
    for _row, oid, old, new in diffs:
        print(f"  oid {oid:>6}  {old:>11} -> {new}")
    print(f"\n{'APPLY' if args.apply else 'DRY-RUN'}: {len(diffs)} of {len(want)} synthetic cites change.")
    if not args.apply:
        print("re-run with --apply.")
        return 0

    for row_id, _o, _old, _new in diffs:
        conn.execute("UPDATE citations SET citation = citation || '#tmp' WHERE id=?", (row_id,))
    for row_id, oid, old, new in diffs:
        conn.execute("UPDATE citations SET citation=? WHERE id=?", (new, row_id))
        log_change(conn, BATCH, oid, "citation_synthetic_order", old, new,
                   authority="section10 resequence after date/cite corrections")
    conn.commit()
    print(f"Applied {len(diffs)} changes; batch {BATCH}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
