"""MCP server for North Dakota Supreme Court opinions."""

import os
import re
import sqlite3
import sys
from pathlib import Path

from fastmcp import FastMCP

from . import corpus, memo, proofread, research
from .db import DEFAULT_DB_PATH, get_connection

mcp = FastMCP(
    "ndlaw",
    instructions=(
        "North Dakota primary law. Opinions (1889–present): use lookup_opinion "
        "for citation-based retrieval, search_opinions for full-text search, and "
        "get_citing_opinions to find cases that cite a given opinion. Constitution, "
        "court rules, statutes (N.D.C.C.), and administrative code (where installed): "
        "use lookup_authority for the text of a provision (with as_of_date for the "
        "version in force on a given date), get_authority_history for its amendment "
        "history, and search_authority for full-text search across these sources."
    ),
)

DB_PATH = DEFAULT_DB_PATH

COURTLISTENER_BASE = "https://www.courtlistener.com"

# A subsection pinpoint trailing a court-rule citation, e.g. "§ 3(c)", "(c)",
# "subsec. 2" — used to tell the caller we returned the whole rule, not the cited
# subsection (rules are stored whole-rule).
_PINPOINT_RE = re.compile(r"\(\s*[0-9a-zA-Z]{1,4}\s*\)|§|\bsubsec|\bsubdiv", re.I)

# A trailing subsection pinpoint on a *court-rule* cite, to be stripped so the
# whole rule resolves: a "§ …"/"subsec."/"subdiv." clause, or a parenthesized
# "(c)" group, at the end of the string. Rule-only — N.D.C.C./const use "§" for
# the section identifier itself, so this must never run against those corpora.
_RULE_PINPOINT_TAIL_RE = re.compile(
    r"\s*(?:,\s*)?(?:(?:§|subsec\.?|subdiv\.?|subdivision)\s*[\w.()\-]*|\([0-9a-zA-Z]{1,4}\))\s*$",
    re.I,
)


def _strip_rule_pinpoint(citation: str) -> str:
    """Drop a trailing subsection pinpoint from a court-rule citation.

    "N.D. Sup. Ct. Admin. R. 22, § 3(c)" -> "N.D. Sup. Ct. Admin. R. 22";
    "N.D. Code Jud. Conduct canon 1, § 3(c)" -> "...canon 1" (the parser's
    prefix+number canonical would drop the "canon" word, so stripping the
    pinpoint off the *raw* cite and resolving that is what makes pinpoints work
    for every rule set, not just the clean "prefix number" ones)."""
    prev = None
    out = citation
    while out != prev:
        prev = out
        out = _RULE_PINPOINT_TAIL_RE.sub("", out).rstrip()
    return out


def _best_cite(conn, alias: str, spec: dict, citation: str) -> str:
    """The citation string to resolve a provision by: raw first, then fallbacks.

    Try the caller's raw citation first — ``corpus.resolve_cite_key`` matches it
    space-insensitively, which already handles the common forms and, crucially,
    any provision whose *stored* citation has idiosyncratic formatting (a 4th
    admin segment like ``10-01-01-01``, a stray space, …) that a regex-rebuilt
    canonical can't reproduce. On a miss, for court rules drop a trailing
    subsection pinpoint and retry (rules are stored whole-rule). Finally fall
    back to the parser's ``exact`` canonical, which rescues alias/word-order
    variants the raw form can't match ("AR 22", "Rule 56 NDRCivP"). Preferring
    canonical first would regress the raw/idiosyncratic class; raw first costs
    at most a couple of extra indexed lookups.
    """
    if corpus.resolve_cite_key(conn, alias, citation):
        return citation
    if spec.get("kind") == "court_rule":
        stripped = _strip_rule_pinpoint(citation)
        if stripped != citation and corpus.resolve_cite_key(conn, alias, stripped):
            return stripped
    exact = spec.get("exact")
    if exact and corpus.resolve_cite_key(conn, alias, exact):
        return exact
    return citation


# Map a normalize_authority() kind to a versioned-law corpus name (corpus.CORPORA).
KIND_TO_CORPUS = {
    "constitution": "const",
    "court_rule": "rule",
    "statute": "ndcc",
    "admin": "admin",
}


