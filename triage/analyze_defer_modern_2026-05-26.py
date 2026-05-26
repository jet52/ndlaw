"""Read-only adjudication analysis for the §6 DEFER_MODERN queue.

For each live DEFER_MODERN pair (two opinions sharing one native
`YYYY ND n` neutral cite, keep.date >= 1997), enrich with:
  - text jaccard (the dup discriminator)
  - docket compatibility (normalized: strip non-digits, drop a leading
    '19'/'20' century prefix the CL ingest adds, ignore 'YYYYNDn' garbage
    dockets that are just the neutral cite restated)
  - same cluster_id?
  - shared primary neutral cite + shared N.W.2d cite?
  - CONFIDENTIAL / juvenile flag (caption-based)
  - source-reporter sets

No writes to the DB. Emits a TSV + a bucket summary to stdout.
"""
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.merge_opinions import _corpus_pairs, _jac  # noqa: E402

DB = Path("opinions.db")

JUV_RE = re.compile(r"\b(interest of|in re [a-z]{1,3}\b|matter of|"
                    r"adoption of|guardianship of|parental rights)",
                    re.I)
CONF_RE = re.compile(r"confidential", re.I)


def norm_docket(d: str | None) -> str | None:
    """Reduce a docket to comparable digits. Returns None for the
    'YYYYNDn' garbage docket (the neutral cite restated as a docket)."""
    if not d:
        return None
    if re.fullmatch(r"\d{4}\s*N\.?D\.?\s*\d+", d.strip(), re.I):
        return None  # garbage: docket == neutral cite
    digits = re.sub(r"\D", "", d)
    if not digits:
        return None
    # CL prepends a 2-digit century to the court's docket (970181 ->
    # 19970181); strip a leading 19/20 when that yields the court form.
    if len(digits) >= 6 and digits[:2] in ("19", "20"):
        stripped = digits[2:]
        # only treat as century-prefixed if the remainder is plausibly
        # a court docket (>= 5 digits, e.g. 970181 / 990162)
        if len(stripped) >= 5:
            return stripped
    return digits


def main() -> None:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    pairs = _corpus_pairs(conn)["DEFER_MODERN"]
    rows = []
    for cite, kid, kn, did, dn in pairs:
        k = conn.execute(
            "SELECT date_filed, docket_number, cluster_id FROM opinions "
            "WHERE id=?", (kid,)).fetchone()
        d = conn.execute(
            "SELECT date_filed, docket_number, cluster_id FROM opinions "
            "WHERE id=?", (did,)).fetchone()
        j = _jac(conn, kid, did)
        kdoc, ddoc = norm_docket(k["docket_number"]), norm_docket(
            d["docket_number"])
        docket_match = (kdoc is not None and kdoc == ddoc)
        docket_conflict = (kdoc is not None and ddoc is not None
                           and kdoc != ddoc)
        same_date = k["date_filed"] == d["date_filed"]
        kcites = {r[0] for r in conn.execute(
            "SELECT citation FROM citations WHERE opinion_id=?", (kid,))}
        dcites = {r[0] for r in conn.execute(
            "SELECT citation FROM citations WHERE opinion_id=?", (did,))}
        shared_cites = kcites & dcites
        conf = bool(CONF_RE.search(kn) or CONF_RE.search(dn))
        juv = bool(JUV_RE.search(kn) or JUV_RE.search(dn))
        rows.append({
            "cite": cite, "keep": kid, "drop": did, "kn": kn, "dn": dn,
            "j": j, "same_date": same_date,
            "docket_match": docket_match, "docket_conflict": docket_conflict,
            "kdoc": k["docket_number"], "ddoc": d["docket_number"],
            "n_shared_cites": len(shared_cites),
            "conf": conf, "juv": juv,
        })
    conn.close()

    # classify
    def bucket(r):
        if not r["same_date"]:
            return "DIFF_DATE"            # scan already filters these out
        if r["docket_conflict"] and r["j"] < 0.55:
            return "DISTINCT_CONTAM"      # different case, contaminated cite
        if r["j"] >= 0.85 and not r["docket_conflict"]:
            return "CLEAN_DUP"            # high text + no docket conflict
        if r["j"] >= 0.55 and not r["docket_conflict"]:
            return "LIKELY_DUP"           # moderate text, no conflict
        if r["docket_conflict"]:
            return "DOCKET_CONFLICT_MIDJAC"
        return "LOWJAC_REVIEW"            # low text, no docket signal

    for r in rows:
        r["bucket"] = bucket(r)

    out = ["bucket\tcite\tkeep\tdrop\tj\tsame_date\tdocket_match\t"
           "docket_conflict\tn_shared_cites\tconf\tjuv\tkdoc\tddoc\t"
           "keep_name\tdrop_name"]
    for r in sorted(rows, key=lambda r: (r["bucket"], -r["j"])):
        out.append(
            f'{r["bucket"]}\t{r["cite"]}\t{r["keep"]}\t{r["drop"]}\t'
            f'{r["j"]:.3f}\t{int(r["same_date"])}\t{int(r["docket_match"])}\t'
            f'{int(r["docket_conflict"])}\t{r["n_shared_cites"]}\t'
            f'{int(r["conf"])}\t{int(r["juv"])}\t{r["kdoc"]!r}\t{r["ddoc"]!r}\t'
            f'{r["kn"]!r}\t{r["dn"]!r}')
    rpt = Path("triage") / "defer-modern-adjudication-2026-05-26.tsv"
    rpt.write_text("\n".join(out), encoding="utf-8")

    from collections import Counter
    c = Counter(r["bucket"] for r in rows)
    print(f"=== DEFER_MODERN adjudication ({len(rows)} pairs) ===")
    for b, n in c.most_common():
        nconf = sum(1 for r in rows if r["bucket"] == b and r["conf"])
        njuv = sum(1 for r in rows if r["bucket"] == b and r["juv"])
        print(f"  {b:24s} {n:4d}   (conf={nconf}, juv={njuv})")
    print(f"  report -> {rpt}")
    print(f"\n  TOTAL conf={sum(r['conf'] for r in rows)}  "
          f"juv={sum(r['juv'] for r in rows)}")


if __name__ == "__main__":
    main()
