"""Scrape opinions from archive.ndcourts.gov (1997–2019).

Fetches the citation index for each year, downloads opinion HTML pages,
extracts metadata and text, archives HTML to ~/refs/opin/archive/,
and optionally ingests into the database as source_reporter='archive'.

Usage:
    python -m ndcourts_mcp.scrape_archive [--year YEAR] [--all] [--ingest] [--db PATH]
    python -m ndcourts_mcp.scrape_archive --year 1997 --ingest
    python -m ndcourts_mcp.scrape_archive --all --ingest
"""

import argparse
import html
import re
import sqlite3
import time
from pathlib import Path

import httpx

from .db import DEFAULT_DB_PATH, create_schema, get_connection, log_provenance

BASE_URL = "https://archive.ndcourts.gov"
ARCHIVE_DIR = Path.home() / "refs" / "opin" / "archive"
YEARS = list(range(1997, 2020))

# Rate limiting
REQUEST_DELAY = 0.3  # seconds between requests


def _fetch(client: httpx.Client, url: str) -> str:
    """Fetch a URL with rate limiting."""
    time.sleep(REQUEST_DELAY)
    resp = client.get(url, follow_redirects=True, timeout=30)
    resp.raise_for_status()
    return resp.text


# ── Citation index parsing ───────────────────────────────────────────

def parse_citation_index(html_text: str, year: int) -> list[dict]:
    """Parse a year's citation index page into a list of {nd_num, case_name, docket, url}."""
    results = []
    # Pattern: <a href="/court/opinions/DOCKET.htm">\n<large>NUM</large> -\nCase Name\n</a>
    pattern = re.compile(
        r'<a href="(/court/opinions/(\d+)\.htm)">\s*'
        r'<large>\s*(\d+)\s*</large>\s*-\s*'
        r'(.+?)\s*</a>',
        re.DOTALL,
    )
    for m in pattern.finditer(html_text):
        path, docket, nd_num, case_name = m.group(1), m.group(2), m.group(3), m.group(4)
        case_name = html.unescape(case_name.strip())
        case_name = re.sub(r'\s+', ' ', case_name)
        results.append({
            "nd_num": int(nd_num),
            "nd_cite": f"{year} ND {nd_num}",
            "case_name": case_name,
            "docket": docket,
            "url": f"{BASE_URL}{path}",
            "path": path,
        })
    return results


# ── Opinion page parsing ─────────────────────────────────────────────

def parse_opinion_page(html_text: str) -> dict:
    """Extract metadata and opinion text from an archive opinion HTML page."""
    result = {}

    # Title tag: "Case Name, Citation, Citation"
    title_m = re.search(r'<title>(.+?)</title>', html_text, re.IGNORECASE)
    if title_m:
        result["title"] = html.unescape(title_m.group(1).strip())

    # Meta description: "Filed DATE. Topic: X. Author: Y. Judge: Z."
    desc_m = re.search(r'<meta name="Description" content="(.+?)"', html_text, re.IGNORECASE)
    if desc_m:
        desc = html.unescape(desc_m.group(1))
        date_m = re.search(r'Filed\s+(\w+\.?\s+\d{1,2},?\s+\d{4})', desc)
        if date_m:
            result["date_raw"] = date_m.group(1)
            result["date_filed"] = _parse_date(date_m.group(1))
        author_m = re.search(r'Author:\s*(.+?)\.(?:\s|$)', desc)
        if author_m:
            result["author_raw"] = author_m.group(1).strip()
        topic_m = re.search(r'Topic:\s*(.+?)\.(?:\s|$)', desc)
        if topic_m:
            result["topic"] = topic_m.group(1).strip()

    # Meta author
    meta_author = re.search(r'<meta name="Author" content="(.+?)"', html_text, re.IGNORECASE)
    if meta_author:
        result["meta_author"] = html.unescape(meta_author.group(1).strip())

    # Extract citations from title
    if "title" in result:
        cites = re.findall(r'\d{4}\s+ND\s+\d+|\d+\s+N\.W\.2d\s+\d+', result["title"])
        result["citations"] = cites

    # Extract opinion text — convert HTML to plain text
    result["text"] = _html_to_text(html_text)

    return result


_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "march": 3, "apr": 4, "april": 4,
    "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_date(date_str: str) -> str | None:
    """Parse 'Jan. 16, 1997' → '1997-01-16'."""
    m = re.match(r"(\w+)\.?\s+(\d{1,2}),?\s+(\d{4})", date_str.strip())
    if not m:
        return None
    month_str = m.group(1).lower().rstrip(".")
    month = _MONTH_MAP.get(month_str)
    if not month:
        return None
    return f"{int(m.group(3)):04d}-{month:02d}-{int(m.group(2)):02d}"


