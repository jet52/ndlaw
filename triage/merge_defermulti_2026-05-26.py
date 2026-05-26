"""§6 DEFER_MULTI residual: the 3 verified CL double-ingest dups among the
9 post-1997 shared-N.W.2d-page clusters (612/638/709/711/719/742/756/766/777).

Live-DB verification 2026-05-26 (head/tail text read, same docket per pair):
  * 612 N.W.2d 278  -> already resolved (dup merged; 2000 ND 126 + 2000 ND 127 distinct)
  * 766 N.W.2d 437  -> already resolved (dup merged; 2009 ND 91 + 2009 ND 104 distinct)
  * 709/711/719/742/756 -> NOT dups: distinct opinions sharing a summary-
                            disposition N.W.2d page; their issue is the missing
                            neutral cite (§6 "120 no-neutral-cite" item), not a merge.
  * 638 N.W.2d 45   -> DUP: 13503 (markdown 2002ND7, decided 2002-01-15, ¶-marked)
                        == 13504 (CL "2002 WL 49271"; date_filed 2002-07-25 is a CL
                        artifact — its own body says "January 15, 2002"). docket 20010314.
  * 777 N.W.2d 62   -> DUP: 15331 (markdown 2010ND8, 2010-01-12) == 15333 (CL
                        "2010 WL 114285"; date_filed 2010-08-25 is a CL artifact —
                        body says "January 12, 2010"). docket 20090135.
  * 2005 ND 75      -> DUP (the deferred Fire & Tornado pair): 14223 (markdown
                        2005ND75) == 14224 (CL, "April 6, 2005"). docket 20040228.
                        Both captions were mangled; canonical from CL cluster
                        8279538 / West.

Keep = the ndcourts.gov markdown row in every case (authoritative ¶-marked text;
merge_pair leaves text_content UNTOUCHED, so the survivor must be the good-text row).
The CL rows carry the inbound cited_by; merge_pair re-points all references.

14223's judges field is analyzer garbage ("Effective, ... Place, ... When") — the
merge keeps it (more tokens), so we overwrite it post-merge with the participating
panel (VandeWalle C.J., Sandstrom J. (auth), Maring J., Jorgensen D.J. for Kapsner
(disqualified); Neumann resigned, did not participate).

Snapshot taken externally: opinions.db.bak-pre-defermulti-2026-05-26.
Row deletions are NOT changelog-revertible — revert via snapshot restore.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from ndcourts_mcp.merge_opinions import merge_pair

BATCH = "section6-defermulti-2026-05-26"

# (keep, drop, canonical_name)
PAIRS = [
    (13503, 13504, "Interest of J.S."),
    (15331, 15333, "Matter of Hanenberg"),
    (14223, 14224,
     "State ex rel. State Fire & Tornado Fund of the North Dakota "
     "Insurance Department v. North Dakota State University"),
]

# survivor 14223 judges cleanup (participating panel, body-confirmed)
JUDGES_FIX = (14223, "Jorgensen, Maring, Sandstrom, VandeWalle")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")
    for keep, drop, canon in PAIRS:
        plan = merge_pair(conn, keep, drop, canon, apply=args.apply, batch=BATCH)
        print(f"  merge {drop} -> {keep}")
        print(f"    name:   {plan['name']}")
        print(f"    judges: {plan['judges']}")
        print(f"    author: {plan['author']}")

    kid, new_judges = JUDGES_FIX
    old = conn.execute("SELECT judges FROM opinions WHERE id=?",
                       (kid,)).fetchone()["judges"]
    print(f"  judges-fix {kid}: {old!r} -> {new_judges!r}")
    if args.apply:
        log_change(conn, BATCH, kid, "judges", old, new_judges,
                   authority="participating panel per opinion body "
                             "(Neumann resigned/did not participate; "
                             "Kapsner disqualified, Jorgensen D.J. sat)")
        conn.execute("UPDATE opinions SET judges=? WHERE id=?",
                     (new_judges, kid))
        log_provenance(
            conn, operation="section6_defermulti_merge",
            command="python -m triage.merge_defermulti_2026-05-26 --apply",
            rows_affected=len(PAIRS),
            notes=(f"batch {BATCH}; merged 3 verified CL double-ingest dups "
                   f"(638 N.W.2d 45 13504->13503; 777 N.W.2d 62 15333->15331; "
                   f"2005 ND 75 14224->14223) + 14223 judges cleanup. "
                   f"Snapshot opinions.db.bak-pre-defermulti-2026-05-26; "
                   f"row deletions not changelog-revertible."))
        conn.commit()
        print("  committed.")
    conn.close()


if __name__ == "__main__":
    main()
