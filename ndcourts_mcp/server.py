"""MCP server for North Dakota Supreme Court opinions."""

import os
import sqlite3
import sys
from pathlib import Path

from fastmcp import FastMCP

from . import memo, proofread, research
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
    for field in ("case_type", "highlight", "opinion_url", "unanimous", "disposition"):
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


def _citation_rows(conn, opinion_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT citation, reporter, is_primary FROM citations WHERE opinion_id = ?",
        (opinion_id,),
    ).fetchall()
    return [{"citation": r["citation"], "reporter": r["reporter"],
             "is_primary": r["is_primary"]} for r in rows]


def _resolve_opinion(conn, query: str):
    """Resolve a query to a single opinion row.

    Tries a citation match first (the query may embed a cite); falls back to
    case-name match. Returns (row, matched_by, candidates) where matched_by is
    'citation' | 'case_name' | None, and candidates is a list of summary dicts
    when a case-name query is ambiguous (row is None in that case)."""
    cite = proofread.extract_cite(query)
    if cite:
        row = conn.execute(
            """SELECT o.* FROM opinions o
               JOIN citations c ON c.opinion_id = o.id
               WHERE c.citation = ?""",
            (cite,),
        ).fetchone()
        if row:
            return row, "citation", []

    name = query.strip()
    exact = conn.execute(
        "SELECT * FROM opinions WHERE lower(case_name) = lower(?) ORDER BY date_filed",
        (name,),
    ).fetchall()
    if len(exact) == 1:
        return exact[0], "case_name", []
    if len(exact) > 1:
        return None, None, [_name_candidate(conn, r) for r in exact[:10]]

    like = conn.execute(
        "SELECT * FROM opinions WHERE case_name LIKE ? ORDER BY date_filed LIMIT 11",
        (f"%{name}%",),
    ).fetchall()
    if len(like) == 1:
        return like[0], "case_name", []
    if len(like) > 1:
        return None, None, [_name_candidate(conn, r) for r in like[:10]]

    return None, None, []


def _name_candidate(conn, row) -> dict:
    ordered, synthetic = proofread.order_citations(_citation_rows(conn, row["id"]))
    return {
        "id": row["id"],
        "case_name": row["case_name"],
        "date_filed": row["date_filed"],
        "citations": [r["citation"] for r in ordered] + synthetic,
    }


def _cite_payload(conn, row) -> dict:
    """Canonical-citation block shared by verify_citation / get_parallel_citations."""
    rows = _citation_rows(conn, row["id"])
    ordered, synthetic = proofread.order_citations(rows)
    return {
        "canonical_case_name": row["case_name"],
        "case_name_full": row["case_name_full"],
        "date_filed": row["date_filed"],
        "author": row["author"],
        "per_curiam": bool(row["per_curiam"]),
        "court": row["court"],
        "docket_number": row["docket_number"],
        "cites_redbook": [
            {"cite": r["citation"], "reporter": r["reporter"],
             "is_primary": bool(r["is_primary"])}
            for r in ordered
        ],
        "synthetic_cites": synthetic,
        "formatted": proofread.format_redbook(row["case_name"], ordered, row["date_filed"]),
        "absolute_url": row["absolute_url"],
    }


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


@mcp.tool()
def verify_citation(query: str, expected_case_name: str | None = None) -> dict:
    """Verify a citation or case name and return its canonical form.

    Confirms the case exists and returns the exact case name, filing date,
    authoring justice, and the full parallel-cite set in Redbook order, plus a
    ready-to-paste formatted citation. Catches wrong volume/page, wrong year,
    and name drift. If expected_case_name is supplied alongside a citation, the
    name as-written is compared to the canonical name and any drift is flagged.

    Args:
        query: A citation ("2024 ND 156", "585 N.W.2d 129") or a case name.
        expected_case_name: Optional — the case name as it appears in the draft,
            to check against the canonical name for drift.
    """
    conn = get_connection(DB_PATH)
    try:
        row, matched_by, candidates = _resolve_opinion(conn, query)
        if row is None:
            result = {"found": False, "query": query}
            if candidates:
                result["error"] = "Ambiguous — multiple opinions match."
                result["candidates"] = candidates
            else:
                result["error"] = f"No opinion found for: {query}"
            return result

        result = {"found": True, "matched_by": matched_by}
        result.update(_cite_payload(conn, row))

        if expected_case_name:
            result["expected_case_name"] = expected_case_name
            result["name_matches"] = proofread.names_match(
                expected_case_name, row["case_name"]
            )
            result["name_similarity"] = proofread.name_similarity(
                expected_case_name, row["case_name"]
            )
        return result
    finally:
        conn.close()