def _html_to_text(html_text: str) -> str:
    """Convert opinion HTML to plain text, preserving paragraph markers."""
    # Extract body content
    body_m = re.search(r'<body[^>]*>(.*)</body>', html_text, re.DOTALL | re.IGNORECASE)
    if not body_m:
        return ""
    body = body_m.group(1)

    # Remove script tags
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r'<noscript[^>]*>.*?</noscript>', '', body, flags=re.DOTALL | re.IGNORECASE)

    # Remove the header navigation and document links
    body = re.sub(r'<table.*?</table>', '', body, count=1, flags=re.DOTALL | re.IGNORECASE)

    # Convert paragraph markers: [&#182;<a name="P1"></a>1] → [¶1]
    body = re.sub(r'\[&#182;<a name="P\d+"></a>(\d+)\]', r'[¶\1]', body)
    # Also handle ¶ directly
    body = re.sub(r'\[¶<a name="P\d+"></a>(\d+)\]', r'[¶\1]', body)

    # Convert <br> to newlines
    body = re.sub(r'<br\s*/?>', '\n', body, flags=re.IGNORECASE)

    # Convert <p> to double newlines
    body = re.sub(r'<p[^>]*>', '\n\n', body, flags=re.IGNORECASE)

    # Convert <hr> to separator
    body = re.sub(r'<hr[^>]*>', '\n---\n', body, flags=re.IGNORECASE)

    # Remove all remaining HTML tags
    body = re.sub(r'<[^>]+>', '', body)

    # Decode HTML entities
    body = html.unescape(body)

    # Clean up whitespace
    body = re.sub(r'[ \t]+', ' ', body)
    body = re.sub(r'\n{3,}', '\n\n', body)
    body = body.strip()

    return body


def _normalize_author(author_str: str) -> str | None:
    """Extract last name from author string, handle Per Curiam."""
    if not author_str:
        return None
    a = author_str.strip()
    if a.lower() in ("per curiam", "per curiam."):
        return None  # will set per_curiam flag instead
    # Take last name from "VandeWalle" or "Gerald W. VandeWalle"
    parts = a.split()
    if parts:
        return parts[-1].rstrip(".,")
    return None


# ── Scraping ─────────────────────────────────────────────────────────

def scrape_year(
    client: httpx.Client, year: int, archive_dir: Path,
) -> list[dict]:
    """Scrape all opinions for a given year. Returns list of parsed opinions."""
    print(f"\n{'='*60}")
    print(f"Year {year}")
    print(f"{'='*60}")

    # Fetch citation index
    index_url = f"{BASE_URL}/opinions/cite/{year}.htm"
    index_html = _fetch(client, index_url)
    entries = parse_citation_index(index_html, year)
    print(f"  {len(entries)} opinions in index")

    # Archive index page
    year_dir = archive_dir / str(year)
    year_dir.mkdir(parents=True, exist_ok=True)
    (year_dir / "_index.htm").write_text(index_html, encoding="utf-8")

    opinions = []
    for i, entry in enumerate(entries):
        nd_cite = entry["nd_cite"]
        docket = entry["docket"]
        htm_path = year_dir / f"{docket}.htm"

        # Skip if already downloaded
        if htm_path.exists():
            raw_html = htm_path.read_text(encoding="utf-8", errors="replace")
        else:
            try:
                raw_html = _fetch(client, entry["url"])
                htm_path.write_text(raw_html, encoding="utf-8")
            except Exception as e:
                print(f"  ERROR fetching {nd_cite}: {e}")
                continue

        # Parse
        parsed = parse_opinion_page(raw_html)
        parsed["nd_cite"] = nd_cite
        parsed["nd_num"] = entry["nd_num"]
        parsed["docket"] = docket
        parsed["case_name_index"] = entry["case_name"]
        parsed["year"] = year
        parsed["source_path"] = str(htm_path.relative_to(Path.home() / "refs" / "opin"))
        opinions.append(parsed)

        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(entries)} fetched", flush=True)

    print(f"  {len(opinions)} opinions scraped")
    return opinions


# ── Database ingestion ───────────────────────────────────────────────

