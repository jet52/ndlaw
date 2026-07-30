"""Versioned primary-law corpora (Constitution, court rules, statutes, admin code).

Opinions are immutable point-in-time events and live in ``opinions.db`` (see
``db.py``). The other ND primary-law sources are *living, amendable* documents:
a provision has a stable identity (e.g. ``N.D.C.C. § 12.1-20-03``) and a chain
of dated *versions*. This module models that valid-time history in a separate
SQLite file per corpus, which the MCP server ``ATTACH``-es onto the opinions
connection so a single session can answer cross-corpus, point-in-time questions
("what did this statute say on the date that opinion applied it").

Design notes:
  * Valid-time only. We track when each version was *in force*
    (``effective_start`` .. ``effective_end``), not transaction time.
  * One file per corpus keeps ``opinions.db`` pristine for its public goal and
    lets each corpus build/release on its own cadence.
  * Provenance/changelog mirror the opinions discipline (every version carries a
    source; corrections are logged) — the foundation for the rules' higher bar.
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

from platformdirs import user_data_path

# Corpus registry: name -> (db filename, ATTACH schema alias, display label).
# The schema alias is how attached tables are qualified in SQL, e.g.
# ``SELECT * FROM const.provisions``.
CORPORA: dict[str, dict[str, str]] = {
    "const": {"file": "constitution.db", "alias": "const", "label": "ND Constitution"},
    "rule": {"file": "rules.db", "alias": "rules", "label": "ND Court Rules"},
    "ndcc": {"file": "statutes.db", "alias": "statutes", "label": "N.D.C.C. (statutes)"},
    "admin": {"file": "admincode.db", "alias": "admin", "label": "ND Admin. Code"},
}

# Far-future sentinel for "still in force" so BETWEEN comparisons are total.
OPEN_ENDED = "9999-12-31"

# Provision → provision cross-reference edges, extracted from version text by
# ``xref_extract`` (jetcite). Edges live in the SOURCE provision's DB and are
# keyed by version (point-in-time) with canonical-citation targets (re-ingest
# safe, resolved across corpora via the cross-link contract). Fully derived —
# rebuildable at any time from text.
XREF_SCHEMA = """
    CREATE TABLE IF NOT EXISTS provision_xrefs (
        id INTEGER PRIMARY KEY,
        provision_id INTEGER NOT NULL REFERENCES provisions(id),
        version_id INTEGER NOT NULL REFERENCES provision_versions(id),
        to_corpus TEXT NOT NULL,      -- 'ndcc' | 'admin' | 'const' | 'rule'
        to_citation TEXT NOT NULL,    -- canonical (jetcite normalized) cite
        to_cite_key TEXT NOT NULL,    -- corpus.cite_key(to_citation)
        raw_text TEXT NOT NULL,       -- the reference as printed
        UNIQUE(version_id, to_citation)
    );
    CREATE INDEX IF NOT EXISTS idx_xrefs_version
        ON provision_xrefs(version_id);
    CREATE INDEX IF NOT EXISTS idx_xrefs_provision
        ON provision_xrefs(provision_id);
    CREATE INDEX IF NOT EXISTS idx_xrefs_target
        ON provision_xrefs(to_corpus, to_cite_key);
