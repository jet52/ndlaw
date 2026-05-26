"""Read-only verification of the §6 DEFER_MODERN LIKELY_DUP tier.

For each distinct LIKELY_DUP pair (0.55 <= jaccard < 0.85, no docket
conflict), confirm the text drift is benign — i.e. the shorter opinion's
word set is essentially contained in the longer one (drift = one source
carries extra syllabus/headnotes/annotations or OCR noise, NOT different
content). A low containment would signal a genuinely distinct opinion
hiding behind a shared docket and needs a PDF read.

Reports, per pair: raw dockets, jaccard, word counts, containment
(|shorter ∩ longer| / |shorter|), and whether a court PDF exists.
"""
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.merge_opinions import _corpus_pairs  # noqa: E402
from ndcourts_mcp.multisource_diff import normalize_words  # noqa: E402

DB = Path("opinions.db")
PDF_DIR = Path("/Users/jerod/refs/nd/opin/pdfs")


def norm_docket(d):
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


def words(t):
    return set(normalize_words(t or ""))


def pdf_for(cite):
    m = re.match(r"(\d{4})\s*ND\s*(\d+)", cite)
    if not m:
        return None
    p = PDF_DIR / m.group(1) / f"{m.group(1)}ND{m.group(2)}.pdf"
    return p if p.exists() else None


def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    seen = set()
    rows = []
    for cite, kid, kn, did, dn in _corpus_pairs(conn)["DEFER_MODERN"]:
        if (kid, did) in seen or (did, kid) in seen:
            continue
        kd = conn.execute("SELECT date_filed,docket_number,text_content "
                          "FROM opinions WHERE id=?", (kid,)).fetchone()
        dd = conn.execute("SELECT date_filed,docket_number,text_content "
                          "FROM opinions WHERE id=?", (did,)).fetchone()
        if kd["date_filed"] != dd["date_filed"]:
            continue
        kdoc, ddoc = norm_docket(kd["docket_number"]), norm_docket(
            dd["docket_number"])
        conflict = kdoc and ddoc and kdoc != ddoc
        wk, wd = words(kd["text_content"]), words(dd["text_content"])
        from ndcourts_mcp.multisource_diff import jaccard, shingles
        j = jaccard(shingles(normalize_words(kd["text_content"] or "")),
                    shingles(normalize_words(dd["text_content"] or "")))
        if not (0.55 <= j < 0.85 and not conflict):
            continue
        seen.add((kid, did))
        short, lng = (wk, wd) if len(wk) <= len(wd) else (wd, wk)
        contain = len(short & lng) / len(short) if short else 0.0
        # neutral cite for PDF lookup
        ncite = next((c[0] for c in conn.execute(
            "SELECT citation FROM citations WHERE opinion_id=? "
            "AND citation LIKE '____ ND %'", (kid,))), cite)
        pdf = pdf_for(ncite)
        rows.append((contain, j, cite, ncite, kid, kn, len(wk),
                     did, dn, len(wd), kd["docket_number"],
                     dd["docket_number"], bool(pdf)))
    conn.close()

    rows.sort()
    print(f"{'contain':>7} {'jac':>5} {'cite':<14} {'pdf':>3}  "
          f"keep/drop word-counts + dockets")
    for (contain, j, cite, ncite, kid, kn, wkn, did, dn, wdn,
         kdoc, ddoc, haspdf) in rows:
        flag = "  <-- LOW CONTAINMENT" if contain < 0.80 else ""
        print(f"{contain:7.3f} {j:5.2f} {ncite:<14} {'Y' if haspdf else '-':>3}  "
              f"k[{kid}]{wkn}w/{kdoc!r}  d[{did}]{wdn}w/{ddoc!r}{flag}")
    print(f"\n{len(rows)} pairs; "
          f"{sum(1 for r in rows if r[0] < 0.80)} below 0.80 containment")


if __name__ == "__main__":
    main()
