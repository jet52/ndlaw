"""Extract citations from opinion text and build citation graph.

Uses jetcite to scan each opinion's text_content, stores all citations
in text_citations, and builds a cited_by reverse index linking ND
opinions to each other. Uses multiprocessing for parallel scanning.

Usage:
    python -m ndcourts_mcp.cite_extract [--db PATH] [--batch-size N] [--limit N] [--workers N]
    python -m ndcourts_mcp.cite_extract --cited-by-only
"""

import argparse
import multiprocessing
import os
import re
import sqlite3
import time
from pathlib import Path

from .db import DEFAULT_DB_PATH, create_schema, get_connection, log_provenance

# Normalize reporter edition spacing: "N.W.2d" <-> "N.W. 2d", "N.W.3d" <-> "N.W. 3d"
_EDITION_RE = re.compile(r'(\.\w\.)\s*(\d[a-z]+)')


def _normalize_cite_key(cite: str) -> str:
    """Normalize citation string for matching between DB and jetcite formats.

    Collapses 'N.W. 2d' and 'N.W.2d' to the same form (no space before edition).
    """
    return _EDITION_RE.sub(r'\1\2', cite)


def build_citation_lookup(conn: sqlite3.Connection) -> dict[str, int]:
    """Build {normalized_citation_string: opinion_id} from the citations table.

    Multiple citation strings may map to the same opinion_id (parallel cites).
    Stores both the raw DB form and a normalized form (edition spacing removed)
    so that jetcite's "N.W. 2d" matches the DB's "N.W.2d".
    """
    rows = conn.execute("SELECT citation, opinion_id FROM citations").fetchall()
    lookup: dict[str, int] = {}
    for row in rows:
        cite = row["citation"]
        oid = row["opinion_id"]
        lookup[cite] = oid
        lookup[_normalize_cite_key(cite)] = oid
    return lookup


# ── Worker function (runs in subprocess) ───────────────────────────

_worker_db_path: Path | None = None


def _init_worker(db_path: Path) -> None:
    """Initialize worker process with DB path."""
    global _worker_db_path
    _worker_db_path = db_path


def _scan_opinion(opinion_id: int) -> tuple[int, list[dict]]:
    """Scan one opinion's text. Returns (opinion_id, list of citation dicts).

    Each worker reads its own opinion text from the DB (read-only)
    to avoid serializing all texts through the multiprocessing pipe.
    """
    import sqlite3
    from jetcite import scan_text

    conn = sqlite3.connect(str(_worker_db_path))
    row = conn.execute("SELECT text_content FROM opinions WHERE id = ?", (opinion_id,)).fetchone()
    conn.close()
    if not row:
        return (opinion_id, [])

    text = row[0]
    citations = scan_text(text, resolve=False)
    if not citations:
        return (opinion_id, [])

    # Compute parallel groups here (pure computation, no DB writes)
    parallel_groups = _assign_parallel_groups(citations)

    results = []
    for cite in citations:
        url = cite.sources[0].url if cite.sources else None
        results.append({
            "normalized": cite.normalized,
            "cite_type": cite.cite_type.value,
            "jurisdiction": cite.jurisdiction,
            "raw_text": cite.raw_text,
            "url": url,
            "parallel_group": parallel_groups.get(cite.normalized),
        })
    return (opinion_id, results)


def _assign_parallel_groups(citations) -> dict[str, int | None]:
    """Assign parallel_group integers to citations that share parallel links."""
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for cite in citations:
        if cite.parallel_cites:
            parent.setdefault(cite.normalized, cite.normalized)
            for pc in cite.parallel_cites:
                parent.setdefault(pc, pc)
                union(cite.normalized, pc)

    if not parent:
        return {c.normalized: None for c in citations}

    root_to_group: dict[str, int] = {}
    next_group = 1
    result: dict[str, int | None] = {}
    for cite in citations:
        n = cite.normalized
        if n in parent:
            root = find(n)
            if root not in root_to_group:
                root_to_group[root] = next_group
                next_group += 1
            result[n] = root_to_group[root]
        else:
            result[n] = None
    return result


