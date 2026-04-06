"""MCP server for North Dakota Supreme Court opinions."""

from pathlib import Path

from fastmcp import FastMCP

from .db import DEFAULT_DB_PATH, get_connection

mcp = FastMCP(
    "ndcourts",
    instructions=(
        "North Dakota Supreme Court opinion database (1889–present). "
        "Use lookup_opinion for citation-based retrieval, search_opinions for "
        "full-text search, and get_citing_opinions to find cases that cite a given opinion."
    ),
)

DB_PATH = DEFAULT_DB_PATH


def _opinion_summary(row) -> dict:
    """Format an opinion row as a summary dict (no full text)."""
    result = {
        "id": row["id"],
        "case_name": row["case_name"],
        "case_name_full": row["case_name_full"],
        "date_filed": row["date_filed"],
        "author": row["author"],
        "per_curiam": bool(row["per_curiam"]),
        "docket_number": row["docket_number"],
        "judges": row["judges"],
        "court": row["court"],
    }
    # Include enriched fields when available
    for field in ("case_type", "highlight", "opinion_url", "unanimous"):
        try:
            val = row[field]
            if val is not None:
                result[field] = bool(val) if field == "unanimous" else val
        except (IndexError, KeyError):
            pass
    return result


def _get_citations(conn, opinion_id: int) -> list[str]:
    rows = conn.execute(
        "SELECT citation FROM citations WHERE opinion_id = ? ORDER BY is_primary DESC",
        (opinion_id,),
    ).fetchall()
    return [r["citation"] for r in rows]


@mcp.tool()
def lookup_opinion(citation: str, include_text: bool = False, text_limit: int = 5000) -> dict:
    """Look up an opinion by any citation (neutral cite, N.W.2d, N.W., etc.).

    Returns metadata and all known citations. Text is excluded by default
    to keep responses manageable — use include_text=True for the first
    text_limit characters, or get_opinion_text() to read in chunks.

    Args:
        citation: A legal citation like "2024 ND 156", "585 N.W.2d 129", etc.
        include_text: Include opinion text in the response (default False).
        text_limit: Max characters of text to include (default 5000). Use get_opinion_text for full text.
    """
    conn = get_connection(DB_PATH)
    try:
        row = conn.execute(
            """SELECT o.* FROM opinions o
               JOIN citations c ON c.opinion_id = o.id
               WHERE c.citation = ?""",
            (citation.strip(),),
        ).fetchone()

        if not row:
            return {"error": f"No opinion found for citation: {citation}"}

        result = _opinion_summary(row)
        result["citations"] = _get_citations(conn, row["id"])
        result["absolute_url"] = row["absolute_url"]
        result["text_length"] = len(row["text_content"])

        if include_text:
            text = row["text_content"]
            if len(text) > text_limit:
                result["text"] = text[:text_limit]
                result["text_truncated"] = True
                result["text_remaining"] = len(text) - text_limit
            else:
                result["text"] = text
                result["text_truncated"] = False

        return result
    finally:
        conn.close()


@mcp.tool()
def get_opinion_text(citation: str, offset: int = 0, limit: int = 10000) -> dict:
    """Read opinion text in chunks.

    Use this to read long opinions in manageable pieces. Start with offset=0
    and advance by the limit to paginate through the text.

    Args:
        citation: A legal citation like "2024 ND 156".
        offset: Character offset to start reading from (default 0).
        limit: Maximum characters to return (default 10000, max 50000).
    """
    limit = min(limit, 50000)
    conn = get_connection(DB_PATH)
    try:
        row = conn.execute(
            """SELECT o.text_content FROM opinions o
               JOIN citations c ON c.opinion_id = o.id
               WHERE c.citation = ?""",
            (citation.strip(),),
        ).fetchone()

        if not row:
            return {"error": f"No opinion found for citation: {citation}"}

        text = row["text_content"]
        chunk = text[offset : offset + limit]

        return {
            "citation": citation,
            "total_length": len(text),
            "offset": offset,
            "chunk_length": len(chunk),
            "has_more": offset + limit < len(text),
            "text": chunk,
        }
    finally:
        conn.close()


