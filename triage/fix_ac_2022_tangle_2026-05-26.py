"""Untangle the Interest of A.C. 2022 ND 123 / 2022 ND 169 three-row mess.

Ground truth (canonical ndcourts.gov PDF + Westlaw 'Interest of AC.doc'):
  2022 ND 123 = REMANDED, filed 2022-06-08, 975 N.W.2d 567
  2022 ND 169 = AFFIRMED, filed 2022-09-15, 979 N.W.2d 929
(both Interest of A.C., docket 20220081). The refs .md/.pdf files for the
two cites were content-swapped (fixed on disk separately).

DB rows:
  18040  text=123, cite 2022 ND 123 OK, 975 N.W.2d 567 OK -> only the
         date is wrong (2022-09-15 -> 2022-06-08). The real 2022 ND 123.
  18052  text=169 (AFFIRMED Sept 15), 979 N.W.2d 929 -> cite MISLABELED
         2022 ND 123; fix to 2022 ND 169 + repoint ND source to the
         de-swapped 169 file. The real 2022 ND 169.
  19676  text=123 (REMANDED) but cite MISLABELED 2022 ND 169 -> a spurious
         duplicate of 18040. Strip the bad cite + detach its (wrong) ND
         source, then merge 19676 -> 18040.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.db import get_connection, log_change, log_provenance  # noqa
from ndcourts_mcp.ingest import recompute_primary  # noqa
from ndcourts_mcp.merge_opinions import merge_pair  # noqa

B = "fix-ac-2022-tangle-2026-05-26"


def main():
    db = get_connection("opinions.db")

    # 1) 18040 — real 2022 ND 123: fix the date
    old = db.execute("SELECT date_filed FROM opinions WHERE id=18040"
                     ).fetchone()["date_filed"]
    log_change(db, B, 18040, "date_filed", old, "2022-06-08",
               authority="canonical ndcourts.gov PDF: 2022 ND 123 filed "
                         "June 8, 2022 (REMANDED)")
    db.execute("UPDATE opinions SET date_filed='2022-06-08' WHERE id=18040")

    # 2) 18052 — real 2022 ND 169: relabel cite + repoint ND source
    cid = db.execute("SELECT id FROM citations WHERE opinion_id=18052 AND "
                     "citation='2022 ND 123'").fetchone()
    log_change(db, B, 18052, "citation", "2022 ND 123", "2022 ND 169",
               authority="body is the Sept 15 2022 AFFIRMED opinion = "
                         "2022 ND 169 / 979 N.W.2d 929; cite was mislabeled")
    db.execute("UPDATE citations SET citation='2022 ND 169' WHERE id=?",
               (cid["id"],))
    log_change(db, B, 18052, "source_path", "markdown/2022/2022ND123.md",
               "markdown/2022/2022ND169.md",
               authority="repoint to the de-swapped 169 file")
    db.execute("UPDATE opinions SET source_path='markdown/2022/2022ND169.md' "
               "WHERE id=18052")
    db.execute("UPDATE opinion_sources SET source_path="
               "'markdown/2022/2022ND169.md' WHERE opinion_id=18052 AND "
               "source_reporter='ND'")

    # 3) 19676 — spurious dup of 18040: strip bad cite + detach wrong source,
    #    then merge into 18040
    c = db.execute("SELECT id FROM citations WHERE opinion_id=19676 AND "
                   "citation='2022 ND 169'").fetchone()
    if c:
        log_change(db, B, 19676, "citation.remove", "2022 ND 169", None,
                   authority="spurious: 19676 text IS the 2022 ND 123 "
                             "opinion; the real 2022 ND 169 is oid 18052")
        db.execute("DELETE FROM citations WHERE id=?", (c["id"],))
    for s in db.execute("SELECT id,source_path FROM opinion_sources WHERE "
                        "opinion_id=19676").fetchall():
        log_change(db, B, 19676, "source.detach", s["source_path"], None,
                   authority="wrong-file source on a spurious dup row")
        db.execute("DELETE FROM opinion_sources WHERE id=?", (s["id"],))
    merge_pair(db, 18040, 19676, "Interest of A.C.", apply=True, batch=B)

    recompute_primary(db, 18040)
    recompute_primary(db, 18052)
    log_provenance(
        db, operation="fix_ac_2022_tangle",
        command="python triage/fix_ac_2022_tangle_2026-05-26.py",
        rows_affected=3,
        notes=(f"batch {B}; untangled Interest of A.C. 2022 ND 123/169: "
               f"fixed 18040 date, relabeled 18052->2022 ND 169 + repointed "
               f"source, merged spurious dup 19676->18040. Refs .md/.pdf "
               f"de-swapped on disk (canonical PDF from ndcourts.gov). "
               f"snapshot opinions.db.bak-pre-ac-tangle-2026-05-26"))
    db.commit()

    print("=== result ===")
    for oid in (18040, 18052):
        o = db.execute("SELECT id,case_name,date_filed,source_path FROM "
                       "opinions WHERE id=?", (oid,)).fetchone()
        cites = [(r["citation"], r["is_primary"]) for r in db.execute(
            "SELECT citation,is_primary FROM citations WHERE opinion_id=? "
            "ORDER BY is_primary DESC", (oid,))]
        print(f"  {oid}: {o['case_name']!r} {o['date_filed']} "
              f"src={o['source_path']} cites={cites}")
    print(f"  19676 gone: "
          f"{db.execute('SELECT 1 FROM opinions WHERE id=19676').fetchone() is None}")
    db.close()


if __name__ == "__main__":
    main()
