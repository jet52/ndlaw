"""Recover the missing 2023 ND 120 (Goetz v. Goetz) + repoint 19722 after the file swap.

Context: the ~/refs markdown+pdf files for 2023 ND 53 and 2023 ND 120 were
content-swapped; the real 2023 ND 120 (2023-07-07) was never ingested. The files
have now been renamed so each matches its content (markdown/2023/2023ND{53,120}
.md/.pdf). This script:
  1. Repoints 19722 (Goetz, 2023 ND 53) source_path/opinion_sources from the old
     misnamed markdown/2023/2023ND120.md -> markdown/2023/2023ND53.md (content
     unchanged; only the pointer was wrong).
  2. Ingests 2023 ND 120 as a new opinion from markdown/2023/2023ND120.md, with
     metadata verified against CourtListener (cluster 9412027) + the opinion text:
     Goetz v. Goetz, 2023-07-07, docket 20220231, author McEvers (Jensen C.J. &
     Tufte joined; Surrogate Judge Nelson dissenting), REVERSED, child custody.
     No N.W.2d parallel is published/known yet -> neutral cite only.

text_citations/cited_by (outbound graph) are NOT built here (jetcite isn't
installed); a later `cite_extract` run will populate them, as for any fresh ingest.

Run with --apply; default dry-run.
"""
from __future__ import annotations
import argparse, sqlite3
from pathlib import Path
from ndcourts_mcp.ingest import _add_citations, _record_source, recompute_primary
from ndcourts_mcp.quality_scan import score_opinion

BATCH = "recover-2023nd120-2026-05-26"
REFS = Path.home() / "refs" / "nd" / "opin"
NEW_MD = REFS / "markdown" / "2023" / "2023ND120.md"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = sqlite3.connect("opinions.db"); conn.row_factory = sqlite3.Row

    # sanity: file now holds 2023 ND 120
    text = NEW_MD.read_text(encoding="utf-8")
    assert "2023 ND 120" in text[:200], "2023ND120.md does not start with 2023 ND 120"
    assert not conn.execute("SELECT 1 FROM citations WHERE citation='2023 ND 120'").fetchone(), \
        "2023 ND 120 already present"

    # --- 1. repoint 19722 to the correctly-named 2023ND53.md ---
    old = "markdown/2023/2023ND120.md"; new = "markdown/2023/2023ND53.md"
    cur = conn.execute("SELECT source_path FROM opinions WHERE id=19722").fetchone()
    print(f"19722 source_path: {cur['source_path']} -> {new}")
    if args.apply:
        conn.execute("INSERT INTO changelog (batch,opinion_id,field,old_value,new_value) "
                     "VALUES (?,19722,'source_path',?,?)", (BATCH, cur["source_path"], new))
        conn.execute("UPDATE opinions SET source_path=? WHERE id=19722", (new,))
        conn.execute("UPDATE opinion_sources SET source_path=? WHERE opinion_id=19722 AND source_path=?",
                     (new, old))

    # --- 2. ingest 2023 ND 120 ---
    print("Ingest 2023 ND 120 (Goetz v. Goetz), docket 20220231, author McEvers")
    if args.apply:
        cur = conn.execute(
            """INSERT INTO opinions
               (cluster_id, case_name, case_name_full, date_filed, docket_number,
                judges, per_curiam, author, absolute_url, source_reporter, source_path, text_content)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (9412027, "Goetz v. Goetz", None, "2023-07-07", "20220231",
             "McEvers, Jensen, Tufte, Nelson", 0, "McEvers", None, "ND",
             "markdown/2023/2023ND120.md", text))
        oid = cur.lastrowid
        _add_citations(conn, oid, ["2023 ND 120"], "ND")
        _record_source(conn, oid, "ND", NEW_MD, REFS, text, is_primary=1,
                        cluster_id=9412027)
        recompute_primary(conn, oid)
        s = score_opinion(text, "ND")
        conn.execute(
            """INSERT OR REPLACE INTO quality_scores
               (opinion_id,ocr_artifacts,garbage_chars,short_line_ratio,has_html,
                para_markers,dupe_cites,overall_score) VALUES (?,?,?,?,?,?,0,?)""",
            (oid, s["ocr_artifacts"], s["garbage_chars"], s["short_line_ratio"],
             s["has_html"], s["para_markers"], s["overall_score"]))
        conn.execute("INSERT INTO changelog (batch,opinion_id,field,old_value,new_value) "
                     "VALUES (?,?,'INGEST',NULL,'Goetz v. Goetz, 2023 ND 120, 2023-07-07')",
                     (BATCH, oid))
        conn.commit()
        print(f"  inserted opinion id={oid}, quality score={s['overall_score']}")
    print("APPLIED" if args.apply else "DRY RUN")
    conn.close()


if __name__ == "__main__":
    main()
