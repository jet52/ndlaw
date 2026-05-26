"""§6 DEFER_MODERN — merge the LIKELY_DUP tier (docket-confirmed 1997+
double-ingests with benign text drift).

LIKELY_DUP = a DEFER_MODERN pair with 0.55 <= shingle-jaccard < 0.85,
no docket conflict, AND word-set containment >= 0.85 (the shorter
opinion's words are essentially a subset of the longer — drift from
syllabus/headnote/annotation/OCR differences, not distinct content).
The shingle-jaccard is depressed by word-order/insertion drift; the
docket match + high containment prove identity.

Eligibility: positive normalized-docket match, OR exactly one side
carries a garbage 'YYYYNDn' placeholder docket (still same neutral
cite + date) — never a docket conflict. Caption-survival policy and
caption helpers are imported verbatim from the CLEAN_DUP pass so the
two batches behave identically.

Dry-run by default. --apply requires --limit.
"""
from __future__ import annotations

import argparse
import importlib.util
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from ndcourts_mcp.db import get_connection, log_provenance  # noqa: E402
from ndcourts_mcp.merge_opinions import (  # noqa: E402
    _corpus_pairs, _jac, merge_pair)
from ndcourts_mcp.multisource_diff import normalize_words  # noqa: E402

# import the exact caption logic from the CLEAN_DUP driver (dashed name)
_spec = importlib.util.spec_from_file_location(
    "mdc_clean", HERE / "merge_defer_modern_clean_2026-05-26.py")
_mdc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mdc)
choose_caption = _mdc.choose_caption
norm_docket = _mdc.norm_docket

BATCH = "section6-defermodern-likely-2026-05-26"
_CONTAIN_FLOOR = 0.85


def _containment(conn, a, b) -> float:
    ta = conn.execute("SELECT text_content FROM opinions WHERE id=?",
                       (a,)).fetchone()[0] or ""
    tb = conn.execute("SELECT text_content FROM opinions WHERE id=?",
                       (b,)).fetchone()[0] or ""
    wa, wb = set(normalize_words(ta)), set(normalize_words(tb))
    short, lng = (wa, wb) if len(wa) <= len(wb) else (wb, wa)
    return len(short & lng) / len(short) if short else 0.0


def likely_dup_pairs(conn):
    seen = set()
    out = []
    for cite, kid, kn, did, dn in _corpus_pairs(conn)["DEFER_MODERN"]:
        if (kid, did) in seen or (did, kid) in seen:
            continue
        kd = conn.execute("SELECT date_filed,docket_number FROM opinions "
                          "WHERE id=?", (kid,)).fetchone()
        dd = conn.execute("SELECT date_filed,docket_number FROM opinions "
                          "WHERE id=?", (did,)).fetchone()
        if kd["date_filed"] != dd["date_filed"]:
            continue
        kdoc, ddoc = norm_docket(kd["docket_number"]), norm_docket(
            dd["docket_number"])
        conflict = kdoc is not None and ddoc is not None and kdoc != ddoc
        positive = kdoc is not None and kdoc == ddoc
        garbage_one = (kdoc is None) ^ (ddoc is None)
        if conflict or not (positive or garbage_one):
            continue
        j = _jac(conn, kid, did)
        if not (0.55 <= j < 0.85):
            continue
        contain = _containment(conn, kid, did)
        if contain < _CONTAIN_FLOOR:        # apply-time safety guard
            continue
        seen.add((kid, did))
        out.append((kid, kn, did, dn, j, contain))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=Path("opinions.db"))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    if args.apply and not args.limit:
        raise SystemExit("--apply requires --limit N (reviewed batch)")
    conn = get_connection(args.db)
    pairs = likely_dup_pairs(conn)

    out = ["action\tkeep\tdrop\tj\tcontain\tkeep_name\tdrop_name\t"
           "survivor_caption"]
    applied = 0
    for kid, kn, did, dn, j, contain in pairs:
        live = conn.execute("SELECT COUNT(*) FROM opinions WHERE id IN (?,?)",
                            (kid, did)).fetchone()[0]
        if live != 2:
            out.append(f"SKIP_STALE\t{kid}\t{did}\t{j:.3f}\t{contain:.3f}\t"
                       f"{kn}\t{dn}\t")
            continue
        canon = choose_caption(kn, dn)
        do = args.apply and applied < args.limit
        merge_pair(conn, kid, did, canon, apply=do, batch=BATCH)
        applied += 1 if do else 0
        out.append(f'{"MERGED" if do else "PENDING"}\t{kid}\t{did}\t'
                   f'{j:.3f}\t{contain:.3f}\t{kn}\t{dn}\t{canon}')

    rpt = Path("triage") / f"{BATCH}.tsv"
    rpt.write_text("\n".join(out), encoding="utf-8")
    if args.apply and applied:
        log_provenance(
            conn, operation="section6_defermodern_likely",
            command=f"python triage/merge_defer_modern_likely_2026-05-26.py "
                    f"--apply --limit {args.limit}",
            rows_affected=applied,
            notes=(f"batch {BATCH}; merged {applied} LIKELY_DUP 1997+ "
                   f"double-ingest pairs (0.55<=j<0.85, docket-confirmed, "
                   f"word-containment>=0.85); survivor caption = fuller "
                   f"style; NOT changelog-revertible — restore snapshot "
                   f"opinions.db.bak-pre-defermodern-likely-2026-05-26"))
        conn.commit()
    print(f"=== §6 DEFER_MODERN LIKELY_DUP: "
          f"{'APPLIED' if args.apply else 'DRY RUN'} ===")
    print(f"  likely_dup pairs  {len(pairs)}")
    print(f"  applied           {applied}")
    print(f"  report -> {rpt}")
    conn.close()


if __name__ == "__main__":
    main()