"""


def resolve_corpus_db_path(corpus: str) -> Path:
    """Locate a corpus DB file independent of working directory or install layout.

    Resolution order mirrors ``db.resolve_db_path``:
      1. ``NDCOURTS_<CORPUS>_DB`` env var (e.g. ``NDCOURTS_CONST_DB``).
      2. The file bundled alongside the source tree / release tarball.
      3. The per-user data directory.
    """
    if corpus not in CORPORA:
        raise ValueError(f"unknown corpus {corpus!r}; expected one of {list(CORPORA)}")
    env = os.environ.get(f"NDCOURTS_{corpus.upper()}_DB")
    if env:
        return Path(env).expanduser()
    filename = CORPORA[corpus]["file"]
    bundled = Path(__file__).resolve().parent.parent / filename
    if bundled.exists():
        return bundled
    return user_data_path("ndcourts-mcp", appauthor=False) / filename


def cite_key(citation: str) -> str:
    """Normalize a citation to a stable lookup key.

    Collapses whitespace, lowercases, and drops punctuation that varies by
    source (periods, section signs, non-breaking spaces) while keeping the
    alphanumerics and hyphens that carry meaning in ND numbering
    (``12.1-20-03``, ``art. I § 8``). Conservative on purpose: two citations
    map to the same key only if they differ solely in cosmetic punctuation.
    """
    s = citation.lower().replace("§", " ")
    # Normalize the spelled-out "article(s)" to the stored "art." abbreviation so
    # "N.D. Const. article I" keys the same as the canonical "art. I". No stored
    # citation uses the full word, so this only ever maps query input onto the
    # existing key, never shifts a stored key.
    s = re.sub(r"\barticles?\b", "art", s)
    # Drop abbreviation dots ("n.d." -> "nd", "art." -> "art") but keep decimal
    # dots inside ND numbering ("12.1-20-03"): only remove a dot that follows a
    # letter, never one between digits.
    s = re.sub(r"(?<=[a-z])\.", "", s)
    # Drop section/subsection filler words so "art VI sec 8" == "art. VI, § 8".
    s = re.sub(r"\b(?:sec|section|subsec|subsection|subdiv|subdivision)\b", " ", s)
    # Keep alphanumerics, hyphens, and (decimal) dots; everything else -> space.
    s = re.sub(r"[^a-z0-9.\- ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def resolve_cite_key(
    conn: sqlite3.Connection, corpus_alias: str, citation: str
) -> str | None:
    """Return the *stored* ``cite_key`` for ``citation``, or None if no provision
    matches.

    Two-tier so the common path stays index-backed: first an exact
    ``cite_key = ?`` equality (an index hit — covers Constitution, N.D.C.C.,
    admin code, and the compact-dotted rule sets), then a whitespace-insensitive
    fallback for citations whose *stored* form spaces its abbreviations
    differently from the query (e.g. stored "N.D. Sup. Ct. Admin. R. 22" vs a
    compact "N.D.Sup.Ct.Admin.R. 22"). ``cite_key`` itself is whitespace-
    *sensitive*, so the fallback compares both sides with spaces removed; a
    corpus-wide check confirmed this collapses no two distinct provisions
    together. Returning the canonical stored key lets callers re-query by
    indexed equality.
    """
    q = f"{corpus_alias}." if corpus_alias and corpus_alias != "main" else ""
    key = cite_key(citation)
    hit = conn.execute(
        f"SELECT cite_key FROM {q}provisions WHERE cite_key = ? LIMIT 1", (key,)
    ).fetchone()
    if hit:
        return hit["cite_key"]
    hit = conn.execute(
        f"SELECT cite_key FROM {q}provisions WHERE REPLACE(cite_key, ' ', '') = ? LIMIT 1",
        (key.replace(" ", ""),),
    ).fetchone()
    return hit["cite_key"] if hit else None


def get_corpus_connection(
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
        # quick existence probe: the schema must have been created
        have = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='provisions'"
        ).fetchone()
        if not have:
            raise FileNotFoundError(
                f"corpus database at {db_path} has no schema; run the corpus "
                f"ingest or call create_corpus_schema()."
            )
    return conn


def create_corpus_schema(conn: sqlite3.Connection) -> None:
    """Create the versioned-provision schema for a single corpus DB."""
    conn.executescript("""
        -- Stable identity of a provision (one row per article/section/rule).
        CREATE TABLE IF NOT EXISTS provisions (
            id INTEGER PRIMARY KEY,
            corpus TEXT NOT NULL,        -- 'const' | 'rule' | 'ndcc' | 'admin'
            citation TEXT NOT NULL,      -- canonical, e.g. 'N.D.C.C. § 12.1-20-03'
            cite_key TEXT NOT NULL,      -- normalized lookup key (see corpus.cite_key)
            hierarchy TEXT,              -- JSON path: title/chapter/section | article/section | ruleset/number
            heading TEXT,                -- catchline / rule title
            status TEXT NOT NULL DEFAULT 'active',  -- active | repealed | superseded
            current_version_id INTEGER REFERENCES provision_versions(id),
            UNIQUE(corpus, cite_key)
        );

        -- Dated text versions. effective_end NULL == currently in force.
        -- effective_start NULL == original/unknown (treat as in force from -inf).
        CREATE TABLE IF NOT EXISTS provision_versions (
            id INTEGER PRIMARY KEY,
            provision_id INTEGER NOT NULL REFERENCES provisions(id),
            effective_start TEXT,        -- ISO date or NULL
            effective_end TEXT,          -- ISO date or NULL (= current)
            text_content TEXT NOT NULL,
            source_authority TEXT,       -- enacting/amending authority (session law, rule order, ballot measure)
            source_url TEXT,
            source_path TEXT,
            added_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
            batch TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_provisions_cite_key ON provisions(cite_key);
        CREATE INDEX IF NOT EXISTS idx_provisions_corpus ON provisions(corpus);
        CREATE INDEX IF NOT EXISTS idx_pv_provision ON provision_versions(provision_id);
        CREATE INDEX IF NOT EXISTS idx_pv_effective ON provision_versions(effective_start, effective_end);

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
            provision_id INTEGER REFERENCES provisions(id),
            version_id INTEGER REFERENCES provision_versions(id),
            field TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            authority TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_corpus_changelog_batch ON changelog(batch);

        -- Amendment EVENTS, distinct from full-text versions. We often know an
        -- amendment occurred (date + enacting authority) before we have captured
        -- the full prior text as a provision_version. This table records the
        -- complete amendment chronology; get_authority_history merges it with
        -- whatever provision_versions exist. version_id links an event to its
        -- captured full text when available (else NULL).
        CREATE TABLE IF NOT EXISTS amendments (
            id INTEGER PRIMARY KEY,
            provision_id INTEGER REFERENCES provisions(id),  -- NULL if not mapped to a current provision
            version_id INTEGER REFERENCES provision_versions(id),
            action TEXT,                 -- 'adopted' | 'amended' | 'repealed' | ...
            effective_date TEXT,         -- ISO date (NULL if only a raw label parsed)
            raw_date TEXT,               -- the source's human date string, verbatim
            election_date TEXT,          -- date the amendment was voted on (where known)
            affected TEXT,               -- affected section(s) as the source states them
            amendment_number TEXT,       -- sequential amendment number (where known)
            authority TEXT,              -- enacting authority, e.g. 'S.L. 1985, ch. 702'
            source_url TEXT,
            raw TEXT,                    -- the source annotation / subject, verbatim
            UNIQUE(provision_id, raw, effective_date)
        );

        CREATE INDEX IF NOT EXISTS idx_amendments_provision ON amendments(provision_id);
        CREATE INDEX IF NOT EXISTS idx_amendments_date ON amendments(effective_date);

        -- FTS over version text + citation/heading for full-text search.
        CREATE VIRTUAL TABLE IF NOT EXISTS provisions_fts USING fts5(
            citation,
            heading,
            text_content,
            content='provision_versions',
            content_rowid='id',
            tokenize='porter unicode61'
        );

        -- Structured subsection index: one row per <li> node parsed from a
        -- version's authoritative `html` (NDCC only, so far). Enables subsection
        -- pinpoint resolution (§ X(1)(a)) and a numbered-vs-lettered oracle.
        -- `text` is the node's OWN text (excludes nested children); assemble a
        -- full subtree by prefix-matching `pincite`.
        CREATE TABLE IF NOT EXISTS provision_subsections (
            id INTEGER PRIMARY KEY,
            provision_id INTEGER NOT NULL REFERENCES provisions(id),
            version_id INTEGER NOT NULL REFERENCES provision_versions(id),
            pincite TEXT NOT NULL,        -- Redbook pinpoint path, e.g. '(1)(a)(1)'
            printed_label TEXT NOT NULL,  -- as printed: '1.' 'a.' '(1)' '(a)'
            label_type TEXT NOT NULL,     -- 'num' | 'alpha' | 'pnum' | 'palpha'
            depth INTEGER NOT NULL,       -- 1..N nesting level
            seq INTEGER NOT NULL,         -- document order within the version
            text TEXT NOT NULL,
            UNIQUE(version_id, pincite)
        );
        CREATE INDEX IF NOT EXISTS idx_subsec_provision ON provision_subsections(provision_id, pincite);
        CREATE INDEX IF NOT EXISTS idx_subsec_version ON provision_subsections(version_id);
    """)
    # Additive migrations for pre-existing corpus DBs (CREATE TABLE IF NOT EXISTS
    # won't add columns to a table that already exists).
    have = {r[1] for r in conn.execute("PRAGMA table_info(amendments)")}
    for col in ("election_date", "affected", "amendment_number"):
        if col not in have:
            conn.execute(f"ALTER TABLE amendments ADD COLUMN {col} TEXT")
    # provision_versions.html: authoritative structured markup (ndlegis.gov JSON).
    pv_cols = {r[1] for r in conn.execute("PRAGMA table_info(provision_versions)")}
    if "html" not in pv_cols:
        conn.execute("ALTER TABLE provision_versions ADD COLUMN html TEXT")
    conn.executescript(XREF_SCHEMA)
    conn.commit()


def index_version_fts(
    conn: sqlite3.Connection, version_id: int, citation: str, heading: str | None, text: str
) -> None:
    """Add one provision_version row to the FTS index.

    FTS is content-backed by provision_versions but versions are written with
    a join to provisions for citation/heading, so we index explicitly at insert
    time rather than via a trigger (keeps the join logic in Python)."""
    conn.execute(
        "INSERT INTO provisions_fts(rowid, citation, heading, text_content) VALUES (?, ?, ?, ?)",
        (version_id, citation, heading or "", text),
    )


def lookup_provision_version(
    conn: sqlite3.Connection,
    corpus_alias: str,
    citation: str,
    as_of_date: str | None = None,
) -> sqlite3.Row | None:
    """Resolve a citation to the version in force on ``as_of_date``.

    ``corpus_alias`` is the ATTACH schema alias (e.g. 'const', 'statutes') or
    '' / 'main' when querying a corpus DB opened directly. ``as_of_date`` is an
    ISO date; None means the current version (effective_end IS NULL).
    """
    q = f"{corpus_alias}." if corpus_alias and corpus_alias != "main" else ""
    key = resolve_cite_key(conn, corpus_alias, citation)
    if key is None:
        return None
    if as_of_date is None:
        sql = (
            f"SELECT p.citation, p.heading, p.status, v.* "
            f"FROM {q}provisions p JOIN {q}provision_versions v "
            f"  ON v.id = p.current_version_id "
            f"WHERE p.cite_key = ?"
        )
        return conn.execute(sql, (key,)).fetchone()
    sql = (
        f"SELECT p.citation, p.heading, p.status, v.* "
        f"FROM {q}provisions p JOIN {q}provision_versions v "
        f"  ON v.provision_id = p.id "
        f"WHERE p.cite_key = ? "
        f"  AND COALESCE(v.effective_start, '0000-01-01') <= ? "
        f"  AND COALESCE(v.effective_end, ?) >= ? "
        f"ORDER BY v.effective_start DESC LIMIT 1"
    )
    return conn.execute(sql, (key, as_of_date, OPEN_ENDED, as_of_date)).fetchone()


# A trailing subsection pinpoint on a statute cite: normalize any of "(1)(a)",
# "(1)(a)", "1(a)", " subsec. (1)" into the canonical parenthesized path "(1)(a)".
_PIN_TOKEN = re.compile(r"\(?([0-9]+|[a-z]+|[ivxlc]+)\)?", re.I)


def normalize_pincite(pin: str) -> str:
    """'(1)(a)', '1(a)', '(1) (a)' -> '(1)(a)'. Empty/garbage -> ''."""
    if not pin:
        return ""
    return "".join(f"({m.group(1).lower()})" for m in _PIN_TOKEN.finditer(pin.strip()))


def lookup_subsection(
    conn: sqlite3.Connection,
    corpus_alias: str,
    citation: str,
    pincite: str,
    as_of_date: str | None = None,
) -> list[sqlite3.Row]:
    """Resolve a subsection pinpoint (§ X(1)(a)) to its node and subtree.

    Returns the matching subsection row plus every descendant, in document
    order (prefix-match on `pincite`). Empty list if the provision, version, or
    pincite is unknown / not indexed. `text` on each row is that node's own
    text; concatenate the returned rows to assemble the full subtree.
    """
    version = lookup_provision_version(conn, corpus_alias, citation, as_of_date)
    if version is None:
        return []
    path = normalize_pincite(pincite)
    if not path:
        return []
    q = f"{corpus_alias}." if corpus_alias and corpus_alias != "main" else ""
    sql = (
        f"SELECT pincite, printed_label, label_type, depth, seq, text "
        f"FROM {q}provision_subsections "
        f"WHERE version_id = ? AND (pincite = ? OR pincite LIKE ? ESCAPE '\\') "
        f"ORDER BY seq"
    )
    like = path.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "(%"
    return conn.execute(sql, (version["id"], path, like)).fetchall()


def attach_corpora(conn: sqlite3.Connection, *, read_only: bool = False) -> list[str]:
    """ATTACH every available corpus DB onto an existing connection.

    Returns the list of corpus names successfully attached. Missing corpus
    files are skipped silently (a chambers install may have only some corpora).
    Safe to call repeatedly: re-attaching an already-attached alias is ignored.

    read_only=True attaches each corpus with mode=ro; this requires the main
    connection to have been opened with URI filenames enabled (uri=True), as
    db.get_connection(read_only=True) does.
    """
    attached: list[str] = []
    existing = {r["name"] for r in conn.execute("PRAGMA database_list")}
    for name, meta in CORPORA.items():
        alias = meta["alias"]
        if alias in existing:
            attached.append(name)
            continue
        path = resolve_corpus_db_path(name)
        if not path.exists():
            continue
        target = f"file:{path}?mode=ro" if read_only else str(path)
        conn.execute(f"ATTACH DATABASE ? AS {alias}", (target,))
        attached.append(name)
    return attached
