"""Opinion browser — FastAPI backend serving REST API + static HTML."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from .db import get_connection
from .justices import KNOWN_LAST_NAMES

app = FastAPI(title="ND Courts Opinion Browser")

STATIC_DIR = Path(__file__).parent / "static"

# Known surrogates / special author values that aren't "bad"
SURROGATE_AUTHORS = {"Per Curiam", "per curiam", "Per curiam"}

# Locally confirmed authors (supplements KNOWN_LAST_NAMES)
CONFIRMED_AUTHORS_PATH = Path(__file__).parent.parent / "confirmed-authors.json"


def _load_confirmed_authors() -> set[str]:
    if CONFIRMED_AUTHORS_PATH.exists():
        return set(json.loads(CONFIRMED_AUTHORS_PATH.read_text()))
    return set()


def _save_confirmed_authors(names: set[str]) -> None:
    CONFIRMED_AUTHORS_PATH.write_text(json.dumps(sorted(names), indent=2) + "\n")


_confirmed_authors: set[str] = _load_confirmed_authors()


def _is_recognized_author(author: str | None) -> bool:
    if not author:
        return True
    if author in SURROGATE_AUTHORS:
        return True
    lower = author.strip().lower()
    return lower in KNOWN_LAST_NAMES or lower in _confirmed_authors


@contextmanager
def _db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


# ── Serve index.html ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC_DIR / "index.html").read_text()


# ── GET /api/facets ───────────────────────────────────────────────

_facets_cache: dict | None = None


@app.get("/api/facets")
def facets():
    global _facets_cache
    if _facets_cache:
        return _facets_cache

    with _db() as conn:
        authors = conn.execute(
            """SELECT author, COUNT(*) as n FROM opinions
               WHERE author IS NOT NULL AND author != ''
               GROUP BY author ORDER BY n DESC"""
        ).fetchall()

        case_types = conn.execute(
            """SELECT case_type, COUNT(*) as n FROM opinions
               WHERE case_type IS NOT NULL AND case_type != ''
               GROUP BY case_type ORDER BY n DESC"""
        ).fetchall()

        reporters = conn.execute(
            """SELECT source_reporter, COUNT(*) as n FROM opinions
               GROUP BY source_reporter ORDER BY n DESC"""
        ).fetchall()

        date_range = conn.execute(
            "SELECT MIN(date_filed) as min_date, MAX(date_filed) as max_date FROM opinions"
        ).fetchone()

    _facets_cache = {
        "authors": [
            {"name": r["author"], "count": r["n"],
             "recognized": _is_recognized_author(r["author"])}
            for r in authors
        ],
        "case_types": [
            {"name": r["case_type"], "count": r["n"]}
            for r in case_types
        ],
        "reporters": [
            {"name": r["source_reporter"], "count": r["n"]}
            for r in reporters
        ],
        "date_min": date_range["min_date"],
        "date_max": date_range["max_date"],
    }
    return _facets_cache


# ── GET /api/opinions ─────────────────────────────────────────────

@app.get("/api/opinions")
def list_opinions(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=50000),
    sort: str = Query("date_filed"),
    sort_dir: str = Query("desc"),
    search: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    author: str | None = None,
    case_type: str | None = None,
    source_reporter: str | None = None,
    has_notes: bool | None = None,
    bad_author: bool | None = None,
    no_author: bool | None = None,
    has_dupes: bool | None = None,
    citation: str | None = None,
    quality: str | None = None,
):
    # Whitelist sortable columns
    allowed_sort = {
        "date_filed", "case_name", "author", "primary_citation",
        "cite_nd", "cite_nd_old", "cite_nw",
        "case_type", "docket_number", "source_reporter", "per_curiam",
        "unanimous", "id", "cited_by_count", "quality_score",
    }
    if sort not in allowed_sort:
        sort = "date_filed"
    if sort_dir not in ("asc", "desc"):
        sort_dir = "desc"

    with _db() as conn:
        if search:
            return _search_opinions(
                conn, search, page, size, sort, sort_dir,
                date_from, date_to, author, case_type,
                source_reporter, has_notes, bad_author, no_author, has_dupes, citation,
                quality,
            )

        where_clauses: list[str] = []
        params: list = []

        if date_from:
            where_clauses.append("o.date_filed >= ?")
            params.append(date_from)
        if date_to:
            where_clauses.append("o.date_filed <= ?")
            params.append(date_to)
        if author:
            where_clauses.append("o.author = ?")
            params.append(author)
        if case_type:
            where_clauses.append("o.case_type = ?")
            params.append(case_type)
        if source_reporter:
            where_clauses.append("o.source_reporter = ?")
            params.append(source_reporter)
        if has_notes:
            where_clauses.append("o.notes IS NOT NULL AND o.notes != ''")
        if bad_author:
            known = KNOWN_LAST_NAMES | {a.lower() for a in SURROGATE_AUTHORS} | _confirmed_authors
            placeholders = ",".join("?" for _ in known)
            where_clauses.append(
                f"o.author IS NOT NULL AND o.author != '' "
                f"AND LOWER(TRIM(o.author)) NOT IN ({placeholders})"
            )
            params.extend(sorted(known))
        if no_author:
            where_clauses.append(
                "(o.author IS NULL OR o.author = '') AND o.per_curiam = 0"
            )
        if has_dupes:
            where_clauses.append(
                "EXISTS (SELECT 1 FROM opinions o2 WHERE o2.case_name = o.case_name "
                "AND o2.date_filed = o.date_filed AND o2.id != o.id)"
            )
        if citation:
            where_clauses.append(
                "EXISTS (SELECT 1 FROM citations ct WHERE ct.opinion_id = o.id AND ct.citation LIKE ?)"
            )
            params.append(f"%{citation}%")
        if quality == "low":
            where_clauses.append(
                "EXISTS (SELECT 1 FROM quality_scores qs WHERE qs.opinion_id = o.id AND qs.overall_score < 40)"
            )
        elif quality == "mid":
            where_clauses.append(
                "EXISTS (SELECT 1 FROM quality_scores qs WHERE qs.opinion_id = o.id AND qs.overall_score BETWEEN 40 AND 65)"
            )
        elif quality == "high":
            where_clauses.append(
                "EXISTS (SELECT 1 FROM quality_scores qs WHERE qs.opinion_id = o.id AND qs.overall_score > 65)"
            )

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        # Sort mapping — subquery aliases don't need table prefix
        if sort in ("primary_citation", "cite_nd", "cite_nd_old", "cite_nw", "cited_by_count", "quality_score"):
            order_col = sort
        else:
            order_col = f"o.{sort}"

        # Count
        count_sql = f"SELECT COUNT(*) as n FROM opinions o{where_sql}"
        total = conn.execute(count_sql, params).fetchone()["n"]

        # Data with citation columns via subqueries (avoids cartesian product)
        data_sql = f"""
            SELECT o.id, o.case_name, o.date_filed, o.author, o.case_type,
                   o.docket_number, o.source_reporter, o.per_curiam, o.unanimous,
                   o.notes,
                   (SELECT c.citation FROM citations c WHERE c.opinion_id = o.id AND c.is_primary = 1 LIMIT 1) as primary_citation,
                   (SELECT c.citation FROM citations c WHERE c.opinion_id = o.id AND c.reporter = 'ND' LIMIT 1) as cite_nd,
                   (SELECT c.citation FROM citations c WHERE c.opinion_id = o.id AND c.reporter = 'NDold' LIMIT 1) as cite_nd_old,
                   COALESCE(
                     (SELECT c.citation FROM citations c WHERE c.opinion_id = o.id AND c.reporter = 'NW2d' LIMIT 1),
                     (SELECT c.citation FROM citations c WHERE c.opinion_id = o.id AND c.reporter = 'NW' AND c.citation LIKE '%N.W.%' LIMIT 1)
                   ) as cite_nw,
                   (SELECT GROUP_CONCAT(c.citation, '; ') FROM citations c WHERE c.opinion_id = o.id AND c.citation NOT LIKE '%N.W.%' AND c.citation NOT LIKE '%ND %' AND c.citation NOT LIKE '%N.D. %') as cite_other,
                   (SELECT COUNT(*) FROM cited_by cb WHERE cb.cited_opinion_id = o.id) as cited_by_count,
                   (SELECT qs.overall_score FROM quality_scores qs WHERE qs.opinion_id = o.id) as quality_score
            FROM opinions o
            {where_sql}
            ORDER BY {order_col} {sort_dir}
            LIMIT ? OFFSET ?
        """
        params.extend([size, (page - 1) * size])
        rows = conn.execute(data_sql, params).fetchall()

    last_page = max(1, (total + size - 1) // size)
    return {
        "last_page": last_page,
        "total": total,
        "data": [_row_to_dict(r) for r in rows],
    }


def _fts5_sanitize(query: str) -> str:
    """Escape a user search string for FTS5 MATCH.

    Wrap each whitespace-delimited token in double quotes so that
    apostrophes, hyphens, and other FTS5 meta-characters are treated
    as literals.  Double-quote characters inside tokens are doubled
    per FTS5 escaping rules.
    """
    tokens = query.split()
    return " ".join('"' + t.replace('"', '""') + '"' for t in tokens)


def _search_opinions(
    conn, search, page, size, sort, sort_dir,
    date_from, date_to, author, case_type,
    source_reporter, has_notes, bad_author, no_author, has_dupes, citation,
    quality=None,
):
    where_clauses: list[str] = []
    params: list = [_fts5_sanitize(search)]

    if date_from:
        where_clauses.append("o.date_filed >= ?")
        params.append(date_from)
    if date_to:
        where_clauses.append("o.date_filed <= ?")
        params.append(date_to)
    if author:
        where_clauses.append("o.author = ?")
        params.append(author)
    if case_type:
        where_clauses.append("o.case_type = ?")
        params.append(case_type)
    if source_reporter:
        where_clauses.append("o.source_reporter = ?")
        params.append(source_reporter)
    if has_notes:
        where_clauses.append("o.notes IS NOT NULL AND o.notes != ''")
    if bad_author:
        known = KNOWN_LAST_NAMES | {a.lower() for a in SURROGATE_AUTHORS}
        placeholders = ",".join("?" for _ in known)
        where_clauses.append(
            f"o.author IS NOT NULL AND o.author != '' "
            f"AND LOWER(TRIM(o.author)) NOT IN ({placeholders})"
        )
        params.extend(sorted(known))
    if no_author:
        where_clauses.append(
            "(o.author IS NULL OR o.author = '') AND o.per_curiam = 0"
        )
    if has_dupes:
        where_clauses.append(
            "EXISTS (SELECT 1 FROM opinions o2 WHERE o2.case_name = o.case_name "
            "AND o2.date_filed = o.date_filed AND o2.id != o.id)"
        )
    if citation:
        where_clauses.append(
            "EXISTS (SELECT 1 FROM citations ct WHERE ct.opinion_id = o.id AND ct.citation LIKE ?)"
        )
        params.append(f"%{citation}%")
    if quality == "low":
        where_clauses.append(
            "EXISTS (SELECT 1 FROM quality_scores qs WHERE qs.opinion_id = o.id AND qs.overall_score < 40)"
        )
    elif quality == "mid":
        where_clauses.append(
            "EXISTS (SELECT 1 FROM quality_scores qs WHERE qs.opinion_id = o.id AND qs.overall_score BETWEEN 40 AND 65)"
        )
    elif quality == "high":
        where_clauses.append(
            "EXISTS (SELECT 1 FROM quality_scores qs WHERE qs.opinion_id = o.id AND qs.overall_score > 65)"
        )

    extra_where = (" AND " + " AND ".join(where_clauses)) if where_clauses else ""

    # Count
    count_sql = f"""
        SELECT COUNT(*) as n
        FROM opinions_fts
        JOIN opinions o ON o.id = opinions_fts.rowid
        WHERE opinions_fts MATCH ?{extra_where}
    """
    total = conn.execute(count_sql, params).fetchone()["n"]

    # Use rank for FTS sort, otherwise user-specified
    if sort == "date_filed":
        order_clause = f"o.date_filed {sort_dir}"
    elif sort in ("primary_citation", "cite_nd", "cite_nd_old", "cite_nw", "cited_by_count", "quality_score"):
        order_clause = f"{sort} {sort_dir}"
    else:
        order_clause = "rank"

    data_sql = f"""
        SELECT o.id, o.case_name, o.date_filed, o.author, o.case_type,
               o.docket_number, o.source_reporter, o.per_curiam, o.unanimous,
               o.notes,
               (SELECT c.citation FROM citations c WHERE c.opinion_id = o.id AND c.is_primary = 1 LIMIT 1) as primary_citation,
               (SELECT c.citation FROM citations c WHERE c.opinion_id = o.id AND c.reporter = 'ND' LIMIT 1) as cite_nd,
               (SELECT c.citation FROM citations c WHERE c.opinion_id = o.id AND c.reporter = 'NDold' LIMIT 1) as cite_nd_old,
               COALESCE(
                 (SELECT c.citation FROM citations c WHERE c.opinion_id = o.id AND c.reporter = 'NW2d' LIMIT 1),
                 (SELECT c.citation FROM citations c WHERE c.opinion_id = o.id AND c.reporter = 'NW' AND c.citation LIKE '%N.W.%' LIMIT 1)
               ) as cite_nw,
               (SELECT GROUP_CONCAT(c.citation, '; ') FROM citations c WHERE c.opinion_id = o.id AND c.citation NOT LIKE '%N.W.%' AND c.citation NOT LIKE '%ND %' AND c.citation NOT LIKE '%N.D. %') as cite_other,
               (SELECT COUNT(*) FROM cited_by cb WHERE cb.cited_opinion_id = o.id) as cited_by_count,
               (SELECT qs.overall_score FROM quality_scores qs WHERE qs.opinion_id = o.id) as quality_score,
               snippet(opinions_fts, 1, '«', '»', '…', 30) as snippet
        FROM opinions_fts
        JOIN opinions o ON o.id = opinions_fts.rowid
        WHERE opinions_fts MATCH ?{extra_where}
        ORDER BY {order_clause}
        LIMIT ? OFFSET ?
    """
    params.extend([size, (page - 1) * size])
    rows = conn.execute(data_sql, params).fetchall()

    last_page = max(1, (total + size - 1) // size)
    return {
        "last_page": last_page,
        "total": total,
        "data": [_row_to_dict(r) for r in rows],
    }


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["per_curiam"] = bool(d.get("per_curiam"))
    d["unanimous"] = bool(d.get("unanimous")) if d.get("unanimous") is not None else None
    d["has_notes"] = bool(d.get("notes"))
    d["author_recognized"] = _is_recognized_author(d.get("author"))
    d.pop("notes", None)  # Don't send raw notes in list view
    return d


# ── GET /api/opinions/{id} ────────────────────────────────────────

@app.get("/api/opinions/{opinion_id}")
def get_opinion(opinion_id: int):
    with _db() as conn:
        row = conn.execute(
            "SELECT * FROM opinions WHERE id = ?", (opinion_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Opinion not found")

        citations = conn.execute(
            "SELECT citation, reporter, is_primary FROM citations WHERE opinion_id = ? ORDER BY is_primary DESC",
            (opinion_id,),
        ).fetchall()

        changelog = conn.execute(
            "SELECT timestamp, batch, field, old_value, new_value FROM changelog WHERE opinion_id = ? ORDER BY timestamp DESC",
            (opinion_id,),
        ).fetchall()

        quality = conn.execute(
            "SELECT * FROM quality_scores WHERE opinion_id = ?",
            (opinion_id,),
        ).fetchone()

        citing = conn.execute(
            """SELECT o.id, o.case_name, o.date_filed, o.author, o.per_curiam,
                      (SELECT c.citation FROM citations c WHERE c.opinion_id = o.id AND c.reporter = 'ND' LIMIT 1) as cite_nd
               FROM cited_by cb
               JOIN opinions o ON o.id = cb.citing_opinion_id
               WHERE cb.cited_opinion_id = ?
               ORDER BY o.date_filed DESC""",
            (opinion_id,),
        ).fetchall()

    d = dict(row)
    d["per_curiam"] = bool(d.get("per_curiam"))
    d["unanimous"] = bool(d.get("unanimous")) if d.get("unanimous") is not None else None
    d["author_recognized"] = _is_recognized_author(d.get("author"))
    d["citations"] = [dict(c) for c in citations]
    d["changelog"] = [dict(c) for c in changelog]
    d["citing_opinions"] = [dict(c) for c in citing]
    if quality:
        qd = dict(quality)
        d["quality_score"] = qd["overall_score"]
        d["quality_details"] = {
            "ocr_artifacts": qd["ocr_artifacts"],
            "garbage_chars": qd["garbage_chars"],
            "short_line_ratio": qd["short_line_ratio"],
            "has_html": qd["has_html"],
            "para_markers": qd["para_markers"],
        }
    else:
        d["quality_score"] = None
        d["quality_details"] = None

    # Parse JSON fields
    for field in ("voting_record", "all_justices"):
        val = d.get(field)
        if val:
            try:
                d[field] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass

    # Remove source_path (internal)
    d.pop("source_path", None)

    return d


# ── PATCH /api/opinions/{id} ──────────────────────────────────────

EDITABLE_FIELDS = {"author", "case_name", "date_filed", "case_type", "judges", "docket_number", "notes", "per_curiam"}


@app.patch("/api/opinions/{opinion_id}")
async def update_opinion(opinion_id: int, request: Request):
    body = await request.json()
    field = body.get("field")
    value = body.get("value")

    if field not in EDITABLE_FIELDS:
        raise HTTPException(400, f"Field '{field}' is not editable")
    if value is None:
        raise HTTPException(400, "Value is required")

    value = value.strip()

    with _db() as conn:
        row = conn.execute(
            f"SELECT {field} FROM opinions WHERE id = ?", (opinion_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Opinion not found")

        old_value = row[field]
        if old_value == value:
            return {"status": "unchanged"}

        conn.execute(
            f"UPDATE opinions SET {field} = ? WHERE id = ?",
            (value, opinion_id),
        )
        conn.execute(
            "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) VALUES (?, ?, ?, ?, ?)",
            ("web-ui", opinion_id, field, old_value, value),
        )
        conn.commit()

        # Invalidate facets cache if author changed
        if field == "author":
            global _facets_cache
            _facets_cache = None

    return {"status": "updated", "field": field, "old_value": old_value, "new_value": value}


# ── Merge: find duplicates, diff, execute merge ──────────────────

import difflib
import re

# ── Not-duplicates exclusion list ──────────────────────────────────

NOT_DUPLICATES_PATH = Path(__file__).parent.parent / "not-duplicates.json"


def _load_not_duplicates() -> list[list[int]]:
    if NOT_DUPLICATES_PATH.exists():
        return json.loads(NOT_DUPLICATES_PATH.read_text())
    return []


def _save_not_duplicates(pairs: list[list[int]]) -> None:
    NOT_DUPLICATES_PATH.write_text(json.dumps(pairs, indent=2) + "\n")


def _is_excluded_pair(id_a: int, id_b: int) -> bool:
    for pair in _load_not_duplicates():
        if set(pair) == {id_a, id_b}:
            return True
    return False


@app.get("/api/not-duplicates")
def list_not_duplicates():
    return _load_not_duplicates()


@app.post("/api/not-duplicates")
async def add_not_duplicate(request: Request):
    body = await request.json()
    id_a, id_b = body.get("id_a"), body.get("id_b")
    if not id_a or not id_b:
        raise HTTPException(400, "id_a and id_b required")
    pairs = _load_not_duplicates()
    if not any(set(p) == {id_a, id_b} for p in pairs):
        pairs.append([id_a, id_b])
        _save_not_duplicates(pairs)
    return {"status": "added", "pair": [id_a, id_b]}


@app.delete("/api/not-duplicates/{id_a}/{id_b}")
def remove_not_duplicate(id_a: int, id_b: int):
    pairs = _load_not_duplicates()
    before = len(pairs)
    pairs = [p for p in pairs if set(p) != {id_a, id_b}]
    if len(pairs) == before:
        raise HTTPException(404, "Pair not found")
    _save_not_duplicates(pairs)
    return {"status": "removed"}

# ── Duplicate candidate queue ────────────────────────────────────────


@app.get("/api/duplicate-queue")
def duplicate_queue(
    strategy: str | None = None,
    min_confidence: float = 0.0,
    limit: int = 50,
):
    """Get unreviewed duplicate candidates for review."""
    with _db() as conn:
        where = ["dc.reviewed = 0"]
        params: list = []
        if strategy:
            where.append("dc.strategy = ?")
            params.append(strategy)
        if min_confidence > 0:
            where.append("dc.confidence >= ?")
            params.append(min_confidence)

        where_sql = " AND ".join(where)
        rows = conn.execute(f"""
            SELECT dc.*,
                   oa.case_name as name_a, oa.date_filed as date_a,
                   oa.source_reporter as src_a, oa.author as author_a,
                   (SELECT c.citation FROM citations c WHERE c.opinion_id = dc.opinion_a AND c.is_primary = 1 LIMIT 1) as cite_a,
                   ob.case_name as name_b, ob.date_filed as date_b,
                   ob.source_reporter as src_b, ob.author as author_b,
                   (SELECT c.citation FROM citations c WHERE c.opinion_id = dc.opinion_b AND c.is_primary = 1 LIMIT 1) as cite_b
            FROM duplicate_candidates dc
            JOIN opinions oa ON oa.id = dc.opinion_a
            JOIN opinions ob ON ob.id = dc.opinion_b
            WHERE {where_sql}
            ORDER BY dc.confidence DESC, dc.text_similarity DESC
            LIMIT ?
        """, params + [limit]).fetchall()

    total = len(rows)  # approximate since we have a limit
    return {
        "total": total,
        "candidates": [dict(r) for r in rows],
    }


@app.post("/api/duplicate-queue/{candidate_id}/resolve")
async def resolve_duplicate(candidate_id: int, request: Request):
    """Mark a duplicate candidate as reviewed."""
    body = await request.json()
    resolved_as = body.get("resolved_as")  # 'merged', 'not-duplicate', 'deferred'
    if resolved_as not in ("merged", "not-duplicate", "deferred"):
        raise HTTPException(400, "resolved_as must be 'merged', 'not-duplicate', or 'deferred'")

    with _db() as conn:
        row = conn.execute(
            "SELECT * FROM duplicate_candidates WHERE id = ?", (candidate_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Candidate not found")

        conn.execute(
            """UPDATE duplicate_candidates
               SET reviewed = 1, resolved_as = ?, reviewed_at = strftime('%Y-%m-%dT%H:%M:%S', 'now')
               WHERE id = ?""",
            (resolved_as, candidate_id),
        )

        # Also add to not-duplicates list if resolved as such
        if resolved_as == "not-duplicate":
            pairs = _load_not_duplicates()
            id_a, id_b = row["opinion_a"], row["opinion_b"]
            if not any(set(p) == {id_a, id_b} for p in pairs):
                pairs.append([id_a, id_b])
                _save_not_duplicates(pairs)

        conn.commit()

    return {"status": "resolved", "resolved_as": resolved_as}


# OCR confusion pairs (common misreads)
_OCR_PAIRS = [
    ("rn", "m"), ("li", "h"), ("cl", "d"), ("tl", "d"),
    ("vv", "w"), ("ii", "u"), ("fi", "fi"),  # ligature
]


def _ocr_score(word_a: str, word_b: str) -> float:
    """Return 0-1 score of how likely this diff is an OCR glitch. Higher = more likely OCR."""
    if word_a == word_b:
        return 0.0
    a, b = word_a.lower(), word_b.lower()
    # Check known OCR confusion pairs
    for bad, good in _OCR_PAIRS:
        if a.replace(bad, good) == b or b.replace(bad, good) == a:
            return 0.95
    # Single-char substitution in a word > 3 chars
    if len(a) == len(b) and len(a) > 3:
        diffs = sum(1 for x, y in zip(a, b) if x != y)
        if diffs == 1:
            return 0.8
    # Transposition
    if len(a) == len(b) and len(a) > 3:
        for i in range(len(a) - 1):
            swapped = a[:i] + a[i+1] + a[i] + a[i+2:]
            if swapped == b:
                return 0.85
    # Extra/missing space
    if a.replace(" ", "") == b.replace(" ", ""):
        return 0.7
    return 0.0


def _text_quality_score(text: str, source_reporter: str) -> float:
    """Heuristic quality score for opinion text. Higher = cleaner."""
    score = 0.0
    # Source preference
    if source_reporter == "ND":
        score += 20
    elif source_reporter == "NW2d":
        score += 10
    elif source_reporter == "NW":
        score += 5

    # Paragraph markers (¶1, ¶2...) indicate well-structured text
    para_marks = re.findall(r'¶\d+', text)
    if para_marks:
        score += 15
        # Sequential paragraph numbers
        nums = [int(re.search(r'\d+', p).group()) for p in para_marks]
        if nums == list(range(nums[0], nums[0] + len(nums))):
            score += 5

    # Penalize OCR artifacts: isolated special chars, broken words
    garbage_chars = len(re.findall(r'(?<!\w)[^\w\s.,;:!?\'\"()\-–—§¶\[\]/{}&@#$%](?!\w)', text))
    score -= garbage_chars * 0.5

    # Penalize very short lines that suggest OCR line-break issues
    lines = text.split('\n')
    short_breaks = sum(1 for l in lines if 0 < len(l.strip()) < 15)
    score -= short_breaks * 0.1

    return score


_QUOTE_NORM = str.maketrans({
    "\u2018": "'", "\u2019": "'",   # '' → '
    "\u201C": '"', "\u201D": '"',   # "" → "
    "\u2013": "-", "\u2014": "-",   # –— → -
})


def _normalize_quotes(text: str) -> str:
    """Normalize curly quotes/apostrophes to straight equivalents for diffing."""
    return text.translate(_QUOTE_NORM)


def _word_diff(text_a: str, text_b: str) -> list[dict]:
    """Compute word-level diff between two texts. Returns list of hunks.

    Normalizes curly/straight quotes before comparison so typographic
    differences don't appear as changes.
    """
    # Normalize quotes for comparison, but preserve original text in output
    norm_a = _normalize_quotes(text_a)
    norm_b = _normalize_quotes(text_b)
    words_a_norm = norm_a.split()
    words_b_norm = norm_b.split()
    words_a = text_a.split()
    words_b = text_b.split()

    sm = difflib.SequenceMatcher(None, words_a_norm, words_b_norm, autojunk=False)
    hunks = []

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            hunks.append({
                "type": "equal",
                "text": " ".join(words_a[i1:i2]),
            })
        elif tag == "replace":
            text_left = " ".join(words_a[i1:i2])
            text_right = " ".join(words_b[j1:j2])
            ocr = max(
                (_ocr_score(wa, wb) for wa, wb in zip(words_a_norm[i1:i2], words_b_norm[j1:j2])),
                default=0.0,
            )
            hunks.append({
                "type": "replace",
                "left": text_left,
                "right": text_right,
                "ocr_likelihood": round(ocr, 2),
            })
        elif tag == "insert":
            hunks.append({
                "type": "insert",
                "right": " ".join(words_b[j1:j2]),
                "ocr_likelihood": 0.0,
            })
        elif tag == "delete":
            hunks.append({
                "type": "delete",
                "left": " ".join(words_a[i1:i2]),
                "ocr_likelihood": 0.0,
            })

    return hunks


def _strip_headnotes(text: str) -> str:
    """Strip West headnotes/syllabus from beginning of opinion text."""
    text = re.sub(r'^---\n[\s\S]*?\n---\n*', '', text)
    return text


@app.get("/api/opinions/{opinion_id}/duplicates")
def find_duplicates(opinion_id: int):
    """Find likely duplicate opinions for merging."""
    with _db() as conn:
        row = conn.execute(
            "SELECT case_name, date_filed FROM opinions WHERE id = ?",
            (opinion_id,),
        ).fetchone()
        if not row:
            raise HTTPException(404, "Opinion not found")

        # Strategy 1: same case_name + date_filed
        candidates = conn.execute(
            """SELECT o.id, o.case_name, o.date_filed, o.author, o.source_reporter,
                      o.source_path, o.cluster_id, o.case_type, o.judges,
                      o.voting_record IS NOT NULL as has_voting_record,
                      LENGTH(o.text_content) as text_length,
                      c.citation as primary_citation
               FROM opinions o
               LEFT JOIN citations c ON c.opinion_id = o.id AND c.is_primary = 1
               WHERE o.case_name = ? AND o.date_filed = ? AND o.id != ?
               ORDER BY o.source_reporter""",
            (row["case_name"], row["date_filed"], opinion_id),
        ).fetchall()
        found_ids = {c["id"] for c in candidates}

        # Strategy 2: shared citations (different opinion rows with same citation string)
        shared = conn.execute(
            """SELECT DISTINCT o2.id, o2.case_name, o2.date_filed, o2.author,
                      o2.source_reporter, o2.source_path, o2.cluster_id, o2.case_type,
                      o2.judges, o2.voting_record IS NOT NULL as has_voting_record,
                      LENGTH(o2.text_content) as text_length,
                      c2.citation as primary_citation
               FROM citations c1
               JOIN citations c2 ON c1.citation = c2.citation AND c1.opinion_id != c2.opinion_id
               JOIN opinions o2 ON o2.id = c2.opinion_id
               LEFT JOIN citations c2p ON c2p.opinion_id = o2.id AND c2p.is_primary = 1
               WHERE c1.opinion_id = ? AND o2.id != ?""",
            (opinion_id, opinion_id),
        ).fetchall()
        for s in shared:
            if s["id"] not in found_ids:
                candidates.append(s)
                found_ids.add(s["id"])

        # Strategy 3: same date + similar name (within same date, fuzzy)
        if not candidates:
            same_date = conn.execute(
                """SELECT o.id, o.case_name, o.date_filed, o.author, o.source_reporter,
                          o.source_path, o.cluster_id, o.case_type, o.judges,
                          o.voting_record IS NOT NULL as has_voting_record,
                          LENGTH(o.text_content) as text_length,
                          c.citation as primary_citation
                   FROM opinions o
                   LEFT JOIN citations c ON c.opinion_id = o.id AND c.is_primary = 1
                   WHERE o.date_filed = ? AND o.id != ?""",
                (row["date_filed"], opinion_id),
            ).fetchall()
            # Simple fuzzy: normalize names and check overlap
            def _normalize(name: str) -> set[str]:
                return {w.lower().strip(".,") for w in (name or "").split() if len(w) > 2}
            src_words = _normalize(row["case_name"])
            for s in same_date:
                if s["id"] in found_ids:
                    continue
                other_words = _normalize(s["case_name"])
                overlap = len(src_words & other_words)
                if overlap >= 2 and overlap >= len(src_words) * 0.5:
                    candidates.append(s)
                    found_ids.add(s["id"])

        # Filter out pairs marked as not-duplicates
        candidates = [c for c in candidates if not _is_excluded_pair(opinion_id, c["id"])]

        return [dict(c) for c in candidates]


@app.get("/api/opinions/{opinion_id}/diff/{other_id}")
def diff_opinions(opinion_id: int, other_id: int):
    """Word-level diff between two opinions with OCR scoring."""
    with _db() as conn:
        row_a = conn.execute(
            """SELECT o.*, c.citation as primary_citation
               FROM opinions o
               LEFT JOIN citations c ON c.opinion_id = o.id AND c.is_primary = 1
               WHERE o.id = ?""",
            (opinion_id,),
        ).fetchone()
        row_b = conn.execute(
            """SELECT o.*, c.citation as primary_citation
               FROM opinions o
               LEFT JOIN citations c ON c.opinion_id = o.id AND c.is_primary = 1
               WHERE o.id = ?""",
            (other_id,),
        ).fetchone()

        if not row_a or not row_b:
            raise HTTPException(404, "Opinion not found")

        cites_a = conn.execute(
            "SELECT citation, reporter FROM citations WHERE opinion_id = ?",
            (opinion_id,),
        ).fetchall()
        cites_b = conn.execute(
            "SELECT citation, reporter FROM citations WHERE opinion_id = ?",
            (other_id,),
        ).fetchall()

    text_a = _strip_headnotes(row_a["text_content"])
    text_b = _strip_headnotes(row_b["text_content"])

    score_a = _text_quality_score(text_a, row_a["source_reporter"])
    score_b = _text_quality_score(text_b, row_b["source_reporter"])

    # Compute diff with higher-quality text as "left" (base)
    if score_a >= score_b:
        hunks = _word_diff(text_a, text_b)
        base_id = opinion_id
    else:
        hunks = _word_diff(text_b, text_a)
        base_id = other_id

    # Metadata comparison
    meta_fields = ["author", "case_type", "judges", "docket_number", "case_name",
                   "date_filed", "cluster_id", "per_curiam", "unanimous", "notes"]
    metadata = {}
    for f in meta_fields:
        val_a = row_a[f] if row_a[f] is not None else None
        val_b = row_b[f] if row_b[f] is not None else None
        if val_a != val_b or val_a is not None:
            metadata[f] = {
                "a": {"id": opinion_id, "value": val_a},
                "b": {"id": other_id, "value": val_b},
                "same": val_a == val_b,
            }

    diff_count = sum(1 for h in hunks if h["type"] != "equal")
    ocr_count = sum(1 for h in hunks if h.get("ocr_likelihood", 0) > 0.6)

    return {
        "base_id": base_id,
        "other_id": other_id if base_id == opinion_id else opinion_id,
        "score_a": round(score_a, 1),
        "score_b": round(score_b, 1),
        "opinion_a": {
            "id": opinion_id,
            "source_reporter": row_a["source_reporter"],
            "source_path": row_a["source_path"],
            "text_length": len(text_a),
            "citations": [dict(c) for c in cites_a],
        },
        "opinion_b": {
            "id": other_id,
            "source_reporter": row_b["source_reporter"],
            "source_path": row_b["source_path"],
            "text_length": len(text_b),
            "citations": [dict(c) for c in cites_b],
        },
        "metadata": metadata,
        "hunks": hunks,
        "diff_count": diff_count,
        "ocr_count": ocr_count,
    }


@app.post("/api/opinions/{survivor_id}/merge")
async def merge_opinions(survivor_id: int, request: Request):
    """Merge another opinion into the survivor.

    Body: {
        "loser_id": int,
        "metadata_picks": {"field": "a"|"b", ...},  # which opinion's value to use
        "text_source": "a"|"b"|"merged",
        "merged_text": "..." (if text_source == "merged")
    }
    """
    body = await request.json()
    loser_id = body.get("loser_id")
    if not loser_id:
        raise HTTPException(400, "loser_id required")

    metadata_picks = body.get("metadata_picks", {})
    text_source = body.get("text_source", "a")
    merged_text = body.get("merged_text")

    with _db() as conn:
        survivor = conn.execute("SELECT * FROM opinions WHERE id = ?", (survivor_id,)).fetchone()
        loser = conn.execute("SELECT * FROM opinions WHERE id = ?", (loser_id,)).fetchone()
        if not survivor or not loser:
            raise HTTPException(404, "Opinion not found")

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()

        # 1. Determine text
        if text_source == "merged" and merged_text:
            final_text = merged_text
        elif text_source == "b":
            final_text = loser["text_content"]
        else:
            final_text = survivor["text_content"]

        # 2. Apply metadata picks
        merge_fields = ["author", "case_type", "judges", "docket_number", "case_name",
                        "date_filed", "cluster_id", "per_curiam", "unanimous", "notes",
                        "voting_record", "all_justices", "highlight"]
        updates = {}
        for field in merge_fields:
            pick = metadata_picks.get(field)
            if pick == "b":
                new_val = loser[field]
                old_val = survivor[field]
                if new_val != old_val:
                    updates[field] = new_val
                    conn.execute(
                        "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) VALUES (?, ?, ?, ?, ?)",
                        ("merge", survivor_id, field, str(old_val) if old_val else None, str(new_val) if new_val else None),
                    )
            elif pick is None and survivor[field] is None and loser[field] is not None:
                # Auto-fill nulls from loser
                updates[field] = loser[field]
                conn.execute(
                    "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) VALUES (?, ?, ?, ?, ?)",
                    ("merge", survivor_id, field, None, str(loser[field])),
                )

        # Update text if changed
        if final_text != survivor["text_content"]:
            updates["text_content"] = final_text
            conn.execute(
                "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) VALUES (?, ?, ?, ?, ?)",
                ("merge", survivor_id, "text_content", f"[{len(survivor['text_content'])} chars]", f"[{len(final_text)} chars]"),
            )

        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            conn.execute(
                f"UPDATE opinions SET {set_clause} WHERE id = ?",
                [*updates.values(), survivor_id],
            )

        # 3. Move all citations from loser to survivor (skip duplicates)
        loser_cites = conn.execute(
            "SELECT citation, reporter, is_primary FROM citations WHERE opinion_id = ?",
            (loser_id,),
        ).fetchall()
        for cite in loser_cites:
            existing = conn.execute(
                "SELECT id FROM citations WHERE opinion_id = ? AND citation = ?",
                (survivor_id, cite["citation"]),
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO citations (opinion_id, citation, reporter, is_primary) VALUES (?, ?, ?, ?)",
                    (survivor_id, cite["citation"], cite["reporter"], cite["is_primary"]),
                )

        # 4. Archive loser source into opinion_sources
        existing_src = conn.execute(
            "SELECT id FROM opinion_sources WHERE source_path = ?",
            (loser["source_path"],),
        ).fetchone()
        if not existing_src:
            conn.execute(
                """INSERT INTO opinion_sources (opinion_id, source_reporter, source_path, cluster_id, text_length, is_primary, added_at)
                   VALUES (?, ?, ?, ?, ?, 0, ?)""",
                (survivor_id, loser["source_reporter"], loser["source_path"],
                 loser["cluster_id"], len(loser["text_content"]), now),
            )
        else:
            # Update to point to survivor
            conn.execute(
                "UPDATE opinion_sources SET opinion_id = ?, is_primary = 0 WHERE id = ?",
                (survivor_id, existing_src["id"]),
            )

        # 5. Log the merge
        conn.execute(
            "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) VALUES (?, ?, ?, ?, ?)",
            ("merge", survivor_id, "merge", f"absorbed opinion id={loser_id}", f"loser_path={loser['source_path']}"),
        )

        # 6. Delete loser's citations, changelog refs, and the opinion itself
        conn.execute("DELETE FROM citations WHERE opinion_id = ?", (loser_id,))
        conn.execute("DELETE FROM opinions WHERE id = ?", (loser_id,))

        # Mark any duplicate candidates involving these opinions as resolved
        conn.execute(
            """UPDATE duplicate_candidates SET reviewed = 1, resolved_as = 'merged',
               reviewed_at = strftime('%Y-%m-%dT%H:%M:%S', 'now')
               WHERE (opinion_a = ? OR opinion_b = ? OR opinion_a = ? OR opinion_b = ?)
               AND reviewed = 0""",
            (survivor_id, survivor_id, loser_id, loser_id),
        )

        conn.commit()

        # Invalidate caches
        global _facets_cache
        _facets_cache = None

    return {
        "status": "merged",
        "survivor_id": survivor_id,
        "loser_id": loser_id,
        "fields_updated": list(updates.keys()),
    }


# ── Confirmed authors ─────────────────────────────────────────────

@app.get("/api/confirmed-authors")
def get_confirmed_authors():
    return sorted(_confirmed_authors)


@app.post("/api/confirmed-authors")
async def confirm_author(request: Request):
    body = await request.json()
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(400, "name required")

    lower = name.lower()
    _confirmed_authors.add(lower)
    _save_confirmed_authors(_confirmed_authors)

    # Invalidate facets cache so author counts refresh
    global _facets_cache
    _facets_cache = None

    # Count how many opinions this clears
    with _db() as conn:
        count = conn.execute(
            "SELECT COUNT(*) as n FROM opinions WHERE LOWER(TRIM(author)) = ?",
            (lower,),
        ).fetchone()["n"]

    return {"status": "confirmed", "name": name, "opinions_cleared": count}


@app.delete("/api/confirmed-authors/{name}")
def unconfirm_author(name: str):
    lower = name.strip().lower()
    if lower not in _confirmed_authors:
        raise HTTPException(404, "Author not in confirmed list")
    _confirmed_authors.discard(lower)
    _save_confirmed_authors(_confirmed_authors)

    global _facets_cache
    _facets_cache = None

    return {"status": "removed", "name": name}


# ── Review flags (file-backed, for Claude Code to consume) ────────

FLAGS_PATH = Path(__file__).parent.parent / "review-flags.json"


def _load_flags() -> list[dict]:
    if FLAGS_PATH.exists():
        return json.loads(FLAGS_PATH.read_text())
    return []


def _save_flags(flags: list[dict]) -> None:
    FLAGS_PATH.write_text(json.dumps(flags, indent=2) + "\n")


@app.get("/api/flags")
def get_flags():
    return _load_flags()


@app.post("/api/flags")
async def upsert_flag(request: Request):
    body = await request.json()
    opinion_id = body.get("opinion_id")
    if not opinion_id:
        raise HTTPException(400, "opinion_id required")

    # Get citation and case_name for context
    with _db() as conn:
        row = conn.execute(
            "SELECT case_name, date_filed FROM opinions WHERE id = ?",
            (opinion_id,),
        ).fetchone()
        citation_row = conn.execute(
            "SELECT citation FROM citations WHERE opinion_id = ? AND is_primary = 1",
            (opinion_id,),
        ).fetchone()

    from datetime import datetime, timezone

    flag = {
        "opinion_id": opinion_id,
        "citation": citation_row["citation"] if citation_row else None,
        "case_name": row["case_name"] if row else None,
        "date_filed": row["date_filed"] if row else None,
        "note": body.get("note", "").strip(),
        "category": body.get("category", "review"),
        "flagged_at": datetime.now(timezone.utc).isoformat(),
    }

    flags = _load_flags()
    # Replace existing flag for same opinion_id, or append
    flags = [f for f in flags if f["opinion_id"] != opinion_id]
    flags.append(flag)
    flags.sort(key=lambda f: f.get("flagged_at", ""))
    _save_flags(flags)
    return flag


@app.delete("/api/flags/{opinion_id}")
def delete_flag(opinion_id: int):
    flags = _load_flags()
    before = len(flags)
    flags = [f for f in flags if f["opinion_id"] != opinion_id]
    if len(flags) == before:
        raise HTTPException(404, "Flag not found")
    _save_flags(flags)
    return {"status": "deleted"}


# ── Entry point ───────────────────────────────────────────────────

def main():
    import uvicorn
    uvicorn.run("ndcourts_mcp.webapp:app", host="127.0.0.1", port=8765)


if __name__ == "__main__":
    main()
