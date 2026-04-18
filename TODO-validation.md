# TODO — Path to a Fully Validated Corpus

Progress map for reaching full two-source validation of every ND Supreme Court opinion 1890–present. Updated 2026-04-18.

## Status snapshot

| Era | Opinions | Primary source | Cross-check coverage | Status |
|-----|----------|----------------|----------------------|--------|
| 1890–1920 | 3,268 | CourtListener NW (OCR) | Westlaw vols 1–44 applied | ✓ Complete |
| 1920–1953 | ~3,286 | CourtListener NW/NW2d (OCR) | Westlaw vols 45–79 pending | ⏳ 35 vols to go |
| 1953–1996 | ~8,476 | CourtListener NW2d (OCR) | None — N.D. Reports series ended | ⚠ Targeted only |
| 1997–2019 | 5,978 | ndcourts.gov | archive.ndcourts.gov: 5,312 (89%) | ⚠ 666 gap, plus source-attachment bug |
| 2020–present | 1,541 | ndcourts.gov + NW2d | Both exist but not linked in `opinion_sources` | ⚠ Source-attachment bug |

Totals below are "outstanding units of review work," not opinions.

## 1 · Westlaw cross-check — finish the N.D. Reports series

- [ ] Download and process Westlaw vols 45–79 (35 volumes, ~3,286 opinions, 1920–1953)
  - Workflow already proven on vols 1–44. Two-volume Westlaw searches work well; daily Quick Check limits apply.
  - Each volume yields 5–40 metadata corrections (author swaps, date fixes).
  - Progress tracked in `westlaw_progress` table; resume via `ingest_westlaw status`.

## 2 · 1953–1996 single-source gap — targeted Westlaw validation

N.D. Reports stopped at vol 79 (1953). Between 1953 and 1996, CourtListener NW2d is the only source. No bound ND reporter exists to Quick Check against, so full-corpus validation isn't possible — but Westlaw Quick Check can still be run on targeted batches where the CL text looks problematic.

- [ ] Build a "low-confidence" batch picker: rank 1953–1996 opinions by (quality_score < 0.6) OR (missing author) OR (author matches junk pattern) OR (date_filed looks suspicious). Output a ranked CSV for Westlaw Quick Check runs.
- [ ] Run Westlaw Quick Check on top-100 low-confidence batches until yield drops below some threshold (e.g., <2 corrections per 50 opinions).
- [ ] Tag validated opinions so they don't get re-queued.

## 3 · 1997–2019 multi-source cross-check

Three sources exist: ndcourts.gov markdown, CourtListener NW2d, archive.ndcourts.gov HTML. All three carry ¶ markers (except CL). Current `opinion_sources` coverage: 1990s 29%, 2000s 90%, 2010s 85%.

- [ ] Close the 666-opinion gap in archive.ndcourts.gov coverage for 1997–2019. Rerun `scrape_archive --all --ingest` against the list of opinions currently missing an `archive` row in `opinion_sources`.
- [ ] Multi-source diff audit: for opinions with 2+ sources, flag pairs where text differs by >N% or paragraph numbering disagrees. Route to Dup Queue / reader pane for human review.

## 4 · 2020+ source-attachment fix (**the matching rework you flagged**)

The issue isn't missed duplicates — name+date matching actually catches 2020s cross-source pairs (only 2 genuine leaks: Holter 2020-07-22 and Swanson 2021-12-09). The issue is that when a CourtListener NW2d opinion is ingested with parallel `20XX ND X` citations, the dedup merge correctly avoids creating a duplicate row — but the ndcourts.gov markdown file at `~/refs/opin/ND/YYYY/YYYYNDn.md` is never linked as a secondary source. 616 of the 925 ND-primary 2020s opinions carry an NW2d citation, yet only 1 has both source_reporters recorded in `opinion_sources`.

This matters because: (a) we can't text-diff between sources if we never recorded the second source, (b) ndcourts.gov is the authoritative text for 1997+ but NW2d is currently "primary" for 616 of the 2020s opinions, and (c) the same bug almost certainly affects 2000s and 2010s merges as well.