@mcp.tool()
def get_parallel_citations(citation: str) -> dict:
    """Return the complete parallel-cite set for a case, in Redbook order.

    Feed any one citation (or a case name) and get every known parallel cite so
    a draft's missing neutral or N.W. parallel can be auto-filled. Synthetic
    back-assigned [YYYY ND nnn] identifiers for pre-1997 opinions are returned
    separately and never folded into the formatted citation.

    Args:
        citation: Any citation ("44 N.W. 301", "1 N.D. 1") or a case name.
    """
    conn = get_connection(DB_PATH)
    try:
        row, _matched_by, candidates = _resolve_opinion(conn, citation)
        if row is None:
            result = {"found": False, "query": citation}
            if candidates:
                result["error"] = "Ambiguous — multiple opinions match."
                result["candidates"] = candidates
            else:
                result["error"] = f"No opinion found for: {citation}"
            return result
        result = {"found": True}
        result.update(_cite_payload(conn, row))
        return result
    finally:
        conn.close()


@mcp.tool()
def verify_quotation(citation: str, quote: str) -> dict:
    """Confirm a quoted passage appears verbatim in a case, with pinpoint ¶.

    Locates the quote in the opinion text. Differences in whitespace, curly vs.
    straight quotes, and dash style are treated as still-verbatim; dropped,
    changed, or inserted words are flagged with a word-level diff and the
    closest actual text. Returns the pinpoint paragraph (¶) when the opinion
    carries paragraph markers (generally 1997+ opinions).

    Args:
        citation: A citation or case name identifying the opinion.
        quote: The quoted passage attributed to the case.
    """
    conn = get_connection(DB_PATH)
    try:
        row, matched_by, candidates = _resolve_opinion(conn, citation)
        if row is None:
            result = {"found_opinion": False, "query": citation}
            if candidates:
                result["error"] = "Ambiguous — multiple opinions match."
                result["candidates"] = candidates
            else:
                result["error"] = f"No opinion found for: {citation}"
            return result

        located = proofread.locate_quote(row["text_content"], quote)
        result = {
            "found_opinion": True,
            "matched_by": matched_by,
            "case_name": row["case_name"],
            "primary_citation": proofread.primary_cite(_citation_rows(conn, row["id"])),
        }
        result.update(located)
        if located.get("paragraph") is None and "paragraph" in located:
            result["paragraph_note"] = (
                "No paragraph markers in this opinion (typical of pre-1997 "
                "text); pinpoint by ¶ is unavailable."
            )
        return result
    finally:
        conn.close()


@mcp.tool()
def get_pinpoint(
    citation: str,
    paragraph: int | None = None,
    quote: str | None = None,
) -> dict:
    """Resolve a pinpoint: paragraph number → its text, or quote → its ¶.

    Provide exactly one of `paragraph` or `quote`. With `paragraph`, returns
    that ¶'s text and a pinpoint cite. With `quote`, locates the passage and
    returns the ¶ it lives in (with verbatim status). Paragraph pinpoints
    require ¶ markers, present on most 1997+ opinions but not pre-1997 text.

    Args:
        citation: A citation or case name identifying the opinion.
        paragraph: Paragraph number to retrieve (e.g. 5 for ¶ 5).
        quote: A quoted passage whose paragraph should be located.
    """
    if (paragraph is None) == (quote is None):
        return {"error": "Provide exactly one of `paragraph` or `quote`."}

    conn = get_connection(DB_PATH)
    try:
        row, matched_by, candidates = _resolve_opinion(conn, citation)
        if row is None:
            result = {"found_opinion": False, "query": citation}
            if candidates:
                result["error"] = "Ambiguous — multiple opinions match."
                result["candidates"] = candidates
            else:
                result["error"] = f"No opinion found for: {citation}"
            return result

        text = row["text_content"]
        primary = proofread.primary_cite(_citation_rows(conn, row["id"]))
        base = {
            "found_opinion": True,
            "matched_by": matched_by,
            "case_name": row["case_name"],
            "primary_citation": primary,
        }

        if paragraph is not None:
            extracted = proofread.extract_paragraph(text, paragraph)
            if extracted is None:
                if not proofread.paragraph_markers(text):
                    base["error"] = (
                        "No paragraph markers in this opinion (typical of "
                        "pre-1997 text); cannot pinpoint by ¶."
                    )
                else:
                    base["error"] = f"Paragraph ¶{paragraph} not found."
                return base
            para_text, truncated = extracted
            base.update({
                "paragraph": paragraph,
                "pinpoint": f"{primary}, ¶ {paragraph}" if primary else None,
                "text": para_text,
                "truncated": truncated,
            })
            return base

        located = proofread.locate_quote(text, quote)
        base.update(located)
        para = located.get("paragraph")
        if para is not None and primary:
            base["pinpoint"] = f"{primary}, ¶ {para}"
        if para is not None:
            extracted = proofread.extract_paragraph(text, para)
            if extracted is not None:
                base["paragraph_text"], base["paragraph_truncated"] = extracted
        return base
    finally:
        conn.close()


