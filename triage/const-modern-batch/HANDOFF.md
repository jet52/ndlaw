# HANDOFF — ND Constitution point-in-time reconstruction

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
  reconstructions (37 provisions). **⚠️ `/tmp` is ephemeral.** If gone, rebuild:
  1. `cp constitution.db /tmp/const-scratch.db`
  2. Re-apply the reconstructions (source of truth = the edit-lists in code + `out*/`,
     never the scratch DB):
     - `triage/const-pilot-2026-06-14/apply_markup.py --apply` (6 pilot)
     - `triage/const-modern-batch/verify_and_splice.py --apply` (13 wave-1)
     - `triage/const-modern-batch/splice_wave2.py` (XII §2 fix + 3 new)
     - `triage/const-modern-batch/splice_multichain.py --apply` (12 chains)
     - `triage/const-modern-batch/splice_x26_2011.py --apply` (art X §26)
     - `triage/const-modern-batch/reconstruct_ix_stale.py --db /tmp/const-scratch.db --chain --apply` (art IX §12/§13)
     - `triage/const-modern-batch/splice_xii_corporations_2006.py --apply` (7 art XII corp repeals)
     - then `scripts/fix_amend167_legacyfund_2024.py /tmp/const-scratch.db --apply`,
       `scripts/apply_modern_text_corrections.py /tmp/const-scratch.db --apply`
  Use the project venv: `.venv/bin/python`.

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
   correctly return nothing. **Companion left open:** the [1981,1986) *old* art IV (former
   §§ 1-46 under the old modern-numbering) is not reconstructed — that's PL-CONST-CROSSWALK,
   bigger than §9-11. §§ 1-8, 12-16 were already correctly dated 1986-12-01.
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
- **Blue Book scans archived this session** (`~/refs/nd/const/`):
  `raw/{1981,1989,1973}_blue-book_ndbb-*.pdf`; extracted constitutions
  `processed/{1981_blue-book-ndbb,1989_blue-book}_constitution.md`. (1973 is pre-reorg
  = a historical witness; we already had one.) **Wanted:** a cleaner 1981 text and any
  1990s/2000s modern compilation for more interior witnesses.

## 7. Path to live (do NOT hand-edit live)
Promote the modern layer to live ONLY when: (a) every spliced provision has a BB
witness or a confirming second read (§3.4), AND (b) the modern snapshot-diff is green.
Then propagate the reconstructions UPSTREAM (into the ingest/data, like the corrections
overlays) and REBUILD — never hand-edit live. Build sequence (NOT idempotent for
history): `ingest_constitution --apply` → `rm constitution_history.db;
ingest_constitution_history --apply` → `merge_const_history --apply` → `make_release.sh`.

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
