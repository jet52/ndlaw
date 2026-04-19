# ndcourts-mcp

MCP server providing access to North Dakota Supreme Court opinions (1889–present).

## Architecture

- **SQLite + FTS5** for full-text and metadata search
- **FastMCP** for the MCP server
- **~/refs/nd/opin/** contains the source data (markdown opinions + CourtListener JSON metadata). The refs/CLAUDE.md at ~/refs/CLAUDE.md is the authoritative layout doc; `~/refs/opin/*` exists as backward-compat symlinks.

## Data sources

Opinions live under `~/refs/nd/opin/`:
- `markdown/<year>/<year>ND<n>.md` — neutral-cite opinions (1997–present), ~7K files, markdown with ¶ markers
- `NW2d/<vol>/<page>.md` — North Western Reporter 2d, ~12K files with paired .json metadata from CourtListener
- `NW/<vol>/<page>.md` — North Western Reporter 1st series, ~6K files with paired .json metadata
- `N.D./<vol>/<page>-<slug>.doc` — Westlaw .doc files, bound N.D. Reports vols 1–44
- `archive/<year>/<docket>.htm` — archive.ndcourts.gov HTML, 1997–2019
- `pdfs/<year>/<year>ND<n>.pdf` — scraper's raw PDFs (parallel tree, not text-indexed)
- `<year>_opinions.json` — scraper's CourtListener-style metadata (not a source file)

JSON metadata includes: cluster_id, case_name, case_name_full, date_filed, citations (parallel), judges, docket_number, absolute_url.

Many opinions exist in multiple sources (e.g., both markdown/ and NW2d/). The ingest pipeline deduplicates by matching parallel citations from the JSON metadata, then records every available source in `opinion_sources`.

## Dependencies

- Python 3.12+
- fastmcp
- sqlite3 (stdlib)
