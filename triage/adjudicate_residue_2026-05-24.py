"""Phase-2 .doc-body-grounded case-name adjudicator (2026-05-24).

For the substantive case-name residue (party-identity and spelling-direction
calls that string rules can't safely decide), resolve each by reading the
Westlaw .doc BODY — the clean, professionally-edited, non-OCR source — and
seeing how the party surnames are actually spelled there.

Per residue row:
  1. Pairing guard: jaccard(.doc-body shingles, opinion text_content shingles).
     Low jaccard => the .doc may describe a shared-page sibling, not this row
     => DEFER_PAIRING (never auto-applied).
  2. Diff classification on the two captions (DB vs Westlaw):
       SPELLING  same parties, a surname differs by <=1 edit / spacing
       SWAP      a whole surname is replaced (Madderson vs Frish) -> misattribution
       ADDITION  Westlaw only adds tokens (handled mostly by Phase-1 sweeps)
       DB_DROP   Westlaw drops tokens DB has (e.g. a relator/first name)
       COMPLEX   not a clean 2-side caption -> defer
  3. Body resolver (SPELLING/SWAP): count each candidate surname in the .doc
     body (authority) and in text_content (CL OCR, corroboration).
       - .doc body has a clear majority winner (>=2 and >=2x loser):
           CL agrees or is silent  -> HIGH
           CL contradicts          -> MED
       - thin margin / .doc silent -> LOW
  4. Decision: USE_WL or KEEP_DB from the winning spelling; only HIGH is
     eligible for --apply, everything else lands in the audit TSV.

Output: triage/residue-adjudication-2026-05-24.tsv (always).
--apply commits only HIGH-confidence USE_WL renames (KEEP_DB -> state.json).
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sqlite3
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from ndcourts_mcp.review_casenames import (  # noqa: E402
    _doc_to_text, _lev1, _party_tokens, _smart_titlecase,
)
from ndcourts_mcp.ingest_westlaw import _normalize_case_name  # noqa: E402
from ndcourts_mcp.multisource_diff import shingles, jaccard  # noqa: E402

# reuse the Phase-1 annotation stripper / proposer for clean WL captions
_spec = importlib.util.spec_from_file_location(
    "residue_sweep", REPO / "triage" / "sweep_residue_patterns_2026-05-24.py")
_rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rs)
_propose_raw = _rs.propose


def propose(s: str) -> str:
    """Phase-1 proposer plus a fix for a mixed-case possessive the borrowed
    smart_titlecase misses (e.g. "WORKMEN's" -> "Workmen's")."""
    out = _propose_raw(s)
    return re.sub(r"\b([A-Z])([A-Z]{2,})('[a-z])",
                  lambda m: m.group(1) + m.group(2).lower() + m.group(3), out)

CLASSIFIED = REPO / "triage" / "casenames-ambig-review-classified-2026-05-20.tsv"
STATE = REPO / "triage" / "casenames-state.json"
DB = REPO / "opinions.db"
OUT = REPO / "triage" / "residue-adjudication-2026-05-24.tsv"
BATCH = "fix-casenames-adjudicate-2026-05-24"

PAIR_MIN = 0.45


_LIG = {"æ": "ae", "Æ": "ae", "œ": "oe", "Œ": "oe", "’": "'", "‘": "'"}


def fold(s: str) -> str:
    """Fold ligatures to ASCII so "Ætna" == "Aetna" (a ligature is not a
    spelling difference, and the ASCII form is preferred for the corpus)."""
    for k, v in _LIG.items():
        s = s.replace(k, v)
    return s


def words(s: str) -> list[str]:
    s = unicodedata.normalize("NFKD", fold(s)).replace("’", "'").lower()
    return re.findall(r"[a-z']+", s)


def count_surname(tok: str, text: str) -> int:
    """Count whole-word occurrences of a surname (and its de-spaced form)."""
    if not tok:
        return 0
    pat = re.escape(tok)
    return len(re.findall(rf"\b{pat}\b", text, re.I))


def sides(name: str) -> list[str]:
    return _normalize_case_name(fold(name)).split(" v ")


def diff_tokens(db_side: str, wl_side: str):
    """Return (spelling_pairs, db_only, wl_only) for one side."""
    # Drop docket-number artifacts (e.g. "5777" from "No. 5777") that survive
    # caption normalization — they are not party surnames.
    dt = [t for t in _party_tokens(db_side) if not t.isdigit()]
    wt = [t for t in _party_tokens(wl_side) if not t.isdigit()]
    spelling, db_only, wl_used = [], [], set()
    for d in dt:
        exact = next((w for w in wt if w == d), None)
        if exact is not None:
            wl_used.add(exact)
            continue
        near = next((w for w in wt if w not in wl_used and _lev1(d, w)), None)
        if near is not None:
            spelling.append((d, near))
            wl_used.add(near)
        else:
            db_only.append(d)
    wl_only = [w for w in wt if w not in wl_used]
    return spelling, db_only, wl_only


def resolve_spelling(db_tok, wl_tok, doc, tc):
    """Body-grounded spelling/identity resolver. Returns (winner, conf, evid)."""
    d_doc, w_doc = count_surname(db_tok, doc), count_surname(wl_tok, doc)
    d_cl, w_cl = count_surname(db_tok, tc), count_surname(wl_tok, tc)
    evid = f"{db_tok}[doc{d_doc}/cl{d_cl}] vs {wl_tok}[doc{w_doc}/cl{w_cl}]"
    # .doc body is the authority.
    if max(d_doc, w_doc) == 0:
        return None, "LOW", evid  # .doc silent
    winner, loser = (wl_tok, db_tok) if w_doc > d_doc else (db_tok, wl_tok)
    win_doc, lose_doc = (w_doc, d_doc) if winner == wl_tok else (d_doc, w_doc)
    win_cl, lose_cl = (w_cl, d_cl) if winner == wl_tok else (d_cl, w_cl)
    if win_doc == lose_doc:
        return None, "LOW", evid  # tie in .doc
    strong = win_doc >= 2 and win_doc >= 2 * lose_doc
    cl_contradicts = lose_cl > win_cl
    if strong and not cl_contradicts:
        return winner, "HIGH", evid
    return winner, "MED", evid


def adjudicate(row, conn):
    oid, db, wl = row["opinion_id"], row["db_name"], row["wl_raw"]
    wln = row["wl_norm"]  # docket-stripped; use for the PROPOSED name so
    dp = row["doc_path"]  # clean_residue can't eat a "Co." period before "No."
    rec = dict(oid=oid, vol=row["volume"], db=db, wl=wl,
               pair="", kind="", decision="DEFER", conf="", proposed="", evid="")
    try:
        doc = _doc_to_text(dp)
    except Exception:
        rec["kind"] = "DOC_UNREADABLE"
        return rec
    doc = fold(doc)
    tc = fold((conn.execute("SELECT text_content FROM opinions WHERE id=?",
                            (int(oid),)).fetchone() or [""])[0] or "")
    pj = jaccard(shingles(words(doc)), shingles(words(tc)))
    rec["pair"] = f"{pj:.2f}"
    if pj < PAIR_MIN:
        rec["kind"] = "DEFER_PAIRING"
        return rec
    sd, sw = sides(db), sides(wl)
    if len(sd) != 2 or len(sw) != 2:
        rec["kind"] = "COMPLEX"
        return rec

    sp_all, dbo_all, wlo_all = [], [], []
    for i in range(2):
        sp, dbo, wlo = diff_tokens(sd[i], sw[i])
        sp_all += sp
        dbo_all += dbo
        wlo_all += wlo

    if not sp_all and not dbo_all and not wlo_all:
        rec["kind"] = "EQUIV"
        return rec
    if wlo_all and not dbo_all and not sp_all:
        rec["kind"] = "ADDITION"
        rec["proposed"] = propose(wln)
        rec["conf"] = "MED"
        rec["decision"] = "USE_WL"
        return rec
    if dbo_all and not wlo_all and not sp_all:
        rec["kind"] = "DB_DROP"
        return rec  # Westlaw drops a party/relator — defer (often KEEP_DB)

    # SPELLING and/or SWAP: resolve every differing surname pair via the body.
    pairs = list(sp_all)
    rec["kind"] = "SPELLING" if not (dbo_all or wlo_all) else "SWAP"
    if rec["kind"] == "SWAP":
        for d in dbo_all:
            for w in wlo_all:
                pairs.append((d, w))
    winners, confs, evids = [], [], []
    for d, w in pairs:
        win, conf, ev = resolve_spelling(d, w, doc, tc)
        winners.append((d, w, win))
        confs.append(conf)
        evids.append(ev)
    rec["evid"] = " ; ".join(evids)
    rank = {"HIGH": 0, "MED": 1, "LOW": 2}
    rec["conf"] = max(confs, key=lambda c: rank[c]) if confs else "LOW"
    # Single-substitution gate: the body resolver is trustworthy only when ONE
    # DB surname is being changed. A heavily-restructured caption produces many
    # bogus cross-token pairs that spuriously inflate confidence (e.g. dropping
    # "Number One" from a district name), so route multi-token diffs to audit.
    distinct_db = len({d for d, _, win in winners if win is not None})
    if distinct_db > 1:
        rec["kind"] += "*MULTI"
        rec["decision"] = "DEFER"
        return rec
    # USE_WL only if every resolved pair points to the WL token; KEEP_DB if all DB.
    decided = [win for _, _, win in winners if win is not None]
    use_wl = decided and all(win == w for (_, w, win) in winners if win)
    keep_db = decided and all(win == d for (d, _, win) in winners if win)
    if use_wl and rec["conf"] != "LOW":
        rec["decision"], rec["proposed"] = "USE_WL", propose(wln)
    elif keep_db and rec["conf"] != "LOW":
        rec["decision"], rec["proposed"] = "KEEP_DB", db
    else:
        rec["decision"] = "DEFER"
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows = list(csv.DictReader(CLASSIFIED.open(), delimiter="\t"))
    state = json.loads(STATE.read_text())
    kept = state["kept_db"]
    conn = sqlite3.connect(DB)

    recs = []
    for r in rows:
        oid = r["opinion_id"]
        cur = conn.execute("SELECT case_name FROM opinions WHERE id=?", (int(oid),)).fetchone()
        if not cur or oid in kept or cur[0] != r["db_name"]:
            continue  # already resolved/kept/edited
        recs.append(adjudicate(r, conn))

    cols = ["oid", "vol", "kind", "decision", "conf", "pair", "db", "wl", "proposed", "evid"]
    with OUT.open("w") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for rec in recs:
            w.writerow(rec)

    print(f"Adjudicated {len(recs)} pending rows -> {OUT.relative_to(REPO)}")
    print("kind x decision:")
    kd = Counter((r["kind"], r["decision"], r["conf"]) for r in recs)
    for k in sorted(kd):
        print(f"  {k[0]:<14} {k[1]:<10} {k[2]:<5} {kd[k]}")
    auto = [r for r in recs if r["decision"] in ("USE_WL", "KEEP_DB") and r["conf"] == "HIGH"]
    print(f"\nHIGH-confidence auto-eligible: {len(auto)}")

    if args.apply:
        cur = conn.cursor()
        renamed = keeps = 0
        for r in auto:
            if r["decision"] == "USE_WL" and r["proposed"] and r["proposed"] != r["db"]:
                cur.execute("UPDATE opinions SET case_name=? WHERE id=?", (r["proposed"], int(r["oid"])))
                cur.execute("INSERT INTO changelog (batch,opinion_id,field,old_value,new_value)"
                            " VALUES (?,?, 'case_name', ?, ?)", (BATCH, int(r["oid"]), r["db"], r["proposed"]))
                renamed += 1
            elif r["decision"] == "KEEP_DB":
                kept[r["oid"]] = {"db_name": r["db"], "source": BATCH,
                                  "verdict": "KEEP_DB_BODY_SPELLING", "volume": int(r["vol"]), "wl_raw": r["wl"]}
                keeps += 1
        conn.commit()
        STATE.write_text(json.dumps(state, indent=2))
        print(f"Applied {renamed} rename(s); added {keeps} keep_db entr(ies).")
        print(f"  revert: python -m ndcourts_mcp.cleanup revert {BATCH}")
    else:
        print("Dry-run only (TSV written). Re-run with --apply to commit HIGH-confidence rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
