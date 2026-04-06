"""Scan for duplicate opinions using multiple detection strategies.

Finds candidate duplicate pairs and stores them in duplicate_candidates
for review via the webapp merge workflow.

Strategies:
1. Shared citation — different opinion_ids with the same citation string
2. Same name + date + text overlap — confirms with text similarity
3. Text fingerprint — minhash on first 500 words to find near-duplicates

Usage:
    python -m ndcourts_mcp.dedup_scan [--db PATH] [--strategy all|citation|name-date|fingerprint]
"""

import argparse
import hashlib
import re
import sqlite3
import time
from collections import defaultdict
from pathlib import Path

from .db import DEFAULT_DB_PATH, create_schema, get_connection


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter, return body only."""
    return re.sub(r"^---\n[\s\S]*?\n---\n*", "", text)


def _tokenize(text: str, max_tokens: int = 500) -> list[str]:
    """Extract first N word tokens from text body."""
    body = _strip_frontmatter(text)
    words = re.findall(r"[a-zA-Z']+", body.lower())
    return words[:max_tokens]


def _text_similarity(text_a: str, text_b: str) -> float:
    """Quick text similarity using word overlap on first 500 words.
    Returns 0.0–1.0 (Jaccard similarity).
    """
    words_a = set(_tokenize(text_a))
    words_b = set(_tokenize(text_b))
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


# ── Minhash for text fingerprinting ──────────────────────────────────

NUM_HASHES = 128


def _minhash(tokens: list[str]) -> list[int]:
    """Compute minhash signature from token list."""
    if not tokens:
        return [0] * NUM_HASHES

    # Generate shingles (3-grams of words)
    shingles = set()
    for i in range(len(tokens) - 2):
        shingles.add(" ".join(tokens[i : i + 3]))

    if not shingles:
        return [0] * NUM_HASHES

    sig = [float("inf")] * NUM_HASHES
    for shingle in shingles:
        for i in range(NUM_HASHES):
            h = int(hashlib.md5(f"{i}:{shingle}".encode()).hexdigest()[:8], 16)
            if h < sig[i]:
                sig[i] = h
    return sig


def _minhash_similarity(sig_a: list[int], sig_b: list[int]) -> float:
    """Estimate Jaccard similarity from two minhash signatures."""
    if not sig_a or not sig_b:
        return 0.0
    return sum(a == b for a, b in zip(sig_a, sig_b)) / len(sig_a)


# ── Strategy 1: Shared citations ─────────────────────────────────────

def _find_citation_dupes(conn: sqlite3.Connection) -> list[tuple[int, int, float]]:
    """Find opinion pairs sharing the same citation string."""
    rows = conn.execute("""
        SELECT c1.opinion_id as id_a, c2.opinion_id as id_b, c1.citation
        FROM citations c1
        JOIN citations c2 ON c1.citation = c2.citation AND c1.opinion_id < c2.opinion_id
    """).fetchall()

    pairs = {}
    for r in rows:
        key = (r["id_a"], r["id_b"])
        if key not in pairs:
            pairs[key] = 0.95  # high confidence for citation match
    return [(a, b, conf) for (a, b), conf in pairs.items()]


# ── Strategy 2: Same name + date + text similarity ───────────────────

def _find_name_date_dupes(conn: sqlite3.Connection) -> list[tuple[int, int, float, float]]:
    """Find opinions with same case_name + date_filed, then check text similarity."""
    rows = conn.execute("""
        SELECT o1.id as id_a, o2.id as id_b,
               o1.text_content as text_a, o2.text_content as text_b
        FROM opinions o1
        JOIN opinions o2 ON o1.case_name = o2.case_name
            AND o1.date_filed = o2.date_filed
            AND o1.id < o2.id
    """).fetchall()

    results = []
    for r in rows:
        sim = _text_similarity(r["text_a"], r["text_b"])
        if sim > 0.5:
            # High text overlap with matching metadata = likely duplicate
            confidence = min(0.95, 0.5 + sim * 0.5)
            results.append((r["id_a"], r["id_b"], confidence, sim))
    return results


# ── Strategy 3: Text fingerprinting ──────────────────────────────────

def _find_fingerprint_dupes(
    conn: sqlite3.Connection, threshold: float = 0.6,
) -> list[tuple[int, int, float, float]]:
    """Find near-duplicate texts using minhash fingerprinting.

    Uses LSH-style banding: split signature into bands, hash each band,
    opinions in the same bucket are candidates.
    """
    print("  Computing minhash signatures...", flush=True)
    rows = conn.execute(
        "SELECT id, text_content FROM opinions ORDER BY id"
    ).fetchall()

    sigs: dict[int, list[int]] = {}
    for i, r in enumerate(rows):
        tokens = _tokenize(r["text_content"])
        sigs[r["id"]] = _minhash(tokens)
        if (i + 1) % 5000 == 0:
            print(f"    {i + 1}/{len(rows)} signatures computed", flush=True)

    print(f"  {len(sigs)} signatures computed. Running LSH...", flush=True)

    # LSH banding: 32 bands of 4 rows each
    bands = 32
    rows_per_band = NUM_HASHES // bands
    buckets: list[dict[int, list[int]]] = [defaultdict(list) for _ in range(bands)]

    for oid, sig in sigs.items():
        for b in range(bands):
            start = b * rows_per_band
            band_slice = tuple(sig[start : start + rows_per_band])
            band_hash = hash(band_slice)
            buckets[b][band_hash].append(oid)

    # Collect candidate pairs from buckets
    candidates: set[tuple[int, int]] = set()
    for b in range(bands):
        for bucket_ids in buckets[b].values():
            if len(bucket_ids) > 1 and len(bucket_ids) < 50:
                for i in range(len(bucket_ids)):
                    for j in range(i + 1, len(bucket_ids)):
                        a, b_id = min(bucket_ids[i], bucket_ids[j]), max(bucket_ids[i], bucket_ids[j])
                        candidates.add((a, b_id))

    print(f"  {len(candidates)} candidate pairs from LSH. Computing similarities...", flush=True)

    results = []
    for a, b in candidates:
        sim = _minhash_similarity(sigs[a], sigs[b])
        if sim >= threshold:
            confidence = min(0.9, sim)
            results.append((a, b, confidence, sim))

    return results


# ── Main ─────────────────────────────────────────────────────────────

def run_scan(
    db_path: Path = DEFAULT_DB_PATH,
    strategy: str = "all",
    clear: bool = False,
) -> None:
    """Run duplicate detection and store candidates."""
    conn = get_connection(db_path)
    create_schema(conn)

    if clear:
        conn.execute("DELETE FROM duplicate_candidates WHERE reviewed = 0")
        conn.commit()
        print("Cleared unreviewed candidates.", flush=True)

    # Load existing pairs to avoid re-inserting
    existing = set()
    for r in conn.execute("SELECT opinion_a, opinion_b FROM duplicate_candidates").fetchall():
        existing.add((r["opinion_a"], r["opinion_b"]))

    inserted = 0
    start = time.time()

    # Strategy 1: Citation overlap
    if strategy in ("all", "citation"):
        print("Strategy 1: Shared citations...", flush=True)
        cite_dupes = _find_citation_dupes(conn)
        for id_a, id_b, confidence in cite_dupes:
            if (id_a, id_b) not in existing:
                conn.execute(
                    """INSERT OR IGNORE INTO duplicate_candidates
                       (opinion_a, opinion_b, strategy, confidence)
                       VALUES (?, ?, 'citation', ?)""",
                    (id_a, id_b, confidence),
                )
                existing.add((id_a, id_b))
                inserted += 1
        conn.commit()
        print(f"  Found {len(cite_dupes)} pairs, {inserted} new", flush=True)

    # Strategy 2: Name + date + text
    prev_inserted = inserted
    if strategy in ("all", "name-date"):
        print("Strategy 2: Same name + date + text similarity...", flush=True)
        nd_dupes = _find_name_date_dupes(conn)
        for id_a, id_b, confidence, sim in nd_dupes:
            if (id_a, id_b) not in existing:
                conn.execute(
                    """INSERT OR IGNORE INTO duplicate_candidates
                       (opinion_a, opinion_b, strategy, confidence, text_similarity)
                       VALUES (?, ?, 'name+date+text', ?, ?)""",
                    (id_a, id_b, confidence, sim),
                )
                existing.add((id_a, id_b))
                inserted += 1
        conn.commit()
        print(f"  Found {len(nd_dupes)} pairs with similarity > 0.5, {inserted - prev_inserted} new", flush=True)

    # Strategy 3: Text fingerprinting
    prev_inserted = inserted
    if strategy in ("all", "fingerprint"):
        print("Strategy 3: Text fingerprinting (minhash + LSH)...", flush=True)
        fp_dupes = _find_fingerprint_dupes(conn)
        for id_a, id_b, confidence, sim in fp_dupes:
            if (id_a, id_b) not in existing:
                conn.execute(
                    """INSERT OR IGNORE INTO duplicate_candidates
                       (opinion_a, opinion_b, strategy, confidence, text_similarity)
                       VALUES (?, ?, 'fingerprint', ?, ?)""",
                    (id_a, id_b, confidence, sim),
                )
                existing.add((id_a, id_b))
                inserted += 1
        conn.commit()
        print(f"  Found {len(fp_dupes)} pairs above threshold, {inserted - prev_inserted} new", flush=True)

    elapsed = time.time() - start

    # Summary
    total = conn.execute("SELECT COUNT(*) FROM duplicate_candidates").fetchone()[0]
    unreviewed = conn.execute("SELECT COUNT(*) FROM duplicate_candidates WHERE reviewed = 0").fetchone()[0]
    by_strategy = conn.execute(
        "SELECT strategy, COUNT(*) as n FROM duplicate_candidates GROUP BY strategy"
    ).fetchall()

    print(f"\nDone in {elapsed:.1f}s. {inserted} new candidates added.")
    print(f"Total candidates: {total} ({unreviewed} unreviewed)")
    for r in by_strategy:
        print(f"  {r['strategy']}: {r['n']}")

    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan for duplicate opinions")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument(
        "--strategy", choices=["all", "citation", "name-date", "fingerprint"],
        default="all", help="Which detection strategies to run (default: all)",
    )
    parser.add_argument("--clear", action="store_true", help="Clear unreviewed candidates first")
    args = parser.parse_args()
    run_scan(args.db, args.strategy, args.clear)


if __name__ == "__main__":
    main()