def _conn_with_corpora() -> sqlite3.Connection:
    """Opinions connection with every available primary-law corpus ATTACHed.

    Missing corpus DBs are skipped, so this works on a chambers install that
    has only some corpora (or none — then it behaves like get_connection)."""
    conn = get_connection(DB_PATH, read_only=True)
    try:
        corpus.attach_corpora(conn, read_only=True)
    except Exception:
        pass
    return conn


def _attached_corpora(conn: sqlite3.Connection) -> dict[str, str]:
    """Return {corpus_name: alias} for corpora currently attached to ``conn``."""
    present = {r["name"] for r in conn.execute("PRAGMA database_list")}
    return {
        name: meta["alias"]
        for name, meta in corpus.CORPORA.items()
        if meta["alias"] in present
    }


def _col(row, name):
    """Safely read a column that may be absent from a leaner SELECT."""
    try:
        return row[name]
    except (IndexError, KeyError):
        return None


def _best_url(row) -> dict:
    """Return the best available source URL, preferring the court's own site.

    ndcourts.gov (`opinion_url`) is the North Dakota courts' official copy and
    is preferred whenever present — *regardless of which source the text came
    from*. A 1997+ opinion whose text was sourced from Westlaw still links to
    its ndcourts.gov page, because the URL is stored independently of
    `source_reporter`. Falls back to the CourtListener cluster URL, fully
    qualified from the stored relative path. Returns {} if neither exists
    (e.g. pre-1997 opinions, where ndcourts.gov has no page).

    Shape: {"url": str, "url_source": "ndcourts.gov" | "courtlistener"}.
    """
    gov = _col(row, "opinion_url")
    if gov:
        return {"url": gov, "url_source": "ndcourts.gov"}
    cl = _col(row, "absolute_url")
    if cl:
        url = cl if cl.startswith("http") else COURTLISTENER_BASE + cl
        return {"url": url, "url_source": "courtlistener"}
    return {}


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
    for field in ("case_type", "highlight", "unanimous", "disposition"):
        try:
            val = row[field]
            if val is not None:
                result[field] = bool(val) if field == "unanimous" else val
        except (IndexError, KeyError):
            pass
    result.update(_best_url(row))
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
        **_best_url(row),
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
    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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

    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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

    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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

        other_cases, statutes, court_rules, constitution, regulations = (
            [], [], [], [], []
        )
        # Resolved in-corpus cases are deduped by opinion id: a case cited by
        # both its neutral and N.W. parallel is ONE authority, not two. The
        # canonical `cite` prefers the neutral form; the rest go in
        # `parallel_cites`. The subject opinion's own id is excluded (a case is
        # not an authority it cites).
        cases_by_oid: dict[int, dict] = {}
        cases_order: list[dict] = []
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
                    roid = resolved["id"]
                    if roid == row["id"]:
                        continue
                    d = cases_by_oid.get(roid)
                    if d is None:
                        d = {
                            "case_name": resolved["case_name"],
                            "date_filed": resolved["date_filed"],
                            "oid": roid,
                            "url": t["url"],
                            "_cites": [],
                        }
                        cases_by_oid[roid] = d
                        cases_order.append(d)
                    if t["normalized"] not in d["_cites"]:
                        d["_cites"].append(t["normalized"])
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

        # Finalize deduped cases: canonical cite (neutral preferred) + parallels.
        def _is_neutral(cite: str) -> bool:
            parts = cite.split()
            return len(parts) >= 3 and parts[1] == "ND" and parts[0].isdigit()

        cases = []
        for d in cases_order:
            cites = d.pop("_cites")
            neutral = [x for x in cites if _is_neutral(x)]
            canonical = neutral[0] if neutral else cites[0]
            d["cite"] = canonical
            d["parallel_cites"] = [x for x in cites if x != canonical]
            cases.append(d)

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

    conn = get_connection(DB_PATH, read_only=True)
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
            **_best_url(row),
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
    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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

    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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
    """Find opinions that cite/construe an N.D.C.C. section, court rule, or
    constitutional provision.

    Accepts forms like "14-09-06.2", "N.D.C.C. § 14-09-06.2", "chapter 28-32",
    "N.D.R.Crim.P. 12", "Rule 56 NDRCivP", or "N.D. Const. art. I, § 8".
    Returns the matched authority (or authorities, if the reference is
    ambiguous) and the opinions citing it, newest first. When the cited
    provision's corpus is installed, also returns the provision's own text.

    Args:
        authority: A statutory, court-rule, or constitutional reference.
        limit: Max opinions per matched authority (default 50, max 200).
    """
    limit = min(limit, 200)
    spec = research.normalize_authority(authority)

    conn = get_connection(DB_PATH, read_only=True)
    try:
        matched: list[dict] = []
        if spec["kind"] in ("constitution", "admin"):
            # Constitution and admin-code cites match text_citations by canonical
            # normalized string (jetcite's normalized form == the canonical
            # citation). Canonicalize via the corpus if installed so varied input
            # still matches; report the provision even if no opinion cites it.
            canonical = spec["exact"] or authority
            ckind = KIND_TO_CORPUS[spec["kind"]]
            ccorp = _conn_with_corpora()
            try:
                calias = _attached_corpora(ccorp).get(ckind)
                if calias:
                    prow = ccorp.execute(
                        f"SELECT citation FROM {calias}.provisions WHERE cite_key = ?",
                        (corpus.cite_key(authority),),
                    ).fetchone()
                    if prow:
                        canonical = prow["citation"]
            finally:
                ccorp.close()
            row = conn.execute(
                "SELECT normalized, url FROM text_citations WHERE normalized = ? LIMIT 1",
                (canonical,),
            ).fetchone()
            matched = [{"normalized": canonical, "url": row["url"] if row else None}]
        else:
            if not spec["token"]:
                return {"error": f"Couldn't parse a statute, court-rule, or constitutional reference from: {authority}"}
            # Prefer an exact canonical match; else token-boundary matches.
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

        # If the cited primary-law corpus is installed, attach the provision's
        # own text (point-in-time aware) so the caller sees what was construed.
        ckind = KIND_TO_CORPUS.get(spec["kind"])
        if ckind:
            ccorp = _conn_with_corpora()
            try:
                alias = _attached_corpora(ccorp).get(ckind)
                if alias:
                    prov = corpus.lookup_provision_version(
                        ccorp, alias, _best_cite(ccorp, alias, spec, authority))
                    if prov:
                        result["provision"] = {
                            "citation": prov["citation"],
                            "heading": prov["heading"],
                            "status": prov["status"],
                            "current_text": prov["text_content"],
                            "note": "Use lookup_authority(..., as_of_date=) for the version in force on a given date.",
                        }
            finally:
                ccorp.close()
        return result
    finally:
        conn.close()


