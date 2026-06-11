# Tools & Utilities Index

Quick reference to the durable tools in this repo, grouped by purpose. Most are CLI modules run as `python -m ndcourts_mcp.<name>` (use the project venv: `.venv/bin/python`). **CLI** = has a runnable `main()`; **lib** = imported helper, no CLI. Almost every DB-mutating tool is **dry-run by default** and takes `--apply`; corrections are logged to the `changelog` table and reversible via `cleanup revert <batch>`.

> One-off, dated scripts in `triage/*.py` and `scripts/*_<date>.py` are historical single-use adjudications — not reusable tooling. They're the audit trail for specific batches (see `CHANGELOG-data.md`), not general utilities.

## Ingest & scraping
| Tool | Kind | Purpose |
|------|------|---------|
| `ingest` | CLI | Ingest opinions from `~/refs/nd/opin/` into SQLite (the main opinions pipeline). |
| `ingest_nwcite` | CLI | Ingest the court-sourced N.W.-cite mirror with tiered text-promotion. |
| `ingest_westlaw` | CLI | Ingest Westlaw `.doc` downloads; compare/correct vs DB (volume-oriented, bound N.D. Reports). |
| `receive_westlaw` | CLI | **Receive Westlaw Find&Print batches** (zip/`.doc` in `~/refs/nd/opin/westlaw-incoming/`): match by cite+party+date, promote bound text over CL-OCR, create missing, archive `.doc`s. Handles pre-1953 N.D.-cite-primary docs (N.W.-cite archive fallback), out-of-state CREATE guard, dup-vs-companion discrimination. |
| `scrape_archive` | CLI | Scrape opinions from archive.ndcourts.gov (1997–2019). |
| `scrape_nwcite` | CLI | Scrape the court-sourced N.W.2d citation index at archive.ndcourts.gov. |
| `merge_nd_metadata` | CLI | Merge rich metadata from `~/refs/nd/opin/` JSON into the opinions DB. |
| `ingest_constitution` / `ingest_constitution_history` | CLI | Ingest ND Constitution + build its point-in-time amendment history (corpus DB). |
| `ingest_rules` / `ingest_statutes` / `ingest_admin` | CLI | Ingest ND court rules / N.D.C.C. statutes / N.D. Admin Code into versioned corpus DBs. |
| `corpus` | lib | Versioned primary-law corpora plumbing (ATTACH per-corpus DBs, point-in-time). |

## Westlaw cross-check workflow (manual download loop)
| Tool | Kind | Purpose |
|------|------|---------|
| `westlaw_worklist` | CLI | Generate the daily manual-Westlaw download worklist. |
| `quality_report` | CLI | Word doc of lowest-quality opinions for Westlaw lookup. |
| `receive_westlaw` | CLI | Ingest the returned batch (see above). |
| `resolve_westlaw_clearwins` | CLI | Conservative "clear wins" pass over the receive_westlaw AMBIGUOUS queue. |
| `review_casenames` | CLI | Review case-name diffs deferred from Westlaw ingest. |
| `merge_westlaw_text` | CLI | Replace low-quality opinion text with clean Westlaw text. |
| `strip_westlaw_synopsis` / `strip_westlaw_headnotes` | CLI | Remove leaked Westlaw editorial (Synopsis stub, West Headnotes, digest refs). |
| `backfill_westlaw_paths` | CLI | Repair stale `opinion_sources.source_path` for Westlaw `.doc`s. |
| `insert_supplemental_opinions` | CLI | (Legacy) insert separate rows for supplemental publications. **NB:** consolidation policy revised 2026-06-09 — see `merge_opinions` + TODO §15. |

## Dedup, merge & consolidation
| Tool | Kind | Purpose |
|------|------|---------|
| `dedup_scan` | CLI | Scan for duplicate opinions (multiple detection strategies). |
| `merge_opinions` | CLI | **§6 duplicate-row merge engine.** `merge_pair(conn, keep, drop, canonical_name, apply)` re-points all 11 opinion-referencing tables drop→keep + deletes drop + FTS triggers + logs. Auto-discovery driver gates on text-jaccard; `merge_pair` itself does not (usable for distinct-text consolidation — see TODO §15). |
| `sweep_type_y` | CLI | Corpus-wide Type-Y supplemental-publication detector (read-only). |
| `typey` | lib | Shared Type-Y discriminator. |
| `detect_cite_swap` | CLI | Adjacent-cite content-swap detector. |

