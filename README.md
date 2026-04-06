# ndcourts-mcp

MCP server providing access to North Dakota Supreme Court opinions (1889–present). Built on SQLite with FTS5 full-text search, served via FastMCP.

## Current Capabilities

### MCP Tools (9 tools)

| Tool | Purpose |
|------|---------|
| `lookup_opinion` | Retrieve opinion by any citation (neutral, N.W.2d, N.W.) |
| `get_opinion_text` | Read opinion text in paginated chunks |
| `get_opinion_metadata` | Metadata-only lookup (no text) |
| `search_opinions` | Full-text search with date/author filters |
| `list_opinions_by_date` | Browse opinions by date range |
| `get_database_stats` | Corpus summary, top authors, by-decade counts |
| `get_voting_record` | Justice votes on a specific opinion |
| `get_justice_stats` | Authorship count, dissent rate for a justice |
| `search_by_case_type` | Filter by case type (criminal, civil, etc.) |

### Database

- **20,382 opinions** from 1890–2026
- **33,217 citation records** linking neutral cites, N.W.2d, and N.W. citations
- **Full-text search** via SQLite FTS5 with porter stemming
- **Changelog table** for auditable, revertible corrections

### Data Sources

| Source | Coverage | Data |
|--------|----------|------|
| CourtListener (NW) | ~6,000 opinions, 1890–1997 | Text + JSON metadata (case name, date, judges, citations) |
| CourtListener (NW2d) | ~12,200 opinions, 1941–present | Text + JSON metadata |
| ndcourts.gov scrape (ND) | ~7,150 opinions, 1997–present | Markdown text with ¶ markers |
| ndcourts.gov metadata | ~7,150 opinions, 1997–present | Case name, date, author, case type, highlight, voting record, justice panel, unanimity, ndcourts.gov URL |

### Data Corrections Applied

6,100+ corrections across 19 batches, all logged in the `changelog` table. See [CHANGELOG-data.md](CHANGELOG-data.md) for details.

- Case normalization (ALL CAPS → title case)
- OCR misread consolidation (Birdzell, Bronson, Bruce, Burke, Christianson, Fisk, etc.)
- Per curiam detection
- Full-name → last-name normalization for surrogates
- Manual review corrections via interactive tool
- Westlaw Quick Check validation (author, date corrections from 46 pre-1920 opinions)
- Unicode ligature normalization (Æ→Ae, œ→oe) in case names
- Auto-detected authors from opinion text (257 opinions with junk-word authors recovered)

## Setup

```bash
# Create venv and install
python3 -m venv .venv
.venv/bin/pip install -e .

# Build the database (requires ~/refs/opin/)
.venv/bin/python3 -m ndcourts_mcp.ingest --rebuild

# Merge ndcourts.gov metadata (requires ~/refs/nd/opin/)
.venv/bin/python3 -m ndcourts_mcp.merge_nd_metadata

# Apply corrections
.venv/bin/python3 -m ndcourts_mcp.cleanup apply
```

### Claude Code Integration

Add to `~/.mcp.json`:

```json
{
  "mcpServers": {
    "ndcourts": {
      "type": "stdio",
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "ndcourts_mcp.server"],
      "cwd": "/path/to/ndcourts-mcp"
    }
  }
}
```

## CLI Tools

| Command | Purpose |
|---------|---------|
| `python -m ndcourts_mcp.ingest [--rebuild]` | Ingest opinions from ~/refs/opin/ |
| `python -m ndcourts_mcp.merge_nd_metadata` | Merge ndcourts.gov JSON metadata |
| `python -m ndcourts_mcp.cleanup apply [--dry-run]` | Apply pending corrections |
| `python -m ndcourts_mcp.cleanup revert <batch>` | Revert a correction batch |
| `python -m ndcourts_mcp.cleanup log` | Show changelog summary |
| `python -m ndcourts_mcp.review [--author X] [--min-count N] [--flagged]` | Interactive author review |
| `python -m ndcourts_mcp.ingest_westlaw <dir> [--apply] [--batch NAME]` | Compare/correct from Westlaw .doc downloads |

## Data Quality: Known Issues and Remaining Cleanup

### Author field (~580 opinions still need attention)

**Junk words as authors (~340 opinions).** CourtListener's parser extracted words from opinion text as "judges" for the older NW opinions. The author was derived from this bad data. Common examples: "Being", "Been", "Dist", "Any", "Action", "Account", "Below", "First", "Other". These should be set to NULL, but many can be recovered by detecting "LastName, J." lines in the opinion text using the review tool.

**Root cause:** Old NW opinions include a disqualification boilerplate at the end, e.g.:
> FISK, J., disqualified, and Hon, CHAS. A. POLLOCK, judge of the Third judicial district, sat by request.

