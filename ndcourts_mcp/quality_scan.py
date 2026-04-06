"""Scan opinion text for quality signals and persist scores.

Detects OCR artifacts, garbage characters, HTML contamination,
short-line damage, and paragraph markers. Produces a composite
0–100 quality score for each opinion.

Usage:
    python -m ndcourts_mcp.quality_scan [--db PATH] [--limit N] [--rescan]
"""

import argparse
import re
import sqlite3
import time
from pathlib import Path

from .db import DEFAULT_DB_PATH, create_schema, get_connection, log_provenance

# ── Detection patterns ───────────────────────────────────────────────

# OCR artifact characters: inverted punctuation, black square, pound sign
# (when not preceded/followed by a digit), double low-9 quotation mark
_OCR_ARTIFACT_CHARS = set("¡¿■£„")

# Characters that are legitimate in legal text (ASCII + common Unicode)
# Smart quotes, section sign, pilcrow, em/en dash, bullet, degree,
# common accented chars in names (é, ñ, etc.)
_LEGIT_NONASCII = set(
    "\u2018\u2019"  # '' smart single quotes
    "\u201C\u201D"  # "" smart double quotes
    "\u2014\u2013"  # — – em/en dash
    "\u00A7"        # § section sign
    "\u00B6"        # ¶ pilcrow
    "\u2022"        # • bullet
    "\u00B0"        # ° degree
    "\u00AB\u00BB"  # «» guillemets
    "\u2026"        # … ellipsis
    "\u00C6\u00E6"  # Ææ
    "\u0152\u0153"  # Œœ
)
# Common accented Latin chars (names, loanwords)
_LEGIT_NONASCII.update(chr(c) for c in range(0x00C0, 0x0100))  # À–ÿ
# Additional math/legal symbols
_LEGIT_NONASCII.update(set("\u00BD\u00BC\u00BE\u00D7\u00F7"))  # ½¼¾×÷

# HTML/JS contamination patterns
_HTML_RE = re.compile(
    r'<\s*(?:script|div|span|html|head|body|style|link|meta|iframe|form|input|button|table|tr|td|th|img|a\s)[^>]*>',
    re.IGNORECASE,
)
_JS_RE = re.compile(
    r'(?:onclick|onload|onerror|javascript\s*:|document\.(?:write|getElementById)|window\.(?:location|open)|var\s+\w+\s*=|function\s*\()',
    re.IGNORECASE,
)

# Paragraph markers: [¶1] or ¶1 at start of line
_PARA_MARKER_RE = re.compile(r'(?:^|\n)\s*(?:\[¶|¶)\d+')


# ── Scoring ──────────────────────────────────────────────────────────

def score_opinion(text: str, source_reporter: str) -> dict:
    """Compute quality signals for a single opinion text.

    Returns a dict with all quality_scores columns except opinion_id and scanned_at.
    """
    # Strip YAML frontmatter before analysis
    text_body = re.sub(r'^---\n[\s\S]*?\n---\n*', '', text)

    if not text_body.strip():
        return {
            "ocr_artifacts": 0,
            "garbage_chars": 0,
            "short_line_ratio": 1.0,
            "has_html": 0,
            "para_markers": 0,
            "overall_score": 0.0,
        }

    # OCR artifacts
    ocr_artifacts = sum(1 for ch in text_body if ch in _OCR_ARTIFACT_CHARS)

    # Garbage characters: non-ASCII that isn't in the legit set
    garbage_chars = 0
    for ch in text_body:
        if ord(ch) > 127 and ch not in _LEGIT_NONASCII:
            if ch not in _OCR_ARTIFACT_CHARS:  # already counted above
                garbage_chars += 1

    # Short-line ratio (OCR line-break damage)
    lines = text_body.split('\n')
    non_empty_lines = [ln for ln in lines if ln.strip()]
    if non_empty_lines:
        short_lines = sum(1 for ln in non_empty_lines if 0 < len(ln.strip()) < 15)
        short_line_ratio = short_lines / len(non_empty_lines)
    else:
        short_line_ratio = 1.0

    # HTML/JS contamination
    has_html = 1 if (_HTML_RE.search(text_body) or _JS_RE.search(text_body)) else 0

    # Paragraph markers (quality signal)
    para_markers = len(_PARA_MARKER_RE.findall(text_body))

    # ── Composite score (0–100, higher = better quality) ──
    score = 50.0  # baseline

    # Source reporter bonus
    if source_reporter == "ND":
        score += 15
    elif source_reporter == "NW2d":
        score += 8

    # Paragraph markers: strong quality signal
    if para_markers >= 3:
        score += 15
    elif para_markers >= 1:
        score += 8

    # Text length bonus (longer opinions tend to be better sourced)
    text_len = len(text_body)
    if text_len > 5000:
        score += 5
    elif text_len < 500:
        score -= 10

    # Penalties
    score -= ocr_artifacts * 2          # each OCR artifact is a strong signal
    score -= garbage_chars * 1          # unknown chars are less certain
    score -= short_line_ratio * 20      # high ratio = severe OCR damage
    if has_html:
        score -= 30                     # HTML contamination is very bad

    # Clamp
    score = max(0.0, min(100.0, score))

    return {
        "ocr_artifacts": ocr_artifacts,
        "garbage_chars": garbage_chars,
        "short_line_ratio": round(short_line_ratio, 4),
        "has_html": has_html,
        "para_markers": para_markers,
        "overall_score": round(score, 1),
    }


