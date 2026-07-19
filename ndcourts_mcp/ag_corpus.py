"""ND Attorney General opinions corpus (``ag_opinions.db``).

Unlike the four primary-law corpora (``corpus.py``), AG opinions are *immutable,
dated documents* — like court opinions, not living/amendable provisions. So this
DB uses an opinions-flavored schema (one row per opinion, no version history)
rather than the ``provisions``/``provision_versions`` model. It is still ATTACHed
onto the shared MCP connection under alias ``ag`` exactly like the corpora, so a
single session can answer cross-corpus questions ("which AG opinions construe
this statute").

Cross-linking: ``ag_text_citations`` mirrors ``opinions.db``'s ``text_citations``
table byte-for-byte in its column set, so the existing cite_type→corpus
resolution logic (audit_corpus) applies unchanged. jetcite extracts the cites in
Phase 3; they resolve to ``<corpus>.provisions.citation`` and to
``citations.citation`` (ND Supreme Court opinions) by exact-string join.
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

from platformdirs import user_data_path

# Registry entry, parallel to corpus.CORPORA but a distinct model (see module
# docstring). alias 'ag' is how attached tables are qualified: ``ag.ag_opinions``.
AG_CORPUS = {"file": "ag_opinions.db", "alias": "ag", "label": "ND Attorney General Opinions"}

# Modern opinion-number shape: YYYY-<letter>-NN (e.g. 2015-L-12). The letter is
# the type code (L=Legal, O=Open Records/Meetings, F=Formal). Pre-modern numbers
# are heterogeneous, so type_code is best-effort.
_NUM_RE = re.compile(r"\b(\d{2,4})-([A-Za-z])-(\d+)\b")


def resolve_ag_db_path() -> Path:
    """Locate ag_opinions.db independent of working directory or install layout.

    Resolution order mirrors ``db.resolve_db_path`` /
    ``corpus.resolve_corpus_db_path``:
      1. ``NDCOURTS_AG_DB`` env var.
      2. The file bundled alongside the source tree / release tarball.
      3. The per-user data directory.
    """
    env = os.environ.get("NDCOURTS_AG_DB")
    if env:
        return Path(env).expanduser()
    bundled = Path(__file__).resolve().parent.parent / AG_CORPUS["file"]
    if bundled.exists():
        return bundled
    return user_data_path("ndcourts-mcp", appauthor=False) / AG_CORPUS["file"]


def cite_key(opinion_number: str) -> str:
    """Normalize an AG opinion number to a stable lookup key.

    Lowercases and strips whitespace/punctuation that varies by source while
    keeping the alphanumerics and hyphens that carry meaning (``2015-l-12``).
    Conservative: two numbers key alike only if they differ solely in cosmetic
    punctuation or case.
    """
    s = (opinion_number or "").lower()
    s = re.sub(r"[^a-z0-9\-]+", "", s)
    return s


def canonical_ag_cite(opinion_number: str) -> str:
    """Build the display citation from the verbatim opinion number.

    Bluebook-style: ``N.D. Op. Att'y Gen. 2015-L-12``. The opinion number is
    kept verbatim (the AG's own identifier); only the reporter prefix is added.
    """
    return f"N.D. Op. Att'y Gen. {opinion_number.strip()}"


def type_code(opinion_number: str, opinion_type: str | None) -> str | None:
    """Best-effort single-letter type code (L|O|F|...).

    Prefer the letter embedded in a modern opinion number; fall back to the
    first letter of the verbatim Type column word.
    """
    m = _NUM_RE.search(opinion_number or "")
    if m:
        return m.group(2).upper()
    t = (opinion_type or "").strip()
    if t:
        # "Legal" -> L, "Open Records & Meetings" -> O, "Formal"/"Advisory" -> F/A
        return t[0].upper()
    return None


def get_ag_connection(
    db_path: Path, *, must_exist: bool = True, read_only: bool = False
) -> sqlite3.Connection:
    if read_only:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    if not read_only:
        conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    if must_exist:
        have = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ag_opinions'"
        ).fetchone()
        if not have:
            raise FileNotFoundError(
                f"AG opinions database at {db_path} has no schema; install the "
                f"ag_opinions.db release asset."
            )
    return conn


def create_ag_schema(conn: sqlite3.Connection) -> None:
    """Create the AG-opinions schema (opinions-flavored, immutable rows)."""
    conn.executescript("""
        -- One row per published AG opinion.
        CREATE TABLE IF NOT EXISTS ag_opinions (
            id INTEGER PRIMARY KEY,
            opinion_number TEXT NOT NULL,   -- verbatim from the source table
            ag_cite TEXT NOT NULL,          -- canonical display cite
            cite_key TEXT NOT NULL,         -- normalized lookup key (ag_corpus.cite_key)
            date_issued TEXT,               -- ISO date, or NULL if unparseable
            date_raw TEXT,                  -- the source's human date string, verbatim
            issued_to TEXT,                 -- requestor (from the "Issued To" column)
            opinion_type TEXT,              -- verbatim "Type" column
            type_code TEXT,                 -- L | O | F | ... (best-effort)
            text_content TEXT,              -- populated in Phase 2 (NULL until then)
            text_source TEXT,               -- 'pdf-text' | 'ocr' | NULL
            ocr_quality INTEGER,            -- artifact count for OCR text; NULL for pdf-text
            source_url TEXT,                -- absolute AG PDF URL (authoritative copy)
            source_path TEXT,               -- local cached PDF under ~/refs/nd/ag/
            scraped_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
            UNIQUE(opinion_number)
        );

        CREATE INDEX IF NOT EXISTS idx_ag_cite_key ON ag_opinions(cite_key);
        CREATE INDEX IF NOT EXISTS idx_ag_date ON ag_opinions(date_issued);
        CREATE INDEX IF NOT EXISTS idx_ag_type ON ag_opinions(type_code);

        -- Citations extracted from AG opinion text by jetcite (Phase 3).
        -- Column set MIRRORS opinions.db text_citations so the existing
        -- cite_type->corpus resolver applies unchanged. ocr_derived flags cites
        -- pulled from OCR text (digit-flip risk; audited, not trusted silently).
        CREATE TABLE IF NOT EXISTS ag_text_citations (
            id INTEGER PRIMARY KEY,
            ag_opinion_id INTEGER NOT NULL REFERENCES ag_opinions(id),
            normalized TEXT NOT NULL,
            cite_type TEXT NOT NULL,        -- case|statute|court_rule|regulation|constitution
            jurisdiction TEXT,
            raw_text TEXT NOT NULL,
            url TEXT,
            ocr_derived INTEGER DEFAULT 0,
            UNIQUE(ag_opinion_id, normalized)
        );

        CREATE INDEX IF NOT EXISTS idx_ag_tc_opinion ON ag_text_citations(ag_opinion_id);
        CREATE INDEX IF NOT EXISTS idx_ag_tc_normalized ON ag_text_citations(normalized);
        CREATE INDEX IF NOT EXISTS idx_ag_tc_type ON ag_text_citations(cite_type);

        -- INBOUND edges: ND Supreme Court / COA opinions that cite an AG opinion.
        -- Built by ag_backlink from opinions.db text (jetcite does not recognize
        -- AG-opinion citations). court_opinion_id is opinions.db opinions.id — a
        -- DERIVED reference (rebuild after opinions.db changes), so no FK. ND
        -- courts cite AG opinions two ways: the Bluebook docket form ("N.D. Op.
        -- Att'y Gen. 2003-L-11", match_kind='docket') and, more often
        -- historically, a date-prose form ("Attorney General's opinion of
        -- February 18, 1975", match_kind='date'). ag_opinion_id is NULL when the
        -- cited opinion is not in our corpus (pre-1942 / gap) — the edge is still
        -- recorded with raw_text preserved.
        CREATE TABLE IF NOT EXISTS ag_cited_by_court (
            id INTEGER PRIMARY KEY,
            court_opinion_id INTEGER NOT NULL,
            ag_opinion_id INTEGER REFERENCES ag_opinions(id),
            normalized TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            match_kind TEXT NOT NULL,        -- 'docket' | 'date'
            resolution TEXT,                 -- 'exact' | 'fuzzy' | NULL (unresolved)
            UNIQUE(court_opinion_id, normalized)
        );
        CREATE INDEX IF NOT EXISTS idx_ag_cbc_ag ON ag_cited_by_court(ag_opinion_id);
        CREATE INDEX IF NOT EXISTS idx_ag_cbc_court ON ag_cited_by_court(court_opinion_id);

        -- Pipeline run provenance (mirrors opinions.db provenance table).
        CREATE TABLE IF NOT EXISTS provenance (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
            operation TEXT NOT NULL,
            command TEXT,
            source_paths TEXT,
            rows_affected INTEGER,
            notes TEXT
        );

        -- Auditable corrections (mirrors opinions.db changelog discipline).
        CREATE TABLE IF NOT EXISTS changelog (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
            batch TEXT NOT NULL,
            ag_opinion_id INTEGER REFERENCES ag_opinions(id),
            field TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            authority TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_ag_changelog_batch ON changelog(batch);

        -- FTS over opinion text + number/requestor. External-content, kept in
        -- sync by triggers (mirrors opinions_fts).
        CREATE VIRTUAL TABLE IF NOT EXISTS ag_opinions_fts USING fts5(
            opinion_number,
            issued_to,
            text_content,
            content='ag_opinions',
            content_rowid='id',
            tokenize='porter unicode61'
        );

        CREATE TRIGGER IF NOT EXISTS ag_opinions_ai AFTER INSERT ON ag_opinions BEGIN
            INSERT INTO ag_opinions_fts(rowid, opinion_number, issued_to, text_content)
            VALUES (new.id, new.opinion_number, COALESCE(new.issued_to,''), COALESCE(new.text_content,''));
        END;

        CREATE TRIGGER IF NOT EXISTS ag_opinions_ad AFTER DELETE ON ag_opinions BEGIN
            INSERT INTO ag_opinions_fts(ag_opinions_fts, rowid, opinion_number, issued_to, text_content)
            VALUES ('delete', old.id, old.opinion_number, COALESCE(old.issued_to,''), COALESCE(old.text_content,''));
        END;

        CREATE TRIGGER IF NOT EXISTS ag_opinions_au AFTER UPDATE ON ag_opinions BEGIN
            INSERT INTO ag_opinions_fts(ag_opinions_fts, rowid, opinion_number, issued_to, text_content)
            VALUES ('delete', old.id, old.opinion_number, COALESCE(old.issued_to,''), COALESCE(old.text_content,''));
            INSERT INTO ag_opinions_fts(rowid, opinion_number, issued_to, text_content)
            VALUES (new.id, new.opinion_number, COALESCE(new.issued_to,''), COALESCE(new.text_content,''));
        END;
    """)
    # Additive migration: `resolution` was added after the first ag_cited_by_court
    # ships (CREATE TABLE IF NOT EXISTS won't alter an existing table).
    cbc_cols = {r[1] for r in conn.execute("PRAGMA table_info(ag_cited_by_court)")}
    if cbc_cols and "resolution" not in cbc_cols:
        conn.execute("ALTER TABLE ag_cited_by_court ADD COLUMN resolution TEXT")
    conn.commit()


def attach_ag(conn: sqlite3.Connection, *, read_only: bool = False) -> bool:
    """ATTACH ag_opinions.db onto an existing connection under alias 'ag'.

    Returns True if attached (or already attached), False if the file is absent
    (a chambers install may not have it). Mirrors corpus.attach_corpora.
    """
    alias = AG_CORPUS["alias"]
    existing = {r["name"] for r in conn.execute("PRAGMA database_list")}
    if alias in existing:
        return True
    path = resolve_ag_db_path()
    if not path.exists():
        return False
    target = f"file:{path}?mode=ro" if read_only else str(path)
    conn.execute(f"ATTACH DATABASE ? AS {alias}", (target,))
    return True