CourtListener's parser treated the entire line as a comma-separated judge list, producing entries like "Chas", "Hon", "Pollock", "Third", "Request", "Dist".

**Single-count OCR noise (~140 opinions).** One-off garbled author values. Low priority — most can be auto-detected from text or set to NULL.

**"Chas" (8 opinions).** Fragment of "Chas. A. Pollock" or "Chas. Fisk" (Charles). Reviewed and corrected via manual review tool (2026-04-04).

### Judges field

**Pre-1997 judges data is largely unusable.** Same CourtListener parsing issue as the author field — the "judges" value is OCR fragments from opinion text, not a clean list of participating justices.

**Post-1997 opinions have clean data** from the ndcourts.gov metadata merge (`all_justices` and `voting_record` fields).

**Potential fix:** For opinions where we have the court composition dates (from `justices.py`), we could infer the default panel and note substitutions from disqualification lines in the text.

### Dates

**~5 opinions with placeholder dates.** ND-sourced opinions where the date couldn't be extracted and defaulted to YYYY-01-01.

### Case names

**Pre-1997 case names from CourtListener are generally good.** Some have OCR artifacts but are readable.

**Post-1997 case names from ndcourts.gov are clean.**

### Duplicate detection

Some opinions may exist under different citations without being linked. The ingest pipeline deduplicates by CourtListener `cluster_id` and by matching parallel citations, but edge cases may remain.

## Proposed: Interactive Data Browser

A terminal or web-based tool for browsing and spot-checking the database:

- Browse by date range, author, case type, or citation
- Side-by-side comparison of our data vs. source files
- Bulk export of citations for Westlaw Quick Check validation
- Ingest corrected data from Westlaw downloads to validate and fix OCR errors

### Westlaw Validation Workflow

1. Export a Word document with a list of citations from the database
2. Upload to Westlaw Quick Check — it resolves all citations and provides download links
3. Download the clean Westlaw opinion text
4. Diff against our OCR text to identify and correct errors
5. Use Westlaw metadata (case name, date, author, judges) to validate our fields

This is particularly valuable for the pre-1920 opinions where OCR quality is worst.

### Tested

Batch1: 46 pre-1920 opinions downloaded as .doc from Westlaw Quick Check. Comparison found 10 author corrections, 3 date corrections, and confirmed opinion text is substantially identical with only minor OCR artifacts. Ready to apply with `--apply`.

## Next Steps

### Immediate (ready to do)

1. ~~**Apply Westlaw batch1 corrections**~~ — Done (2026-04-05). 10 author + 3 date + 6 ligature corrections applied.
2. ~~**Investigate Murphy v. District Court mismatch**~~ — Partially resolved (2026-04-05). Both State v. Poull and Murphy v. District Court share citation 14 N.D. 557 with different N.W. parallel cites. Both exist as separate DB records, but sharing an N.D. start page is suspicious given both opinions are multi-page. Flagged in `notes` field for manual verification.
3. **Continue manual author review** — ~580 opinions with unrecognized authors. Run `python -m ndcourts_mcp.review --min-count 2` to work through the remaining junk words and OCR noise. Most can be auto-detected from "LastName, J." in the opinion text or set to NULL.

### Short-term

4. **Simplify MCP tools to reduce token cost** — The current 9-tool surface area is expensive for LLM clients that load all tool schemas into context. Consolidate overlapping tools (e.g., merge `get_opinion_metadata` into `lookup_opinion`, combine `get_justice_stats` and `get_voting_record`) to reduce the number of tools and total schema tokens.
5. **Generate more Westlaw citation batches** — Export citations for pre-1920 opinions in groups of 50, download via Quick Check, and run through `ingest_westlaw.py` to systematically validate and correct metadata.
6. **Rebuild judges field for pre-1997 opinions** — Use court composition dates from `justices.py` to infer the default panel, then parse disqualification/substitution lines from opinion text to note surrogates.
7. **Null out remaining junk-word authors** — After manual review identifies which can be recovered from text, set the rest (Being, Been, Dist, Any, Action, etc.) to NULL in a batch.

### Medium-term

8. **Text quality correction** — For opinions where we have Westlaw downloads, consider replacing OCR text with Westlaw's clean text (keeping our case headers/citations separate).
9. **Interactive data browser** — Terminal or web-based tool for browsing and spot-checking the database.
10. **Citation network analysis** — Build a graph of which opinions cite which others by parsing citation references within opinion text.

## Reference Files

| File | Purpose |
|------|---------|
| `ndcourts_mcp/justices.py` | All 52 elected justices (1889–present) with service dates |
| `CHANGELOG-data.md` | Human-readable log of every correction batch |
