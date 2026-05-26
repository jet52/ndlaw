# Data Corrections Log

Changes applied to the opinions database after import from CourtListener and ndcourts.gov sources. All corrections are recorded in the `changelog` SQLite table and can be reverted with `python -m ndcourts_mcp.cleanup revert <batch>`.

## Per-pair review resolutions 2026-05-26 — the 5 same-neutral-cite pairs + S.H.B. + Smithberg/G.L.D.

The residual §6 DEFER_MODERN "two N.W.2d pages under one neutral cite" pairs were adjudicated individually (user-ruled per-pair), several against just-pulled Westlaw `.doc`s. Final corpus **19,909**; invariants 22/2/0; 0 orphans; FTS synced throughout.

- **`fix-farstveet-2000nd189-2026-05-26`** — *Farstveet v. Rudolph* 2000 ND 189: kept the rehearing-inclusive text (13407, 630 N.W.2d 24), merged the original-only capture (13246, 618 N.W.2d 181) into it; neutral primary; **both** N.W.2d parallels retained; date corrected 2001-07-10 → **2000-10-26** (the original filing; rehearing was 2001). Snapshot `…-pre-farstveet-…`.
- **`fix-gietzen-2010nd82-2026-05-26`** — *State v. Gietzen* 2010 ND 82: **Westlaw confirmed** `782 N.W.2d 66` is the *withdrawn* advance sheet ("withdrawn because it was modified") and `786 N.W.2d 1` is the operative modified bound opinion (~162 words added). Kept the final (15476, 786 N.W.2d 1); merged the withdrawn advance (15426); **dropped** the withdrawn `782 N.W.2d 66` cite + its source (user-ruled) and a malformed `2010 N.D. 82`. Snapshot `…-pre-gietzen-…`.
- **`fix-redist-watford-2026-05-26`** — two original-order+amended-order pairs (Westlaw-confirmed):
  - *In re Judicial Redistricting* 2013 ND 135: kept the **amended** order (16137, 839 N.W.2d 808 — renamed "Northwest Central" → "North Central" district + conformed Admin. Rules 6/6.1); merged the superseded original (16084, 833 N.W.2d 543); neutral primary, both N.W.2d cites kept.
  - *Petition to Change Resident Chambers … Judgeship No. 8 (Watford City→Minot)* 2002 ND 54: the two rows are **complementary** (¶1–15 original order 643 N.W.2d 1 + ¶16 "ORDER AMENDED" 650 N.W.2d 812), so **stitched** them into one row (13562) — full order-as-amended — rather than dropping half; both N.W.2d cites kept. (FTS verified it indexes the stitched amendment text.) Snapshot `…-pre-redist-watford-…`.
- **`fix-smithberg-gld-2026-05-26`** (no row deletion, changelog-revertible) — *Smithberg v. Jacobson* 2020 ND 46 and *Interest of G.L.D.* 2020 ND 45 are distinct; `939 N.W.2d 405` is G.L.D.'s (page-json dk 20190179). Stripped the contaminant + its NW2d source from Smithberg (17603); fixed G.L.D.'s malformed docket `2020ND45` → `20190179`.
- **`fix-shb-2010nd149-tangle-2026-05-26`** — *S.H.B. v. T.A.H.* 2010 ND 149: an A.C.-style 3-row mislabel. 15479 = the real 2010 ND 149 (S.B./T.H. termination, AFFIRMED, 786 N.W.2d 706) — fixed its malformed `2010 N.D. 149` cite and moved its ND-markdown + archive sources off the spurious row (then promoted ND primary). 15480 = a spurious row holding *2010 ND 147*'s text (A.D.S./R.S. deprivation) under 2010 ND 149's cites — stripped its wrong cites/sources and merged it into 15489, the correct *Interest of R.S.* 2010 ND 147 (also dropped a malformed `2010 N.D. 147`). Net: 2010 ND 149 → 15479 only, 2010 ND 147 → 15489 only. Snapshot `…-pre-shb-…`.

## Batch `fix-ac-2022-tangle-2026-05-26` — untangled Interest of A.C. 2022 ND 123 / 2022 ND 169

The deferred A.C. pair turned out to be a content-swap + three-way mislabel across files and DB rows (same failure mode as the Goetz 2023 ND 53/120 swap). User supplied the canonical ndcourts.gov PDF (`~/Downloads/2022ND123.pdf`) + the Westlaw `.doc`, which fixed the ground truth: **2022 ND 123** = *Interest of A.C.*, No. 20220081, **REMANDED, filed 2022-06-08, 975 N.W.2d 567** (Jensen, C.J.); **2022 ND 169** = the same case **AFFIRMED, filed 2022-09-15, 979 N.W.2d 929**.

- **Refs files de-swapped on disk** (`~/refs`, not version-controlled): `markdown/2022/2022ND123.md` ↔ `2022ND169.md` and `pdfs/2022/2022ND123.pdf` ↔ `2022ND169.pdf` each held the *other* opinion. Installed the canonical ndcourts.gov PDF at `pdfs/2022/2022ND123.pdf`; moved the 169-content PDF to `2022ND169.pdf`; swapped the markdown pair. Verified each filename's page-1 cite+disposition now matches.
- **DB (`fix-ac-2022-tangle-2026-05-26`, snapshot `opinions.db.bak-pre-ac-tangle-2026-05-26`, corpus 19,915 → 19,914):** **18040** = real 2022 ND 123 — fixed only its `date_filed` (2022-09-15 → 2022-06-08; cite/975 N.W.2d 567/REMANDED already correct). **18052** = real 2022 ND 169 — relabeled cite `2022 ND 123` → `2022 ND 169` and repointed its ND source to `markdown/2022/2022ND169.md` (979 N.W.2d 929/AFFIRMED/9-15 already correct). **19676** = a spurious duplicate (carried the 2022 ND 123 *text* under a mislabeled `2022 ND 169` cite) — stripped the bad cite, detached its wrong-file source, merged → 18040.
- **Verification:** each cite now on exactly one row (`2022 ND 123`→18040, `2022 ND 169`→18052); `align_primary_source` 0/0/0; invariants 22/2/0; 0 orphans; FTS synced. Script `triage/fix_ac_2022_tangle_2026-05-26.py`. (Westlaw `Interest of AC.doc` confirmed 2022 ND 123 = 975 N.W.2d 567; 18040 already carried that NW2d source.)
- **Pattern flag:** this is the *second* adjacent-neutral-cite content-swap in the ndcourts.gov refs (after Goetz 2023 ND 53/120) — possible systemic scraper mis-save worth a sweep (noted in TODO §7).

## Batch `section6-review-clear-2026-05-26` — §6 DEFER_MODERN, the unambiguous residual-review resolutions (12 of 19)

Worked the 19 residual review pairs (LOWJAC_REVIEW + DOCKET_CONFLICT_MIDJAC) via `triage/classify_review_2026-05-26.py` + text reads. 12 resolved cleanly here; 7 genuinely-ambiguous held for a policy call (below). Corpus 19,926 → **19,915**. Invariants 22/2/0; 0 orphans; FTS synced. Snapshot `opinions.db.bak-pre-review-clear-2026-05-26`; script `triage/fix_review_clear_2026-05-26.py`.