def _scan_treatment(conn, cited_oid: int, scan_limit: int):
    """Scan opinions citing ``cited_oid`` for sentence-local treatment signals.

    Shared by check_treatment and detect_overruled_in_draft. Returns
    ``(total_citing, scanned, signal_counts, entries)`` where each entry has the
    citing case/cite/date, paragraph, citing context, and conservative signal.
    """
    total = conn.execute(
        "SELECT COUNT(*) AS n FROM cited_by WHERE cited_opinion_id = ?",
        (cited_oid,),
    ).fetchone()["n"]
    citing_rows = conn.execute(
        """SELECT o.id, o.case_name, o.date_filed, o.text_content,
                  cb.citation AS matched_citation
           FROM cited_by cb
           JOIN opinions o ON o.id = cb.citing_opinion_id
           WHERE cb.cited_opinion_id = ?
           ORDER BY o.date_filed DESC
           LIMIT ?""",
        (cited_oid, scan_limit),
    ).fetchall()

    entries = []
    counts = {memo.NEGATIVE: 0, memo.DISTINGUISHED: 0,
              memo.POSITIVE: 0, memo.NEUTRAL: 0}
    for r in citing_rows:
        ctx = memo.citing_context(r["text_content"], r["matched_citation"])
        context = ctx.get("context") if ctx.get("found") else None
        signal = memo.classify_treatment(context) if context else memo.NEUTRAL
        counts[signal] += 1
        entries.append({
            "citing_case": r["case_name"],
            "citing_citation": r["matched_citation"],
            "date_filed": r["date_filed"],
            "paragraph": ctx.get("paragraph"),
            "context": context,
            "signal": signal,
        })
    return total, len(citing_rows), counts, entries


@mcp.tool()
def check_treatment(citation: str, limit: int = 50, scan_limit: int = 300) -> dict:
    """Citator: how later opinions have treated a case (KeyCite/Shepard's-style).

    Aggregates opinions citing the target and, for each, returns the citing
    sentence, its paragraph, and a CONSERVATIVE, NON-AUTHORITATIVE treatment
    signal scanned from that sentence alone. Possible-negative and
    distinguished items are surfaced first so they are never truncated away.

    IMPORTANT: signals are heuristic — a citing sentence may use a treatment
    word about a different case. This is NOT a "still good law" verdict. Always
    read the returned sentence and the full citing opinion before relying on it.

    Args:
        citation: A citation or case name identifying the case to check.
        limit: Max citing entries to return (default 50, max 200).
        scan_limit: Max (most-recent) citing opinions to scan for signals
            (default 300) — counts are reported over the scanned set.
    """
    limit = min(limit, 200)
    conn = get_connection(DB_PATH)
    try:
        row, matched_by, candidates = _resolve_opinion(conn, citation)
        if row is None:
            result = {"found": False, "query": citation}
            if candidates:
                result["error"] = "Ambiguous — multiple opinions match."
                result["candidates"] = candidates
            else:
                result["error"] = f"No opinion found for: {citation}"
            return result

        total, scanned, counts, entries = _scan_treatment(conn, row["id"], scan_limit)

        # Stable: newest-first within each signal bucket, negatives surfaced first.
        entries.sort(key=lambda e: e["date_filed"] or "", reverse=True)
        entries.sort(key=lambda e: memo.SIGNAL_ORDER[e["signal"]])

        return {
            "found": True,
            "matched_by": matched_by,
            "case_name": row["case_name"],
            "primary_citation": proofread.primary_cite(_citation_rows(conn, row["id"])),
            "total_citing": total,
            "scanned": scanned,
            "signal_counts": counts,
            "citations": entries[:limit],
            "returned": min(limit, len(entries)),
            "note": (
                "Treatment signals are heuristic and sentence-local, NOT a "
                "still-good-law verdict. A citing sentence may use a treatment "
                "word about a different case. Read each sentence — and the full "
                "citing opinion — before relying on it. Possible-negative and "
                "distinguished items are listed first."
            ),
        }
    finally:
        conn.close()


