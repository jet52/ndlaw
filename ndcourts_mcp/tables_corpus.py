"""tables.db — reproduced numeric TABLES from opinions, served over MCP.

A side channel that mirrors figures.db: the linearized-table cleanup (see
scripts/scan_numeric_tables.py) reconstructs each table's geometry from a
geometry-bearing source (Westlaw .doc / court PDF / archive HTML). The STRUCTURED
CELLS are the single source of truth; the inline monospace block spliced into
opinions.text_content (under a bracketed ``[Table N]`` anchor) and the markdown /
HTML renderings stored here are ALL build products of those cells — so the two
copies cannot drift (an invariant enforces inline == render_monospace(cells)).

tables.db ATTACH-es under alias ``tbl`` exactly like figures.db (``fig``); an
install that lacks it simply serves no tables.

Table `tbl.opinion_tables`: one row per table, keyed by ``opinion_id`` (+ a
display ``cite``) and ``table_index`` (matches the inline ``[Table N]``).
"""
from __future__ import annotations

import json
import os
import sqlite3
from html import escape as _h
from pathlib import Path

from platformdirs import user_data_path

TBL_CORPUS = {"file": "tables.db", "alias": "tbl", "label": "ND opinion tables"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS opinion_tables (
  id            INTEGER PRIMARY KEY,
  opinion_id    INTEGER NOT NULL,
  cite          TEXT,
  table_index   INTEGER NOT NULL,       -- 1-based; matches inline [Table N]
  caption       TEXT,                   -- title row if any, else editorial
  ncols         INTEGER,
  cells_json    TEXT NOT NULL,          -- JSON: list[list[str]] full grid (source of truth)
  render_monospace TEXT NOT NULL,       -- == the inline block in text_content
  render_markdown  TEXT NOT NULL,
  render_html      TEXT NOT NULL,
  source        TEXT                    -- provenance tag for the table's origin
);
CREATE INDEX IF NOT EXISTS ix_tbl_oid ON opinion_tables(opinion_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_tbl_oid_idx ON opinion_tables(opinion_id, table_index);
"""


def resolve_tables_db_path() -> Path:
    env = os.environ.get("NDCOURTS_TABLES_DB")
    if env:
        return Path(env).expanduser()
    bundled = Path(__file__).resolve().parent.parent / TBL_CORPUS["file"]
    if bundled.exists():
        return bundled
    return user_data_path("ndcourts-mcp", appauthor=False) / TBL_CORPUS["file"]


def attach_tables(conn: sqlite3.Connection, *, read_only: bool = False) -> bool:
    """ATTACH tables.db under alias 'tbl'. True if attached/present, False if absent."""
    alias = TBL_CORPUS["alias"]
    if alias in {r["name"] for r in conn.execute("PRAGMA database_list")}:
        return True
    path = resolve_tables_db_path()
    if not path.exists():
        return False
    target = f"file:{path}?mode=ro" if read_only else str(path)
    conn.execute(f"ATTACH DATABASE ? AS {alias}", (target,))
    return True


# ── canonical renderers (grid = list[list[str]]) ──────────────────────────────
# A leading single-cell row is a table title/caption; the next row is the header.

def _split(grid: list[list[str]]):
    """Return (title, body, ncol). A leading single-cell row is a title. Ragged
    rows are padded to a common width, then trailing all-empty columns (a common
    Westlaw/​extraction artifact) are dropped so the grid isn't padded wider than
    its real data."""
    title = None
    body = grid
    # A leading single-cell row is a caption only when it spans a WIDER table
    # below it; a genuinely 1-column grid has no title (every row is one cell).
    if (grid and len(grid[0]) == 1 and len(grid) > 1
            and max(len(r) for r in grid[1:]) > 1):
        title, body = grid[0][0], grid[1:]
    ncol = max(len(r) for r in body)
    body = [r + [""] * (ncol - len(r)) for r in body]
    # drop fully-empty rows (extraction spacers), keeping at least a header
    body = [r for r in body if any(c.strip() for c in r)] or body
    # drop trailing columns that are empty in every row
    while ncol > 1 and all(r[ncol - 1].strip() == "" for r in body):
        ncol -= 1
        body = [r[:ncol] for r in body]
    return title, body, ncol


def render_monospace(grid: list[list[str]]) -> str:
    """Fixed-width block. Single-column grids render as a plain aligned column
    (no header rule); multi-column grids get a header row + dashed rule."""
    title, body, ncol = _split(grid)
    w = [max(len(r[j]) for r in body) for j in range(ncol)]

    def fmt(r):
        return "  ".join(r[j].ljust(w[j]) if j == 0 else r[j].rjust(w[j])
                         for j in range(ncol)).rstrip()

    out = []
    if title:
        out += [title, ""]
    headerless = ncol == 1 or all(c.strip() == "" for c in body[0])
    if headerless:
        # bare column, or a table whose source gives no header row: no rule
        rows = body[1:] if (ncol > 1 and all(c.strip() == "" for c in body[0])) else body
        out += [fmt(r) for r in rows]
        return "\n".join(out)
    out.append(fmt(body[0]))
    out.append("  ".join("-" * w[j] for j in range(ncol)))
    out += [fmt(r) for r in body[1:]]
    return "\n".join(out)


def render_markdown(grid: list[list[str]]) -> str:
    title, body, ncol = _split(grid)
    esc = lambda s: s.replace("|", "\\|")
    lines = []
    if title:
        lines += [f"**{esc(title)}**", ""]
    lines.append("| " + " | ".join(esc(c) for c in body[0]) + " |")
    lines.append("| " + " | ".join("---" for _ in range(ncol)) + " |")
    for r in body[1:]:
        lines.append("| " + " | ".join(esc(c) for c in r) + " |")
    return "\n".join(lines)


def render_html(grid: list[list[str]]) -> str:
    title, body, ncol = _split(grid)
    parts = ['<table class="opinion-html-table">']
    if title:
        parts.append(f"<caption>{_h(title)}</caption>")
    parts.append("<thead><tr>"
                 + "".join(f"<th>{_h(c)}</th>" for c in body[0])
                 + "</tr></thead>")
    parts.append("<tbody>")
    for r in body[1:]:
        parts.append("<tr>" + "".join(f"<td>{_h(c)}</td>" for c in r) + "</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def caption_of(grid: list[list[str]]) -> str | None:
    title, _, _ = _split(grid)
    return title


def cells_json(grid: list[list[str]]) -> str:
    return json.dumps(grid, ensure_ascii=False)
