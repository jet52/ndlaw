"""§6 DEFER_MODERN residual review — the unambiguous resolutions.

  * 10 MERGE_CLEAN: dup + CL summary stub, same primary neutral cite +
    one shared N.W.2d cite (the 5 ex-DOCKET_CONFLICT are consolidated-
    docket-list artifacts). merge stub -> full.
  * Everett 2010 ND 4: the two rows are the same opinion; one carries a
    CONTAMINATED N.W.2d cite (777 N.W.2d 62 = Cass Cnty v. Hanenberg).
    Strip the contaminant, then merge.
  * O'Hara 2017 ND 159: distinct from Jasmann 2017 ND 150; 897 N.W.2d 326
    is Jasmann's (page-json). Strip the contaminant from O'Hara (no merge).

The 7 genuinely-ambiguous pairs (original+rehearing/amended, fragment,
both-contaminated) are NOT touched here — they need a policy call.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
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

BATCH = "section6-review-clear-2026-05-26"

# (keep, drop) — keep = the full opinion (longer text), drop = the stub
CLEAN = [(12919, 12918), (13254, 13255), (13669, 13668), (13852, 13853),
         (14262, 14261), (15246, 15245), (15557, 15556), (15724, 15725),
         (15846, 15849), (15975, 15976)]


def strip_cite(conn, oid, cite, why):
    row = conn.execute("SELECT id FROM citations WHERE opinion_id=? AND "
                       "citation=?", (oid, cite)).fetchone()
    if not row:
        return False
    log_change(conn, BATCH, oid, "citation.remove", cite, None, authority=why)
    conn.execute("DELETE FROM citations WHERE id=?", (row["id"],))
    # detach a matching contaminated NW2d source, if any
    m = re.match(r"(\d+)\s*N\.?W\.?(?:2d|3d)?\s*(\d+)", cite)
    if m:
        pg = f"NW2d/{m.group(1)}/{m.group(2)}"
        for s in conn.execute("SELECT id,source_path,is_primary FROM "
                              "opinion_sources WHERE opinion_id=? AND "
                              "source_reporter='NW2d'", (oid,)).fetchall():
            if (not s["is_primary"]
                    and re.search(pg + r"(?:_\d+)?\.md$", s["source_path"] or "")):
                log_change(conn, BATCH, oid, "source.detach", s["source_path"],
                           None, authority=why)
                conn.execute("DELETE FROM opinion_sources WHERE id=?",
                             (s["id"],))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=Path("opinions.db"))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    log = []

    for keep, drop in CLEAN:
        kn = conn.execute("SELECT case_name FROM opinions WHERE id=?",
                          (keep,)).fetchone()["case_name"]
        dn = conn.execute("SELECT case_name FROM opinions WHERE id=?",
                          (drop,)).fetchone()["case_name"]
        canon = choose_caption(kn, dn)
        merge_pair(conn, keep, drop, canon, apply=args.apply, batch=BATCH)
        if args.apply:
            recompute_primary(conn, keep)
        log.append(f"MERGE_CLEAN keep {keep} <- drop {drop}  => {canon!r}")

    # Everett: strip the Hanenberg contaminant from 15332, then merge
    if args.apply:
        strip_cite(conn, 15332, "777 N.W.2d 62",
                   "contaminated: 777 N.W.2d 62 is Cass Cnty v. Hanenberg "
                   "(dk 20090135), not Everett 2010 ND 4")
        merge_pair(conn, 15508, 15332, "Everett v. State", apply=True,
                   batch=BATCH)
        recompute_primary(conn, 15508)
    log.append("EVERETT strip 777 N.W.2d 62 from 15332; merge 15508 <- 15332")

    # O'Hara: strip Jasmann's cite (distinct cases, no merge)
    if args.apply:
        strip_cite(conn, 16963, "897 N.W.2d 326",
                   "contaminated: 897 N.W.2d 326 is Jasmann v. State "
                   "(dk 20160396), not O'Hara 2017 ND 159")
    log.append("OHARA strip 897 N.W.2d 326 from 16963 (no merge)")

    if args.apply:
        log_provenance(
            conn, operation="section6_review_clear",
            command="python triage/fix_review_clear_2026-05-26.py --apply",
            rows_affected=len(CLEAN) + 2,
            notes=(f"batch {BATCH}; 10 clean dup-stub merges + Everett "
                   f"(contam-strip+merge) + O'Hara (contam-strip); snapshot "
                   f"opinions.db.bak-pre-review-clear-2026-05-26"))
        conn.commit()
    (Path("triage") / f"{BATCH}.tsv").write_text("\n".join(log), "utf-8")
    print(f"=== review-clear: {'APPLIED' if args.apply else 'DRY RUN'} ===")
    print("\n".join("  " + x for x in log))
    conn.close()


if __name__ == "__main__":
    main()
