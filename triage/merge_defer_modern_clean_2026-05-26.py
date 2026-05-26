"""§6 DEFER_MODERN — merge the CLEAN_DUP tier (docket-confirmed
1997+ double-ingests).

A DEFER_MODERN pair is two opinions that share a native `YYYY ND n`
neutral cite with keep.date_filed >= 1997. CLEAN_DUP = text jaccard
>= 0.85 AND no docket conflict (a garbage 'YYYYNDn' placeholder docket
on one side counts as no-conflict, not a conflict). Every such pair is
the same opinion ingested twice under two caption styles.

Survivor (keep) = the more-cited row (scan heuristic). Survivor caption
= the fuller of the two captions (period-initials / 'Interest of' /
'Disciplinary Board v.' style preferred over smushed 'In re GRH'),
with trailing consolidation/confidential/docket annotations stripped.
Caller policy ratified 2026-05-26.

Dry-run by default. --apply requires --limit (reviewed batch). Snapshot
+ invariants are run by the shell wrapper, not here.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.db import get_connection, log_provenance  # noqa: E402
from ndcourts_mcp.merge_opinions import (  # noqa: E402
    _canonical_name, _corpus_pairs, _jac, merge_pair)

BATCH = "section6-defermodern-clean-2026-05-26"

# true dups whose BOTH captions are mangled (no clean full-style choice);
# merge deferred to the worklist for a hand-picked caption rather than
# imposing a bad one. 2005 ND 75 = the State Fire & Tornado Fund multi-
# party 'ex rel.' case; real caption needs human selection.
_DEFER_CAPTION = {(14224, 14223)}

# a trailing parenthetical whose interior matches this is metadata
# (consolidation/cross-reference/confidential/docket), not caption text
_ANNOT_META = re.compile(
    r"consolidat|consol|cross[\s.-]*ref|confidential|w/|with\b|"
    r"\bsee\b|\bmemo\b|\d{5,}", re.I)
_TRAIL_PAREN = re.compile(r"\s*\(([^()]*)\)\s*$")
_DOCKET_TAIL = re.compile(r"\s*;?\s*No\.?\s*\d{5,}.*$")
_BARE_CONF = re.compile(r"[\s,]*\bCONFIDENTIAL\b\s*$", re.I)
_INITIALS = re.compile(r"[A-Za-z]\.[A-Za-z]\.")
_SMUSHED = re.compile(r"\b(In re|In Interest of)\s+[A-Z]{2,}\b")
_FULLWORDS = re.compile(
    r"Interest of|Disciplinary Board|Judicial Conduct|Commission v", re.I)


def clean_caption(s: str) -> str:
    s = s.strip()
    prev = None
    while prev != s:                      # strip stacked trailing annots
        prev = s
        s = _DOCKET_TAIL.sub("", s).strip()
        s = _BARE_CONF.sub("", s).strip()
        m = _TRAIL_PAREN.search(s)
        if m and _ANNOT_META.search(m.group(1)):
            s = s[:m.start()].rstrip()
    # collapse whitespace; drop trailing separators but PRESERVE a final
    # period (it belongs to a terminal initial like 'J.C.S.' or 'et al.')
    s = re.sub(r"\s{2,}", " ", s).strip().rstrip(",; ").strip()
    return s


def fullness(s: str) -> int:
    score = 0
    if _INITIALS.search(s):
        score += 3
    if _FULLWORDS.search(s):
        score += 2
    if " v. " in s or re.search(r"\bv\.?\b", s):
        score += 1
    if _SMUSHED.search(s):
        score -= 2
    if re.search(r"\b[A-Z]{4,}\b", s):    # ALL-CAPS chunk
        score -= 1
    if s != s.upper():                    # has lowercase
        score += 1
    return score


def choose_caption(keep_name: str, drop_name: str) -> str:
    kf, df = fullness(keep_name), fullness(drop_name)
    chosen = keep_name if kf >= df else drop_name
    # apply the ratified probate transform ('In Re Estate of X' ->
    # 'Estate of X', current ND style) then strip metadata annotations
    cleaned = clean_caption(_canonical_name(chosen))
    return cleaned or keep_name.strip()   # never return empty


def norm_docket(d: str | None) -> str | None:
    if not d:
        return None
    if re.fullmatch(r"\d{4}\s*N\.?D\.?\s*\d+", d.strip(), re.I):
        return None
    digits = re.sub(r"\D", "", d)
    if not digits:
        return None
    if len(digits) >= 6 and digits[:2] in ("19", "20") and len(digits) - 2 >= 5:
        return digits[2:]
    return digits


def clean_dup_pairs(conn) -> list[tuple]:
    """Distinct (keep, drop) pairs classified CLEAN_DUP, dedup'd across
    the neutral+N.W.2d rows that name the same pair twice."""
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
        j = _jac(conn, kid, did)
        if j >= 0.85 and not conflict:
            seen.add((kid, did))
            out.append((kid, kn, did, dn, j))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=Path("opinions.db"))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    if args.apply and not args.limit:
        raise SystemExit("--apply requires --limit N (reviewed batch)")
    conn = get_connection(args.db)
    pairs = clean_dup_pairs(conn)

    out = ["action\tkeep\tdrop\tj\tkeep_name\tdrop_name\tsurvivor_caption"]
    applied = 0
    for kid, kn, did, dn, j in pairs:
        # converge: skip if a prior merge in this batch already removed a row
        live = conn.execute("SELECT COUNT(*) FROM opinions WHERE id IN (?,?)",
                            (kid, did)).fetchone()[0]
        if live != 2:
            out.append(f"SKIP_STALE\t{kid}\t{did}\t{j:.3f}\t{kn}\t{dn}\t")
            continue
        if (kid, did) in _DEFER_CAPTION or (did, kid) in _DEFER_CAPTION:
            out.append(f"DEFER_CAPTION\t{kid}\t{did}\t{j:.3f}\t{kn}\t{dn}\t"
                       f"both captions mangled — hand-pick in worklist")
            continue
        canon = choose_caption(kn, dn)
        do = args.apply and applied < args.limit
        merge_pair(conn, kid, did, canon, apply=do, batch=BATCH)
        applied += 1 if do else 0
        out.append(f'{"MERGED" if do else "PENDING"}\t{kid}\t{did}\t'
                   f'{j:.3f}\t{kn}\t{dn}\t{canon}')

    rpt = Path("triage") / f"{BATCH}.tsv"
    rpt.write_text("\n".join(out), encoding="utf-8")
    if args.apply and applied:
        log_provenance(
            conn, operation="section6_defermodern_clean",
            command=f"python triage/merge_defer_modern_clean_2026-05-26.py "
                    f"--apply --limit {args.limit}",
            rows_affected=applied,
            notes=(f"batch {BATCH}; merged {applied} CLEAN_DUP 1997+ "
                   f"double-ingest pairs (j>=0.85, docket-confirmed); "
                   f"survivor caption = fuller style, annotations stripped; "
                   f"NOT changelog-revertible (row deletions) — restore "
                   f"snapshot opinions.db.bak-pre-defermodern-2026-05-26"))
        conn.commit()
    print(f"=== §6 DEFER_MODERN CLEAN_DUP: "
          f"{'APPLIED' if args.apply else 'DRY RUN'} ===")
    print(f"  clean_dup pairs   {len(pairs)}")
    print(f"  applied           {applied}")
    print(f"  report -> {rpt}")
    conn.close()


if __name__ == "__main__":
    main()
