# Building the Opinion Database

How to recreate `opinions.db` from source data. All commands assume you're in the project root with the virtualenv active.

## Prerequisites

- Python 3.12+
- Virtual environment: `python3 -m venv .venv && source .venv/bin/activate && pip install -e .`
- Source data in `~/refs/nd/opin/` (see Source Data below)

## Source Data

| Directory | Source | Coverage | Format |
|-----------|--------|----------|--------|
| `~/refs/nd/opin/NW/` | CourtListener | ~6,000 opinions, 1890–1997 | .md + .json metadata |
| `~/refs/nd/opin/NW2d/` | CourtListener | ~12,200 opinions, 1941–present | .md + .json metadata |
| `~/refs/nd/opin/markdown/` | ndcourts.gov scrape | ~7,150 opinions, 1997–present | .md with ¶ markers |
| `~/refs/nd/opin/N.D./{vol}/` | Westlaw Quick Check | Vols 1–44 (~3,300 opinions) | .doc files |
| `~/refs/nd/opin/archive/` | archive.ndcourts.gov | ~5,300 opinions, 1997–2019 | .htm files |
| `~/refs/nd/opin/pdfs/<year>/` | scraper | raw PDFs, weekly from ndcourts.gov | .pdf (not text-indexed) |
| `~/refs/nd/opin/<year>_opinions.json` | scraper | ~7,150 opinions, 1997–present | JSON (case_type, voting_record, etc.) |

## Build Steps (in order)

### 1. Ingest base opinions

```sh
python -m ndcourts_mcp.ingest --rebuild
```

Ingests NW → NW2d → ND in that order. Deduplicates by `cluster_id` and parallel citation matching. Creates `opinions`, `citations`, `opinion_sources`, and FTS index.

### 2. Merge ndcourts.gov metadata

```sh
python -m ndcourts_mcp.merge_nd_metadata
```

Enriches 1997+ opinions with case_type, voting_record, all_justices, unanimous, highlight, opinion_url, docket_number from ndcourts.gov JSON.

### 3. Apply data corrections

```sh
python -m ndcourts_mcp.cleanup apply
```

Applies all correction batches (case normalization, OCR misreads, per curiam detection, etc.). See CHANGELOG-data.md for batch details. All corrections are logged to the `changelog` table and can be reverted with `python -m ndcourts_mcp.cleanup revert <batch>`.

### 4. Auto-detect authors from text

```sh
python -m ndcourts_mcp.auto_author --apply
```

Recovers real authors from "LastName, J." lines in opinion text for opinions with junk-word authors.

### 5. Extract citations and build citation graph

```sh
python -m ndcourts_mcp.cite_extract
```

Scans all opinion text for citations using jetcite. Populates `text_citations` and `cited_by` tables. Uses multiprocessing; checkpoint-based so it can resume.

### 6. Process Westlaw downloads

```sh
# Volume-based (repeat for each volume):
python -m ndcourts_mcp.ingest_westlaw process input-data/vol8/ --volume 8 --apply --batch westlaw-nd-vol8 --case-names skip

# Individual case downloads:
python -m ndcourts_mcp.ingest_westlaw process input-data/low-quality/ --apply --batch westlaw-low-quality

# Replace text for pre-1997 opinions with Westlaw text:
python -m ndcourts_mcp.merge_westlaw_text --apply
```

### 7. Scrape archive.ndcourts.gov

```sh
python -m ndcourts_mcp.scrape_archive --all --ingest
```

Scrapes 1997–2019 opinions from the old court website. Adds `archive` source entries for existing opinions; creates new records for any missing opinions.

### 8. Score text quality

```sh
python -m ndcourts_mcp.quality_scan --rescan
```

Scores all opinions on OCR artifacts, garbage characters, HTML contamination, short-line ratio, and paragraph markers.

### 9. Run duplicate detection

```sh
python -m ndcourts_mcp.dedup_scan
```

Finds duplicate candidates via citation overlap, name+date+text similarity, and minhash fingerprinting.

### 10. Run audit

```sh
python -m ndcourts_mcp.audit --save
```

Checks for citation gaps, phantom citations, duplicate reporter citations, and volume coverage. Saves report to MISSING_OPINIONS.md.

## Verification

```sh
python -m ndcourts_mcp.audit
python -m ndcourts_mcp.ingest_westlaw status
sqlite3 opinions.db "SELECT COUNT(*) FROM opinions; SELECT COUNT(*) FROM provenance;"
```

## Pipeline Tools Reference

| Module | Purpose |
|--------|---------|
| `ingest.py` | Base ingest from ~/refs/opin/ |
| `merge_nd_metadata.py` | Enrich with ndcourts.gov JSON |
| `cleanup.py` | Batch corrections with audit trail |
| `auto_author.py` | Recover authors from text |
| `review.py` | Interactive author review |
| `cite_extract.py` | Citation extraction + cited_by graph |
| `ingest_westlaw.py` | Westlaw download processing |
| `merge_westlaw_text.py` | Replace text with Westlaw copies |
| `scrape_archive.py` | Scrape archive.ndcourts.gov |
| `quality_scan.py` | Text quality scoring |
| `dedup_scan.py` | Duplicate detection |
| `audit.py` | Missing opinion audit |
| `quality_report.py` | Generate .docx for Westlaw lookup |
