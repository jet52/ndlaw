"""Merge rich metadata from ~/refs/nd/opin/ JSON files into the opinions database.

The JSON files (scraped from ndcourts.gov) contain case names, filing dates,
authors, case types, voting records, highlights, and justice panels for all
neutral-cite opinions from 1997–present. This script matches them against
existing database records by citation and updates metadata fields.

Usage:
    python -m ndcourts_mcp.merge_nd_metadata [--db PATH] [--refs PATH] [--dry-run]
"""

import json
import re
from datetime import datetime
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection

REFS_ND_DIR = Path.home() / "refs" / "nd" / "opin"


def _parse_date(date_str: str) -> str | None:
    """Convert 'M/D/YYYY' or 'MM/DD/YYYY' to 'YYYY-MM-DD'."""
    if not date_str:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _normalize_author(author_str: str | None) -> str | None:
    """Extract last name from author field like 'McEvers, Lisa K. Fair'."""
    if not author_str:
        return None
    # Take the part before the first comma
    name = author_str.split(",")[0].strip()
    # Handle "Per Curiam" or similar
    if name.lower() in ("per curiam", "per_curiam"):
        return None
    return name


def _load_json_records(refs_dir: Path) -> list[dict]:
    """Load all non-backup JSON opinion records."""
    records = []
    for f in sorted(refs_dir.glob("*_opinions.json")):
        if ".backup" in f.name:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            records.extend(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  Warning: failed to read {f.name}: {e}")
    return records


def merge(db_path: Path, refs_dir: Path, dry_run: bool = False):
    records = _load_json_records(refs_dir)
    print(f"Loaded {len(records)} metadata records from {refs_dir}")

    conn = get_connection(db_path)

    # Ensure new columns exist (for databases created before schema update)
    for col, col_type in [
        ("opinion_url", "TEXT"),
        ("case_type", "TEXT"),
        ("highlight", "TEXT"),
        ("voting_record", "TEXT"),
        ("all_justices", "TEXT"),
        ("unanimous", "INTEGER"),
    ]:
        try:
            conn.execute(f"ALTER TABLE opinions ADD COLUMN {col} {col_type}")
        except Exception:
            pass  # Column already exists

    stats = {"updated": 0, "not_found": 0, "skipped": 0}

    for rec in records:
        citation = rec.get("citation", "").strip()
        if not citation:
            stats["skipped"] += 1
            continue

        # Find the opinion by citation
        row = conn.execute(
            """SELECT o.id, o.case_name, o.date_filed, o.author, o.docket_number,
                      o.case_name_full, o.per_curiam
               FROM opinions o
               JOIN citations c ON c.opinion_id = o.id
               WHERE c.citation = ?""",
            (citation,),
        ).fetchone()

        if not row:
            stats["not_found"] += 1
            continue

        opinion_id = row["id"]

        # Parse metadata from JSON
        case_name = rec.get("case_name") or row["case_name"]
        date_filed = _parse_date(rec.get("filing_date")) or row["date_filed"]
        author = _normalize_author(rec.get("author")) or row["author"]
        docket_numbers = rec.get("docket_numbers", [])
        docket_number = ", ".join(docket_numbers) if docket_numbers else row["docket_number"]

        # Check per curiam from author field
        per_curiam = row["per_curiam"]
        raw_author = rec.get("author", "")
        if raw_author and "per curiam" in raw_author.lower():
            per_curiam = 1
            author = None

        # Build judges string from all_justices
        all_justices = [j for j in rec.get("all_justices", []) if j]
        judges = ", ".join(all_justices) if all_justices else None

        # New fields
        case_type = rec.get("case_type")
        highlight = rec.get("highlight")
        opinion_url = rec.get("opinion_url")
        unanimous = 1 if rec.get("unanimous") else (0 if rec.get("unanimous") is False else None)

        voting_record = json.dumps(rec["voting_record"]) if rec.get("voting_record") else None
        all_justices_json = json.dumps(all_justices) if all_justices else None

        if not dry_run:
            conn.execute(
                """UPDATE opinions SET
                    case_name = ?,
                    date_filed = ?,
                    author = ?,
                    docket_number = ?,
                    per_curiam = ?,
                    judges = ?,
                    case_type = ?,
                    highlight = ?,
                    opinion_url = ?,
                    unanimous = ?,
                    voting_record = ?,
                    all_justices = ?
                   WHERE id = ?""",
                (
                    case_name,
                    date_filed,
                    author,
                    docket_number,
                    per_curiam,
                    judges,
                    case_type,
                    highlight,
                    opinion_url,
                    unanimous,
                    voting_record,
                    all_justices_json,
                    opinion_id,
                ),
            )
        stats["updated"] += 1

    if not dry_run:
        conn.commit()

    conn.close()

    print(f"\nDone {'(dry run)' if dry_run else ''}.")
    print(f"  {stats['updated']} opinions updated")
    print(f"  {stats['not_found']} citations not found in database")
    print(f"  {stats['skipped']} records skipped (no citation)")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Merge ND metadata into opinions database")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Database path")
    parser.add_argument("--refs", type=Path, default=REFS_ND_DIR, help="ND opinion JSON directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without writing")
    args = parser.parse_args()

    merge(args.db, args.refs, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
