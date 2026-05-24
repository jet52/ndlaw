"""Fix 4 more CL-metadata-contaminated case_names, from re-adjudicating the
CONFIDENTIAL + REVIEW buckets of scan_casename_contamination after the
"published opinions are public" correction (see CHANGELOG -24b).

Genuine contamination (column = a different case / garbage; fix from the
authoritative frontmatter caption):
  12478  'Mundal v. Meyer Flaten' -> 'State, County of Cass ex rel. L.F.F. v.
         K.D.M.'   (docket 1997ND134 -> 'Civil No. 970030')
  15353  'sather' (junk fragment) -> 'Cruff v. H.K.'   (docket -> 'No. 20090149')
  5380   'State v. Pancoast' -> 'State v. Kent'   (body: State v. Myron R. Kent)
  17030  'WSI v. Questar Energy Services, Inc.' -> 'Disciplinary Board of the
         Supreme Court of the State of North Dakota v. Lee'

case_name_full is already correct on all four; only case_name (and the synthetic
docket on 12478) change. Citations untouched.

LEFT ALONE (verified same-case caption variants — column is a legitimate
"Estate of"/"Adoption of"/"Guardianship of"/"Matter of"/"Trust of" caption with
a matching docket): 13736, 13943, 15147, 15501, 15563, 16991, 17392, 6012
(OCR variant that keeps the relator), 12544, 16484, 16536, 17158, 17381.
COLUMN ALREADY CORRECT (the frontmatter SHORT title was the contaminated field):
15600, 15869, 15931 (truly State v. Johnson / Garg / Gagnon). Those three — plus
17030 — also carry a STRAY SECOND ND-neutral cite (a separate cite-level
contamination cluster) flagged for a future cite-cleanup pass; not touched here.

Modes: --apply (default --dry-run). Revertible via `cleanup revert
fix-casename-contamination-2026-05-24c`.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change  # noqa: E402

BATCH = "fix-casename-contamination-2026-05-24c"
AUTH = ("opinion text frontmatter caption (published; self-consistent with the "
        "in-body caption); column was CL-metadata-contaminated")

TARGETS = {
    12478: "Mundal v. Meyer Flaten",
    15353: "sather",
    5380: "State v. Pancoast",
    17030: "WSI v. Questar Energy Services, Inc.",
}


def _frontmatter(head: str) -> dict[str, str]:
    m = re.match(r"---\s*\n(.*?)\n---", head, re.S)
    if not m:
        return {}
    fm, out = m.group(1), {}
    for key in ("title", "title_full", "docket_number"):
        km = re.search(rf'^{key}:\s*"?(.*?)"?\s*$', fm, re.M)
        if km and km.group(1).strip():
            out[key] = km.group(1).strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)

    plan, n_fields = [], 0
    for oid, expected_old in TARGETS.items():
        r = conn.execute(
            "SELECT case_name, case_name_full, docket_number, "
            "substr(text_content,1,1600) AS head FROM opinions WHERE id=?", (oid,)
        ).fetchone()
        if r is None or r["case_name"] != expected_old:
            print(f"!! oid {oid}: guard failed (case_name={r and r['case_name']!r}, "
                  f"expected {expected_old!r}); SKIPPING")
            continue
        fm = _frontmatter(r["head"])
        if not fm.get("title"):
            print(f"!! oid {oid}: no frontmatter title; SKIPPING")
            continue
        changes = [("case_name", r["case_name"], fm["title"]),
                   ("case_name_full", r["case_name_full"], fm.get("title_full")),
                   ("docket_number", r["docket_number"], fm.get("docket_number"))]
        changes = [(f, old, new) for f, old, new in changes if new and new != old]
        plan.append((oid, changes))
        print(f"oid {oid}:")
        for f, old, new in changes:
            print(f"  {f}: {str(old)[:55]!r} -> {str(new)[:55]!r}")

    print(f"\n{len(plan)}/{len(TARGETS)} ready.")
    if not args.apply:
        print("DRY-RUN. re-run with --apply.")
        return 0

    for oid, changes in plan:
        for field, _old, new in changes:
            conn.execute(f"UPDATE opinions SET {field}=? WHERE id=?", (new, oid))
        for field, old, new in changes:
            log_change(conn, BATCH, oid, field, old, new, authority=AUTH)
        n_fields += len(changes)
    conn.commit()
    print(f"\nApplied {len(plan)} fixes ({n_fields} field changes); batch {BATCH}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
