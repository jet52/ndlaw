"""Resolve the White v. Lauder knot (oids 5833 / 5834) — verified 2026-05-25.

Bound N.D. Reports vol 10 prints two distinct companion mandamus per curiams,
both following Gunn v. Lauder (10 N.D. 389, 87 N.W. 999), both at 87 N.W. 1135:
  - 10 N.D. 400 (oid 5834): "Patrick White v. W. S. Lauder", filed Nov. 21, 1901, with
    syllabus "Mandamus to Judge—Disqualification—Failure to Call Other Judge".
  - 10 N.D. 445 (oid 5833): "Patrick White et al. v. W. S. Lauder", filed Nov. 21, 1901.
Two distinct opinions (ruled keep-both 2026-05-25). Two data errors on 5834:
  1. date_filed 1901-10-25 is Willard v. Monarch's date (next case on p.400); the
     bound page + CL text say Nov. 21, 1901.
  2. NW-image source NW/87/996.pdf is Willard's N.W. page; White is at 87 N.W. 1135.
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change  # noqa: E402

BATCH = "fix-white-lauder-2026-05-25"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)

    # 1. date_filed 5834: 1901-10-25 -> 1901-11-21
    cur = conn.execute("SELECT date_filed FROM opinions WHERE id=5834").fetchone()["date_filed"]
    print(f"5834 date_filed: {cur} -> 1901-11-21")
    # 2. NW-image source_path 5834: NW/87/996.pdf -> NW/87/1135.pdf
    src = conn.execute(
        "SELECT source_path FROM opinion_sources WHERE opinion_id=5834 AND source_reporter='NW-image'"
    ).fetchone()
    print(f"5834 NW-image source_path: {src['source_path'] if src else None} -> NW/87/1135.pdf")

    if not args.apply:
        print("\nDRY-RUN. Re-run with --apply.")
        return 0

    if cur == "1901-10-25":
        conn.execute("UPDATE opinions SET date_filed='1901-11-21' WHERE id=5834")
        log_change(conn, BATCH, 5834, "date_filed", "1901-10-25", "1901-11-21",
                   authority="bound 10 N.D. 400 'Opinion filed Nov. 21, 1901'; 10-25 was Willard v. "
                             "Monarch's date (next case on the page), mis-grabbed by CL")
    else:
        print(f"  SKIP date: 5834 is {cur}, not 1901-10-25")

    if src and src["source_path"] != "NW/87/1135.pdf":
        conn.execute(
            "UPDATE opinion_sources SET source_path='NW/87/1135.pdf' "
            "WHERE opinion_id=5834 AND source_reporter='NW-image'")
        log_change(conn, BATCH, 5834, "opinion_source_path_nw_image", src["source_path"], "NW/87/1135.pdf",
                   authority="87 N.W. 1135 is White v. Lauder; NW/87/996.pdf is Willard v. Monarch "
                             "(mis-attached). Both White companions share the 87 N.W. 1135 page.")
    else:
        print("  SKIP NW-image: already 1135 or missing")

    conn.commit()
    print(f"\nApplied; batch {BATCH}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
