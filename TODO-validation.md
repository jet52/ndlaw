# TODO — Path to a Fully Validated Corpus

Progress map for reaching full two-source validation of every ND Supreme Court opinion 1890–present. Updated 2026-04-24.

**End goal:** a corpus accurate enough to be offered to the ND Supreme Court as the authoritative text of its opinions, or at least a reliable proxy. That bar is higher than "useful research tool" — it drives the provenance, reversibility, and verification standards below.

## Status snapshot

| Era | Opinions | Primary source | Cross-check coverage | Status |
|-----|----------|----------------|----------------------|--------|
| 1890–1924 | ~3,748 | CourtListener NW (OCR) | Westlaw vols 1–52 applied | ✓ Complete (metadata); text-merge triage pending for 455 rows |
| 1924–1932 | 1,119 | CourtListener NW (OCR) | Westlaw vols 53–62 applied | ✓ Complete (metadata) |
| 1932–1953 | ~1,687 | CourtListener NW/NW2d (OCR) | Westlaw vols 63–79 pending | ⏳ 17 vols to go |
| 1953–1996 | ~8,476 | CourtListener NW2d (OCR) | None — N.D. Reports series ended | ⚠ Targeted only |
| 1997–2019 | 5,978 | ndcourts.gov | archive.ndcourts.gov: 5,312 (89%) | ⏳ 666 archive-gap remaining (source-attachment fixed 2026-04-18) |
| 2020–present | 1,542 | ndcourts.gov | NW2d linked where available | ✓ Source-attachment fixed 2026-04-18 |

Totals below are "outstanding units of review work," not opinions.

## 1 · Westlaw cross-check — finish the N.D. Reports series

- [ ] Download and process Westlaw vols 63–79 (17 volumes, ~1,687 opinions, 1932–1953). Vols 1–62 complete as of 2026-04-24.
  - Workflow already proven on vols 1–62. Two-volume Westlaw searches work well; daily Quick Check limits apply.
  - Each volume yields 5–80+ metadata corrections (author swaps, date fixes). Later vols trend higher.
  - Progress tracked in `westlaw_progress` table; resume via `ingest_westlaw status`.
