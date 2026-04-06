"""Database schema and connection management."""

import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).parent.parent / "opinions.db"


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def log_provenance(
    conn: sqlite3.Connection,
    operation: str,
    command: str | None = None,
    source_paths: str | None = None,
    rows_affected: int | None = None,
    notes: str | None = None,
) -> None:
    """Record a pipeline run in the provenance table."""
    conn.execute(
        """INSERT INTO provenance (operation, command, source_paths, rows_affected, notes)
           VALUES (?, ?, ?, ?, ?)""",
        (operation, command, source_paths, rows_affected, notes),
    )
    conn.commit()


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS opinions (
            id INTEGER PRIMARY KEY,
            cluster_id INTEGER UNIQUE,
            case_name TEXT NOT NULL,
            case_name_full TEXT,
            date_filed TEXT NOT NULL,
            court TEXT DEFAULT 'North Dakota Supreme Court',
            docket_number TEXT,
            judges TEXT,
            per_curiam INTEGER DEFAULT 0,
            author TEXT,
            absolute_url TEXT,
            opinion_url TEXT,
            case_type TEXT,
            highlight TEXT,
            voting_record TEXT,
            all_justices TEXT,
            unanimous INTEGER,
            source_reporter TEXT NOT NULL,
            source_path TEXT NOT NULL,
            text_content TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS citations (
            id INTEGER PRIMARY KEY,
            opinion_id INTEGER NOT NULL REFERENCES opinions(id),
            citation TEXT NOT NULL,
            reporter TEXT,
            is_primary INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS changelog (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
            batch TEXT NOT NULL,
            opinion_id INTEGER NOT NULL REFERENCES opinions(id),
            field TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT
        );

        CREATE TABLE IF NOT EXISTS opinion_sources (
            id INTEGER PRIMARY KEY,
            opinion_id INTEGER NOT NULL REFERENCES opinions(id),
            source_reporter TEXT NOT NULL,
            source_path TEXT NOT NULL,
            cluster_id INTEGER,
            text_length INTEGER,
            is_primary INTEGER DEFAULT 0,
            added_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_opinion_sources_opinion_id ON opinion_sources(opinion_id);
        CREATE INDEX IF NOT EXISTS idx_opinion_sources_path ON opinion_sources(source_path);

        CREATE INDEX IF NOT EXISTS idx_changelog_batch ON changelog(batch);
        CREATE INDEX IF NOT EXISTS idx_changelog_opinion_id ON changelog(opinion_id);

        CREATE INDEX IF NOT EXISTS idx_citations_citation ON citations(citation);
        CREATE INDEX IF NOT EXISTS idx_citations_opinion_id ON citations(opinion_id);
        CREATE INDEX IF NOT EXISTS idx_opinions_date ON opinions(date_filed);
        CREATE INDEX IF NOT EXISTS idx_opinions_cluster_id ON opinions(cluster_id);
        CREATE INDEX IF NOT EXISTS idx_opinions_author ON opinions(author);

        -- Citations extracted from opinion text by jetcite
        CREATE TABLE IF NOT EXISTS text_citations (
            id INTEGER PRIMARY KEY,
            opinion_id INTEGER NOT NULL REFERENCES opinions(id),
            normalized TEXT NOT NULL,
            cite_type TEXT NOT NULL,
            jurisdiction TEXT,
            raw_text TEXT NOT NULL,
            url TEXT,
            parallel_group INTEGER,
            UNIQUE(opinion_id, normalized)
        );

        CREATE INDEX IF NOT EXISTS idx_text_citations_opinion_id ON text_citations(opinion_id);
        CREATE INDEX IF NOT EXISTS idx_text_citations_normalized ON text_citations(normalized);
        CREATE INDEX IF NOT EXISTS idx_text_citations_cite_type ON text_citations(cite_type);

        -- Reverse index: which opinions cite which
        CREATE TABLE IF NOT EXISTS cited_by (
            id INTEGER PRIMARY KEY,
            cited_opinion_id INTEGER NOT NULL REFERENCES opinions(id),
            citing_opinion_id INTEGER NOT NULL REFERENCES opinions(id),
            citation TEXT NOT NULL,
            UNIQUE(cited_opinion_id, citing_opinion_id)
        );

        CREATE INDEX IF NOT EXISTS idx_cited_by_cited ON cited_by(cited_opinion_id);
        CREATE INDEX IF NOT EXISTS idx_cited_by_citing ON cited_by(citing_opinion_id);

        -- Quality scores for opinion text
        CREATE TABLE IF NOT EXISTS quality_scores (
            opinion_id INTEGER PRIMARY KEY REFERENCES opinions(id),
            ocr_artifacts INTEGER,
            garbage_chars INTEGER,
            short_line_ratio REAL,
            has_html INTEGER DEFAULT 0,
            para_markers INTEGER,
            dupe_cites INTEGER DEFAULT 0,
            overall_score REAL,
            scanned_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))
        );

        -- Duplicate candidate pairs
        CREATE TABLE IF NOT EXISTS duplicate_candidates (
            id INTEGER PRIMARY KEY,
            opinion_a INTEGER NOT NULL REFERENCES opinions(id),
            opinion_b INTEGER NOT NULL REFERENCES opinions(id),
            strategy TEXT NOT NULL,
            confidence REAL NOT NULL,
            text_similarity REAL,
            reviewed INTEGER DEFAULT 0,
            resolved_as TEXT,
            reviewed_at TEXT,
            UNIQUE(opinion_a, opinion_b)
        );

        CREATE INDEX IF NOT EXISTS idx_dupcand_a ON duplicate_candidates(opinion_a);
        CREATE INDEX IF NOT EXISTS idx_dupcand_b ON duplicate_candidates(opinion_b);
        CREATE INDEX IF NOT EXISTS idx_dupcand_reviewed ON duplicate_candidates(reviewed);

        -- Pipeline run provenance
        CREATE TABLE IF NOT EXISTS provenance (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
            operation TEXT NOT NULL,
            command TEXT,
            source_paths TEXT,
            rows_affected INTEGER,
            notes TEXT
        );

        -- Westlaw volume processing progress
        CREATE TABLE IF NOT EXISTS westlaw_progress (
            id INTEGER PRIMARY KEY,
            volume INTEGER NOT NULL,
            reporter TEXT NOT NULL DEFAULT 'N.D.',
            opinions_total INTEGER,
            opinions_matched INTEGER,
            opinions_not_found INTEGER,
            corrections_applied INTEGER,
            downloaded_at TEXT,
            processed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
            source_path TEXT,
            notes TEXT
        );

        -- Checkpoint tracking for citation extraction
        CREATE TABLE IF NOT EXISTS cite_extract_progress (
            opinion_id INTEGER PRIMARY KEY REFERENCES opinions(id),
            processed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now'))
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS opinions_fts USING fts5(
            case_name,
            text_content,
            content='opinions',
            content_rowid='id',
            tokenize='porter unicode61'
        );

        -- Triggers to keep FTS in sync
        CREATE TRIGGER IF NOT EXISTS opinions_ai AFTER INSERT ON opinions BEGIN
            INSERT INTO opinions_fts(rowid, case_name, text_content)
            VALUES (new.id, new.case_name, new.text_content);
        END;

        CREATE TRIGGER IF NOT EXISTS opinions_ad AFTER DELETE ON opinions BEGIN
            INSERT INTO opinions_fts(opinions_fts, rowid, case_name, text_content)
            VALUES ('delete', old.id, old.case_name, old.text_content);
        END;

        CREATE TRIGGER IF NOT EXISTS opinions_au AFTER UPDATE ON opinions BEGIN
            INSERT INTO opinions_fts(opinions_fts, rowid, case_name, text_content)
            VALUES ('delete', old.id, old.case_name, old.text_content);
            INSERT INTO opinions_fts(rowid, case_name, text_content)
            VALUES (new.id, new.case_name, new.text_content);
        END;
    """)