@mcp.tool()
def get_cited_authorities(citation: str) -> dict:
    """Outbound authorities a case relies on, grouped by type.

    Maps the authority graph around a case: cited cases (in-corpus ND opinions
    resolved to name/date/oid; others with a source URL), statutes (N.D.C.C.),
    court rules, constitutional provisions, and regulations — each with an
    official-source link where available.

    Args:
        citation: A citation or case name identifying the opinion.
    """
    conn = get_connection(DB_PATH)
    try:
        row, matched_by, candidates = _resolve_opinion(conn, citation)
        if row is None:
            result = {"found": False, "query": citation}
            if candidates:
                result["error"] = "Ambiguous — multiple opinions match."
                result["candidates"] = candidates
            else:
                result["error"] = f"No opinion found for: {citation}"
            return result

        tcs = conn.execute(
            """SELECT normalized, cite_type, jurisdiction, raw_text, url
               FROM text_citations WHERE opinion_id = ?
               ORDER BY cite_type, jurisdiction, normalized""",
            (row["id"],),
        ).fetchall()

        cases, other_cases, statutes, court_rules, constitution, regulations = (
            [], [], [], [], [], []
        )
        for t in tcs:
            entry = {"cite": t["normalized"], "url": t["url"]}
            if t["cite_type"] == "case":
                resolved = conn.execute(
                    """SELECT o.id, o.case_name, o.date_filed
                       FROM citations c JOIN opinions o ON o.id = c.opinion_id
                       WHERE c.citation = ?""",
                    (t["normalized"],),
                ).fetchone()
                if resolved:
                    cases.append({
                        "cite": t["normalized"],
                        "case_name": resolved["case_name"],
                        "date_filed": resolved["date_filed"],
                        "oid": resolved["id"],
                        "url": t["url"],
                    })
                else:
                    other_cases.append({**entry, "jurisdiction": t["jurisdiction"]})
            elif t["cite_type"] == "statute":
                statutes.append(entry)
            elif t["cite_type"] == "court_rule":
                court_rules.append(entry)
            elif t["cite_type"] == "constitution":
                constitution.append(entry)
            elif t["cite_type"] == "regulation":
                regulations.append(entry)

        return {
            "found": True,
            "matched_by": matched_by,
            "case_name": row["case_name"],
            "primary_citation": proofread.primary_cite(_citation_rows(conn, row["id"])),
            "counts": {
                "in_corpus_cases": len(cases),
                "other_cases": len(other_cases),
                "statutes": len(statutes),
                "court_rules": len(court_rules),
                "constitution": len(constitution),
                "regulations": len(regulations),
            },
            "nd_cases": cases,
            "other_cases": other_cases,
            "statutes": statutes,
            "court_rules": court_rules,
            "constitution": constitution,
            "regulations": regulations,
        }
    finally:
        conn.close()


@mcp.tool()
def case_summary(citation: str) -> dict:
    """One-call bench-memo front matter for a case.

    Returns name, full caption, all parallel cites (Redbook-ordered; synthetic
    [YYYY ND nnn] separate), date, author, panel, voting record, disposition,
    paragraph count, syllabus points (pre-1953), and citation-graph counts.
    `disposition` and `syllabus_points` are DERIVED/heuristic — verify against
    the opinion.

    Args:
        citation: A citation or case name identifying the opinion.
    """
    import json as _json

    conn = get_connection(DB_PATH)
    try:
        row, matched_by, candidates = _resolve_opinion(conn, citation)
        if row is None:
            result = {"found": False, "query": citation}
            if candidates:
                result["error"] = "Ambiguous — multiple opinions match."
                result["candidates"] = candidates
            else:
                result["error"] = f"No opinion found for: {citation}"
            return result

        oid = row["id"]
        text = row["text_content"]
        cite_rows = _citation_rows(conn, oid)
        ordered, synthetic = proofread.order_citations(cite_rows)
        para_count = len(proofread.paragraph_markers(text))

        cited_out = conn.execute(
            "SELECT COUNT(*) AS n FROM cited_by WHERE citing_opinion_id = ?", (oid,)
        ).fetchone()["n"]
        cited_by_n = conn.execute(
            "SELECT COUNT(*) AS n FROM cited_by WHERE cited_opinion_id = ?", (oid,)
        ).fetchone()["n"]

        return {
            "found": True,
            "matched_by": matched_by,
            "case_name": row["case_name"],
            "case_name_full": row["case_name_full"],
            "date_filed": row["date_filed"],
            "author": row["author"],
            "per_curiam": bool(row["per_curiam"]),
            "court": row["court"],
            "docket_number": row["docket_number"],
            "case_type": row["case_type"],
            "cites_redbook": [
                {"cite": r["citation"], "reporter": r["reporter"],
                 "is_primary": bool(r["is_primary"])}
                for r in ordered
            ],
            "synthetic_cites": synthetic,
            "formatted": proofread.format_redbook(row["case_name"], ordered,
                                                  row["date_filed"]),
            "panel": _json.loads(row["all_justices"]) if row["all_justices"] else None,
            "voting_record": (_json.loads(row["voting_record"])
                              if row["voting_record"] else None),
            "unanimous": bool(row["unanimous"]) if row["unanimous"] is not None else None,
            "paragraph_count": para_count or None,
            "disposition": memo.extract_disposition(text),
            "syllabus_points": memo.extract_syllabus(text),
            "cited_by_count": cited_by_n,
            "cites_out_count": cited_out,
            "text_length": len(text),
            "absolute_url": row["absolute_url"],
            "derived_note": (
                "`disposition` and `syllabus_points` are heuristically extracted "
                "from the opinion text; verify before relying on them. Panel and "
                "voting data exist for 1997+ opinions only."
            ),
        }
    finally:
        conn.close()


