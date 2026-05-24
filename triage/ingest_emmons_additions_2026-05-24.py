"""Ingest the 3 missing Emmons County per curiams + apply the two noted fixes.

Source: bound N.D. Reports vol. 9 (Google scan, filed at
N.D./9/_bound-volume.pdf). The N.W. reporter's cite-based pulls returned only
one opinion per surname per page, so a 2nd McKenzie (p.611), 2nd Mellon (p.613),
and 2nd Thistlewaite (p.614) — confirmed as distinct per-parcel tax-foreclosure
suits by the bound volume (each its own captioned PER CURIAM) — were never
ingested.

These 3 have IDENTICAL disposition text + same caption + same cites as their
siblings (the only real distinguisher is the separate suit / parcel, not stated
in the one-paragraph memo). A `notes` flag marks them do-not-merge so a future
jaccard dedup pass does not collapse them.

Also applies: (a) oid 20496 case_name McLean->McLain (bound volume:
"Calvin B. McLain"); (b) Middlewest Grain N.W. parallel-cite fixes
(2171->472, 20499->473, 2169->474) — DB had lumped them at 173 N.W. 475.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection  # noqa: E402

BATCH = "ingest-emmons-additions-2026-05-24"
SRC = "N.D./9/_bound-volume.pdf"
NOTE = ("Distinct per-parcel tax-foreclosure per curiam; one of multiple "
        "identically-captioned Emmons County v. {d} suits at 9 N.D. {p}, all "
        "decided 1900-11-13 with identical disposition (Emmons Co. v. Thompson, "
        "9 N.D. 598). DO NOT MERGE — separate suits, identical text. "
        "Ingested from bound N.D. Reports vol. 9 p.{p}.")

PER_CURIAM = (
    "PER CURIAM. The controlling questions in this case were involved and "
    "decided in the case of Emmons Co. v. Thompson (decided this term) 9 N.D. "
    "598, 84 N.W. 385. The order appealed from is in all things reversed, and "
    "the District Court is directed to enter an order reversing the same, and "
    "also to enter an order denying the application made herein to vacate said "
    "judgment and tax sale, with costs of both courts to appellant.")


def text_content(full: str, page: int) -> str:
    return (
        f'---\ntitle: "Emmons County v. {full.split("v. ")[1].split(",")[0].title()}"\n'
        f'title_full: "{full}"\n'
        f'court: "North Dakota Supreme Court"\ndate_filed: 1900-11-13\n'
        f'citations:\n  - "9 N.D. {page}"\n  - "84 N.W. 1118"\n'
        f'judges: "Per Curiam"\n'
        f'source: "N.D. Reports vol. 9 (bound volume scan), p. {page}"\n---\n\n'
        f"{full}\n\n(Opinion filed November 13, 1900.)\n\n"
        f"Appeal from District Court, Emmons County; Winchester, J.\n\n"
        f"George M. Register and Cochrane & Corliss, for appellant.\n\n"
        f"H. A. Armstrong, Stevens & Allen, and F. H. Register, for respondents.\n\n"
        f"{PER_CURIAM}\n")


# (case_name, case_name_full, nd_page, defendant-for-note)
NEW = [
    ("Emmons County v. McKenzie", "EMMONS COUNTY v. ALEX. McKENZIE, et al.", 611, "McKenzie"),
    ("Emmons County v. Mellon", "EMMONS COUNTY v. R. B. MELLON, et al.", 613, "Mellon"),
    ("Emmons County v. Thistlewaite", "EMMONS COUNTY v. RICHARD THISTLEWAITE, et al.", 614, "Thistlewaite"),
]
CITE_FIXES = [(2171, "173 N.W. 475", "173 N.W. 472"),
              (20499, "173 N.W. 475", "173 N.W. 473"),
              (2169, "173 N.W. 475", "173 N.W. 474")]


def log(cur, oid, field, old, new, authority):
    cur.execute("INSERT INTO changelog (batch,opinion_id,field,old_value,new_value,authority)"
                " VALUES (?,?,?,?,?,?)", (BATCH, oid, field, old, new, authority))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)
    cur = conn.cursor()

    print("=== NEW opinions ===")
    for cn, full, page, d in NEW:
        print(f"  {cn!r} @ 9 N.D. {page} / 84 N.W. 1118  (full: {full!r})")
    print("=== McLain fix ===")
    cur_name = cur.execute("SELECT case_name FROM opinions WHERE id=20496").fetchone()[0]
    print(f"  20496 {cur_name!r} -> 'Emmons County v. McLain'")
    print("=== Middlewest N.W. cite fixes ===")
    for oid, old, new in CITE_FIXES:
        ex = cur.execute("SELECT 1 FROM citations WHERE opinion_id=? AND citation=?", (oid, old)).fetchone()
        print(f"  oid {oid}: {old} -> {new}  ({'ok' if ex else 'OLD CITE NOT FOUND'})")

    if not args.apply:
        print("\nDry-run. Re-run with --apply.")
        return 0

    new_oids = []
    for cn, full, page, d in NEW:
        cur.execute(
            "INSERT INTO opinions (case_name, case_name_full, date_filed, court, "
            "per_curiam, author, source_reporter, source_path, text_content, notes) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (cn, full, "1900-11-13", "North Dakota Supreme Court", 1, None,
             "ND-image", SRC, text_content(full, page), NOTE.format(d=d, p=page)))
        oid = cur.lastrowid
        new_oids.append(oid)
        cur.execute("INSERT INTO citations (opinion_id,citation,reporter,is_primary) VALUES (?,?,?,1)",
                    (oid, f"9 N.D. {page}", "ND"))
        cur.execute("INSERT INTO citations (opinion_id,citation,reporter,is_primary) VALUES (?,?,?,0)",
                    (oid, "84 N.W. 1118", "NW"))
        cur.execute("INSERT INTO opinion_sources (opinion_id,source_reporter,source_path,is_primary) "
                    "VALUES (?,?,?,1)", (oid, "ND-image", SRC))
        log(cur, oid, "ingest", None, cn,
            f"bound N.D. Reports vol. 9 p.{page} (distinct per-parcel per curiam)")

    cur.execute("UPDATE opinions SET case_name='Emmons County v. McLain' WHERE id=20496")
    log(cur, 20496, "case_name", "Emmons County v. McLean", "Emmons County v. McLain",
        "bound N.D. Reports vol. 9 p.612 (Calvin B. McLain)")

    for oid, old, new in CITE_FIXES:
        cur.execute("UPDATE citations SET citation=? WHERE opinion_id=? AND citation=?", (new, oid, old))
        log(cur, oid, "citation", old, new, "bound N.D. Reports vol. 44 (parallel-cite cross-reference)")

    conn.commit()
    print(f"\nApplied: {len(new_oids)} new opinions (oids {new_oids}), McLain fix, {len(CITE_FIXES)} cite fixes.")
    print(f"  revert: python -m ndcourts_mcp.cleanup revert {BATCH}  (note: new-opinion inserts need manual delete)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
