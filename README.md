# ndcourts-mcp

MCP server providing access to North Dakota Supreme Court opinions (1889–present). Built on SQLite with FTS5 full-text search, served via FastMCP. Includes a web-based opinion browser with merge/diff tools.

## Current Capabilities

### MCP Tools (8 tools)

| Tool | Purpose |
|------|---------|
| `lookup_opinion` | Retrieve opinion by any citation (neutral, N.W.2d, N.W.) with optional text |
| `get_opinion_text` | Read opinion text in paginated chunks |
| `search_opinions` | Full-text search with date/author filters |
| `list_opinions_by_date` | Browse opinions by date range |
| `get_database_stats` | Corpus summary, source breakdown, quality stats, provenance |
| `justice_info` | Voting record for a case, or aggregate stats for a justice |
| `search_by_case_type` | Filter by case type (criminal, civil, etc.) |
| `get_citing_opinions` | Find opinions that cite a given opinion |

### Web Opinion Browser

Full-featured web UI at `http://localhost:8765` with:
- Tabulator table with sortable columns (date, author, citations, quality score, cited-by count)
- Reader pane with opinion text, voting record, citing opinions, and multi-source comparison
- Meld-style side-by-side diff/merge tool for deduplication and source comparison
- Quality filter (low/mid/high), duplicate queue, flag system
- Keyboard navigation (vim-style j/k, Tab for hunks, Space to toggle)

### Database

- **20,383 opinions** from 1890–2026
- **113K+ cited-by links** from citation extraction
- **Text quality scores** for all opinions (OCR artifacts, HTML contamination, etc.)
- **716 duplicate candidates** for review (citation-overlap pairs now require text-similarity confirmation)
- **Full changelog** for auditable, revertible corrections

### Data Sources

| Source | Coverage | Data |
|--------|----------|------|
| CourtListener (NW) | ~6,000 opinions, 1890–1997 | Text + JSON metadata |
| CourtListener (NW2d) | ~12,200 opinions, 1941–present | Text + JSON metadata |
| ndcourts.gov (ND) | ~2,135 opinions, 1997–present | Markdown text with ¶ markers |
| ndcourts.gov metadata | ~7,150 opinions, 1997–present | Case type, voting record, justice panel, etc. |
| Westlaw Quick Check | Vols 1–44 N.D. Reports + 40 individual cases | .doc files with clean text |
| archive.ndcourts.gov | ~5,300 opinions, 1997–2019 | HTML with ¶ markers |

### Data Corrections Applied

7,100+ corrections across 65+ batches, all logged in the `changelog` table. See [CHANGELOG-data.md](CHANGELOG-data.md) for details.

- Case normalization (ALL CAPS → title case)
- OCR misread consolidation (Birdzell, Bronson, Bruce, Burke, Christianson, Fisk, etc.)
- Per curiam detection
- Full-name → last-name normalization for surrogates
- Manual review corrections via interactive tool
- Westlaw Quick Check validation (vols 1–44 + 40 individual cases)
- Unicode ligature normalization (Æ→Ae, œ→oe) in case names
- Auto-detected authors from opinion text (257 opinions recovered)
- Text replacement with clean Westlaw text (36 pre-1997 opinions)
- Citation-based dedup tightened to require text similarity (eliminated false positives from citation collisions where different cases share a reporter page)

## Setup

```bash
# Create venv and install
python3 -m venv .venv
.venv/bin/pip install -e .

# Build the database (see BUILD.md for full instructions)
.venv/bin/python3 -m ndcourts_mcp.ingest --rebuild
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

### Web UI

```bash
source .venv/bin/activate
python -m uvicorn ndcourts_mcp.webapp:app --port 8765
# For read-only mode:
NDCOURTS_READONLY=1 python -m uvicorn ndcourts_mcp.webapp:app --port 8765
```

## CLI Tools

| Command | Purpose |
|---------|---------|
| `python -m ndcourts_mcp.ingest [--rebuild]` | Ingest opinions from ~/refs/nd/opin/ |
| `python -m ndcourts_mcp.merge_nd_metadata` | Merge ndcourts.gov JSON metadata |
| `python -m ndcourts_mcp.cleanup apply` | Apply pending corrections |
| `python -m ndcourts_mcp.cleanup revert <batch>` | Revert a correction batch |
| `python -m ndcourts_mcp.review` | Interactive author review |
| `python -m ndcourts_mcp.auto_author [--apply]` | Auto-detect authors from text |
| `python -m ndcourts_mcp.cite_extract` | Extract citations and build cited_by graph |
| `python -m ndcourts_mcp.quality_scan [--rescan]` | Score text quality for all opinions |
| `python -m ndcourts_mcp.dedup_scan` | Detect duplicate opinions |
| `python -m ndcourts_mcp.audit [--save]` | Check for missing opinions and data gaps |
| `python -m ndcourts_mcp.quality_report` | Generate .docx of worst-quality opinions |
| `python -m ndcourts_mcp.ingest_westlaw status` | Show Westlaw download progress |
| `python -m ndcourts_mcp.ingest_westlaw process <dir> --volume N --apply` | Process Westlaw volume |
| `python -m ndcourts_mcp.ingest_westlaw export V1 V2` | Export citations for Westlaw lookup |
| `python -m ndcourts_mcp.merge_westlaw_text --apply` | Replace text with Westlaw copies |
| `python -m ndcourts_mcp.scrape_archive --all --ingest` | Scrape archive.ndcourts.gov |

## Ongoing Work

### Continue Westlaw Downloads
Volumes 1–44 of N.D. Reports are processed. Resume with volume 45. Use `ingest_westlaw status` to check progress and `ingest_westlaw export` to generate citation lists for Quick Check.

### Review Duplicate Candidates
716 candidates found via citation overlap (with text-similarity confirmation), name+date+text similarity, and minhash fingerprinting. Use the "Dup Queue" button in the web UI to review and merge or dismiss.

### Multi-Source Text Comparison
5,300+ opinions have archive.ndcourts.gov sources available alongside CourtListener text. Use the "Sources" section in the reader pane to compare and apply corrections. ndcourts.gov text is authoritative for 1997+ opinions — use Westlaw/archive only as reference for corrections, not wholesale replacement.

### Author Review
~580 opinions with unrecognized authors remain. Run `python -m ndcourts_mcp.review --min-count 2` to work through junk words and OCR noise.

### Rebuild Judges Field
Pre-1997 judges data from CourtListener is largely unusable. Could infer panels from court composition dates in `justices.py` and parse disqualification lines from opinion text.

### Court Rules (Future)
Add ND court rules as a separate data source — either a new DB table or a separate project. Rules are the court's other key output alongside opinions.

## Reference Files

| File | Purpose |
|------|---------|
| `BUILD.md` | Step-by-step database rebuild instructions |
| `CHANGELOG-data.md` | Log of every correction batch |
| `MISSING_OPINIONS.md` | Audit report of citation gaps and data anomalies |
| `ndcourts_mcp/justices.py` | All 52 elected justices (1889–present) with service dates |