- [ ] Write a `backfill_sources` pass: for every opinion with parallel citations, check the filesystem for a matching markdown/json at each expected path and insert a row in `opinion_sources` if missing. For neutral cites (`YYYY ND N`), look under `~/refs/opin/ND/YYYY/YYYYND{N}.md`. For NW2d, look under `~/refs/opin/NW2d/{vol}/{page}.md`. For archive, reuse `scrape_archive` matching.
- [ ] After backfill, for 1997+ opinions where ndcourts.gov source exists, set it as `is_primary=1` in `opinion_sources` and optionally update the opinions row's `source_reporter` to `ND`. Keep NW2d as secondary. ndcourts.gov is authoritative per project policy.
- [ ] Fix the root cause in the merge logic (in `ingest.py` / `merge_nd_metadata.py`) so future ingests record all available sources, not just the first one hit.
- [ ] Resolve the 2 known cross-source leaks: Holter v. City of Mandan (IDs 17670/19516) and Swanson v. Larson (IDs 17913/19616).

## 5 · New-opinions pipeline — keep the DB current

Existing state: `/Users/jerod/code/scraper` has a weekly launchd job (`com.jerod.ndsc-scraper`, Fridays 07:00) that runs `weekly_scrape.sh` and writes JSON to `~/refs/nd/opin/`. **That output is not wired into the ndcourts-mcp ingest.** The ingest reads from `~/refs/opin/ND/{year}/YYYYND{n}.md` — a different directory, populated by some other (unknown) process.

- [ ] Decide: (a) extend `weekly_scrape.sh` to also write markdown to `~/refs/opin/ND/{year}/` in the format our ingest expects, or (b) teach `ndcourts_mcp.ingest` to read directly from `~/refs/nd/opin/{year}_opinions.json`. Option (b) removes the sync step.
- [ ] Add a post-scrape step that runs `python -m ndcourts_mcp.ingest` (incremental, not --rebuild) + `cite_extract` + `quality_scan` against any new opinions, then commits the updated `opinions.db` (if we want it committed) or logs the delta.
- [ ] Register a second launchd job (or chain it to the existing one) that runs the ingest after the scrape finishes. Keep the two concerns separate so a scrape failure doesn't block ingest and vice versa.
- [ ] Add a heartbeat check: if the DB's `MAX(date_filed)` is more than 3 weeks behind today, alert (email / log line visible in shell startup). Catches silent scraper failures.
- [ ] One-off: verify we aren't missing any 2026 opinions released between the last scrape (2026-04-17) and today. Expected max through 2026-04-18 is still 2026 ND 70 (2026-03-26 was the last release).

## 6 · Duplicate review queue

- [ ] Work through the 713 unreviewed citation-overlap dup candidates via the Dup Queue UI. Post-tightening (citation + text similarity), these are real candidates rather than collisions.
- [ ] Keep the name+date+text strategy running on new ingests; it stays at 0 unreviewed currently.

## 7 · Quality and metadata cleanup — long tail

- [ ] 17 opinions with `overall_score < 0.5`. Review in the low-quality queue; most will be OCR-garbled early-1900s opinions that Westlaw vols 45–79 will fix.
- [ ] 90 opinions with no author and not per_curiam. Run `python -m ndcourts_mcp.review` and `auto_author` to recover what's recoverable.
- [ ] Rebuild pre-1997 judges field (panel membership) from `justices.py` service dates plus disqualification lines in opinion text. Currently unusable from CourtListener metadata.

## 8 · Definition of "fully validated"

An opinion is considered validated when:
- It has at least two independent source texts linked in `opinion_sources` (OR it sits in the 1953–1996 single-source era and has been either auto-verified against Westlaw Quick Check or manually spot-checked), AND
- Its author, date_filed, and case_name have been confirmed against a non-OCR source (ndcourts.gov, Westlaw, or bound reporter), AND
- `overall_score >= 0.5`, AND
- Parallel citations are populated from metadata, not just the ingest source.

Progress metric to track: `% of opinions meeting all four criteria`, by decade, in `get_database_stats`.
