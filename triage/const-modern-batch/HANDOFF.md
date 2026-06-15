# HANDOFF — ND Constitution point-in-time reconstruction

> **▶ NEXT TASKS (2026-06-15): see `HANDOFF-NEXT-orphans-and-live.md`** — the modern layer is
> substantively complete; remaining work is (1) the orphan tails, then (2) live promotion. This
> file is the campaign background/method reference.

Last updated 2026-06-15. Read this fully before acting. Standing plan:
`TODO-const-history-validation.md`. Design + decisions:
`data/design-modern-const-versions-2026-06-14.md`.

---

## 0. Goal
Make `constitution.db` return the correct constitutional text **as of any date**,
1889→present, from either citation scheme — to a standard the ND Supreme Court could
adopt as authoritative. A provision is "versioned" when its `provision_versions` rows
form a gap-free point-in-time timeline reflecting every amendment.

## 1. Current state (2026-06-15)

- **Historical layer (1889–1980): DONE, LIVE, validated.** Built from session-law
  text via `ingest_constitution_history` ← `data/constitution_amendments.json`. The 4
  structural amendments + Amendment I are live. Snapshot-diff vs printed Blue Books:
  1925 = 99.5%, 1973 = 97%. **Do not redo.**
- **Modern layer (1981–present): IN PROGRESS, SCRATCH-ONLY.** ndconst.org gives only
  *current* text, so each modern provision shipped as one flat version. We reconstruct
  prior versions from the session-law **redline** PDFs. **44 of 96** amended modern
  provisions reconstructed (in `/tmp/const-scratch.db`); **integrity 0 gaps**. The
  **live DB's modern layer is still flat** — no modern version-chains are live yet.
  (Live HAS received: the historical fixes, the amendment-chronology corrections, and
  three current-text corrections — see §5.)