@mcp.tool()
def lookup_authority(citation: str, as_of_date: str | None = None) -> dict:
    """Retrieve the text of a ND constitutional, statutory, court-rule, or
    administrative provision — optionally as it read on a specific date.

    Resolves citations like "N.D. Const. art. I, § 8", "N.D.C.C. § 12.1-20-03",
    "N.D.R.Civ.P. 56", or "N.D. Admin. Code § 75-02-01". When ``as_of_date`` is
    given (ISO ``YYYY-MM-DD``), returns the version in force on that date; this
    is what lets you read a statute "as the court applied it" in an older
    opinion. Omit ``as_of_date`` for the current text.

    Returns the provision text, heading, effective window, enacting/amending
    authority, source URL, and a count of opinions construing it. If the
    relevant corpus is not installed, says so.

    Args:
        citation: A constitutional, statutory, court-rule, or admin-code reference.
        as_of_date: Optional ISO date; the version in force then (default: current).
    """
    spec = research.normalize_authority(citation)
    ckind = KIND_TO_CORPUS.get(spec["kind"])
    if not ckind:
        return {"error": f"Couldn't recognize a ND primary-law citation in: {citation}"}

    conn = _conn_with_corpora()
    try:
        alias = _attached_corpora(conn).get(ckind)
        if not alias:
            return {
                "found": False,
                "citation": citation,
                "corpus": ckind,
                "error": f"The {corpus.CORPORA[ckind]['label']} corpus is not installed on this server.",
            }
        lookup_cite = _best_cite(conn, alias, spec, citation)
        row = corpus.lookup_provision_version(conn, alias, lookup_cite, as_of_date)
        warning = None
        if not row and as_of_date:
            # No captured version covers as_of_date. If the provision exists,
            # return its earliest captured version with a clear warning rather
            # than nothing — full historical text before that date may not yet
            # be captured (the amendment chronology is in get_authority_history).
            q = f"{alias}."
            stored_key = corpus.resolve_cite_key(conn, alias, lookup_cite)
            prov = conn.execute(
                f"SELECT id FROM {q}provisions WHERE cite_key = ?",
                (stored_key,),
            ).fetchone() if stored_key else None
            if prov:
                row = conn.execute(
                    f"SELECT p.citation, p.heading, p.status, v.* "
                    f"FROM {q}provisions p JOIN {q}provision_versions v "
                    f"  ON v.provision_id = p.id WHERE p.id = ? "
                    f"ORDER BY COALESCE(v.effective_start,'0000-01-01') ASC LIMIT 1",
                    (prov["id"],),
                ).fetchone()
                if row:
                    warning = (
                        f"No captured text is dated on or before {as_of_date}; "
                        f"returning the earliest captured version (effective "
                        f"{row['effective_start']}). Earlier text may exist but is "
                        f"not yet captured — see get_authority_history for the "
                        f"amendment chronology."
                    )
        if not row:
            asof = f" in force on {as_of_date}" if as_of_date else ""
            return {"found": False, "citation": citation, "corpus": ckind,
                    "error": f"No provision matching {citation!r}{asof}."}
        # cross-link: how many opinions construe this authority (jetcite's
        # normalized form equals the canonical citation).
        construing = conn.execute(
            "SELECT COUNT(DISTINCT opinion_id) AS n FROM text_citations WHERE normalized = ?",
            (row["citation"],),
        ).fetchone()["n"]
        result = {
            "found": True,
            "corpus": ckind,
            "citation": row["citation"],
            "heading": row["heading"],
            "status": row["status"],
            "as_of_date": as_of_date,
            "effective_start": row["effective_start"],
            "effective_end": row["effective_end"],
            "is_current": row["effective_end"] is None,
            "source_authority": row["source_authority"],
            "source_url": row["source_url"],
            "text": row["text_content"],
            "opinions_construing": construing,
        }
        if warning:
            result["warning"] = warning
        # Rules are stored whole-rule; subsection pinpoints are not separately
        # retrievable. If the caller asked for one, return the full rule but say
        # so rather than silently dropping the pinpoint. (Statutes/const use "§"
        # for the section itself, so only flag the court-rule corpus.)
        if ckind == "rule" and _PINPOINT_RE.search(citation):
            result["note"] = (
                "Subsection-level retrieval is not supported; returning the full "
                f"text of {row['citation']}. Read the relevant subsection within it."
            )
        return result
    finally:
        conn.close()