@mcp.tool()
def get_subsequent_history(citation: str) -> dict:
    """Related opinions sharing the case's docket (rehearings, supplemental, etc.).

    Finds other opinions on the same docket number, ordered by date, with a
    relation hint. Docket-linking also surfaces companion opinions and same-
    docket duplicates, so this is a research aid — verify the relationship.

    Args:
        citation: A citation or case name identifying the opinion.
    """
    conn = get_connection(DB_PATH)
    try:
        row, matched_by, candidates = _resolve_opinion(conn, citation)
        if row is None:
            result = {"found": False, "query": citation}
            if candidates:
                result["error"] = "Ambiguous — multiple opinions match."
                result["candidates"] = candidates
            else:
                result["error"] = f"No opinion found for: {citation}"
            return result

        docket = (row["docket_number"] or "").strip()
        base = {
            "found": True,
            "matched_by": matched_by,
            "case_name": row["case_name"],
            "date_filed": row["date_filed"],
            "docket_number": docket or None,
        }
        if not docket:
            base["related"] = []
            base["note"] = "No docket number recorded; cannot link related opinions."
            return base

        related_rows = conn.execute(
            """SELECT id, case_name, date_filed FROM opinions
               WHERE docket_number = ? AND id != ?
               ORDER BY date_filed""",
            (docket, row["id"]),
        ).fetchall()

        target_date = row["date_filed"] or ""
        related = []
        for r in related_rows:
            d = r["date_filed"] or ""
            if d > target_date:
                hint = "later (rehearing / supplemental / remand?)"
            elif d < target_date:
                hint = "earlier (prior decision?)"
            else:
                hint = "same date (companion or duplicate?)"
            related.append({
                "oid": r["id"],
                "case_name": r["case_name"],
                "date_filed": r["date_filed"],
                "citations": _get_citations(conn, r["id"]),
                "relation_hint": hint,
            })

        base["related"] = related
        base["note"] = (
            "Linked by shared docket number. This also catches companion "
            "opinions and same-docket duplicates — confirm the actual "
            "relationship before citing as subsequent history."
        )
        return base
    finally:
        conn.close()


@mcp.tool()
def authoring_justice_on_issue(
    justice: str,
    issue: str,
    limit: int = 15,
) -> dict:
    """Opinions a justice has authored on an issue (predictive bench-memo signal).

    Full-text searches `issue` and filters to opinions authored by `justice`,
    newest first, with snippets. Reflects authored majority/lead opinions
    (the `author` field); separate writings are most fully attributed 1997+.

    Args:
        justice: Authoring justice's last name (e.g. "VandeWalle").
        issue: Search terms for the issue (supports AND/OR/NOT, quoted phrases).
        limit: Max results (default 15, max 50).
    """
    limit = min(limit, 50)
    conn = get_connection(DB_PATH)
    try:
        rows = conn.execute(
            """SELECT o.*, snippet(opinions_fts, 1, '>>>', '<<<', '...', 40) AS snippet
               FROM opinions_fts
               JOIN opinions o ON o.id = opinions_fts.rowid
               WHERE opinions_fts MATCH ? AND o.author LIKE ?
               ORDER BY rank LIMIT ?""",
            (issue, f"%{justice}%", limit),
        ).fetchall()

        total = conn.execute(
            """SELECT COUNT(*) AS n FROM opinions_fts
               JOIN opinions o ON o.id = opinions_fts.rowid
               WHERE opinions_fts MATCH ? AND o.author LIKE ?""",
            (issue, f"%{justice}%"),
        ).fetchone()["n"]

        results = []
        for r in rows:
            summary = _opinion_summary(r)
            summary["citations"] = _get_citations(conn, r["id"])
            summary["snippet"] = r["snippet"]
            results.append(summary)

        return {
            "justice": justice,
            "issue": issue,
            "total_authored_matching": total,
            "returned": len(results),
            "opinions": results,
            "note": (
                "Matches opinions where `author` contains the justice's name "
                "(authored majority/lead opinions). Separate concurrences/"
                "dissents are most fully attributed for 1997+."
            ),
        }
    finally:
        conn.close()


@mcp.tool()
def search_boolean(
    query: str,
    date_from: str | None = None,
    date_to: str | None = None,
    author: str | None = None,
    limit: int = 20,
) -> dict:
    """Westlaw-style Boolean / proximity search.

    Connectors: `&` (AND), `|` or `OR` (OR), `%` or `NOT` (BUT NOT), `/N`
    (within N words), `/s` (same sentence ≈ NEAR/20), `/p` (same paragraph ≈
    NEAR/50), `!` truncation (e.g. `negligen!` → negligen*), and "quoted
    phrases". Because FTS5 has no sentence/paragraph unit, /s and /p are
    token-distance approximations — the translated FTS query and any
    approximation notes are returned for transparency.

    Args:
        query: A Westlaw-style query (e.g. `warrant /s nighttime % consent`).
        date_from: Filter to opinions filed on/after this date (YYYY-MM-DD).
        date_to: Filter to opinions filed on/before this date (YYYY-MM-DD).
        author: Filter by authoring justice's last name.
        limit: Maximum results (default 20, max 50).
    """
    limit = min(limit, 50)
    fts, notes = research.translate_boolean(query)
    if not fts:
        return {"error": "Query is empty after translation.",
                "translated_query": fts, "notes": notes}

    conn = get_connection(DB_PATH)
    try:
        sql = """
            SELECT o.*, snippet(opinions_fts, 1, '>>>', '<<<', '...', 40) AS snippet
            FROM opinions_fts JOIN opinions o ON o.id = opinions_fts.rowid
            WHERE opinions_fts MATCH ?
        """
        params: list = [fts]
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

        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError as e:
            return {"error": f"FTS5 rejected the translated query: {e}",
                    "translated_query": fts, "notes": notes}

        results = []
        for row in rows:
            r = _opinion_summary(row)
            r["citations"] = _get_citations(conn, row["id"])
            r["snippet"] = row["snippet"]
            results.append(r)

        return {
            "query": query,
            "translated_query": fts,
            "notes": notes,
            "count": len(results),
            "results": results,
        }
    finally:
        conn.close()