@mcp.tool()
def search_opinions(
    query: str,
    date_from: str | None = None,
    date_to: str | None = None,
    author: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Full-text search across all opinions.

    Returns matching opinions ranked by relevance with snippets.
    Use this to find opinions on a topic, legal issue, or factual pattern.

    Args:
        query: Search terms (supports AND, OR, NOT, quoted phrases).
        date_from: Filter to opinions filed on or after this date (YYYY-MM-DD).
        date_to: Filter to opinions filed on or before this date (YYYY-MM-DD).
        author: Filter by authoring justice's last name.
        limit: Maximum results to return (default 20, max 50).
    """
    limit = min(limit, 50)
    conn = get_connection(DB_PATH)
    try:
        sql = """
            SELECT o.*, snippet(opinions_fts, 1, '>>>', '<<<', '...', 40) as snippet,
                   rank
            FROM opinions_fts
            JOIN opinions o ON o.id = opinions_fts.rowid
            WHERE opinions_fts MATCH ?
        """
        params: list = [query]

        if date_from:
            sql += " AND o.date_filed >= ?"
            params.append(date_from)
        if date_to:
            sql += " AND o.date_filed <= ?"
            params.append(date_to)
        if author:
            sql += " AND o.author LIKE ?"
            params.append(f"%{author}%")

        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)

        rows = conn.execute(sql, params).fetchall()

        results = []
        for row in rows:
            result = _opinion_summary(row)
            result["citations"] = _get_citations(conn, row["id"])
            result["snippet"] = row["snippet"]
            results.append(result)

        return results
    finally:
        conn.close()



@mcp.tool()
def list_opinions_by_date(
    date_from: str,
    date_to: str,
    author: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List opinions filed within a date range.

    Returns opinions in reverse chronological order.

    Args:
        date_from: Start date (YYYY-MM-DD).
        date_to: End date (YYYY-MM-DD).
        author: Optional filter by authoring justice's last name.
        limit: Maximum results (default 50, max 200).
    """
    limit = min(limit, 200)
    conn = get_connection(DB_PATH)
    try:
        sql = """SELECT * FROM opinions
                 WHERE date_filed >= ? AND date_filed <= ?"""
        params: list = [date_from, date_to]

        if author:
            sql += " AND author LIKE ?"
            params.append(f"%{author}%")

        sql += " ORDER BY date_filed DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(sql, params).fetchall()

        results = []
        for row in rows:
            result = _opinion_summary(row)
            result["citations"] = _get_citations(conn, row["id"])
            results.append(result)

        return results
    finally:
        conn.close()


@mcp.tool()
def get_database_stats() -> dict:
    """Get summary statistics about the opinion database.

    Returns counts, date range, and top authors.
    """
    conn = get_connection(DB_PATH)
    try:
        total = conn.execute("SELECT COUNT(*) as n FROM opinions").fetchone()["n"]
        date_range = conn.execute(
            "SELECT MIN(date_filed) as earliest, MAX(date_filed) as latest FROM opinions"
        ).fetchone()
        citations_count = conn.execute(
            "SELECT COUNT(*) as n FROM citations"
        ).fetchone()["n"]

        top_authors = conn.execute(
            """SELECT author, COUNT(*) as n FROM opinions
               WHERE author IS NOT NULL
               GROUP BY author ORDER BY n DESC LIMIT 15"""
        ).fetchall()

        by_decade = conn.execute(
            """SELECT (CAST(substr(date_filed, 1, 3) AS INTEGER) * 10) || '0s' as decade,
                      COUNT(*) as n
               FROM opinions
               GROUP BY decade ORDER BY decade"""
        ).fetchall()

        # Source breakdown
        by_source = conn.execute(
            """SELECT source_reporter, COUNT(*) as n FROM opinions
               GROUP BY source_reporter ORDER BY n DESC"""
        ).fetchall()

        # Correction count
        corrections = conn.execute(
            "SELECT COUNT(*) as n FROM changelog"
        ).fetchone()["n"]

        # Data freshness from provenance
        last_runs = conn.execute(
            """SELECT operation, timestamp, rows_affected, notes
               FROM provenance ORDER BY timestamp DESC LIMIT 5"""
        ).fetchall()

        # Quality summary
        quality = conn.execute(
            """SELECT AVG(overall_score) as avg_score,
                      MIN(overall_score) as min_score,
                      MAX(overall_score) as max_score
               FROM quality_scores"""
        ).fetchone()

        # Cited-by count
        cited_by_count = conn.execute(
            "SELECT COUNT(*) as n FROM cited_by"
        ).fetchone()["n"]

        return {
            "total_opinions": total,
            "total_citations": citations_count,
            "cited_by_links": cited_by_count,
            "earliest": date_range["earliest"],
            "latest": date_range["latest"],
            "top_authors": [
                {"author": r["author"], "count": r["n"]} for r in top_authors
            ],
            "by_decade": [
                {"decade": r["decade"], "count": r["n"]} for r in by_decade
            ],
            "by_source": [
                {"source": r["source_reporter"], "count": r["n"]} for r in by_source
            ],
            "corrections_applied": corrections,
            "quality": {
                "avg_score": round(quality["avg_score"], 1) if quality["avg_score"] else None,
                "min_score": quality["min_score"],
                "max_score": quality["max_score"],
            } if quality else None,
            "recent_pipeline_runs": [
                {"operation": r["operation"], "timestamp": r["timestamp"],
                 "rows_affected": r["rows_affected"], "notes": r["notes"]}
                for r in last_runs
            ],
        }
    finally:
        conn.close()


@mcp.tool()
def justice_info(
    justice: str,
    citation: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict:
    """Get justice information — voting record for a specific case, or
    aggregate statistics across cases.

    If citation is provided, returns the voting record for that opinion.
    Otherwise, returns aggregate stats (authorship count, dissent rate, etc.)
    for the justice across all cases (optionally filtered by date range).

    Only covers opinions from 1997–present (neutral-cite era with voting data).

    Args:
        justice: Justice's last name (e.g., "Tufte", "Crothers").
        citation: Optional citation for a specific opinion's voting record.
        date_from: Optional start date (YYYY-MM-DD) for aggregate stats.
        date_to: Optional end date (YYYY-MM-DD) for aggregate stats.
    """
    import json as _json

    conn = get_connection(DB_PATH)
    try:
        # Single-opinion voting record
        if citation:
            row = conn.execute(
                """SELECT o.case_name, o.date_filed, o.author, o.voting_record,
                          o.all_justices, o.unanimous
                   FROM opinions o
                   JOIN citations c ON c.opinion_id = o.id
                   WHERE c.citation = ?""",
                (citation.strip(),),
            ).fetchone()

            if not row:
                return {"error": f"No opinion found for citation: {citation}"}

            return {
                "citation": citation,
                "case_name": row["case_name"],
                "date_filed": row["date_filed"],
                "author": row["author"],
                "unanimous": bool(row["unanimous"]) if row["unanimous"] is not None else None,
                "justices": _json.loads(row["all_justices"]) if row["all_justices"] else None,
                "voting_record": _json.loads(row["voting_record"]) if row["voting_record"] else None,
            }

        # Aggregate stats
        sql = """SELECT voting_record, author, date_filed FROM opinions
                 WHERE all_justices LIKE ?"""
        params: list = [f"%{justice}%"]

        if date_from:
            sql += " AND date_filed >= ?"
            params.append(date_from)
        if date_to:
            sql += " AND date_filed <= ?"
            params.append(date_to)

        rows = conn.execute(sql, params).fetchall()

        total = 0
        authored = 0
        majority = 0
        dissent = 0
        concurring = 0
        separate = 0

        for row in rows:
            vr = _json.loads(row["voting_record"]) if row["voting_record"] else {}
            vote = None
            for name, v in vr.items():
                if name.lower() == justice.lower():
                    vote = v
                    break
            if vote is None:
                continue
            total += 1
            if vote == "majority":
                majority += 1
            elif vote == "dissent":
                dissent += 1
            elif vote == "concurring":
                concurring += 1
            elif vote == "separate":
                separate += 1
            if row["author"] and row["author"].lower() == justice.lower():
                authored += 1

        return {
            "justice": justice,
            "cases_participated": total,
            "authored": authored,
            "majority": majority,
            "dissent": dissent,
            "concurring": concurring,
            "separate": separate,
            "dissent_rate": round(dissent / total, 3) if total else 0,
        }
    finally:
        conn.close()


@mcp.tool()
def search_by_case_type(
    case_type: str,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 30,
) -> list[dict]:
    """Search opinions by case type classification.

    Case types include values like 'Appeal - Criminal - Misc. Felony',
    'Appeal - Civil - Constitutional Law', 'Original Jurisdiction', etc.
    Partial matches are supported.

    Args:
        case_type: Case type to search for (partial match, case-insensitive).
        date_from: Optional start date (YYYY-MM-DD).
        date_to: Optional end date (YYYY-MM-DD).
        limit: Maximum results (default 30, max 100).
    """
    limit = min(limit, 100)
    conn = get_connection(DB_PATH)
    try:
        sql = "SELECT * FROM opinions WHERE case_type LIKE ?"
        params: list = [f"%{case_type}%"]

        if date_from:
            sql += " AND date_filed >= ?"
            params.append(date_from)
        if date_to:
            sql += " AND date_filed <= ?"
            params.append(date_to)

        sql += " ORDER BY date_filed DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(sql, params).fetchall()
        results = []
        for row in rows:
            result = _opinion_summary(row)
            result["citations"] = _get_citations(conn, row["id"])
            results.append(result)
        return results
    finally:
        conn.close()


@mcp.tool()
def get_citing_opinions(citation: str, limit: int = 20) -> list[dict]:
    """Find opinions that cite a given opinion.

    Returns opinions that reference the given citation in their text,
    ordered by date (newest first). Requires citation extraction to have
    been run (python -m ndcourts_mcp.cite_extract).

    Args:
        citation: A legal citation like "2024 ND 156" or "585 N.W.2d 129".
        limit: Maximum results (default 20, max 100).
    """
    limit = min(limit, 100)
    conn = get_connection(DB_PATH)
    try:
        # Find the cited opinion
        row = conn.execute(
            "SELECT opinion_id FROM citations WHERE citation = ?", (citation,)
        ).fetchone()
        if not row:
            return {"error": f"No opinion found for citation: {citation}"}
        cited_id = row["opinion_id"]

        # Get citing opinions via cited_by
        citing_rows = conn.execute(
            """SELECT o.*, cb.citation as matched_citation
               FROM cited_by cb
               JOIN opinions o ON o.id = cb.citing_opinion_id
               WHERE cb.cited_opinion_id = ?
               ORDER BY o.date_filed DESC
               LIMIT ?""",
            (cited_id, limit),
        ).fetchall()

        results = []
        for r in citing_rows:
            result = _opinion_summary(r)
            result["citations"] = _get_citations(conn, r["id"])
            result["matched_citation"] = r["matched_citation"]
            results.append(result)

        return results
    finally:
        conn.close()


def main():
    mcp.run()


if __name__ == "__main__":
    main()
