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


def build_citation_lookup(conn: sqlite3.Connection) -> dict[str, list[int]]:
    """Build {normalized_citation_string: [opinion_id, ...]} from the citations table.

    A citation string may map to MORE THAN ONE opinion when distinct cases share
    a reporter page (e.g. a short order and the next case both begin on
    298 N.W.2d 372). The lookup therefore keeps every candidate; the caller
    disambiguates by the citing case name (see `_resolve_cited_oid`). Stores both
    the raw DB form and a normalized form (edition spacing removed) so jetcite's
    "N.W. 2d" matches the DB's "N.W.2d".
    """
    rows = conn.execute("SELECT citation, opinion_id FROM citations").fetchall()
    lookup: dict[str, list[int]] = {}
    for row in rows:
        oid = row["opinion_id"]
        for key in (row["citation"], _normalize_cite_key(row["citation"])):
            bucket = lookup.setdefault(key, [])
            if oid not in bucket:
                bucket.append(oid)
    return lookup


def build_opinion_meta(conn: sqlite3.Connection) -> dict[int, tuple[str, str]]:
    """Return {opinion_id: (case_name, date_filed)} for cited_by disambiguation."""
    return {
        r["id"]: (r["case_name"] or "", r["date_filed"] or "")
        for r in conn.execute("SELECT id, case_name, date_filed FROM opinions")
    }


# Structural/connective tokens that don't help distinguish two case names.
_NAME_STOP = frozenset({
    "v", "vs", "in", "re", "matter", "of", "the", "and", "a", "an",
    "ex", "rel", "et", "al", "no", "city", "state", "county",
})


def _name_tokens(name: str) -> set[str]:
    """Distinctive lowercase word tokens of a case name (drops structural words)."""
    if not name:
        return set()
    return {t for t in re.findall(r"[a-z0-9]+", name.lower())
            if t not in _NAME_STOP and len(t) > 1}