def ingest_opinions(conn: sqlite3.Connection, opinions: list[dict]) -> dict:
    """Ingest scraped opinions. For missing opinions, create new records.
    For existing opinions, add an archive source entry."""
    stats = {"new": 0, "source_added": 0, "already_have": 0, "errors": 0}

    for op in opinions:
        nd_cite = op["nd_cite"]

        # Check if opinion exists by citation
        existing = conn.execute(
            """SELECT o.id, o.source_reporter FROM opinions o
               JOIN citations c ON c.opinion_id = o.id
               WHERE c.citation = ?""",
            (nd_cite,),
        ).fetchone()

        if existing:
            oid = existing["id"]
            # Check if we already have an archive source for this opinion
            has_archive = conn.execute(
                "SELECT id FROM opinion_sources WHERE opinion_id = ? AND source_reporter = 'archive'",
                (oid,),
            ).fetchone()

            if has_archive:
                stats["already_have"] += 1
                continue

            # Add archive as an additional source
            conn.execute(
                """INSERT INTO opinion_sources
                   (opinion_id, source_reporter, source_path, text_length, is_primary,
                    added_at)
                   VALUES (?, 'archive', ?, ?, 0,
                    strftime('%Y-%m-%dT%H:%M:%S', 'now'))""",
                (oid, op.get("source_path", ""), len(op.get("text", ""))),
            )
            stats["source_added"] += 1
        else:
            # New opinion — create it
            text = op.get("text", "")
            if not text:
                stats["errors"] += 1
                continue

            case_name = op.get("case_name_index", "Unknown")
            date_filed = op.get("date_filed")
            if not date_filed:
                print(f"  SKIP {nd_cite}: no date parsed")
                stats["errors"] += 1
                continue

            author_raw = op.get("meta_author") or op.get("author_raw")
            author = _normalize_author(author_raw) if author_raw else None
            per_curiam = 1 if (author_raw and "per curiam" in author_raw.lower()) else 0

            # Build frontmatter + text
            full_text = f"---\ntitle: \"{case_name}\"\ncourt: \"North Dakota Supreme Court\"\ndate_filed: {date_filed}\ncitations:\n - \"{nd_cite}\"\n"
            for c in op.get("citations", []):
                if c != nd_cite:
                    full_text += f" - \"{c}\"\n"
            if op.get("docket"):
                full_text += f"docket_number: \"{op['docket']}\"\n"
            full_text += f"---\n\n{text}"

            cursor = conn.execute(
                """INSERT INTO opinions
                   (case_name, date_filed, source_reporter, source_path,
                    text_content, author, per_curiam, docket_number)
                   VALUES (?, ?, 'archive', ?, ?, ?, ?, ?)""",
                (case_name, date_filed, op.get("source_path", ""),
                 full_text, author, per_curiam, op.get("docket")),
            )
            new_id = cursor.lastrowid

            # Add citations
            conn.execute(
                "INSERT INTO citations (opinion_id, citation, reporter, is_primary) VALUES (?, ?, 'ND', 1)",
                (new_id, nd_cite),
            )
            for c in op.get("citations", []):
                if c != nd_cite:
                    reporter = "NW2d" if "N.W.2d" in c else "ND"
                    conn.execute(
                        "INSERT OR IGNORE INTO citations (opinion_id, citation, reporter, is_primary) VALUES (?, ?, ?, 0)",
                        (new_id, c, reporter),
                    )

            # Add opinion_sources
            conn.execute(
                """INSERT INTO opinion_sources
                   (opinion_id, source_reporter, source_path, text_length, is_primary,
                    added_at)
                   VALUES (?, 'archive', ?, ?, 1,
                    strftime('%Y-%m-%dT%H:%M:%S', 'now'))""",
                (new_id, op.get("source_path", ""), len(full_text)),
            )

            stats["new"] += 1
            print(f"  NEW: {nd_cite} — {case_name} (id={new_id})")

    conn.commit()
    return stats


# ── CLI ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape opinions from archive.ndcourts.gov")
    parser.add_argument("--year", type=int, help="Scrape a single year")
    parser.add_argument("--all", action="store_true", help="Scrape all years (1997–2019)")
    parser.add_argument("--ingest", action="store_true", help="Ingest into database")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--archive-dir", type=Path, default=ARCHIVE_DIR)
    args = parser.parse_args()

    if not args.year and not args.all:
        parser.error("Specify --year YEAR or --all")

    years = [args.year] if args.year else YEARS
    archive_dir = args.archive_dir
    archive_dir.mkdir(parents=True, exist_ok=True)

    client = httpx.Client(
        headers={"User-Agent": "ndcourts-mcp/1.0 (ND Supreme Court opinion database)"},
        timeout=30,
    )

    all_opinions = []
    for year in years:
        opinions = scrape_year(client, year, archive_dir)
        all_opinions.extend(opinions)

    client.close()

    print(f"\n{'='*60}")
    print(f"Total scraped: {len(all_opinions)} opinions")

    if args.ingest:
        conn = get_connection(args.db)
        create_schema(conn)
        stats = ingest_opinions(conn, all_opinions)
        years_str = f"{min(years)}-{max(years)}" if len(years) > 1 else str(years[0])
        log_provenance(conn, "scrape_archive",
                       source_paths=f"archive.ndcourts.gov ({years_str})",
                       rows_affected=stats["new"] + stats["source_added"],
                       notes=f"new={stats['new']}, sources_added={stats['source_added']}")
        conn.close()
        print(f"\nIngestion results:")
        print(f"  New opinions created: {stats['new']}")
        print(f"  Archive source added: {stats['source_added']}")
        print(f"  Already had archive:  {stats['already_have']}")
        print(f"  Errors:               {stats['errors']}")
    else:
        print("(dry run — use --ingest to add to database)")


if __name__ == "__main__":
    main()
