"""figures.db — reproduced figures (plat maps, survey drawings, photos, diagrams,
tables-as-image) extracted from the court PDFs, served over MCP.

figures.db ships as its own release asset and is ATTACH-ed onto the shared MCP
connection under alias ``fig`` exactly like the primary-law corpora and AG opinions,
so a chambers install that lacks it simply serves no figures. The `[[Image here]]`
figure pipeline (Phase-1 vision classification + PDF-scan false-negative recovery)
builds it via scripts/build_figures_db.py.

Table `fig.opinion_figures`: one row per figure, keyed by canonical `cite` (stable
across re-ingest) with `opinion_id` as a convenience; carries kind/caption/page +
the image BLOB.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from platformdirs import user_data_path

FIG_CORPUS = {"file": "figures.db", "alias": "fig", "label": "ND opinion figures"}


def resolve_figures_db_path() -> Path:
    """Locate figures.db independent of working directory (mirrors resolve_ag_db_path)."""
    env = os.environ.get("NDCOURTS_FIGURES_DB")
    if env:
        return Path(env).expanduser()
    bundled = Path(__file__).resolve().parent.parent / FIG_CORPUS["file"]
    if bundled.exists():
        return bundled
    return user_data_path("ndcourts-mcp", appauthor=False) / FIG_CORPUS["file"]


def attach_figures(conn: sqlite3.Connection, *, read_only: bool = False) -> bool:
    """ATTACH figures.db onto an existing connection under alias 'fig'.

    Returns True if attached (or already attached), False if the file is absent.
    Mirrors ag_corpus.attach_ag.
    """
    alias = FIG_CORPUS["alias"]
    existing = {r["name"] for r in conn.execute("PRAGMA database_list")}
    if alias in existing:
        return True
    path = resolve_figures_db_path()
    if not path.exists():
        return False
    target = f"file:{path}?mode=ro" if read_only else str(path)
    conn.execute(f"ATTACH DATABASE ? AS {alias}", (target,))
    return True
