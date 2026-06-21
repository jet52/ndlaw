# Reversion Recovery — silent loss of validated corrections

**Opened 2026-06-21.** The DB is the single source of truth, but ingest /
`merge_nd_metadata` / the weekly pipeline re-read the `~/refs` source and
silently overwrote corrected fields without logging — undoing prior work on
every run. Root cause: the `1997_opinions.json` source is itself contaminated
(misfiled content, e.g. `1997ND16.md` holds 1997 ND 15) and the writers blindly
applied it. Scalar fields are now detected (`reconcile_corrections`), guarded
(`merge_nd_metadata` write-guard), and partly restored. **`text_content` (the
opinion bodies) is NOT yet covered** — this file is the plan to fix that and the
running list of everything still open.

## DONE (2026-06-21)
- `reconcile_corrections.py` — changelog-vs-DB reconciliation (INTACT/REVERTED/DIVERGED) for scalar fields.
- invariant `corrections_not_reverted` (baseline 109) — catches new scalar reversions.
- `merge_nd_metadata` write-guard — keeps/restores logged corrections instead of clobbering (dry-run: 517 guarded / 495 restored).
- Restored **309 reverted content corrections** (`restore-reverted-corrections-2026-06-21`): docket 189, case_name 47, author 20, date_filed 20, judges 16, opinion_url 14, per_curiam 3.
- Decontaminated 11 mislabeled 1997 opinions (`casename-docket-decontam-1997-2026-06-20`).

## OPEN — scalar / metadata
- [ ] **109 `source_reporter` reversions** — provenance, coupled to `opinion_sources` + `source_reporter_matches_primary`. Restore via `align_primary_source`, not blind UPDATE. (in `triage/changelog-reconcile.csv`)
- [ ] **337 DIVERGED scalar fields** — current value ≠ both original and intended; review for intentional-vs-lost (case_name 183, source_path 98, author 31, source_reporter 19, judges 6). (`triage/changelog-reconcile.csv`)
- [ ] **Broader case_name contamination beyond the 11** — no prior correction to restore, so these need NEW corrections: the **18248–18280 cluster** (~13, e.g. 18248 body=Wittmayer not "Burr v. Kulas"; 18278↔18279 Rieger↔Hintz swap), plus 12391→Heitkamp, 12438 done, 12511→State v. Sisson, 19242="Case 2018ND1" placeholder. Build body-caption-arbitrated worklist (court spreadsheet + CL + body caption). (`triage/casename-audit.csv` raw)
- [ ] **188 cite-shaped docket placeholders** remaining (148×1997) — the precise fingerprint of the reverted/contaminated cohort; reconcile against body "No." line + court file numbers.
- [ ] **Source fix** — correct `1997_opinions.json` case_name/docket + rename misfiled `markdown/1997/*.md` so re-ingest is clean. Lower urgency now the guard protects the DB.

## OPEN — opinion BODY text (`text_content`) re-validation  ← the main initiative
We never reconciled body text. The reconciliation method doesn't apply (changelog
stores *descriptions*, not literal text). Probe 2026-06-21: OCR artifacts 0 (held),
but **26 opinions have garbled `[IF`/`[I¶` markers** the marker batches had fixed →
proof some body work reverted. Plan below.

### Phase 0 — Stop the bleeding (protect `text_content`)  — CORE DONE 2026-06-21
- [x] Map every write path to `text_content`. **Silent auto-writer (the weekly-pipeline mechanism):** `ingest._ingest_nd_opinions` line ~346 (conditional marker-gated update, NO changelog log). **Logged/deliberate writers (tracked, recoverable, not silent):** `ingest_nwcite` (309/466, court-archive promotion — logs), `merge_westlaw_text`/`receive_westlaw` (westlaw promotion — logs), `strip_*`/`fix_*`/`webapp` (these ARE corrections).
- [x] **Guard the silent writer:** `reconcile_corrections.corrected_text_opinion_ids()` + `ingest._body_is_protected()` — the ND ingest now skips overwriting any body with a logged `text_content.*` correction and reports `body_protected`. **15,166 corrected bodies protected.** Tested; invariants 23/2/0.
- [ ] Decide whether to also guard the deliberate promoters (`ingest_nwcite`, westlaw merge): they LOG and are run manually, so they are not the silent culprit, but they CAN downgrade a corrected body — add a `--force`-gated guard or a pre-run protected-body warning.
- [ ] Optional: store a post-correction `content_hash` per opinion as durable provenance (enables value-level body reconciliation later).

### Phase 1 — Detect body reversions: re-run detectors vs documented baselines
Most body validation was done by **re-runnable detectors** with a documented
"done" state in CHANGELOG-data.md / memory. Re-run each; any count above its
baseline = reverted or new work.

| validation | detector to re-run | documented baseline |
|---|---|---|
| OCR artifacts (`¡¿■£„`) | `quality_scan --rescan` | 0 corpus-wide ✓ (re-probed clean) |
| garbled/OCR paragraph markers | grep `[IF`/`[I¶`/dotted `[¶ N.]` + `para_continuity` | 0 garbled (⚠ **26 found 2026-06-21**) |
| digit-flips (3↔8/5↔6 etc.) | `triage/digit_compare_*` (DB ¶ digits vs court PDF) | 0 after sweep (1,021 fixed) |
| body stored twice / dedup | `triage/shingle_selfsim_*` | pre-1997 clean, 2 known |
| substantive missing ¶ | `text-missing-measured` / substantive-missing detector | 219 spliced, 7 held |
| signature-block splices | sig-splice detector | 473 done |
| two-column mis-extraction | mean-body-line-length detector | 2 known |
| missing/garbled markers (modern) | invariant `nd_modern_paragraph_markers` | 18 known |
| stray cite spacing | `refs_diff citespaces` | 2 intentional ranges |
| pinpoint vs ¶-range / [¶N] continuity | `audit_corpus` | documented |
| DB body vs ~/refs source | `refs_diff compare` + `selfcheck` | major bucket triaged |

- [ ] Run the full suite; build a diff table (current vs baseline) → the reverted-body worklist.

### Phase 2 — Token-level body reconciliation (surgical text fixes)
- [ ] Extend reconciliation to structured `text_content.*` batches where old/new are tokens: `digit_flip`, `citefix`, `cite_token`, `marker`, `pincite`, `header_cite`, `cite_spacing`, `splice_para`. Parse the changed token, ¶-anchor it (don't bare-substring — the 12-sample had 5 ambiguous), and classify INTACT/REVERTED. Catches surgical reverts the aggregate detectors miss.

### Phase 3 — Re-apply + re-validate
- [ ] Re-apply reverted surgical fixes from changelog tokens (¶-anchored).
- [ ] Re-run structural fixers where regressed (re-dedup, re-splice) — **verify against the court PDFs** (gold standard; never from the PDF text layer alone — see digit-flip doctrine).
- [ ] Re-extract the citation graph + apply `print_anomalies`; run `invariants`.

### Phase 4 — Make body integrity durable
- [ ] Promote the cheap detectors to invariants (garbled-marker count, ocr_artifact count, shingle-self-sim count) so any future body reversion fails the dashboard.
- [ ] Per-opinion post-correction `content_hash` provenance for fast future reconciliation.

## Immediate leads (found while probing)
- 26 opinions: `text_content LIKE '%[IF %' OR '%[I¶%'` — start Phase 1 here.
- 5/12 digit-flip sample "ambiguous" — motivates the ¶-anchored Phase-2 detector.
