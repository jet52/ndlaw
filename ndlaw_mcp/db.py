"""Connection management for the served databases.

The public tree ships the serving half of this module only: path
resolution and the read-only connection the MCP server and web UI open.
Schema creation, migration, and the changelog/provenance writers belong to
the ingest pipeline, which is not part of this distribution — the released
databases are built elsewhere and served read-only here.
"""

import os
import sqlite3
from pathlib import Path

from platformdirs import user_data_path


def resolve_db_path() -> Path:
    """Locate opinions.db independent of working directory or install layout.

    Resolution order:
      1. ``NDLAW_DB`` environment variable (explicit override; the deprecated
         pre-v3.0.0 ``NDCOURTS_DB`` still works as a fallback).
      2. ``opinions.db`` bundled alongside the source tree / release tarball.
      3. The per-user data directory (where a pip/uvx install keeps it); a DB
         left in the deprecated ``ndcourts-mcp`` data dir is still found.
    """
    env = os.environ.get("NDLAW_DB") or os.environ.get("NDCOURTS_DB")
    if env:
        return Path(env).expanduser()
    bundled = Path(__file__).resolve().parent.parent / "opinions.db"
    if bundled.exists():
        return bundled
    data = user_data_path("ndlaw-mcp", appauthor=False) / "opinions.db"
    legacy = user_data_path("ndcourts-mcp", appauthor=False) / "opinions.db"
    if not data.exists() and legacy.exists():
        return legacy
    return data


DEFAULT_DB_PATH = resolve_db_path()


def get_connection(
    db_path: Path = DEFAULT_DB_PATH, *, must_exist: bool = True, read_only: bool = False
) -> sqlite3.Connection:
    """Open the opinions DB.

    read_only=True opens with SQLite's mode=ro (URI filename), so the engine
    itself rejects any write — the MCP server uses this so that even a bug in
    the serving stack cannot alter the corpus. Ingest and fix scripts keep the
    default read-write connection.
    """
    if must_exist and not Path(db_path).exists():
        raise FileNotFoundError(
            f"opinions.db not found at {db_path}. Download the database release "
            f"asset or set NDLAW_DB to its location (see the README 'Quick "
            f"start'). Pass must_exist=False to create a new database."
        )
    if read_only:
        # uri=True also makes ATTACH on this connection honor URI filenames,
        # which corpus.attach_corpora() relies on to attach corpora read-only.
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    if not read_only:
        conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
