# TODO — Path to a Fully Validated Corpus

Progress map for reaching full two-source validation of every ND Supreme Court opinion 1890–present. Updated 2026-04-27.

**End goal:** a corpus accurate enough to be offered to the ND Supreme Court as the authoritative text of its opinions, or at least a reliable proxy. That bar is higher than "useful research tool" — it drives the provenance, reversibility, and verification standards below.

## Status snapshot

| Era | Opinions | Primary source | Cross-check coverage | Status |
|-----|----------|----------------|----------------------|--------|
| 1890–1924 | ~3,748 | CourtListener NW (OCR) | Westlaw vols 1–52 applied | ✓ Complete (metadata); text-merge triage pending for 455 rows |
| 1924–1938 | 1,618 | CourtListener NW (OCR) | Westlaw vols 53–68 applied | ✓ Complete (metadata) |
| 1938–1946 | 453 | CourtListener NW/NW2d (OCR) | Westlaw vols 69–74 applied | ✓ Complete (metadata) |
| 1946–1953 | 343 | CourtListener NW2d (OCR) | Westlaw vols 75–79 applied | ✓ Complete (metadata) |
| 1953–1996 | ~8,476 | CourtListener NW2d (OCR) | None — N.D. Reports series ended | ⚠ Targeted only |
| 1997–2019 | 5,978 | ndcourts.gov | archive.ndcourts.gov: 5,312 (89%) | ⏳ 666 archive-gap remaining (source-attachment fixed 2026-04-18) |
| 2020–present | 1,542 | ndcourts.gov | NW2d linked where available | ✓ Source-attachment fixed 2026-04-18 |

Totals below are "outstanding units of review work," not opinions.

## 1 · Westlaw cross-check — bound N.D. Reports series complete