## Quality, validation & health
| Tool | Kind | Purpose |
|------|------|---------|
| `invariants` | CLI | **Read-only health dashboard** (23 checks + known-baseline tracking). Run after every mutation. |
| `audit_corpus` | CLI | **Cross-corpus systematic-error triage** (TODO-audit.md Tier 1): cite-graph temporal sanity, pinpoint-vs-¶-range, [¶N] continuity, opinion↔statute/rule/const/admin xref resolution, provision-version intervals, changelog↔CHANGELOG-data sync. Writes TSVs to `triage/`. |
| `quality_scan` | CLI | Scan opinion text for quality signals (`ocr_artifacts` = count of `¡¿■£„`, garbage chars, etc.); `--rescan` recomputes all. |
| `validate` | CLI | Validation orchestrator + the `/goal` completion gate. |
| `validation_status` | CLI | Per-opinion validation ledger (era tier, crosscheck state, authority). |
| `audit` / `audit_sources` | CLI | Audit for missing opinions / data anomalies / source completeness. |
| `volume_date_check` | CLI | Flag opinions whose `date_filed` is inconsistent with the reporter volume's date range. |
| `multisource_diff` | CLI/lib | Multi-source diff audit (also exports `jaccard`, `shingles`, `normalize_words`). |
| `triage/shingle_selfsim_*` | script | Body-duplication detector (audit check #6): word-8-shingle self-similarity; catches markerless stored-twice bodies. Re-run after merge concatenations. |
| `triage/digit_compare_*` + `digit_flip_candidates_*` + `render_flip_crops_*` | scripts | The print-verified digit-flip pipeline: per-¶ DB-vs-PDF digit compare → context-matched candidates → **render the printed glyphs** (never apply from the PDF text layer alone — 3/693 candidates were text-layer ToUnicode errors). |

## Citation graph
| Tool | Kind | Purpose |
|------|------|---------|
| `cite_extract` | CLI | Extract citations from opinion text → build forward (`text_citations`) + reverse (`cited_by`) graph. Applies `print_anomalies` overrides on every cited_by rebuild (typo'd-in-print cites resolve to the intended case — SCHEMA.md Contract 3). Needs jetcite ≥2.1.0 editable-installed (see `reference_jetcite_coupling` memory). |
| `detect_cite_swap` | CLI | Detect adjacent-cite content swaps. |

## Corrections, schema & one-offs
| Tool | Kind | Purpose |
|------|------|---------|
| `cleanup` | CLI | **Apply/manage data corrections with full audit trail; `cleanup revert <batch>`.** |
| `align_primary_source` | CLI | Align `source_path` / `opinion_sources.is_primary` with `source_reporter`. |
| `backfill_sources` | CLI | Link on-disk source files that were never recorded in `opinion_sources`. |
| `auto_author` | CLI | Auto-detect authors for opinions with junk/garbled author values. |
| `review` | CLI | Interactive author review tool. |
| `recompute_is_primary` | CLI | One-off: recompute `citations.is_primary` (Contract 2 / SCHEMA.md). |
| `migrate_reporter_taxonomy` / `migrate_changelog_cl` | CLI | One-off schema migrations (reporter taxonomy; CL-diff-ready changelog). |
| `fix_*` (feldmann_2017, kitchen_kleinsmith_2013, westlaw_pairings[_round2], archive_pairings, type_y_archive_pairings, cl_metadata_contamination) | CLI | Targeted one-off contamination/pairing fixes (kept for revert/audit). |

## Server & UI
| Tool | Kind | Purpose |
|------|------|---------|
| `server` | CLI | **The MCP server** (FastMCP) — opinions + primary-law tools. |
| `webapp` | CLI | Opinion-browser FastAPI backend (REST + static HTML). |

## Reference data & pure helpers (lib)
| Tool | Purpose |
|------|---------|
| `db` | Schema + connection (`get_connection`, `DEFAULT_DB_PATH`, `log_change`, `log_provenance`). |
| `justices` | ND Supreme Court justice reference data (service dates; surrogate caveats apply). |
| `nd_const_phrases` | Quote→provision table for the ND Constitution. |
| `memo` / `proofread` / `research` | Pure helpers backing the jetmemo / jetredline / human-research MCP tools. |

## Scripts (`scripts/`)
| Script | Purpose |
|--------|---------|
| `make_release.sh` | Build the public release (zip the DB asset). |
| `backfill_gov_urls.py` | Backfill ndcourts.gov `opinion_url` by neutral cite (scraper venv; padding/nondeterminism gotchas). |
| `merge_const_history.py` | Merge const-history into the served DB (deploy pipeline). |
| `wf_amend_extract*.js` | Workflow scripts for constitutional-amendment extraction. |

## Common workflows
- **OCR cross-check (pre-1953 / no-PDF):** `quality_scan --rescan` → build cite list of `ocr_artifacts>0` lacking a Westlaw source → pull from Westlaw → drop zips in `~/refs/nd/opin/westlaw-incoming/<date>/` → `receive_westlaw --incoming <dir>` (dry-run) → review TSV → `--apply` → `quality_scan --rescan` → `invariants`.
- **Modern OCR artifacts (1997+, `source='ND'`):** these are PDF→markdown conversion defects, NOT OCR — fix from the local court PDF (`~/refs/nd/opin/pdfs/`), not Westlaw. Worklist: `triage/ocr-pdf-reextract-worklist.tsv`.
- **N.D. Reports consolidation:** audit shared-N.D.-cite groups → verify against bound `N.D./<vol>/_bound-volume.pdf` (offset drifts; calibrate with `mutool draw -r 130` + read printed page no.) → `merge_pair` + concatenate text + parallel cites + drop freed synthetic + drop self-cites → `invariants`. Policy + audit: TODO §15, `triage/nd-consolidation-audit-2026-06-09.md`.
- **After any data change:** log to `changelog` (via `log_change`) + `CHANGELOG-data.md`; run `invariants` (target 23 ok / 2 known / 0 regressed).
