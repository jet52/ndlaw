"""ND Judicial Ethics Advisory Committee opinions corpus (``jeac_opinions.db``).

Like AG opinions (``ag_corpus.py``), JEAC opinions are immutable, dated
documents — an opinions-flavored schema (one row per opinion, no version
history), ATTACHed onto the shared MCP connection under alias ``jeac``.

The corpus is tiny (22 opinions, 1990–2025, published at
ndcourts.gov/supreme-court/committees/judicial-ethics-advisory-committee/opinions)
and heavily construes the N.D. Code of Judicial Conduct — jetcite's existing
``ndcodejudconduct`` recognizers cover the outbound cites.

Cross-linking mirrors the AG contract: ``jeac_text_citations`` matches
``text_citations``'s column set; ``jeac_cited_by_court`` holds inbound
court→JEAC edges built by scanning opinions.db prose (courts reference these
as e.g. "Judicial Ethics Advisory Committee ... opinion" — rarely with a
number, so unresolved edges keep raw_text).
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

from platformdirs import user_data_path

JEAC_CORPUS = {
    "file": "jeac_opinions.db",
    "alias": "jeac",
    "label": "ND Judicial Ethics Advisory Committee Opinions",
}

# Opinion numbers are <year>-<seq>: two-digit years through the 1990s
# ("90-1" … "96-1"), four-digit after ("2000-1" … "2025-1").
_NUM_RE = re.compile(r"^(\d{2}|\d{4})-(\d+)$")


def opinion_year(opinion_number: str) -> int | None:
    m = _NUM_RE.match((opinion_number or "").strip())
    if not m:
        return None
    y = int(m.group(1))
    if y < 100:
        # Two-digit years: the committee's 19xx run is 90-1 … 96-1, but the
        # site also slips into two-digit form for modern opinions (the 2022-1
        # PDF is named "Opinion 22-1.pdf"). Pivot at 90: >=90 → 19xx, else 20xx.
        return 1900 + y if y >= 90 else 2000 + y
    return y


def cite_key(opinion_number: str) -> str:
    """Normalize to a stable lookup key: four-digit year + seq (``1990-1``).

    Makes ``90-1`` and ``1990-1`` collide; lowercases and strips cosmetic
    punctuation otherwise.
    """
    s = (opinion_number or "").strip().lower()
    m = _NUM_RE.match(s)
    if m:
        y = opinion_year(s)
        return f"{y}-{int(m.group(2))}"
    return re.sub(r"[^a-z0-9\-]+", "", s)


def canonical_jeac_cite(opinion_number: str) -> str:
    """Display citation: ``N.D. Jud. Ethics Advisory Op. 96-1`` (number verbatim)."""
    return f"N.D. Jud. Ethics Advisory Op. {opinion_number.strip()}"


def resolve_jeac_db_path() -> Path:
    """Locate jeac_opinions.db (mirrors ag_corpus.resolve_ag_db_path)."""
    env = os.environ.get("NDCOURTS_JEAC_DB")
    if env:
        return Path(env).expanduser()
    bundled = Path(__file__).resolve().parent.parent / JEAC_CORPUS["file"]
    if bundled.exists():
        return bundled
    return user_data_path("ndcourts-mcp", appauthor=False) / JEAC_CORPUS["file"]


def get_jeac_connection(
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
            "SELECT name FROM sqlite_master WHERE type='table' AND name='jeac_opinions'"
        ).fetchone()
        if not have:
            raise FileNotFoundError(
                f"JEAC opinions database at {db_path} has no schema; install the "
                f"jeac_opinions.db release asset."
            )
    return conn


def create_jeac_schema(conn: sqlite3.Connection) -> None:
    """Create the JEAC-opinions schema (opinions-flavored, immutable rows)."""
    conn.executescript("""
        -- One row per published JEAC opinion.
        CREATE TABLE IF NOT EXISTS jeac_opinions (
            id INTEGER PRIMARY KEY,
            opinion_number TEXT NOT NULL,   -- verbatim from the committee page ("90-1")
            jeac_cite TEXT NOT NULL,        -- canonical display cite
            cite_key TEXT NOT NULL,         -- normalized key (four-digit year: "1990-1")
            year INTEGER,                   -- opinion year (from the number)
            date_issued TEXT,               -- ISO date parsed from the opinion text, or NULL
            digest TEXT,                    -- the committee page's question summary(ies)
            status TEXT NOT NULL DEFAULT 'active',  -- 'active' | 'withdrawn' | 'superseded'
                                            -- (page carries a compare-with-current-Code NOTE;
                                            --  no per-opinion status markers as of 2026-07)
            text_content TEXT,              -- full opinion text
            text_source TEXT,               -- 'pdf-text' | 'ocr'
            source_url TEXT,                -- absolute ndcourts.gov PDF URL
            source_path TEXT,               -- local cache under ~/refs/nd/jeac/
            scraped_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
            UNIQUE(opinion_number)
        );

        CREATE INDEX IF NOT EXISTS idx_jeac_cite_key ON jeac_opinions(cite_key);
        CREATE INDEX IF NOT EXISTS idx_jeac_year ON jeac_opinions(year);

        -- Outbound citations extracted by jetcite (mirrors text_citations).
        CREATE TABLE IF NOT EXISTS jeac_text_citations (
            id INTEGER PRIMARY KEY,
            jeac_opinion_id INTEGER NOT NULL REFERENCES jeac_opinions(id),
            normalized TEXT NOT NULL,
            cite_type TEXT NOT NULL,
            jurisdiction TEXT,
            raw_text TEXT NOT NULL,
            url TEXT,
            ocr_derived INTEGER DEFAULT 0,
            UNIQUE(jeac_opinion_id, normalized)
        );
        CREATE INDEX IF NOT EXISTS idx_jeac_tc_opinion ON jeac_text_citations(jeac_opinion_id);
        CREATE INDEX IF NOT EXISTS idx_jeac_tc_normalized ON jeac_text_citations(normalized);

        -- INBOUND edges: court opinions citing a JEAC opinion. court_opinion_id
        -- is opinions.db opinions.id — DERIVED (rebuild after opinions.db
        -- changes), so no FK. jeac_opinion_id NULL = referenced opinion not
        -- identifiable (courts usually cite these descriptively, without a
        -- number); the edge is still recorded with raw_text preserved.
        CREATE TABLE IF NOT EXISTS jeac_cited_by_court (
            id INTEGER PRIMARY KEY,
            court_opinion_id INTEGER NOT NULL,
            jeac_opinion_id INTEGER REFERENCES jeac_opinions(id),
            normalized TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            match_kind TEXT NOT NULL,        -- 'number' | 'prose'
            resolution TEXT,                 -- 'exact' | NULL (unresolved)
            UNIQUE(court_opinion_id, normalized)
        );
        CREATE INDEX IF NOT EXISTS idx_jeac_cbc_jeac ON jeac_cited_by_court(jeac_opinion_id);
        CREATE INDEX IF NOT EXISTS idx_jeac_cbc_court ON jeac_cited_by_court(court_opinion_id);

        -- Pipeline provenance + auditable corrections (house discipline).
        CREATE TABLE IF NOT EXISTS provenance (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
            operation TEXT NOT NULL,
            command TEXT,
            source_paths TEXT,
            rows_affected INTEGER,
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS changelog (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
            batch TEXT NOT NULL,
            jeac_opinion_id INTEGER REFERENCES jeac_opinions(id),
            field TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            authority TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_jeac_changelog_batch ON changelog(batch);

        -- FTS over number + digest + text (external-content, trigger-synced).
        CREATE VIRTUAL TABLE IF NOT EXISTS jeac_opinions_fts USING fts5(
            opinion_number,
            digest,
            text_content,
            content='jeac_opinions',
            content_rowid='id',
            tokenize='porter unicode61'
        );
        CREATE TRIGGER IF NOT EXISTS jeac_opinions_ai AFTER INSERT ON jeac_opinions BEGIN
            INSERT INTO jeac_opinions_fts(rowid, opinion_number, digest, text_content)
            VALUES (new.id, new.opinion_number, COALESCE(new.digest,''), COALESCE(new.text_content,''));
        END;
        CREATE TRIGGER IF NOT EXISTS jeac_opinions_ad AFTER DELETE ON jeac_opinions BEGIN
            INSERT INTO jeac_opinions_fts(jeac_opinions_fts, rowid, opinion_number, digest, text_content)
            VALUES ('delete', old.id, old.opinion_number, COALESCE(old.digest,''), COALESCE(old.text_content,''));
        END;
        CREATE TRIGGER IF NOT EXISTS jeac_opinions_au AFTER UPDATE ON jeac_opinions BEGIN
            INSERT INTO jeac_opinions_fts(jeac_opinions_fts, rowid, opinion_number, digest, text_content)
            VALUES ('delete', old.id, old.opinion_number, COALESCE(old.digest,''), COALESCE(old.text_content,''));
            INSERT INTO jeac_opinions_fts(rowid, opinion_number, digest, text_content)
            VALUES (new.id, new.opinion_number, COALESCE(new.digest,''), COALESCE(new.text_content,''));
        END;
    """)
    conn.commit()


def attach_jeac(conn: sqlite3.Connection, *, read_only: bool = False) -> bool:
    """ATTACH jeac_opinions.db under alias 'jeac' (mirrors attach_ag)."""
    alias = JEAC_CORPUS["alias"]
    existing = {r["name"] for r in conn.execute("PRAGMA database_list")}
    if alias in existing:
        return True
    path = resolve_jeac_db_path()
    if not path.exists():
        return False
    target = f"file:{path}?mode=ro" if read_only else str(path)
    conn.execute(f"ATTACH DATABASE ? AS {alias}", (target,))
    return True