@mcp.tool()
def constitutional_amendments(
    date_from: str | None = None, date_to: str | None = None, limit: int = 200,
) -> dict:
    """List the chronology of amendments to the ND Constitution.

    Returns every amendment from ndconst.org's authoritative table (1889–present,
    ~167 amendments) with its effective date, election date, affected section(s),
    subject, and a link to the enacting session law. Optionally filter by
    effective-date range (ISO ``YYYY-MM-DD``). Note: pre-1996 amendments list the
    section numbers in effect at the time (the Constitution was renumbered in
    1996), so those do not map to current article/section citations.

    Args:
        date_from: Only amendments effective on/after this ISO date.
        date_to: Only amendments effective on/before this ISO date.
        limit: Max amendments to return (default 200).
    """
    conn = _conn_with_corpora()
    try:
        alias = _attached_corpora(conn).get("const")
        if not alias:
            return {"found": False,
                    "error": "The ND Constitution corpus is not installed on this server."}
        where = ["effective_date IS NOT NULL"]
        params: list = []
        if date_from:
            where.append("effective_date >= ?"); params.append(date_from)
        if date_to:
            where.append("effective_date <= ?"); params.append(date_to)
        params.append(min(limit, 500))
        rows = conn.execute(
            f"""SELECT DISTINCT amendment_number, effective_date, election_date,
                       affected, raw AS subject, source_url
                FROM {alias}.amendments
                WHERE {' AND '.join(where)}
                ORDER BY effective_date DESC, amendment_number LIMIT ?""",
            params,
        ).fetchall()
        return {
            "found": True,
            "date_from": date_from,
            "date_to": date_to,
            "count": len(rows),
            "amendments": [
                {
                    "amendment_number": r["amendment_number"],
                    "effective_date": r["effective_date"],
                    "election_date": r["election_date"],
                    "affected": r["affected"],
                    "subject": r["subject"],
                    "source_url": r["source_url"],
                }
                for r in rows
            ],
        }
    finally:
        conn.close()


