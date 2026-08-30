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
import re
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
  source        TEXT,                   -- provenance tag for the table's origin
  layout        TEXT NOT NULL DEFAULT 'mono'
);
CREATE INDEX IF NOT EXISTS ix_tbl_oid ON opinion_tables(opinion_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_tbl_oid_idx ON opinion_tables(opinion_id, table_index);
"""

# ── layout ───────────────────────────────────────────────────────────────────
# Two kinds of table live here, and they want different typography:
#
#   'mono'  — the numeric grid this corpus was built for (money columns, year
#             columns, caseload counts). Right-justified fixed-width columns are
#             exactly right, and the web renders the inline block verbatim in a
#             <pre>. This is the default and covers every table through 2026-08.
#   'prose' — cells that are long running text (2026 ND 34 ¶ 14 is the first:
#             a 4x6 grid of case citations). Right-justifying those is wrong and
#             the fixed-width block is far too wide to read, so the web renders
#             render_html as a real <table> instead, and the cells' `*…*`
#             emphasis becomes <em> (JT 2026-08-24).
#
# The inline text_content copy stays fixed-width for BOTH — it is the corpus's
# plain-text representation and the anti-drift invariant is keyed on it — but a
# prose table's columns are left-aligned, since right-justified sentences are
# an artifact of a renderer meant for numbers.
LAYOUTS = ("mono", "prose")

# The corpus emphasis grammar, identical to web_templates._ITAL (pinned by
# tests/test_tables_corpus.py): a single-asterisk pair whose content starts
# with a letter/quote/paren and contains a letter. `***` omissions, `* * *`,
# and `**NNN` second-series star pages can never match.
_ITAL = re.compile(
    r"(?<![\w*])\*(?=[^*\n]*[A-Za-z])"
    r"([A-Za-z(\"'‘“§$][^*\n]{0,250}?[^\s*]|[A-Za-z])(?<!\[)\*(?!\*)")


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Create the table if absent, and add any column a older tables.db lacks."""
    conn.executescript(SCHEMA)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(opinion_tables)")}
    if "layout" not in cols:
        conn.execute("ALTER TABLE opinion_tables "
                     "ADD COLUMN layout TEXT NOT NULL DEFAULT 'mono'")


def resolve_tables_db_path() -> Path:
    env = os.environ.get("NDLAW_TABLES_DB") or os.environ.get("NDCOURTS_TABLES_DB")
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
    # drop fully-empty rows (extraction spacers), keeping at least a header —
    # EXCEPT a leading all-empty row, which is the source's way of saying "no
    # header row": render_monospace/markdown/html then draw no header rule
    # (2026-08-17: the four archive-table splices of the quote reflow are
    # data-first tables — a net-income computation, a jury vote tally)
    lead_empty = bool(body) and ncol > 1 and not any(c.strip() for c in body[0])
    body = [r for r in body if any(c.strip() for c in r)] or body
    if lead_empty and body and any(re.search(r"\d", c) for c in body[0]):
        # …and only when the first REAL row is data (carries a digit): an
        # empty spacer above a worded header row (8132's elector list) is
        # still a spacer
        body = [[""] * ncol] + body
    # drop trailing columns that are empty in every row
    while ncol > 1 and all(r[ncol - 1].strip() == "" for r in body):
        ncol -= 1
        body = [r[:ncol] for r in body]
    return title, body, ncol


def render_monospace(grid: list[list[str]], layout: str = "mono") -> str:
    """Fixed-width block. Single-column grids render as a plain aligned column
    (no header rule); multi-column grids get a header row + dashed rule.

    ``layout='prose'`` left-aligns every column: right-justification reads as
    a decimal point on numbers and as damage on sentences."""
    title, body, ncol = _split(grid)
    w = [max(len(r[j]) for r in body) for j in range(ncol)]
    left = layout == "prose"

    def fmt(r):
        return "  ".join(r[j].ljust(w[j]) if (left or j == 0) else r[j].rjust(w[j])
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
    if ncol > 1 and not any(c.strip() for c in body[0]):
        # headerless: markdown needs a header row, so an empty one carries the rule
        lines.append("| " + " | ".join(" " for _ in range(ncol)) + " |")
        lines.append("| " + " | ".join("---" for _ in range(ncol)) + " |")
        body = body[1:]
    else:
        lines.append("| " + " | ".join(esc(c) for c in body[0]) + " |")
        lines.append("| " + " | ".join("---" for _ in range(ncol)) + " |")
        body = body[1:]
    for r in body:
        lines.append("| " + " | ".join(esc(c) for c in r) + " |")
    return "\n".join(lines)


def _cell_html(text: str, emphasis: bool) -> str:
    """Escape a cell, then (prose tables only) turn the corpus's `*…*` emphasis
    markers into <em>. Escaping ALWAYS happens first — the marker grammar is
    recognized in escaped text, never in raw DB text. Gated on the layout
    because a numeric grid's asterisks are the court's own table-footnote
    daggers (`$ 44,068.00*`, `499**`, `*****`), not emphasis."""
    esc = _h(text)
    return _ITAL.sub(lambda m: f"<em>{m.group(1)}</em>", esc) if emphasis else esc


def render_html(grid: list[list[str]], layout: str = "mono") -> str:
    title, body, ncol = _split(grid)
    em = layout == "prose"
    cls = "opinion-html-table tbl-prose" if em else "opinion-html-table"
    parts = [f'<table class="{cls}">']
    if title:
        parts.append(f"<caption>{_cell_html(title, em)}</caption>")
    if ncol > 1 and not any(c.strip() for c in body[0]):
        body = body[1:]                      # headerless: no <thead>
    else:
        parts.append("<thead><tr>"
                     + "".join(f"<th>{_cell_html(c, em)}</th>" for c in body[0])
                     + "</tr></thead>")
        body = body[1:]
    parts.append("<tbody>")
    for r in body:
        parts.append("<tr>" + "".join(f"<td>{_cell_html(c, em)}</td>" for c in r)
                     + "</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def caption_of(grid: list[list[str]]) -> str | None:
    title, _, _ = _split(grid)
    return title


def cells_json(grid: list[list[str]]) -> str:
    return json.dumps(grid, ensure_ascii=False)