@mcp.tool()
def search_faceted(
    query: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    author: str | None = None,
    case_type: str | None = None,
    disposition: str | None = None,
    has_dissent: bool | None = None,
    has_concurrence: bool | None = None,
    unanimous: bool | None = None,
    limit: int = 30,
) -> list[dict]:
    """Faceted opinion search: filter by metadata, optionally with full text.

    Any combination of facets may be supplied. With `query`, results are FTS
    relevance-ranked; otherwise newest first. Disposition is a partial match
    (e.g. "REVERSED" matches "REVERSED AND REMANDED"). Dissent/concurrence/
    unanimity derive from voting data present for 1997+ opinions only.

    Args:
        query: Optional full-text query (plain FTS5 syntax).
        date_from: Filed on/after (YYYY-MM-DD).
        date_to: Filed on/before (YYYY-MM-DD).
        author: Authoring justice's last name (partial).
        case_type: Case-type classification (partial).
        disposition: Disposition substring (e.g. "REVERSED", "AFFIRMED", "DISMISSED").
        has_dissent: Require (or exclude) a dissenting vote.
        has_concurrence: Require (or exclude) a concurring/separate writing.
        unanimous: Require (or exclude) a unanimous decision.
        limit: Maximum results (default 30, max 100).
    """
    limit = min(limit, 100)
    conn = get_connection(DB_PATH)
    try:
        params: list = []
        if query:
            sql = """
                SELECT o.*, snippet(opinions_fts, 1, '>>>', '<<<', '...', 40) AS snippet
                FROM opinions_fts JOIN opinions o ON o.id = opinions_fts.rowid
                WHERE opinions_fts MATCH ?
            """
            params.append(query)
        else:
            sql = "SELECT o.* FROM opinions o WHERE 1=1"

        if date_from:
            sql += " AND o.date_filed >= ?"
            params.append(date_from)
        if date_to:
            sql += " AND o.date_filed <= ?"
            params.append(date_to)
        if author:
            sql += " AND o.author LIKE ?"
            params.append(f"%{author}%")
        if case_type:
            sql += " AND o.case_type LIKE ?"
            params.append(f"%{case_type}%")
        if disposition:
            sql += " AND o.disposition LIKE ?"
            params.append(f"%{disposition.upper()}%")
        if has_dissent is not None:
            sql += (" AND o.voting_record LIKE '%dissent%'" if has_dissent
                    else " AND (o.voting_record IS NULL OR o.voting_record NOT LIKE '%dissent%')")
        if has_concurrence is not None:
            sql += (" AND o.voting_record LIKE '%concurring%'" if has_concurrence
                    else " AND (o.voting_record IS NULL OR o.voting_record NOT LIKE '%concurring%')")
        if unanimous is not None:
            sql += " AND o.unanimous = ?"
            params.append(1 if unanimous else 0)

        sql += " ORDER BY rank LIMIT ?" if query else " ORDER BY o.date_filed DESC LIMIT ?"
        params.append(limit)

        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError as e:
            return [{"error": f"Query rejected: {e}"}]

        results = []
        for row in rows:
            r = _opinion_summary(row)
            r["citations"] = _get_citations(conn, row["id"])
            try:
                if row["snippet"] is not None:
                    r["snippet"] = row["snippet"]
            except (IndexError, KeyError):
                pass
            results.append(r)
        return results
    finally:
        conn.close()