@mcp.tool()
def get_authority_history(citation: str) -> dict:
    """Show the amendment history of a ND constitutional, statutory, court-rule,
    or administrative provision — every version with its effective dates and the
    authority that enacted or amended it.

    Use this to see how a provision changed over time, then call
    ``lookup_authority`` with a specific ``as_of_date`` to read any version in
    full. Version text is truncated here; full text comes from lookup_authority.

    Args:
        citation: A constitutional, statutory, court-rule, or admin-code reference.
    """
    spec = research.normalize_authority(citation)
    ckind = KIND_TO_CORPUS.get(spec["kind"])
    if not ckind:
        return {"error": f"Couldn't recognize a ND primary-law citation in: {citation}"}

    conn = _conn_with_corpora()
    try:
        alias = _attached_corpora(conn).get(ckind)
        if not alias:
            return {"found": False, "citation": citation, "corpus": ckind,
                    "error": f"The {corpus.CORPORA[ckind]['label']} corpus is not installed."}
        q = f"{alias}."
        stored_key = corpus.resolve_cite_key(conn, alias, _best_cite(conn, alias, spec, citation))
        prov = conn.execute(
            f"SELECT id, citation, heading, status FROM {q}provisions WHERE cite_key = ?",
            (stored_key,),
        ).fetchone() if stored_key else None
        if not prov:
            return {"found": False, "citation": citation, "corpus": ckind,
                    "error": f"No provision matching {citation!r}."}
        versions = conn.execute(
            f"""SELECT effective_start, effective_end, source_authority, source_url,
                       substr(text_content, 1, 240) AS excerpt, length(text_content) AS len
                FROM {q}provision_versions WHERE provision_id = ?
                ORDER BY COALESCE(effective_start, '0000-01-01')""",
            (prov["id"],),
        ).fetchall()
        # Amendment events — the full chronology, including amendments whose
        # prior full text has not yet been captured as a provision_version.
        amendments = conn.execute(
            f"""SELECT action, effective_date, raw_date, election_date, affected,
                       amendment_number, authority, source_url, raw
                FROM {q}amendments WHERE provision_id = ?
                ORDER BY COALESCE(effective_date, '0000-01-01')""",
            (prov["id"],),
        ).fetchall()
        result = {
            "found": True,
            "corpus": ckind,
            "citation": prov["citation"],
            "heading": prov["heading"],
            "status": prov["status"],
            "version_count": len(versions),
            "captured_versions": [
                {
                    "effective_start": v["effective_start"],
                    "effective_end": v["effective_end"],
                    "is_current": v["effective_end"] is None,
                    "source_authority": v["source_authority"],
                    "source_url": v["source_url"],
                    "excerpt": v["excerpt"] + ("…" if v["len"] > 240 else ""),
                }
                for v in versions
            ],
            "amendment_count": len(amendments),
            "amendments": [
                {
                    "amendment_number": a["amendment_number"],
                    "action": a["action"],
                    "effective_date": a["effective_date"],
                    "election_date": a["election_date"],
                    "affected": a["affected"],
                    "subject": a["raw"],
                    "authority": a["authority"],
                    "source_url": a["source_url"],
                }
                for a in amendments
            ],
        }
        if versions and not amendments:
            result["note"] = (
                "No amendment events recorded; the captured version is the text "
                "as published. (Amendment chronology may be incomplete for v1.)"
            )
        elif amendments:
            result["note"] = (
                "Amendment events list the chronology; full prior text is only "
                "available for captured_versions. Use lookup_authority(..., "
                "as_of_date=) to read a captured version."
            )
        return result
    finally:
        conn.close()