## 2. THE TWO DATABASES — critical
- **LIVE: `constitution.db`** (repo root, gitignored — it's a build artifact). Holds
  the served data. This session corrected its amendment chronology + 3 current texts
  (§5) but its modern layer is still single-version-per-provision.
- **SCRATCH: `/tmp/const-scratch.db`** — the working copy with ALL modern
  reconstructions (44 provisions / +52 versions + in-place fixes). **⚠️ `/tmp` is ephemeral.**
- **ONE-COMMAND REBUILD (verified reproducible 2026-06-15):**
  `bash scripts/rebuild_const_modern.sh` — backs up any current scratch, copies
  `constitution.db` → scratch, replays every splice script in order, and asserts the
  rebuilt version-content signature == the validated scratch. Last run: **REPRODUCIBLE YES**
  (sig `4e37129438f0549d`, 678 versions, integrity 0). It does NOT re-fetch ndconst.org and
  does NOT promote (no write to `constitution.db`). The individual scripts (for reference):
  apply_markup → verify_and_splice → splice_wave2 → splice_multichain → splice_x26_2011 →
  reconstruct_ix_stale(--chain) → fix_amend167 → apply_modern_text_corrections →
  splice_xii_corporations_2006 → fix_artiv_renumber_1986 → fix_ix7_head_secondread.
  (`reconstruct_ix_stale.py` was hardened 2026-06-15 to accept an already-corrected base.)
  Use the project venv: `.venv/bin/python`.
- **NOTE (at promotion time):** the script-replay reproduces the layer today, but it is
  base-state-sensitive (the ix_stale fix was needed when base absorbed a correction). Before
  the eventual live promotion, snapshot the final layer declaratively
  (`data/const_modern_versions.json` + idempotent applier, mirroring
  `const_modern_text_corrections.json`) so the build is robust to base drift; keep the splice
  scripts as provenance. Deferred until the modern layer is COMPLETE (decision below).

## 3. What's been reconstructed (37) and what hasn't (the work left)

The 96 amended modern provisions break down:
- **Single-amendment set: COMPLETE.** 13 redline-reconstructed; **34 confirmed
  CREATE_SECTION** (new section/article → single version is already correct, no recon);
  12 needs-base-source. (`RESULTS-wave2.md`.)
- **Multi-amendment chains: 12 of 14 spliced** (`RESULTS-multi.md`). 2 discontinuities
  skipped — art V §1/§12 (the 1997 measure CREATED new sections; the earlier 1986
  amendment is on the old, repealed §1/§12 — different lineage).
- **art X §26, art IX §12/§13: reconstructed** this session.

### REMAINING WORK (prioritized)
1. **needs-base-source / native-source bucket** — blocked on source files (PL-SOURCE-FILES):
   - art V §1/§2-11/§12 — the 1997 executive-article **replacement** (pre-1997 text
     is a full-article rewrite, not in the redline; needs 1979-80 native text or the
     pre-1997 compilation).
   - art VIII §6 — heavy multi-subsection; both the redline and 1981 BB are OCR-degraded.
   - art I §1, art X §6, art XIII §1 — clean-reprint / bare-repeal (prior not visible).
2. ~~**art XII §§ 3/7/8/12/14/15/17** (corporations)~~ — **DONE 2026-06-15.** Pre-repeal
   text recovered (1981+1989 BB dual witness + 1925 cross-check), repealed eff. 2006-07-01
   (Legislative Council codified note; S.L. 2005 ch. 623). `splice_xii_corporations_2006.py`.
   Flipped all 7 MISMATCH→MATCH at both witnesses (1989 91.2%→95.6%). `ndconst-org-errors.md`
   row 6. Residual: confirm the measure's stated effective date (July 1 vs 30-day default)
   before live.
3. ~~**art IV §§ 9-11 — the 1985 art IV recreation gap.**~~ **DONE 2026-06-15.** It was a
   *renumber*, not a repeal: former §§ 14/15/19 → §§ 9/10/11 eff. 1986-12-01 (codifier
   note + 1981 BB). §9/§10 were falsely stamped 1889-10-01, §11 at 1981-01-01; all three
   moved to 1986-12-01 (`fix_artiv_renumber_1986.py`, row 7). Pre-1986 those citations
   correctly return nothing. **Companion (the [1981,1986) old art IV crosswalk): §§1-16 DONE
   2026-06-15** (`splice_artiv_crosswalk_1981.py`, `ARTIV-CROSSWALK-PLAN.md`) — prepended the
   old §N content (sourced from the validated historical layer via the derived art IV→1889 map,
   38/45 at ratio≥0.92; no Replacement Vol 13 needed) to each shared §1-16. Renumber crux
   verified (bribery §14→§9 across 1986). **Still open:** §§2/5/11 "[Unconstitutional.]" stubs +
   §§17-46 repealed-only (no modern citation). Reproducible (sig 26c3f13b1e907899, 691 versions).
4. ~~**Second-read pass (required before live).**~~ **DONE 2026-06-15.** All 10 owed items
   independently witnessed (`second_read_check.py` + the changelog batch
   `modern-ix7-secondread-2026-06-15`): 8 BB-witnessed (I §16, II §1, IX §1, IX §2, IX §10,
   IX §12, IX §13, XII §1), 1 measure-witnessed (X §26 vs 2011 CAA, overlap 1.0). **One real
   error found + fixed:** art IX §7 head kept an un-reversed 1982 addition ("for any specific
   educational or charitable institution") — corrected vs a quadruple witness (1981 BB + 1925
   §160 + 1954/1973 BB), `fix_ix7_head_secondread.py`. With §3.4 cleared, the gate to live is
   now only #1/#2 (the needs-base-source bucket + the art IV crosswalk companion) plus a
   clean snapshot-diff — see §7.

## 4. The reconstruction method (how it works)

A session-law measure is a **redline**: struck = DELETED by this amendment (was in the
prior), underlined = ADDED (not in the prior). The prior = current with the redline
reversed (keep struck, drop underlined). Encode each amendment as an **edit-list**
`[[after_phrase, before_phrase], …]` where each `after_phrase` occurs EXACTLY ONCE in
the version it applies to; applying the list yields the prior. Then **splice**.

- **Single amendment** → reverse against current; splice prior `[1981, d1)` (carried)
  or none (created).
- **Multi-amendment CHAIN** → walk LATEST→earliest: latest `version_after` must equal
  current; reverse each measure to get the version before it; the next-earlier
  measure's `version_after` must equal it (continuity). STOP at a CREATE (chain head).
  Carried provisions' earliest reversal = the `[1981, d1)` head.
- **Rendering:** use `mutool draw -r <dpi>` — these session-law PDFs are AcroForms whose
  body text lives in field XObjects that pdftotext/pdftoppm DROP. 200 dpi is often too
  small for redlines; agents should re-render at 400-500 dpi.

**Multi-agent campaign:** `prep.py` / `prep_multi.py` render measures → `batch-*.json`;
`general-purpose` agents read images and return edit-lists (strict JSON) → `out*/`; main
context VERIFIES every result before splicing. Agents are reliable on BB-checkable reads
(0% error vs 40% for solo hand-reads) — but NEVER trust a read without the gates.

### Verification gates (non-negotiable; main context runs these)
1. **Mechanical:** each anchor unique; `apply(edit_list, version_after) == version_before`.
2. **1981 Blue Book witness:** the prior must appear (normalized) in the 1981 BB where
   the article is clean (arts VIII/X/XI; others OCR-degraded → no witness → needs-2nd-read).
3. **Chain continuity:** consecutive versions connect; latest == current DB text.
4. **Structural:** no markup-flatten artifacts; plausible length; verbatim preserved.

## 5. Data errors & the reproducible-correction mechanisms

The reconstruction gates double as a data-quality audit of ndconst.org. **Running list:
`triage/ndconst-org-errors.md`.** Each error is corrected in our DBs reproducibly:
- **`AMENDMENT_AFFECTED_CORRECTIONS`**, **`_SOURCE_URL_CORRECTIONS`**,
  **`_EFFECTIVE_DATE_CORRECTIONS`** (dicts in `ndcourts_mcp/ingest_constitution.py`) —
  fix mislabeled amendment rows (167 affected→art X §26; 164 source→ima.pdf; 164
  effective→2023-01-01) before linking, so a clean rebuild reproduces them.
- **`data/const_modern_text_corrections.json`** + `ingest_constitution.apply_text_corrections`
  — override current-version text where ndconst.org is stale or corrupt (art IX §12/§13
  stale 2024 terminology; art VII §10 was a served 404 HTML page). Applier for built
  DBs: `scripts/apply_modern_text_corrections.py <db> --apply`. **FTS is external-content
  — delete rows via the `'delete'` command, not `DELETE FROM` (see the script).**
- **Effective-date rule** (verified from primary sources, full writeup
  `triage/const-amendment-effective-dates-2026-06-14.md`): default = **30 days after the
  election unless the measure states otherwise** (N.D. Const. art. III §8; rule set 1918;
  before 1918 = date of canvass). A measure's stated date controls. The DB's dates match
  the (user-reviewed) ndconst.org column and follow this rule; only 164 was wrong.

## 6. Validation — the snapshot-diff harnesses

- **Historical:** `triage/const-pilot-2026-06-14/snapshot_diff.py` (vs 1925/1954/1973). Green.
- **Modern:** `triage/const-modern-batch/snapshot_diff_modern.py` — reconstruct each
  modern provision as of T, diff vs a modern-scheme Blue Book. **Run: `.venv/bin/python
  triage/const-modern-batch/snapshot_diff_modern.py`. Re-run after every splice.**
  - **1989 (T=1989-07-01): 95.6% match-or-near** (was 90.6%; +art XII corp recon) — the
    dependable interior witness. Residual MISMATCH 3 = art IV §16 / VI §12 / X §5 (pre-existing
    formatting NEAR-misses). 1981: art XII MISMATCH 7→0.
  - 1981 (T=1981-01-01): the scan's microfilm OCR under-parses arts I/III/VI/IX, so its
    rate looks low (~50%); what parses matches. A cleaner 1981 text would raise it.
- **1989 BB re-extracted via marker OCR 2026-06-15** — `~/refs/nd/const/processed/1989_blue-book-marker_constitution.md`
  is the reliable 1989 witness now (the older `1989_blue-book_constitution.md` dropped art XIII §1's
  sub-3 tail at a page break and has letter-spacing garble). marker is complete + clean (MATCH 77→114).
  Regenerate: `~/.local/bin/marker_single ~/refs/nd/const/raw/1989_blue-book_ndbb-6361.pdf
  --page_range "66-97" --disable_image_extraction --output_dir <dir>` (0-indexed; PDF pages 67-98 =
  the constitution). The snapshot-diff harness points 1989 at this file.
- **Blue Book scans archived this session** (`~/refs/nd/const/`):
  `raw/{1981,1989,1973}_blue-book_ndbb-*.pdf`; extracted constitutions
  `processed/{1981_blue-book-ndbb,1989_blue-book}_constitution.md`. (1973 is pre-reorg
  = a historical witness; we already had one.) **Wanted:** a cleaner 1981 text and any
  1990s/2000s modern compilation for more interior witnesses.

## 7. Path to live (do NOT hand-edit live)
**DECISION 2026-06-15 (user): HOLD until the modern layer is COMPLETE; do not promote the
44 validated reconstructions incrementally. Local build + verify only — nothing outward-facing
(no GitHub release, no server deploy) until then.**

Gating conditions to promote: (a) every spliced provision has a BB witness or a confirming
second read — **§3.4 DONE**; (b) the modern snapshot-diff is green — currently 1989 95.6%,
1981 MISMATCH 0 (residual = OCR/parse, not data); (c) the remaining buckets are reconstructed:
**#1 needs-base-source (BLOCKED on native source files — PL-SOURCE-FILES) and the art IV
[1981,1986) crosswalk companion.** Build reproducibility is already PROVEN (§2,
`scripts/rebuild_const_modern.sh`, REPRODUCIBLE YES).

When promoting (all conditions met): snapshot the final layer to `data/const_modern_versions.json`
+ idempotent applier, fold into the build, REBUILD — never hand-edit live. Full build sequence
(NOT idempotent for history): `ingest_constitution --apply` → `rm constitution_history.db;
ingest_constitution_history --apply` → `merge_const_history --apply` →
`rebuild_const_modern.sh` (or the JSON applier) → `make_release.sh`.

## 8. Key files
- Plan/design: `TODO-const-history-validation.md`, `data/design-modern-const-versions-2026-06-14.md`.
- Results: `RESULTS-wave2.md` (single-amendment), `RESULTS-multi.md` (chains),
  `RESULTS-snapshot-diff.md` (validation). Error log: `triage/ndconst-org-errors.md`.
  Effective-date study: `triage/const-amendment-effective-dates-2026-06-14.md`.
- Splicers/tools: `prep.py`, `prep_multi.py`, `verify_and_splice.py`, `splice_wave2.py`,
  `splice_multichain.py`, `splice_x26_2011.py`, `reconstruct_ix_stale.py`,
  `snapshot_diff_modern.py` (all in `triage/const-modern-batch/`);
  `scripts/{fix_amend167_legacyfund_2024,apply_modern_text_corrections}.py`.
- Ingest: `ndcourts_mcp/ingest_constitution.py` (modern mirror + correction overlays),
  `ndcourts_mcp/ingest_constitution_history.py` (1889 layer).
- Changelog: `CHANGELOG-data-primarylaw.md`. Memory: `project_const_modern_pointintime.md`.

## 9. Doctrine / gotchas (learned the hard way)
- **Render with `mutool draw`, NOT pdftoppm/pdftotext** (AcroForm field text). Re-render
  at 400-500 dpi for redlines.
- **Resolve PDFs by the source_url's exact filename** (CAA = legislative referrals; IMA =
  initiated measures; INITM/CNSTM odd years). 2021+ sessions are giant whole-session PDFs.
- **The #1 read error: keeping an ADDED (underlined) span in the prior.** Re-check every change.
- **A CREATE ends a chain** ("a new section/article … created and enacted"). If CREATE
  is NOT the first amendment, it's a discontinuity (new section on an old citation) — skip.
- **Preserve source verbatim** — spelling, punctuation, typos. Don't modernize.
- **ndconst.org current text can be stale or a 404 page** — the "latest amendment's text
  == DB current" gate is the detector; corrections go in `const_modern_text_corrections.json`.
- **NEVER hand-edit live**; reconstructions live in scratch until promoted via rebuild.
