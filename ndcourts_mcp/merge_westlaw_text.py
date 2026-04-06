"""Replace low-quality opinion text with clean Westlaw opinion text.

For opinions where we have a Westlaw .doc download and the current text came
from CourtListener (NW, NW2d), replaces text_content with the Westlaw
opinion body. Preserves YAML frontmatter from the existing record.

Opinions sourced from ndcourts.gov (source_reporter='ND') are NOT replaced —
the court's own text is authoritative for 1997+ opinions. Westlaw downloads
for those should be used as a reference to identify specific corrections.

Usage:
    python -m ndcourts_mcp.merge_westlaw_text [--db PATH] [--dry-run] [--batch NAME]
"""

import argparse
import re
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection
from .ingest_westlaw import _doc_to_text, _parse_westlaw_doc

# Headnote leak detection
_HEADNOTE_STARTS = re.compile(
    r"^(Syllabus|Synopsis|West Headnotes|Attorneys and Law Firms)",
    re.IGNORECASE,
)
_BRACKETED_NUMS = re.compile(r"\[\d+\]")


def _extract_frontmatter(text: str) -> tuple[str, str]:
    """Split text into YAML frontmatter and body. Returns (frontmatter, body)."""
    m = re.match(r"(---\n[\s\S]*?\n---\n*)", text)
    if m:
        return m.group(1), text[m.end():]
    return "", text


def _extract_star_pages(text: str) -> set[str]:
    """Extract star pagination markers like *293 from text."""
    return set(re.findall(r"\*\d+", text))


def _validate_westlaw_text(wl_text: str, db_text_body: str, case_name: str) -> list[str]:
    """Validate Westlaw text before replacement. Returns list of warnings (empty = OK)."""
    warnings = []

    # Headnote leak check
    first_200 = wl_text[:200]
    if _HEADNOTE_STARTS.search(first_200):
        warnings.append("REJECT: Westlaw text starts with headnote/syllabus content")
        return warnings

    if len(_BRACKETED_NUMS.findall(wl_text[:500])) >= 3:
        warnings.append("REJECT: Westlaw text has bracketed headnote references in opening")
        return warnings

    # Length sanity check
    if len(wl_text) < len(db_text_body) * 0.3 and len(db_text_body) > 500:
        warnings.append(
            f"REJECT: Westlaw text suspiciously short ({len(wl_text)} vs {len(db_text_body)} chars)"
        )
        return warnings

    # Star pagination cross-check (informational, not blocking)
    wl_stars = _extract_star_pages(wl_text)
    db_stars = _extract_star_pages(db_text_body)
    if db_stars and not wl_stars:
        warnings.append(f"INFO: DB has star pagination ({len(db_stars)} markers) but Westlaw does not")
    elif db_stars and wl_stars:
        missing = db_stars - wl_stars
        extra = wl_stars - db_stars
        if missing:
            warnings.append(f"INFO: Star pages in DB but not Westlaw: {sorted(missing)[:5]}")
        if extra:
            warnings.append(f"INFO: Star pages in Westlaw but not DB: {sorted(extra)[:5]}")

    return warnings


def process_all(
    db_path: Path = DEFAULT_DB_PATH,
    dry_run: bool = True,
    batch_name: str = "westlaw-text-merge",
) -> None:
    """Replace text for opinions with Westlaw sources."""
    conn = get_connection(db_path)

    # Find opinions with westlaw source that are NOT ndcourts.gov-sourced
    rows = conn.execute("""
        SELECT os.opinion_id, os.source_path,
               o.case_name, o.date_filed, o.source_reporter, o.text_content,
               qs.overall_score
        FROM opinion_sources os
        JOIN opinions o ON o.id = os.opinion_id
        LEFT JOIN quality_scores qs ON qs.opinion_id = o.id
        WHERE os.source_reporter = 'westlaw'
          AND o.source_reporter != 'ND'
        ORDER BY qs.overall_score ASC
    """).fetchall()

    if not rows:
        print("No eligible opinions with Westlaw sources found.")
        return

    nd_skipped = conn.execute("""
        SELECT COUNT(*) FROM opinion_sources os
        JOIN opinions o ON o.id = os.opinion_id
        WHERE os.source_reporter = 'westlaw' AND o.source_reporter = 'ND'
    """).fetchone()[0]

    print(f"Eligible for text replacement: {len(rows)}")
    if nd_skipped:
        print(f"Skipped (ndcourts.gov source, reference only): {nd_skipped}")
    print()

    replaced = 0
    rejected = 0
    errors = 0

    for row in rows:
        oid = row["opinion_id"]
        source_path = Path(row["source_path"])
        case_name = row["case_name"]
        date = row["date_filed"]
        score = row["overall_score"]

        print(f"{case_name} ({date}) [score={score:.0f}]")

        # Load and parse Westlaw doc
        if not source_path.exists():
            print(f"  SKIP: source file not found: {source_path}")
            errors += 1
            continue

        try:
            wl_raw = _doc_to_text(source_path)
            parsed = _parse_westlaw_doc(wl_raw)
        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1
            continue

        if not parsed or not parsed.get("opinion_text"):
            print(f"  SKIP: could not parse opinion text from Westlaw doc")
            errors += 1
            continue

        wl_text = parsed["opinion_text"]

        # Split existing text into frontmatter + body
        frontmatter, db_body = _extract_frontmatter(row["text_content"])

        # Validate
        warnings = _validate_westlaw_text(wl_text, db_body, case_name)
        for w in warnings:
            print(f"  {w}")

        if any(w.startswith("REJECT") for w in warnings):
            rejected += 1
            continue

        # Build new text: preserve frontmatter, replace body
        new_text = frontmatter + wl_text

        old_len = len(row["text_content"])
        new_len = len(new_text)

        if dry_run:
            print(f"  WOULD REPLACE: {old_len} → {new_len} chars")
        else:
            conn.execute(
                "UPDATE opinions SET text_content = ? WHERE id = ?",
                (new_text, oid),
            )
            conn.execute(
                "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                "VALUES (?, ?, 'text_content', ?, ?)",
                (batch_name, oid, f"[{old_len} chars from {row['source_reporter']}]",
                 f"[{new_len} chars from westlaw]"),
            )
            print(f"  REPLACED: {old_len} → {new_len} chars")

        replaced += 1

    if not dry_run:
        conn.commit()

    conn.close()

    print(f"\n{'DRY RUN — ' if dry_run else ''}Summary:")
    print(f"  Replaced: {replaced}")
    print(f"  Rejected: {rejected}")
    print(f"  Errors: {errors}")

    if not dry_run and replaced > 0:
        print(f"\nRun quality_scan --rescan to update scores.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replace opinion text with clean Westlaw text"
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Show what would change (default)")
    parser.add_argument("--apply", action="store_true",
                        help="Actually replace text")
    parser.add_argument("--batch", default="westlaw-text-merge",
                        help="Changelog batch name")
    args = parser.parse_args()
    process_all(args.db, dry_run=not args.apply, batch_name=args.batch)


if __name__ == "__main__":
    main()
