"""Merge the 74 N.D. 242 CL double-ingest pair (vol 74 §10).

Textbook §6 CourtListener double-ingest, confirmed against the bound
N.D. Reports vol 74 pp. 242-243 (user-supplied PDF):

  74 N.D. 242 = a SINGLE opinion — *In re Adams* (File No. 6966),
  Burr, J.; Christianson Ch. J., Nuessle, Burke, Morris JJ. concur;
  21 N.W.2d 351; filed 1945-08-08. (The case ending atop p. 242 is
  the separate *In re Hanson*, 74 N.D. 224.)

  keep = 7180  matter caption "In re Adams", low cluster_id 3933583,
               correct per-opinion author Burr, NW2d/21/351_2.md
  drop = 7179  parties caption "Northern Pacific Railway Co. v.
               McDonald", high cluster_id 6852041, CL-mis-defaulted
               author "Burke" (its OWN body text reads "BURR, Judge.");
               carries the westlaw .doc + NW2d/21/351.md sources

Both 0 inbound cited_by; tie broken by lower cluster_id -> keep 7180.
This was the lone genuinely-open pair in the 147 legacy
duplicate_candidates (dc id 1359).

merge_pair picks the fuller panel from drop ("Burke, Burr, Christxanson,
Morris, Nuessle"); the survivor judges typo Christxanson -> Christianson
is fixed below from the bound volume.

Snapshot: opinions.db.bak-pre-vol74-adams-merge-2026-05-26.
Row deletion NOT changelog-revertible -> revert via snapshot restore.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from ndcourts_mcp.merge_opinions import merge_pair

BATCH = "section6-vol74-adams-2026-05-26"
KEEP, DROP, CANON = 7180, 7179, "In re Adams"
JUDGES_FIX = ("Burke, Burr, Christxanson, Morris, Nuessle",
              "Burke, Burr, Christianson, Morris, Nuessle")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")
    plan = merge_pair(conn, KEEP, DROP, CANON, apply=args.apply, batch=BATCH)
    print(f"  merge {DROP} -> {KEEP}")
    for k in ("name", "judges", "author"):
        print(f"    {k}: {plan[k]}")

    old, new = JUDGES_FIX
    cur = conn.execute("SELECT judges FROM opinions WHERE id=?", (KEEP,)).fetchone()
    print(f"  judges typo-fix on survivor {KEEP}: {cur['judges']!r} (expect {old!r}) -> {new!r}")
    if args.apply:
        if cur["judges"] != old:
            raise SystemExit(f"judges precondition failed: got {cur['judges']!r}, expected {old!r}")
        log_change(conn, BATCH, KEEP, "judges", old, new,
                   authority="bound N.D. Reports vol 74 p.243: OCR typo "
                             "Christxanson -> Christianson")
        conn.execute("UPDATE opinions SET judges=? WHERE id=?", (new, KEEP))
        log_provenance(
            conn, operation="section6_vol74_adams_merge",
            command="python -m triage.merge_vol74_adams_2026-05-26 --apply",
            rows_affected=1,
            notes=(f"batch {BATCH}; merged 74 N.D. 242 CL double-ingest "
                   f"(drop 7179 -> keep 7180 'In re Adams', Burr J.), confirmed "
                   f"one-opinion against bound vol 74 pp.242-243; judges typo "
                   f"Christxanson->Christianson fixed. Snapshot "
                   f"opinions.db.bak-pre-vol74-adams-merge-2026-05-26; row "
                   f"deletion not changelog-revertible."))
        conn.commit()
        print("  committed.")
    conn.close()


if __name__ == "__main__":
    main()
