"""§6 DEFER_MODERN DISTINCT_CONTAM — SAFE_STRIP tier.

Two distinct 1997+ opinions share one N.W.2d cite; the page-keyed
NW2d/<vol>/<page>.json names the true owner (by docket). The non-owner
carries the cite as CL cross-contamination AND keeps its own primary
neutral cite, so the contaminant can be stripped cleanly.

Per pair, on the NON-OWNER:
  * delete the contaminated `citations` row (the shared N.W.2d cite,
    always is_primary=0 here — the neutral cite is primary)
  * detach the contaminated `opinion_sources` NW2d row that points at
    the owner's reporter page (NW2d/<vol>/<page>.md[_n])
Both logged to changelog. The owner is left untouched.

Reads the adjudicated worklist `triage/contam-adjudication-2026-05-26.tsv`
(SAFE_STRIP rows). Dry-run by default; --apply required to write.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.db import get_connection, log_change, log_provenance  # noqa

BATCH = "section6-contam-safestrip-2026-05-26"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=Path("opinions.db"))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    rows = [l.split("\t") for l in
            open("triage/contam-adjudication-2026-05-26.tsv")
            .read().splitlines()[1:] if l.startswith("SAFE_STRIP")]

    out = ["shared\towner\tstrip\tcite_deleted\tsrc_detached\tstrip_remaining_cites"]
    n_cite = n_src = 0
    for r in rows:
        shared, owner, strip = r[1], int(r[2]), int(r[4])
        # guard: the cite on the non-owner must be secondary (is_primary=0)
        row = conn.execute(
            "SELECT id,is_primary FROM citations WHERE opinion_id=? AND "
            "citation=?", (strip, shared)).fetchone()
        if not row:
            out.append(f"{shared}\t{owner}\t{strip}\tMISSING\t\t")
            continue
        if row["is_primary"]:
            out.append(f"{shared}\t{owner}\t{strip}\tSKIP_PRIMARY\t\t")
            continue
        # contaminated NW2d source row(s): page path NW2d/<vol>/<page>(.md or _n.md)
        m = re.match(r"(\d+)\s*N\.?W\.?(?:2d|3d)?\s*(\d+)", shared)
        page = f"NW2d/{m.group(1)}/{m.group(2)}"
        srcs = conn.execute(
            "SELECT id,source_path,is_primary FROM opinion_sources WHERE "
            "opinion_id=? AND source_reporter='NW2d'", (strip,)).fetchall()
        detach = [s for s in srcs
                  if re.search(page + r"(?:_\d+)?\.md$", s["source_path"] or "")]
        # never detach a primary source (would orphan); expect ND-primary
        detach = [s for s in detach if not s["is_primary"]]

        if args.apply:
            log_change(conn, BATCH, strip, "citation.remove", shared, None,
                       authority=f"contam: {shared} owned by oid {owner} "
                                 f"per NW2d/{m.group(1)}/{m.group(2)}.json")
            conn.execute("DELETE FROM citations WHERE id=?", (row["id"],))
            for s in detach:
                log_change(conn, BATCH, strip, "source.detach",
                           s["source_path"], None,
                           authority=f"contam NW2d source for owner oid {owner}")
                conn.execute("DELETE FROM opinion_sources WHERE id=?",
                             (s["id"],))
        n_cite += 1
        n_src += len(detach)
        rem = [c[0] for c in conn.execute(
            "SELECT citation FROM citations WHERE opinion_id=?", (strip,))]
        out.append(f"{shared}\t{owner}\t{strip}\t{shared}\t"
                   f"{';'.join(s['source_path'] for s in detach)}\t{rem}")

    rpt = Path("triage") / f"{BATCH}.tsv"
    rpt.write_text("\n".join(out), encoding="utf-8")
    if args.apply:
        log_provenance(
            conn, operation="section6_contam_safestrip",
            command="python triage/fix_contam_safestrip_2026-05-26.py --apply",
            rows_affected=n_cite,
            notes=(f"batch {BATCH}; stripped {n_cite} contaminated N.W.2d "
                   f"citations + detached {n_src} contaminated NW2d sources "
                   f"from non-owner 1997+ opinions (owner = NW2d page-json "
                   f"docket); snapshot opinions.db.bak-pre-contam-2026-05-26"))
        conn.commit()
    print(f"=== contam SAFE_STRIP: {'APPLIED' if args.apply else 'DRY RUN'} ===")
    print(f"  cites stripped    {n_cite}")
    print(f"  sources detached  {n_src}")
    print(f"  report -> {rpt}")
    conn.close()


if __name__ == "__main__":
    main()
