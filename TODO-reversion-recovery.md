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

## opinion BODY text (`text_content`) — QA CONFIRMATION (downgraded 2026-06-21)
**Re-framed after checking the ingest path:** body corrections were most likely
NOT silently reverted. Why:
- The weekly pipeline runs `ingest --incremental`, which is **year-gated**
  (`since_year` = latest opinion's year; skips all older files) — so it only
  adds the current year's new opinions and **never touches an old body**.
- `merge_nd_metadata` (the confirmed metadata reverter) **does not write
  `text_content`** at all.
- The "26 garbled `[IF`/`[I¶` markers" are **residue, not reversions** — 0 of the
  26 ever had a logged marker fix (1976–2024, scattered misses).
- The only path that could overwrite an old body is a **full (non-incremental)
  ingest**, and only the narrow `ingest.py` line-346 case (source has `[¶`,
  current lacks it) — which the **Phase 0 guard now blocks** regardless.

So this is QA verification (confirm bodies held + clean genuine residue), not
urgent recovery. Run the detector sweep below to confirm; expect mostly clean +
a small residue list (the 26 markers, the 5 ambiguous digit-flips).

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
| garbled/OCR paragraph markers | grep `[IF`/`[I¶`/dotted `[¶ N.]` + `para_continuity` | 26 found 2026-06-21 — RESIDUE (0 ever marker-fixed), not reversions; clean up as QA |
| digit-flips (3↔8/5↔6 etc.) | `triage/digit_compare_*` (DB ¶ digits vs court PDF) | 0 after sweep (1,021 fixed) |
| body stored twice / dedup | `triage/shingle_selfsim_*` | pre-1997 clean, 2 known |
| substantive missing ¶ | `text-missing-measured` / substantive-missing detector | 219 spliced, 7 held |
| signature-block splices | sig-splice detector | 473 done |
| two-column mis-extraction | mean-body-line-length detector | 2 known |
| missing/garbled markers (modern) | invariant `nd_modern_paragraph_markers` | 18 known |
| stray cite spacing | `refs_diff citespaces` | 2 intentional ranges |
| pinpoint vs ¶-range / [¶N] continuity | `audit_corpus` | documented |
| DB body vs ~/refs source | `refs_diff compare` + `selfcheck` | major bucket triaged |

- [x] Run the full suite; build a diff table (current vs baseline) → the reverted-body worklist.

### Phase 1 RESULT — signature-block truncation (2026-06-21) — 216 fixes, COHORT 273 → 58
The body sweep surfaced a NEW defect class (not a reversion): the modern DB body
was ingested verbatim from an **older clean-format markdown** whose analyzer
**dropped the final `[¶N]` signature paragraph(s)**, collapsing the justice panel
to a single trailing name (or dropping it entirely). Current `~/refs` markdown is
complete (matches the court PDFs); re-ingest would regress formatting, so the fix
is a surgical splice/insert, not re-extraction.

**Detection (reproducible):** `refs_diff sigscan` (max-`[¶N]` gap; replaces the
73%-false-positive word-ratio `refs_diff truncscan`) → `scripts/classify_sig_drops_2026-06-21.py`
(OCR-tolerant, date-agnostic name matching) → `triage/sig-drops-classified.csv`.
Initial: 273 flagged = MARKER_GARBLED 31 / TRUE_TRUNCATION 200 / CONTENT_LOSS 22 / REVIEW 20.

**Applied batches (all PDF-corroborated, changelog-logged & revertible, invariants 23/3/0):**
| batch | n | what |
|---|---|---|
| `restore-sig-truncation-2026-06-21` | 102 | single-opinion splice (orphan→full panel) |
| `fix-marker-garbled-2026-06-21` | 24 | repair garbled `[¶N]` marker (text already complete) |
| `restore-sig-truncation-phase2-2026-06-21` | 6 | append single-justice separate-writing signature |
| `restore-sig-truncation-phase4-2026-06-21` | 77 | **positional** majority-panel insert before trailing notation |
| `restore-sig-truncation-phase5-2026-06-21` | 5 | orphan-name replace (footnote/roman-tolerant) |
| `restore-sig-truncation-phase6-2026-06-21` | 2 | participation-note insert/append |

Key methods/guards (see `scripts/fix_sig_truncation_phase*.py`): **divergence guard**
(every justice in the DB's trailing element must be in the source panel — rejected
16311); **short-surname exact-match** (edit-distance matched "Sand" inside "VANDeWalle");
roman numerals in a signature run are **SECTION HEADINGS** (part III/VI), PDF-confirmed,
stripped (they already live in the body); `justices.py` Jensen start 2019→2017 fixed.

**OPEN — manual worklist (`triage/sig-drops-classified.csv`); best done by hand w/ the court PDF:**
- [ ] **TRUE_TRUNCATION 8 (one-offs):** 3 datelines (12600/12657/12722 — "Dated at Bismarck" judgeship
  orders; dateline duplicated in source + spelled-out "Chief Justice"/"Justice" roles); 2 surrogate-in-panel
  (13288/16366 — Grosz/Graff in panel; need a `, S.J./D.J.` line-break in the panel formatter); 2 complex
  intertwined (12726/13127 — note+panel fused, OCR'd); 1 GENUINE divergence (16311 — DB "Sandstrom concurs"
  vs source "Crothers concurs"; needs a human read on which is right, then targeted fix).
- [ ] **MARKER_GARBLED 8:** surrogate-note valid-marker / single-name dissent / split-panel + 15214's note now
  lacks its `[¶8]` marker (cosmetic — panel restored). Add the missing markers.
- [ ] **CONTENT_LOSS 22:** real substantive paragraph loss; overlaps the 1997 contamination (12392/12398/12455).
  Verify each vs PDF / bound volume — do NOT auto-fix.
- [ ] **REVIEW 20:** ambiguous multi-opinion 2-3/5-name panels.
- [ ] justice-name OCR garbles WITHIN restored panels (NEU-MANN, MAKING, YANDE WALLE, McEYERS) — separate cleanup batch.
- [ ] **Phase 4 (durability):** promote the `sigscan` max-`[¶N]`-gap to an invariant once the cohort is worked down.
- NOTE: phase3 was built then REMOVED (unsafe — it append-duplicated participation notes); do not resurrect.

### Phase 2 — Token-level body reconciliation (surgical text fixes)
- [ ] Extend reconciliation to structured `text_content.*` batches where old/new are tokens: `digit_flip`, `citefix`, `cite_token`, `marker`, `pincite`, `header_cite`, `cite_spacing`, `splice_para`. Parse the changed token, ¶-anchor it (don't bare-substring — the 12-sample had 5 ambiguous), and classify INTACT/REVERTED. Catches surgical reverts the aggregate detectors miss.

### Phase 3 — Re-apply + re-validate
- [ ] Re-apply reverted surgical fixes from changelog tokens (¶-anchored).
- [ ] Re-run structural fixers where regressed (re-dedup, re-splice) — **verify against the court PDFs** (gold standard; never from the PDF text layer alone — see digit-flip doctrine).
- [ ] Re-extract the citation graph + apply `print_anomalies`; run `invariants`.

### Phase 4 — Make body integrity durable
- [ ] Promote the cheap detectors to invariants (garbled-marker count, ocr_artifact count, shingle-self-sim count) so any future body reversion fails the dashboard.
- [ ] Per-opinion post-correction `content_hash` provenance for fast future reconciliation.

## Immediate leads / residue (found while probing)
- 26 opinions: `text_content LIKE '%[IF %' OR '%[I¶%'` — RESIDUE (never marker-fixed), QA cleanup.
- 5/12 digit-flip sample "ambiguous" — bare substring isn't enough; motivates the ¶-anchored Phase-2 detector (for QA confirmation, not recovery).
