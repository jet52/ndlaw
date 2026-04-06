"""Extract citations from opinion text and build citation graph.

Uses jetcite to scan each opinion's text_content, stores all citations
in text_citations, and builds a cited_by reverse index linking ND
opinions to each other.

Usage:
    python -m ndcourts_mcp.cite_extract [--db PATH] [--batch-size N] [--limit N]
    python -m ndcourts_mcp.cite_extract --cited-by-only
"""

import argparse
import sqlite3
import time
from pathlib import Path

try:
    from jetcite import Citation, CitationType, scan_text
except ImportError:
    raise ImportError(
        "jetcite is required for citation extraction. "
        "Install with: pip install -e /Users/jerod/code/jetcite"
    )

from .db import DEFAULT_DB_PATH, create_schema, get_connection

import re

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


def assign_parallel_groups(citations: list[Citation]) -> dict[str, int | None]:
    """Assign parallel_group integers to citations that share parallel links.

    Uses union-find to cluster citations connected via parallel_cites.
    Returns {normalized: group_int_or_None}.
    """
    # Build adjacency from parallel_cites
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

    # Assign group numbers to clusters
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


def extract_and_store(
    conn: sqlite3.Connection,
    opinion_id: int,
    text: str,
    citation_lookup: dict[str, int],
) -> dict[str, int]:
    """Scan one opinion and store results. Returns citation type counts."""
    citations = scan_text(text, resolve=False)
    if not citations:
        return {}

    parallel_groups = assign_parallel_groups(citations)
    counts: dict[str, int] = {}

    # Get this opinion's own citations so we can detect self-cites
    own_cite_rows = conn.execute(
        "SELECT citation FROM citations WHERE opinion_id = ?", (opinion_id,)
    ).fetchall()
    own_cites = {r["citation"] for r in own_cite_rows}
    own_cites_normalized = {_normalize_cite_key(c) for c in own_cites}

    for cite in citations:
        ct = cite.cite_type.value
        counts[ct] = counts.get(ct, 0) + 1

        # Pick the first URL from sources
        url = cite.sources[0].url if cite.sources else None

        conn.execute(
            """INSERT OR IGNORE INTO text_citations
               (opinion_id, normalized, cite_type, jurisdiction, raw_text, url, parallel_group)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                opinion_id,
                cite.normalized,
                ct,
                cite.jurisdiction,
                cite.raw_text,
                url,
                parallel_groups.get(cite.normalized),
            ),
        )

        # Build cited_by for case citations that resolve to an opinion in our DB
        if cite.cite_type == CitationType.CASE:
            norm_key = _normalize_cite_key(cite.normalized)
            cited_opinion_id = citation_lookup.get(cite.normalized) or citation_lookup.get(norm_key)
            if cited_opinion_id and cited_opinion_id != opinion_id:
                # Skip if this is just a parallel cite for the citing opinion itself
                if norm_key not in own_cites_normalized:
                    conn.execute(
                        """INSERT OR IGNORE INTO cited_by
                           (cited_opinion_id, citing_opinion_id, citation)
                           VALUES (?, ?, ?)""",
                        (cited_opinion_id, opinion_id, cite.normalized),
                    )

    return counts


def rebuild_cited_by(conn: sqlite3.Connection, citation_lookup: dict[str, int]) -> int:
    """Rebuild cited_by table from existing text_citations data.

    Returns count of rows inserted.
    """
    conn.execute("DELETE FROM cited_by")

    rows = conn.execute(
        """SELECT tc.opinion_id, tc.normalized
           FROM text_citations tc
           WHERE tc.cite_type = 'case'"""
    ).fetchall()

    # Build set of own citations per opinion for self-cite detection (normalized keys)
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
                try:
                    conn.execute(
                        """INSERT OR IGNORE INTO cited_by
                           (cited_opinion_id, citing_opinion_id, citation)
                           VALUES (?, ?, ?)""",
                        (cited_opinion_id, opinion_id, normalized),
                    )
                    inserted += 1
                except sqlite3.IntegrityError:
                    pass  # UNIQUE constraint — already linked via a parallel cite

    conn.commit()
    return inserted


def process_all(
    db_path: Path = DEFAULT_DB_PATH,
    batch_size: int = 100,
    limit: int | None = None,
    cited_by_only: bool = False,
) -> None:
    """Main entry point. Scan opinions and build citation graph."""
    conn = get_connection(db_path)
    create_schema(conn)

    citation_lookup = build_citation_lookup(conn)
    print(f"Citation lookup: {len(citation_lookup)} entries")

    if cited_by_only:
        print("Rebuilding cited_by from existing text_citations...")
        count = rebuild_cited_by(conn, citation_lookup)
        print(f"  {count} cross-links created")
        conn.close()
        return

    # Get opinions to process, newest first, skipping already-processed
    opinions = conn.execute(
        """SELECT o.id, o.text_content
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

    already_done = conn.execute("SELECT count(*) FROM cite_extract_progress").fetchone()[0]
    print(f"Opinions to scan: {total_to_process} (of {total} remaining, {already_done} already done)")

    total_counts: dict[str, int] = {}
    processed = 0
    batch_start = time.time()

    for i, row in enumerate(opinions):
        counts = extract_and_store(conn, row["id"], row["text_content"], citation_lookup)
        conn.execute(
            "INSERT OR IGNORE INTO cite_extract_progress (opinion_id) VALUES (?)",
            (row["id"],),
        )

        for k, v in counts.items():
            total_counts[k] = total_counts.get(k, 0) + v
        processed += 1

        # Commit and report at batch boundaries
        if processed % batch_size == 0 or processed == total_to_process:
            conn.commit()
            elapsed = time.time() - batch_start
            rate = elapsed / batch_size if processed % batch_size == 0 else elapsed / (processed % batch_size)
            batch_num = (processed + batch_size - 1) // batch_size
            total_batches = (total_to_process + batch_size - 1) // batch_size

            total_cites = sum(total_counts.values())
            type_summary = ", ".join(f"{v} {k}" for k, v in sorted(total_counts.items(), key=lambda x: -x[1]))
            print(
                f"[batch {batch_num}/{total_batches}] "
                f"{processed}/{total_to_process} opinions "
                f"({rate:.1f}s/opinion) — "
                f"{total_cites} citations ({type_summary})"
            )
            batch_start = time.time()

    # Final summary
    tc_count = conn.execute("SELECT count(*) FROM text_citations").fetchone()[0]
    cb_count = conn.execute("SELECT count(*) FROM cited_by").fetchone()[0]
    print(f"\nDone. {tc_count} text_citations, {cb_count} cited_by links.")
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract citations from opinion text")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--limit", type=int, default=None, help="Process at most N opinions")
    parser.add_argument(
        "--cited-by-only",
        action="store_true",
        help="Skip scanning, just rebuild cited_by from existing text_citations",
    )
    args = parser.parse_args()
    process_all(args.db, args.batch_size, args.limit, args.cited_by_only)


if __name__ == "__main__":
    main()
