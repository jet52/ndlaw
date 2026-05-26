"""§6 DEFER_MODERN DISTINCT_CONTAM — the 6 NEEDS_CITE pairs resolved.

These 6 "pairs" are not 6 contaminations but 12 CourtListener
"Affirmance by summary opinion" STUB rows (NW2d-only, ~400 chars, no
neutral cite) that each duplicate a full ND opinion already in the DB
(complete text, neutral cite, ndcourts.gov source). They never deduped
because the stub had no neutral cite to match on. Identity is
conclusive: same docket + parties + date + the stub's neutral cite
(recovered from the markdown tree) == the full opinion's neutral cite.

Resolution per pair:
  * 6 NON-OWNER stubs carry a CONTAMINATED N.W.2d cite (belongs to the
    page's true owner): strip the cite + detach the contaminated _2.md
    source FIRST so nothing wrong propagates, then merge stub -> full.
  * 6 OWNER stubs carry the CORRECT N.W.2d cite that the full opinion is
    MISSING: merge stub -> full so the parallel transfers, completing it.
Keep = the full ND opinion; recompute_primary keeps the neutral cite
primary and the transferred N.W.2d secondary.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from ndcourts_mcp.db import get_connection, log_change, log_provenance  # noqa
from ndcourts_mcp.ingest import recompute_primary  # noqa
from ndcourts_mcp.merge_opinions import merge_pair  # noqa

_spec = importlib.util.spec_from_file_location(
    "mdc_clean", HERE / "merge_defer_modern_clean_2026-05-26.py")
_mdc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mdc)
choose_caption = _mdc.choose_caption

BATCH = "section6-contam-stub-merge-2026-05-26"

# (stub, full, role, shared_nw_cite, contaminated_src_substr)
PAIRS = [
    (14582, 18589, "OWNER", "719 N.W.2d 384", None),
    (14583, 18591, "NONOWNER", "719 N.W.2d 384", "NW2d/719/384_2.md"),
    (17128, 19339, "OWNER", "909 N.W.2d 110", None),
    (17129, 19341, "NONOWNER", "909 N.W.2d 110", "NW2d/909/110_2.md"),
    (17131, 19342, "OWNER", "909 N.W.2d 112", None),
    (17132, 19337, "NONOWNER", "909 N.W.2d 112", "NW2d/909/112_2.md"),
    (17206, 19255, "OWNER", "913 N.W.2d 773", None),
    (17207, 19254, "NONOWNER", "913 N.W.2d 773", "NW2d/913/773_2.md"),
    (17289, 19279, "OWNER", "919 N.W.2d 334", None),
    (17290, 19277, "NONOWNER", "919 N.W.2d 334", "NW2d/919/334_2.md"),
    (17282, 19278, "OWNER", "919 N.W.2d 180", None),
    (17283, 19283, "NONOWNER", "919 N.W.2d 180", "NW2d/919/180_2.md"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=Path("opinions.db"))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    out = ["role\tstub\tfull\tshared\tsurvivor_caption\tsurvivor_cites_after"]
    merged = 0
    for stub, full, role, shared, src in PAIRS:
        sn = conn.execute("SELECT case_name FROM opinions WHERE id=?",
                          (stub,)).fetchone()
        fn = conn.execute("SELECT case_name FROM opinions WHERE id=?",
                          (full,)).fetchone()
        if sn is None or fn is None:
            out.append(f"{role}\t{stub}\t{full}\t{shared}\tMISSING_ROW\t")
            continue
        if args.apply and role == "NONOWNER":
            # strip the contaminated cite + detach the contaminated source
            cid = conn.execute("SELECT id FROM citations WHERE opinion_id=? "
                               "AND citation=?", (stub, shared)).fetchone()
            if cid:
                log_change(conn, BATCH, stub, "citation.remove", shared, None,
                           authority=f"contaminated cite (owner is the "
                                     f"{shared} page); stub merging to {full}")
                conn.execute("DELETE FROM citations WHERE id=?", (cid["id"],))
            if src:
                s = conn.execute("SELECT id,source_path FROM opinion_sources "
                                 "WHERE opinion_id=? AND source_path=?",
                                 (stub, src)).fetchone()
                if s:
                    log_change(conn, BATCH, stub, "source.detach", src, None,
                               authority="contaminated NW2d page source")
                    conn.execute("DELETE FROM opinion_sources WHERE id=?",
                                 (s["id"],))
        canon = choose_caption(fn["case_name"], sn["case_name"])
        merge_pair(conn, full, stub, canon, apply=args.apply, batch=BATCH)
        if args.apply:
            recompute_primary(conn, full)
            merged += 1
        cites = [c[0] for c in conn.execute(
            "SELECT citation FROM citations WHERE opinion_id=? "
            "ORDER BY is_primary DESC", (full,))] if args.apply else []
        out.append(f"{role}\t{stub}\t{full}\t{shared}\t{canon}\t{cites}")

    rpt = Path("triage") / f"{BATCH}.tsv"
    rpt.write_text("\n".join(out), encoding="utf-8")
    if args.apply:
        log_provenance(
            conn, operation="section6_contam_stub_merge",
            command="python triage/merge_contam_stubs_2026-05-26.py --apply",
            rows_affected=merged,
            notes=(f"batch {BATCH}; merged {merged} CL summary-stub dups into "
                   f"full ND opinions (6 owner stubs transfer the correct "
                   f"N.W.2d parallel; 6 non-owner stubs had the contaminant "
                   f"stripped first); NOT changelog-revertible (row deletes) "
                   f"— snapshot opinions.db.bak-pre-contam-stub-2026-05-26"))
        conn.commit()
    print(f"=== contam stub-merge: {'APPLIED' if args.apply else 'DRY RUN'} ===")
    print(f"  pairs merged   {merged if args.apply else 0} / {len(PAIRS)}")
    print(f"  report -> {rpt}")
    conn.close()


if __name__ == "__main__":
    main()