# ── Main process: collect results and write to DB ──────────────────


def _store_results(
    conn: sqlite3.Connection,
    opinion_id: int,
    cite_dicts: list[dict],
    citation_lookup: dict[str, int],
    own_cites_map: dict[int, set[str]],
) -> dict[str, int]:
    """Store scan results for one opinion. Returns citation type counts."""
    counts: dict[str, int] = {}
    own_normalized = own_cites_map.get(opinion_id, set())

    for cd in cite_dicts:
        ct = cd["cite_type"]
        counts[ct] = counts.get(ct, 0) + 1

        conn.execute(
            """INSERT OR IGNORE INTO text_citations
               (opinion_id, normalized, cite_type, jurisdiction, raw_text, url, parallel_group)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (opinion_id, cd["normalized"], ct, cd["jurisdiction"],
             cd["raw_text"], cd["url"], cd["parallel_group"]),
        )

        # Build cited_by for case citations
        if ct == "case":
            norm_key = _normalize_cite_key(cd["normalized"])
            cited_opinion_id = citation_lookup.get(cd["normalized"]) or citation_lookup.get(norm_key)
            if cited_opinion_id and cited_opinion_id != opinion_id:
                if norm_key not in own_normalized:
                    conn.execute(
                        """INSERT OR IGNORE INTO cited_by
                           (cited_opinion_id, citing_opinion_id, citation)
                           VALUES (?, ?, ?)""",
                        (cited_opinion_id, opinion_id, cd["normalized"]),
                    )

    conn.execute(
        "INSERT OR IGNORE INTO cite_extract_progress (opinion_id) VALUES (?)",
        (opinion_id,),
    )
    return counts


def rebuild_cited_by(conn: sqlite3.Connection, citation_lookup: dict[str, int]) -> int:
    """Rebuild cited_by table from existing text_citations data."""
    conn.execute("DELETE FROM cited_by")

    rows = conn.execute(
        "SELECT tc.opinion_id, tc.normalized FROM text_citations tc WHERE tc.cite_type = 'case'"
    ).fetchall()

    own_cites: dict[int, set[str]] = {}
    for r in conn.execute("SELECT opinion_id, citation FROM citations").fetchall():
        own_cites.setdefault(r["opinion_id"], set()).add(_normalize_cite_key(r["citation"]))

    inserted = 0
    for row in rows:
        opinion_id = row["opinion_id"]
        normalized = row["normalized"]
        norm_key = _normalize_cite_key(normalized)
        cited_opinion_id = citation_lookup.get(normalized) or citation_lookup.get(norm_key)
        if cited_opinion_id and cited_opinion_id != opinion_id:
            if norm_key not in own_cites.get(opinion_id, set()):
                conn.execute(
                    """INSERT OR IGNORE INTO cited_by
                       (cited_opinion_id, citing_opinion_id, citation)
                       VALUES (?, ?, ?)""",
                    (cited_opinion_id, opinion_id, normalized),
                )
                inserted += 1

    conn.commit()
    return inserted


def process_all(
    db_path: Path = DEFAULT_DB_PATH,
    batch_size: int = 100,
    limit: int | None = None,
    cited_by_only: bool = False,
    workers: int | None = None,
) -> None:
    """Main entry point. Scan opinions and build citation graph."""
    conn = get_connection(db_path)
    create_schema(conn)

    citation_lookup = build_citation_lookup(conn)
    print(f"Citation lookup: {len(citation_lookup)} entries", flush=True)

    if cited_by_only:
        print("Rebuilding cited_by from existing text_citations...")
        count = rebuild_cited_by(conn, citation_lookup)
        print(f"  {count} cross-links created")
        conn.close()
        return

    # Build own-cites map for self-cite detection (normalized keys)
    own_cites_map: dict[int, set[str]] = {}
    for r in conn.execute("SELECT opinion_id, citation FROM citations").fetchall():
        own_cites_map.setdefault(r["opinion_id"], set()).add(_normalize_cite_key(r["citation"]))

    # Get opinions to process, newest first, skipping already-processed
    opinions = conn.execute(
        """SELECT o.id
           FROM opinions o
           LEFT JOIN cite_extract_progress p ON p.opinion_id = o.id
           WHERE p.opinion_id IS NULL
           ORDER BY o.date_filed DESC""",
    ).fetchall()

    total = len(opinions)
    if limit:
        opinions = opinions[:limit]
        total_to_process = limit
    else:
        total_to_process = total

    if total_to_process == 0:
        print("Nothing to process.", flush=True)
        conn.close()
        return

    already_done = conn.execute("SELECT count(*) FROM cite_extract_progress").fetchone()[0]

    if workers is None:
        workers = max(1, (os.cpu_count() or 1) - 2)  # leave 2 cores free
    print(
        f"Opinions to scan: {total_to_process} (of {total} remaining, {already_done} already done)\n"
        f"Workers: {workers}, batch size: {batch_size}",
        flush=True,
    )

    # Pass only opinion IDs — workers read text from DB themselves
    work_ids = [row["id"] for row in opinions]

    total_counts: dict[str, int] = {}
    processed = 0
    batch_start = time.time()
    overall_start = time.time()

    # Process with multiprocessing pool
    with multiprocessing.Pool(
        processes=workers,
        initializer=_init_worker,
        initargs=(db_path,),
    ) as pool:
        for opinion_id, cite_dicts in pool.imap_unordered(_scan_opinion, work_ids, chunksize=4):
            counts = _store_results(conn, opinion_id, cite_dicts, citation_lookup, own_cites_map)
            for k, v in counts.items():
                total_counts[k] = total_counts.get(k, 0) + v
            processed += 1

            # Commit and report at batch boundaries
            if processed % batch_size == 0 or processed == total_to_process:
                conn.commit()
                elapsed = time.time() - batch_start
                batch_count = batch_size if processed % batch_size == 0 else processed % batch_size
                rate = elapsed / batch_count
                batch_num = (processed + batch_size - 1) // batch_size
                total_batches = (total_to_process + batch_size - 1) // batch_size
                overall_rate = (time.time() - overall_start) / processed
                eta_secs = overall_rate * (total_to_process - processed)
                eta_h, eta_m = divmod(int(eta_secs), 3600)
                eta_m //= 60

                total_cites = sum(total_counts.values())
                type_summary = ", ".join(
                    f"{v} {k}" for k, v in sorted(total_counts.items(), key=lambda x: -x[1])
                )
                print(
                    f"[batch {batch_num}/{total_batches}] "
                    f"{processed}/{total_to_process} "
                    f"({rate:.1f}s/op, {1/overall_rate:.1f} op/s) "
                    f"ETA {eta_h}h{eta_m:02d}m — "
                    f"{total_cites} citations ({type_summary})",
                    flush=True,
                )
                batch_start = time.time()

    # Final summary
    tc_count = conn.execute("SELECT count(*) FROM text_citations").fetchone()[0]
    cb_count = conn.execute("SELECT count(*) FROM cited_by").fetchone()[0]
    overall = time.time() - overall_start
    print(
        f"\nDone in {overall/3600:.1f}h. "
        f"{tc_count} text_citations, {cb_count} cited_by links.",
        flush=True,
    )
    log_provenance(conn, "cite_extract", rows_affected=processed,
                   notes=f"{tc_count} text_citations, {cb_count} cited_by")
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract citations from opinion text")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--limit", type=int, default=None, help="Process at most N opinions")
    parser.add_argument("--workers", type=int, default=None, help="Number of worker processes")
    parser.add_argument(
        "--cited-by-only",
        action="store_true",
        help="Skip scanning, just rebuild cited_by from existing text_citations",
    )
    args = parser.parse_args()
    process_all(args.db, args.batch_size, args.limit, args.cited_by_only, args.workers)


if __name__ == "__main__":
    main()
