"""Sweep for CourtListener-metadata contamination and drop stray neutral cites.

Several CL JSON metadata files in ``~/refs/nd/opin/NW{,2d,3d}/`` list
two unrelated neutral ND cites in the same record (the Feldmann-vs-
Pipeline-Petition pattern). When ndcourts-mcp ingests those JSONs, the
DB row picks up the bogus extra cite. The ND-side ingest then matches
the stray cite to a different markdown file and may link it as an
additional source, contaminating the row further (case_name, date,
source_path, archive linkage).

This sweep:

  1. Walks every CL JSON metadata file under NW/, NW2d/, NW3d/.
  2. Flags JSONs whose ``citations`` list contains 2+ neutral ND cites.
  3. For each DB row affected (any row carrying 2+ of the suspect ND
     cites), determines the row's "real" cite from its ``source_path``
     (``markdown/<year>/<year>NDN.md`` → ``<year> ND N``) and drops the
     other ND cite(s) from the citations table as strays.

Subtler kinds of contamination (wrong source_path, wrong text_content,
wrong archive linkage) are NOT corrected here; they need per-case
attention because they involve overwriting opinion content. Two such
cases — Feldmann (oid 16829) and Kitchen/Kleinsmith (oids 15988,
16488) — were already fixed by their dedicated scripts before this
sweep.

After running with ``--apply``, re-run:

  - ``ndcourts_mcp.cite_extract --cited-by-only``
        rebuild cited_by from text_citations (drops cite-based links
        that now point at the wrong owner).
  - ``ndcourts_mcp.fix_archive_pairings --apply``
        re-link any archive rows that became detectable as wrong-paired
        once their stray cite no longer matched.

Usage:
    python -m ndcourts_mcp.fix_cl_metadata_contamination
        [--db PATH] [--refs PATH] [--apply]
        [--batch fix-cl-metadata-contamination-2026-05-04]
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from .db import DEFAULT_DB_PATH, log_provenance

DEFAULT_BATCH = "fix-cl-metadata-contamination-2026-05-04"
ND_NEUTRAL = re.compile(r"^\d{4}\s+ND\s+\d+$")
SOURCE_RE = re.compile(r"markdown/(\d{4})/(\d{4})ND(\d+)\.md")


@dataclass
class Drop:
    opinion_id: int
    case_name: str
    derived_cite: str          # the cite that genuinely belongs to the row
    stray_cite: str            # the cite to remove
    json_path: str             # CL metadata file that introduced the stray
    cite_row_id: int           # citations.id to delete


def find_drops(conn: sqlite3.Connection, refs_dir: Path) -> list[Drop]:
    drops: list[Drop] = []
    seen_oids: set[int] = set()

    for tree in ("NW", "NW2d", "NW3d"):
        for jp in (refs_dir / tree).rglob("*.json"):
            try:
                data = json.loads(jp.read_text(encoding="utf-8"))
            except Exception:
                continue
            cites = data.get("citations") or []
            nd_cites = [c for c in cites if ND_NEUTRAL.match(c)]
            if len(nd_cites) < 2:
                continue

            # Find every DB row that carries 2+ of these ND cites
            candidate_oids: set[int] = set()
            for nc in nd_cites:
                for r in conn.execute(
                    "SELECT opinion_id FROM citations WHERE citation = ?", (nc,)
                ):
                    candidate_oids.add(r["opinion_id"])
            for oid in candidate_oids:
                if oid in seen_oids:
                    continue
                row_cites = {
                    r["citation"]
                    for r in conn.execute(
                        "SELECT citation FROM citations WHERE opinion_id = ?",
                        (oid,),
                    )
                }
                nd_in_row = [nc for nc in nd_cites if nc in row_cites]
                if len(nd_in_row) < 2:
                    continue

                op = conn.execute(
                    "SELECT case_name, source_path FROM opinions WHERE id = ?",
                    (oid,),
                ).fetchone()
                src_match = SOURCE_RE.search(op["source_path"] or "")
                if not src_match:
                    print(f"!! oid {oid}: source_path {op['source_path']} "
                          f"doesn't match expected ND markdown layout, skipping",
                          file=sys.stderr)
                    continue
                derived = f"{src_match.group(1)} ND {int(src_match.group(3))}"
                if derived not in nd_in_row:
                    print(f"!! oid {oid}: derived cite {derived!r} not among "
                          f"row's ND cites {nd_in_row!r} — needs deeper "
                          f"investigation; skipping", file=sys.stderr)
                    continue

                strays = [c for c in nd_in_row if c != derived]
                for stray in strays:
                    cite_row = conn.execute(
                        "SELECT id FROM citations "
                        "WHERE opinion_id = ? AND citation = ?",
                        (oid, stray),
                    ).fetchone()
                    if cite_row is None:
                        continue
                    drops.append(Drop(
                        opinion_id=oid, case_name=op["case_name"],
                        derived_cite=derived, stray_cite=stray,
                        json_path=str(jp.relative_to(refs_dir)),
                        cite_row_id=cite_row["id"],
                    ))
                seen_oids.add(oid)
    return drops


def apply_drops(conn: sqlite3.Connection, drops: list[Drop], batch: str) -> int:
    written = 0
    for d in drops:
        conn.execute("DELETE FROM citations WHERE id = ?", (d.cite_row_id,))
        conn.execute(
            "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
            "VALUES (?, ?, 'citations.stray', ?, NULL)",
            (batch, d.opinion_id,
             f"{d.stray_cite!r} removed (CL metadata contamination at {d.json_path})"),
        )
        written += 1
    return written


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("--refs", type=Path,
                   default=Path.home() / "refs" / "nd" / "opin")
    p.add_argument("--apply", action="store_true",
                   help="Write changes (default is dry-run)")
    p.add_argument("--batch", default=DEFAULT_BATCH)
    args = p.parse_args()

    conn = sqlite3.connect(str(args.db))
    conn.row_factory = sqlite3.Row

    print("Scanning CL JSON metadata for multi-neutral-cite contamination…")
    drops = find_drops(conn, args.refs)
    print(f"Stray cites to remove: {len(drops)} "
          f"(across {len({d.opinion_id for d in drops})} rows)")
    print()

    by_oid: dict[int, list[Drop]] = {}
    for d in drops:
        by_oid.setdefault(d.opinion_id, []).append(d)
    for oid, ds in by_oid.items():
        print(f"  oid {oid}  {ds[0].case_name[:40]!r}  derived={ds[0].derived_cite}")
        for d in ds:
            print(f"     drop {d.stray_cite!r}  (from {d.json_path})")

    if not args.apply:
        print("\n(dry-run; pass --apply to write changes)")
        return

    print(f"\nApplying… batch={args.batch}")
    try:
        written = apply_drops(conn, drops, args.batch)
        log_provenance(
            conn,
            operation="fix_cl_metadata_contamination",
            command=" ".join(sys.argv),
            rows_affected=written,
            notes=f"batch={args.batch}; "
                  f"strays_dropped={len(drops)}, "
                  f"rows_touched={len({d.opinion_id for d in drops})}",
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    print(f"Done. {written} changelog rows written.")
    print()
    print("Next steps:")
    print("  ndcourts_mcp.cite_extract --cited-by-only       # rebuild cited_by")
    print("  ndcourts_mcp.fix_archive_pairings --apply       # re-link wrong archives")


if __name__ == "__main__":
    main()
