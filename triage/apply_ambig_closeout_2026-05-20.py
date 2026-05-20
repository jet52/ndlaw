"""Close out the 6 AMBIG entries from the vol-16-79 mispaired adjudication.

Three actions, each gated by --apply (default dry-run):

  1. ADD source rows for 2 ALREADY_PAIRED_BY_NAME Kerr cases (oids 276, 278).
     Pattern: fix-cairncross-source-2026-05-19.

  2. INGEST 2 corpus-gap opinions (McCue v. Great Northern Ry. Co. at
     19 N.D. 57; Lammadee v. Middlewest Grain Co. at 44 N.D. 247).
     Pattern: emmons-county-vol9-ingest-2026-05-19.

  3. The remaining 2 entries (Bussey -> oid 1189, Nelson@250 -> oid 2169)
     are already correctly paired with primary westlaw sources; no DB
     change. Documented in CHANGELOG-data.md as classifier blind spots.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection  # noqa: E402
from ndcourts_mcp.ingest_westlaw import (  # noqa: E402
    _doc_to_text,
    _parse_westlaw_doc,
)

BATCH = "fix-casenames-vol16-79-ambig-2026-05-20"

# (.doc absolute path, paired opinion_id) — already-existing Kerr siblings.
KERR_SOURCES = [
    ("/Users/jerod/refs/nd/opin/N.D./16/0059-Kerr-v-Herred.doc", 278),
    ("/Users/jerod/refs/nd/opin/N.D./16/0059-Kerr-v-Swanson.doc", 276),
]

# (.doc, case_name, case_name_full, refs-relative source_path) — corpus gaps.
GAPS = [
    {
        "doc": "/Users/jerod/refs/nd/opin/N.D./19/0057-State-ex-rel-McCue-v-Great-Northern-R-Co.doc",
        "case_name": "State ex rel. McCue v. Great Northern Railway Co.",
        "case_name_full": "State ex rel. T. F. McCue, Attorney General v. Great Northern Railway Company",
        "rel_path": "N.D./19/0057-State-ex-rel-McCue-v-Great-Northern-R-Co.doc",
    },
    {
        "doc": "/Users/jerod/refs/nd/opin/N.D./44/0247-Lammadee-v-Middlewest-Grain-Co.doc",
        "case_name": "Lammadee v. Middlewest Grain Co.",
        "case_name_full": "Sarah E. Lammadee v. Middlewest Grain Company and H. T. Hogy",
        "rel_path": "N.D./44/0247-Lammadee-v-Middlewest-Grain-Co.doc",
    },
]


def build_frontmatter(case_name, case_name_full, date_filed, citations) -> str:
    cite_lines = "\n".join(f'  - "{c}"' for c in citations)
    return (
        "---\n"
        f'title: "{case_name}"\n'
        f'title_full: "{case_name_full}"\n'
        f'court: "North Dakota Supreme Court"\n'
        f"date_filed: {date_filed}\n"
        "citations:\n"
        f"{cite_lines}\n"
        'judges: "Per Curiam"\n'
        "---\n\n"
    )


def reporter_for(cite: str) -> str:
    if " N.D. " in cite:
        return "ND"
    if " N.W. " in cite:
        return "NW"
    return "ALR"  # provisional for L.R.A., Am.Ann.Cas. etc.


def add_kerr_sources(conn, apply: bool) -> int:
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    added = 0
    for doc_path, oid in KERR_SOURCES:
        existing = cur.execute(
            "SELECT id FROM opinion_sources WHERE opinion_id = ? AND source_path = ?",
            (oid, doc_path),
        ).fetchone()
        if existing:
            print(f"  oid {oid}: source already present, skipping")
            continue
        text_length = len(_doc_to_text(Path(doc_path)))
        cluster_id = cur.execute(
            "SELECT cluster_id FROM opinions WHERE id = ?", (oid,)
        ).fetchone()["cluster_id"]
        print(f"  ADD source oid {oid:>5}  westlaw is_primary=0  "
              f"path={Path(doc_path).name}")
        if apply:
            cur.execute(
                """INSERT INTO opinion_sources
                       (opinion_id, source_reporter, source_path, cluster_id,
                        text_length, is_primary, added_at)
                       VALUES (?, 'westlaw', ?, ?, ?, 0, ?)""",
                (oid, doc_path, cluster_id, text_length, now),
            )
            cur.execute(
                """INSERT INTO changelog
                       (batch, opinion_id, field, old_value, new_value)
                       VALUES (?, ?, 'opinion_sources.add', NULL, ?)""",
                (BATCH, oid, f"westlaw is_primary=0 {doc_path}"),
            )
            added += 1
    return added


def ingest_gap(conn, gap: dict, apply: bool) -> int | None:
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    doc_path = Path(gap["doc"])
    raw_text = _doc_to_text(doc_path)
    parsed = _parse_westlaw_doc(raw_text) or {}
    cites = list(parsed.get("all_citations") or [])
    if parsed.get("primary_citation"):
        cites.insert(0, parsed["primary_citation"])
    cites = list(dict.fromkeys(cites))
    date_filed = parsed.get("date_filed")
    if not date_filed:
        print(f"  ERROR: no date parsed from {doc_path.name}")
        return None

    # Defensive: only keep canonical ND + NW + LRA cites (skip free-text fragments
    # that the parser sometimes splits like "Am.Ann.Cas. 1912C" / "871").
    keep = []
    import re
    for c in cites:
        if re.match(r"^\d+\s+(N\.D\.|N\.W\.|L\.R\.A\.)", c):
            keep.append(c)
    cites = keep

    text_content = build_frontmatter(
        gap["case_name"], gap["case_name_full"], date_filed, cites,
    )
    # Append the original Westlaw body (everything below the All Citations
    # footer is informational; we keep the body up to but not including
    # "All Citations" to match the emmons batch shape).
    lines = raw_text.splitlines()
    body_start = None
    body_end = len(lines)
    for i, ln in enumerate(lines):
        if ln.strip() == "Attorneys and Law Firms" or ln.strip() == "Opinion":
            body_start = i
            break
    for j in range(len(lines) - 1, -1, -1):
        if lines[j].strip() == "All Citations":
            body_end = j
            break
    if body_start is None:
        body_start = 0
    text_content += "\n".join(lines[body_start:body_end]).strip() + "\n"

    print(f"\n  INGEST {doc_path.name}")
    print(f"    case_name      = {gap['case_name']!r}")
    print(f"    case_name_full = {gap['case_name_full']!r}")
    print(f"    date_filed     = {date_filed}")
    print(f"    citations      = {cites!r}")
    print(f"    text_length    = {len(text_content)}")

    if not apply:
        return None

    cur.execute(
        """INSERT INTO opinions
              (case_name, case_name_full, date_filed, court, per_curiam,
               judges, source_reporter, source_path, text_content)
              VALUES (?, ?, ?, 'North Dakota Supreme Court', 1,
                      'Per Curiam', 'westlaw', ?, ?)""",
        (gap["case_name"], gap["case_name_full"], date_filed,
         gap["rel_path"], text_content),
    )
    new_oid = cur.lastrowid
    print(f"    -> new oid {new_oid}")

    for i, c in enumerate(cites):
        cur.execute(
            "INSERT INTO citations (opinion_id, citation, reporter, is_primary) "
            "VALUES (?, ?, ?, ?)",
            (new_oid, c, reporter_for(c), 1 if i == 0 else 0),
        )

    cur.execute(
        """INSERT INTO opinion_sources
              (opinion_id, source_reporter, source_path, text_length,
               is_primary, added_at)
              VALUES (?, 'westlaw', ?, ?, 1, ?)""",
        (new_oid, gap["rel_path"], len(text_content), now),
    )

    cur.execute(
        """INSERT INTO changelog
              (batch, opinion_id, field, old_value, new_value)
              VALUES (?, ?, 'opinion.insert', NULL, ?)""",
        (BATCH, new_oid,
         f"{gap['case_name']} | {date_filed} | {' | '.join(cites)}"),
    )
    return new_oid


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)

    print("=== Kerr source rows ===")
    kerr_added = add_kerr_sources(conn, args.apply)

    print("\n=== Corpus-gap ingests ===")
    gap_oids = []
    for gap in GAPS:
        new_oid = ingest_gap(conn, gap, args.apply)
        if new_oid:
            gap_oids.append(new_oid)

    if args.apply:
        conn.commit()
        print(f"\nDONE under batch '{BATCH}':")
        print(f"  source rows added: {kerr_added}")
        print(f"  new opinions:      {len(gap_oids)} (oids {gap_oids})")
        print(f"  revert source rows: DELETE FROM opinion_sources WHERE ... (see changelog)")
        print(f"  revert ingests:    DELETE FROM opinions WHERE id IN ({','.join(map(str, gap_oids))})")
    else:
        print(f"\nDry-run. Run with --apply to commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