- **10 MERGE_CLEAN** — dup + CL summary stub, same primary neutral cite + one shared N.W.2d cite. The 5 ex-DOCKET_CONFLICT (Hoffman 1999 ND 122, W.E. 2000 ND 208, Garaas 2002 ND 181, D.P.O. 2003 ND 127, Edin 2005 ND 109) were flagged only because one row's docket is a consolidated list (`20020103, 20020113`) vs a single docket — same neutral + N.W.2d cite + j 0.88–0.94 confirm one opinion. The other 5 (Chambering 2009 ND 133, Pizza Corner 2010 ND 243, Benz Farm 2011 ND 184, Come Big or Stay Home 2012 ND 91, MayPort 2012 ND 257) are dup+stub (j≈0). Merged stub→full, caption per the fuller-style policy.
- **Everett v. State 2010 ND 4** — the two rows are one opinion (same docket 20090244); the drop carried a **contaminated** `777 N.W.2d 62` (that page is *Cass County State's Attorney v. Hanenberg*, dk 20090135, per the page-json). Stripped the contaminant, then merged keeping the correct `789 N.W.2d 282`. Survivor 15508 = `2010 ND 4` + `789 N.W.2d 282`.
- **O'Hara v. Schneider 2017 ND 159** — distinct from *Jasmann v. State* 2017 ND 150; `897 N.W.2d 326` is Jasmann's (page-json dk 20160396). Stripped the contaminant from O'Hara (no merge — distinct cases). O'Hara 16963 = `2017 ND 159`.

## Batches `section6-contam-safestrip-2026-05-26` + `section6-contam-stub-merge-2026-05-26` — §6 DEFER_MODERN, the DISTINCT_CONTAM tier (75 pairs)

The 75 DISTINCT_CONTAM pairs (two genuinely different 1997+ cases sharing one N.W.2d cite) split into two distinct problems, resolved separately. **Authoritative owner signal throughout: `~/refs/nd/opin/NW2d/<vol>/<page>.json`** is keyed by reporter page, so it names (by docket) the case that actually occupies that page — independently confirmed by reading the page `.md` text (8-sample check: page text always named the owner + matching neutral cite). Adjudication `triage/analyze_contam_2026-05-26.py` → `triage/contam-adjudication-2026-05-26.tsv`.

**`section6-contam-safestrip-2026-05-26` — 69 cite-contamination strips** (snapshot `opinions.db.bak-pre-contam-2026-05-26`). The non-owner opinion keeps its own primary neutral cite, so the contaminated N.W.2d cite (always is_primary=0) was simply deleted, and the contaminated NW2d *source* row (pointing at the owner's reporter page) detached — **69 citations stripped + 68 NW2d sources detached**. E.g. *State v. Urrabazo* (2021 ND 179) carried *State v. Woodruff*'s `965 N.W.2d 425`; stripped. 0 opinions left citeless; all 69 owners retain their cite; invariants 22/2/0; 0 orphans. Script `triage/fix_contam_safestrip_2026-05-26.py`.

**`section6-contam-stub-merge-2026-05-26` — 12 duplicate summary-stubs merged** (snapshot `opinions.db.bak-pre-contam-stub-2026-05-26`; corpus 19,938 → **19,926**). The remaining 6 "pairs" were a **premise shift**: not contaminations but 12 CourtListener "Affirmance by summary opinion" STUB rows (NW2d-only, ~400 chars, no neutral cite) that each duplicate a full ND opinion already in the DB — they never deduped because the stub had no neutral cite to match on (recovered each from the markdown tree by docket grep; identity = same docket + parties + date + neutral cite, conclusive despite ~0 text jaccard, which is just stub-vs-full length). Resolution: the **6 NON-OWNER stubs** had their contaminated N.W.2d cite stripped + `_2.md` source detached *before* merge so nothing wrong propagated; the **6 OWNER stubs** carried the correct N.W.2d parallel that the full opinion was **missing**, so the merge transferred it — *completing 6 parallel citations* (e.g. *Clifford v. Redmann* 18589 now `2006 ND 93` + `719 N.W.2d 384`). Keep = the full ND opinion; `recompute_primary` kept the neutral cite primary (6 owner survivors verified neutral-primary). Two truncated/mangled survivor captions cleaned from the markdown body caption (19277 `…Commissioners (cons` → full name; 19279 `.J.K. v. M.J.K.` → `Guardianship and Conservatorship of M.J.K.`). `align_primary_source` 6 flips; invariants 22/2/0; 12/12 stubs deleted; 0 orphans; FTS synced. NOT changelog-revertible (row deletes). Script `triage/merge_contam_stubs_2026-05-26.py`.

**Net:** the DISTINCT_CONTAM tier is fully cleared (0 remaining in the live scan). The §6 DEFER_MODERN queue now holds only non-dup review buckets: 19 LOWJAC_REVIEW, 10 DOCKET_CONFLICT_MIDJAC, and the 1 deferred-caption pair (14224/14223).

## Batch `section6-defermodern-likely-2026-05-26` — §6 DEFER_MODERN, the LIKELY_DUP tier (40 1997+ double-ingest merges)

Second pass on §6 DEFER_MODERN: the LIKELY_DUP tier (shingle-jaccard 0.55–0.85, no docket conflict). All 40 are the same opinion double-ingested under two caption styles; the depressed shingle-jaccard is word-order/insertion drift (one source carries the syllabus/headnotes/annotations or OCR noise), not distinct content. **Verified before merging** (`triage/verify_likely_dup_2026-05-26.py`): every pair has **word-set containment 0.96–0.99** (the shorter opinion's words are a near-subset of the longer) with near-equal word counts, and **docket-confirmed** (39 exact normalized-docket matches + 1997 ND 101 against a garbage `1997ND101` placeholder docket, same date + same cites). PDF reads were held in reserve but unneeded — the docket+cite+date+containment evidence was conclusive.

- **40 LIKELY_DUP pairs merged** (`merge_pair`, keep = more-cited row). Corpus **19,978 → 19,938**. The merge driver re-enforces the safety floor at apply time (word-containment ≥ 0.85). Same caption-survival policy as the CLEAN_DUP pass — survivor takes the fuller style: disciplinary cases land on `Disciplinary Board v. X` over `In re Disciplinary Action Against X`; juvenile on `Interest of X.Y.` over `In re XY`; `Buchholtz v. Director, N.D. Dept. of Transportation` over the ALL-CAPS variant. Annotations stripped (added `see`/`memo` to the stripper for `(see Docket Memo)` / `(see Memo)` clerk notes). Confidential/juvenile included.
- **Verification:** `align_primary_source --apply` (0 rewrites, 1 flip), invariants **22 ok / 2 known / 0 regressed** (`neutral_cite_uniqueness` 75 → **36**), **0 orphan refs / 0 self-cites**, FTS in sync (19,938). **NOT changelog-revertible** — snapshot `opinions.db.bak-pre-defermodern-likely-2026-05-26`. Script `triage/merge_defer_modern_likely_2026-05-26.py` (imports the caption logic from the CLEAN_DUP driver verbatim); merge log `triage/section6-defermodern-likely-2026-05-26.tsv`.
- **§6 DEFER_MODERN dup tiers now fully drained** (211 of 212 mergeable pairs merged across both passes; 1 deferred = 14224/14223 *2005 ND 75* Fire & Tornado Fund, needs a hand-picked caption). Remaining DEFER_MODERN queue is **non-merge work**: 75 DISTINCT_CONTAM (cite-contamination hygiene), 19 LOWJAC_REVIEW, 10 DOCKET_CONFLICT_MIDJAC — worklist `triage/defer-modern-adjudication-2026-05-26.tsv`.

## Batch `section6-defermodern-clean-2026-05-26` — §6 DEFER_MODERN, the CLEAN_DUP tier (170 1997+ double-ingest merges)

First pass at the long-deferred §6 DEFER_MODERN queue (post-1997 pairs that share a native `YYYY ND n` neutral cite). The live scan (`merge_opinions._corpus_pairs`) yielded 521 DEFER_MODERN rows; deduped across the neutral+N.W.2d rows that name each pair twice and adjudicated each with text jaccard + docket comparison (`triage/analyze_defer_modern_2026-05-26.py`), they resolve to: **171 CLEAN_DUP** (j≥0.85 + no docket conflict), 40 LIKELY_DUP (j 0.55–0.85, docket-confirmed), **75 DISTINCT_CONTAM** (genuinely different cases sharing one contaminated N.W.2d cite — *not* dups), 14 LOWJAC_REVIEW, 5 DOCKET_CONFLICT_MIDJAC. This batch applies the CLEAN_DUP tier only.

- **170 of 171 CLEAN_DUP pairs merged** (`merge_pair` drop → keep; keep = the more-cited row per the scan heuristic). Every pair is one opinion ingested twice under two caption styles (the ndcourts.gov "smushed" form `In re GRH` / `In Interest of EH` vs the CourtListener full form `Matter of G.R.H.` / `Interest of M.S.` / `Disciplinary Board v. X`); all 170 are docket-confirmed (166 exact normalized-docket match, 4 against a garbage `YYYYNDn` placeholder docket on the drop side — still same date + same neutral cite + j≥0.88). Corpus **20,148 → 19,978**.
- **Caption-survival policy (user-ratified 2026-05-26): survivor takes the fuller/period-initial style**, with trailing consolidation / cross-reference / `(CONFIDENTIAL)` / docket annotations stripped, the ratified probate transform applied (`In Re Estate of X` → `Estate of X`), and terminal initial periods preserved (`Interest of J.C.S.`, not `J.C.S`). Confidential/juvenile pairs were included (merging a duplicate row never de-anonymizes; per the published-opinions-public policy) — 90 conf / 114 juv across the mergeable set.
- **1 pair deferred** (`14224`/`14223`, *2005 ND 75* = the State Fire & Tornado Fund multi-party `ex rel.` case): a true dup, but *both* DB captions are mangled (`FIRE AND TORNADO FUND v. University` / `State of ND v. NDSU, et al.`), so the merge is held for a hand-picked caption rather than imposing a bad one.
- **Verification:** `align_primary_source --apply` (0 source_path rewrites, 1 primary-flag flip), invariants **22 ok / 2 known / 0 regressed** (`neutral_cite_uniqueness` 258 → **75**, the expected drop from collapsing native-cite dups — well under the 258 baseline), **0 orphan refs / 0 self-cites**. **NOT changelog-revertible** (170 `DELETE FROM opinions`) — recovery is snapshot `opinions.db.bak-pre-defermodern-2026-05-26`. Script `triage/merge_defer_modern_clean_2026-05-26.py`; adjudication worklist `triage/defer-modern-adjudication-2026-05-26.tsv`; merge log `triage/section6-defermodern-clean-2026-05-26.tsv`.
- **Remaining §6 DEFER_MODERN (second pass):** 40 LIKELY_DUP (probable merges — verify the text drift), the 1 deferred-caption pair; plus **75 DISTINCT_CONTAM**, which are a *separate cite-contamination bug* (a wrong N.W.2d parallel hung on a distinct opinion via CL cross-contamination) and need cite-hygiene fixes, not merges; plus 19 review-bucket pairs.

## Batch `recover-2023nd120-2026-05-26` — recovered the missing Goetz v. Goetz, 2023 ND 120

Follow-up to the Goetz merge: a real, *distinct* 2023 ND 120 Goetz v. Goetz (2023-07-07) was missing from the corpus because the `~/refs` source files for 2023 ND 53 and 2023 ND 120 were content-swapped — `markdown/2023/2023ND53.md` (and the matching pdf) held the 2023 ND 120 text, and `2023ND120.md`/pdf held the 2023 ND 53 text (confirmed by reading both PDFs).

- **File rename (`~/refs`, not version-controlled):** swapped both the `.md` and `.pdf` pairs so each name matches its content. Verified afterward: `2023ND53.{md,pdf}` = 2023 ND 53, `2023ND120.{md,pdf}` = 2023 ND 120.
- **Repointed 19722** (Goetz, 2023 ND 53) `source_path` and its ND `opinion_sources` row from the old misnamed `markdown/2023/2023ND120.md` → `markdown/2023/2023ND53.md` (text_content unchanged — it was already the 2023 ND 53 text).
- **Ingested 2023 ND 120 as oid 20503** via the ingest pipeline's helpers (`_add_citations`, `_record_source`, `recompute_primary`): Goetz v. Goetz, 2023-07-07, docket 20220231, author McEvers (Chief Justice Jensen and Justice Tufte joined; Surrogate Judge Nelson dissenting), disposition REVERSED, child-custody/residential-responsibility, cluster_id 9412027. text_content = the corrected `markdown/2023/2023ND120.md` (verbatim, 17 `[¶N]` markers); ND-neutral primary cite `2023 ND 120`; ND markdown primary source; quality score 80.8; FTS-indexed. Corpus 20,147 → 20,148. Invariants 22 ok / 2 known / 0 regressed. Snapshot `opinions.db.bak-pre-recover-2023nd120`; script `triage/recover_2023nd120_2026-05-26.py`.
- **Residual:** (a) no N.W.2d parallel cite yet (absent from CL and the opinion text); add when published. (b) `text_citations`/`cited_by` for 20503 are unbuilt (jetcite not installed) — a later `cite_extract` run populates the outbound graph, as for any fresh ingest.

## Batch `fix-three-dups-2026-05-26` — Goetz / Swanson duplicates + Holter cross-source leak

Three citation-collision / cross-source items flagged by name+date dedup, each verified against CourtListener and (for Holter) the West reporter `.doc`. Corpus 20,149 → 20,147 (two merges). Invariants 22 ok / 2 known / 0 regressed. Snapshot `opinions.db.bak-pre-dedup3-2026-05-26`; script `triage/fix_three_dups_2026-05-26.py`.

- **Goetz v. Goetz — true duplicate, merged 20385 → 19722.** Both rows were *Goetz v. Goetz, 2023 ND 53 / 988 N.W.2d 553*, 2023-03-31, docket 20220231, McEvers (CL confirms 988 N.W.2d 553 = 2023 ND 53). Kept 19722 (ND-neutral primary, 2 sources). **Discovered (logged TODO, not fixed here):** the real **2023 ND 120** Goetz v. Goetz (2023-07-07) is missing from the corpus and the `~/refs` files are content-swapped — `markdown/2023/2023ND53.md` contains the 2023 ND 120 text, `2023ND120.md` contains the 2023 ND 53 text. Needs a file-name swap + a new ingest of 2023 ND 120 (cross-repo).
- **Swanson v. Larson — true duplicate, merged 19616 → 17913.** Same opinion ingested twice via a zero-padded native cite: `2021 ND 0216` (17913) vs `2021 ND 216` (19616); identical source files. Normalized the survivor's cite to `2021 ND 216`, removed the redundant `2021ND0216.md` source row, aligned `opinions.source_path` to `markdown/2021/2021ND216.md`.
- **Holter v. City of Mandan — NOT a duplicate; fixed a mis-attributed parallel.** 17670 = *2020 ND 152* (main opinion, 2020-07-22, 946 N.W.2d 524) and 19516 = *2020 ND 202* (denial of rehearing with Jensen, C.J., dissenting, joined by Tufte, J., 2020-09-21) are distinct publications sharing docket 20190277. The West `.doc` filed at **948 N.W.2d 858** is explicitly the 2020 ND 202 rehearing dissent, so that parallel belongs to 19516 — but it had been hung on 17670 (CL grouped it onto the 152 cluster, the known CL parallel cross-contamination). Moved `948 N.W.2d 858` from 17670 → 19516; corrected 19516's corrupted docket (`2020ND202` → `20190277`) and date (`2020-07-22` → `2020-09-21`). Both opinions kept.

## Batch `unwrap-anchors-2026-05-26` (2, `field=text_content`) — last has_html anchors

The 2 remaining `has_html=1` opinions held genuine `<a href="URL">URL</a>` markup around URLs the Court itself cited: **20116** *Axvig v. Czajkowski* (2025-07-17) → `https://www.merriam-webster.com/dictionary/specification` ("See Merriam-Webster's Online Dictionary, [specification]"); **20290** *Matter of Emelia Hirsch Trust* (2025-04-24) → `https://www.ndcourts.gov/legal-self-help` (the form at "the Court's Legal Self Help Center"). Inner anchor text equals the href in both, so unwrapped each `<a href="X">X</a>` → `X`, leaving the bare URL — citation preserved, markup removed. Corpus `has_html` 2 → **0**; both rescore ~82. Invariants 22 ok / 2 known / 0 regressed. Script `triage/unwrap_anchors_2026-05-26.py`.

## Batch `dedup-13240-2026-05-26` + quality-scanner HTML/JS & prime-mark hardening — low-score follow-ups

Closed the two follow-ups from the low-score work; both turned out to be scanner false positives plus one real de-duplication.

**`dedup-13240-2026-05-26` (1, `field=text_content`).** 13240 *Johnson v. Johnson* (2000 ND 170) stored the opinion **twice**: a frontmatter/title/caption/attorney shell, then copy1 (the half whose `[¶N]` markers had been Thai-codec mojibake'd, repaired the prior batch) and copy2 (the originally-intact copy, complete through the ¶166 Sandstrom dissent). Healthy 2000-era siblings carry one copy. Kept the shell + the clean copy2 (`text[:first 'MARING, Justice'] + text[second:]`): 237,643 → 119,578 chars, one coherent opinion, ¶1–166, 0 garbage chars, score 67.9. FTS verified in sync.

**Quality-scanner HTML/JS detection tightened (`quality_scan.py`).** `has_html` was 13, of which 11 were false positives on legitimate legal prose: `_JS_RE`'s `function\s*\(` matched "governmental function (…)", "Prosecution Function (1971)", "banking function (…)" (6 opinions: 3434, 9554, 10982, 12909, 13138, 19939); `_HTML_RE`'s short tag names `th`/`a` matched dictionary usage quotes — "<the fruits of one's labor>", "<the wisdom that accrues with age>", "<a sentence of 20 years in prison>", "< the [amount] of the fine is doubled >" (5 opinions: 10112, 13701, 15792, 16336, 17430). Tightened `_HTML_RE` to require real tag+`attr="value"` syntax and `_JS_RE` to require a `function(){` body / `handler=` form. Result: `has_html` 13 → **2** — only the genuinely-embedded `<a href="https://…">` anchors remain (20116 *Axvig*, 20290 *Hirsch Trust*). A 3,000-opinion sample confirmed no false-positive blowup.

**Prime/double-prime added to `_LEGIT_NONASCII`.** 1787 *Bayne v. Thorson* (1917) scored 8.5 because `′`×7 and `″`×31 (feet/inches in a bridge-contract dimensional table, e.g. "6″ joists") were counted as garbage. `′ ″` are legitimate in legal text (surveys, metes-and-bounds, dimensions); added them. After a corpus `--rescan` nothing scores <25 (bottom is now legitimately-modest short/old opinions at 26.5–32). Invariants **22 ok / 2 known / 0 regressed**. Scripts: `triage/dedup_13240_2026-05-26.py`; snapshot `opinions.db.bak-pre-dedup13240-2026-05-26`.

## Batches `fix-noauthor-2026-05-26` + `demangle-13240-2026-05-26` + quality-scorer fix — no-author & low-score queues

**No-author / non-per-curiam queue (79 → 40).** `auto_author` only rescans opinions with a *non-null* author (it fixes garbled values), so the empty-author set needed manual byline-vs-per-curiam triage. Each correction verified against the opinion's own text:
- **5 author recoveries** (`field=author`): the authoring byline existed but was missed (page-image markers / post-syllabus position / separately-published concurrence). 441 → Morgan (`*1052 MORGAN, C. J.`), 20388 → Christianson (`CHRISTIANSON, J. (concurring)`), 20390 → Robinson (`ROBINSON, J. (concurring specially)`), 20391 → Gronna (`A. J. *247 GRONNA, District Judge`), 15216 → Sandstrom (`SANDSTROM, Justice.` ¶1; 2009 ND 113, confirmed via CourtListener).
- **34 per curiam** (`field=per_curiam`, 0→1): genuine `PER CURIAM.`/`Per Curiam.` dispositions (pre-1953 + modern Rule 35.1 and discipline per curiams) plus 12570 *Disciplinary Action Against Fisher* (ORDER OF SUSPENSION signed `/s/` by all five justices). Empty author is correct for these.
- **40 left untouched**: authorless summary dispositions ("Affirmed by summary opinion" / "Affirmed.") — no byline, no per-curiam label. CourtListener's own records carry `author: null, per_curiam: false` for these, so labeling them per curiam would invent a disposition the source doesn't state. They remain a recognized authorless-by-design category.

**Low-quality queue (18 `overall_score < 0.5` → 0).** Not OCR garble: `quality_scan.score_opinion` counted U+00A0 (non-breaking space — pervasive in Westlaw `.doc` exports) and `¢` as garbage and applied an *absolute* penalty (`score -= garbage_chars`), so any long clean opinion with ~70+ NBSPs was driven below zero and clamped to 0.0 (15 of 18 were also stale, scored before their later Westlaw promote). Fix: added U+00A0 + `¢` to `_LEGIT_NONASCII`; corpus-wide `quality_scan --rescan` (score range 0.0→ now 8.5–84.5, avg 59.2; `<0.5` queue empty; the original 18 now 37.5–68.0).

**`demangle-13240-2026-05-26` (1, `field=text_content`).** 13240 *Johnson v. Johnson* (2000 ND 170) had its analyzer `[¶N]`/`§`/em-dash characters mis-decoded through a Thai (CP874) codec: `ถ`(U+0E16)×212→`¶`, `ง`(U+0E07)×75→`§`, `โ\x80\x94`(U+0E42 + control bytes)×9→`—` (em-dash UTF-8 `E2 80 94`). Counts match the pristine on-disk `markdown/2000/2000ND170.md` exactly; repaired in place, restoring the paragraph markers the proofread/pinpoint tools rely on. Snapshot `opinions.db.bak-pre-author-percuriam-2026-05-26`; scripts `triage/fix_noauthor_2026-05-26.py`, `triage/demangle_13240_2026-05-26.py`. Invariants **22 ok / 2 known / 0 regressed**. **Open follow-up:** 13240's `text_content` (~237 KB) is the repaired ND markdown concatenated with the NW2d OCR copy — a double-source ingest defect to de-dup via re-ingest (TODO §8).

## Batch `restore-phantom-westlaw-paths-2026-05-26` — 35 blanked vol-79 westlaw source paths restored

The §2-residual triage (2026-05-25) flagged 35 `opinion_sources` rows with an empty `source_path`, all `source_reporter='westlaw'`, as "phantom second sources." They are not phantom: all 35 are vol-79 N.D. Reports Westlaw `.doc`s at `~/refs/nd/opin/N.D./79/<page>-<slug>.doc` that exist on disk. Their paths were set correctly by `backfill-westlaw-source-paths` (2026-04-27), then **blanked by a bug in `receive_westlaw._promote`**: the `westlaw-receive-2026-05-16` run computed an empty `archive_path` and overwrote both `opinions.source_path` and the westlaw `opinion_sources.source_path` with `''`, then set `is_primary=1` on the now-empty row (the `is_primary=1 WHERE source_path=archive_path` clause matched the empty path). `text_content` had already been promoted to the Westlaw bound text — only the file pointer was lost.

Verification before restore (paths from the recorded backfill `new_value`): N.D. citation page == `.doc` filename page for 35/35 (0 mismatch); file exists for 35/35; two captions spot-read (79 N.D. 366 *Carroll v. Ryan*; 79 N.D. 673 *State ex rel. City of Minot v. Gronna*); the surviving 34 vol-79 westlaw siblings already use the identical absolute-path convention with the westlaw row primary.

Restored both `opinions.source_path` (34 westlaw-primary opinions) and the westlaw `opinion_sources.source_path` (all 35) to the absolute `/Users/jerod/refs/nd/opin/N.D./79/...` path. **12705** *In re Lyons' Estate* (79 N.D. 595 / 58 N.W.2d 845) is NW2d-primary — only its westlaw `opinion_sources` row was restored (it stays NW2d-primary, westlaw as 2nd source); jaccard 0.86 vs the NW2d `text_content` confirms the same opinion, so its `validation_status.crosscheck_state` was upgraded `single_source_accepted` → `cross_checked` (`sources_seen=["NW2d","westlaw"]`).

Result: corpus-wide `opinion_sources` rows with empty `source_path` now = **0** (any reporter). Corpus unchanged at 20,149. Invariants **22 ok / 2 known / 0 regressed**. Snapshot `opinions.db.bak-pre-phantom-paths-2026-05-26`; restore script `triage/restore_phantom_westlaw_paths_2026-05-26.py`. **Open code follow-up:** guard `receive_westlaw._promote` so an empty `archive_path` can never overwrite a non-empty `source_path` (prevents recurrence on the next gap-era receive).

## `cited_by` shared-page disambiguation — 2026-05-25 (graph rebuild, not a row batch)

Fixed a silent misattribution in the citation graph: `cite_extract.build_citation_lookup` mapped each citation string to a *single* opinion, so when distinct cases share a reporter page (845 colliding cite strings, 1,750 opinions), every citer of that page was attributed to one arbitrary winner. Concretely, all 8 citers of `298 N.W.2d 372` had been attributed to *In re McMahon* (20482) when they actually cite *Boedecker v. St. Alexius Hospital* (8266) — which showed 0 citers.

Resolution (depends on **jetcite ≥2.1.0**, which now returns `Citation.antecedent_name`, the case name preceding a cite):
- `build_citation_lookup` is now list-valued (all candidates per cite); added `text_citations.antecedent_name` (additive column + self-healing migration in `db.py`).
- New resolver `_resolve_cited_oid`: drops candidates filed after the citing opinion (a case can't be cited before it exists), then picks the candidate whose `case_name` shares the most distinctive tokens with the citing opinion's antecedent name; a tie or no-match is **skipped** (not guessed) and logged to `triage/cited-by-unresolved-collisions.csv`.
- Backfilled `antecedent_name` for the colliding-cite rows (`triage/backfill_antecedent_names_2026-05-25.py`), then rebuilt: `python -m ndcourts_mcp.cite_extract --cited-by-only`. Snapshot `opinions.db.bak-pre-citedby-disambig-2026-05-25`.

Result: `cited_by` 112,226 → **110,455** edges (net −1,771: colliding cites re-pointed to the correct case; 3,848 genuinely-ambiguous edges skipped). Verified: *Boedecker* 8266 now has its 8 citers, *McMahon* 20482 has 0; `100 N.W. 1084` is now distributed across Hanson/Lough/Marshall-Wells. Invariants 22 ok / 2 known / 0 regressed. The unresolved triage is dominated by **modern same-name dup clusters** (e.g., `2022 ND 123` → 18040|18052, Goetz `2023 ND 53` → 19722|20385) where two DB opinions share both the cite and the name — useful input to the §6 DEFER_MODERN dedup, not a name-extraction failure.

## Batches `fix-author-byline-` / `fix-coa-caption-court-` / `fix-percuriam-orders-2026-05-25` — §2 low-confidence Quick Check (30 opinions)

Worked the §2 low-confidence picker's priority set (`triage/lowconf-1953-1996-2026-05-25.csv`). The CSV predated the 2026-05-25 Westlaw apply, so all 94 priority rows were already tagged out of `unvalidated`; recomputing the anomaly conditions against current state left **31 rows still flagged**, resolved here down to **2** (20482 pending external lookup; 9770 a confirmed false positive). Snapshot `opinions.db.bak-pre-lowconf-fixes-2026-05-25`. Invariants **22 ok / 2 known / 0 regressed**. Each correction was verified against the opinion's own stored text (byline / caption / signature block) — no heuristic bulk-apply.

- **`fix-author-byline-2026-05-25` (10):** single-letter "authors" were stray middle initials parsed out of panel signature blocks; recovered the real authoring judge from each "Opinion of the Court by …" byline — 20422 Pederson, 20433 Pederson, 20434 Jorgensen, 20437 Hoberg, 20441 Ilvedson, 20447 Bakken, 20461 Hodny, 20469 Pederson, 20475 Kerian, and 20436 Erickstad (was empty). Seven of these are ND Court of Appeals panel opinions (1988–94) decided by District/Surrogate judges sitting by assignment.
- **`fix-coa-caption-court-2026-05-25` (2):** leaked Westlaw header "Court of Appeals of North Dakota." had been stored as the `case_name`. **20480** → *Reimers Seed Co. v. Stedman* (court → North Dakota Court of Appeals, author Heen); **20487** → *City of Bismarck v. Berger* (court → COA, author Medd). Court field corrected on the two genuinely-mislabeled COA opinions; 20434 left as Supreme Court (its own body header reads "IN THE SUPREME COURT" despite a CA docket suffix).
- **`fix-percuriam-orders-2026-05-25` (18):** Supreme Court attorney-discipline orders and judicial-vacancy administrative orders that are institutional/per curiam dispositions (signature block reads "BY THE COURT", all-justices `/s/`, or an unsigned "IT IS ORDERED") — set `per_curiam=1`, which resolves the spurious NO_AUTHOR flag honestly. oids 8873, 9080, 9162, 9207, 9767, 10028, 10722, 10796, 10797, 11798, 12201, 12204, 20479, 20481, 20483, 20484, 20485, and 20482.
- **Validation tagging + picker hardening:** the 29 fully-fixed oids → `validation_status.crosscheck_state='corrected'` (batch `lowconf-quickcheck-2026-05-25`). The picker query now `LEFT JOIN`s `validation_status` and excludes resolved states (`corrected`/`single_source_accepted`/`cross_checked`) so a rebuild no longer re-queues validated rows — the 1953–1996 worklist drops from 6,069 era rows to **47** still needing attention.
- **`fix-mcmahon-caption-2026-05-25` (1):** **20482** `case_name` `"Unk"` → **In re Disciplinary Action Against McMahon** (case_name_full = "In the Matter of the Application for Disciplinary Action against Patrick M. McMahon, a member of the Bar of the State of North Dakota"). Identified via CourtListener cluster 7923731, corroborated by the Westlaw `.doc` and confirmed by matching date (1980-08-20), the five concurring justices (Erickstad/Paulson/Pederson/Sand/VandeWalle), and ND bar membership. CL's "South Dakota Supreme Court" label is a CL error; `court` left as North Dakota.
- **`fix-mcmahon-docket-2026-05-25` (1):** the `298 N.W.2d 372` shared-cite with oid 8266 *Boedecker* **verified against the bound reporter image** (Westlaw page PDF of 298 N.W.2d 372): the McMahon order sits at the top of p.372 and *Boedecker* begins at the bottom of the same page — a legitimate shared starting page, both cites correct (not a mis-pagination). Recovered McMahon's docket `No. 9723` from the image; 20482 `crosscheck_state` → `cross_checked`. (The 8 `cited_by` on 20482 most likely belong to *Boedecker* — a low-priority `cite_extract` attribution re-check.)
- **`register-nwimage-298nw2d372-2026-05-25` (2):** filed the Westlaw page image at `~/refs/nd/opin/NW2d/298/372.pdf` and registered it as a non-primary `NW-image` source on **both** oid 20482 (McMahon) and oid 8266 (Boedecker), the two cases that begin on that page. Same refs-only image-provenance convention as `register-nwimage-confidential-2026-05-25`. **9770** *Estate of Papineau v. All Other Persons Unknown* is a false positive — "Unknown" is a legitimate quiet-title defendant; no change.

## Batch `merge-356nw2d-dups-2026-05-25` (5 merges) + `register-nwimage-confidential-2026-05-25` (2) — 356 N.W.2d 1984 dedup + 1984 audit

The §2 re-pull of the 6 "single-source" 356 N.W.2d opinions exposed a CL artifact: a **−4-page cascade of duplicate ingests** in vol 356 (1984). CL ingested a second copy of each of these opinions shifted **−4 pages and a few days earlier**, so the dup's N.W.2d cite collided with a neighbor (incl. two interleaved Nebraska cases, *State v. Vernon* 218 Neb. 539 = 356 N.W.2d 887 and *State v. Kaiser* 218 Neb. 556 = 356 N.W.2d 890). Each dup was confirmed against the Westlaw `.doc` pulled by case name + text jaccard.

**5 duplicate merges** (`merge_opinions.merge_pair`; keep = correct-cite, court-archive/westlaw-sourced twin; drop = −4 dup; all drops had inbound cited_by handled). After each, removed the dup's carried-over wrong cite, synthetic cite, and wrong-page source from the survivor; re-ran `recompute_primary`:

| Dropped (−4 dup) | Kept (twin) | Case · jaccard |
|---|---|---|
| 9235 @ 889 | 20486 @ 893 | State v. Lawson · 0.83 |
| 9237 @ 890 | 9239 @ 894 | First Federal v. Scherle · 0.83 |
| 9240 @ 897 | 9243 @ 901 | Calavera v. Vix · 0.79 |
| 9242 @ 899 | 9244 @ 903 | State v. Ronngren · 0.84 |
| 9238 @ 893 | 9241 @ 897 | Bauer v. Bauer · 0.91 (found by the 1984 audit; both 2-source) |

Also re-homed **State v. Lawson's own court-archive page** (`court-archive/356/1007.htm`, docket 1007, which itself cites 356 N.W.2d 893) from the Bauer −4 dup (9238) where the cascade had misfiled it, onto the Lawson survivor (20486) — Lawson now correctly carries court-archive + westlaw. Corpus 20,154 → **20,149**. Snapshots `opinions.db.bak-pre-merge-356dups-2026-05-25`, `-pre-bauer-2026-05-25`. Resequenced `section10-resequence-2026-05-25f`/`-25g`; invariants **22 ok / 2 known / 0 regressed**.

**1984 audit (task complete):** an all-pairs text-jaccard sweep of all 226 ND opinions filed in 1984 (`triage/merge_356nw2d_dups_2026-05-25.py` + ad-hoc sweep) found the Bauer pair as the *only* remaining duplicate (now merged); same-date and docket-collision passes corroborate. **1984 is now duplicate-clean.** A broader pass (adjacent N.W.2d volumes / other years for the same CL −4-cascade signature) is a recommended follow-up.

**2 confidential NW-image registrations** (`register-nwimage-confidential-2026-05-25`): the genuinely single-source confidential cases **Clw v. Mj** (7710, 254 N.W.2d 446) and **Bh v. Kd** (11482, 506 N.W.2d 368) — page-image PDFs filed at `NW2d/<vol>/<page>.pdf`, registered as non-primary `NW-image` sources; anonymized `text_content` left unchanged (no de-anonymizing .doc text merged).

## Batch `fix-casename-rorvig-10933-2026-05-25` (1) — case-name correction

oid 10933 (472 N.W.2d 914, docket 910249, 1991-08-15) case_name **"Disciplinary Board of the Supreme Court of the State v. Johnson" → "…v. Rorvig"**. CL had mislabeled it with the name of its shared-page companion *Johnson* (oid 10931, docket 910126, 1991-04-29). Authority: the Westlaw/bound caption is "Disciplinary Action Against Donald K. Rorvig," and the Rorvig `.doc` matched 10933 at jaccard 1.00 (surfaced during `westlaw-receive-2026-05-25`). Invariants 22 ok / 2 known / 0 regressed.

## Batch `westlaw-receive-2026-05-25` (180) + editorial strips — single-source 1953–1996 second sources

Ingested the Westlaw Find&Print returns for the §2 single-source pull (183 cites, 3 zips). `receive_westlaw` promoted the Westlaw bound text to the authoritative second source. **177 of 183 pull-list opinions now carry a `westlaw` source** (178 auto-promoted + 2 explicit-oid; 3 of the 178 promotes, incl. *Rorvig*/10933, were non-pull-list shared-page siblings). Snapshots `opinions.db.bak-pre-westlaw-singlesource-2026-05-25`, `-pre-explicit-2026-05-25`. Invariants **22 ok / 2 known / 0 regressed**.

- **178 auto-promoted** (`receive_westlaw --incoming … --apply`); 0 created, 0 low-sim.
- **2 explicit-oid promotes** (`triage/promote_explicit_singlesource_2026-05-25.py`): *Sletten* (11968) and *Moosbrugger* (11969) — both at 536 N.W.2d 354 **and** filed the same day, so the formulaic disciplinary captions went AMBIGUOUS in the auto-resolver; hand-confirmed (jaccard 0.85 / 0.71).
- **472 N.W.2d 914 dup** resolved cleanly: *Johnson*→10931 and *Rorvig*→10933 (jaccard 1.00, confirming 10933 is **Rorvig** despite its "Johnson" `case_name` — a cleanup item).

**Editorial strips (redistribution scope):** the `receive_westlaw` memorandum-fallback path bypasses the Synopsis stripper, so Westlaw editorial leaked. Cleaned: `strip-westlaw-headnotes-2026-05-25` (20 rows — West Headnotes / Procedural Posture) + `strip-westlaw-synopsis-singlesource-2026-05-25` (4 rows — Synopsis stub, scoped to this batch). **0 West Headnotes / Procedural Posture markers remain** in the promoted rows. **14 rows** retain a *narrative-style* Synopsis ("no-stub-found") that the stripper conservatively leaves to avoid clipping court narrative — flagged to the project's existing human-review backlog (a separate corpus-wide ~285-row synopsis residue was noted, out of scope here).

**6 still unsourced (need a targeted re-pull):**
- **4 in 356 N.W.2d 889–899** (Lawson 9235, Scherle 9237, Calavera 9240, Ronngren 9242): Westlaw returned two **Nebraska** cases for some 356-range requests — *State v. Vernon* (218 Neb. 539) and *State v. Kaiser* (218 Neb. 556) — which the parser correctly refused (no ND N.W.2d cite). Re-pull by exact cite + verify our N.W.2d page numbers for these 1984 ND opinions. (*Calavera* 9240 shares 356 N.W.2d 897 with *Bauer* 9241, which already had a source and absorbed that pull.)
- **2 anonymized confidential cases** not returned: *Clw v. Mj* (254 N.W.2d 446), *Bh v. Kd* (506 N.W.2d 368) — handle carefully.

Revert: `cleanup revert westlaw-receive-2026-05-25` (+ `align_primary_source --apply`); strips revert by their own batches.

## Batch `fix-white-lauder-2026-05-25` (2) — White v. Lauder knot resolved (10 N.D. 400 / 445)

Resolved the long-flagged *White v. Lauder* knot (oids 5833/5834). Read bound N.D. Reports vol 10 pp.400 & 445 (offset +64) and the N.W. images (NW/87/996, /1135). **Finding: two distinct companion mandamus per curiams** (ruled keep-both 2026-05-25), both following *Gunn v. Lauder* (10 N.D. 389, 87 N.W. 999), both at 87 N.W. 1135, both filed Nov. 21, 1901:
- **10 N.D. 400** (oid 5834): "Patrick White v. W. S. Lauder," with syllabus "Mandamus to Judge—Disqualification—Failure to Call Other Judge."
- **10 N.D. 445** (oid 5833): "Patrick White et al. v. W. S. Lauder," no syllabus. Distinct LEXIS IDs (57/58); bound prints both at separate pages with other cases between.

Two errors corrected on **5834**: (1) `date_filed` **1901-10-25 → 1901-11-21** — the 10-25 was *Willard v. Monarch Elevator*'s date (the next case down on bound p.400, "filed Oct. 25, 1901"), mis-grabbed by CL; bound + CL text both say Nov. 21. (2) NW-image source **NW/87/996.pdf → NW/87/1135.pdf** — 996 is *Willard*'s N.W. page (the N.W. reporter cross-references 10 N.D. 400 to Willard); White is at 87 N.W. 1135. Both White companions now share the 87 N.W. 1135 image. No merge. Snapshot `opinions.db.bak-pre-whitelauder-2026-05-25`; resequenced `section10-resequence-2026-05-25e` (16 cites; 5834 now 1901 ND 64, 5833 ND 65). Invariants **22 ok / 2 known / 0 regressed**.

## Batch `fix-date-holds-clerror-verified-2026-05-25` (23) — date-discrepancy holds reviewed

Reviewed all **93 >31d `date_filed` holds** (`triage/date-discrepancy-holds-2026-05-24.tsv`). **Key finding: the court-source date is NOT reliably the opinion's filing date for these holds** — archive.ndcourts.gov pages surface several dates (petition, argument, lower-court memorandum, rehearing) and the parser can grab a non-filing one. So the ratified "court date governs" policy (§2) does not cleanly apply to the >31d band.

**Arbiter = the N.W.2d reporter volume window.** Opinions in one N.W.2d volume are filed within ~weeks; CL's `date_filed` matches that window for the bulk of the corpus. Testing both candidate dates against each opinion's volume window (built from volume-mates' CL dates, in `triage/classify_date_holds_2026-05-25.py`) split the 93 into two opposite error patterns:
- **40 — KEEP CL**: CL is in-window; the court-source date is months *before* it (a proceeding/argument date, or a wrong document in the docket). CL is correct.
- **23 — ADOPT court** (this batch): the court date is in-window; CL is *after* it. CL had recorded a later **rehearing/denial/mandate** date as `date_filed`. Each verified by reading the opinion's own source — archive "Filed" line (20) or Westlaw `.doc` (3, which show both the filing date and the later CL date, e.g. 8359 Ness filed 1981-01-29 with rehearing 1981-04-15; 10098 Hoopman filed 1988-03-29 with 1988-05-09). Reporter cite independently confirms (e.g. 8359 in 301 N.W.2d cannot be an April 1981 opinion). **8454 City of Casselton**: CL had **1994-10-25** for a **1981** case (307 N.W.2d 849 + docket Civ. 9935 + archive "Filed June 30, 1981") → corrected to 1981-06-30.
- **30 — KEEP CL (default)**: 28 land in a wide/contaminated window (undecidable by the test — some windows are themselves polluted by other bad dates) + 2 degenerate; left at CL per the conservative default (some may be the same rehearing-date pattern; a future per-source pass could revisit).

Snapshot `opinions.db.bak-pre-dateholds-verified-2026-05-25`. Resequenced `section10-resequence-2026-05-25d` (724 synthetic cites re-dealt). Invariants **22 ok / 2 known / 0 regressed**.

**Process note (transparency):** an earlier bulk apply of 69 ADOPT (`fix-date-holds-adopt-court-2026-05-25` + resequence `-25b`) was made before the volume-window validation, then found to be ~40 wrong and reverted — dates via `cleanup revert`, synthetic cites by re-running the resequencer (`-25c`, since §10 batches log under a synthetic `citation_synthetic_order` field the generic `cleanup revert` can't reverse — a known tool limitation). Net effect of `-25b`/`-25c` is nil; only the 23 verified corrections + `-25d` stand.

## Vol 21 §10 cluster verification + vols 50/64/74/23/32 dispositions — 2026-05-25 (NO data changes)

Filed vol 21 (and vol 23, which turned out to need nothing) into the refs tree and verified vol 21's clusters at 300 dpi (offset **+22**, flat across the volume). Resequencer dry-run **0 of 12,604** drift before and after. **No DB changes.**

- **21 N.D. 69** — *Willis v. Weatherwax* (699, 128 N.W. 307) above *State ex rel. Kramer v. Kiefer* (733, 129 N.W. 925); both 1910-10-21, both per curiams following different lead cases. NW order = bound order. Provisional correct. No change.
- **21 N.D. 348** — *Lanpher-Skinner Co. v. Quam* (765, 131 N.W. 246) above *Heard v. Holbrook* (767, 131 N.W. 251); both 1911-03-28. NW order = bound order. Provisional correct. No change.

**Dispositions for the not-on-disk volumes** (50/64/74 are not on archive.org; user investigating physical copies):

- **Vol 50 — 50 N.D. 25 — RESOLVED without the volume.** *Lincoln Addition Improvement Co. v. Lenhart* lead (2863, 195 N.W. 14, full opinion) + same-day per curiam Mem (20390, 195 N.W. 33, "joint with Baker v. Lenhart"). Lead + dependent per curiam → **lead-first** per the 2026-05-25 ruling; the default NW-page tiebreak already orders it lead-first (14<33). Provisional 1922 ND 171 (lead) / 172 (per curiam) correct. No photo, no KNOWN_ORDER entry.
- **Vol 64 — 64 N.D. 367 — VERIFIED + REORDERED 2026-05-25** (HeinOnline per-case scan `64_N.D._367_Caselaw_Scan.pdf`, filed `~/refs/nd/opin/N.D./64/367-hein-scan.pdf`). The bound page prints *Marian Ott v. L. R. Kelley* (4484, File 6233, 252 N.W. 271, per curiam) ABOVE *Thorvaldson-Johnson Co. v. Cochran* (4482, File 6234, 252 N.W. 268, Christianson J., continues to p.368) — i.e. N.D. order follows file number (6233<6234), the inverse of the N.W. tie (268<271). N.D. bound order governs → added `KNOWN_ORDER [4484, 4482]` and re-ran the resequencer (`section10-resequence-2026-05-25`, **2 cites**): Ott 1934 ND 6→**5**, Thorvaldson 5→**6**. Snapshot `opinions.db.bak-pre-section10-vol64-2026-05-25`. Invariants **22 ok / 2 known / 0 regressed**.
- **Vol 74 — 74 N.D. 242 — investigate one-vs-two before ordering (pp. 241–243).** oids 7179 (*N.P. Ry. v. McDonald*; per curiam, "decision in application of Hanson, 21 N.W.2d 341, determines this case") and 7180 (*In re Adams*; Burr, J. full opinion) share docket **File 6966**, cite **21 N.W.2d 351**, and the same parties, but carry different CL cluster_ids (6852041 vs 3933583) and word-jaccard 0.635. Signature of a CL double-ingest or a lead+companion split rather than two independent cases — resolve as a §6 merge/keep-separate question; the bound page shows whether one opinion or two print there.
- **Vols 23 & 32 — NO verification needed.** Each has exactly one shared N.D. page and it is *different-date* (23 N.D. 352: 1912-05-27 / 1912-06-14; 32 N.D. 373: 1916-01-05 / 1916-01-06). The `(date, …)` sort already orders these correctly; no on-page tie to break. Removed from the pending list.

## Vols 16/17/18 §10 cluster verification — 2026-05-25 (NO data changes)

Filed the three newly-obtained bound volumes (16, 17, 18) into `~/refs/nd/opin/N.D./<vol>/_bound-volume.pdf` and read every §10 shared-page cluster at 300 dpi (main session — bg agents are denied Bash+Read, can't render scans). Page offsets: vol 16 +16 near p.59, +18 by p.106 (scan accumulates ~2 unnumbered leaves); vols 17 & 18 a flat +18. Resequencer dry-run before and after = **0 of 12,604** synthetic cites drift. **No DB changes.**

- **16 N.D. 59** — Kerr v. Sunstrum (274) → Kerr v. Swanson (276) → Kerr v. Herred (278, next day 1907-02-23). All dependent per curiams following *Kerr v. Anderson* (16 N.D. 36, a different page). Sunstrum/Swanson tie matches the NW-page tiebreak (614 < 615). Provisional correct. No change.
- **16 N.D. 106** — State ex rel. Harvey v. Davies (296, 1907-04-30) above A. B. Farquhar Co. v. Higham (295, 1907-05-04). Different dates; date sort governs. No change.
- **17 N.D. 393** — Soliah v. Cormack (415, 1908-05-28) and Erickson v. Elliott (422, 1908-06-19) share a start page but are different dates; Erickson is a short per curiam slotted above the earlier-dated Soliah (editorial). Date sort correct (68, 72). No change.
- **17 N.D. 266** — *Skeffington v. Prante* (383, dependent per curiam) printed ABOVE *Ross v. Prante* (382, lead with full syllabus); both filed 1908-03-20, both genuinely start on p.266 (Ross continues to 267). Kept **lead-first** (Ross 1908 ND 40, Skeffington 41) per the 2026-05-25 ruling — the reporter's top-of-page placement of the short companion is a typesetting artifact, not decision sequence. (Skeffington's per curiam mis-prints Ross's cite as "17 N.D. 226"; harmless OCR/print typo, Ross is at 266.) No change.
- **18 N.D. 76** — *State ex rel. City of Minot v. Willis* companion per curiam (20386, 118 N.W. 823) printed ABOVE the lead (458, 118 N.W. 820); both filed 1908-11-19. Lead's caption+syllabus sit at the bottom of p.76, opinion body (Fisk, J.) on p.77. Kept **lead-first** (458 → 1908 ND 105, 20386 → 106) and the lead's cite **at 18 N.D. 76** (caption-page convention; the companion's "18 N.D. 77" is an opinion-text pinpoint). No change.

**Convention ruled 2026-05-25:** for a lead opinion + its same-day dependent per curiam sharing a page, order the LEAD first even where the reporter prints the short companion above it; do not add a `KNOWN_ORDER` flip (the default NW-page tiebreak already does it). Encoded in `triage/section10_resequence_2026-05-24.py`'s `KNOWN_ORDER` comment. Verified-volume list updated in TODO-validation.md §10.

## Batch `fix-date-bound-volume-2026-05-24` (2) + `section10-resequence-2026-05-24e` (3) — vols 10/27/41/47 cluster verification

Verified the §10 shared-page clusters in the four newly-filed bound volumes (10, 27, 41, 47) by reading each N.D. page at 300 dpi. (A background agent was attempted but its sandbox denied Bash + Read — it couldn't render/read the scans — so this was done in the main session. Offsets: vol 10 +64, vol 27 +42, vol 41 +32, vol 47 +22.)

- **27 N.D. 458** — Hackney v. Lynn → Bussey v. Boynton (both filed 1914-04-13). Matches provisional (58, 59). No change.
- **41 N.D. 473** — Druey v. Baldwin (lead) + Robinson, J. separate opinion (a Mem at 182 N.W. 700). Lead before separate by design; provisional correct (13, 14). No change.
- **47 N.D. 266** — Altenbrun (lead) + concurrence (one caption, "181 N.W. 590, 908"). Lead before concurrence; order correct. **Date fix:** bound shows "Opinion filed January 28, 1921"; DB had 1921-01-24 → corrected **2473 & 20388 → 1921-01-28** (`fix-date-bound-volume-2026-05-24`, court date governs, 4d). Resequence `section10-resequence-2026-05-24e` (3 cites; Altenbrun now 1921 ND 17/18, lead first).
- **10 N.D. 400 — FLAGGED, not changed.** Not a real same-date cluster: *White v. Lauder* (oid 5834) has DB date 1901-10-25 but the bound page reads "Opinion filed Nov. 21, 1901", and it is entangled with **oid 5833** (also *White v. Lauder*, 1901-11-21, **10 N.D. 445**, same N.W. 1135) — 5834's NW-image source is actually at 87 N.W. **996**, not 1135. A cite/page knot among the related White v. Lauder / Ginn mandamus matters (87 N.W. 996–1135); needs both bound pages (400 + 445) + the N.W. pages read to determine whether there are one or two opinions and their correct cites/dates. **Do not date-fix 5834 in isolation.**

Invariants **22 ok / 2 known / 0 regressed**; all 4 synthetic invariants OK; 0 synthetic dup strings. (`neutral_cite_uniqueness` reads 247 not 258 — a concurrent native-1997 dedup in the shared `opinions.db` from the parallel casename session, unrelated to this batch.)

## Batch `fix-date-court-filed-2026-05-24` (108) + `fix-date-holds-investigated-2026-05-24` (2) — court filing date governs

**Policy (ratified 2026-05-24):** where CL's `date_filed` disagrees with the court's filing date — the court-archive "Filed" line (archive.ndcourts.gov) or the bound N.D. Reports/`.doc` date — the **court's date governs**. Resolver: `triage/resolve_date_discrepancies_2026-05-24.py`. Snapshot `opinions.db.bak-pre-datefix-2026-05-24`.

- **108 auto-adoptions applied** (`fix-date-court-filed-2026-05-24`): all **≤31-day** gaps (the filed-vs-decided/released band), where the court source date is safely the true filing date. 37 ≤7d, 23 8–14d, 48 15–31d.
- **2 investigated holds corrected** (`fix-date-holds-investigated-2026-05-24`): **Starke v. Starke** (20457) 1989-07-17 → **1990-07-17** (column was a year-typo — the only non-1990 opinion in the 458 N.W.2d cluster); **Larson disciplinary** (20479) 1990-06-11 → **1990-09-21** (column was a *response deadline* quoted in the order; the `.doc` order date is Sept 21, 1990).
- **2 holds confirmed correct as-is** (column kept): Bard (10248, archive mis-parsed "1998" for a 430 N.W.2d=1988 case), Robar (8360, archive "1982" for a 301 N.W.2d=1980-81 case).
- **6 rehearing-like holds left untouched** (court date later by 44–183d): 7396, 10655, 10797, 8677, 6948, 1014.

**Self-correction (important):** the resolver's guard was initially asymmetric — it held only court-dates *later* by >31d (rehearings) but **auto-adopted large *earlier* gaps**, which silently applied **85 bad date changes** including a 90-year jump (oid 9597 1986→1896), a 13-year jump (8454 1994→1981), and an 11-opinion cluster all collapsed to 1992-05-05 (archive parse artifacts). **All 85 reverted**; the guard is now **symmetric** (hold any >31d gap, either direction) and those 85 are held for review. The 108 kept are all ≤31d. Resequence `section10-resequence-2026-05-24d` (872 provisional cites re-ordered, dominated by the Starke 1-year move). Invariants **22 ok / 2 known / 0 regressed**; `neutral_cite_uniqueness` 258. Held set (93 total) written to `triage/date-discrepancy-holds-2026-05-24.tsv` for manual review.

## Batch `strip-westlaw-headnotes-2026-05-24` (85 opinions — pre-release editorial strip)

**Redistribution-scope cleanup, surfaced by the `make_release` gate before v0.5.0.** 85 westlaw-sourced opinions (1970–2024) carried a leading Westlaw editorial block — a "Synopsis" stub + a `Procedural Posture(s):` line — ahead of the court-authored content. Per the redistribution scope (NOTICE.md), Westlaw editorial is excluded from the public DB. Ran `strip_westlaw_headnotes.py --apply`: surgically removed the Synopsis stub + Procedural Posture line (court content begins at the first of "Syllabus by the Court"/"Syllabus"/"Attorneys and Law Firms"/"Opinion"/author byline), preserving the opinion, syllabus, and factual record. 85/85 stripped cleanly (0 flagged, 0 collapsed; deltas ~80–115 chars each). Post-strip scan: **0** editorial markers (West Headnotes / Procedural Posture / Thomson Reuters / KeyCite / End of Document). Full prior `text_content` logged to the changelog for revert (`cleanup revert strip-westlaw-headnotes-2026-05-24`); snapshot `opinions.db.bak-pre-strip-headnotes-2026-05-24`. Root cause is fixed-forward in `ingest_westlaw._is_section_header`; these 85 predated that fix.

## Batches `fix-source-provenance-2026-05-24` (5) + `fix-goetz-stray-cite-2026-05-24` (1)

**Source-provenance cleanup, following the neutral-cite untangle below.** After the cites/case_name/docket were corrected, two rows still pointed `source_path`/`opinion_sources` at the *displaced* case's files:
- **16924 (State v. Ayala, 2017 ND 126):** `source_path` + primary `opinion_sources` `markdown/2017/2017ND116.md` (Cox's) → `…/2017ND126.md`; archive source `archive/2017/20160380.htm` (Cox's docket) → `…/20160369.htm` (Ayala's; file exists).
- **17030 (Disciplinary v. Lee, 2017 ND 216):** `source_path` + primary `opinion_sources` `…/2017ND241.md` (Questar's) → `…/2017ND216.md`. (Docket `20170241` is Lee's REAL docket per the PDF — unchanged.)
Cox (16930) and Questar (17053) were already clean and keep `…116.md`/`…241.md`. `source_path` and the is_primary `opinion_sources` row updated in lockstep; `source_path_matches_primary`/`source_reporter_matches_primary`/`primary_source_unique` all green. Tool: `triage/fix_source_provenance_2026-05-24.py`.

**Goetz (19722) — resolved the dual-neutral-cite, flagged the rest.** PDF check confirmed a **scraper FILENAME SWAP**: `pdfs/2023/2023ND120.pdf` actually contains *2023 ND 53* (filed Mar 31, REMANDED) and `pdfs/2023/2023ND53.pdf` contains *2023 ND 120* (filed Jul 7, REVERSED) — two distinct opinions in docket 20220231 (the July opinion's ¶1 cites the March one). 19722's TEXT is the March *2023 ND 53*, so its `2023 ND 120` cite was the stray — dropped (kept `2023 ND 53` + `988 N.W.2d 553`); 19722 is now a clean `2023 ND 53`. After this, **no opinion carries >1 native neutral cite.** Tool: inline (batch `fix-goetz-stray-cite-2026-05-24`). **Flagged, NOT fixed (needs source-tree + dedup work):** (a) 19722 and **20385** are now duplicate `2023 ND 53` rows (0.916 text sim) — merge candidate; (b) the real `2023 ND 120` (July) is **missing** — its authoritative text is on disk at the mis-named `markdown/2023/2023ND53.md`; (c) ROOT CAUSE: swap the 4 mis-named refs files (`2023ND53`/`2023ND120` × `.pdf`/`.md`) in the scraper output, then re-ingest, to fix permanently (text isn't stored verbatim, so a manual paste would mis-format vs the corpus).

## Batches `fix-neutral-cite-contamination-2026-05-24` (16 stray drops) + `-invert` (2 corrections)

**CL-metadata "two unrelated neutral cites in one record" contamination (Feldmann class).** 17 opinions carried 2 native `ND-neutral` cites; one is the real cite, the other a stray copied from a different case's CL record. Dropped the stray from 16 rows (excluded 19722, below) and rebuilt `cited_by` so no edge resolves a stray to the wrong row. Real cite identified from the court `markdown/YYYY/YYYYNDn.md` filename — **then double-checked against the authoritative bound PDFs** (`~/refs/nd/opin/pdfs/`), which caught two that the filename heuristic got **backwards** (the markdown file itself was misfiled):
- **16924** text is *State v. Miguel Ayala* → real `2017 ND 126` (N.W. 894/865). `2017 ND 116` is *State v. Cox* (oid 16930, N.W. 894/906) — a duplicate, dropped. First pass wrongly kept 116 / dropped 126; **inverted** in `-invert`.
- **17030** text is *Disciplinary Action Against Lee* → real `2017 ND 216` (N.W. 901/727). `2017 ND 241` is *WSI v. Questar* (oid 17053, N.W. 902/757) — duplicate, dropped. **Inverted**.

The other 14 verified correct against PDFs (incl. the swap pairs Bethany/Edith Johnson `2012 ND 31`↔`27` and Kitchen/Kleinsmith `2013 ND 18`↔`19`, and Keller `2000 ND 138` vs the later `2000 ND 141`). Orphan strays were bogus (no PDF / cited by no one): `2010 ND 54`, `2012 ND 196`, `2016 ND 332`. Tools: `triage/fix_neutral_cite_contamination_2026-05-24.py` + `triage/fix_neutral_cite_invert_2026-05-24.py`. Snapshot `opinions.db.bak-pre-neutral-cite-contamination-2026-05-24`. Invariants 22/2/0.

**Flagged, NOT fixed (separate pass):** (a) **19722 (Goetz)** — text is *2023 ND 53* (also at oid 20385) yet filed as `2023ND120.md` claiming `2023 ND 120`; a text-identity tangle. (b) **Residual provenance on 16924 & 17030** — `source_path`/`opinion_sources` primary still point at the displaced case's markdown (`2017ND116.md`/`2017ND241.md`), 16924 carries Cox's archive htm (`20160380`), 17030's docket (`20170241`) looks synthesized. Citations are now correct; the source-provenance untangle is deferred.

## Batch `fix-casename-contamination-2026-05-24c` (4 opinions, 6 field changes)

**Re-adjudication of the CONFIDENTIAL + REVIEW buckets** (`scan_casename_contamination`) after the published-opinions correction (`-24b`). 4 more genuine contaminations fixed from the authoritative frontmatter caption (`case_name_full` was already correct on all four; citations untouched): **12478** "Mundal v. Meyer Flaten" → "State, County of Cass ex rel. L.F.F. v. K.D.M." (docket `1997ND134` → `Civil No. 970030`); **15353** `"sather"` (junk fragment) → "Cruff v. H.K." (docket → `No. 20090149`); **5380** "State v. Pancoast" → "State v. Kent" (body: *State v. Myron R. Kent*); **17030** "WSI v. Questar Energy Services, Inc." → "Disciplinary Board of the Supreme Court of the State of North Dakota v. Lee". Tool: `triage/fix_casename_contamination_2026-05-24c.py`. Invariants 22/2/0.

**Left alone** (verified *same-case* caption variants — column is a legitimate "Estate of / Adoption of / Guardianship of / Matter of / Trust of" caption, docket matches): 13736 (D.D.I., Inc. — a *company*, not juvenile), 13943, 15147, 15501, 15563, 16991, 17392, 6012 (OCR variant that keeps the relator), 12544, 16484, 16536, 17158, 17381. **Column already correct** (the frontmatter *short* `title` was the contaminated field, not the column): 15600, 15869, 15931 — truly *State v. Johnson / Garg / Gagnon*. Those three **plus 17030** also carry a **stray second ND-neutral cite** — a separate cite-level contamination cluster flagged for a future cite-cleanup pass (not touched here).

## Batch `fix-casename-contamination-2026-05-24b` (1 opinion, 2 field changes)

**Follow-on to the batch below; corrects a misplaced caution.** oid 12451 was initially *held* out of the `-24` batch on a confidentiality worry (an `L.D.C.` child-support matter; the column anonymized the mother as "L.D.C.'s Mother"). That worry was wrong: **every opinion in this DB is a *published* opinion**, and this one's published caption already names the adult party — *In the Interest of L.D.C. Daniel P. RICHTER, Director of Ward County Social Service Board … v. Linda CLARK* (the court initializes only the child). So the published caption is public; the "(CONFIDENTIAL)" strings seen on some rows are editorial scrape/metadata labels, not seals. Unlike the `-24` rows this is the *same* case (not a different case crossed in), but its `docket_number` was the synthesized `1997ND104` and its `case_name` a non-standard hand-anonymized label. Fixed `case_name` "Ward County Social Service Board v. L.D.C.'s Mother" → **"Richter v. Clark"** and `docket_number` "1997ND104" → **"Civil 960291"** (`case_name_full` already correct). **Policy going forward: published captions are treated as public; anonymized-looking captions / (CONFIDENTIAL) labels are not a fix blocker.**

## Batch `fix-casename-contamination-2026-05-24` (13 opinions, 26 field changes)

**CL-metadata contamination (the Longtine/Herrick class), surfaced by `detect_overruled_in_draft`.** 13 opinions filed in 1997 carried a COMPLETELY DIFFERENT real case's `case_name` and a synthesized `1997NDnnn` `docket_number` (derived from the neutral cite, not a real docket), while their `case_name_full` and the in-body caption were correct. Example: oid 12500 — `case_name` "Longtine v. Yeado" / docket "1997ND155", but the text is unambiguously *State v. Herrick* ("Criminal 970019-970021"). Fixed `case_name` ← frontmatter `title` and `docket_number` ← frontmatter `docket_number` for all 13 (the authoritative caption, self-consistent with the body); `case_name_full` was already correct on every row, so only 13 names + 13 dockets changed. **Parallel citations were NOT touched** — they belong to the real case in the text (the contamination crossed name/docket only). oids: 12346, 12388, 12389, 12392, 12397, 12398, 12403, 12415, 12418, 12438, 12486, 12500, 12520. Tools: `triage/scan_casename_contamination_2026-05-24.py` (read-only bucketing scan) + `triage/fix_casename_contamination_2026-05-24.py` (guarded, `--apply`). Snapshot: `opinions.db.bak-pre-casename-contamination-2026-05-24`. Invariants 22 ok / 2 known / 0 regressed; FTS re-synced.

**Deliberately EXCLUDED from this batch (verified false positives or sensitive):** 12476 (column "…v. Schmidt" already correct; the frontmatter *short* `title` was the wrong field); 13804/15073/15796/15844 (modern estate/matter cases — 8-digit dockets MATCH, "Estate of X"/"Matter of Y" is a legitimate caption of the same case); 14223 (NDSU — same case, column caption is more complete); 12463 (Heustis/Heusis OCR variant, same attorney-reinstatement case). **12451 was initially held** on a confidentiality worry — **now resolved and fixed in `-24b` (above)**: these are published opinions, so it was not a real concern; corrected to "Richter v. Clark" / docket "Civil 960291". **Residual:** the scan only catches contamination where the wrong and right captions share no distinctive token; same-token crossings (e.g., two "State v. X" cases) would be missed.

## Batch `disposition-extract-2026-05-24` (new derived column, 7,353 rows)

**Derived metadata, not a correction.** Added a nullable `opinions.disposition` column (also added to `db.py` `create_schema` for fresh rebuilds) and populated it via `memo.extract_disposition`, which reads the modern all-caps disposition line (e.g. `REVERSED AND REMANDED.`) printed between the "Appeal from..." line and the authoring byline. 7,353 of 20,154 opinions received a disposition (456 distinct values; AFFIRMED 4,532 / REVERSED-family ~1,925 / DISMISSED variants / WRIT GRANTED-DENIED / etc.); opinions lacking that convention (mostly pre-modern) stay NULL. **Heuristic/derived — verify before relying on it; it is NOT authoritative text.** Backs the §12 `search_faceted` disposition facet and the later `detect_overruled_in_draft` work. Tool: `triage/extract_disposition_2026-05-24.py` (idempotent; `--revert` sets all back to NULL). Logged to `provenance` (not the `changelog` table, as it is a bulk derivation rather than a per-cell correction). Snapshot: `opinions.db.bak-pre-disposition-2026-05-24`. Invariants unchanged: 22 ok / 2 known / 0 regressed; FTS integrity verified post-update.

## Batch `fix-douglas-date-misread-2026-05-24` (1 date revert) + `section10-resequence-2026-05-24c` (12 cites)

**Self-correction.** The `fix-bound-discrepancies-2026-05-24` batch changed *Douglas v. Glazier* (oid 5774, 9 N.D. 615) date_filed 1900-12-08 → 1900-11-24 from a **150-dpi scan misread**. Re-reading the bound page at **300 dpi** shows "Opinion filed **December 8, 1900**" — the original 1900-12-08 was correct. Reverted (`fix-douglas-date-misread-2026-05-24`), then re-ran the resequencer (`section10-resequence-2026-05-24c`, 12 cites): Douglas returns to `1900 ND 107` (its Dec-8 slot), *Wilson* stays `1900 ND 85` (Nov 13, confirmed at 300 dpi + corroborated by the all-Nov-13 Emmons block). The other `fix-bound-discrepancies` changes are **confirmed correct** and untouched: Wilson 5747 → 1900-11-13, and Nelson 2169 → 173 N.W. 475 (independently confirmed by the `NW/173/{475,474}.md` source paths and a 300-dpi read showing Nelson at 173 N.W. 475 / Olson 474).

**Lesson:** read filing dates / cite digits from bound scans at **≥300 dpi** (or from the Westlaw `.doc` text, which carries a parseable date) — 150 dpi misreads single digits (this Douglas error, and a Cairncross "Oct 10"→"Oct 19" misread caught the same way). Invariants **22 ok / 2 known / 0 regressed**; `neutral_cite_uniqueness` 258.

## Batch `section10-resequence-2026-05-24b` (1 cluster reordered — vols 14 & 24)

Filed two newly-downloaded bound volumes — **N.D. vol 14** (746 pp.) and **N.D. vol 24** (785 pp.) — into `~/refs/nd/opin/N.D./{14,24}/_bound-volume.pdf` and verified their §10 clusters against the scans (offsets vol 14 +22; vol 24 +29 near p.327, drifting to +31 by p.393 — plates; always re-confirm via running header).

- **14 N.D. 557 — REORDERED.** Bound prints *Murphy v. District Court* (per-curiam, writ denied, top of p.557) then *State v. Poull* (the substantive opinion, p.557–565+). Provisional had Poull first (N.W. 717 < 734); N.D. order governs. Added `[152, 146]` to the resequencer's `KNOWN_ORDER` and re-ran → Murphy `1905 ND 89`, Poull `1905 ND 90` (2 cites swapped, batch suffix `b`).
- **24 N.D. 326 — correct as-is.** *Burger v. Sinclair* (lead; caption + syllabus on p.325, opinion text p.326) → *Seckerson v. Sinclair* (companion). Provisional Burger 112 / Seckerson 113 stands. (Citation-convention note: Burger's case opens on p.325 but is cited at 326 = opinion-text page; not treated as an error.)
- **24 N.D. 395 — correct as-is.** *McCarty v. Kepreta* (lead, 101k-char opinion, p.395–) → *McCarty v. Talley* (1.2k-char companion). Provisional Kepreta 10 / Talley 11 stands.

Invariants **22 ok / 2 known / 0 regressed**; `neutral_cite_uniqueness` 258; 12,604 cites. On-disk bound N.D. volumes now: **1, 2, 3, 7, 9, 14, 19, 20, 24, 34, 44**.

## Batch `section10-resequence-2026-05-24` (23 synthetic cites renumbered)

Resequenced the 1900 synthetic `YYYY ND nnn` cites after the `fix-bound-discrepancies` date corrections moved two opinions. Tool: **`triage/section10_resequence_2026-05-24.py`** — the new **canonical §10 ordering tool**: recomputes the whole pre-1997 sequence from current DB state (default sort `date_filed, ND-page, NW-page, oid`) + the verified on-page orders in `KNOWN_ORDER`, then applies only the cites that changed. Re-run it after any future pre-1997 data correction. It folds in (supersedes) the one-shot `fix_section10_cluster_order` / `fix_section10_ndverify` scripts.

Correcting *Emmons County v. Wilson* (5747) to 1900-11-13 moved it from `1900 ND 106` to `1900 ND 85` (joining the Nov-13 Emmons block, after Thistlewaite@614=84); correcting *Douglas v. Glazier* (5774) to 1900-11-24 moved it from `107` to `96`. The 21 opinions filed between those points shifted +1/+2; everything outside the 85–107 span (incl. `1900 ND 108` Boyd and all other years) is unchanged. **23 changelog rows** (`field='citation_synthetic_order'`). Invariants **22 ok / 2 known / 0 regressed**; `neutral_cite_uniqueness` 258; count still 12,604. Verified anchors unchanged: 3 N.D. 538 (Globe 6/Kellogg 7), Emmons 66–84, 44 N.D. 250 (Nelson 127/Olson 128).

## Batch `fix-bound-discrepancies-2026-05-24` (2 date_filed + 1 N.W. cite)

Applied the two data-quality flags surfaced during §10 bound-volume verification (authoritative source = the bound N.D. Reports scans). Tool: `triage/fix_bound_discrepancies_2026-05-24.py`.
- **9 N.D. 615 date_filed** (bound vol 9 p.615): *Emmons County v. Wilson* (5747) 1900-12-08 → **1900-11-13** (it is the Nov-13 Emmons block's tail, filed with the rest, not Dec 8); *Douglas v. Glazier* (5774) 1900-12-08 → **1900-11-24**. The DB had lumped both at 12-08.
- **44 N.D. 250 N.W. cite** (bound vol 44 p.250): *Nelson v. Middlewest Grain Co.* (2169) 173 N.W. 474 → **173 N.W. 475**. (2169 had been mis-set to 474 by `ingest-emmons-additions-2026-05-24`; the 472/473/474 run belongs to the page-247 companions, and the bound vol 44 p.250 prints Nelson at 475, Olson at 474.)

Snapshot `opinions.db.bak-pre-resequence-2026-05-24` (taken before both batches). 3 changelog rows. Invariants **22 ok / 2 known / 0 regressed**. The date changes trigger the `section10-resequence` batch above.

## Batch `fix-section10-cluster-order-ndverify-2026-05-24` (4 synthetic cites reordered)

Verified the on-page publication order for every §10 shared-page cluster that falls in an **on-disk bound N.D. Reports volume** (vols 9, 19, 20, 34, 44), reading each bound scan against the provisional oid-order. Offsets calibrated via running header: vol 9 +110, vol 19 +18, vol 20 **+22** (initial +34 was a low-res misread), vol 34 **+26**, vol 44 +17. Tool: `triage/fix_section10_ndverify_order_2026-05-24.py` (revertible).

**Correct as-is (no change):** 19 N.D. 57 (McCue v. Minneapolis "Soo" Ry → McCue v. Great Northern), 20 N.D. 370 (McAndress → Koch), 20 N.D. 372 (Andor → Fitzmaurice), 20 N.D. 412 (Winterer → Stoltze), 34 N.D. 601 (Tallmadge → Mercer County State Bank). The 20 N.D. 370/372 opinions are per-curiam contempt companions to the lead *State v. Hoffman* (this-day-decided).

**Reordered (2 clusters, 4 cites):**
- **9 N.D. 615** (vol 9 pdf 725): bound prints *Emmons County v. Wilson* (top) then *Douglas v. Glazier* — provisional had Douglas first (it sorted by N.W. 552 < 1119). Now Wilson `1900 ND 106` / Douglas `1900 ND 107`.
- **44 N.D. 250** (vol 44 pdf 267): bound prints *N. M. Nelson v. Middlewest Grain Co.* (top) then *Henry Olson v. Middlewest Grain Co.* — provisional had Olson first (DB lists both at 173 N.W. 474, so oid broke the tie). **N.D. Reports order governs** the ND synthetic cite (reporter-order guard). Now Nelson `1919 ND 127` / Olson `1919 ND 128`.

**Two data-quality flags surfaced while reading (NOT changed here — need separate review):**
- **9 N.D. 615 date_filed:** bound shows *Wilson* "Opinion filed November 13, 1900" and *Douglas* "Opinion filed November 24, 1900", but the DB dates **both** 1900-12-08. Wilson is actually the tail of the Nov-13 Emmons block (so its synthetic number should eventually sit with the 66–84 group, not 106). Correcting these filing dates would cascade into the synthetic sequence — deferred.
- **44 N.D. 250 N.W. cite:** bound shows *Nelson* at **173 N.W. 475** and *Olson* at 173 N.W. 474, but the DB has **both** at 173 N.W. 474 (2169 Nelson was set to 474 by `ingest-emmons-additions-2026-05-24` — likely an error for this page-250 Nelson; the 472/473/474 sequence applied to the page-247 companions). Recommend 2169 → 173 N.W. 475 after review.

15 → **4 changelog rows** (`field='citation_synthetic_order'`). Invariants **22 ok / 2 known / 0 regressed**; `neutral_cite_uniqueness` held 258. No new snapshot (covered by `opinions.db.bak-pre-section10-phase1a-2026-05-24` + changelog revert).

## Batch `fix-section10-cluster-order-2026-05-24` (15 synthetic cites reordered)

Replaced the **provisional oid-tiebreaker** within-cluster order with the **true N.D. on-page publication order** for the shared-page clusters whose order is authoritatively known. Tool: `triage/fix_section10_cluster_order_2026-05-24.py` (dry-run default; revertible — old cite string stored per changelog row).

- **3 N.D. 538** (vol 3 bound, prior session; N.D.=N.W.): **Globe Investment Co. v. Boyum → Kellogg, Johnson & Co. v. Gilman**. Was reversed (Kellogg `1894 ND 6`); now Globe `1894 ND 6` / Kellogg `1894 ND 7`.
- **9 N.D. 608–614 Emmons County tax-foreclosure block** (read this session from the bound vol 9 scan `~/refs/nd/opin/N.D./9/_bound-volume.pdf`, pp.608–614 = pdf pages 718–724, offset +110). Top-to-bottom on-page order transcribed: 608 Cranmer→Davidson; 609 Davidson→Baker→Couch; 610 Cranmer→Ganger→Kelly; 611 Lilly→McKenzie→McKenzie; 612 McKenzie→McLain→Mellon; 613 Mellon→Mellon→Robinson; 614 Thistlewaite→Thistlewaite. (Identical-caption duplicates — 2× McKenzie p.611, 2× Mellon p.613, 2× Thistlewaite p.614 — kept in oid order; they are indistinguishable.) 611 and 614 already matched; 13 cites reordered across pp.608–613.
- **44 N.D. 247** (Nelson→Lammadee) was already correct — not touched.

**Mechanism:** pure within-cluster permutation — each cluster keeps its exact set of `YYYY ND nnn` numbers, only the oid↔number mapping changes, so no other opinion's number shifts and per-year uniqueness holds. Numbers remain PROVISIONAL until the publish freeze. **15 changelog rows** (`field='citation_synthetic_order'`). Invariants **22 ok / 2 known / 0 regressed**; `neutral_cite_uniqueness` held 258. No new snapshot (covered by `opinions.db.bak-pre-section10-phase1a-2026-05-24` + changelog revert).

## Batch `section10-phase1a-synthetic-2026-05-24` (12,604 synthetic cites — §10 Phase 1A)

Back-assigned a synthetic medium-neutral citation `YYYY ND nnn` to **every pre-1997 opinion** (`date_filed < 1997-01-01`), extending the post-1997 neutral-cite format corpus-wide as a stable universal unique identifier (§10, ratified design 2026-05-19/24). Tool: `triage/section10_phase1a_2026-05-24.py` (`--measure`/`--apply`/`--revert`).

- **12,604 `citations` rows inserted**, `reporter='ND-neutral-synthetic'`, **`is_primary=0` always** — a synthetic/editorial ID, never the official cite, so the existing official `ND`/regional primary is unchanged (verified: oid 5274 still primary `3 N.D. 538`). 12,604 changelog rows (`field='citation_synthetic'`, authority=`section10-phase1a-order(date,ND-page,NW-page,oid)`).
- **Sequence per year** in sort order `(date_filed, ND-vol, ND-page, NW-vol, NW-page, oid)`; ND-cited sorts before NW2d-only on a same-date tie. 0 opinions had an unparseable primary cite (no date+oid-only placements needed).
- **Taxonomy/contract changes (code):** `ingest.SYNTHETIC_REPORTERS = {'ND-neutral-synthetic'}` added to `REPORTER_TAXONOMY` but kept OUT of `PRIMARY_LADDER` (so `recompute_primary` never selects it); `migrate_reporter_taxonomy.py` hardened to skip synthetic rows (its `_classify_reporter` would otherwise relabel a `YYYY ND nnn` string as native `ND-neutral` and strip provenance); SCHEMA.md Contract 1 enum extended + Contract 2 rung-1/Interim text corrected (earlier draft wrongly had the synthetic becoming primary).
- **4 new invariants** (all green at 0): `synthetic_format` (matches `^\d{4} ND \d+$`), `synthetic_uniqueness_per_year` (each `YYYY ND nnn` → one opinion), `synthetic_only_pre_1997`, `synthetic_never_primary`. Dashboard **22 ok / 2 known / 0 regressed**. `neutral_cite_uniqueness` held at **258 (Δ=+0)** — the synthetic strings (years ≤1996) introduced zero collisions and don't overlap native cites (years ≥1997).
- **PROVISIONAL within-cluster order.** The 101 opinions in 48 genuine shared-page collision clusters (42 NW-orderable + 31 truly-tied + 28 NW2d-era member rows) were tie-broken by `oid` as a placeholder — numbers are PROVISIONAL until a publish freeze (renumber freely; ratified stability policy). Worklist: `triage/section10-cluster-worklist-2026-05-24.tsv`. **Next:** apply the on-page orders already verified last session (e.g. 3 N.D. 538 should be Globe→Kellogg, currently assigned Kellogg `1894 ND 6`/Globe `1894 ND 7`; 44 N.D. 247 Nelson→Lammadee; the 9 N.D. 608–615 Emmons block), then resolve the remaining clusters via bound-image reads.

Snapshot `opinions.db.bak-pre-section10-phase1a-2026-05-24`. Revert: `python triage/section10_phase1a_2026-05-24.py --revert`.

## Batch `section6-rex-twins-2026-05-24` (18 merges)

The §10 shared-page analysis surfaced 18 `X v. Y` + `Re X`/`In the Matter of …` twin pairs, each sharing the same N.D. page, N.W. page, AND docket number — one Westlaw-bound row captioned by the parties, one CL re-ingest captioned by the estate/matter. **Text-read 2026-05-24 confirmed all 18 are one opinion double-ingested** (the `Re X` full caption names the same parties + same docket as the `X v. Y` row — e.g. `Re Schenum` = "Estate of James Schenum, **D.C. Cullen v. Ida Sullivan**"; `In re Hanson` = "Application of Hanson… **Northern Pacific Ry v. McDonald**"). These are NOT like the Emmons per curiams (different defendants / separate suits) — same case. Tool: `triage/merge_rex_twins_2026-05-24.py`.

Kept the Westlaw-bound `X v. Y` row, dropped the CL twin (via `merge_pair`): 2994 Cullen/Sullivan, 3269 Bd. Medical Examiners/Shortridge, 3588 Campbell, 3685 Brilz, 4110 Garrity, 4205 McHugh, 4271 Rusch, 4286 Stricker, 4448 Teiten, 4894 State v. Jackson (re White), 5030 Knauss, 5038 Perry, 7177 NP Ry/McDonald (re Hanson), 7520 Eberlein (re Bratcher), 7646 Nelson v. Chadwick (re Glavkee), 8814 Hvidsten, 9805 Peschel, 9816 Lamb. `align_primary_source --apply` (18 flips). Corpus **20,172 → 20,154**. Snapshot `opinions.db.bak-pre-rex-twins-2026-05-24`. Invariants **18 ok / 2 known / 0 regressed**.

## Batch `ingest-emmons-additions-2026-05-24` (3 new opinions; 1 case_name; 3 cite fixes)

Reading the bound N.D. Reports vol. 9 scan (for §10 on-page ordering) revealed the Emmons County tax-foreclosure block (9 N.D. 608–615) carries **20** per-curiam memoranda but our DB/`.doc`s had only 17 — the N.W.-reporter cite-based Westlaw pulls returned one opinion per surname per page, missing the 2nd McKenzie (611), 2nd Mellon (613), and 2nd Thistlewaite (614). User confirmed these are separate per curiams (distinct per-parcel suits, identical disposition text). Tool: `triage/ingest_emmons_additions_2026-05-24.py`.

- **3 new opinions** (oids 20500 McKenzie@611, 20501 Mellon@613, 20502 Thistlewaite@614): per_curiam, 1900-11-13, ND-primary `9 N.D. <p>` + `84 N.W. 1118`, text transcribed from the bound volume. **Source convention (new):** `source_reporter='ND-image'`, `source_path='N.D./9/_bound-volume.pdf'` (the filed bound-volume scan). Each carries a `notes` **DO-NOT-MERGE** flag — they share caption + cites + identical text with their siblings (only the separate suit/parcel distinguishes them), so a future jaccard dedup must not collapse them. Corpus 20,169 → **20,172**.
- **McLain spelling** (oid 20496): `Emmons County v. McLean` → `…v. McLain` (bound volume: "Calvin B. McLain").
- **Middlewest Grain N.W. parallel cites** (read from bound vol. 44): 2171 Nelson → `173 N.W. 472`, 20499 Lammadee → `173 N.W. 473`, 2169 Nelson → `173 N.W. 474` (DB had lumped all three at 475; the N.W. reporter ordered the companions non-monotonically vs the N.D. Reports).

**On-page order resolved** (for §10) from vols 3/9/44: 3 N.D. 538 Globe→Kellogg (N.D.=N.W.); 44 N.D. 247 Nelson→Lammadee (no gap — full block present 246–250); 9 N.D. 608–615 Emmons full order recorded. **Bound-volume scans filed** at `~/refs/nd/opin/N.D./<vol>/_bound-volume.pdf` (vols 3, 9, 44) — co-located with each volume's per-opinion `.doc`s for findability. *(Open: Benness oid 2172 dated 1919-06-21 in DB but "June 27, 1919" in the bound volume — low-priority date check.)* DB snapshot `opinions.db.bak-pre-emmons-additions-2026-05-24`. Invariants **18 ok / 2 known / 0 regressed**.

## Batch `fix-61nd179-dup-2026-05-24` (1 merge)

§10 shared-page image triage surfaced a duplicate at 61 N.D. 179 / 237 N.W. 709. Read the Westlaw N.W. Reporter page image (`~/refs/nd/opin/NW/237/709.pdf`): there is only ONE *First State Bank of Granville v. Bond* opinion there (No. 5959, Burke J., a one-paragraph companion to the lead *First State Bank of Granville v. Cox* at 237 N.W. 708). Our DB carried it twice — oid 4184 (`First State Bank of Granville v. Bond`, Westlaw bound source) and oid 4185 (`First State Bank v. Bond`, CL NW-only). Same docket (`File No. 5959`), same date, same cites; the 0.40 text jaccard was just OCR noise on a short memo.

Merged 4185 → **4184** (keep the Westlaw-bound row + fuller caption) via `merge_pair`; `align_primary_source --apply` (1 flip). Corpus **20,170 → 20,169**. Snapshot `opinions.db.bak-pre-61nd179-dup-2026-05-24`. Invariants **18 ok / 2 known / 0 regressed**.

## Batch `fix-casenames-latin-caps-followup-2026-05-24` (23 case_names)

Resolved the held edge cases from the Latin-caps normalization, per user decisions. Tool: `triage/normalize_latin_caps_followup_2026-05-24.py`.
- **15 parenthetical `(In re ...)` deletions** — for the modern consolidated captions, removed the redundant trailing `(In re Interest of X)` parenthetical rather than re-casing it (`Peterson v. S.B. (In re Interest of S.B.)` → `Peterson v. S.B.`). Only parentheticals containing `In re` were removed; legitimate parentheticals untouched.
- **8 `et. al` → `et al`** (stray-period fix).
- `Habeas Corpus` (2): user chose to keep (proper writ name) — no change.

Residual scan: 0 `(In re ...)` parens, 0 `et. al`. Two pre-existing defects deliberately left for a separate pass (not Latin-caps): oid 17289 leading `.` (`.J.K.`) and 17555 capital `V.` (`… V. Bolinske`). DB snapshot `opinions.db.bak-pre-latin-followup-2026-05-24`. Invariants **18 ok / 2 known / 0 regressed**.

## Batch `fix-casenames-latin-caps-2026-05-24` (513 case_names)

Normalized relational Latin-phrase capitalization across all 20,170 case titles (user-directed): these phrases carry no internal capital — the only capital allowed is the very first letter of the whole title. Tool: `triage/normalize_latin_caps_2026-05-24.py`.
- **ex rel (258):** `Ex Rel`/`EX REL`/`ex. rel` → `ex rel` (mid-title) — always an error, never deliberate styling; includes the stray-`ex.`-period fix.
- **in re at title-start (257):** `In Re`/`In RE` → `In re` (capital I as first letter, lowercase `re`).
- ex parte (4): all already correct (`Ex parte` at start) — no-op.

**Held (not touched):** 15 modern (2018+) parenthetical court captions where `In re` begins a nested caption — `Peterson v. S.B. (In re Interest of S.B.)`. These are the Court's deliberate styling of consolidated juvenile/disciplinary appeals, so left for a separate decision rather than blindly lowercased. Residual case-sensitive scan: 0 wrong `ex rel`, exactly those 15 `In re` parentheticals remain. DB snapshot `opinions.db.bak-pre-latin-caps-2026-05-24`. Invariants **18 ok / 2 known / 0 regressed**.

## State-only: 104 EQUIV → keep_db (2026-05-24)

TUI-queue hygiene (no DB change): the 104 EQUIV rows from the Phase-2 adjudication (DB and Westlaw captions party-identical after normalizing punctuation/abbreviation/apostrophe/ligature) marked `kept_db` in `triage/casenames-state.json` (verdict `KEEP_DB_EQUIV`) so they no longer surface in the per-volume TUI. Includes 25 `County of X` rows where the user chose 2026-05-24 to **keep** the DB form rather than adopt West's `X County` (the West-form preference is situational, not a blanket rule). Tool: `triage/keep_equiv_2026-05-24.py`. No case_name changed; reversible via git.

## Batch `fix-casenames-other-mined-2026-05-24` (28 renames)

Mined the clean capacity/jurisdiction adds out of the 178 OTHER residue (`triage/mine_other_2026-05-24.py` → `triage/other-mined-2026-05-24.tsv`). The OTHER rows are all ADDITION-kind (Westlaw only adds tokens), so this buckets *what* is added; curly-apostrophe folding + a `<County> County Court/Com'rs` jurisdiction pattern were needed to catch the real shapes.

Applied 28 (27 capacity + 1 jurisdiction), all consistent with the ratified ROLE_APPOSITIVE policy: official-capacity appositives (`Birdzell, Tax Commission`; `Olsness, State Ins. Com'r`; `Wallace`/`Thoresen, State Tax Com'r` across companion cases; `Lamb, State Highway Com'r`) and one jurisdiction (`Squire v. County Court` → `v. Ward County Court`). Note oid 2612 `State v. McCray` → `State ex rel. Herigstad, State's Atty., v. McCray` adds a named relator (purely additive from the bound caption; user-approved).

Remaining 150 OTHER + 32 MULTICASE_MISSED not cleanly mineable → TUI. DB snapshot `opinions.db.bak-pre-other-mined-2026-05-24`. Invariants **18 ok / 2 known / 0 regressed**.

## Batch `fix-casenames-addition-2026-05-24` (12 renames; 26 keep_db)

Sub-classified the 248 ADDITION rows (Westlaw adds detail the DB lacks) from the Phase-2 adjudication into the established ADDS_DETAIL buckets (`triage/subclassify_addition_2026-05-24.py` → `triage/addition-subclassified-2026-05-24.tsv`); applied the clean 38 (`triage/apply_addition_2026-05-24.py`):
- **12 renames** — LOCALITY_OF (9) + ROLE_APPOSITIVE (3), the buckets ratified 2026-05-20: capacity adds (`Olsness, State Com'r of Insurance`; `Payne, Director General`; `Harding, Board of Railroad Com'rs`) and locality/entity expansions (`First State Bank of Ray`; `Farmers' & Merchants' Bank of Sheyenne`; `Union Central Life Ins. Co. of Cincinnati, Ohio`).
- **26 keep_db** (verdict `KEEP_DB_ADDITION_NOISE`) — DOCKET_METADATA (17) + LONG_PLEADING (9): Westlaw adds only dates/pipes/docket nos. (`…Oct. 20. 1920. |`, `(two cases). Nos. 7279, 7280`) or a full complaint party-recitation; the DB short caption is the correct case name.

Deferred to TUI / further mining: 178 OTHER (mixed capacity/jurisdiction adds + ambiguity) and 32 MULTICASE_MISSED (`In re X's Estate.` reframes — judgment calls). DB snapshot `opinions.db.bak-pre-addition-2026-05-24`. Invariants **18 ok / 2 known / 0 regressed**.

## Batch `fix-casenames-adjudicate-2026-05-24` (18 renames; 12 keep_db)

Phase 2: a `.doc`-body-grounded adjudicator for the substantive residue (spelling-direction and party-identity calls string rules can't decide). For each row it reads the Westlaw `.doc` **body** — the clean, professionally-edited, non-OCR source — and counts how each candidate surname is actually spelled there; the `.doc` body is the authority, with CL `text_content` as corroboration. Tool: `triage/adjudicate_residue_2026-05-24.py`; full per-row evidence in `triage/residue-adjudication-2026-05-24.tsv`.

Guards (all added after auditing the HIGH bucket caught real errors): pairing jaccard ≥ 0.45 (low → possible shared-page sibling → defer); ligature fold (`æ↔ae`, so `Aetna`≠`Ætna`-rename); curly-apostrophe + docket-number token stripping; **single-substitution gate** (only one DB surname may change — multi-token restructures defer, which correctly caught a bad `Minot Special School District Number One`→`…Dist` truncation and a multi-matter caption). Confidence: `.doc` body majority ≥2 and ≥2× the loser, CL not contradicting → HIGH; only HIGH auto-applies.

Applied 30 HIGH (audited clean):
- **18 renames** — body-proven OCR/typo/misattribution fixes. Examples: oid 1522 `Fango`→`Fargo` (body Fargo 9×/Fango 0×); 289 `ex rel. Madderson`→`Frish` (Frish 4×/0×); 1847 `Larger`→`Langer, Atty. Gen.`; 4734 `Jordan`→`Jordon`; spacing `La Moure`/`La Flame`/`La Bree`; `Inter-State`, `Investors'`; abbreviation expansions (`Elev.`→`Elevator`, `P.`→`Power`, `Mach.`→`Machine`); 7401 `State`→`North Dakota Workmen's Compensation Bureau`.
- **12 keep_db** (verdict `KEEP_DB_BODY_SPELLING`) — body confirms the DB spelling; no rename.

Deferred (not auto-applied): 248 ADDITION (separate accept-detail sub-classification), 104 EQUIV (normalize-equivalent keeps), ~20 MED spelling/swap (human-audit pile), ~50 multi-token/complex/low-pairing (TUI). DB snapshot `opinions.db.bak-pre-adjudicate-2026-05-24`. Invariants **18 ok / 2 known / 0 regressed**.

## Batch `fix-casenames-residue-patterns-2026-05-24` (17 renames; 5 keep_db)

Phase 1 of automating the 505-item pending case-name residue: three high-precision patterns mined from the user's TUI decisions, each applied only under a strict gate where `norm(DB)` is a clean subset of `norm(Westlaw)` — i.e. Westlaw only *adds* material and never changes a party surname. Surname spelling-direction calls were deliberately routed to the Phase-2 `.doc`-body adjudicator instead. Tool: `triage/sweep_residue_patterns_2026-05-24.py`.

- **ANNOT_KEEP (5, no rename → `kept_db`):** Westlaw = DB + a reporter annotation only (`(two/three cases)`), so the DB caption is already correct. Marked `kept_db` (verdict `KEEP_DB_ANNOTATION`): oids 1195, 1244, 1359, 1927, 4487.
- **CAPACITY (8 renames):** Westlaw adds a party's official-capacity appositive; docket tails (`Cr. 176`, `Nos. 4967-4971`) stripped. E.g. 993 `…v. Mitchell` → `…v. Mitchell, Treas.`; 3965 `…v. Peterson` → `…, Building Inspector`; 5038/5030/5043/6057 `…, Sheriff`/`, Warden`.
- **SUFFIX (9 renames):** Westlaw adds a corporate suffix — `Co., Limited` (Harvey Mercantile, oids 996/1870/2394) and `Co., Inc.` (Advance-Rumely Thresher, oids 4218/4252/4224/4233/4268; Dennstedt Land 1947).

Excluded: `In re …'s Estate.` multi-matter prefixes (e.g. oid 9819) deferred to Phase 2/TUI. DB snapshot `opinions.db.bak-pre-residue-patterns-2026-05-24`. Invariants **18 ok / 2 known / 0 regressed**. (Revert renames via `cleanup revert`; the 5 `kept_db` additions are removable from `triage/casenames-state.json`.)

## Batch `fix-casenames-jurisdiction-2026-05-24` (25 case_names; 6 keep_db reversals)

Policy decision (user-ratified 2026-05-24): for governmental respondents where the Westlaw caption adds a geographic jurisdiction the DB omits — courts (`v. District Court of/for/in and for <County> County`) and bodies (`Board of Com'rs of Dunn County`, `Board of Education of City of Fargo`, `Park District of City of Enderlin`) — the **full West caption is authoritative**. The bare DB form (`v. District Court`) is a truncation that fails to identify which court/body is the party. Reporter annotations (`(N cases)`, `Cr./Civ. NNN`, judicial-district tails) are stripped as non-name material.

Surfaced by a dry-run of the proposed "county-jurisdiction sweep" (`triage/sweep_jurisdiction_2026-05-24.py`). The dry-run revealed the `fix-casenames-vol16-79-detail-2026-05-20` batch had already *applied* ~30 such adds via its ROLE_APPOSITIVE/LOCALITY_OF buckets, while the user's TUI had *rejected* the identical shape on a handful of rows — an internal inconsistency. Resolving toward the West caption (rather than stripping) is corroborated by the user's own contemporaneous TUI edits doing the same by hand (oid 952 `Paulson v. County` → `v. Ward County`; oid 404 adding `ex rel. … Mayor`).

Dispositions:
- **REVERSE_KEPT (6):** reversed prior TUI `keep_db` and applied the West caption (oids 277 *Vallelly v. Board of Park Com'rs of Park District of City of Grand Forks*, 353/354 *Zinn v. District Court in and for Morton County* / *for Barnes County*, 377 *Ladd*, 726 *Baker v. City Council of City of La Moure*, 951 *Pederson v. Board of Com'rs of Billings County*). Removed from `triage/casenames-state.json` `kept_db`.
- **APPLY_PENDING (16):** applied the West caption to still-pending ambiguous-queue rows (district courts + boards of education/commissioners).
- **STRIP_APPLIED (3):** stripped reporter annotations from already-applied rows — oid 11543 `(five cases)`, 1080 `in Tenth Judicial Dist.`, 10065 `, Fifth Judicial Dist.`

**Excluded** (correctly applied earlier, left untouched): Group 3 person + official-capacity appositives (`Scofield, Sheriff of Ward County`); Group 4 entity proper names (`Farmers' Bank of Mercer County`). **Relator-loss guard:** oids 2063 (`Rhea ex rel. Rhea`) and 2527 (`Hufford ex rel. Property Holders & Taxpayers`) excluded — the West caption drops a substantive `ex rel.` relator; their `KEEP_DB_HAS_REL` stands. **Deferred to TUI (3):** genuine multi-case/garbage captions — 4716 (`… BUTTZ v. ROBINSON`), 10068 (`Petition of Village Board of Wheatland …`), 11544 (paragraph-form caption).

DB snapshot `opinions.db.bak-pre-jurisdiction-2026-05-24`. Invariants **18 ok / 2 known / 0 regressed**.

## Batch `fix-casenames-vol16-79-orphans-2026-05-20` (7 opinion_sources rows)

Investigation of the 7 ORPHAN_SIBLING entries from the same-day adjudication: NOT corpus gaps. Every one of the .docs corresponds to an opinion already in the DB under a different OID (the cite-shared sibling of the cite-matched row the mispaired-TSV listed). Jaccard `.doc` body vs. the correct OID's `text_content` is 0.85–0.92 for all 7.

The .docs were simply never registered in `opinion_sources` for their correct paired opinion — same micro-fix pattern as `fix-cairncross-source-2026-05-19` (vol 11–15 batch). All 7 correct opinions already carry an `NW` primary source (CL text); the Westlaw `.doc` is added as non-primary (`is_primary=0`), promotion deferred to a future `merge_westlaw_text` pass.

| .doc | correct oid | DB case_name |
|---|---:|---|
| `N.D./20/0372-Fitzmaurice-v-Willis.doc` | 680 | Fitzmaurice v. Willis |
| `N.D./20/0412-Stoltze-v-Hurd.doc` | 692 | Stoltze v. Hurd |
| `N.D./21/0348-Heard-v-Holbrook.doc` | 767 | Heard v. Holbrook |
| `N.D./23/0352-Bismarck-Water-Supply-Co-v-City-of-Bismarck.doc` | 937 | Bismarck Water Supply Co. v. City of Bismarck |
| `N.D./24/0395-McCarty-v-Kepreta.doc` | 1007 | McCarty v. Kepreta |
| `N.D./32/0373-Sundahl-v-First-State-Bank-of-Edmunds.doc` | 1487 | Sundahl v. First State Bank |
| `N.D./34/0601-Mercer-County-State-Bank-of-Manhaven-v-Hayes.doc` | 1641 | Mercer County State Bank v. Hayes |

Note: 3 of these .docs carry richer bound captions than the DB row — applied as `fix-casenames-vol16-79-orphan-enrich-2026-05-20` (see below).

## Batch `fix-foster-county-implement-372-2026-05-20` (2 fields, 1 opinion)

Reversal of a TUI keep_db decision for oid 372 after pulling the bound `.doc` for verification. User initially kept `Foster Implement Co. v. Smith` (DB) over Westlaw's `FOSTER COUNTY IMPLEMENT CO.` during the vol-17 TUI run, on the conservative judgment that "Foster County" vs "Foster" might be the substantive party-identity dispute. Bound `.doc` (`N.D./17/0178-Foster-County-Implement-Co-v-Smith.doc`) settles it:

> **Caption:** `FOSTER COUNTY IMPLEMENT CO. v. SMITH.`
> **Synopsis:** "Action by the **Foster County Implement Company** against E. Delafield Smith."
> **Opinion (Fisk, J.):** "This is an appeal from a judgment of the district court of Foster county in plaintiff's favor."

The plaintiff is *Foster County Implement Company* — a corporation operating in Foster County. CL dropped "County" from the corporate name during ingest; bound's form is authoritative. Same category as the accepted `Anderson` → `Anderson & Jorgenson` (oid 287) and `Wirtz` → `Wirtz Bros.` (oid 391): bound supplies missing party identity.

Applied:
- `case_name`: `Foster Implement Co. v. Smith` → `Foster County Implement Co. v. Smith`
- `case_name_full`: `Foster Implement Company v. E. Delafield Smith` → `Foster County Implement Company v. E. Delafield Smith`
- Removed oid 372 entry from `triage/casenames-state.json` `kept_db`

Invariants **18 ok / 2 known / 0 regressed**.

## Batch `fix-casenames-vol16-79-detail-2026-05-20` (702 case_names)

Pattern-based bulk apply of the high-confidence sub-buckets within the 927-row `ACCEPT_WL_ADDS_DETAIL` group from the earlier autorev classification. User reviewed a stratified 48-row sample (`triage/casenames-adds-detail-sample50-2026-05-20.tsv`) and selected per-pattern policies; this batch applies them.

**Sub-classification** (`triage/subclassify_adds_detail_2026-05-20.py`) split the 927 into:

| sub-pattern | total | policy | applied |
|---|---:|---|---:|
| LOCALITY_OF | 402 | Accept all | 402 |
| ROLE_APPOSITIVE | 175 | Accept all | 175 |
| PAREN_PARTY | 130 | Accept all | 130 (+ 5 skipped as already-equal) |
| MULTICASE_MISSED | 45 | Defer to TUI | 0 |
| LONG_PLEADING | 9 | Defer to TUI | 0 |
| DOCKET_METADATA | 17 | Defer to TUI | 0 |
| STATE_EXPANSION | 1 | Defer to TUI | 0 |
| OTHER | 148 | Defer to TUI | 0 |

**LOCALITY_OF (402)** — bank-of-locality is the dominant pattern (`First Nat. Bank` → `First Nat. Bank of Hannaford`); ND case law has many same-named banks distinguished by city, so the bound version is more precise. Also captures school district + county additions (`School Dist. No. 50` → `School Dist. No. 50 of Barnes County`).

**ROLE_APPOSITIVE (175)** — bound's role-of-defendant appositive (Atty. Gen., Sheriff, State Auditor, County Treasurer, District Judge). Common with `State ex rel.` cases where the relator's role is specified.

**PAREN_PARTY (130)** — parenthetical party additions (Intervener, Garnishee, Intervenor) that bound caption preserves but CL stripped.

**Tooling additions** in `triage/apply_adds_detail_2026-05-20.py`:
- `clean_residue()` strips trailing `Cr.`/`Civ.` docket markers, `Nos. NNN, NNN` numbering, trailing pipes/commas, and a `Supreme Court of North Dakota,` prefix that the .doc parser occasionally captures from the court header line into the caption (oid 398 sample).
- `smart_titlecase()` extends to handle apostrophe-followed-by-uppercase abbreviations: `'S→'s`, `'Rs→'rs`, `'R→'r`, `'N→'n`, `'D→'d`, `'T→'t` (covers Ass'N, Com'rs, Don'T, etc.).
- Post-pass replaces `ex rel. Name. Atty. Gen.` → `ex rel. Name, Atty. Gen.` (period→comma between the relator name and the role appositive — Westlaw's bound caption uses comma, .doc parser sometimes emits period).

**Deferred to TUI (220 total)**: 148 OTHER (mixed residue patterns) + 45 MULTICASE_MISSED (In re X's Estate / consolidated case reframings) + 17 DOCKET_METADATA (`(two cases). Nos. X, Y`) + 9 LONG_PLEADING (full pleading captions) + 1 STATE_EXPANSION. Plus the 372 main-classification DEFER_AMBIG + 12 DEFER_MULTICASE + 1 DEFER_WL_GARBAGE = **605 entries remain for `python -m ndcourts_mcp.review_casenames --volumes 16-79`**.

Combined two-batch totals on the 2,054-item ambiguous-review queue: 749 case_name UPDATEs (47 autorev + 702 detail) + 694 state.json keep_db = **1,443 of 2,054 closed (70%)**.

Invariants **18 ok / 2 known / 0 regressed**.

## Batch `fix-casenames-vol16-79-autorev-2026-05-20` (47 case_names + 694 state.json keep_db)

Auto-classification + bulk closeout of the 2,054-item ambiguous case-name diff queue for vols 16–79 (the `review_casenames` TUI's deferred work since 2026-05-13). This is the queue separate from this morning's 107 mispaired entries — these are diffs where the `.doc` is *correctly* paired with the cite-matched row, but its caption differs from the DB's case_name in some non-equivalent way (abbreviation, party detail, OCR, etc.).

Pipeline:
1. `triage/extract_ambig_review_2026-05-20.py` re-runs `review_casenames.extract_diffs` across vols 16–79 and dumps 2,054 non-equivalent, non-mispaired diffs to `triage/casenames-ambig-review-2026-05-20.tsv`.
2. `triage/classify_ambig_review_2026-05-20.py` buckets each row using token-set + ordered-abbreviation alignment + targeted regex detection (locality, role, parenthetical, OCR-1, encoding, multicase, garbage).
3. `triage/apply_ambig_review_2026-05-20.py` applies the high-confidence buckets.

**Verdict breakdown (2,054):**

| verdict | count | action |
|---|---:|---|
| KEEP_DB_PURE_ABBREV | 609 | state.json keep_db (no DB change) |
| KEEP_DB_HAS_REL | 86 | state.json keep_db (no DB change) |
| ACCEPT_WL_OCR_FIX | 43 | UPDATE case_name |
| ACCEPT_WL_ENCODING_FIX | 4 | UPDATE case_name |
| ACCEPT_WL_ADDS_DETAIL | 927 | **deferred to TUI** (~25% false-positive rate: long pleading captions, "In re Estate" reframing, missed multicase) |
| DEFER_AMBIG | 372 | deferred to TUI |
| DEFER_MULTICASE | 12 | deferred to TUI |
| DEFER_WL_GARBAGE | 1 | deferred to TUI |

**47 case_name UPDATEs applied** (43 OCR + 4 encoding):

OCR fixes (DB had a 1-edit garble in a single surname token; bound Westlaw is authoritative): `Byxne→Byrne` (×7 — Burchard, Reichert, Manning, Thompson, Gunderson, Preckel, Reichert), `McIntyxe→McIntyre` (×2 Bowman County), `Statea→State` (oid 3031), `Elevatop→Elevator` (oid 3024), `Standaed→Standard` (oid 823), `OTTEM→Otten` (oid 10361), `Ranson→Ransom` (oid 2832), `Danger→Langer` (oid 2600), `Hazlet→Hazlett`, `Hilleboe→Hilliboe`, `Thompkins→Tompkins`, `Erldelt→Erdelt`, `Ankenbaurer→Ankenbauer`, etc. Plus surname-variant judgment calls where the bound printed one spelling (`Larson→Larsen`, `Chamberlain→Chamberlin`, `McMillan→McMillen`, `Nielson→Nielsen`).

Encoding fixes: 4 entries with `&198tna` (HTML-entity garbage for `Æ`) → `Ætna`. The `&198` is hex `0xC6` = Æ — clear ingest-time encoding bug.

**694 KEEP_DB state.json entries** (the TUI now skips these on next interactive run): pure-abbreviation diffs like `Manufacturing Co.→Mfg. Co.`, `Northern Pacific Railway Co.→Northern Pac. Ry. Co.`, `Minneapolis, St. Paul, & Sault Ste. Marie Railway Co.→Minneapolis, St. P. & S. S. M. Ry. Co.`, `Township→Tp.`, `Workmen's→Workmen's` (curly vs straight). DB retains the more readable expanded form (matches vol 1–5 user preference: 90% keep-DB rate on this class of diff).

**1,312 entries remain for TUI review** — primarily the ACCEPT_WL_ADDS_DETAIL bucket. Classifier surfaced these as candidates for accepting Westlaw's added party detail (locality, role, parenthetical), but ~25% are edge cases that need human judgment: oid 3149 *Wishek v. Hildenbrand* (66-word pleading caption); oid 4046 *Backman v. Larson* → "Larson's Estate" (framing change, not detail-add); oid 3818 *Klingensmith v. Siegal* + "Heffner v. Same" (missed multicase). The TUI run will close these out with human review.

Invariants **18 ok / 2 known / 0 regressed**.

Tool notes:
- `review_casenames._smart_titlecase` has bugs surfaced here too: `'S` possessive → `'S` (not `'s`); `'Rs` abbreviation → `'Rs` (should be `'rs`); mixed-case `McKEE'S` not detected. The apply script uses a corrected `smart_titlecase` that handles these (Mc/Mac mixed-case + all-caps, `'S`/`'Rs`/`'R` casing).
- `extract_diffs` is slow (~3 minutes for vols 16–79) — re-parses every .doc on every run. Cache candidate if we expect to re-run.

## Batch `fix-casenames-vol16-79-deferred-2026-05-20` (2)

Closeout of the 2 case_name corrections deferred from this morning's vol-16-79 SAME bucket. Both bound `.doc` bodies pulled and verified; corrections applied:

| oid | bound (corrected) | was |
|---:|---|---|
| 1354 | Minneapolis, St. P. & S. S. M. R. Co. v. State Board of Ry. Com'rs | In re Appeal of Minneapolis, St. Paul, & Sault Ste. Marie Railroad |
| 4622 | Casselton Reporter v. The Fargo Forum. State ex rel. Casselton Reporter v. Doherty, County Auditor | Casselton Reporter Ex Rel. Potter v. Alleged Newspaper Called "The Fargo Forum" |

**oid 1354**: the bound N.W. Reporter caption (`MINNEAPOLIS, ST. P. & S. S. M. R. CO. v. STATE BOARD OF RY. COM'RS.`) uses the standard `v.` adversary form; CL's `In re Appeal of...` was the docket-style framing of the same case. Synopsis section confirms: "appeal of the Minneapolis, St. Paul & Sault Ste. Marie Railroad Company … from an order of the State Board of Railway Commissioners". Adopted bound form; possessive `Com'rs` (lowercase `r`) is the bound spelling — separately, `smart_titlecase` in `triage/adjudicate_mispaired_2026-05-20.py` has a bug rendering it as `Com'Rs` (regex only handles `'S`-possessive, not `'Rs`-abbreviation). Logged as tool refinement.

**oid 4622**: the `.doc` caption was *not* truncated — the `_parse_westlaw_doc` parser only caught the first 4 lines (`CASSELTON REPORTER et al. v. THE FARGO FORUM et al. STATE ex rel. CASSELTON REPORTER et al. v.`), missing the second case's defendant (`DOHERTY, County Auditor, et al.`). Reading the full `.doc` body resolved this: two consolidated cases (election contest + mandamus to compel issuance of certificate of election), per Morris, J. Adopted bound multi-case form matching this morning's *Burleigh County / Same / International Harvester* precedent. `The Fargo Forum` keeps capitalized `The` because the newspaper's name (and whether `The Fargo Forum` was a valid candidate distinct from `The Fargo Forum and Daily Republican`) is the substantive dispute. Tool refinement logged: `_parse_westlaw_doc` should follow through to subsequent `v.` markers for consolidated captions.

Invariants **18 ok / 2 known / 0 regressed**. Revertible.

## Batch `fix-casenames-vol16-79-ambig-2026-05-20` (2 source rows + 2 new opinions)

Closeout of the 6 AMBIG entries from this morning's vol-16-79 mispaired adjudication. Investigation (`triage/investigate_ambig_2026-05-20.py`) decomposed them into three buckets:

**Bucket 1 — Already-paired-by-name (2):** the `.doc` corresponds to an opinion that exists in the DB under the same name (the cite-shared sibling of the cite-matched row), just without the Westlaw `.doc` registered. Added as non-primary `westlaw` `opinion_sources` rows (same pattern as today's earlier orphan closeout):
- `0059-Kerr-v-Herred.doc` → oid 278 *Kerr v. Herred* (1907-02-23) — exact name match
- `0059-Kerr-v-Swanson.doc` → oid 276 *Kerr v. Swanson* (1907-02-20) — exact name match

Low AMBIG jaccards (0.27–0.31) are an artifact of these being very short per-curiam memos ("Following Kerr v. Anderson…"), not actual divergence.

**Bucket 2 — Classifier already-paired (2):** the `.doc` IS already correctly attached as the primary westlaw source for a different OID; the mispaired flag was a cite-only matching artifact (the cite-matched row was a sibling on the same shared page). No DB change:
- `0458-Bussey-v-Boynton.doc` → already primary source of oid 1189 *Bussey v. Boynton* (sibling: oid 1186 *Hackney v. Lynn* at 27 N.D. 458)
- `0250-Nelson-v-Middlewest-Grain-Co.doc` → already primary source of oid 2169 *Nelson v. Middlewest Grain Co.* (sibling: oid 2167 *Olson* at 44 N.D. 250)

**Bucket 3 — Corpus gaps (2 new opinions):** the `.doc` represents a real missing opinion. Pattern matches `emmons-county-vol9-ingest-2026-05-19` — sibling memorandum decisions on the same docket page that CL never captured because there was no matching cluster.

| new oid | case_name | N.D. cite | N.W. cite | date | controlled by |
|---:|---|---|---|---|---|
| 20498 | State ex rel. McCue v. Great Northern Railway Co. | 19 N.D. 57 | 120 N.W. 874 | 1909-04-16 | *State ex rel. McCue v. N. P. Ry. Co.* (this day decided), 120 N. W. 869 |
| 20499 | Lammadee v. Middlewest Grain Co. | 44 N.D. 247 | 173 N.W. 475 | 1919-06-21 | *Kluver v. Middlewest Grain Co.*, 173 N.W. 468 |

Evidence:
- **McCue v. Great Northern**: the parallel 1908-04-22 *State ex rel. McCue* cluster has 3 sibling opinions in DB (Great Northern @ 17 N.D. 370, MStP&SSM @ 301, Northern Pacific @ 223). The 1909-04-16 cluster previously had only 2 in DB (oid 498 NP, oid 499 MStP&SSM). The `.doc` at `N.D./19/0057-State-ex-rel-McCue-v-Great-Northern-R-Co.doc` is the missing third (a per curiam following the day's NP decision).
- **Lammadee**: the two `.doc`s at `N.D./44/0247` (`0247-Nelson-v-Middlewest-Grain-Co.doc` and `0247-Lammadee-v-Middlewest-Grain-Co.doc`) are byte-identical except for the plaintiff name (NELSON ↔ LAMMADEE). Same memorandum, distinct sibling opinions. DB had only oid 2171 *Nelson v. Middlewest Grain Co.* @ 247.

Method (matches Emmons): parse each `.doc` via `_parse_westlaw_doc`; INSERT `opinions` row (per_curiam=1, source_reporter=`westlaw`, source_path = refs-relative `N.D./<vol>/<file>.doc`, text_content = YAML frontmatter + body up to "All Citations"); INSERT N.D. citation (primary) + N.W. citation (secondary); INSERT westlaw `opinion_sources` row (is_primary=1); changelog audit. Corpus 20,168 → **20,170**.

Tool refinement logged: the AMBIG branch in `triage/adjudicate_mispaired_2026-05-20.py` should also (a) consult `opinion_sources` for the .doc (catches Bucket 2 = Bussey/Nelson@250), and (b) fuzzy-match parsed `.doc` case_name vs DB case_name (catches Bucket 1 = Kerr siblings). Same refinement as the ORPHAN classifier needs.

Invariants **18 ok / 2 known / 0 regressed**. Reversal: `DELETE FROM opinions WHERE id IN (20498, 20499)` + cascade (no automatic helper for `opinion.insert`); the 2 source rows are removable by changelog audit IDs.

## Batch `fix-casenames-vol16-79-orphan-enrich-2026-05-20` (3)

Case-name enrichments for the 3 ORPHAN-pairing opinions whose bound `.doc` captions add a role or locality qualifier the DB was missing. Pattern matches earlier accepted enrichments (`Barry v. Truax, District Court Clerk` and `State Bank of Maxbass` / `State Bank of Menagha` from vol 11–15 and vol 16–79 SAME).

| oid | bound (corrected) | was |
|---:|---|---|
| 680 | Fitzmaurice v. Willis, County Com'rs | Fitzmaurice v. Willis |
| 1487 | Sundahl v. First State Bank of Edmunds | Sundahl v. First State Bank |
| 1641 | Mercer County State Bank of Manhaven v. Hayes | Mercer County State Bank v. Hayes |

Invariants **18 ok / 2 known / 0 regressed**. Revertible.

Tool note: the ORPHAN_SIBLING classifier in `triage/adjudicate_mispaired_2026-05-20.py` checked whether the `.doc`'s source_path was attached to *any* opinion. A stronger check would also fuzzy-match the parsed `.doc` case_name against `opinions.case_name` (or look up its primary cite) — that would have surfaced these 7 as `ALREADY_PAIRED_BY_NAME` rather than `ORPHAN_SIBLING`. Logged as a tool refinement.

Invariants **18 ok / 2 known / 0 regressed**. Changelog-revertible (the 7 `opinion_sources.add` field entries can be removed by ID).

## Batch `fix-casenames-vol16-79-bound-2026-05-20` (58)

Vol-16–79 mispaired closeout in a single batch, methodology continued from `fix-casenames-vol11-15-bound-2026-05-19`: parse each archived Westlaw `.doc` in `~/refs/nd/opin/N.D./<vol>/`, compute jaccard(`.doc` body tokens, DB row `text_content` tokens), classify each of the 107 mispaired entries surfaced by the hardened `review_casenames` guard. No Westlaw page-image pulls needed.

Analyzer at `triage/adjudicate_mispaired_2026-05-20.py`; verdict TSV at `triage/casenames-mispaired-adjudication-2026-05-20.tsv`; applier at `triage/apply_mispaired_2026-05-20.py`. Thresholds: SAME ≥ 0.55, DIFF < 0.20, AMBIG otherwise.

**Verdict breakdown (107):**
- **59 SAME** → 58 applied (oid 1354 *Minneapolis Ry. Co.* skipped at user direction — consolidated-case caption rewrite warrants human review); 1 deferred
- **24 FALSE_POSITIVE_NORM** — DB already matches bound after Unicode normalization (curly `'` → `'`, Æ → ae). No DB change. Drives nearly all of the O'Connor/O'Brien/O'Toole/O'Hare/O'Sullivan/O'Dell/O'Rourke entries the guard flagged.
- **10 ALREADY_PAIRED** — `.doc` is correctly attached to a *different* opinion via `opinion_sources` (the cite-shared sibling case); guard's cite-only matching surfaced the wrong pair but the actual ingest got it right. No DB change.
- **7 ORPHAN_SIBLING** — `.doc` body diverges from this row AND `.doc` isn't paired with any opinion (potential corpus gaps; see TODO §1).
- **6 AMBIG** (jaccard 0.35–0.50) — defer to manual review. Includes oid 274 *Kerr v. Sunstrum* x2 (sibling docs `Kerr v. Herred`, `Kerr v. Swanson` at 16 N.D. 59).
- **1 SAME_NEEDS_HUMAN** — oid 4622 *Casselton Reporter v. The Fargo Forum*: Westlaw caption itself is truncated (`... v.` with no defendant). DB version is more complete; left as-is.

**Tooling additions beyond vol 11–15:**
- `deep_strip()` adds trailing-date (`June 19. 1907`) and bare-docket (`Cr.` after the number was already stripped) cleanup
- `smart_titlecase()` handles `McKEE'S` / `McINTYRE'S` mixed-case Mc-prefix words and `'S` → `'s` possessive
- Truncated-source guard bumps any proposal whose source caption ends with dangling `v.` to SAME_NEEDS_HUMAN

**Representative fixes (58):** wrong defendant captioned (oid 286 *Smith v. Show* → *Smith v. Bradley*; oid 651 *Borden v. McNamara* → *Borden v. Graves*); missing party detail (oid 1528 *State Bank v. Hurley* → *State Bank of Maxbass v. Hurley Farmers' Elevator Co. (Whitmore, Intervener). Same v. John D. Gruber Co. (Whitmore, Intervener)*); misspelled surnames (oid 504 *Chanlder* → *Chandler*; oid 2616 *Kenneggy* → *Kennelly*; oid 4047 *Bryne* → *Byrne*; oid 8659 *Schillerstrom* → *Schillerstorm*); format standardization (Manufacturing → Mfg.; *County of X* → *X County*; Pacific → Pac.); consolidated-case captions reunited (*Same v. ...* sub-cases preserved per bound).

**Outstanding work surfaced (not in this batch):**
- **7 ORPHAN_SIBLINGs** — investigate as potential corpus gaps: vol 20/oid 672 (FITZMAURICE v. WILLIS @ 20 N.D. 372), vol 20/683 (STOLTZE v. HURD @ 412), vol 21/765 (HEARD v. HOLBROOK @ 348), vol 23/929 (BISMARCK WATER SUPPLY v. CITY OF BISMARCK @ 352), vol 24/978 (McCARTY v. KEPRETA @ 395), vol 32/1486 (SUNDAHL v. FIRST STATE BANK @ 373), vol 34/1640 (MERCER COUNTY STATE BANK v. HAYES @ 601).
- **6 AMBIGs** and **oid 1354** and **oid 4622** — manual review queue.
- **2053 ambiguous case-name diffs (non-mispaired)** across vols 16–79 — still pending interactive TUI run via `review_casenames`.

Invariants **18 ok / 2 known / 0 regressed**. All 58 changes changelog-revertible.

## Batch `nw-bound-image-source-section10-spotcheck-2026-05-19` (11 NW-image rows) + §10 design + spot-check

Section 10 (back-assignment of synthetic medium-neutral `YYYY ND nnn` cites for pre-1997 opinions) — design ratified, ordering theory spot-checked **4/4**.

**Design ratified** (to be applied in a separate implementation batch):
- Storage: extend `citations.reporter` taxonomy with `ND-neutral-synthetic`; one row per back-assigned opinion; `is_primary=0` always.
- Format: `YYYY ND nnn` where `YYYY` = `date_filed`'s year, `nnn` = 1-based sequence within year.
- Ordering key: `(date_filed, ND-starting-page, NW-starting-page, on-page-order)`.
- Visual marker: render as `[YYYY ND nnn]` (bracketed) in MCP / `lookup_opinion` output to distinguish from native cites.
- Scope: all pre-1997 opinions (`date_filed < '1997-01-01'`, ~14,000 opinions).
- Invariants (planned): `synthetic_format`, `synthetic_uniqueness_per_year`, `synthetic_only_pre_1997`, `synthetic_never_primary`.
- The 258 post-1997 `neutral_cite_uniqueness` baseline is **not** in §10 scope (that's §6 dup-pair cleanup).

**Spot-check** (`nw-bound-image-source-section10-spotcheck-2026-05-19`, 11 NW-image rows): 4 of 5 spot-check bound pages delivered (the 5th — `96 N.W. 1134` for the Sykes/Montgomery same-NW/diff-date category — Westlaw returned the Minn *In re Zeugner* case instead; the user's selection went to the wrong disambiguation entry). Of the 4 delivered, all confirm the `(N.D.-page, N.W.-page, date)` ordering heuristic:

| Cluster | Predicted | Bound printed | Verdict |
|---|---|---|---|
| 10 N.D. 400 (Willard, White) | Willard (87 N.W. 996) → White (1135) | ✓ matches | same-date/diff-NW holds |
| 14 N.D. 557 (Poull, Murphy) | Poull (105 N.W. 717) → Murphy (734) | ✓ matches | N.W.-page-within-vol holds |
| 100 N.W. 1084 (Hanson, Lough, Marshall-Wells) | by N.D. page 361→387→396 | ✓ matches | diff-both holds (N.D.-page primary) |
| 111 N.W. 614 (Anderson + Sunstrum/Swanson/Herred) | Anderson (16 N.D. 36) → Sunstrum (16 N.D. 59) | ✓ matches | N.D.-page primary, N.W.-page secondary |

**Outstanding residual risk**: the "same-NW/diff-date" category (only 3 clusters in the 1B set — `12 N.D. 504`, `68 N.D. 310`, `78 N.D. 10`) is untested by direct bound-page evidence. Can be re-pulled with corrected disambiguation if anomalies surface during §10 assignment.

**Bonus finding** (from 87 N.W. 996 read): oid5834 *White v. Lauder* (1901-10-25) is confirmed a CL date-drift dup of oid5833 (1901-11-21, bound-validated date). Already logged as a §6 cleanup item.

§10 implementation deferred to a later session per user direction.

## Batch `fix-emmons-nw-cite-2026-05-19` (4 cite updates)

Cleanup of the N.W. cites for the 5747–5751 Emmons County rows surfaced by the bound `.docs` during the 2026-05-19 vol-9 ingest. CL had assigned `84 N.W. 1117` to all 8 Emmons County 1117-cluster rows uniformly, but the bound .docs split the cluster across N.W. pages:

| oid | case | N.D. page | old cite | bound cite |
|---:|---|---|---|---|
| 5751 | Lilly | 611 | 84 N.W. 1117 | 84 N.W. 1117 ✓ (already correct) |
| 5750 | Mellon | 612 | 84 N.W. 1117 | **84 N.W. 1118** |
| 5749 | Robinson | 613 | 84 N.W. 1117 | **84 N.W. 1118** |
| 5748 | Thistlewaite | 614 | 84 N.W. 1117 | **84 N.W. 1118** |
| 5747 | Wilson | 615 | 84 N.W. 1117 | **84 N.W. 1119** |

Page-break in the bound reporter: 1117 covers N.D. pages 608–611 (Cranmer/Davidson/Baker/Couch/Davidson/Cranmer/Ganger/Kelly/Lilly), 1118 covers 612–614, 1119 starts with Wilson@615. 4 `citations.citation` UPDATEs applied (changelog-revertible). Invariants **18 ok / 2 known / 0 regressed**.

## Batch `fix-casenames-vol11-15-bound-2026-05-19` (14) + `fix-cairncross-source-2026-05-19` (1)

Vol-11–15 mispaired closeout — **resolved entirely digitally**, no Westlaw page-image pull needed. The Westlaw `.docs` in `~/refs/nd/opin/N.D./<vol>/` are the bound N.D. Reports text; jaccard-comparing each `.doc` body to the cite-matched DB row's `text_content` cleanly classifies the 20 mispaired entries: 17 SAME (jac ≥ 0.55), 3 DIFF (jac < 0.20), 0 ambiguous.

**14 case_name corrections to the bound caption** (`fix-casenames-vol11-15-bound-2026-05-19`):

| oid | bound (corrected) | was (CL) |
|---:|---|---|
| 5927 | Anderson v. Cass County Drain Com'rs | Hagman v. Cass County Drain Com'rs |
| 5988 | Hertzler v. Cass County | Hertzler v. Freeman |
| 6012 | State ex rel. Styles v. Baeverstad | State v. Beaverstall |
| 6013 | Persons v. Persons | Persons v. Smith |
| 6022 | Hunter v. McDevitt | Hunter v. Coe |
| 36 | Davis v. Dinnie | Davis v. Jacobson |
| 54 | Fox v. Jones | Fox v. Walley |
| 6049 | Barry v. Truax, District Court Clerk | Barry v. Traux |
| 78 | Avery Mfg. Co. v. Smith | Avery Manufacturing Co. v. Crumb |
| 94 | Hulet v. Gates | Hulet v. Northern Pacific Railway Co. |
| 158 | Hart v. Evanson | Hart v. Hanson |
| 157 | Brown v. Hodgson | Brown v. Newman |
| 161 | McCormick Harvesting Mach. Co. v. Citizens' Bank of Drayton | McCormick Harvester Machine Co. v. Caldwell |
| 235 | Skjelbred v. Southard | Skjelbred v. Shafer |

Pattern: CL captioned by a co-party (plaintiff or defendant), a wrong defendant, or a misspelled surname — same opinion (jaccard 0.78–0.99). Two iterations needed: title-casing escaped on the `McDEVITT`/`McCORMICK`/`MacH.` cases (`Mc`/`Mac` regex only handled lowercase-following-Mc), fixed in a follow-up update under the same batch.

**3 false-positives in the SAME bucket (no DB change)**: oids 83 *State v. O'Malley*, 121 *O'Keefe v. Leistikow*, 252 *Higbee v. Daeley* — the guard diverted only because the bound `.doc` rendered the apostrophe as a curly quote (`’`) or the Æ ligature, which didn't normalize-equal under `_same_case`. DB already matches the bound (after curly→straight and Æ→ae normalization). Logged as a normalize-improvement candidate for the tool.

**3 DIFF cases — all false-positives too** (different kind): oids 5982/Montgomery, 6/Lough, 146/State v. Poull. The `.docs` parsed by `extract_diffs` describe *siblings* (Sykes v. Allen, Cairncross v. Omlie, Murphy v. District Court — all in DB) that share the cite. But the *actual* `opinion_sources` table already pairs each opinion with its own correct `.doc` — the ingest got the pairing right; the review tool's cite-only `_find_db_opinion` returned an arbitrary sibling and the per-pair view showed the wrong sibling's caption. Listed for tool refinement: the guard should consult the existing opinion_sources pairings, not just the cite-matched row, when classifying a `.doc`.

**1 micro-fix surfaced** (`fix-cairncross-source-2026-05-19`): oid45 *Cairncross v. Omlie* (13 N.D. 387) had its Westlaw `.doc` on disk but was missing a `westlaw` `opinion_sources` row — registered as non-primary (promote-to-primary deferred to a future `merge_westlaw_text` pass). All other DIFF/SAME oids in this batch were already correctly sourced.

Invariants **18 ok / 2 known / 0 regressed**. All changelog-revertible. Methodology lesson: digital adjudication via `.doc`-body jaccard is far cheaper and produces the same answers as the page-image pulls used for vols 1–10; the bound page images add visual confidence but rarely change the verdict. Use page-image pulls only for genuinely ambiguous cases going forward.

## Batch `emmons-county-vol9-ingest-2026-05-19` (9 new opinions)

Corpus growth — 9 Emmons County tax-foreclosure memorandum decisions ingested from N.D./9/ Westlaw `.doc`s that were on disk since the original vol-79 Quick Check but never made it into the DB (no matching CL row to pair against). Discovery surfaced by reading the bound `NW/84/1117.pdf` page image (TODO §1 today). New opinions (all 1900-11-13, per curiam, controlled by *Emmons Co. v. Thompson* 84 N.W. 385):

| oid | case_name | N.D. cite | N.W. cite |
|---:|---|---|---|
| 20489 | Emmons County v. Cranmer | 9 N.D. 608 | 84 N.W. 1117 |
| 20490 | Emmons County v. Baker | 9 N.D. 609 | 84 N.W. 1117 |
| 20491 | Emmons County v. Davidson | 9 N.D. 609 | 84 N.W. 1117 |
| 20492 | Emmons County v. Cranmer | 9 N.D. 610 | 84 N.W. 1117 |
| 20493 | Emmons County v. Ganger | 9 N.D. 610 | 84 N.W. 1117 |
| 20494 | Emmons County v. McKenzie | 9 N.D. 611 | 84 N.W. 1118 |
| 20495 | Emmons County v. McKenzie | 9 N.D. 612 | 84 N.W. 1118 |
| 20496 | Emmons County v. McLean | 9 N.D. 612 | 84 N.W. 1118 |
| 20497 | Emmons County v. Mellon | 9 N.D. 613 | 84 N.W. 1118 |

Method: parse each `.doc` via `_parse_westlaw_doc`; INSERT `opinions` row (court=`North Dakota Supreme Court`, per_curiam=1, source_reporter=`westlaw`, source_path refs-relative `N.D./9/<file>.doc`, text_content = full bound text with YAML frontmatter); INSERT N.D. citation (primary) + N.W. citation (secondary, taxonomy `NW`); INSERT westlaw `opinion_sources` row (is_primary=1); changelog audit. Same-defendant surname appearing at multiple N.D. pages (Cranmer 608+610, Davidson 608+609, McKenzie 611+612) reflects separate tax-foreclosure actions on different properties. Corpus 20,159 → **20,168**.

**Related cite-cleanup follow-up surfaced:** the existing rows oids 5751 Lilly@611, 5750 Mellon@612, 5749 Robinson@613, 5748 Thistlewaite@614, 5747 Wilson@615 all carry N.W. cite `84 N.W. 1117`, but the bound `.docs` for pages ≥611 use `84 N.W. 1118 (Mem)`. CL gave them the cluster's starting N.W. page; the bound pagination puts pages 611+ on N.W. 1118. Logged in TODO §1; low-priority data-quality fix.

Invariants **18 ok / 2 known / 0 regressed**. Reversal would be `DELETE FROM opinions WHERE id IN (20489..20497)` + cascade — recorded in changelog under `emmons-county-vol9-ingest-2026-05-19` but no automatic revert helper for `opinion.insert` field type.

## O'Conner/O'Connor corpus-wide audit (2026-05-19)

Audit prompted by yesterday's two O'Conner spelling fixes (oids 5430, 5762). Query: all `case_name LIKE '%O''Connor%'` opinions, 1893–1905. Result: **5 surviving rows**, of which:
- **oid5406 *Elton v. O'Connor*** (68 N.W. 84, 1896-05) — bound says CONNOR, DB CONNOR ✓ matches
- **oid5555 *Tetrault v. O'Connor*** (76 N.W. 225, 1898) — bound says CONNOR ✓; *different individual* (A. M. O'Connor, not M. J.)
- **oid5396 *Selliger v. O'Connor*** (67 N.W. 824, 1896-06) — *candidate* (body says "M. J. O'Connor"; bound not yet pulled); 67 N.W. is adjacent to 68 N.W. (Elton CONNOR), so likely OK as-is, but unconfirmed

**Refined hypothesis (correcting yesterday's CHANGELOG):** the original characterization "CL OCR systematically misread Conner as Connor for sheriff M. J. O'Conner" is too strong. The bound *N.W. Reporter itself uses different spellings* across volumes for what appears to be the same individual (vol 68 N.W. → CONNOR; vol 69 N.W. + vol 84 N.W. → CONNER). CL happens to match each bound's chosen spelling. There is no systematic OCR error — the variance is in the printed reporter. No further fixes warranted unless oid5396's bound pull reveals CONNER. Pull `67 N.W. 824` only if/when convenient.

## Batches `nw-bound-image-source-2026-05-19b` (10) + `fix-henniges-johnson-5758-2026-05-19` (4)

Closeout of the 3 non-unique vol-6–10 bound-page pulls + the *Henniges v. Johnson* correction (re-interpreting yesterday's "missing opinion" finding).

**Non-uniques delivered + filed at NW tree, NW-image source rows registered:**
- `NW/73/1102.pdf` → oid5486 *State v. O'Grady* (bound caption matches DB) ✓
- `NW/84/1117.pdf` → 8 NW-image rows for the entire Emmons County cluster (oids 5747-5754 share the bound page) ✓
- `NW/87/1135.pdf` → oid5833 *White v. Lauder* (the 1901-11-21 row; bound-validated matches DB) ✓

**Correction of yesterday's CHANGELOG (commit `bbe3f72`) — "Henniges v. Johnson missing opinion" was wrong.** Investigated when Westlaw delivered the editable `.doc`: the bound `.doc` and oid5758's existing `text_content` are the **same opinion** (jaccard 0.818, identical disposition/panel). *Paschke* is the third-party good-faith purchaser referenced 12+ times in the body; *Johnson* (John Johnson, mortgagor) is the actual defendant. CL captioned the case by the wrong party. There is no missing opinion. Applied via `fix-henniges-johnson-5758-2026-05-19`:
- **oid5758 case_name** `Henniges v. Paschke` → `Henniges v. Johnson` (bound + appellate caption)
- **Re-attached** `NW/84/350.pdf` as oid5758's `NW-image` source (reverts the erroneous `fix-mispaired-nwimage-5758-2026-05-19` removal; the bound page IS oid5758's)
- **Registered** the Westlaw bound text at `N.D./9/0489-Henniges-v-Johnson.doc` as oid5758's `westlaw` source (the .doc existed on disk from the original vol-79 Quick Check but was never wired to opinion_sources — likely a vol-9 ingest miss)
- **Added** parallel citation `81 Am.St.Rep. 588` (per the bound .doc's All Citations; tagged `ALR` provisionally pending an `AmStRep` taxonomy value — see SCHEMA follow-up)

**Real new corpus gap discovered (84 N.W. 1117):** the bound *MEMORANDUM DECISIONS* page contains **at least 11 distinct Emmons County tax cases** (Baker, Couch, Cranmer ×2, Davidson ×2, Ganger, Kelly, Lilly visible on page 1; Wilson/Thistlewaite/Robinson/Mellon on subsequent pages). Our corpus has the 8 Wilson–Davidson rows (oids 5747-5754) but **Baker, Cranmer (×2), Ganger are missing** — likely 4 additional Emmons County v. X opinions in vol 9 N.D. (9 N.D. ~605-617 range, all decided 1900-11-13 per curiam, all controlled by *Emmons Co. v. Thompson* at 84 N.W. 385). Logged in TODO §1; separate ingest pass needed.

**Also surfaced (lower-priority §6 cleanup):** oid5834 *White v. Lauder* (1901-10-25, same cites 10 N.D. 400 / 87 N.W. 1135 as oid5833) is almost certainly a CL date-drift double-ingest of the same opinion as oid5833 (1901-11-21, the bound-validated date). §6 `merge_pair` candidate.

Invariants **18 ok / 2 known / 0 regressed**. All changes changelog-revertible.

## Batches `fix-casenames-vol6-10-bound-2026-05-19` (7) + `nw-bound-image-source-2026-05-19` (18) + `fix-mispaired-nwimage-5758-2026-05-19` (1)

Bound N.W. Reporter resolution for the 21 vol-6–10 mispaired items (the diverted output of the hardened `review_casenames` guard). Westlaw delivered 18 of 21 (3 non-unique cites — 73 N.W. 1102 *O'Grady*, 84 N.W. 1117 *Emmons County* cluster, 87 N.W. 1135 *White v. Lauder* — still pending after document selection). All 18 filed at `~/refs/nd/opin/NW/<vol>/<page>.pdf` and registered as non-primary `NW-image` `opinion_sources` rows.

**7 case_name corrections to the authoritative bound-reporter caption** (`fix-casenames-vol6-10-bound-2026-05-19`):

| oid | cite | old (CL) | new (bound) | reason |
|---|---|---|---|---|
| 5487 | 73 N.W. 203 | *Red River Lumber Co. v. Children of Israel* | *Red River Lumber Co. v. Friel* | CL titled by co-defendant Congregation; body confirms Friel |
| 5490 | 73 N.W. 430 | *Gull River Lumber Co. v. Lee* | *Gull River Lumber Co. v. Brock* | CL titled by co-defendant Lee (county treasurer); body confirms Brock is mortgagor |
| 5542 | 75 N.W. 904 | *Tribune Printing & Binding Co. v. Barnes* | *Knight v. Barnes* | CL titled by plaintiff *company*; bound uses individual plaintiffs Knight et al. |
| 5575 | 77 N.W. 1000 | *Warnken & Co. v. Langdon Mercantile Co.* | *Warnken v. Chisholm* | CL titled by partnership names; bound uses individual surnames |
| 5430 | 69 N.W. 692 | *State ex rel. Brooks Bros. v. O'Connor* | *State ex rel. Brooks Bros. v. O'Conner* | CL OCR: defendant M. J. O'Conner (sheriff), CL stored "Connor"; bound consistently "Conner" |
| 5675 | 81 N.W. 31 | *Richardson v. Campbell* | *Campbell v. Richardson* | parties transposed — DB used trial-court order; bound uses appellate caption (Campbell appellant) |
| 5762 | 84 N.W. 359 | *Olson v. O'Connor* | *Olson v. O'Conner* | same M. J. O'Conner sheriff spelling fix as 5430 |

**10 bound-validated unchanged**: 5406 *Elton v. O'Connor* (different individual; bound also "Connor"), 5421 *Elstad v. Northwestern Elevator Co*, 5465/5545 *Scottish American Mortgage Co. v. Reeve* (style only — bound abbreviates "Mortg." / hyphenates), 5548 *O'Leary v. Brooks Elevator Co.*, 5555 *Tetrault v. O'Connor*, 5606 *Lane v. O'Toole*, 5627 *O'Toole v. Omlie*, 5640 *Red River Valley National Bank v. North Star Boot & Shoe Co.*, 5719 *St. Anthony & Dakota Elevator Co. v. Soucie*.

**Surprise finding — corpus gap discovered** (`fix-mispaired-nwimage-5758-2026-05-19`): the bound page `NW/84/350.pdf` *does not* belong to oid5758 *Henniges v. Paschke* despite CL's cite assignment. p.350 left column ends *Paschke*; right column begins **`HENNIGES et al. v. JOHNSON et al.`** (Walsh county; decided same day 1900-11-20) — a **separate ND Supreme Court opinion missing from our corpus**. oid5758's case_name is correctly *Henniges v. Paschke* (body confirms — Fred Henniges v. John Paschke, mortgage dispute); CL gave it the wrong N.W. start-page cite. Removed the wrongly-attributed `NW-image` source row from oid5758; the PDF remains in the NW tree as a placeholder for the future *Henniges v. Johnson* ingest. Tracked in TODO §1.

**Cross-cutting OCR pattern surfaced:** M. J. O'Conner (sheriff named in multiple late-1890s cases) is consistently "Conner" in the bound reporter but "Connor" across the CL-derived text and metadata — likely a systematic CL OCR error. 2 fixed here (5430, 5762); a corpus-wide audit for the same person/spelling pattern would be worthwhile (logged in TODO §1).

**Result**: 18 NW-image rows + 7 case_name updates − 1 mis-attributed row removal. Invariants **18 ok / 2 known / 0 regressed**. All changes changelog-revertible (no row deletions, no snapshot needed).

## Batches `fix-casenames-vol1-5-bound-2026-05-18` (3) + `nw-bound-image-source-2026-05-18` (5)

Resolution of the 5 vol-1–5 case-name items the hardened tool diverted, using **scanned bound N.W. Reporter page images** pulled from Westlaw (image-only PDFs — an independent third witness, distinct from both the CourtListener OCR and the Westlaw `.doc` editorial text). Filed at `~/refs/nd/opin/NW/<vol>/<page>.pdf` (co-located with the existing CL `<page>.md`/`.json`).

Bound-reporter caption is authoritative. Findings:
- **oid5380 `State v. Pancoast`** (5 N.D. 516 / 67 N.W. 1052) — ✓ already correct. The reporter caption is *STATE v. PANCOAST*; defendant William W. Pancoast was charged under the alias *Myron R. Kent* and the court **expressly** states it will use "Kent" in the opinion body — which is exactly why `text_content` reads "Kent" while `case_name`/`.doc` say "Pancoast". Not a shared-page tangle, not a mispairing; single opinion. No change.
- **oid5242 `Coler v. Dwight School Tp. of Richland County`** (3 N.D. 249 / 55 N.W. 587) — ✓ bound-validated (the prior pass's value matches the reporter caption).
- **`fix-casenames-vol1-5-bound-2026-05-18` (3 case_name corrections to the bound-authoritative caption)**: oid5152 `Sanford v. Duluth & Dakota Elevator Co.` → **`Sanford v. Bell`** (reporter: *SANFORD v. BELL et al.*; CL had titled it by a co-defendant); oid5182 `Pirie v. Gillitt` → **`Carson v. Gillitt`** (reporter: *CARSON et al. v. GILLITT et al.*; CL titled by a co-plaintiff); oid5203 `State v. Hazledahl` → **`State v. Hasledahl`** (reporter: *STATE v. HASLEDAHL*; CL `z`/`s` OCR error — the Westlaw `.doc` was right). Changelog-revertible; no row deletions. **Doctrine note:** the items the `_same_case` guard diverts are not necessarily mispairings/missing opinions — frequently CL simply titled a single opinion by a co-party or OCR-corrupted a surname; the bound reporter is the tiebreaker and here vindicated the Westlaw `.doc` over both CL and the earlier conservative reverts.
- **`nw-bound-image-source-2026-05-18` (5 rows)**: each PDF registered as a non-primary `NW-image` `opinion_sources` row (`source_path=NW/<vol>/<page>.pdf`, `text_length=0`, `is_primary=0`) — an independent human-verifiable witness toward the §9 two-source bar. New convention documented in `SCHEMA.md` (`opinion_sources.source_reporter` provenance values). **Redistribution:** Westlaw-delivered scans — PDFs stay in `~/refs`, excluded from the public release; the DB row is only a refs-relative path reference (bytes never enter the repo/`opinions.db`).
- Invariants **18 ok / 2 known / 0 regressed** (`NW-image` rows are inert w.r.t. the primary-source invariants — they join only `is_primary=1`).

## Batch `fix-casenames-vol1-5-misattrib-2026-05-18` (6 rows) + `review_casenames` tool hardening

First systematic case-name sweep session (vols 1–5, restarted at vol 1, via `review_casenames` TUI): 13 case-name corrections applied (`westlaw-nd-vol{1,2,3,4}-casenames`) + 120 keep-DB decisions recorded (`triage/casenames-state.json`). **Post-review audit found 6 of the 13 applied changes were wrong** and reverted them to each opinion's correct value (verified against the opinion's own `text_content` title):

- **oid5152** `Sanford v. Bell` → `Sanford v. Duluth & Dakota Elevator Co.` (mis-paired .doc)
- **oid5182** `Carson v. Gillitt` → `Pirie v. Gillitt` (mis-paired .doc)
- **oid5192** `Northern Pac. R. Co. v. Tressler, County Treasurer` → `Cleary v. County of Eddy` (shared-page: cite shared with oid5197, the real NP RR v. Tressler)
- **oid5274** `Globe Inv. Co. v. Boyum` → `Kellogg, Johnson & Co. v. Gilman` (shared-page `3 N.D. 538`, the §6-confirmed-distinct pair with oid5275)
- **oid5203** `State v. Hasledahl.*` → `State v. Hazledahl` (leaked footnote-star artifact)
- **oid5291** `…Fargo Gas & Electric Co` → `…Co.` (normalization wrongly stripped an abbreviation period)

The 7 legitimate cleanups remain applied (5126 Slattery, 5212 *State ex rel. Northern Pac. R. Co.*, 5242 Coler, 5255 Heger, 5266 Power v. Larabee, 5286 Paulson, 5306 Dows). Revert batch is changelog-revertible; no row deletions, no snapshot needed.

**Root cause + tool fix (`ndcourts_mcp/review_casenames.py`, committed).** `_find_db_opinion` binds a Westlaw `.doc` to a DB opinion by *shared citation alone*; pre-1953 shared-page clusters make it return an arbitrary co-located opinion, so the parsed caption could belong to a sibling — and the per-pair TUI gave the reviewer no signal. Fixes: (1) **pairing guard** — before surfacing a rename, verify the `.doc` caption describes the same case as the opinion's own `text_content` title via a new `_same_case` (reuses `_case_names_match`, then an OCR-tolerant edit-distance≤1 principal-token match on *both* the plaintiff and defendant side, so spelling variants like `Powers`/`Power`, `Spalding`/`Spaulding`, `De Groat`/`DeGroat` are still offered while a true party swap is blocked); mismatches divert to `triage/casenames-mispaired-2026-05-18.tsv` and are never offered. (2) **normalization** — `_strip_decorative_period` keeps abbreviation periods (`Co.`), added `_TRAIL_STAR` strips footnote-star artifacts. Re-scoped vols 1–5: the 6 errors now auto-divert (4 true mispairings flagged, incl. 5380 *Pancoast*/text-says-*Kent*; the rest resolve to case-only `equiv`); validated 15/15 on a unit harness incl. negative guards.

## Batches `section6-needsdecision-2026-05-18` (16) + `section6-defermulti-2026-05-18` (5)

Adjudication of the §6 long-tail bands left after MERGE-HOLD-LOWJAC: **NEEDS_DECISION** (82 cite-rows → 70 unique opinion-pairs, jaccard <0.55, scan-labelled "distinct/shared-page") and **DEFER_MULTI** (37 cites where >2 rows share one cite). Worklists `triage/section6-needsdecision-worklist-2026-05-18.tsv` + `triage/section6-defermulti-worklist-2026-05-18.tsv`.

- **NEEDS_DECISION — 16 merged** (`section6-needsdecision-2026-05-18`). All 68 live pairs were metadata-stratified, then every same-/near-same-party candidate was text-read. 16 proved to be CL-markdown + Westlaw-bound double-ingests of one opinion (identical disposition text + identical panel-concurrence line + same docket/date; the only deltas were Syllabus-present, ALL-CAPS caption, and OCR garble in the `judges` field — the documented pre-1953 westlaw+NW jaccard-depression artifact). Keep = the Westlaw-bound row (preserves the court's "Syllabus by the Court"; `merge_pair` keeps survivor text untouched), independent of `cited_by` (re-pointed either way). Pairs (keep←drop): 7522←7523 Milde v. Leigh, 4484←4485 Ott v. Kelley, 4807←4808 Southall v. Thompson, 4826←4827 State v. Hawley, 4845←4846 Paseka v. Armour & Co., 5060←5061 Bateman v. State, 5087←5088 Raatz v. Sand, 9543←9544 State ex rel. Magrum v. Nygaard, 9676←9677 Ahoe v. Massill, 9807←9808 In re the Appeal of Hatlie, 4426←4427 Baird v. Gray, 4809←4810 Southall v. Quam, 4842←4844 Weir v. Armour & Co., 4841←4843 Haugen v. Armour & Co., 9811←9813 McArthur v. Cass County, 9810←9812 Arnold v. Cass County. Corpus −16.
- **NEEDS_DECISION — 50 confirmed keep-separate, NOT merged.** Different-party opinions legitimately sharing one reporter page (the documented per-curiam shared-page model — different parties, near-zero jaccard, often adjacent N.D. pages, e.g. *Marquart v. Schaffner* 30 N.D. 342 / *Holobuck v. Schaffner* 30 N.D. 344 @ 152 N.W. 660; *Becker v. Duncan* 8 N.D. 600 / *Heyrock v. McKenzie* 8 N.D. 601 @ 80 N.W. 762) plus 3 deliberate supplemental-publication inserts that share the lead's N.D. cite by design (`Druey v. Baldwin` separate opinion 20387, `Altenbrun` concurrence 20388, `Lincoln Addition` joint per curiam 20390 — correct per the supplemental-publications doctrine, scan false-positives). 2 stale (already merged away: 11201/11200 @ 489 N.W.2d 885, 12028/12027 @ 539 N.W.2d 869).
- **DEFER_MULTI — 5 merged** (`section6-defermulti-2026-05-18`), text-read from the 6 same-matter candidates in otherwise-distinct clusters: 1014←1015 *Hawkins v. Sinclair* (CL date-drift double-ingest, kept Westlaw row with the correct 1912-11-20 date matching the Sinclair group), 20386←459 *State ex rel. City of Minot v. Willis* per-curiam follow-on (459 was the CL copy of the same follow-on the deliberate supplemental insert 20386 represents — kept the supplemental row), 3130←3132 *State ex rel. Solberg v. Spicher* (identical 24k habeas opinion), 3233←3235 *State ex rel. Pfann v. Kunkel* (identical habeas opinion, same author), 10931←10932 *Disciplinary Bd. v. Johnson* (same docket 910126 / date / interim-suspension order — CL double-ingest of two cluster_ids; both NW2d-only, kept the fuller-caption + authored row). **9767/9768 *In re Schirado* confirmed DISTINCT** — interim Order of Suspension (1986-09-16) vs final order (1986-11-03): different text, dispositions, dates; sequential orders, each its own publication. Corpus −5.
- **DEFER_MULTI — rest keep-separate.** ~14 all-distinct shared-page companion clusters (e.g. *Emmons County v.* 8 defendants @ 84 N.W. 1117; *Cass County Drain Com'rs* @ 92 N.W. 1133/1134; the Lynn/Lillethun/Sinclair per-curiam batches); the 249 N.W. 718 / 277 N.W. 604 / 280 N.W. 204 / 4 N.W.2d 224 / 64 N.D. 367 clusters' embedded dups were resolved by the NEEDS_DECISION pass (residue now distinct); 489 N.W.2d 886 / 521 N.W.2d 643 / 57 N.W.2d 242 already adjudicated in the 2026-05-17 §6-handadj clusters work.
- **Deferred (untouched this pass):** 9 post-1997 DEFER_MULTI clusters are **DEFER_MODERN** (612 N.W.2d 278, 638 N.W.2d 45, 709/711/719/742/756 N.W.2d, 766/777 N.W.2d) — touch the public release + the 258 `neutral_cite_uniqueness` baseline, and two carry CONFIDENTIAL juvenile matters; handled separately with the rest of the 530 DEFER_MODERN set.
- **Cite-hygiene follow-ups surfaced** (not row merges, captured in TODO §6): a few distinct opinions share an N.D. parallel that is contaminated on one side (CL parallel-cite cross-contamination, e.g. *White v. Lauder* `10 N.D. 400`); and `55 U.S.L.W. 2667` is carried as an opinion citation on two distinct 1987 opinions (foreign secondary cite — should be stripped per the 2026-05-17 foreign-cross-ref policy).
- **Result**: corpus 20,180 → **20,159** (−21). `align_primary_source --apply` (16 + 4 primary-flag flips, 0 source_path rewrites, 0 no-primary). Invariants **18 ok / 2 known / 0 regressed**; `neutral_cite_uniqueness` Δ=+0 (correct — all pre-1953/pre-1997 N.W./N.W.2d, no `YYYY ND n` cite); **0 orphan refs** across citations/opinion_sources/text_citations/cited_by + 0 residual refs to dropped oids.
- **Safety**: snapshots `opinions.db.bak-pre-s6-needsdecision-2026-05-18` (pre the 16) and `opinions.db.bak-pre-s6-defermulti-2026-05-18` (pre the 5). `merge_pair` `DELETE`s the drop row — **NOT changelog-revertible**; snapshot-only recovery.

## Batches `section6-lowjac-mid-merge-2026-05-18` (10) + `section6-lowjac-supp-merge-2026-05-18` (15)

Per-pair adjudication of the 28 MID_NEEDS_READ pairs (name-sim 0.80–0.95) from the §6 0.55–0.85 band, after the SAFE-25 batch below.

- **MID REC_MERGE — 10 merged** (`section6-lowjac-mid-merge-2026-05-18`): same parties, pure name-format/abbreviation variants (`Comp.`=`Compensation`, `…of St. Paul`, `, Inc.`, `Ins. Co.`=`Insurance`, relator truncation), author-compatible → true double-ingest. Corpus −10.
- **MID KEEP_DISTINCT_SUPP — 15: doctrine default OVERTURNED by text read.** These had identical caption + same cite + same date but *different author*, which the supplemental-publication doctrine flags as likely lead-vs-rehearing (recommend keep). User directed a per-pair text read; **all 15 proved to be the SAME opinion double-ingested** — a CL/ndcourts markdown copy (`# header / ## Opinion`, no Syllabus) plus a Westlaw bound copy (`Syllabus by the Court` + attorneys block); identical dispositions/concurring justices; the "different author" was a metadata mis-parse and the 0.60–0.85 jaccard was the Syllabus-present-vs-absent + pre-1953 OCR-drift artifact (the documented westlaw+NW band phenomenon), not distinct opinions. **15 merged** (`section6-lowjac-supp-merge-2026-05-18`), keep = the Westlaw-bound row (preserves the court's "Syllabus by the Court"); `cited_by` re-pointed. Corpus −15. *Lesson: in the pre-1953 §6 band, same-name/same-cite/different-author is frequently a CL+Westlaw double-ingest, not a separate authored opinion — text-read before trusting the diff-author heuristic.*
- **3 MID REC_DISTINCT** (Middlewest Grain family Nelson/Olson/Livingston; `Johnson` vs `Colgrove` v. National Union Fire) — different plaintiffs sharing a page; confirmed distinct, NOT merged.
- merge_pair re-point briefly regressed `source_reporter/path_matches_primary` (15, expected for swapped-keep rows); cleared by the standard `align_primary_source --apply` (15 primary-flag flips). Final invariants 18 ok / 2 known / 0 regressed; orphans OK.
- **Safety**: snapshots `opinions.db.bak-pre-section6-mid-2026-05-18` (pre the 10) and `opinions.db.bak-pre-section6-supp-2026-05-18` (pre the 15); provenance `section6_dedup_lowjac_mid` / `_supp`. Row deletes are snapshot-only revert.

## Batch `section6-lowjac-safedup-2026-05-18` (25 opinion-pairs)

Adjudicated subset of the 146 §6 MERGE-HOLD-LOWJAC band (pre-1997 same-cite/same-date pairs at 0.55–0.85 jaccard, which deliberately mixes true double-ingests with distinct shared-page opinions). Stratified by case-name identity (the real discriminator — *not* jaccard, which overlaps): SAFE_TRUEDUP = normalized name-sim ≥0.95 + non-contradictory author + same cite + same date.

- **49 SAFE rows → 25 distinct opinion-pairs** (cite double-views — N.W. + N.D. — collapse), no transitive overlap. Explicit per-pair `merge_pair()` (NOT a lowered-`--min-jaccard` batch-apply, which would have destroyed the 44 distinct shared-page pairs in the band). Keep = more inbound `cited_by`, tie → lower cluster_id; canonical name via the conservative probate-only `_canonical_name`.
- **Result**: corpus 20,229 → **20,204** (−25). Invariants 18 ok / 2 known / 0 regressed; all 4 orphan checks OK (merge_pair 13-table re-point + FTS triggers).
- **Adjudication artifacts** (committed): `triage/section6-lowjac-adjudication-2026-05-18.tsv` (all 146 bucketed SAFE/MID/DISTINCT) and `triage/section6-lowjac-MID-recommendations-2026-05-18.tsv` (per-pair reasoned recs for the 28 MID pairs — awaiting user batch approval, NOT applied). The 44 DISTINCT_SHAREDPAGE pairs are correctly left unmerged.
- **Safety**: snapshot `opinions.db.bak-pre-section6-lowjac-2026-05-18`. Row deletions are snapshot-only revert (not changelog-replayable); provenance logged (`section6_dedup_lowjac_safe`).

## Batch `westlaw-pdfocr-residue-2026-05-18` (30 rows)

Closes the 10 non-promoted residue from `westlaw-receive-2026-05-18`, resolving each by its **unique neutral cite** (the N.W.2d primary cite was non-unique — shared 2018–19 disposition pages — and the parser extracted no `date_filed` from these PDF-era docs, which is why automated name+date resolution went AMBIGUOUS).

- **Group A — 8 explicit-oid promotions** (Gardner 2019 ND 122/19351, Lee 2019 ND 142/19357, Hollis 2019 ND 163/19362, T.A.G. 2019 ND 167/19363, Wills 2019 ND 176/19367, Facio 2019 ND 199/19370, TigerSwan 2019 ND 219/19375, Holter 2020 ND 202/19516): neutral cite → exactly one oid, then the tested `receive_westlaw._promote` (jaccard 0.82–0.91 vs prior OCR text — same opinion, clean Westlaw bound text now primary).
- **Group B — 2 hand-verified manual promotions** (Neset 1998 ND 206/12782, Richardson 2020 ND 246/19532): `_parse_westlaw_doc` extracted no body (ORDER-of-Reinstatement format; minimal per-curiam N.D.R.App.P. 35.1 memo). Both read in full and confirmed genuine complete opinions; oid certain via unique neutral cite. Promoted with the Westlaw footer (`All Citations`/`End of Document`/© Thomson Reuters) stripped per redistribution scope. The `_promote` jaccard gate was deliberately bypassed (it guards *automated* shared-page mis-resolution — moot for a hand-verified explicit-oid promote); prior jaccard recorded in the changelog authority note (Neset 0.017 — DB text was unusable garbled scanned-OCR; Richardson 0.425).
- **Result**: all **41/41** mandatory-OCR worklist opinions now carry a Westlaw source and ≥2 sources. 30 changelog rows (10 × text_content+source_reporter+source_path), authority-stamped. Docs archived to the correct reporter trees (`N.W.2d/<vol>/`, `N.W.3d/<vol>/`).
- **Safety**: snapshot `opinions.db.bak-pre-pdfocr-residue-2026-05-18`. Revert: `cleanup revert westlaw-pdfocr-residue-2026-05-18` then `align_primary_source --apply`. Invariants 18 ok / 2 known / 0 regressed.

## Batch `westlaw-receive-2026-05-18` (93 rows)

PDF-era second-source closure. Under the ratified PDF-era policy (TODO §9), opinions whose court PDF is a page-image scan (text required OCR) and that lack an independent second source must get a Westlaw copy. The detector (`triage/classify_pdf_extraction.py`, structural: ~1 full-page raster per page = scanned) flagged 41 such opinions (`triage/westlaw-pdf-ocr-worklist-2026-05-18.md`); user pulled them via Westlaw Find&Print.

- **Tool**: `python -m ndcourts_mcp.receive_westlaw --incoming … --apply`.
- **Result**: 41 docs → **31 promoted** (Westlaw bound text now primary, clean text replacing scanned OCR; matched to existing oids by neutral cite, jaccard 0.45–0.89), **0 created**, 8 AMBIGUOUS + 1 LOW_SIM (oid 12782 *Neset* 1998 ND 206, jaccard 0.01 — near-empty scanned-memo DB text) + 1 skipped memo, all held unwritten for a later neutral-cite-keyed pass. 93 changelog rows (31 × text_content+source_reporter+source_path), authority-stamped.
- **Code fix (committed)**: `receive_westlaw._archive_doc` hardcoded the `N.W.2d/` archive tree; PDF-era pulls carry `N.W.3d`. Made it reporter-series-aware (`N.W.3d`/`N.W.2d`/`N.W.` by parsed series). **Process note:** the first fix had a regex-group mismap (volume read as series) that archived all 31 to bogus `N.W.2d/2d|3d/` dirs with page-collisions; caught immediately by source_path verification, reverted via snapshot `opinions.db.bak-pre-westlaw-pdfocr-2026-05-18` (atomic, nothing else since), bogus dirs purged, group mapping fixed, re-applied clean. Net DB effect = the clean re-run only.
- **Safety**: snapshot `opinions.db.bak-pre-westlaw-pdfocr-2026-05-18`. Revert: `cleanup revert westlaw-receive-2026-05-18` then `align_primary_source --apply`. Invariants 18 ok / 2 known / 0 regressed.

## Batch `lukenbill-19966-2026-05-18` (3 rows)

*Northstar Center v. Lukenbill Family Partnership* (oid 19966, `2024 ND 212`) — hand-adjudicated substituted-opinion case. Westlaw returned two docs for the citation: original `14 N.W.3d 45` (filed 2024-11-21) and **substituted `17 N.W.3d 1`** (filed 2025-01-24, after rehearing denied 2025-01-22; its header states "Opinion, 14 N.W.3d 45, superseded"). Normalized-body comparison: 0.947 — same opinion with internal substantive revisions (¶15–17 note/breach reasoning; +1 ¶ at the merger-doctrine/indemnification disposition), **not** an appended rehearing opinion. Decision (user): keep only the substituted opinion as authoritative; no second row.

- `date_filed` 2024-02-14 → **2024-11-21** (original announcement date; the prior value was a scraper docket-collision artifact, docket 20240034; ND practice: a substituted opinion retains the original cite/decision date).
- `notes` set to the full supersession chain (original 14 N.W.3d 45 2024-11-21; rehearing denied 2025-01-22; substituted 2025-01-24 17 N.W.3d 1; neutral 2024 ND 212 retained throughout).
- Added parallel citation `17 N.W.3d 1` (`NW3d`, non-primary); neutral `2024 ND 212` remains `is_primary`. Text/source promoted via the `westlaw-receive-2026-05-18` batch (jaccard 0.89).
- **Safety**: same snapshot. Revert: `cleanup revert lukenbill-19966-2026-05-18`. Invariants 18 ok / 2 known / 0 regressed.

## Batch `reporter-taxonomy-2026-05-17` (15,029 rows)

Applied SCHEMA.md Contract 1: migrated `citations.reporter` to the closed taxonomy and deleted foreign cross-refs mis-scraped into `citations`.

- **Tool**: `python -m ndcourts_mcp.migrate_reporter_taxonomy --apply` (reclassifies every row from its citation *string* via the rewritten `ingest._classify_reporter`, so it is idempotent and string-driven, not old-value-driven).
- **Result**: 14,568 reporter reclassifications + 461 row deletions. Transitions: `ND`→`ND-neutral` 7,444; `NDold`→`ND` 6,676; misfiled `A.L.R.` (from NW/NW2d) → `ALR` 300; `L.R.A.` → `LRA` 69; 79 prior-NULL resolved (→NW2d 68, →ND 6, →NW 5). Post-state distribution: NW2d 12,049 / ND-neutral 7,444 / ND 6,682 / NW 6,034 / ALR 300 / LRA 69; **0 NULL, 0 out-of-taxonomy**. No `US`/`SCT`/`LED` rows — those reporters appear only in opinion text (`text_citations`), never as a parallel cite row.
- **461 deletions (user-ratified)**: rows whose citation string is a foreign/specialty reporter outside the entire Contract-1 universe (South Western `157 S.W. 811`, American State Reports `125 Am. St. Rep. 608`, A.F.T.R., Oil & Gas Rep., L.R.R.M.) — mis-scraped cross-references that belong in `text_citations`, not `citations`. Guard verified **0** were the sole citation of any opinion (no orphaning). Snapshot is the real revert; each delete also logged to `changelog` (`field='citations.delete'`, old_value=citation) for the audit trail.
- **Code (lockstep, Contract-1 enum)**: rewrote `ingest._classify_reporter` (adds A.L.R./L.R.A./U.S./S.Ct./L.Ed. detection, NW3d; renames NDold→ND, ND→ND-neutral; no longer falls back to `source_reporter`); updated consumers `audit_sources`, `backfill_sources` (path test only — `:139`/`:173` source_reporter untouched), `audit`, `quality_scan:228`, `webapp` (cite-selection), `ingest_westlaw:780`, and the citation-INSERT paths (`scrape_archive`, `receive_westlaw`, `insert_supplemental_opinions`, `ingest_nwcite`) now classify + call `recompute_primary`. All `source_reporter` logic deliberately left untouched (independent axis).
- **Safety**: pre-batch snapshot `opinions.db.bak-pre-reporter-contract-2026-05-17`. Revert via snapshot (row deletes are not changelog-replayable). Corpus citations 33,039 → 32,578.

## Batch `is-primary-recompute-2026-05-17` (24,183 rows)

Applied SCHEMA.md Contract 2: recomputed `citations.is_primary` for every opinion per the selection ladder.

- **Tool**: `python -m ndcourts_mcp.recompute_is_primary --apply` (single transaction; `ingest.recompute_primary` per opinion).
- **Ladder**: `ND-neutral` > `ND` > `NW3d` > `NW2d` > `NW`; ties → lowest citation id; `ALR`/`LRA`/`US`/`SCT`/`LED` never primary; exactly one `is_primary=1` per opinion.
- **Result**: 24,183 is_primary flips across 11,978 of 20,229 opinions (fixes the prior 817 multi-primary AND the systemic "regional primary instead of official" — post-1997 N.W.2d→neutral, pre-1997 official N.D. Reports promoted over N.W.). Spot-checked: oid 9485 `1998 ND 13` (ND-neutral) primary over `375 N.W.2d 203`; oid 1 `13 N.D. 359` (ND) primary over `100 N.W. 1079` (NW). Post-state: **0 multi-primary, 0 zero-primary, 0 secondary-primary**.
- **Invariants**: added `citation_single_primary_per_opinion`, `reporter_in_taxonomy`, `secondary_never_primary` (all OK at 0). Dashboard: **18 ok, 2 at known baseline (neutral_cite_uniqueness 258, nd_modern_paragraph_markers 85), 0 regressed**. `align_primary_source` dry-run: 0 changes (source-provenance axis undisturbed — confirms axis independence).
- **Safety**: same snapshot `opinions.db.bak-pre-reporter-contract-2026-05-17`. Revert: `cleanup revert is-primary-recompute-2026-05-17`.

## Batch `strip-westlaw-headnotes-2026-05-15` (186 rows)

Corrective scope sweep: removed Westlaw editorial (West Headnotes block, "Procedural Posture(s)" lines, Synopsis stub) that leaked into `text_content` during this session's Westlaw ingests — content the redistribution scope (`NOTICE.md`) excludes. Caught by the pre-release scope scan before any public release.

- **Root cause**: `ingest_westlaw._is_section_header` exact-matched section names, but modern Westlaw writes "West Headnotes (20)" with a headnote count, so the `West Headnotes` DROP never fired on modern-format docs → the editorial block + Synopsis stub + Procedural Posture leaked. Fixed forward in `_is_section_header` (strips a trailing `(N)` before the membership test).
- **Tool**: `python -m ndcourts_mcp.strip_westlaw_headnotes --apply`
- **Rule**: surgically excise the `West Headnotes …` block (header line through the next court-authored boundary — Syllabus by the Court / Syllabus / Attorneys and Law Firms / Opinion / author / PER CURIAM), drop `Procedural Posture(s):` lines, and re-run the existing tested `strip_synopsis_editorial` for the Synopsis stub. Court-authored Synopsis narrative and the court's "Syllabus by the Court" are preserved (verified on oid 6404: West Headnotes [1]–[20] removed, Syllabus by the Court + Opinion intact).
- **Result**: 186 rows stripped (all westlaw-sourced), 0 unchanged, 0 flagged-incomplete. Full-corpus re-scan: **West Headnotes 0, Procedural Posture(s) 0, Thomson Reuters 0, KeyCite 0**. Corpus row count unchanged (20,486). 186 changelog rows (1 text_content each), full prior text retained for revert.
- **Process note**: first apply rolled back on a stale-key f-string error before commit (no DB change); fixed and re-applied clean.
- **Safety**: pre-batch snapshot `opinions.db.bak-pre-strip-headnotes-20260515_213944`. Revert: `cleanup revert strip-westlaw-headnotes-2026-05-15`. Invariants: 13 ok, 2 known, 0 regressed.

## Batch `westlaw-queue-clearwins-2026-05-15` (15 rows)

Conservative "clear wins" pass over the 98 `westlaw-receive-2026-05-15` AMBIGUOUS docs. Promotes only where the Westlaw doc's distinctive party surname uniquely identifies exactly one cleaned-cite candidate that is not part of a duplicate pair and clears the 0.20 jaccard floor.

- **Tool**: `python -m ndcourts_mcp.resolve_westlaw_clearwins --apply`
- **Result**: 5 promoted (Guardianship of Frank `137 N.W.2d 218`→6450; Transportation Div. v. Sandstrom `337 N.W.2d 160`→8950; State Bank v. Patten `357 N.W.2d 239`→9252; Gange `429 N.W.2d 429`→10212; First Nat'l Bank v. Jacobsen `431 N.W.2d 284`→10255), jaccard 0.79–0.91. 93 deferred (0 dup, 0 low-sim, 93 unclear — the classifier is deliberately strict; many human-obvious ones, e.g. Sletten→11968, defer due to a brittle doc-lookup string match, a known limitation to widen later).
- **Changelog rows**: 15 = 5 × (text_content + source_reporter + source_path), authority-stamped. Each `.doc` archived to `~/refs/nd/opin/N.W.2d/{vol}/{page:04d}-{slug}.doc`.
- **Process note**: first apply used a placeholder source_path (broke `source_files_on_disk`); snapshot-restored, fixed to call the real `_archive_doc`, re-applied. Invariants: 13 ok, 2 known, 0 regressed.
- **Safety**: pre-batch snapshot `opinions.db.bak-pre-clearwins-20260515_210455`. Revert: `cleanup revert westlaw-queue-clearwins-2026-05-15` then `align_primary_source --apply`.

## Batch `westlaw-receive-2026-05-15` (971 rows)

Ingested the manual Westlaw Find & Print returns for the gap-era worklist (batches 1–4 + the non-unique resolution passes; 425 docs). Westlaw bound is the highest authority for the 1953–1996 era.

- **Tool**: `python -m ndcourts_mcp.receive_westlaw --apply`
- **Source**: `~/refs/nd/opin/westlaw-incoming/2026-05-15/` (8 Westlaw Precision zips/doc); each `.doc` archived to `~/refs/nd/opin/N.W.2d/{vol}/{page:04d}-{slug}.doc` (parallel to bound `N.D./`).
- **Resolution** (final, after three bug fixes — see history): cite match with the trailing Westlaw `(Mem)`/`(Table)` suffix stripped; a candidate is accepted only if it AGREES on cleaned caption OR filing date OR ≥0.45 text-jaccard (a lone cite candidate is not enough — shared reporter pages put a different opinion at the same cite). Two-phase: classify all docs read-only against the original DB, then a reconcile pass (at most one doc may promote a given row; extra docs resolving to the same row are demoted to create as distinct companions), then apply. Sub-0.20 jaccard MATCH still flags rather than overwrites.
- **Result**: 317 promoted to Westlaw-authoritative text; 10 created (genuine Type-Y companions: Mittelstadt, Reimers Seed Co. [Ct. App.], Larson disc., Williston/Bismarck/Rugby/Washburn vacancies, McMahon, Lawson, Berger [Ct. App.]); 98 ambiguous (multi-party estate/guardianship/juvenile + formulaic judicial-vacancy captions on same-date shared pages) reported for manual review; 0 low-sim, 0 parse errors, 0 created-vs-existing duplicates, 0 double-promotes. Corpus 20,476 → 20,486.
- **Changelog rows**: 971 = 317 × (text_content + source_reporter + source_path) + 10 × (opinions.insert + citation), authority-stamped `Westlaw bound (Find&Print, <cite>)`.
- **Bug history (3 fixes; each prior apply snapshot-restored, none committed)**: (1) in-run ordering — early creates exposed rows to later shared-page docs; fixed via two-phase. (2) `(Mem)` citation suffix prevented matching existing rows → ~46 duplicate creates; fixed by `_clean_cite`. (3) lone-cite candidate auto-matched without agreement → 5 shared-page rows double-promoted (companion text loss); fixed by agreement scoring + reconcile. Final apply verified: apply == dry-run, created (10) == single_source_accepted (10), 0 double-promote, 0 dup-create, invariants 0 regressed.
- **Known residual (manual queue)**: formulaic judicial-vacancy orders on shared pages are heuristically inseparable; ~1 (522 N.W.2d 747 "Judgeship No. 9 Washburn") created where it should promote onto existing oid 11762, plus the formulaic-vacancy creates, are routed to the manual review list for adjudication. The 98 ambiguous are the broader manual queue.
- **Safety**: pre-batch snapshot `opinions.db.bak-pre-westlaw-receive-20260515_202453`. Revert with `python -m ndcourts_mcp.cleanup revert westlaw-receive-2026-05-15` then `python -m ndcourts_mcp.align_primary_source --apply` (the 10 created rows need manual DELETE). Invariants: 13 ok, 2 known, 0 regressed.

## Batch `court-archive-gap-create-2026-05-15` (114 rows)

Created 57 opinions that exist in the court-sourced NW-cite archive but were entirely absent from the corpus (the §2 gap candidates), after triage narrowed 292 raw candidates to the genuinely-addable set.

- **Tool**: `python -m ndcourts_mcp.ingest_nwcite --create-gap --apply`
- **Triage of the 292**: text-containment identity check (not fuzzy names) found only 4 already present; of the 288 missing, 235 were shared-cite disposition/table pages (not opinions → manual-review queue, `triage/court-archive-shared-cite-pages-2026-05-15.md`), leaving 57 unique-cite genuine opinions.
- **Scope** (decided 2026-05-15): create all 57 — 12 ND Supreme Court substantive + 6 ND Supreme Court short summary dispositions + **39 ND Court of Appeals** (corpus scope expanded to include the Court of Appeals as a distinct `court` value).
- **Result**: 57 new opinions (18 `court='North Dakota Supreme Court'`, 39 `court='North Dakota Court of Appeals'`). Each: court-archive primary source, frontmatter built from the court page (date_filed from the page's "Filed" meta — 100% coverage, three independent signals), citations, `validation_status='single_source_accepted'`. Corpus 20,419 → 20,476.
- **Changelog rows**: 114 = 57 `opinions.insert` + 57 `citation`, authority-stamped.
- **Safety**: pre-batch snapshot `opinions.db.bak-pre-gap-create-20260515_192344`. NOTE: `cleanup revert` does not auto-undo row creation — reverting this batch requires `DELETE FROM opinions WHERE id IN (…)` for the 57 (or restore the snapshot). Invariants: 13 ok, 2 known, 0 regressed.

## Batch `court-archive-containment-rescue-2026-05-15` (3,009 rows)

Containment-rule rescue of the 1,018 `manual_outlier` opinions the `court-archive-promote-2026-05-15` ratio gate flagged rather than auto-promoting. Triage showed these were not "court worse" but **CourtListener self-duplicated `text_content`** (the opinion duplicated within the row), with the court-archive text as the single clean canonical copy.

- **Tool**: `python -m ndcourts_mcp.ingest_nwcite --rescue-flagged --apply`
- **Rule** (approved 2026-05-15, extends the promotion policy): promote when court-text shingle-containment in the DB body ≥ 0.85 AND the DB shows the caption-duplication signature (first-8-words recur ≥ 2×, unique-extra fraction < 0.55). Containment ≥ 0.85 guarantees the court text is neither truncated nor a distinct second opinion, so the DB "extra" is duplicated content and the swap loses nothing unique.
- **Result**: 1,003 promoted (CL self-duplication corrected, court-authoritative text + syllabus recovered); 7 kept flagged as `court-source-truncated` (court page itself incomplete, DB is the full opinion — court-archive re-scrape item); 8 left flagged (clean-contained without the duplication signature / 2 divergent — manual).
- **Changelog rows**: 3,009 = 1,003 × (text_content + source_reporter + source_path), authority-stamped `court-archive (archive.ndcourts.gov NW-cite)`.
- **Finding**: ~1,003 gap-era CL opinions had self-duplicated body text — a concrete upstream CourtListener data defect, recorded for the deferred CL-feedback objective. Triage: `triage/court-archive-flagged-triage-2026-05-15.md`.
- **Safety**: pre-batch snapshot `opinions.db.bak-pre-containment-rescue-20260515_155121`. Revert with `python -m ndcourts_mcp.cleanup revert court-archive-containment-rescue-2026-05-15` then `python -m ndcourts_mcp.align_primary_source --apply`. Invariants: 13 ok, 2 known, 0 regressed.

## Batch `court-archive-promote-2026-05-15` (15,910 rows)

Promoted `text_content` to the court-sourced archive.ndcourts.gov NW-cite text for opinions whose primary was CourtListener OCR (NW2d/NW), closing most of the 1953–1996 single-source gap with a court-authoritative source.

- **Tool**: `python -m ndcourts_mcp.ingest_nwcite --apply`
- **Source**: `archive.ndcourts.gov/opinions/cite/NWcite.htm` → `~/refs/nd/opin/court-archive/<vol>/<id>.htm` (787 N.W.2d vols indexed; gap-era vols 139–560 mirrored, 5,344 opinion pages).
- **Policy** (approved 2026-05-15): gate is the length ratio = court_body / db_body (frontmatter stripped); jaccard is informational. ratio ∈ [0.95, 1.60] → auto-promote (body swapped, YAML frontmatter preserved verbatim, primary repointed); [0.80,0.95)∪(1.60,2.50] → review band (flagged); <0.80 or >2.50 → manual outlier (flagged); non-CL primary (ndcourts.gov/westlaw, 1997+) → cross-check only, never demoted.
- **Result**: 3,710 promoted (recovers official "Syllabus by the Court" pre-~1978 and caption/procedural front-matter throughout, strips CL OCR artifacts); 1,049 flagged for review (1,018 manual-outlier, 11 review-band, 10 shared-cite-ambiguous Type-Y, 10 non-CL-divergent); 31 non-CL cross-checked; 292 unmatched gap candidates deferred (`triage/court-archive-gap-candidates-2026-05-15.md`).
- **Changelog rows**: 15,910 = 3,710 × (text_content + source_reporter + source_path) + 4,780 court-archive source attachments. All authority-stamped `court-archive (archive.ndcourts.gov NW-cite)`.
- **Why**: the court archive is court-authoritative and was never shorter than the CL OCR it replaces in a 1965–1998 sample — a corpus upgrade toward the authoritative-text bar, not merely a cross-check.
- **Safety**: pre-batch DB snapshot at `opinions.db.bak-pre-court-archive-promote-20260515_115623`. Revert with `python -m ndcourts_mcp.cleanup revert court-archive-promote-2026-05-15` then `python -m ndcourts_mcp.align_primary_source --apply` (re-syncs `opinion_sources.is_primary`). Invariants: 13 ok, 2 known, 0 regressed.

## Batch `strip-westlaw-synopsis-2026-05-13` (5,733 rows)

Removed the Westlaw editorial "Synopsis" stub and any "The Supreme Court, J., held that..." holding summary from `text_content` of all westlaw-sourced opinions. Court-authored narrative within Synopsis sections (the court's published statement of facts in older bound entries) is preserved.

- **Tool**: `python -m ndcourts_mcp.strip_westlaw_synopsis --apply`
- **Coverage**: 5,738 westlaw-sourced rows with a `Synopsis` header → 5,320 had only the editorial stub (full section dropped); 413 had court narrative after the stub (stub stripped, narrative preserved); 5 had only court-authored cross-reference content (left unchanged).
- **Why**: aligns the redistributed `text_content` with the project's scope of court-authored opinions and court-authored syllabi only. See [`NOTICE.md`](NOTICE.md). Westlaw's case-report content (court of origin, attorneys, disposition) is factual and not copyrightable per *Matthew Bender & Co. v. West Publishing*, 158 F.3d 674 (2d Cir. 1998), but it is also not the court's own work and falls outside the project's redistribution scope.
- **Forward-compat**: `ingest_westlaw._parse_westlaw_doc` now calls the stripper on every newly-ingested `.doc`, so future ingests cannot reintroduce the editorial content.
- **Safety**: pre-batch DB snapshot at `opinions.db.bak-pre-strip-synopsis-2026-05-13`. Revert with `python -m ndcourts_mcp.cleanup revert strip-westlaw-synopsis-2026-05-13`.

## Batch 00: Metadata merge (not in changelog — additive only)

- **Source**: `~/refs/nd/opin/*_opinions.json` (scraped from ndcourts.gov)
- **Scope**: 7,153 opinions (1997–2026)
- **Fields updated**: case_name, date_filed, author, case_type, highlight, voting_record, all_justices, unanimous, opinion_url, docket_number, judges, per_curiam
- **Applied by**: `python -m ndcourts_mcp.merge_nd_metadata`

## Batch 01: Case normalization (4,827 rows)

Normalized ALL CAPS author names from CourtListener's older metadata to title case. Consolidated VandeWalle variants. Fixed a few OCR misreads where the correct name was unambiguous (CRIMSON→Grimson, MAKING→Maring).

| From | To | Count |
|------|----|-------|
| WALLE | VandeWalle | 810 |
| ERICKSTAD | Erickstad | 727 |
| MESCHKE | Meschke | 513 |
| LEVINE | Levine | 483 |
| GIERKE | Gierke | 343 |
| SAND | Sand | 316 |
| PEDERSON | Pederson | 314 |
| PAULSON | Paulson | 212 |
| NEUMANN | Neumann | 189 |
| SANDSTROM | Sandstrom | 187 |
| BURKE | Burke | 62 |
| MARING | Maring | 58 |
| TEIGEN | Teigen | 66 |
| VOGEL | Vogel | 90 |
| STRUTZ | Strutz | 55 |
| JOHNSON | Johnson | 55 |
| MORRIS | Morris | 54 |
| CHRISTIANSON | Christianson | 33 |
| NUESSLE | Nuessle | 30 |
| Vande Walle | VandeWalle | 30 |
| KAPSNER | Kapsner | 37 |
| BURR | Burr | 26 |
| BIRDZELL | Birdzell | 25 |
| GRIMSON | Grimson | 20 |
| SATHRE | Sathre | 19 |
| CROTHERS | Crothers | 8 |
| BiRdzell | Birdzell | 7 |
| CRIMSON | Grimson | 7 |
| VANDEWALLE, VandeWALLE, Vandewalle | VandeWalle | 9 |
| Vande Walle Cmef, Vande Vande Walle, De Walle, YANDEWALLE, Walle, WÁLLE | VandeWalle | 8 |
| MAKING | Maring | 4 |
| ER1CKSTAD, EKICKSTAD | Erickstad | 2 |
| LEYINE | Levine | 1 |
| PEDERuON | Pederson | 1 |
| BuRR | Burr | 1 |
| BiRDZELL, BlRDZELL | Birdzell | 2 |
| SATURE | Sathre | 4 |
| TKIGEN, TLIGEN | Teigen | 2 |
| BRUCE, BUTTZ, COLE, COOLEY, SWENSON, WOLFE, KNEESHAW, KONENKAMP, McKENNA, MOELLRING, JANSONIUS, GEN, PUGH, KNUDSON | title case | 1–3 each |

## Batch 02: Birdzell OCR variants (423 rows)

OCR misreads of "Birdzell" from NW/NW2d scanned opinions, all within Luther E. Birdzell's 1918–1933 tenure. 100+ distinct misspellings consolidated.

Top variants by count:

| From | Count |
|------|-------|
| Biedzell | 72 |
| Bikdzell | 65 |
| Bibdzell | 26 |
| Birdzbll | 17 |
| Birdzele | 17 |
| Birdzeel | 12 |
| Birdzeix | 12 |
| Biruzell | 12 |
| Birbzell | 9 |
| Birdzelu | 8 |
| Birdzull | 7 |
| Birdzehl | 5 |

Plus ~90 variants with 1–4 occurrences each.

**Excluded** (need further investigation):
- Bhucb (1914) — before Birdzell's tenure, likely Bruce
- Bmuzei (1917) — judges field shows separate justice from Birdzell

## Batch 03: Bronson OCR variants (76 rows)

OCR misreads of "Bronson" from NW scanned opinions, all within Harrison A. Bronson's 1918–1924 tenure.

| From | Count |
|------|-------|
| Beonson | 51 |
| Bbonson | 13 |
| Beokson | 3 |
| BeoNSON | 2 |
| Beohson | 1 |
| Beoiyson | 1 |
| BeoNsoN | 1 |
| Beonsou | 1 |
| BeoxsoN | 1 |
| Bkonson | 1 |
| Broxkon | 1 |

## Batch 04: Bruce OCR variants (33 rows)

OCR misreads of "Bruce" from NW scanned opinions, all within Andrew A. Bruce's 1912–1918 tenure.

| From | Count |
|------|-------|
| Bbuce | 12 |
| Beuce | 11 |
| Beucb | 3 |
| Beuoe | 2 |
| Bhucb | 1 |
| Bruoe | 1 |
| Bsuce | 1 |
| Beugb | 1 |
| Brtjoe | 1 |

## Batch 05: Burke OCR variants (185 rows)

OCR misreads of "Burke" spanning all three Burke tenures (Edward T. 1911–1916, John 1919–1937, Thomas J. 1951–1966). 44 distinct misspellings.

Top variants:

| From | Count |
|------|-------|
| Bure | 23 |
| Burice | 20 |
| Bueke | 17 |
| Buee | 10 |
| Bubke | 9 |
| Buekb | 9 |
| Bueice | 8 |
| Burk | 8 |
| Bukke | 7 |
| Bukr | 7 |
| Buer | 7 |
| Burnt | 6 |

Plus 32 variants with 1–4 occurrences each.

## Batch 05b: Context-verified fixes (3 rows)

Corrections identified by examining the judges field to determine which justice was missing from the panel.

| From | To | Date | Reasoning |
|------|----|------|-----------|
| Nubs | Nuessle | 1924 | Judges field missing Nuessle; other panel members accounted for |
| Nubsslb | Nuessle | 1947 | Judges field missing Nuessle; other panel members accounted for |
| Bums | Burr | 1929 | Judges field missing Burr; other panel members accounted for |

## Batch 06: Misc justice OCR variants (276 rows)

Consolidated OCR misreads for multiple justices, plus full-name → last-name normalization for surrogate judges.

| Justice | Variants corrected | Rows |
|---------|--------------------|------|
| Christianson | Cheistianson, Ci-Iristianson, Christian, + 18 more | ~35 |
| Fisk | Eisk, Fisic, Bisk, Pisk, Pise, Rise, Risk, Fise, Eisic | ~50 |
| Robinson | Bobinson, Eobinson | ~18 |
| Birdzell | Bird (truncated) | 18 |
| Johnson | Joiinson, Joi-Inson, Jonnson, Jonxson, Jorinson, Johrson | ~15 |
| Grimson | Crimson, Geimson, G-Rimson, + 5 more | ~14 |
| Erickstad | Erick, Erick-Stad, Ralph J. Erickstad, + 4 more | ~18 |
| Nuessle | Ntjessle, Nubssle, Nuessee, + 14 more | ~25 |
| Sathre | Sature, Satiire, Satpire, Sathke | ~10 |
| Morris | Moréis, Mórris, Mortus, Morjris, Mobbis, M'Orris, Norris | ~10 |
| Spalding | Spalning, Spauding, Spálding | ~4 |
| Wallin | Walltn, Wali | ~3 |
| Teigen | Teígen | 1 |
| Ellsworth | Ellsworti | 1 |
| Burke | Bubkb | 3 |

Full-name surrogates normalized: Adam Gefreh→Gefreh, Beryl J. Levine→Levine, Clifford Jansonius→Jansonius, Clifford Schneller→Schneller, Eugene A. Burdick→Burdick, Hamilton E. Englert→Englert, Harry E. Rittgers→Rittgers, James H. O'Keefe→O'Keefe, Ralph B. Maxwell→Maxwell, William F. Hodny→Hodny, Douglas B. Heen→Heen, A. C. Bakken→Bakken.

## Batch 06b: Per curiam corrections (30 rows)

OCR-mangled "Per Curiam" labels set to author→NULL, per_curiam→1.

Variants: Cueiam (12), Oueiam (3), Pee (3), Per Curiam (2), Cubiam, Cuetam, Cuexam, Cukiam, Curium, Curriam, Curtam, Oubiam, Ourtam, Ourxam (1 each).

## Batch 06c: Stragglers (4 rows)

Case normalization missed in batch 01: ENGLERT→Englert (2), Engleet→Englert (2).

## Batch: manual-review (8 rows)

"Chas" opinions reviewed interactively via `review.py` (2026-04-04). "Chas" was a fragment from "CHAS. A. POLLOCK" or "CHAS. FISK" (Charles Fisk) in the disqualification boilerplate. True authors identified from "LastName, J." lines in the opinion text.

## Batch: westlaw-batch1 (13 rows)

46 pre-1920 opinions downloaded from Westlaw Quick Check and compared via `ingest_westlaw.py`. Applied 2026-04-05.

**10 author corrections:**

| Citation | Old (DB) | New (Westlaw) |
|----------|----------|---------------|
| 38 N.D. 499 (Beauchamp) | Bruce | Christianson |
| 44 N.D. 89 (Gray v. Gray) | Birdzell | Christianson |
| 38 N.D. 425 (Hope Nat. Bank) | Robinson | Grace |
| 44 N.D. 111 (Livingston) | Birdzell | Robinson |
| 22 N.D. 251 (Morrison v. Lee) | Crawford | Fisk |
| 31 N.D. 504 (Ramstad v. Carr) | Buttz | Christianson |
| 44 N.D. 5 (Sandvig v. Kleppe) | Crace | Grace |
| 14 N.D. 501 (State v. Harris) | Any | Morgan |
| 41 N.D. 55 (State v. Hiertz) | Birdzell | Grace |
| 41 N.D. 599 (Vanevery) | Grace | Robinson |

**3 date corrections:**

| Citation | Old (DB) | New (Westlaw) | Note |
|----------|----------|---------------|------|
| 11 N.D. 376 (Brandrup v. Britten) | 1903-07-01 | 1902-11-24 | Placeholder date |
| 14 N.D. 445 (Hanson v. Skogman) | 1905-10-02 | 1905-10-10 | 8-day discrepancy |
| 11 N.D. 458 (Ross v. Page) | 1903-07-01 | 1902-12-10 | Placeholder date |

**3 case name diffs skipped:**
- Fargo & S W R Co. v. Brewer (Westlaw) vs Fargo & Southwestern Ry. Co. v. Brewer (DB) — DB has better expanded form, kept DB
- Murphy v. District Court (Westlaw) vs State v. Poull (DB) — both opinions share citation 14 N.D. 557 with different N.W. parallel cites (105 N.W. 717 for Poull, 105 N.W. 734 for Murphy). Both exist in DB as separate records. However, both opinions span multiple N.W. pages — unlikely they truly share the same N.D. start page. Flagged in `notes` field on both records (ids 146, 152) for manual verification.
- Phoenix case name handled in ligature normalization batch below

## Batch: westlaw-batch1-casenames (6 rows)

Normalized Unicode ligatures (Æ, œ) to plain ASCII in case names. These are OCR artifacts from old typesetting that interfere with search. Applied 2026-04-05.

| ID | Old | New |
|----|-----|-----|
| 799 | Boos v. Ætna Insurance | Boos v. Aetna Insurance |
| 2835 | Coughlin v. Ætna Life Insurance | Coughlin v. Aetna Life Insurance |
| 3593 | Wenstrom v. Ætna Life Insurance | Wenstrom v. Aetna Life Insurance |
| 3868 | Pipan v. Ætna Insurance | Pipan v. Aetna Insurance |
| 5487 | Red River Lumber Co. v. Children of Isræl | Red River Lumber Co. v. Children of Israel |
| 5499 | Phœnix Assurance Co. v. McDermont | Phoenix Assurance Co. v. McDermont |

## Batch: auto-author-text (257 rows)

Auto-detected real authors from "LastName, J." / "LastName, C. J." / "LastName, District Judge." lines in opinion text. Applied 2026-04-05 via `python -m ndcourts_mcp.auto_author --apply`.

These opinions had junk-word authors (Being, Been, Dist, Action, etc.) or OCR garbles from CourtListener's broken judge-field parsing. The script scans the first 3000 chars of the opinion body for the authorship line pattern.

Top corrections by old author:

| Old author | Recovered as | Count |
|------------|-------------|-------|
| Being | Fisk, Bruce, Spalding, Robinson, Morgan, Burke, Christianson, Goss, Birdzell, Grace, Bronson, others | 126 |
| Been | Young, Morgan, Corliss, Wallin, Fisk, Spalding, Birdzell | 30 |
| Other | Wallin | 6 |
| Any | Corliss, Bartholomew, Young, Wallin, Spalding, Goss | 11 |
| Account | Spalding, Fisk, Carmody | 8 |
| Action | Young, Morgan, Bruce, Spalding, Grace | 6 |
| Below | Burke, Bruce, Fisk, Pollock | 6 |
| + 70 more single/double-count mappings | various | 64 |

Also corrected OCR garbles: Bartxiolomew→Bartholomew, Engertjd→Engerud, Engebud→Morgan, Moelxjring→Moellring, Birdzeell→Robinson, and others.

## Schema change: notes column (2026-04-05)

Added `notes TEXT` column to the `opinions` table for flagging records that need manual investigation. Used to flag the shared 14 N.D. 557 citation between State v. Poull (id=146) and Murphy v. District Court (id=152).

## Batch: westlaw-nd-vol1-2 (6 rows, 1 reverted)

Complete Westlaw download of volumes 1–2 N.D. Reports (118 opinions, 1890–1892). Compared against DB via `ingest_westlaw.py`. Applied 2026-04-05. Source files saved to `~/refs/opin/N.D./vol1-2/`.

**3 author corrections:**

| Citation | Old | New |
|----------|-----|-----|
| 1 N.D. 143 (Devore v. Woodruff) | Been | Corliss |
| 1 N.D. 159 (Short v. Northern Pac. Elevator) | Bartholomew | Wallin |
| 1 N.D. 121 (Bode v. New England Inv. Co.) | Corliss | Wallin |

**2 date corrections (1 reverted):**

| Citation | Old | New | Note |
|----------|-----|-----|------|
| 2 N.D. 310 (Northern Pac. R. Co. v. Barnes) | 1892-01-12 | 1892-01-21 | |
| 2 N.D. 30 (Mills v. Howland) | 1891-06-07 | 1891-07-07 | |
| 2 N.D. 397 (Cleary v. County of Eddy) | 1892-02-09 | 1892-01-12 | **Reverted** — citation collision with Tressler; wrong opinion matched |

**3 not found in DB:** Clark v. Sullivan (2 N.D. 103), Bowne v. Wolcott (1 N.D. 497), State ex rel. Ohlquist v. Swan (1 N.D. 5)

**2 citation collisions flagged:** Cleary/Tressler at 2 N.D. 397 (different N.W. cites: 51 N.W. 586 vs 51 N.W. 787). Notes added to both records.

## Batch: westlaw-nd-vol1-2-casenames (8 rows)

Genuine spelling corrections identified by comparing Westlaw case names with DB. Applied 2026-04-05.

| Old | New |
|-----|-----|
| O'Hara v. Town of Park River | O'Hare v. Town of Park River |
| Garr, Scott & Co. v. Spaulding | Garr, Scott & Co. v. Spalding |
| Brathwaite v. Aikin | Braithwaite v. Aikin |
| Linton v. Minnepolis & Northern Elevator Co. | Linton v. Minneapolis & Northern Elevator Co. |
| Power v. Larabee (2 records) | Powers v. Larabee |
| State ex rel. Faussett v. Harris | State ex rel. Fausett v. Harris |
| State ex rel. Goodsill v. Woodmansee | State ex rel. Goodsill v. Woodmanse |

## Batch: westlaw-nd-vol3-4 (14 rows)

Complete Westlaw download of volumes 3–4 N.D. Reports (125 opinions, 1892–1895). Applied 2026-04-05. Source files saved to `~/refs/opin/N.D./vol3-4/`.

**11 author corrections** (mostly Bartholomew↔Corliss/Wallin swaps — early court had only 3 justices and CourtListener picked wrong one), **1 OCR fix** (Coirliss→Corliss), **1 date fix** (1893-12-03→1893-12-23).

**1 citation collision flagged:** Globe Inv. Co. v. Boyum / Kellogg, Johnson & Co. v. Gilman both at 3 N.D. 538.

## Batch: westlaw-nd-vol3-4-casenames (5 rows)

Spelling corrections: McMillen→McMillan (3 records), Hegar→Heger, Braithwaite v. Akin→Aiken.

## Batch: westlaw-nd-vol5 (2 rows) + westlaw-nd-vol5-casenames (1 row)

Volume 5 N.D. Reports (65 opinions, 1895–1896). Applied 2026-04-05.

2 author corrections (Bartholomew→Wallin, Corliss→Wallin). 1 case name fix: State v. Kent→State v. Pancoast (wrong defendant name in DB).

## Batch: westlaw-nd-vol6 (3 rows, 1 reverted) + westlaw-nd-vol5-6-casenames (3 rows)

Volume 6 N.D. Reports (69 opinions, 1896–1897). Applied 2026-04-05.

2 author corrections (Bartholomew→Corliss). 1 correction reverted: Westlaw had a typo "Barholomew" which was wrongly applied. Case name fixes: Shuttuck→Shattuck, Ellestad→Elstad, Fryer→Fryar.

## Batch: westlaw-nd-vol7 (8 rows)

Volume 7 N.D. Reports (88 opinions, 1897–1898). Applied 2026-04-05.

4 author corrections (3× Bartholomew→Corliss/Wallin). 4 date corrections. 3 citation collisions flagged (Red River v. Friel / Children of Israel at 7 N.D. 46; Gull River v. Brock / Lee at 7 N.D. 135; Knight v. Barnes / Tribune Printing at 7 N.D. 591).

## Batches: westlaw-nd-vol20 through westlaw-nd-vol23 (55 rows)

Volumes 20–23 N.D. Reports (341 opinions, 1910–1912). Applied 2026-04-15. Source files archived to `~/refs/opin/N.D./{20..23}/`. Run with `--case-names skip`.

| Volume | Files | Author fixes | Date fixes | Total |
|--------|-------|--------------|------------|-------|
| 20 | 79 | 10 | 2 | 12 |
| 21 | 93 | 15 | 8 | 23 |
| 22 | 94 | 10 | 2 | 12 |
| 23 | 75 | 5 | 3 | 8 |

All files matched DB records.

## Batches: westlaw-nd-vol24 through westlaw-nd-vol31 (69 rows)

Volumes 24–31 N.D. Reports (484 opinions, 1912–1915). Applied 2026-04-16. Source files archived to `~/refs/opin/N.D./{24..31}/`. Run with `--case-names skip` (case-name diffs deferred for separate review).

| Volume | Files | Author fixes | Date fixes | Total |
|--------|-------|--------------|------------|-------|
| 24 | 61 | 5 | 4 | 9 |
| 25 | 51 | 7 | 2 | 9 |
| 26 | 59 | 5 | 4 | 9 |
| 27 | 64 | 7 | 1 | 8 |
| 28 | 56 | 4 | 5 | 9 |
| 29 | 63 | 8 | 1 | 9 |
| 30 | 65 | 4 | 4 | 8 |
| 31 | 65 | 4 | 4 | 8 |

**3 not found in DB** (logged to `input-data/vol{25,29}/unmatched.txt`):
- 25 N.D. 268 — Great West Life Assur. Co. v. Shumway
- 29 N.D. 90 — First Nat. Bank v. Simmons Hardware Co.
- 29 N.D. 94 — Heitsch v. Minneapolis Threshing Mach. Co.

## Batches: westlaw-nd-vol32 through westlaw-nd-vol44 (269 rows)

Volumes 32–44 N.D. Reports (867 opinions, 1915–1920). Applied 2026-04-17 and 2026-04-18. Source files archived to `~/refs/opin/N.D./{32..44}/`. Run with `--case-names skip`.

| Volume | Files | Author fixes | Date fixes | Total |
|--------|-------|--------------|------------|-------|
| 32 | 60 | 4 | 1 | 5 |
| 33 | 60 | 4 | 4 | 8 |
| 34 | 65 | 5 | 8 | 13 |
| 35 | 54 | 6 | 6 | 12 |
| 36 | 66 | 6 | 4 | 10 |
| 37 | 74 | 15 | 1 | 16 |
| 38 | 57 | 15 | 0 | 15 |
| 39 | 68 | 23 | 1 | 24 |
| 40 | 54 | 11 | 1 | 12 |
| 41 | 84 | 28 | 9 | 37 |
| 42 | 88 | 30 | 2 | 32 |
| 43 | 75 | 30 | 7 | 37 |
| 44 | 62 | 38 | 2 | 40 |

All files matched DB records. Author-correction counts climb sharply from vol 37 onward as the Birdzell/Bronson/Christianson era of OCR misreads becomes denser.

## Batches: westlaw-nd-vol45 through westlaw-nd-vol48 (214 rows)

Volumes 45–48 N.D. Reports (390 opinions, 1919–1922). Applied 2026-04-19. Source files archived to `~/refs/nd/opin/N.D./{45..48}/`. Run with `--case-names skip`.

| Volume | Files | Author fixes | Date fixes | Total |
|--------|-------|--------------|------------|-------|
| 45 | 73 | 35 | 2 | 37 |
| 46 | 76 | 34 | 2 | 36 |
| 47 | 60 | 28 | 4 | 32 |
| 48 | 181 | 95 | 14 | 109 |

One unmatched file in vol 47 (47 N.D. 375, Merchants' State Bank v. Sawyer Farmers' Co-op Ass'n) — citation not present in DB; follow-up to investigate. Vol 48 is unusually large (181 opinions) and dense with corrections as the Birdzell/Bronson/Christianson OCR-misread era continues.

## Batches: westlaw-nd-vol49 through westlaw-nd-vol52 (186 rows)

Volumes 49–52 N.D. Reports (480 opinions, 1921–1924). Applied 2026-04-21. Source files archived to `~/refs/nd/opin/N.D./{49..52}/`. Run with `--case-names skip`.

| Volume | Files | Author fixes | Date fixes | Total |
|--------|-------|--------------|------------|-------|
| 49 | 155 | 76 | 4 | 80 |
| 50 | 109 | 55 | 4 | 59 |
| 51 | 104 | 13 | 4 | 17 |
| 52 | 112 | 27 | 3 | 30 |

All 480 files matched existing opinions (no unmatched citations). Case-name diffs skipped per prior convention; 42 case-name deltas visible in the run log are candidates for a follow-up case-name pass if/when desired.

## Batches: westlaw-nd-vol53 and westlaw-nd-vol54 (40 rows)

Volumes 53–54 N.D. Reports (248 opinions, 1925–1926). Applied 2026-04-22. Source files archived to `~/refs/nd/opin/N.D./{53,54}/`. Run with `--case-names skip`.

| Volume | Files | Author fixes | Date fixes | Total |
|--------|-------|--------------|------------|-------|
| 53 | 118 | 28 | 3 | 31 |
| 54 | 130 | 7 | 2 | 9 |

All 248 files matched existing opinions (no unmatched citations). 39 case-name diffs skipped (15 in vol 53, 24 in vol 54) — added to the deferred case-name review backlog.

## Batches: westlaw-nd-vol55 through westlaw-nd-vol57 (64 rows)

Volumes 55–57 N.D. Reports (370 opinions, 1926–1928). Applied 2026-04-23. Source files archived to `~/refs/nd/opin/N.D./{55,56,57}/`. Run with `--case-names skip`.

| Volume | Files | Author fixes | Date fixes | Total |
|--------|-------|--------------|------------|-------|
| 55 | 137 | 20 | 3 | 23 |
| 56 | 121 | 22 | 0 | 22 |
| 57 | 112 | 18 | 1 | 19 |

All 370 files matched existing opinions (no unmatched citations). 56 case-name diffs skipped (19 in vol 55, 21 in vol 56, 16 in vol 57) — added to the deferred case-name review backlog.

## Batches: westlaw-nd-vol58 through westlaw-nd-vol62 (148 rows)

Volumes 58–62 N.D. Reports (501 opinions, 1928–1932). Applied 2026-04-24. Source files archived to `~/refs/nd/opin/N.D./{58..62}/`. Run with `--case-names skip`.

| Volume | Files | Author fixes | Date fixes | Total |
|--------|-------|--------------|------------|-------|
| 58 | 120 | 34 | 2 | 36 |
| 59 | 82  | 38 | 1 | 39 |
| 60 | 106 | 18 | 3 | 21 |
| 61 | 99  | 25 | 1 | 26 |
| 62 | 94  | 25 | 1 | 26 |

All 501 files matched existing opinions (no unmatched citations). 82 case-name diffs skipped (23+10+20+14+15 across vols 58–62) — added to the deferred case-name review backlog.

## Batches: westlaw-nd-vol63 through westlaw-nd-vol68 (14 rows)

Volumes 63–68 N.D. Reports (499 opinions, 1932–1938). Applied 2026-04-25. Source files archived to `~/refs/nd/opin/N.D./{63..68}/`. Run with `--case-names skip`. The 64-65 and 66-67 Westlaw zips were combined exports; split locally by scanning each `.doc` for its `\b{vol}\s+N\.D\.\s+\d+` citation.

| Volume | Files | Author fixes | Date fixes | Total |
|--------|-------|--------------|------------|-------|
| 63 | 87  | 4 | 0 | 4 |
| 64 | 94  | 0 | 0 | 0 |
| 65 | 78  | 0 | 1 | 1 |
| 66 | 89  | 0 | 3 | 3 |
| 67 | 65  | 0 | 3 | 3 |
| 68 | 86  | 0 | 3 | 3 |

All 499 files matched existing opinions (no unmatched citations). Sharp drop in correction rate vs. vols 58–62 (14 fixes here vs. 148 prior) — author metadata in this run was largely clean already. 84 case-name diffs skipped (12+17+14+16+10+15 across vols 63–68) — added to the deferred case-name review backlog.

## Batches: westlaw-nd-vol69 through westlaw-nd-vol74 (9 rows)

Volumes 69–74 N.D. Reports (453 opinions, 1938–1946). Applied 2026-04-26. Source files archived to `~/refs/nd/opin/N.D./{69..74}/`. Run with `--case-names skip`. The 69-70 and 71-72 Westlaw zips were combined exports; split locally by scanning each `.doc` for its `\b{vol}\s+N\.D\.\s+\d+` citation.

| Volume | Files | Author fixes | Date fixes | Total |
|--------|-------|--------------|------------|-------|
| 69 | 72 | 0 | 0 | 0 |
| 70 | 87 | 0 | 1 | 1 |
| 71 | 73 | 0 | 1 | 1 |
| 72 | 79 | 0 | 4 | 4 |
| 73 | 77 | 0 | 3 | 3 |
| 74 | 65 | 0 | 0 | 0 |

All 453 files matched existing opinions (no unmatched citations). All 9 corrections were date_filed; zero author corrections in this run, continuing the clean-author trend that started at vol 64. 95 case-name diffs skipped (12+14+19+14+20+16 across vols 69–74) — added to the deferred case-name review backlog.

## Batches: westlaw-nd-vol75 through westlaw-nd-vol79 (10 rows) — **bound N.D. Reports series complete**

Volumes 75–79 N.D. Reports (343 opinions, 1946–1953). Applied 2026-04-27. Source files archived to `~/refs/nd/opin/N.D./{75..79}/`. Run with `--case-names skip`. The 75-76, 77-78, and 79-80 Westlaw zips were combined exports; split locally by scanning each `.doc` for its `\b{vol}\s+N\.D\.\s+\d+` citation.

| Volume | Files | Author fixes | Date fixes | Total |
|--------|-------|--------------|------------|-------|
| 75 | 64 | 0 | 2 | 2 |
| 76 | 59 | 0 | 2 | 2 |
| 77 | 78 | 0 | 1 | 1 |
| 78 | 73 | 0 | 3 | 3 |
| 79 | 69 | 0 | 2 | 2 |

All 343 files matched existing opinions (no unmatched citations). All 10 corrections were date_filed; zero author corrections, continuing the clean-author trend from vol 64. 44 case-name diffs skipped (7+6+13+14+4 across vols 75–79) — added to the deferred case-name review backlog.

The 79-80 zip's "80 ND" search hits were all modern neutral-cite false positives (the bound N.D. Reports series ends at vol 79); the splitter routed zero files to vol 80, confirmed by manual inspection of unmatched files. Eight files in the 75-76 zip were also modern neutral-cite hits (post-1953 NW2d-only opinions plus one 1906 case already archived under vol 15) and were correctly excluded.

**Series milestone:** Westlaw cross-check now applied to all 79 volumes of the bound N.D. Reports (1890–1953). Total Westlaw ingest: ~6,750 .doc files, ~440 metadata corrections across vols 1–79. The 1953–1996 NW2d-only era has no further bound-reporter source; targeted Westlaw Quick Check on low-confidence opinions is the next stage (TODO-validation §2).

## Batch: westlaw-text-merge (incremental, 5,730 rows added 2026-04-21)

`python -m ndcourts_mcp.merge_westlaw_text --apply` run after the vol 49–52 ingest to replace text_content with cleaner Westlaw copies where the pre-1997 Westlaw source beats the OCR NW/NW2d text. Run twice in error (the second was triggered accidentally when a shell pipe failed); of the 5,730 changelog rows, 2,866 are no-op duplicates (old_value = new_value, text_content field only) and 371 reflect minor Westlaw-reparse differences. DB state is correct — the stored text_content is the Westlaw version. Revert of the batch still unwinds correctly because entries replay in reverse timestamp order.

2,865 distinct opinions received replacement text. 455 errors reported by the tool (opinions where the Westlaw source exists but the text-similarity check prevented a safe replace) — worth triaging in a follow-up.

## Batches: backfill-westlaw-source-paths (4,087) + backfill-westlaw-source-paths-tmp (1,611)

Applied 2026-04-27. Script: `python -m ndcourts_mcp.backfill_westlaw_paths --apply [--batch NAME]`.

Repaired stale `opinion_sources.source_path` values for 5,698 westlaw rows. Volume-based ingest had been recording the temporary staging path (`input-data/volN/...` for vols 11–79 + `/tmp/westlaw-volN/...` for vols 53–62 + `/tmp/westlaw-stage/volN/...` for vols 63–68) instead of the final archive path under `~/refs/nd/opin/N.D./N/`. The DB row was set in `_archive_single_doc` *before* the batch archiver `_archive_westlaw_docs` ran, and was never updated.

Discovered when `merge_westlaw_text --dry-run` reported 2,070 "errors" (most prior runs had ~455 — the gap was the new vols 49–79 batches with the same stale-path bug). After the backfill, the dry-run dropped to 110 genuine parse errors + 27 suspicious-length rejects.

Resolution algorithm: for each stale path, extract `vol(\d+)` from the path prefix, build a slug from the `NNN - Case Name.doc` filename, then `glob(f"*-{slug}.doc")` in `~/refs/nd/opin/N.D./{vol}/`. 125 same-slug collisions within a volume disambiguated by matching the `{page:04d}-` prefix to the page from the opinion's `vol N.D. page` citation. All 5,698 resolved cleanly.

**Root cause fixed in `ingest_westlaw.py`** (same date): `_archive_single_doc` now computes and returns the predicted archive path even in volume mode (instead of returning `doc_path`), so future ingests record the correct path on insert. The batch archiver still does the actual file copy after the per-file loop.

## Batch: westlaw-text-merge-2026-04-27 (5,466 rows)

`python -m ndcourts_mcp.merge_westlaw_text --apply --batch westlaw-text-merge-2026-04-27`. Replaced text_content with cleaner Westlaw copies for 2,733 opinions across vols 49–79. Two changelog rows per opinion (`text_content` + `source_reporter`).

Bug fix vs. 2026-04-21 run: query now filters out `o.source_reporter='westlaw'` (already-merged opinions), preventing the no-op-duplicate behavior that produced 2,866 spurious rows last time.

| Source reporter pre-merge | Opinions migrated to westlaw |
|----|----:|
| NW   | 2,144 |
| NW2d | 589 |

Initial residuals: 137. After parser fixes (next entry) the count dropped to 29; the 137 ⇒ 29 reduction is logged in the pass2/pass3 batches below.

## Batches: westlaw-text-merge-2026-04-27-pass2 (216 rows) + pass3 (10 rows)

Triage of the 137 residuals from the pass1 run revealed three parser limitations in `_parse_westlaw_doc`:

1. **108 of 110 SKIPs were a single root cause:** post-classic Westlaw exports lack the bare "Opinion" header line. The body begins after `Attorneys and Law Firms` + the attorney list + an author line (e.g., `ERICKSTAD, Judge.`). Parser extended to detect this format and use the author line as `body_start`. Pass2 unlocked 103 merges.
2. **Star-pagination prefix and `PER CURIAM` and `District Judge` markers:** edge cases where the author detection regex didn't fire (`*962 GOSS, J.`, `PER CURIAM.`, `COLE, District Judge.`). Regex extended to strip leading `*\d+\s+` and to accept those marker variants.
3. **"All Citations" search window was 20 lines from EOF**, but docs with long Footnotes sections push the marker further back (e.g., State v. Thompson at line 135 of 157). Search now scans the entire doc from the end. Pass3 unlocked 5 more merges (3 stragglers from #2 plus 2 that needed the wider footer search).

After three passes, **2,841 opinions migrated to Westlaw text in this session** (2,733 + 103 + 5).

The errors-report tool added in the same commit (`merge_westlaw_text --errors-report PATH`) categorizes residuals into actionable buckets and writes a markdown triage doc. Current residuals (29):

| Category | Count | Action |
|---|---:|---|
| Westlaw text suspiciously short (< 30% of DB) | 27 | case-by-case; see report |
| Missing opinion header AND no Attorneys section | 2 | likely irretrievable from this Westlaw export |

Of the 27 length-rejects, manual inspection of the report suggests two sub-patterns:
- ~4 are wrong pairings: the Westlaw .doc filename does not match the DB case name (e.g., DB "Burger v. Sinclair" linked to a "Seckerson v. Sinclair" .doc — same NW page citation, different case). These should have the `opinion_sources` row deleted.
- The rest are real differences: NW2d-era opinions where Westlaw exports only the opinion body while the DB stores body + CL-OCR headnotes (e.g., Stormon v. Weiss has a 200K .doc but only 10 body lines).

After this session, **5,701 opinions are westlaw-primary** (up from 2,865 at session start) of 5,735 with a westlaw source linked. Triage report committed at `triage/westlaw-merge-residuals-2026-04-27.md`.

## Batches: backfill-sources-insert (5,548 rows) + backfill-sources-promote (5,260 rows)

Applied 2026-04-18. Script: `python -m ndcourts_mcp.backfill_sources --apply [--promote]`.

Closes the source-attachment gap that accumulated because ingest's dedup merge added citations but never recorded the secondary source file in `opinion_sources`. Audit (`audit_sources`) showed 5,260 ndcourts.gov markdown files and 288 archive.ndcourts.gov HTML files existed on disk but were not linked.

**Insert phase** (5,548 `opinion_sources` INSERTs):

| Reporter | Rows | Era |
|----------|------|-----|
| ND | 5,260 | 1997–2026 |
| archive | 288 | 1997–2019 |

**Promote phase** (5,260 opinions flipped to ND-primary):

For 1997+ opinions whose primary was NW2d (5,258) or westlaw (2) but now have a linked ND source, set `opinion_sources.is_primary=1` on the ND row and update `opinions.source_reporter` to 'ND'. ndcourts.gov is authoritative for 1997+. Did NOT alter `opinions.source_path` or `text_content` — those may still point at the old source file and will be aligned in a follow-up pass (TODO-validation §4 Phase 3).

**Known limitations:**
- 122 post-1997 opinions remain NW2d-primary. None carry an ND citation, so they have no ndcourts.gov counterpart to promote to. Likely memorandum opinions or orders without a neutral cite.
- 2 opinions (IDs 20383, 20384) list an ND citation but the markdown file is missing from disk. Tracked in TODO-validation §7.
- Root-cause fix in `ingest.py` merge logic still pending — future ingests will reopen the gap until the merge path is updated to insert the secondary `opinion_sources` row (TODO-validation §4).

## Batch: align-primary-source (5,281 rows)

Applied 2026-04-18. Script: `python -m ndcourts_mcp.align_primary_source --apply`.

Cleanup of stale `opinions.source_path` values left behind by the backfill promote pass and by an older `merge_westlaw_text` bug. For every opinion whose `source_path` or the `is_primary` flag in `opinion_sources` disagreed with `opinions.source_reporter` (treated as ground truth), rewrote the path and flipped the primary flag.

- 5,247 ND-primary opinions had `source_path` still pointing at `NW2d/...md` post-promote. Now point at `ND/...md`.
- 34 westlaw-primary opinions had `source_path` pointing at `NW/...md` or `NW2d/...md` and had the wrong `opinion_sources` row marked primary. Flipped to the `.doc` file and the westlaw `opinion_sources` row.

Post-run integrity: every opinion has exactly one `opinion_sources` row with `is_primary=1`, and `opinions.source_path` matches that row for all 20,384 records.

Root cause of the westlaw drift fixed in `merge_westlaw_text.py` (now updates `source_path` and flips `opinion_sources.is_primary` atomically with the text replacement).

## Batches: westlaw-merge-residuals-2026-04-27-pairings (27 rows) + westlaw-text-merge-2026-04-27-pairings (36 rows)

Applied 2026-04-27. Fixed nine Westlaw .doc pairings that had been attached to the wrong opinion at ingest, and merged the now-correctly-paired text.

Each of nine vol/page locations in the bound N.D. Reports has two short opinions (a lead opinion plus a per curiam follow-on filed the same day) that legitimately share the same `<vol> N.D. <page>` cite. The volume-based ingest paired one .doc with one of the two arbitrarily and orphaned the other. The triage report at `triage/westlaw-merge-residuals-2026-04-27.md` flagged these as "westlaw-text-too-short" because the wrong-paired .doc was a 4-line per curiam follow-on while the DB row was the lead opinion (or vice versa).

Pair fixes (vol/page → wrong-paired opinion / correct opinion):

| Vol/Page | Wrong-paired (deleted) | .doc reattached to | Orphan .doc reattached to |
|---|---|---|---|
| 14/557 | 146 State v. Poull | 152 Murphy v. Dist. Ct. | 146 (0557-State-v-Poull.doc) |
| 24/326 | 1012 Burger v. Sinclair | 1013 Seckerson v. Sinclair | 1012 (0326-Burger.doc) |
| 17/266 | 382 Ross v. Prante | 383 Skeffington v. Prante | 382 (0266-Ross.doc) |
| 17/393 | 415 Soliah v. Cormack | 422 Erickson v. Elliott | 415 (0393-Soliah.doc) |
| 16/106 | 295 Farquhar v. Higham | 296 Harvey v. Davies | 295 (0106-Farquhar.doc) |
| 51/13 | 2955 Hintz v. Jackson | 2958 Klingenstein | 2955 (0013-Hintz.doc) |
| 48/577 | 2597 Johnson Const. | 2606 Hanson v. Houska | 2597 (0577-Johnson-Const.doc) |
| 64/367 | 4482 Thorvaldson-Johnson | 4484 Ott v. Kelley | 4482 (0367-Thorvaldson.doc) |
| 50/813 | 2935 Farmers Bank v. Jeske | 2946 Hassen v. Salem | 2935 (0813-Farmers.doc) |

Pairing batch: 9 deletions + 18 insertions in `opinion_sources` (27 changelog rows under `field='opinion_sources.westlaw'`). Text-merge batch: all 18 newly-paired rows merged successfully (36 changelog rows: 18 × `text_content` + 18 × `source_reporter`).

Applied via `python -m ndcourts_mcp.fix_westlaw_pairings --apply` followed by `python -m ndcourts_mcp.merge_westlaw_text --apply --batch westlaw-text-merge-2026-04-27-pairings`. Both batches revertible (deletions/insertions are reflected in changelog and could be reversed by hand if needed; the standard `cleanup revert` only handles `opinions`-table fields).

Side issues surfaced and deferred to TODO-validation §1:
- Opinions 4484/4485 are duplicate Ott v. Kelley rows; the .doc was attached to 4484 only.
- Opinion 2946 (Hassen v. Salem rehearing) is cited `50 N.D. 825` in the DB but Westlaw's "All Citations" footer says `50 N.D. 813`. Cite conflict left in place pending bound-volume verification.

## Batch: westlaw-text-remerge-2026-04-28-full-bound (62 rows)

Applied 2026-04-28. Re-merged 31 Westlaw-paired opinions with a corrected parser that extracts the full bound publication entry (Syllabus by the Court + Attorneys + Opinion + in-publication rehearing material), instead of the body-only extraction the prior parser produced.

**Why:** verifying whether the prior pairing-batch had stripped any "Syllabus by the Court" content surfaced a corpus-wide finding — CourtListener's source .md files contain *no* "Syllabus by the Court" content for any pre-1953 opinion checked (0 of 18 in this batch; 0% of CL .md files vs ~97% of corresponding Westlaw .docs). CL never preserved the court's own syllabus. The bound N.D. Reports series (1890–1953) routinely included a "Syllabus by the Court" section as the court's official restatement of the holding — see *Sargent County v. State*, 47 N.D. 561 (1921), and ~5,500 other pre-1953 opinions in the corpus.

**Parser changes (`ndcourts_mcp/ingest_westlaw.py`):**
- New `_extract_full_bound_text(lines, all_cites_idx)` extracts the published bound entry, anchored at the first court-published section (Syllabus by the Court → Syllabus → Synopsis → Attorneys and Law Firms) rather than just the "Opinion" header.
- Drops `West Headnotes` (unambiguously Westlaw editorial). Preserves `Synopsis` because in older bound publications Westlaw's "Synopsis" section often contains the court's published statement of facts (referenced in opinions as "after stating the facts as above"); modern Synopsis sections are short editorial summaries that are harmless to retain.
- Preserves `Syllabus by the Court` (court's own text, the historical practice). "Syllabus by Editorial Staff" is a distinct line that does not match my header set, so editorial-staff syllabi are correctly excluded by virtue of falling before the "Synopsis" header where extraction begins.
- New `full_bound_text` field on `_parse_westlaw_doc` result; `merge_westlaw_text` now prefers it over the legacy `opinion_text` body-only extraction.

**Validator changes (`ndcourts_mcp/merge_westlaw_text.py`):**
- Renamed `_HEADNOTE_STARTS` → `_EDITORIAL_STARTS`. Only `West Headnotes` is unambiguously editorial leakage worth rejecting at the start of a body. `Syllabus by the Court`, `Syllabus`, `Synopsis`, and `Attorneys and Law Firms` are now valid starting markers since they're intentionally included by the new parser.
- Added idempotency check: skip rows where the new text equals the current text (no-op).
- Added `--include-westlaw` flag to re-process rows already at `source_reporter='westlaw'` (use after parser fixes).
- Added `--ids` flag to limit processing to specific opinion IDs.

**Re-merge results:** 33 IDs processed (the 18 just-paired in the previous batch + 15 Type X residuals from the original 29 in `triage/westlaw-merge-residuals-2026-04-27.md`). 31 successfully replaced with longer/cleaner text; 1 unchanged (Klingenstein 2958 — full_bound text matched current); 1 rejected (Chester 9128 — reclassified as Type Y, handled below).

Notable size changes:
- Stormon v. Weiss (13627): 397,178 → 204,723 chars. The DB previously contained the opinion text *twice* (two different OCR encodings concatenated by an old ingest bug); the replacement is the deduplicated full bound entry.
- Sargent County v. State (2502): 203,316 → 204,035 chars. Now correctly captures the syllabus + statement of facts + main opinion + Birdzell's rehearing analysis + Grace's further dissent — the full bound entry. Prior parser was extracting only the post-opinion-header content (~27% of bound entry).
- 14 cases gained 100–5000 chars by adding the syllabus.

## Batch: westlaw-supplemental-publications-2026-04-28 (37 rows)

Applied 2026-04-28. Inserted 6 new opinion rows for Westlaw .docs that are SEPARATE supplemental publications — concurring opinions, rehearings, per-curiam follow-ons, and memoranda published in the bound reporter at a discontinuous N.W. cite from the main opinion. The volume-based ingest had paired each supplemental .doc with the main DB row (because they share the N.D. starting page) and orphaned the supplemental publication entirely.

**Discovery context:** the user proposed two hypotheses: (a) the bound reporter sometimes published supplementals at discontinuous page ranges, and (b) the "headnotes/syllabus" content I was treating as CL editorial was in fact the court's official syllabus. Both hypotheses confirmed by the data — see audit notes above.

**The 6 supplementals (new opinion IDs 20386–20391):**

| Main OID | Main cite | New OID | Supplemental cite | Nature |
|---|---|---|---|---|
| 458 | 118 N.W. 820 | 20386 | 118 N.W. 823 (Mem) | Per curiam follow-on |
| 2125 | 172 N.W. 663 (Bronson, J.) | 20387 | 182 N.W. 700 (Mem) | Robinson, J., separate opinion (10 N.W. vols later) |
| 2473 | 181 N.W. 590 | 20388 | 181 N.W. 908 | Concurring opinion |
| 2635 | 187 N.W. 233 (1922-02-11) | 20389 | 187 N.W. 619 (1922-04-11) | On rehearing — denied |
| 2863 | 195 N.W. 14 | 20390 | 195 N.W. 33 (Mem) | Per curiam (joint with Baker v. Lenhart) |
| 9128 | 34 N.W.2d 418 (1948-10-27) | 20391 | 35 N.W.2d 137 (1948-12-06) | On petition for rehearing |

Each new row carries: case_name with disambiguation suffix; primary citation = the supplemental's distinct N.W. cite; parallel citation = the shared N.D. cite; date_filed parsed from the .doc; `notes` field linking back to the main opinion. The .doc opinion_sources westlaw row was detached from the main opinion and re-attached to the new row (is_primary=1).

Special case for Chester (9128): the citation `35 N.W.2d 137` had been incorrectly listed on the main row alongside `34 N.W.2d 418`; that citation was moved to the new supplemental row 20391 since it actually pertains to the rehearing publication, not the main.

Applied via `python -m ndcourts_mcp.insert_supplemental_opinions --apply`. Changelog entries: 6 detaches + 6 opinion inserts + 12 citation inserts + 1 citation move + 6 fresh opinion_sources rows + provenance row = 37 total.

**Pattern signal for future ingests:** when a Westlaw .doc has a different N.W. cite from the existing DB row that shares its N.D. cite, treat it as a separate publication, not as a re-pairing target. Update `ingest_westlaw.py` to detect this case at ingest time rather than relying on volume-page filename collision.

## Batch: westlaw-syllabus-recovery-corpus-wide-2026-04-28 (11,402 rows)

Applied 2026-04-28. Corpus-wide re-merge of every Westlaw-paired opinion through the corrected parser, recovering the court's official "Syllabus by the Court" text and any other published bound-entry content the prior body-only parser had dropped.

**Scope:** 5,744 eligible opinions (every row with `opinion_sources.source_reporter='westlaw'` and `opinions.source_reporter NOT IN ('ND')`). Of those, **5,701 replaced** with cleaner full-bound-entry text, **43 skipped** as idempotent (text already at the new format from earlier batches), **0 rejected**, **0 errors**. Each replaced row produced 2 changelog entries (`text_content` + `source_reporter`), totaling 11,402 rows.

**Result:** 4,717 pre-1953 opinions now contain "Syllabus by the Court" content, up from a near-zero baseline. The 1,022 pre-1953 westlaw opinions still without a syllabus marker are predominantly per-curiam follow-ons, memorandum decisions, and short rehearing-only publications that did not have a published syllabus in the bound reporter — these match the `(Mem)` cite pattern Westlaw uses for memoranda.

**Why this matters for the authoritative-text goal:** CourtListener's NW/NW2d source files contain zero "Syllabus by the Court" content for pre-1953 opinions (verified earlier in this session: 0 of 18 audited CL .md files). The court's own syllabus is part of the published opinion as the bound N.D. Reports printed it; without it, the DB was systematically missing court-authored content. This batch closes that gap for the entire bound-series era.

Applied via `python -m ndcourts_mcp.merge_westlaw_text --apply --include-westlaw --batch westlaw-syllabus-recovery-corpus-wide-2026-04-28`. Single-threaded run took roughly 13 minutes for 5,744 docs (~7 docs/sec including textutil + parser + SQL). One bug fixed mid-run: format string crashed on rows with NULL `quality_score`; nothing committed before the crash, restarted cleanly.

## Batch: refs-migration-nd-opin (14,877 rows)

Applied 2026-04-18. Not a correction — a path-rewrite migration to align `source_path` values with the move of the source tree from `~/refs/opin/` to `~/refs/nd/opin/` (the canonical path documented in `~/refs/CLAUDE.md`).

Rewrite rules:
- Relative `ND/<year>/<file>.md` → `markdown/<year>/<file>.md` (7,408 rows across both tables). The `ND/` directory was renamed to `markdown/` to match the canonical layout.
- Absolute `/Users/jerod/refs/opin/...` → `/Users/jerod/refs/nd/opin/...` (74 rows, all Westlaw .doc files).

Tables touched: `opinions.source_path` (7,429 rows), `opinion_sources.source_path` (7,448 rows). Every row logged in changelog. No content changed, only paths.

Filesystem moves were atomic `mv` operations within the same filesystem. Backward-compat symlinks at `~/refs/opin/{ND,NW,NW2d,NW3d,N.D.,archive}` point into the new tree so other consumers (jetmemo-skill, jetcite, etc.) continue working through the symlink.

## Freshness ingest 2026-05-04 — ND 71–90 (20 new opinions)

Closed a 6-week gap between the DB's last ingested opinion (2026 ND 70, 2026-03-26) and ndcourts.gov's current state (2026 ND 90, 2026-04-22). Two release days had accumulated unscraped: 2026-04-09 (ND 71–77) and 2026-04-22 (ND 78–90).

The scraper's launchd job had been running weekly and downloading PDFs + JSON metadata correctly, but the chained `ndcourts_mcp.ingest` + `merge_nd_metadata` step (§5 of TODO-validation.md) is not yet wired into `weekly_scrape.sh`, so opinions sat on disk without entering the DB. Manual ingest run today plugged the gap.

20 new rows inserted, ids 20392–20411. After `merge_nd_metadata`, all carry correct `case_name`, `date_filed`, `author`, `case_type`, `judges`, `voting_record`, and `opinion_url` from `~/refs/nd/opin/2026_opinions.json`.

### Side fix: 2026 ND 62 / 2026 ND 73 docket-collision (Romanyshyn)

ND 62 (filed 2026-02-26) and ND 73 (filed 2026-04-09) are two distinct opinions in the same Stark County criminal case (docket 20250295) — ND 73 is the post-remand merits opinion that ND 62 set up. The scraper's docket-keyed dedup mistakenly assigned ND 73's JSON record the same `pdf_path` and `markdown_path` as ND 62, leaving the actual `2026ND73.pdf` (downloaded fine) without a corresponding markdown file and pointing the JSON at the wrong text.

Corpus sweep across 2000–2026 found 20 docket-collision pairs total; **19 were handled correctly with distinct paths** — only ND 62/73 was broken. This is a recent regression, not systemic.

Resolution:
- `2026_opinions.json` ND 73 record: `pdf_path` and `markdown_path` rewritten to point at the correct `2026ND73.{pdf,md}` files; stale `claude_query_hash` and `claude_query_timestamp` (which had been computed against ND 62's text) cleared so a future analysis run will re-do.
- `2026ND73.md` regenerated from the actual `2026ND73.pdf` via `extract_text_from_pdf` + `cleanup_markdown` + `save_text_to_markdown_file`. 9,534 chars, 20 ¶ markers, ¶5 explicitly references "State v. Romanyshyn, 2026 ND 62, ¶¶ 6-7. On remand …" confirming distinct content.
- Backup of pre-edit JSON kept at `2026_opinions.json.backup_pre-nd73-fix-20260504_161948`.

Root cause in the scraper not yet diagnosed — see TODO-validation.md §5 follow-ups.

### Scraper code fix: opinion_processor.py:752 (markdown-write skip)

Companion fix to the long-standing §5 bug. `--skip-analysis` mode was treating `existing_data.get('markdown_path')` as proof the markdown file existed, without verifying. Updated to also call `os.path.exists()` against the resolved path; if the file is missing, fall through to regenerate. Mirrors the check the non-`skip_analysis` branch already does on lines 766–781.

In practice this bug only fired once in this session (against the conflated ND 73 JSON record above, where `markdown_path` pointed to ND 62's existing file — so the "file exists" guard wouldn't have caught it anyway). But it closes a real silent-skip path going forward.

## Batch: fix-westlaw-pairings-round2-2026-05-04 (12 rows + 8 followup) + text-merge

Applied 2026-05-04. Four more wrong-paired Westlaw .docs surfaced by the multi-source diff audit's westlaw+NW <0.20 band — same shape as the original §1 9-pairings cluster fix but in volumes that batch missed. Two opinions share each bound N.D. page; volume-based ingest paired one .doc with the wrong opinion and orphaned the other.

| Vol/page | Wrong-paired opinion (had wrong .doc) | True home of wrong .doc | Sim before |
|---|---|---|---|
| 51 N.D. 300 | 3011 *Dorr County State Bank v. Adams* | 3007 *County of Dickey v. Gesme* | 0.014 |
| 21 N.D. 69 | 699 *Willis v. Weatherwax* | 733 *State ex rel. Kramer v. Kiefer* | 0.132 |
| 12 N.D. 504 | 5982 *Montgomery v. Tucker* | 6023 *Sykes v. Allen* | 0.132 |
| 27 N.D. 458 | 1186 *Hackney v. Lynn* | 1189 *Bussey v. Boynton* | 0.139 |

Applied via `python -m ndcourts_mcp.fix_westlaw_pairings_round2 --apply`: 4 deletes + 8 inserts = 12 changelog rows under batch `fix-westlaw-pairings-round2-2026-05-04`. Followed by `merge_westlaw_text --apply` (4 home-opinion text replacements) + a manual `is_primary` / `source_path` correction on the 4 wrong-paired opinions (8 followup rows in the same batch — needed because `align_primary_source` skipped them; see follow-up below) + `merge_westlaw_text --apply --include-westlaw --ids 3011,699,5982,1186` to force-refresh text for the originally-wrong-paired rows (4 more replacements).

Notable replacement: oid 3011 *Dorr v. Adams* text_content went from **9,775 chars to 18,222 chars** — the wrongly-paired Dickey .doc was a much shorter opinion. The other 3 swaps were closer in length.

Diff audit `<0.20` band: 87 → 83. Invariants: 13 ok / 2 baseline / 0 regressed.

**Bug surfaced in `align_primary_source`:** its driving query at `align_primary_source.py:31-35` is an INNER JOIN on `opinion_sources s ON s.opinion_id = o.id AND s.is_primary = 1`. When all `opinion_sources` rows for an opinion have `is_primary = 0`, the opinion doesn't match the JOIN and the script silently skips it — exactly the case here, since this batch's deletes-then-inserts left the 4 affected opinions with no primary row at all. Captured as a TODO follow-up. The invariants dashboard correctly caught it (`primary_source_unique` went from 0 → 4 violations until the manual fix landed).

## Batch: fix-cl-metadata-contamination-2026-05-04 (10 rows) + fix-archive-pairings-post-cl-cleanup-2026-05-04 (4 rows) + manual detach (1 row)

Applied 2026-05-04. Sweep for the same CourtListener-metadata contamination pattern the Feldmann fix uncovered.

`ndcourts_mcp.fix_cl_metadata_contamination` walks every CL JSON metadata file under `~/refs/nd/opin/NW{,2d,3d}/`, flags any whose `citations` list contains 2+ neutral ND cites (a smoking gun for cross-opinion contamination — modern opinions have exactly one neutral cite), and for each affected DB row identifies the row's true cite from its `source_path` (`markdown/<year>/<year>NDN.md` → `<year> ND N`) and drops the other cites as strays.

Sweep found 16 contaminated CL JSONs; 6 were already cleaned up by prior batches (Feldmann, Kitchen/Kleinsmith, Keller, Johnson swap), 10 still dirty:

| oid | source_path's derived cite | Stray dropped | CL JSON |
|---|---|---|---|
| 12476 | 1997 ND 132 | 1997 ND 129 | NW2d/566/407.json |
| 14095 | 2004 ND 168 | 2004 ND 115 | NW2d/686/115.json |
| 15393 | 2010 ND 57  | 2010 ND 54  | NW2d/780/663.json |
| 15600 | 2011 ND 48  | 2011 ND 65  | NW2d/795/367.json |
| 15869 | 2012 ND 138 | 2012 ND 148 | NW2d/818/718.json |
| 15931 | 2012 ND 198 | 2012 ND 196 | NW2d/821/373.json |
| 16826 | 2016 ND 241 | 2016 ND 332 | NW2d/888/769.json |
| 16924 | 2017 ND 116 | 2017 ND 126 | NW2d/894/865.json |
| 17030 | 2017 ND 241 | 2017 ND 216 | NW2d/901/727.json |
| 17035 | 2017 ND 220 | 2017 ND 233 | NW2d/902/501.json |

10 changelog rows under batch `fix-cl-metadata-contamination-2026-05-04`.

Then `cite_extract --cited-by-only` rebuilt cited_by from text_citations: 163,475 cross-links re-derived; the cited_by table is now consistent with the corrected citations table.

Then `fix_archive_pairings --apply` (batch `fix-archive-pairings-post-cl-cleanup-2026-05-04`) re-classified archive linkages now that the strays no longer matched: 1 swap + 1 detach + 1 relink-after-swap = 4 changelog rows.

| Action | oid | Description |
|---|---|---|
| swap (with relink) | 15393 ↔ 15515 | `archive/2010/20090357.htm` (Disciplinary Board case) moves from 15393 to 15515; `archive/2010/20090276.htm` (titled `State v. M.B., 2010 ND 57, 780 N.W.2d 663`) inserted on 15393. |
| detach | 15931 | `archive/2012/20120145.htm` (titled `2012 ND 196`) detached from 15931 (which is `2012 ND 198`); no replacement available in archive index. |

One residual: oid 17030 (WSI v. Questar Energy Services). Its wrong archive `archive/2017/20170241.htm` is titled `Disciplinary Board v. Lee, 2017 ND 216, 901 N.W.2d 727` — neutral disagrees with the row's `2017 ND 241` but the parallel `901 N.W.2d 727` matches both rows (CL data also lists this parallel on the Lee opinion's record, which is itself a separate contamination), so `fix_archive_pairings`' title-check accepts the linkage. Manually detached this 1 row; logged under the same batch.

**Pattern note for `fix_archive_pairings`:** the title-check returns "ok" when EITHER the title's neutral cite OR its parallel cite appears in the row's citations. That's too lenient when both opinions in a contamination pair share a parallel cite. Tighten to require the title's neutral cite to be in the row's citations (with the parallel as a secondary check). Captured under TODO §3.

Verification:
- invariants dashboard: 13 ok / 2 baseline / 0 regressed (unchanged)
- multi-source diff audit `<0.20` band: 88 → 87
- All 16 contaminated CL JSONs no longer cross-pollute DB rows.

The CL JSON files themselves are upstream and unfixed, but the DB now ignores their bogus extra cites and the dedup-by-cluster_id behavior in `_ingest_nw_opinions` means future ingests won't re-introduce them.

## Batch: fix-feldmann-2017-2026-05-04 (8 rows)

Applied 2026-05-04. Final Type Y candidate from the deep triage. The CourtListener metadata at `NW2d/889/399.json` mistakenly lists `2017 ND 255` as a parallel cite of *In the Matter of a Petition to Permit Temporary Provision of Legal Services* (the Dakota Access Pipeline pro hac vice order, 2017 ND 1, filed 2017-01-18). When ingest dutifully attached the bogus cite, the ND-side ingest then matched `2017 ND 255` to `markdown/2017/2017ND255.md` (which is actually the Estate of Feldmann opinion at oid 17060) and linked it as the primary source — replacing the correct `2017ND1.md`. `merge_nd_metadata` then overwrote case_name, date_filed, and author with Feldmann's data.

So oid 16829's row was thoroughly contaminated: correct cites (`2017 ND 1`, `889 N.W.2d 399`) but Feldmann's case_name, Feldmann's filing date, Feldmann's text_content, and Feldmann's archive linkage. The Feldmann opinion itself was already correct at oid 17060, untouched.

Fixes applied via `python -m ndcourts_mcp.fix_feldmann_2017 --apply`:

| oid | Field | Old | New |
|---|---|---|---|
| 16829 | `citations.stray` | `'2017 ND 255'` | (removed; CL metadata contamination) |
| 16829 | `opinion_sources.archive` | row → `archive/2017/20170034.htm` | (detached; Feldmann's archive, owned by 17060) |
| 16829 | `opinion_sources.ND.source_path` | `markdown/2017/2017ND255.md` | `markdown/2017/2017ND1.md` |
| 16829 | `opinions.case_name` | "Estate of Feldmann" | "Petition to Permit Temporary Provision of Legal Services" |
| 16829 | `opinions.date_filed` | `2017-10-26` | `2017-01-18` |
| 16829 | `opinions.source_path` | `markdown/2017/2017ND255.md` | `markdown/2017/2017ND1.md` |
| 16829 | `opinions.per_curiam` | `0` | `1` |
| 16829 | `opinions.text_content` | (was Feldmann content, ~13.7k chars) | (now Pipeline Petition content, 13,275 chars) |

`opinions.author` left at NULL (per curiam) — already NULL, no change recorded.

Followed by clearing `cite_extract_progress` and `text_citations`/`cited_by` for oid 16829 and re-running `python -m ndcourts_mcp.cite_extract`, which scanned the corrected text and extracted 5 outgoing citations.

Post-fix: opinion 16829 represents the actual Pipeline Petition opinion with clean cites, correct text, and no archive. Invariants stayed clean (13 ok / 2 baseline / 0 regressed). Diff audit `<0.20` band: 89 → 88. **All 5 Type Y candidates from the deep triage are now resolved.**

The CL metadata error at `NW2d/889/399.json` itself isn't fixable from our side, but the dedup-by-cluster_id behavior in `_ingest_nw_opinions` means the bogus `2017 ND 255` cite won't be re-introduced on subsequent re-ingests.

## Batch: fix-kitchen-kleinsmith-2013-2026-05-04 (5 rows)

Applied 2026-05-04. The Kleinsmith Type Y candidate from the deep triage was untangled by reading the actual markdown content. Two reciprocal-discipline opinions filed Feb 12, 2013:

- `markdown/2013/2013ND18.md` is the **Kitchen** opinion (Craig V. Kitchen, suspension with conditions).
- `markdown/2013/2013ND19.md` is the **Kleinsmith** opinion (Philip M. Kleinsmith, reprimand and probation).

DB state before:
- `oid 15988`: source_path = `2013ND18.md` (Kitchen text), but `case_name = "Reciprocal Discipline of Kleinsmith"` ✗. Cites: `2013 ND 18`, `826 N.W.2d 620` (own); `2013 ND 19` (stray). Archive: `archive/2013/20130018.htm` (Kitchen — correct).
- `oid 16488`: source_path = `2013ND19.md` (Kleinsmith text), case_name correct ✓. Cites: `2013 ND 19`, `863 N.W.2d 843` (own); `2013 ND 18` (stray). Archive: `archive/2013/20130018.htm` ✗ (Kitchen's, not Kleinsmith's). Kleinsmith's correct archive `archive/2013/20130019.htm` (4 KB, titled "Reciprocal Discipline of Kleinsmith, 2013 ND 19, 863 N.W.2d 843") existed on disk but was never linked.

Fixes applied via `python -m ndcourts_mcp.fix_kitchen_kleinsmith_2013 --apply`:

| oid | Field | Old | New |
|---|---|---|---|
| 15988 | `case_name` | "Reciprocal Discipline of Kleinsmith" | "In re Reciprocal Discipline of Kitchen" |
| 15988 | `citations.stray` | `'2013 ND 19'` | (removed) |
| 16488 | `opinion_sources.archive` | row → `archive/2013/20130018.htm` | (detached) |
| 16488 | `opinion_sources.archive` | (none) | new row → `archive/2013/20130019.htm` |
| 16488 | `citations.stray` | `'2013 ND 18'` | (removed) |

Post-fix: both rows have correct `case_name`, only their own citations, and correct archive linkages. Diff audit `<0.20` band: 90 → 89.

**Pattern-level lesson:** when DB rows have multiple neutral cites and the case_name doesn't match the source markdown's own header, trust the markdown text (and the source_path) over the case_name field. The case_name was likely set during ingest from a heuristic that pulled the wrong "v." line from a per-curiam opinion's header. Future ingests should validate case_name against the markdown's leading lines.

## Batch: fix-type-y-archive-pairings-2026-05-04 (6 rows)

Applied 2026-05-04. Surfaced by the deep-triage of the §3 multi-source diff audit (see `triage/archive-83-deep-triage-2026-05-04.md`). Three Type Y archive cross-pollutions where the original `fix_archive_pairings` title-check passed (the archive's neutral cite was on the linked opinion's row) but only because that neutral cite was itself a stray contaminant — the archive HTML was actually for a same-day same-case-name follow-on opinion.

| Action | Source row | Target row | Archive | Stray cite removed |
|---|---|---|---|---|
| move | 13202 (2000 ND 138, *Disciplinary Board v. Keller* lead) | 13203 (2000 ND 141, *Disciplinary Board v. Keller* follow-on) | `archive/2000/20000189.htm` | `2000 ND 141` from 13202 |
| swap | 15805 (2012 ND 31, *Johnson v. Johnson*) | 15807 (2012 ND 27, *Johnson v. NDWSI*) | `archive/2012/20110159.htm` ↔ `archive/2012/20110213.htm` | `2012 ND 27` from 15805, `2012 ND 31` from 15807 |

Applied via `python -m ndcourts_mcp.fix_type_y_archive_pairings --apply`. 6 changelog rows: 3 archive linkage moves + 3 stray citation removals.

Post-fix verification:
- `13202`: cites `['2000 ND 138', '613 N.W.2d 510']`, no archive (correct — the lead's archive was missing all along, the move surfaced that).
- `13203`: cites `['2000 ND 141', '613 N.W.2d 511']`, archive `archive/2000/20000189.htm` (correctly linked now).
- `15805`: cites `['2012 ND 31', '812 N.W.2d 455']`, archive `archive/2012/20110213.htm` (matches the file's title).
- `15807`: cites `['2012 ND 27', '812 N.W.2d 467']`, archive `archive/2012/20110159.htm` (matches the file's title).
- Invariants dashboard: 13 ok / 2 baseline / 0 regressed (unchanged).
- Multi-source diff audit `<0.20` band: 93 → 90.

Two remaining Type Y candidates from the deep triage (`16488` Kleinsmith/Kitchen and `16829` Feldmann) are NOT in this batch. The Kleinsmith case has the additional complication that the linked archive HTML's title says "Reciprocal Discipline of *Kitchen*" while both DB rows are recorded as "Kleinsmith" — needs to determine whether the case_name is mis-recorded in the DB or whether Kitchen is a third opinion not in the DB at all. The Feldmann case (oid 16829) has its `source_path` itself pointing at the wrong markdown file (`2017ND255.md` instead of `2017ND1.md`), so `text_content` is also contaminated — needs a full row repair, separate from this batch. Both captured under TODO §3.

## Batch: fix-archive-pairings-2026-05-04 (37 rows)

Applied 2026-05-04. Surfaced by the multi-source diff audit (TODO §3) and reconciled by `ndcourts_mcp.fix_archive_pairings`, which indexes every archive HTML's `<title>` and compares the file's title-cite against the linked opinion's citations.

The script walked all 5,600 `opinion_sources WHERE source_reporter='archive'` rows. 5,566 were correctly linked. 34 were wrong:

| Action | Count | Description |
|---|---|---|
| detach | 27 | Linked file's title cites a different opinion that already has its own correct archive linkage. Just delete the wrong row. |
| swap | 3 | Linked file's title cites opinion C (which already has an archive), AND a different archive file in the index matches the original opinion W. Re-point the file to C; insert a new linkage for W → swap_path. Both opinions end up correctly linked. |
| move | 4 | Linked file's title cites C, C has no archive yet. Move the row from W to C. W loses its archive (no replacement available in the index). |

Common root cause: the archive scraper used a docket-number-based key that collided across cases sharing case names (e.g., serial *Estate of Feldmann* opinions at adjacent docket numbers). The fix is reversible — every change logged in the `changelog` table under `batch='fix-archive-pairings-2026-05-04'`.

Multi-source diff audit re-run after applying: <0.20 archive pairs dropped 111 → 93. The remaining 93 are archive HTMLs with correct titles but body text that disagrees with the primary source — likely truncated/stub HTML or primary-text issues, captured separately in TODO §3.

## Batch: align-source-path-2026-05-04 (3 rows)

Applied 2026-05-04. Surfaced by the new `ndcourts_mcp.invariants` dashboard, which flagged three opinions whose `opinions.source_path` pointed at a staging path (`input-data/vol52/...`) that no longer exists on disk while the corresponding primary `opinion_sources.source_path` correctly pointed at the canonical N.D./52/... archive path. Stale leftovers from the original vol52 Westlaw ingest that earlier `align_primary_source` runs missed.

| OID | Old `source_path` | New `source_path` |
|---|---|---|
| 3181 | `input-data/vol52/001 - Rogers Lumber Co v Schatzel.doc` | `/Users/jerod/refs/nd/opin/N.D./52/0844-Rogers-Lumber-Co-v-Schatzel.doc` |
| 3085 | `input-data/vol52/006 - Olsness v Baird.doc` | `/Users/jerod/refs/nd/opin/N.D./52/0064-Olsness-v-Baird.doc` |
| 3096 | `input-data/vol52/007 - State v First State Bank of Jud.doc` | `/Users/jerod/refs/nd/opin/N.D./52/0083-State-v-First-State-Bank-of-Jud.doc` |

Applied via `python -m ndcourts_mcp.align_primary_source --apply --batch align-source-path-2026-05-04` (3 source_path rewrites, 0 primary-flag flips, the existing `opinion_sources` rows already had the right paths and primary flags). Post-run dashboard: 13 ok, 2 at known baseline (258 §6 dup pairs, 85 §4 short orders), 0 regressions.

The dashboard catching this kind of drift is exactly the regression-detector role it's meant to play. Drop the `source_path_matches_primary` baseline back to 0 in `invariants.py` so any future drift fails loudly.

## Batch: westlaw-receive-2026-05-17 (747 rows) + westlaw-queue-clearwins-2026-05-17 (6 rows) + westlaw-receive-2026-05-17-handadj (57 rows)

Applied 2026-05-17. Gap-era (1953–1996) Westlaw Find&Print returns for worklist batch `2026-05-17` (291 opinions listed via `westlaw_worklist --apply`). 287 `.doc` files received (4 zips of 98/83/91/11 + 2 single docs Fuchs/Karabensh); 285 ND-parseable.

| Pass | Batch | Opinions | Changelog rows |
|---|---|---|---|
| Auto-promote + low-sim flag | `westlaw-receive-2026-05-17` | 249 promoted, 1 flagged | 747 |
| Surname clear-wins | `westlaw-queue-clearwins-2026-05-17` | 2 (337 N.W.2d 160→8950, 496 N.W.2d 24→11317) | 6 |
| Hand-adjudicated shared-page pairs | `westlaw-receive-2026-05-17-handadj` | 19 (explicit-oid promote) | 57 |

**270 opinions** migrated to authoritative Westlaw bound text (`source_reporter='westlaw'`, primary). Each promote logs `text_content` + `source_reporter` + `source_path` to the `changelog` table; all three batches are revertible via `cleanup revert <batch>`. Pre-batch snapshot `opinions.db.bak-pre-receive-2026-05-17`. `align_primary_source --apply` a no-op (0 rewrites/flips). Invariants: 13 ok / 2 at known baseline / **0 regressed** after each pass. Corpus row count unchanged (20,256 — all promotes, no inserts).

Hand-adjudicated 19 (caption + date confirmed, decisive text-jaccard separation vs the page-mate): 73 N.W.2d 782 Gunsch→14732 / Karabensh→14733; 176 N.W.2d 522 Fuchs→6846 / Giese→6847 (DB rows were tiny CL stubs — low jaccard is the stub being replaced; mapping is docket-decisive, Civ. 8581/8580); 378 N.W.2d 678 White→9519 / Williams→9520; 383 N.W.2d 813 United Bank→9594 / Kautzman→9595; 404 N.W.2d 50 Garcia→9875 / Miller→9878; 456 N.W.2d 772 Britton→10656 / Palda→10657; 469 N.W.2d 801 Ebach→10874 / Schumacher→10873; 519 N.W.2d 311 Voigt→11698 / Nassif→11699; 525 N.W.2d 250 Morehouse→11803 / Kieffer→11804; 472 N.W.2d 914 Rorvig→10933.

Not promoted (held for manual / §6): 472 N.W.2d 914 Johnson + 481 N.W.2d 225 Johnson (§6 dup-row pairs 10931/10932, 11075/11076 — blocked on §6 dedup); 109 N.W.2d 249 Healy (lead-vs-rehearing name/date conflict, j non-decisive); 505 N.W.2d 749 Schmidt oid 11479 (LOW_SIM j=0.01, receive-flagged); remaining category-B §6 dup pairs (auto-resolve after §6 + receive re-run). 2 docs were Nebraska (218 Neb. 539/556) and correctly rejected as non-ND; the ND opinion at 356 N.W.2d 890 (oid 9237 *First Federal S&L v. Scherle*) is unaffected — DB cite confirmed correct by the coherent ND pagination run 889/890/893, needs a future name-based re-pull only. Full triage: `triage/westlaw-shared-cite-followups-2026-05-17.md`.

Note: the prior-session `westlaw-*-2026-05-16` batches (handoff state, 488 promoted) are in the in-DB `changelog` table but were not written up here; their detail lives in the `.remember/` handoff and `triage/*-2026-05-16.*`. Auditable via `SELECT ... FROM changelog WHERE batch LIKE '%2026-05-16%'`.

## Batch: section6-handadj-2026-05-17 (31 rows, 14 row deletions)

Applied 2026-05-17. Targeted §6 duplicate-row merges for the clean tranche of the 45 Westlaw-receive-blocked pairs. The corpus-wide engine (`merge_opinions`) drained the auto-mergeable ≥0.85 band in the prior session and won't auto-pick these (both rows carry inbound `cited_by`, so its keep=cb0-re-ingest rule doesn't fire), so these were merged via `merge_pair()` with a hand-resolved keep row.

**Scope:** the 45 §6-blocked oids → 28 pairs → 19 true-dup (j≥0.55) / 9 distinct-page-mate (must NOT merge). Of the 19 true-dups, **14 clean simple pairs applied**; deferred: `57 N.W.2d 242` (3-row cluster), `344 N.W.2d 489` Anderson (same-name, j=0.70 borderline), `521 N.W.2d 643` Hosman (multi-row cluster w/ distinct Ferris). `472 N.W.2d 914` auto-rejected by the exactly-2-rows guard (3 rows: Johnson dup + the already-promoted Rorvig).

**Keep-row policy** (approved): keep = row with more inbound `cited_by`; tie → longer `text_content` (the survivor's text is retained, drop's discarded); tie → lower oid. **Refinement applied:** `merge_pair` keeps the survivor's text, so where exactly one row was `source_reporter='westlaw'` (authoritative bound text) and the other not, keep was flipped to the Westlaw row to avoid discarding bound text — affected 1 pair, `466 N.W.2d 114` (keep flipped to 10803; `cited_by` is preserved either way since `merge_pair` unions both directions). `canonical_name = _canonical_name(keep.case_name)` (conservative — only the safe probate transform; caption cleanup deferred to the tracked §1 case-name pass), except `466 N.W.2d 114` set to `Whitaker v. Century 21` (human-verified from the opinion text — CL truncated to "Whitaker", Westlaw misparsed first name "Walter" as surname; not a regex guess).

| cite | keep | drop (deleted) |
|---|---|---|
| 532 N.W.2d 59 | 11924 | 11923 |
| 385 N.W.2d 102 | 9611 | 9610 |
| 466 N.W.2d 114 | 10803 (westlaw) | 10804 |
| 337 N.W.2d 160 | 8950 | 8949 |
| 549 N.W.2d 196 | 12201 | 12200 |
| 481 N.W.2d 225 | 11076 | 11075 |
| 496 N.W.2d 24 | 11317 | 11316 |
| 528 N.W.2d 369 | 11847 | 11846 |
| 58 N.W.2d 278 | 12694 | 12693 |
| 506 N.W.2d 402 | 11486 | 11485 |
| 549 N.W.2d 671 | 12204 | 12203 |
| 519 N.W.2d 301 | 11695 | 11694 |
| 546 N.W.2d 366 | 12165 | 12164 |
| 517 N.W.2d 631 | 11660 | 11659 |

Changelog: 31 rows (14 `merge.absorbed` audit rows attributed to survivors, 12 `judges` best-of-breed, 4 `author`, 1 `case_name` — the 466 verified caption). Corpus 20256 → **20242**. Verification: `align_primary_source --apply` (10 source_path rewrites + 4 primary-flag flips at merge time, 0 after receive re-run), invariants **13 ok / 2 baseline / 0 regressed**, **0 orphan refs** across citations/opinion_sources/cited_by/text_citations/changelog. `neutral_cite_uniqueness` stayed Δ=0 (correct — these are pre-1997 N.W.2d opinions with no `YYYY ND n` neutral cite; the 258 baseline is post-1997 DEFER_MODERN territory).

**Reversibility: NOT changelog-revertible.** `merge_pair` does `DELETE FROM opinions` for each drop row; recovery is snapshot-only from `opinions.db.bak-pre-s6-handadj-2026-05-17`.

Payoff: a `receive_westlaw` re-run then auto-promoted 7 of the merged survivors to Westlaw bound text (385, 337, 496, 528, 506, 519, 517 N.W.2d cites) — previously permanently blocked by the dup pair. `481 N.W.2d 225` correctly held LOW_SIM (the Johnson doc genuinely doesn't match the survivor text, j≈0.004). 6 merged cites have no doc in the 2026-05-17 incoming and will fill on a future pull.

## Batch: section6-handadj-trio-2026-05-17 (7 rows, 3 row deletions)

Applied 2026-05-17. The "borderline trio" deferred from `section6-handadj-2026-05-17` (`triage/section6-deferred-2026-05-17.md`): same caption + same date but sub-threshold jaccard, undecidable from jaccard alone. Resolved by reading both full texts of each pair — **all three are true duplicates** (verbatim-identical judicial text; the low jaccard was an artifact of one row carrying the attorney/caption header block the other lacks, plus short opinions):

| cite | keep | drop (deleted) | j | classification basis |
|---|---|---|---|---|
| 344 N.W.2d 489 | 9059 | 9058 | 0.70 | identical PER CURIAM body, same docket Civ. 10509, panel, "appeal dismissed / Striegel v. Dakota Hills" |
| 489 N.W.2d 885 | 11201 | 11200 | 0.54 | identical Levine opinion, same docket Civ. 920066, "affirm per Rule 35.1(a)(7) / Kummer v. Backes" |
| 539 N.W.2d 869 | 12028 | 12027 | 0.39 | same 7-defendant consolidated double-jeopardy opinion, dockets Cr. 950236-950242, Sandstrom, "reverse and remand / State v. Zimmerman" |

Note: `539 N.W.2d 869` had been *leaned "distinct"* in the deferral doc on the jaccard signal alone; reading the text corrected that to a clear dup (the long repetitive multi-party caption inflated one side's word count). Vindicates the "read both texts, don't guess from jaccard" rule.

Keep policy: all three pairs are cb1/cb1 ties with neither row `source_reporter='westlaw'` → tie-break on longer `text_content` (keep the fuller row that carries the attorney block). `canonical_name = _canonical_name(keep)` — all three already clean party captions, unchanged. Changelog: 7 rows (3 `merge.absorbed`, 3 `judges`, 1 `author`). Corpus 20242 → **20239**.

Verification: `align_primary_source --apply` (3 source_path rewrites, 0 after receive re-run), invariants **13 ok / 2 baseline / 0 regressed**, **0 orphan refs**. **NOT changelog-revertible** — snapshot `opinions.db.bak-pre-s6-trio-2026-05-17` is the only recovery path. Payoff: the `receive_westlaw` re-run auto-promoted **all 3 survivors** (9059, 11201, 12028) to Westlaw bound text — the trio's `§6`-blocked status is fully cleared.

## Batch: section6-handadj-clusters-2026-05-17 (11 rows, 6 row deletions)

Applied 2026-05-17. The 3 deferred multi-row clusters (`triage/section6-deferred-2026-05-17.md`). All texts read in full; every internal pair is a clean true-dup (same docket/author/disposition, identical judicial text; low jaccard = attorney-header-block artifact, same pattern as the trio). The cross-case pairs are genuine distinct page-mates and were NOT merged — they survive as separate rows sharing the N.W. page.

| cite | resolution | keep(s) | dropped (deleted) |
|---|---|---|---|
| 57 N.W.2d 242 | 3→1 true-dup cluster (one probate opinion captioned both *United States v. State* and *In re Heiden's Estate*; same File No. 7343, identical per curiam "appeal dismissed") | **12544** (westlaw, carries "Syllabus by the Court" — authoritative bound entry) | 12545, 12546 |
| 521 N.W.2d 643 | 4→2: two distinct Bulman-tort cases sharing the page, each duplicated | **11740** Hosman (Civ. 940054), **11741** Ferris (Civ. 940022) | 11738, 11739 |
| 489 N.W.2d 886 | 4→2: two distinct Backes DUI-license cases sharing the page, each duplicated | **11204** Woessner (Civ. 920071, VandeWalle), **11205** Putney (Civ. 920067, Meschke) | 11202, 11203 |

Keep policy: `57 N.W.2d 242` applied the westlaw-row refinement (12544 is the only `source_reporter='westlaw'` row and the only one with the full bound entry incl. Syllabus by the Court). The other four merges are cb1/cb1 ties with neither row westlaw → tie-break longer `text_content` (keep the fuller WL-derived row with the attorney block). `canonical_name = _canonical_name(keep)` — all unchanged (`United States v. State` not an "In Re X's Estate" form, so no probate transform; authoritative re-caption of 57 N.W.2d 242 deferred to the §1 case-name pass). Changelog: 11 rows (6 `merge.absorbed`, 4 `judges`, 1 `author`). Corpus 20239 → **20233**.

Verification: `align_primary_source --apply` (4 source_path rewrites + 1 primary-flag flip at merge time, 0 after receive re-run), invariants **13 ok / 2 baseline / 0 regressed**, **0 orphan refs**. **NOT changelog-revertible** — snapshot `opinions.db.bak-pre-s6-clusters-2026-05-17` is the only recovery path. Payoff: the `receive_westlaw` re-run auto-promoted `12544`, `11740` (Hosman) and `11741` (Ferris) to Westlaw bound text; `11204` (Woessner) / `11205` (Putney) de-duped correctly but have no doc in the 2026-05-17 incoming — they fill on a future pull. All 3 clusters' `§6`-blocked status cleared.

## Batch: section6-handadj-pagemates-2026-05-17 (2 merge rows) + westlaw-receive-2026-05-17-pagemates (6 rows)

Applied 2026-05-17. Resolution of the deferred "9 distinct page-mates" line. Reading the texts showed that line was **stale and partly misclassified**: 6 of the original cites (Fuchs/Giese, United Bank/Kautzman, Britton/Palda, Schumacher/Ebach, Morehouse/Kieffer, Gunsch/Karabensh) were already fully resolved by the earlier `westlaw-receive-2026-05-17-handadj` category-A pass (both page-mates carry bound text), and two more were dissolved by the trio/cluster merges. The genuine still-open set resolved three ways:

**(a) Two misclassified true-dups → merged** (`section6-handadj-pagemates-2026-05-17`, snapshot `opinions.db.bak-pre-s6-pagemates-2026-05-17`, NOT changelog-revertible). Both were CL double-ingests with `date_filed` drift, not distinct page-mates — reading the texts proved it (same docket, same opinion text):
- `109 N.W.2d 249` — 6148→**6147**. *Claim of S.A. Healy Co. v. N.D. Workmen's Comp. Bureau*, File No. 7904; both rows carry the identical main opinion + "On Petition for Rehearing … we adhere to our former opinion." 6147 dated 1960-11-16 (decision), 6148 dated 1961-05-26 (rehearing) — same published entry.
- `263 N.W.2d 114` — 7819→**7818**. *In Interest of D.S. / Garaas v. D.S.*, Civ. 9383, Paulson J.; same opinion, 7818 dated 1978-02-16 (decision), 7819 dated 1978-03-02.

  **Keep-date deviation from policy** (flagged): the approved tiebreak is longer text, which would pick 6148/7819; instead kept 6147/7818 because they carry the correct *decision* `date_filed` and `merge_pair` preserves the survivor's date. Text-length tiebreak is moot here — the Westlaw bound doc replaces the survivor text on the receive re-run regardless. Both survivors then auto-promoted to Westlaw bound text (their full opinion+rehearing docs were in the 2026-05-17 incoming).

**(b) Genuine distinct page-mates, both docs in hand → explicit-promote** (`westlaw-receive-2026-05-17-pagemates`, changelog-revertible): `489 N.W.2d 886` — Woessner doc → 11204 (j=0.64), Putney doc → 11205 (j=0.64). Two distinct Backes DUI cases (Civ. 920071 VandeWalle / Civ. 920067 Meschke) sharing the page; the cluster merge had kept them as 2 distinct survivors, and their own docs were both present so each was promoted to its correct oid.

**(c) Genuine distinct, no doc in batch → left correctly queued** (no action, not blocked): `356 N.W.2d 897` 9240 *Calavera v. Vix* (9241 *Bauer v. Bauer* already promoted; Calavera is a distinct page-mate whose doc was not pulled), `536 N.W.2d 354` 11968 *Sletten* + 11969 *Moosbrugger* (distinct disciplinary, different dockets, no docs in the 2026-05-17 incoming). All three remain listed-unreceived and will re-list for their own Westlaw pull via the pool-aging fix — they are NOT data errors, just awaiting their own bound text.

Corpus 20233 → **20231** (2 merges; the 4 promotes add no rows). Verification: `align_primary_source` 0 rewrites/flips, invariants **13 ok / 2 baseline / 0 regressed**, **0 orphan refs**. `receive_westlaw` re-run promoted 263→265 (the 2 merged survivors). Net: 6147, 7818, 11204, 11205 all now carry Westlaw bound text with correct `date_filed`.

## Batch: s6-481-johnson-resolve-2026-05-17 (1 row, no row/text change)

Applied 2026-05-17. Last §6-deferred item: `481 N.W.2d 225` *Disc. Bd. v. Johnson* oid 11076, flagged LOW_SIM (j=0.004) by `westlaw-receive-2026-05-17`.

**Diagnosis: parser gap, not a data error.** 11076 already holds the complete, clean disbarment order (3393 ch — full ORDER OF DISBARMENT + all four justice signatures; disciplinary orders are short, so CL's text is not OCR-degraded). The Westlaw doc is unmistakably the *same* opinion (same cite, date 1992-02-12, docket 920029, parties, ORDER OF DISBARMENT, identical Erickstad/VandeWalle/Meschke/Levine signatures). The j=0.004 is a parser-extraction artifact: `_parse` returns `opinion_text=''` and `full_bound_text=` only the 349-char Westlaw editorial *Synopsis* for the "ORDER OF DISBARMENT" format (no Opinion/Justice-author header before the order body), so the similarity was synopsis-vs-order, meaningless.

Resolution (no row/text mutation — bookkeeping only, fully reversible): the Westlaw bound doc independently confirms caption + docket 920029 + date + disposition + all four signatures verbatim, which satisfies cross-source validation even though the text body is not swapped (the doc parses to only the editorial Synopsis, which is stripped per redistribution policy anyway; the CL text is already the complete clean order). `validation_status.crosscheck_state` flagged → **corrected** (note records the rationale), `sources_seen=["NW2d","westlaw-confirmed"]`, `review_flags` row deleted, `westlaw_requests.received_at` set with `received_path` = the archived doc. Changelog: 1 row (`validation.crosscheck_state`). Invariants **13 ok / 0 regressed**. No snapshot needed (no `opinions` row/text change).

**Follow-up flagged (parser gap, corpus-wide):** the disciplinary "ORDER OF DISBARMENT/SUSPENSION" format (per-curiam order with no Opinion/Justice-author header) defeats `_parse`/`_parse_westlaw_doc` body extraction — they yield `opinion_text=''` + Synopsis-only `full_bound_text`. In the 2026-05-17 incoming this signature hit exactly 2 docs: `37 Johnson` (this item) and `44 Schmidt` = the *other* batch LOW_SIM, `505 N.W.2d 749` *Disc. Bd. v. Schmidt* oid 11479. So 11479 is almost certainly the identical situation (complete clean CL order + same-opinion Westlaw doc that won't parse), resolvable the same way after a confirmatory read. Root-cause option: teach the Westlaw parser an order-format body extractor (after the headnotes/synopsis block, ending at the justice signatures) so future disciplinary-order Find&Print returns promote normally instead of LOW_SIM-flagging. Tracked in TODO §6 and `triage/section6-deferred-2026-05-17.md`.

## Batch: westlaw-receive-2026-05-17 (parser fix re-run — Johnson + Schmidt promoted)

Applied 2026-05-17. Root-cause fix for the disciplinary ORDER-format parser gap surfaced by the 481 N.W.2d 225 Johnson item, plus its sibling 505 N.W.2d 749 Schmidt.

**Code fix** (`ingest_westlaw.py`, `_extract_full_bound_text`): disciplinary / per-curiam ORDER docs (disbarment, suspension, discipline, reprimand) have no `Opinion` header or Justice-author line — the court's published text begins at an `ORDER OF …` / `ORDER FOR …` line. The West Headnotes DROP-skip only stopped at `_ALL_HEADERS`, so with no such header before All Citations it consumed the entire order body, leaving `full_bound_text` = editorial Synopsis only (→ spurious LOW_SIM on receive). Added module-level `_ORDER_BODY_RE = ^\*?\d*\s*ORDER\s+(?:OF|FOR)\b` and made the DROP-skip also stop at it. Tight by design (requires `ORDER` + ws + OF/FOR — prose "In order to…" / "ORDERED," do not match).

**Regression verification:** parsed all 285 docs in the 2026-05-17 incoming before/after — exactly **2 changed** (`37 Johnson` full_bound_text 349→3325, `44 Schmidt` 693→5272), the other 283 byte-identical. Corpus safety scan: 400-doc random sample from `~/refs/nd/opin/{N.W.2d,N.W.,N.D.}` (pool 7,724) — only 2 docs contain any `ORDER OF/FOR` line and **0** have one inside a West-Headnotes drop region, so the change cannot alter any normally-parsed opinion.

**Data effect:** `receive_westlaw` re-run dry-run `low_sim` 2 → **0**; both `481 N.W.2d 225` *Disc. Bd. v. Johnson* (oid 11076) and `505 N.W.2d 749` *Disc. Bd. v. Schmidt* (oid 11479) now MATCH and were promoted to Westlaw bound text (`source_reporter='westlaw'`, `crosscheck_state='corrected'`). Johnson thereby upgrades from the earlier bookkeeping-only confirmation (`s6-481-johnson-resolve-2026-05-17`) to the actual bound text; Schmidt's prior LOW_SIM flag is resolved. Changelog rows under batch `westlaw-receive-2026-05-17`; promotes are changelog-revertible. Corpus unchanged (20231). Invariants **13 ok / 2 baseline / 0 regressed**, align 0 rewrites/flips.

Forward-looking: future disciplinary-order Find&Print returns now promote normally instead of LOW_SIM-flagging. `505 N.W.2d 749` is no longer a separate open item.

## Batch: fix-cite-discrepancy-2026-05-17 (30 rows)

Applied 2026-05-17. Surfaced by the corpus-wide Type Y sweep (`sweep_type_y`, batch `triage/type-y-sweep-2026-05-17.tsv`): 37 cases where a westlaw-`.doc`-paired opinion's DB N.W. parallel cite disagreed with the Westlaw bound "All Citations" footer at jaccard=1.00 (literally the same opinion). Not Type Y — citation-accuracy bugs (OCR/CL-metadata wrong digits). All 37 pre-1953.

Adjudication (read-only, `_classify`-style): authority = Westlaw "All Citations" footer, corroborated by (a) the doc's N.D. cite matching the DB row's N.D. cite for all 37 (correct opinion pairing), (b) jaccard=1.00 same text, (c) era-plausibility on the volume-error cases (e.g. oid 5092/5093 DB `338 N.W.` for a 1912 opinion is structurally impossible — `138 N.W.` is correct). Safety gate: skip if the corrected cite already belongs to a *different* opinion (collision ⇒ not a simple typo).

**30 SAFE — corrected** (`UPDATE citations`, changelog-revertible, no row/text deletes): oids 2, 33, 136, 151, 159, 166, 167, 181, 247, 443, 618, 713, 841, 1677, 2374, 2663, 2671, 2740, 3482, 5092, 5093, 5222, 5858, 5941, 5972, 6024, 9825, 11208, 11213, 11406. Each: the wrong N.W. parallel cite string replaced with the Westlaw footer cite (is_primary/reporter preserved). Examples: `100 N.W. 108`→`708` (oid 2, 1↔7), `338 N.W. 7`→`138` (5092, leading digit), `54 N.W. 195`→`154` (5222, dropped "1"), `40 N.W.2d 102`→`49` (9825). Invariants 13 ok / 2 baseline / **0 regressed**.

**7 FLAGGED — not auto-applied** (corrected cite already on another, usually adjacent, oid → likely shared-page/companion, lead+rehearing, or CL double-ingest, not a typo): oids 6023 (→5982), 107 (→68), 190 (→189), 2167 (→2169/2170/2171), 2795 (→2826), and the 2 `DB_NO_NW` 4008 (→4009) / 4062 (→4063). Captured in `triage/cite-discrepancy-flagged-2026-05-17.md` for per-item review (§6-flavored).

Known cosmetic lag: the wrong cite may still appear in the opinion's `text_content` YAML frontmatter (display-only; the authoritative `citations` table — what lookup/FTS use — is now correct). Frontmatter re-render is a separate cleanup, not a correctness issue.

## Batch: fix-cite-discrepancy-flagged-2026-05-17 (4 rows) + fix-middlewest-pairings-2026-05-17 + section6-flagged-collisions-2026-05-17 (2 merges)

Applied 2026-05-17. Per-item human review (in Word) of the 7 flagged cite-collisions from `triage/cite-discrepancy-flagged-2026-05-17.md`. They split three ways:

- **Distinct opinions legitimately sharing an N.W. reporter page** (cite fix safe; shared cite is correct) — user-confirmed each: **#1** 6023 *Sykes v. Allen* `98 N.W. 1134`→`96 N.W. 1134` (shares page w/ 5982 *Montgomery v. Tucker*, both `12 N.D. 504`); **#2** 107 *State v. Gearhart* `103 N.W. 880`→`102 N.W. 880` (w/ 68 *Beidler & Robinson Lumber*, diff N.D. pages); **#3** 190 *Walker v. Stimmel* `107 N.W. 1083`→`107 N.W. 1081` (w/ 189 *Tamlyn v. Peterson*); **#5** 2795 *Olness v. Duffy* `193 N.W. 113`→`194 N.W. 113` (w/ 2826 *Weigel v. Powers Elevator*). Authority = each opinion's own Westlaw "All Citations" footer. Batch `fix-cite-discrepancy-flagged-2026-05-17`, changelog-revertible.
- **#4 pairing scramble (no cite change)** — `fix-middlewest-pairings-2026-05-17`. 2167 *Olson v. Middlewest Grain* was paired to `0250-Nelson...doc`; the unpaired `0250-Olson...doc` existed on disk; 2169 *Nelson@250* had no doc. Re-promoted 2167 from the correct Olson doc and 2169 from the freed Nelson doc (explicit-oid `_promote`). Cites were already correct (`44 N.D. 250 / 173 N.W. 474` and `…/475`); the bug was the `.doc` pairing. Each Middlewest companion now its own correctly-paired record.
- **#6/#7 §6 CL-double-ingest dups** — `section6-flagged-collisions-2026-05-17`, snapshot `opinions.db.bak-pre-s6-flagged-2026-05-17`, NOT changelog-revertible. `4009→4008` *State v. Ligaarden*, `4063→4062` *Ellis v. Fiske* (jaccard 0.74/0.67, same name/date/N.D./A.L.R.; partner had no Westlaw doc). Kept the Westlaw-bound row (authoritative-text refinement); survivor inherits the N.W. cite via re-point — resolving the `DB_NO_NW` too. Corpus 20231 → 20229.

Invariants 13 ok / 0 regressed / 0 orphan at each step. All 37 Type-Y-sweep cite bugs now resolved (30 SAFE + 7 flagged).

## Batch: fix-dup-citation-rows-2026-05-17 (308 changelog rows; 292 citation + 16 opinion_sources duplicate rows removed)

Applied 2026-05-17. **Root-cause defect found:** `merge_opinions._dedup_simple` (used for the `citations`/`opinion_sources`/`changelog` re-point in every `merge_pair`) is a blind `UPDATE opinion_id` — its name notwithstanding it does NO dedup. Whenever a merged pair shared a citation or source_path (the *normal* case for duplicate opinions), the survivor got duplicate `(opinion_id, citation)` / `(opinion_id, source_path)` rows, including conflicting `is_primary`. Pre-existing and corpus-wide: **256 opinions / 291 citation dup-pairs** (all of this session's 26 `merge_pair` survivors + ~230 from prior-session §6 merges, which used the same code) + **16 opinion_sources dup-pairs**. Invariants never caught it (no per-opinion uniqueness check).

Fixes (3 parts):
1. **Code root cause** (`merge_opinions.py`): `citations` and `opinion_sources` re-point now uses `_repoint_unique` keyed on `(opinion_id, citation)` / `(opinion_id, source_path)` — deletes drop rows colliding with a keep row, then re-points the rest. `changelog` stays blind `UPDATE` (append-only audit log — many rows per opinion are correct).
2. **Corpus cleanup** (this batch): per duplicate group, kept the `is_primary`-preferring lowest-id row, deleted the rest (292 citation rows across 291 groups — one group had 3; 16 opinion_sources rows), each deletion logged to `changelog` (changelog-revertible). Distinct opinions sharing a cite were **not** touched (key is per-opinion). Snapshot `opinions.db.bak-pre-dupcite-2026-05-17`.
3. **New invariants** (`invariants.py`): `citation_row_unique_per_opinion` and `source_row_unique_per_opinion` — both keyed per-opinion so they never flag legitimate cross-opinion shared cites; both now pass (0). Dashboard now 15 ok / 2 baseline / 0 regressed.

Surfaced but NOT fixed here (separate, needs a documented contract): **817 opinions carry >1 `is_primary=1` citation row** — the undocumented `is_primary` contract / A.L.R.-class mis-flagging. Tracked as the A.L.R. follow-up below.