@mcp.tool()
def find_opinions_construing(authority: str, limit: int = 50) -> dict:
    """Find opinions that cite/construe an N.D.C.C. section or court rule.

    Accepts forms like "14-09-06.2", "N.D.C.C. § 14-09-06.2", "chapter 28-32",
    "N.D.R.Crim.P. 12", or "Rule 56 NDRCivP". Returns the matched authority
    (or authorities, if the reference is ambiguous) and the opinions citing it,
    newest first.

    Args:
        authority: A statutory or court-rule reference.
        limit: Max opinions per matched authority (default 50, max 200).
    """
    limit = min(limit, 200)
    spec = research.normalize_authority(authority)
    if not spec["token"]:
        return {"error": f"Couldn't parse a statute or court-rule reference from: {authority}"}

    conn = get_connection(DB_PATH)
    try:
        # Prefer an exact canonical match; else token-boundary matches.
        matched: list[dict] = []
        if spec["exact"]:
            row = conn.execute(
                "SELECT normalized, url FROM text_citations WHERE cite_type = ? AND normalized = ? LIMIT 1",
                (spec["kind"], spec["exact"]),
            ).fetchone()
            if row:
                matched = [{"normalized": row["normalized"], "url": row["url"]}]
        if not matched:
            cands = conn.execute(
                "SELECT DISTINCT normalized, url FROM text_citations "
                "WHERE cite_type = ? AND normalized LIKE ?",
                (spec["kind"], f"%{spec['token']}"),
            ).fetchall()
            matched = [
                {"normalized": c["normalized"], "url": c["url"]}
                for c in cands
                if research.authority_token_matches(c["normalized"], spec["token"])
            ]

        if not matched:
            return {"found": False, "authority": authority,
                    "parsed": spec,
                    "error": f"No opinions cite {spec['exact'] or spec['token']}."}

        groups = []
        for a in matched:
            ops = conn.execute(
                """SELECT DISTINCT o.id, o.case_name, o.date_filed
                   FROM text_citations tc JOIN opinions o ON o.id = tc.opinion_id
                   WHERE tc.normalized = ?
                   ORDER BY o.date_filed DESC LIMIT ?""",
                (a["normalized"], limit),
            ).fetchall()
            total = conn.execute(
                "SELECT COUNT(DISTINCT opinion_id) AS n FROM text_citations WHERE normalized = ?",
                (a["normalized"],),
            ).fetchone()["n"]
            groups.append({
                "authority": a["normalized"],
                "url": a["url"],
                "total_opinions": total,
                "returned": len(ops),
                "opinions": [
                    {"oid": o["id"], "case_name": o["case_name"],
                     "date_filed": o["date_filed"],
                     "citations": _get_citations(conn, o["id"])}
                    for o in ops
                ],
            })

        result = {"found": True, "authority": authority, "parsed": spec,
                  "matched_authorities": [g["authority"] for g in groups],
                  "results": groups}
        if len(groups) > 1:
            result["note"] = (
                "The reference matched multiple authorities (no rule-set/§ prefix "
                "given); each is listed separately."
            )
        return result
    finally:
        conn.close()


@mcp.tool()
def more_like_this(citation: str, limit: int = 10) -> list[dict]:
    """Find opinions doctrinally similar to a given case (hybrid ranking).

    Blends two signals: co-citation (sharing the same cited authorities) and
    keyword overlap (shared salient terms). Each result reports both sub-scores
    so the ranking is explainable.

    Args:
        citation: A citation or case name identifying the seed opinion.
        limit: Maximum related opinions (default 10, max 30).
    """
    limit = min(limit, 30)
    conn = get_connection(DB_PATH)
    try:
        row, _matched_by, candidates = _resolve_opinion(conn, citation)
        if row is None:
            err = {"error": (f"No opinion found for: {citation}" if not candidates
                             else "Ambiguous — multiple opinions match.")}
            if candidates:
                err["candidates"] = candidates
            return [err]

        oid = row["id"]

        cocite = conn.execute(
            """SELECT tc2.opinion_id AS oid, COUNT(*) AS shared
               FROM text_citations tc1
               JOIN text_citations tc2 ON tc2.normalized = tc1.normalized
               WHERE tc1.opinion_id = ? AND tc2.opinion_id != ?
               GROUP BY tc2.opinion_id HAVING shared >= 2
               ORDER BY shared DESC LIMIT 60""",
            (oid, oid),
        ).fetchall()
        cocite_map = {r["oid"]: r["shared"] for r in cocite}

        kw_map: dict[int, float] = {}
        terms = research.salient_terms(row["text_content"], 12)
        if terms:
            fts = " OR ".join(f'"{t}"' for t in terms)
            try:
                kw_rows = conn.execute(
                    """SELECT opinions_fts.rowid AS oid, rank
                       FROM opinions_fts WHERE opinions_fts MATCH ?
                       ORDER BY rank LIMIT 80""",
                    (fts,),
                ).fetchall()
                for r in kw_rows:
                    if r["oid"] != oid:
                        kw_map[r["oid"]] = -float(r["rank"])  # higher = better
            except sqlite3.OperationalError:
                pass

        cands = set(cocite_map) | set(kw_map)
        if not cands:
            return []
        max_shared = max(cocite_map.values()) if cocite_map else 1
        kw_vals = list(kw_map.values())
        kw_lo, kw_hi = (min(kw_vals), max(kw_vals)) if kw_vals else (0.0, 1.0)
        kw_span = (kw_hi - kw_lo) or 1.0

        scored = []
        for cid in cands:
            shared = cocite_map.get(cid, 0)
            n_cite = shared / max_shared
            n_kw = ((kw_map[cid] - kw_lo) / kw_span) if cid in kw_map else 0.0
            scored.append((0.5 * n_cite + 0.5 * n_kw, shared, n_kw, cid))
        scored.sort(reverse=True)

        results = []
        for score, shared, n_kw, cid in scored[:limit]:
            crow = conn.execute(
                "SELECT id, case_name, date_filed FROM opinions WHERE id = ?", (cid,)
            ).fetchone()
            results.append({
                "oid": cid,
                "case_name": crow["case_name"],
                "date_filed": crow["date_filed"],
                "citations": _get_citations(conn, cid),
                "shared_authorities": shared,
                "keyword_score": round(n_kw, 3),
                "score": round(score, 3),
            })
        return results
    finally:
        conn.close()


