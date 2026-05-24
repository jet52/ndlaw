"""Fix CL-metadata-contaminated case_name / case_name_full / docket_number on
13 vetted 1997-era opinions (the Longtine/Herrick class).

Each row's case_name COLUMN held a COMPLETELY DIFFERENT real case, and its
docket_number was a synthesized `1997NDnnn` (derived from the neutral cite, not
a real docket). The opinion's own text_content frontmatter — title / title_full
/ docket_number, matching the in-body caption — is the authoritative source.
The parallel citations are CORRECT (they belong to the real case in the text)
and are NOT touched.

Each oid is guarded on its expected (wrong) current case_name. New values are
read from the row's own frontmatter at apply time. Vetted by reading every body
caption (scan_casename_contamination_2026-05-24.py + manual verification);
excluded false positives: 12451 (juvenile L.D.C. — would de-anonymize), 12463
(Heustis OCR, same case), 12476 (column already correct), 13804/15073/15796/
15844 (estate captions, same case), 14223 (NDSU, same case).

Modes: --apply (default --dry-run). Revertible via `cleanup revert
fix-casename-contamination-2026-05-24`.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change  # noqa: E402

BATCH = "fix-casename-contamination-2026-05-24"
AUTH = ("opinion text frontmatter caption (self-consistent with the in-body "
        "caption; authoritative); column was CL-metadata-contaminated with a "
        "different case's name + a synthesized 1997NDnnn docket")

# oid -> expected current (wrong) case_name guard.
TARGETS = {
    12346: "State v. Ertelt",
    12388: "Wishnatsky v. Huey",
    12389: "Orgaard v. Orgaard",
    12392: "Ingalls v. Paul Revere Life Insurance Group",
    12397: "Traynor v. Leclerc",
    12398: "In the Matter of the Estate of Ruben J. Peterson, Deceased",
    12403: "City of Williston v. Hegstad",
    12415: ("Joseph D. Moch, Personal Representative of the Estate of Joseph J. "
            "Moch v. Patrick D. Moch, Lillian M. Moch"),
    12418: "Disciplinary Board v. Leier",
    12438: "Symington v. Walle Mutual Insurance Co.",
    12486: "McCabe v. North Dakota Workers Compensation Bureau",
    12500: "Longtine v. Yeado",
    12520: "State v. Osier",
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

    plan = []
    for oid, expected_old in TARGETS.items():
        r = conn.execute(
            "SELECT case_name, case_name_full, docket_number, "
            "substr(text_content,1,1600) AS head FROM opinions WHERE id=?", (oid,)
        ).fetchone()
        if r is None:
            print(f"!! oid {oid}: row missing"); return 1
        if r["case_name"] != expected_old:
            print(f"!! oid {oid}: guard failed — case_name is {r['case_name']!r}, "
                  f"expected {expected_old!r}; SKIPPING")
            continue
        fm = _frontmatter(r["head"])
        if not fm.get("title") or not fm.get("title_full"):
            print(f"!! oid {oid}: missing frontmatter title/title_full; SKIPPING")
            continue
        plan.append((oid, r, fm))
        print(f"oid {oid}:")
        print(f"  case_name      {r['case_name']!r} -> {fm['title']!r}")
        print(f"  case_name_full {str(r['case_name_full'])[:55]!r} -> {fm['title_full'][:55]!r}")
        print(f"  docket_number  {r['docket_number']!r} -> {fm.get('docket_number')!r}")

    print(f"\n{len(plan)}/{len(TARGETS)} ready.")
    if not args.apply:
        print("DRY-RUN. re-run with --apply.")
        return 0

    n_fields = 0
    for oid, r, fm in plan:
        changes = [("case_name", r["case_name"], fm["title"]),
                   ("case_name_full", r["case_name_full"], fm["title_full"]),
                   ("docket_number", r["docket_number"], fm.get("docket_number"))]
        changes = [(f, old, new) for f, old, new in changes if new and new != old]
        for field, _old, new in changes:
            conn.execute(f"UPDATE opinions SET {field}=? WHERE id=?", (new, oid))
        for field, old, new in changes:
            log_change(conn, BATCH, oid, field, old, new, authority=AUTH)
        n_fields += len(changes)
    conn.commit()
    print(f"\nApplied {len(plan)} contamination fixes ({n_fields} field changes); "
          f"batch {BATCH}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