def _resolve_cited_oid(
    candidates: list[int],
    antecedent_name: str | None,
    citer_date: str,
    meta: dict[int, tuple[str, str]],
) -> int | None:
    """Pick which candidate opinion a citation refers to, or None if unresolved.

    1. Drop candidates filed after the citing opinion (a case can't be cited
       before it exists).
    2. If one remains, return it.
    3. Otherwise disambiguate by the antecedent (citing) case name: the candidate
       whose case_name shares the most distinctive tokens, provided it is a unique
       winner with at least one shared token.
    4. Else return None (caller skips the edge — see Phase 2 fallback policy).
    """
    feasible = [o for o in candidates if not citer_date or meta.get(o, ("", ""))[1] <= citer_date]
    if not feasible:
        return None
    if len(feasible) == 1:
        return feasible[0]
    at = _name_tokens(antecedent_name or "")
    if at:
        scored = sorted(
            ((len(at & _name_tokens(meta.get(o, ("", ""))[0])), o) for o in feasible),
            reverse=True,
        )
        if scored[0][0] >= 1 and (len(scored) == 1 or scored[0][0] > scored[1][0]):
            return scored[0][1]
    return None


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
            "antecedent_name": cite.antecedent_name,
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
    citation_lookup: dict[str, list[int]],
    own_cites_map: dict[int, set[str]],
    meta: dict[int, tuple[str, str]],
    unresolved: list[tuple] | None = None,
) -> dict[str, int]:
    """Store scan results for one opinion. Returns citation type counts."""
    counts: dict[str, int] = {}
    own_normalized = own_cites_map.get(opinion_id, set())
    citer_date = meta.get(opinion_id, ("", ""))[1]

    for cd in cite_dicts:
        ct = cd["cite_type"]
        jurisdiction = cd["jurisdiction"]

        resolved: list[int] = []
        others: list[int] = []
        if ct == "case":
            norm_key = _normalize_cite_key(cd["normalized"])
            resolved = (citation_lookup.get(cd["normalized"])
                        or citation_lookup.get(norm_key) or [])
            others = [o for o in resolved if o != opinion_id]
            # Skip the opinion's OWN citation mis-extracted from the caption as
            # an authority it cites — a case cannot cite itself. Guard only when
            # the cite is unique to this opinion; shared-page twins (others
            # present) are kept for shared-page disambiguation.
            if norm_key in own_normalized and not others:
                continue
            # Any match to a corpus opinion means a North Dakota case: the N.W.
            # regional reporter defaults to 'us', but a unique volume+page that
            # resolves into our (ND-only) corpus is definitionally ND.
            if resolved:
                jurisdiction = "nd"

        counts[ct] = counts.get(ct, 0) + 1

        conn.execute(
            """INSERT OR IGNORE INTO text_citations
               (opinion_id, normalized, cite_type, jurisdiction, raw_text, url, parallel_group, antecedent_name)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (opinion_id, cd["normalized"], ct, jurisdiction,
             cd["raw_text"], cd["url"], cd["parallel_group"], cd.get("antecedent_name")),
        )

        # Build cited_by for case citations
        if ct == "case":
            if norm_key in own_normalized:
                continue
            candidates = others
            if not candidates:
                continue
            cited_opinion_id = _resolve_cited_oid(
                candidates, cd.get("antecedent_name"), citer_date, meta)
            if cited_opinion_id:
                conn.execute(
                    """INSERT OR IGNORE INTO cited_by
                       (cited_opinion_id, citing_opinion_id, citation)
                       VALUES (?, ?, ?)""",
                    (cited_opinion_id, opinion_id, cd["normalized"]),
                )
            elif unresolved is not None:
                unresolved.append((opinion_id, cd["normalized"], cd.get("antecedent_name"),
                                   "|".join(str(o) for o in candidates)))

    conn.execute(
        "INSERT OR IGNORE INTO cite_extract_progress (opinion_id) VALUES (?)",
        (opinion_id,),
    )
    return counts


def rebuild_cited_by(
    conn: sqlite3.Connection,
    citation_lookup: dict[str, list[int]],
    triage_path: Path | None = None,
) -> tuple[int, int]:
    """Rebuild cited_by from text_citations, disambiguating shared-page cites.

    Returns (inserted, unresolved). Collisions that cannot be attributed to a
    single case (no antecedent name, or none matches) are skipped and, if
    `triage_path` is given, written there for review.
    """
    conn.execute("DELETE FROM cited_by")

    rows = conn.execute(
        "SELECT opinion_id, normalized, antecedent_name FROM text_citations WHERE cite_type = 'case'"
    ).fetchall()

    own_cites: dict[int, set[str]] = {}
    for r in conn.execute("SELECT opinion_id, citation FROM citations").fetchall():
        own_cites.setdefault(r["opinion_id"], set()).add(_normalize_cite_key(r["citation"]))

    meta = build_opinion_meta(conn)

    inserted = 0
    unresolved: list[tuple] = []
    for row in rows:
        opinion_id = row["opinion_id"]
        normalized = row["normalized"]
        norm_key = _normalize_cite_key(normalized)
        if norm_key in own_cites.get(opinion_id, set()):
            continue
        candidates = citation_lookup.get(normalized) or citation_lookup.get(norm_key) or []
        candidates = [o for o in candidates if o != opinion_id]
        if not candidates:
            continue
        citer_date = meta.get(opinion_id, ("", ""))[1]
        cited_opinion_id = _resolve_cited_oid(
            candidates, row["antecedent_name"], citer_date, meta)
        if cited_opinion_id:
            conn.execute(
                """INSERT OR IGNORE INTO cited_by
                   (cited_opinion_id, citing_opinion_id, citation)
                   VALUES (?, ?, ?)""",
                (cited_opinion_id, opinion_id, normalized),
            )
            inserted += 1
        elif len(candidates) > 1:
            unresolved.append((opinion_id, normalized, row["antecedent_name"],
                               "|".join(str(o) for o in candidates)))

    conn.commit()

    if triage_path is not None and unresolved:
        import csv
        with open(triage_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["citing_opinion_id", "citation", "antecedent_name", "candidate_oids"])
            w.writerows(unresolved)

    # Report distinct edges (UNIQUE collapses a citer that reaches the same case
    # via multiple parallel cites), not the pre-dedup insert attempts.
    edges = conn.execute("SELECT COUNT(*) FROM cited_by").fetchone()[0]
    return edges, len(unresolved)


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
        triage = db_path.parent / "triage" / "cited-by-unresolved-collisions.csv"
        triage.parent.mkdir(exist_ok=True)
        count, unresolved = rebuild_cited_by(conn, citation_lookup, triage_path=triage)
        print(f"  {count} cross-links created; {unresolved} shared-page collisions unresolved "
              f"(skipped, logged to {triage})")
        conn.close()
        return

    # Build own-cites map for self-cite detection (normalized keys)
    own_cites_map: dict[int, set[str]] = {}
    for r in conn.execute("SELECT opinion_id, citation FROM citations").fetchall():
        own_cites_map.setdefault(r["opinion_id"], set()).add(_normalize_cite_key(r["citation"]))

    # Opinion metadata (case_name, date_filed) for cited_by disambiguation
    meta = build_opinion_meta(conn)
    unresolved_links: list[tuple] = []

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
            counts = _store_results(conn, opinion_id, cite_dicts, citation_lookup,
                                    own_cites_map, meta, unresolved_links)
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
    if unresolved_links:
        triage = db_path.parent / "triage" / "cited-by-unresolved-collisions.csv"
        triage.parent.mkdir(exist_ok=True)
        import csv
        with open(triage, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["citing_opinion_id", "citation", "antecedent_name", "candidate_oids"])
            w.writerows(unresolved_links)
    print(
        f"\nDone in {overall/3600:.1f}h. "
        f"{tc_count} text_citations, {cb_count} cited_by links. "
        f"{len(unresolved_links)} shared-page collisions unresolved (skipped).",
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
