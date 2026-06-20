"""One-off: the 20 needs-review spots held back by `fix_cite_spacing`.

Each was PDF/context-verified individually (see CHANGELOG-data.md batch
`cite-spacing-review-2026-06-20`). Three kinds:

  ndcc  — a slip-opinion PAGE NUMBER was injected into a section number that
          straddled a page break; the PDF sentence has no such digit. We
          reconstruct the true cite (dropping the page digit).
  ndac  — simple de-space to the court's predominant print form.
  range — a multi-section range; per the court's convention we keep a space
          before the range hyphen so the first cite stays a complete 3-part
          section (not mistakable for a 4-part N.D.A.C. cite).
  hist  — 1943 N.D. Revised Code (the NDCC's predecessor — ND primary law; no
          corpus yet) / out-of-state / municipal. De-space to the true form;
          won't enter the ND citation graph.

11715 (`27-20-30 -32`) is intentionally NOT here: it is a pre-1997 opinion with
no PDF and already carries the range space the convention calls for.

Every pattern REQUIRES internal whitespace, so it matches only the mangled
occurrence and never a clean copy of the same cite elsewhere in the opinion.
Dry-run by default; --apply writes + logs changelog + re-extracts.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.db import get_connection, log_change  # noqa: E402

BATCH = "cite-spacing-review-2026-06-20"

# (oid, pattern, replacement, expected_count, kind, basis)
FIXES = [
    # --- N.D.C.C. page-break: drop the injected slip page number ---
    (16049, r"59-\s+3\s+12-15",       "59-12-15",     1, "ndcc", "2013 ND 85 PDF: § 59-12-15"),
    (16230, r"25-03\.3-\s+1\s+01",    "25-03.3-01",   1, "ndcc", "2014 ND 31 PDF: § 25-03.3-01"),
    (16672, r"32-\s+9\s+03\.2-02",    "32-03.2-02",   1, "ndcc", "2016 ND 45 PDF: § 32-03.2-02"),
    (16784, r"28-34-\s+1\s+01",       "28-34-01",     1, "ndcc", "2016 ND 175 PDF: § 28-34-01"),
    (17747, r"34-\s+6\s+03-01",       "34-03-01",     1, "ndcc", "2021 ND 2 PDF: § 34-03-01"),
    (17898, r"19-\s+4\s+03\.4-01",    "19-03.4-01",   1, "ndcc", "2021 ND 200 PDF: § 19-03.4-01"),
    (18109, r"14-02\.4-\s+2\s+02",    "14-02.4-02",   1, "ndcc", "2022 ND 222 PDF: § 14-02.4-02"),
    (18192, r"65-01-\s+5\s+02",       "65-01-02",     1, "ndcc", "2023 ND 91 PDF: § 65-01-02"),
    # --- N.D.A.C.: de-space to the court's print form ---
    (19426, r"33-15-07-\s+2",         "33-15-07-2",   1, "ndac", "2019 ND 280 PDF: § 33-15-07-2(1)"),
    # --- range: keep the space before the range hyphen ---
    (17642, r"28-\s+32-42-49",        "28-32-42 -49", 1, "range", "2020 ND 93 PDF: §§ 28-32-42-49 (range)"),
    # --- historical ND (1943 Revised Code) ---
    (16462, r"47-\s+1901",            "47-1901",      1, "hist", "2015 ND 94: N.D. Rev. Code of 1943 § 47-1901"),
    # --- out-of-state / municipal ---
    (17539, r"59\s+-6a201",           "59-6a201",     1, "hist", "2019 ND 196: Kan. Stat. Ann. § 59-6a201"),
    (18998, r"10-\s+0601",            "10-0601",      1, "hist", "2013 ND 96: Fargo Municipal Code § 10-0601"),
    (19841, r"2-\s+117",              "2-117",        1, "hist", "2024 ND 10: U.P.C. § 2-117"),
    (19841, r"2-\s+115",              "2-115",        1, "hist", "2024 ND 10: U.P.C. § 2-115"),
    (19912, r"13-\s+3101",            "13-3101",      1, "hist", "2024 ND 164: Ariz. Rev. Stat. Ann. § 13-3101"),
    (19992, r"20-\s+0403",            "20-0403",      3, "hist", "2024 ND 236: Fargo Municipal Code § 20-0403 (x3)"),
    (20075, r"19-\s+4902",            "19-4902",      1, "hist", "2024 ND 99: Idaho Code § 19-4902"),
    (20117, r"25-\s+1509\.2",         "25-1509.2",    1, "hist", "2025 ND 136: Fargo Municipal Code § 25-1509.2"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--db", default="opinions.db")
    args = ap.parse_args()

    conn = get_connection(Path(args.db))
    conn.row_factory = sqlite3.Row
    touched = set()
    ok = True
    for oid, pat, repl, n_exp, kind, basis in FIXES:
        text = conn.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        new, n = re.subn(pat, repl, text)
        m = re.search(pat, text)
        ctx = ""
        if m:
            i = m.start()
            ctx = re.sub(r"\s+", " ", text[i - 18:m.end() + 12]).strip()
        flag = "" if n == n_exp else f"  ⚠ expected {n_exp} got {n}"
        if n != n_exp:
            ok = False
        print(f"[{kind:5}] oid {oid}  /{pat}/ → {repl!r}  (n={n}){flag}")
        if ctx:
            print(f"          …{ctx}…")
        if args.apply and n == n_exp:
            conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            log_change(conn, BATCH, oid, "text_content.cite_spacing_review",
                       (m.group(0) if m else pat), repl, authority=basis)
            touched.add(oid)

    if args.apply:
        if not ok:
            conn.rollback()
            print("\nABORTED: a pattern did not match its expected count. No changes written.")
            return
        conn.commit()
        print(f"\nAPPLIED {len(FIXES)} fixes across {len(touched)} opinions.")
        # re-extract the graph-eligible (ndcc/ndac/range) opinions
        graph_oids = sorted({oid for oid, *_rest in FIXES})
        qm = ",".join("?" * len(graph_oids))
        conn.execute(f"DELETE FROM text_citations WHERE opinion_id IN ({qm})", graph_oids)
        conn.execute(f"DELETE FROM cited_by WHERE citing_opinion_id IN ({qm})", graph_oids)
        conn.execute(f"DELETE FROM cite_extract_progress WHERE opinion_id IN ({qm})", graph_oids)
        conn.commit()
        conn.close()
        print("Cleared graph rows; run: python -m ndcourts_mcp.cite_extract  then  --cited-by-only")
    else:
        print(f"\nDRY-RUN. {'all patterns matched' if ok else 'MISMATCHES ABOVE'}. Re-run with --apply.")
        conn.close()


if __name__ == "__main__":
    main()