@mcp.tool()
def search_authority(
    query: str, corpus_name: str | None = None,
    as_of_date: str | None = None, limit: int = 20,
) -> dict:
    """Full-text search across ND primary law (Constitution, court rules,
    statutes, administrative code).

    Searches provision text and headings. By default returns the version
    currently in force; pass ``as_of_date`` (ISO ``YYYY-MM-DD``) to search the
    text as it read on that date. Restrict to one corpus with ``corpus_name``
    ('const', 'rule', 'ndcc', or 'admin').

    Args:
        query: Search terms (FTS5 syntax; e.g. 'search seizure', '"probable cause"').
        corpus_name: Optional corpus filter ('const' | 'rule' | 'ndcc' | 'admin').
        as_of_date: Optional ISO date; search text in force then (default: current).
        limit: Max results across all corpora (default 20, max 100).
    """
    limit = min(limit, 100)
    conn = _conn_with_corpora()
    try:
        attached = _attached_corpora(conn)
        if corpus_name:
            if corpus_name not in corpus.CORPORA:
                return {"error": f"Unknown corpus {corpus_name!r}; expected one of {list(corpus.CORPORA)}."}
            attached = {k: v for k, v in attached.items() if k == corpus_name}
        if not attached:
            return {"found": False, "query": query,
                    "error": "No matching primary-law corpus is installed on this server."}

        # Collect each corpus's best matches separately, then round-robin merge
        # so no single corpus crowds the others out of a small result set.
        per_corpus: dict[str, list[dict]] = {}
        for name, alias in attached.items():
            q = f"{alias}."
            if as_of_date is None:
                where = "v.id = p.current_version_id"
                params: tuple = (query, limit)
            else:
                where = ("COALESCE(v.effective_start,'0000-01-01') <= ? "
                         "AND COALESCE(v.effective_end, ?) >= ?")
                params = (query, as_of_date, corpus.OPEN_ENDED, as_of_date, limit)
            sql = (
                f"SELECT p.citation, p.heading, v.effective_start, v.effective_end, "
                f"       substr(v.text_content, 1, 280) AS excerpt "
                f"FROM {q}provisions_fts f "
                f"JOIN {q}provision_versions v ON v.id = f.rowid "
                f"JOIN {q}provisions p ON p.id = v.provision_id "
                f"WHERE f.provisions_fts MATCH ? AND {where} "
                f"ORDER BY rank LIMIT ?"
            )
            try:
                rows = conn.execute(sql, params).fetchall()
            except sqlite3.OperationalError as e:
                return {"error": f"search failed for corpus {name}: {e}"}
            per_corpus[name] = [{
                "corpus": name,
                "citation": r["citation"],
                "heading": r["heading"],
                "effective_start": r["effective_start"],
                "is_current": r["effective_end"] is None,
                "excerpt": r["excerpt"],
            } for r in rows]

        # Round-robin: take the i-th best from each corpus in turn until full.
        hits: list[dict] = []
        for i in range(max((len(v) for v in per_corpus.values()), default=0)):
            for name in attached:
                if i < len(per_corpus[name]):
                    hits.append(per_corpus[name][i])
            if len(hits) >= limit:
                break
        hits = hits[:limit]
        return {
            "found": bool(hits),
            "query": query,
            "as_of_date": as_of_date,
            "corpora_searched": list(attached),
            "count": len(hits),
            "results": hits,
        }
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
    conn = get_connection(DB_PATH, read_only=True)
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
    conn = get_connection(DB_PATH, read_only=True)
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