- [ ] **Triage 455 `merge_westlaw_text` errors (as of 2026-04-21 run).** Opinions where a Westlaw source exists but the text-similarity guard blocks a safe text replacement. Almost certainly a mix of (a) real mismatches where Westlaw has the wrong case (don't replace), (b) legitimate cases where OCR noise pushed similarity below threshold (should replace — loosen threshold or manual confirm), and (c) cases where the Westlaw .doc pairs to the wrong opinion row in the DB. Build a report: for each of the 455, show the Westlaw citation, the DB opinion's citation, the similarity score, and a side-by-side text snippet. Sort by similarity descending so the easy wins surface first. Do not auto-apply — this is a human-review pass for authoritative-text work. Tool: `merge_westlaw_text --errors-report` (to add).
- [ ] **Case-name sweep across vols 1–62.** Every Westlaw ingest so far has run with `--case-names skip`, deferring the case-name deltas. Vols 49–52 had 42 skipped diffs; vols 53–54 added 39 (15 + 24); vols 55–57 added 56 (19 + 21 + 16); vols 58–62 added 82 more (23 + 10 + 20 + 14 + 15); across vols 1–62 the backlog is likely several hundred. Westlaw's case names are typically cleaner than NW/NW2d's ALL CAPS headnote-style names, but not always right (headnote drift, "et al." handling, abbreviation style). Build a review tool that presents each diff with citation, DB value, Westlaw value, and both text snippets so the human can pick or edit. Output as a named changelog batch per volume (`westlaw-nd-volNN-casenames`). Revisit cadence: batch through it after every 10 volumes or so rather than per-volume — easier to stay in context.

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

- [x] Write `audit_sources` to measure the gap (2026-04-18).
- [x] Write `backfill_sources` pass: for every opinion with parallel citations, check filesystem for expected markdown/HTML and insert missing `opinion_sources` rows. 5,548 rows linked on 2026-04-18 (batch `backfill-sources-insert`).
- [x] Promote ndcourts.gov to primary for 1997+ opinions where the ND source now exists. 5,260 opinions flipped on 2026-04-18 (batch `backfill-sources-promote`).
- [x] Fix the root cause in `ingest.py` so future ingests record every available source in `opinion_sources`, not just the first one encountered (2026-04-18, commit `4e16481`). Added `_record_source` helper called from all four ingest paths (NW/NW2d fresh + dedup, ND fresh + dedup; ND dedup also promotes to primary for 1997+). Verified idempotent by re-running ingest against the backfilled DB — no duplicate rows, no re-flipped primaries. Spot-checked `merge_nd_metadata.py` (doesn't touch `opinion_sources` — safe) and `ingest_westlaw.py` (already inserts correctly — line 424).
- [x] Align `opinions.source_path` and `opinion_sources.is_primary` with `opinions.source_reporter` (2026-04-18). `align_primary_source --apply` rewrote 5,281 stale source_path values and flipped 34 primary flags on westlaw-sourced opinions where `merge_westlaw_text` had updated source_reporter without touching opinion_sources. Verified integrity: every opinion has exactly one primary source row. Root cause also fixed in `merge_westlaw_text.py` so future runs won't reopen the gap.
- [ ] Text_content alignment: 85 opinions are ND-primary but have no `[¶N]` markers. Inspection showed these are short disciplinary orders where neither the NW2d nor the ND version has paragraph markers, so replacement would be no-op content. No action needed unless a future source (e.g., Westlaw Quick Check) provides a cleaner text for specific ones — capture case-by-case.
- [ ] Resolve the 2 known cross-source leaks that name+date dedup missed: Holter v. City of Mandan (IDs 17670/19516) and Swanson v. Larson (IDs 17913/19616).
- [ ] Resolve Goetz v. Goetz duplicate: opinions 19722 (source: `markdown/2023/2023ND120.md`, case_name "Goetz v. Goetz, et al.") and 20385 (source: `NW2d/988/553.md`, case_name "Goetz v. Goetz") both have citation "2023 ND 53" in the `citations` table — a citation collision from mis-ingest, discovered during the refs-migration audit. One of them likely belongs to a different opinion. Confirm which row is canonical, merge or fix citations.

## 5 · New-opinions pipeline — keep the DB current

`/Users/jerod/code/scraper` has a weekly launchd job (`com.jerod.ndsc-scraper`, Fridays 07:00) that runs `weekly_scrape.sh`. It writes JSON metadata and PDFs to `~/refs/nd/opin/` but is supposed to also write markdown under `markdown/<year>/<year>ND<n>.md` — that step is currently failing silently. The scraper's cache logic treats `existing_data.get('markdown_path')` as "markdown exists" without checking the filesystem.

- [x] Unify source trees so scraper output and ndcourts-mcp ingest agree on paths. `~/refs/opin/` is now backward-compat symlinks into `~/refs/nd/opin/` (2026-04-18, batch `refs-migration-nd-opin`). `ndcourts_mcp.ingest` now reads from `~/refs/nd/opin/`.
- [ ] Fix the scraper's markdown-write path in `~/code/scraper/scraper/opinion_processor.py`. The `--skip-analysis` branch at line 752 skips whenever `existing_data.get('markdown_path')` is truthy without verifying the file is on disk. Change the check to `markdown_path and Path(COURT_DATA_DIR/markdown_path).exists()`. `needs_filesystem_reprocessing` already does this correctly — the skip-analysis branch just has a separate, broken early exit.
- [ ] Once the scraper writes markdown again, verify its output vs. our ingest expectations: paragraph markers `[¶N]`, no weird `I N   T H E   S U P R E M E   C O U R T` spacing. The `markdown_cleanup.py` module in the scraper is supposed to handle this — confirm it's being called in the PDF-extract path.
- [ ] Add a post-scrape step (invoked from `weekly_scrape.sh`) that runs `python -m ndcourts_mcp.ingest` (incremental) + `cite_extract` + `quality_scan` against any new opinions. Log the delta.
- [ ] Chain the ingest job to the scraper's launchd job (or register a second launchd job at e.g. Fri 08:00 that runs the ingest). Keep concerns separate so a scrape failure doesn't block ingest and vice versa.
- [ ] Add a heartbeat check: if `MAX(date_filed)` in opinions.db is more than 3 weeks behind today's date, alert (log line on shell startup or email).
- [ ] One-off: verify we aren't missing any 2026 opinions released between the last known release (2026 ND 70, 2026-03-26) and today.
- [ ] Escalation to marker: the scraper's pdfminer extraction fails on scanned/corrected/imaged PDFs. Plumb an escalation path that detects extraction failures (e.g., text < 100 chars/page, or fails the quality score threshold) and re-runs those PDFs through `~/code/markdown-opin/` (marker-based pipeline). Marker is slow (~30s/PDF) so this should be an on-demand escalation, not a default step.

## 6 · Duplicate review queue

- [ ] Work through the 713 unreviewed citation-overlap dup candidates via the Dup Queue UI. Post-tightening (citation + text similarity), these are real candidates rather than collisions.
- [ ] Keep the name+date+text strategy running on new ingests; it stays at 0 unreviewed currently.

## 7 · Missing source files — small gaps

Cases where the opinion record claims a source but the underlying file is absent. Discovered by `audit_sources`.

- [ ] Recover `~/refs/nd/opin/markdown/1997/1997ND5.md` (State v. Torres, 1997-01-16, opinion id 20383). Not on disk; adjacent files 1997ND50–59 exist. Re-scrape from ndcourts.gov or restore from `~/refs/nd/opin/1997_opinions.json`.
- [ ] Recover `~/refs/nd/opin/markdown/1998/1998ND22.md` (State v. Schmidt, 1998-01-22, opinion id 20384). Same pattern — adjacent 1998ND220–228 exist but not the single-digit file.
- [ ] Investigate whether the missing-file pattern is systemic to low-numbered ND opinions (ND5, ND22 ⇒ possibly naming collision with ND50/ND220 during download). Re-run `audit_sources` periodically to catch new gaps.

## 8 · Quality and metadata cleanup — long tail

- [ ] 17 opinions with `overall_score < 0.5`. Review in the low-quality queue; most will be OCR-garbled early-1900s opinions that Westlaw vols 45–79 will fix.
- [ ] 90 opinions with no author and not per_curiam. Run `python -m ndcourts_mcp.review` and `auto_author` to recover what's recoverable.
- [ ] Rebuild pre-1997 judges field (panel membership) from `justices.py` service dates plus disqualification lines in opinion text. Currently unusable from CourtListener metadata.

## 9 · Definition of "fully validated"

An opinion is considered validated when:
- It has at least two independent source texts linked in `opinion_sources` (OR it sits in the 1953–1996 single-source era and has been either auto-verified against Westlaw Quick Check or manually spot-checked), AND
- Its author, date_filed, and case_name have been confirmed against a non-OCR source (ndcourts.gov, Westlaw, or bound reporter), AND
- `overall_score >= 0.5`, AND
- Parallel citations are populated from metadata, not just the ingest source.

Progress metric to track: `% of opinions meeting all four criteria`, by decade, in `get_database_stats`.