@mcp.tool()
def detect_overruled_in_draft(
    draft_text: str,
    scan_limit: int = 200,
    max_cases: int = 60,
) -> dict:
    """Proofreading pass: flag cited cases that later opinions may have
    overruled, superseded, abrogated, or distinguished.

    Extracts every ND / N.W. / N.D. case citation in the draft, resolves each
    to a corpus opinion, and runs it through the citator. Cases with a possible-
    negative or distinguished signal are flagged with the citing context for
    human verification; the rest are reported as clear.

    IMPORTANT (same caution as the citator): signals are heuristic and
    sentence-local, NOT a "still good law" verdict. ALWAYS read each flagged
    entry — and the full citing opinion — before relying on it. Citations that
    don't resolve to a corpus opinion (foreign/federal cases, or typos) are
    listed under `unresolved` and were NOT checked; absence of a flag is not
    assurance a case is good law.

    Args:
        draft_text: The text of the draft opinion or memo.
        scan_limit: Max citing opinions to scan per cited case (default 200).
        max_cases: Max distinct cited cases to check (default 60).
    """
    conn = get_connection(DB_PATH)
    try:
        cites = research.extract_case_cites(draft_text)
        resolved: dict[int, str] = {}
        unresolved: list[str] = []
        for c in cites:
            r = conn.execute(
                "SELECT opinion_id FROM citations WHERE citation = ?", (c,)
            ).fetchone()
            if r:
                resolved.setdefault(r["opinion_id"], c)
            else:
                unresolved.append(c)

        oids = list(resolved)[:max_cases]
        flagged, clear = [], []
        for oid in oids:
            total, scanned, counts, entries = _scan_treatment(conn, oid, scan_limit)
            neg = [e for e in entries
                   if e["signal"] in (memo.NEGATIVE, memo.DISTINGUISHED)]
            crow = conn.execute(
                "SELECT case_name FROM opinions WHERE id = ?", (oid,)
            ).fetchone()
            item = {
                "case_name": crow["case_name"],
                "cited_as": resolved[oid],
                "primary_citation": proofread.primary_cite(_citation_rows(conn, oid)),
                "oid": oid,
                "total_citing": total,
                "scanned": scanned,
                "signal_counts": counts,
            }
            if neg:
                neg.sort(key=lambda e: e["date_filed"] or "", reverse=True)
                neg.sort(key=lambda e: memo.SIGNAL_ORDER[e["signal"]])
                item["treatment_entries"] = neg
                flagged.append(item)
            else:
                clear.append(item)

        flagged.sort(key=lambda i: i["signal_counts"][memo.NEGATIVE], reverse=True)

        return {
            "cases_cited": len(resolved),
            "checked": len(oids),
            "flagged_count": len(flagged),
            "flagged": flagged,
            "clear": clear,
            "unresolved": unresolved,
            "truncated": len(resolved) > max_cases,
            "note": (
                "Heuristic proofreading aid, NOT a still-good-law verdict. "
                "Treatment signals are sentence-local and a citing sentence may "
                "use a treatment word about a different case — ALWAYS read each "
                "flagged entry and the full citing opinion. `unresolved` cites "
                "(foreign/federal or not in the corpus) were NOT checked, and an "
                "absent flag is not assurance a case remains good law."
            ),
        }
    finally:
        conn.close()


def main():
    """Run the MCP server.

    Defaults to stdio (how local MCP clients launch the server as a
    subprocess — they pass no env, so this path is unchanged). For a
    remote/team deployment set:

      NDCOURTS_TRANSPORT=http   serve Streamable HTTP (or `sse`)
      NDCOURTS_HOST=127.0.0.1   bind address (default localhost-only;
                                front it with a TLS+auth reverse proxy)
      NDCOURTS_PORT=8000        bind port

    The server exposes read-only tools; auth/TLS belong in the proxy.
    """
    transport = os.environ.get("NDCOURTS_TRANSPORT", "stdio").lower()
    if transport in ("http", "streamable-http", "sse"):
        norm = "sse" if transport == "sse" else "http"
        host = os.environ.get("NDCOURTS_HOST", "127.0.0.1")
        port = int(os.environ.get("NDCOURTS_PORT", "8000"))
        print(
            f"ndcourts-mcp: serving {norm} on {host}:{port} "
            "(front with a TLS+auth reverse proxy; tools are read-only)",
            file=sys.stderr,
        )
        mcp.run(transport=norm, host=host, port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