# ── Batch processing ─────────────────────────────────────────────────

def process_all(
    db_path: Path = DEFAULT_DB_PATH,
    batch_size: int = 500,
    limit: int | None = None,
    rescan: bool = False,
) -> None:
    """Scan all opinions and store quality scores."""
    conn = get_connection(db_path)
    create_schema(conn)

    if rescan:
        conn.execute("DELETE FROM quality_scores")
        conn.commit()
        print("Cleared existing scores for rescan.", flush=True)

    # Get opinions to process (skip already-scored unless rescan)
    opinions = conn.execute(
        """SELECT o.id, o.text_content, o.source_reporter
           FROM opinions o
           LEFT JOIN quality_scores qs ON qs.opinion_id = o.id
           WHERE qs.opinion_id IS NULL
           ORDER BY o.date_filed"""
    ).fetchall()

    total = len(opinions)
    if limit:
        opinions = opinions[:limit]

    to_process = len(opinions)
    if to_process == 0:
        already = conn.execute("SELECT COUNT(*) FROM quality_scores").fetchone()[0]
        print(f"Nothing to process ({already} already scored).", flush=True)
        conn.close()
        return

    already_done = conn.execute("SELECT COUNT(*) FROM quality_scores").fetchone()[0]
    print(
        f"Opinions to scan: {to_process} (of {total} remaining, {already_done} already done)",
        flush=True,
    )

    processed = 0
    start = time.time()
    batch_start = time.time()

    for row in opinions:
        oid = row["id"]
        text = row["text_content"]
        reporter = row["source_reporter"]

        scores = score_opinion(text, reporter)

        conn.execute(
            """INSERT OR REPLACE INTO quality_scores
               (opinion_id, ocr_artifacts, garbage_chars, short_line_ratio,
                has_html, para_markers, dupe_cites, overall_score)
               VALUES (?, ?, ?, ?, ?, ?, 0, ?)""",
            (oid, scores["ocr_artifacts"], scores["garbage_chars"],
             scores["short_line_ratio"], scores["has_html"],
             scores["para_markers"], scores["overall_score"]),
        )

        processed += 1
        if processed % batch_size == 0 or processed == to_process:
            conn.commit()
            elapsed = time.time() - batch_start
            rate = processed / (time.time() - start)
            eta = (to_process - processed) / rate if rate > 0 else 0
            print(
                f"  {processed}/{to_process} "
                f"({rate:.0f} op/s, ETA {int(eta)}s)",
                flush=True,
            )
            batch_start = time.time()

    # Duplicate-reporter citation pass: flag opinions with >1 cite per reporter
    dupe_rows = conn.execute("""
        SELECT c.opinion_id, COUNT(*) as n
        FROM citations c
        WHERE c.reporter IN ('ND', 'NDold')
        GROUP BY c.opinion_id, c.reporter
        HAVING n > 1
    """).fetchall()
    dupe_count = 0
    for dr in dupe_rows:
        conn.execute(
            "UPDATE quality_scores SET dupe_cites = ? WHERE opinion_id = ?",
            (dr["n"], dr["opinion_id"]),
        )
        dupe_count += 1
    if dupe_count:
        conn.commit()
        print(f"  Flagged {dupe_count} opinions with duplicate reporter citations", flush=True)

    # Summary
    elapsed = time.time() - start
    stats = conn.execute("""
        SELECT COUNT(*) as total,
               AVG(overall_score) as avg_score,
               MIN(overall_score) as min_score,
               MAX(overall_score) as max_score,
               SUM(CASE WHEN has_html = 1 THEN 1 ELSE 0 END) as html_count,
               SUM(ocr_artifacts) as total_ocr,
               SUM(garbage_chars) as total_garbage,
               SUM(CASE WHEN dupe_cites > 0 THEN 1 ELSE 0 END) as dupe_cite_count
        FROM quality_scores
    """).fetchone()

    print(
        f"\nDone in {elapsed:.1f}s. {stats['total']} opinions scored.\n"
        f"  Average score: {stats['avg_score']:.1f}\n"
        f"  Range: {stats['min_score']:.1f} – {stats['max_score']:.1f}\n"
        f"  HTML contaminated: {stats['html_count']}\n"
        f"  Total OCR artifacts: {stats['total_ocr']}\n"
        f"  Total garbage chars: {stats['total_garbage']}\n"
        f"  Duplicate reporter citations: {stats['dupe_cite_count']}",
        flush=True,
    )
    log_provenance(conn, "quality_scan", rows_affected=stats["total"],
                   notes=f"avg={stats['avg_score']:.1f}, html={stats['html_count']}, ocr={stats['total_ocr']}")
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan opinion text for quality signals")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--limit", type=int, default=None, help="Process at most N opinions")
    parser.add_argument("--rescan", action="store_true", help="Clear existing scores and rescan all")
    args = parser.parse_args()
    process_all(args.db, args.batch_size, args.limit, args.rescan)


if __name__ == "__main__":
    main()