- [x] Download and process Westlaw vols 75–79 (5 volumes, 343 opinions, 1946–1953). Applied 2026-04-27 — 10 date_filed corrections, 0 author corrections, 44 case-name diffs deferred. **All 79 volumes of the bound N.D. Reports series now Quick-Checked against Westlaw (1890–1953).**
- [x] Re-run `merge_westlaw_text --apply` to incorporate vols 49–79 .doc files (2026-04-27, batch `westlaw-text-merge-2026-04-27`). 2,733 opinions migrated to Westlaw text. Idempotency bug also fixed — query now skips already-merged opinions. **5,698 stale `source_path` rows backfilled** in the same session — long-standing bug where volume-based ingest recorded the staging path instead of the final archive path; root cause fixed in `ingest_westlaw.py`.
- [x] Triage merge_westlaw_text residuals — 137 → 29 in the 2026-04-27 session. Three parser fixes (modern Westlaw format, star-pagination + `PER CURIAM` + `District Judge` author markers, widened "All Citations" search) unlocked 108 of the 110 SKIP residuals. Tool added: `merge_westlaw_text --errors-report PATH`. Current report at `triage/westlaw-merge-residuals-2026-04-27.md` with the remaining 29 categorized.
- [x] Resolve the 9 wrong-pairings cluster from the residuals (2026-04-27, batch `westlaw-merge-residuals-2026-04-27-pairings` + `westlaw-text-merge-2026-04-27-pairings`). Each of nine vol/page locations had two short opinions (lead + per curiam follow-on) sharing an `<vol> N.D. <page>` cite; ingest had paired one .doc with the wrong opinion and orphaned the other. Fix: 9 deletions + 18 insertions in `opinion_sources`; all 18 newly-paired texts merged. Surfaced two side issues, captured below.
- [x] Resolve the remaining 20 residuals (2026-04-28). 14 Type X (parser was extracting body-only instead of full bound entry) re-merged via batch `westlaw-text-remerge-2026-04-28-full-bound` after parser fix in `ingest_westlaw.py:_extract_full_bound_text`. 6 Type Y (separate supplemental publications at distinct N.W. cites) inserted as new opinion rows 20386–20391 via batch `westlaw-supplemental-publications-2026-04-28`. 1 case (Klingenstein 2958) was already correct.
- [x] **CORPUS-WIDE syllabus recovery (2026-04-28).** Re-merged 5,701 of 5,744 westlaw-paired opinions through the new full-bound-entry parser. 4,717 pre-1953 opinions now contain "Syllabus by the Court"; the 1,022 without are correctly without (memoranda, per-curiam follow-ons). Batch `westlaw-syllabus-recovery-corpus-wide-2026-04-28`, 11,402 changelog rows, ~13 min wall-clock.
- [ ] **CORPUS-WIDE: identify additional Type Y supplemental publications still hiding in the corpus.** The 6 found in this session were the ones surfaced by `merge_westlaw_text` length-rejects on the 29 residuals. There are likely more — any opinion where the .doc's "All Citations" N.W. cite differs from the DB row's N.W. cite. Sweep: scan all westlaw-paired rows, parse each .doc, compare N.W. cite to DB primary, flag mismatches. Each is a candidate for a new opinion row (per `insert_supplemental_opinions.py`).
- [ ] **Detect Type Y at ingest time.** Update `ingest_westlaw.py` so a .doc whose All Citations N.W. cite differs from the matched DB row's N.W. cite is treated as a separate publication (creating a new opinion row), not paired with the existing row. Currently the volume-page filename collision is the only signal, which only catches some.
- [ ] **Pin down the "Syllabus by the Court" cutoff year.** Sampled scan shows the practice was alive 1890s–1950s (97%+ of Westlaw .docs in that range). Post-1953 the bound N.D. Reports series ended and we have very few Westlaw .docs to sample. CL's NW2d source files don't preserve syllabi (CL never did), so they're not informative. Quick test: download Westlaw .docs for ~10 opinions each from 1955, 1965, 1975, 1985, 1995 and check for "Syllabus by the Court" presence. Pinpointing the cutoff helps target the corpus-wide syllabus-recovery sweep above.
- [ ] **Dedup Ott v. Kelley 4484/4485** (252 N.W. 271, 1934-01-15). Both rows are the same opinion (different cluster_ids in CourtListener); 4484 has cleaner judges field. Westlaw .doc currently attached to 4484 only. Plan: merge 4485 into 4484, delete 4485, ensure incoming citations and FTS rebuild.
- [ ] **Hassen v. Salem 2946 N.D. cite conflict** (1924-03-20 rehearing). DB cites `50 N.D. 825`; Westlaw's "All Citations" footer on the .doc says `50 N.D. 813`. The Farmers Bank .doc at the same `0813-` page also cites `50 N.D. 813`, so two distinct opinions claim that page in Westlaw. Resolve by checking the bound 50 N.D. volume directly to determine the correct N.D. starting page for the rehearing.
- [ ] **Case-name sweep across vols 1–79.** Every Westlaw ingest ran with `--case-names skip`, deferring the case-name deltas. Vols 49–52 had 42 skipped diffs; vols 53–54 added 39 (15 + 24); vols 55–57 added 56 (19 + 21 + 16); vols 58–62 added 82 more (23 + 10 + 20 + 14 + 15); vols 63–68 added 84 more (12 + 17 + 14 + 16 + 10 + 15); vols 69–74 added 95 more (12 + 14 + 19 + 14 + 20 + 16); vols 75–79 added 44 more (7 + 6 + 13 + 14 + 4); across vols 1–79 the backlog is likely several hundred. Westlaw's case names are typically cleaner than NW/NW2d's ALL CAPS headnote-style names, but not always right (headnote drift, "et al." handling, abbreviation style). Build a review tool that presents each diff with citation, DB value, Westlaw value, and both text snippets so the human can pick or edit. Output as a named changelog batch per volume (`westlaw-nd-volNN-casenames`). Revisit cadence: batch through it after every 10 volumes or so rather than per-volume — easier to stay in context.

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
- [x] Fix the scraper's markdown-write path in `~/code/scraper/scraper/opinion_processor.py:752` (2026-05-04, uncommitted). The `--skip-analysis` branch now resolves `markdown_path` against `COURT_DATA_DIR` and checks `os.path.exists()`; if the file is missing it falls through to regenerate instead of taking the cached early exit. Mirrors the check the non-`skip_analysis` branch already had at lines 766–781.
- [ ] Once the scraper writes markdown again, verify its output vs. our ingest expectations: paragraph markers `[¶N]`, no weird `I N   T H E   S U P R E M E   C O U R T` spacing. The `markdown_cleanup.py` module in the scraper is supposed to handle this — confirm it's being called in the PDF-extract path. (Spot-checked 2026-05-04: 2026ND72.md and freshly-regenerated 2026ND73.md still carry the `I N   T H E   S U P R E M E   C O U R T` letter-spacing artifact, so `cleanup_markdown` is not handling that pattern.)
- [x] Add a post-scrape step (invoked from `weekly_scrape.sh`) that runs `ingest` + `merge_nd_metadata` + `cite_extract` + `quality_scan` against any new opinions. Log the delta. **Done 2026-05-04** (scraper commit `06c966c`). Stages run independently — `set -uo pipefail` (no `-e`) plus a `record()` helper captures each stage's exit code; final exit is the worst seen so launchd surfaces it. Stats helper prints opinion count + `MAX(date_filed)` before/after.
- [x] Chain the ingest job to the scraper's launchd job. **Done 2026-05-04** — same `weekly_scrape.sh` commit. Single launchd job (`com.jerod.ndsc-scraper`) now runs both stages. The "concerns separate" requirement is met by per-stage exit-code capture rather than a separate launchd job; if stage isolation needs strengthening later (e.g., scrape running 30 min and blocking ingest), split into two jobs at that point.
- [ ] Add a heartbeat check: if `MAX(date_filed)` in opinions.db is more than 3 weeks behind today's date, alert (log line on shell startup or email).
- [x] One-off: verify we aren't missing any 2026 opinions released between the last known release (2026 ND 70, 2026-03-26) and today. **Done 2026-05-04** — 20 missing (ND 71–90 across releases of 2026-04-09 and 2026-04-22), now ingested as ids 20392–20411. See CHANGELOG-data.md "Freshness ingest 2026-05-04".
- [ ] **Diagnose the scraper's docket-collision regression (2026 ND 62 / ND 73, Romanyshyn).** ND 73's JSON record was assigned ND 62's `pdf_path` and `markdown_path` because both share docket 20250295. A corpus sweep across 2000–2026 found 19 other docket-collision pairs (cases with multiple opinions on the same docket — substituted opinions, rehearings, or related orders) that the scraper handled correctly with distinct paths; only ND 62/73 was broken. This is a recent regression, likely tied to the WIP `skip_analysis` plumbing in `opinion_processor.py`. The data was hand-fixed for ND 73 today; the code path that produced the bad record is not yet identified. Fix it before more docket collisions appear in 2026.
- [x] Investigate the misplaced markdown file at `~/refs/nd/opin/markdown/79/673.md`. **Done 2026-05-04** — file was a stale jetcite cache from 2026-04-25 (CourtListener citation-lookup copy of *State ex rel. Minot v. Gronna*, 79 N.D. 673). The opinion is already in the DB (id 12830) with two sources (Westlaw .doc + NW2d markdown), so the stray file was redundant. Deleted with companions in data-repo commit `5653de9`. Ingest now reports 0 errors. Reversible from git history if a third independent source for one 1953 opinion ever turns out to be useful for the §3 multi-source diff audit.
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
