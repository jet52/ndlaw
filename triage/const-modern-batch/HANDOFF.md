# HANDOFF — ND Constitution point-in-time reconstruction

Written 2026-06-14 for a fresh agent picking up this work. Read this fully before
acting. The standing project plan is `TODO-const-history-validation.md`; the modern
design + decisions are `data/design-modern-const-versions-2026-06-14.md`.

---

## 0. The goal
Make `constitution.db` return the correct constitutional text **as of any date**
from 1889→present (point-in-time versioning), to a standard the ND Supreme Court
could adopt as authoritative. A provision is "versioned" when its
`provision_versions` rows form a gap-free timeline reflecting each amendment.

## 1. State of the two layers
- **Historical layer (1889–1980): DONE, LIVE, VALIDATED.** Built from session-law
  text (`ingest_constitution_history` ← `data/constitution_amendments.json`). 265
  provisions, real multi-version timelines. The 4 structural amendments + Amendment
  I were closed this session and are **live** in `constitution.db`. Validated by the
  snapshot-diff harness: **1925 = 99.5%, 1973 = 97%** match-or-near vs the printed
  Blue Books. Do NOT redo this.
- **Modern layer (1981–present): IN PROGRESS.** ndconst.org gives only *current*
  text, so each modern provision shipped as a single flat version. We are
  reconstructing prior versions from the session-law **redline** PDFs. 96 modern
  provisions have post-1981 amendments; **19 are reconstructed so far (on scratch
  only)**; the live DB's modern layer is still flat (no regression, no live modern
  reconstructions yet).

## 2. THE TWO DATABASES — critical
- **LIVE: `constitution.db` + `constitution_history.db`** (repo root). Historical
  fixes are live here. Backups: `*.bak-pre-struct-2026-06-14`. JSON backup:
  `data/constitution_amendments.json.bak-pre-struct-2026-06-14`.
- **SCRATCH: `/tmp/const-scratch.db`** — the working copy with EVERYTHING (historical
  + all 19 modern reconstructions). **⚠️ `/tmp` is ephemeral — this file may be gone.**
  If missing, rebuild it: `cp constitution.db /tmp/const-scratch.db`, then re-apply
  the modern reconstructions (their SOURCE OF TRUTH is the edit-lists in code, not
  the DB):
  - the 6 earlier: `triage/const-pilot-2026-06-14/transcriptions.json` via
    `apply_markup.py --apply` (+ art X §21 is in that file).
  - the 13 wave-1: `triage/const-modern-batch/verify_and_splice.py --apply`.
  Modern reconstructions are NEVER lost as long as those two files survive.

## 3. How modern reconstruction works (the method)
A redline measure shows **strikethrough = DELETED** (was in the prior, removed by
this amendment) and **underline = ADDED** (new in this amendment). The prior
version = current text with the redline reversed: **keep struck, drop underlined.**
We encode each provision as an **edit-list** `[[after_phrase, before_phrase], …]`
where `after_phrase` is a substring occurring EXACTLY ONCE in the current DB text,
and applying the list to current yields the prior. Then we **splice**: set the
current version's `effective_start = d1` (the amendment date) and insert a prior
version `[1981-01-01, d1-1]`.

### Non-negotiable verification (main context runs this; never trust a read alone)
1. **Mechanical:** each anchor unique; `apply(edit_list, current) == prior`.
2. **1981 Blue Book independent witness:** the prior must appear (normalized) in
   `~/refs/nd/const/processed/1981_blue-book_constitution.md`. THIS GATE CAUGHT A
   40% ERROR RATE in solo hand-reads — it is mandatory. **BUT the BB is only clean
   for articles VIII, X, XI** (others are letter-spacing-degraded OCR, e.g.
   `Sectio n 1 . Al l me n`, ocr_quality ~0.6). For degraded-BB articles there is no
   witness → such reads are flagged `needs-2nd-read` and go to SCRATCH ONLY, never
   live, until a confirming second independent read agrees.
3. **Structural:** no markup-flatten artifacts (`departmentbranches`), plausible
   length, classification consistent.

### Doctrine / gotchas (learned the hard way)
- **Render with `mutool draw`, NOT pdftoppm.** These session-law PDFs are AcroForms
  whose body text lives in form-field XObjects; pdftoppm/pdftotext DROP it, leaving
  blank pages with only the strike/underline rules. `prep.render()` is fixed to use
  mutool; do the same anywhere you rasterize these PDFs.
- **The #1 read error is keeping an ADDED (underlined) span in the prior.** Re-check
  every change against the image.
- **Classify before reconstructing:** REDLINE (reverse it) | CLEAN_REPRINT (prior
  not visible → needs 1981-base source) | CREATE_SECTION ("created and enacted" /
  "adding a new" → no prior, single version is correct) | SUBSECTION_PARTIAL (only
  some subsections reprinted) | UNREADABLE.
- **Heavy multi-subsection sections need NATIVE SOURCE, not redline reads:** art
  VIII §6 (and IX §12, VI §13, X §24) — both the redline and the 1981 BB are
  OCR-degraded past the authoritative bar. These wait on PL-SOURCE-FILES (request
  native files from Legislative Council). Do not hand-reconstruct them.
- **Preserve source verbatim** — spelling, punctuation, typos (e.g. art XI §29's
  "farmers and ranches" typo). Do not modernize.
- **Build sequence is NOT idempotent.** To rebuild: `ingest_constitution --apply`
  → `rm constitution_history.db; ingest_constitution_history --apply` →
  `merge_const_history --apply`. Historical corrections go UPSTREAM into
  `constitution_amendments.json`, not hand-edited into the DB.

## 4. The multi-agent campaign (how we're scaling the reads)
Design + agent spec: `triage/const-modern-batch/PROPOSAL.md`. Pipeline:
- `prep.py` — for each single-amendment modern provision: resolve CAA via
  `reconstruct_modern_versions.resolve_pdf`, locate the measure page(s)
  (`find_pages`), render to PNG (mutool), write per-provision records, split into
  `batch-N.json`. Skips → `skipped.json`.
- **Launch 8–10 `general-purpose` agents** (one per batch), each given: the spec
  path, its `batch-N.json` (citation, verbatim current_text, amendment date/number,
  png_paths, pdftext_hint), and the strict JSON output spec. Agents read the images,
  classify, and return prior_text + edit_list + confidence + flags.
- **Main context verifies** every result (the 3 gates above) and splices passing
  ones into scratch via the `verify_and_splice.py` pattern. BB-witnessed → accept;
  no-witness high-confidence → scratch + `needs-2nd-read`.

### Wave 1 (done): `RESULTS-wave1.md`
9 agents, 18 provisions → **13 REDLINE spliced to scratch** (3 BB-witnessed:
art X §9/§17, XI §25; 10 `needs-2nd-read`: art III §5/6/7, VI §13, IX §4/6/10,
XII §2/6, XIII §2), 2 CREATE_SECTION (art V §6, XI §29 — no splice needed), 3 to
re-do (art XII §1, XIII §1 medium-confidence images; art V §7 had the WRONG measure
attached — actually CREATE_SECTION). Integrity 0/0. Agents were reliable: 3/3
BB-checkable passed (vs 40% solo error).

## 5. WHAT TO DO NEXT (in order)
1. **Re-prep with the fixes.** `prep.py` render is fixed (mutool). Still TODO in
   `prep.py`/`resolve_pdf`: (a) glob `*IMA*.pdf` for initiated measures (art I §1,
   XI §25 sources); (b) harden `find_pages` (it mis-mapped pages in multi-chapter
   PDFs — match article AND the "Section N." reprint, verify the preamble names the
   right section, and skip "DISAPPROVED" chapters); (c) the 7 giant whole-session
   PDFs (`sl2021/2023/2025.pdf`, 2400pp) need a bounded locator (don't scan all
   pages). Re-run prep to recover the ~50 currently in `skipped.json`.
2. **Run the next 8–10-agent wave** over the newly-prepped batches PLUS confirming
   second-reads of Wave 1's 10 `needs-2nd-read` provisions (assign each to a
   different agent than implied; accept only on agreement).
3. **Verify every result yourself** (mechanical + BB + structural), splice to
   scratch. Repeat waves until single-amendment provisions are exhausted (~74 total,
   19 done).
4. **Multi-amendment provisions (22):** these need each intermediate version's
   reprint, not just one redline — chain them (see art X §21 in `transcriptions.json`
   for a clean 3-version example, and the art LIV trio for forward-splice). Later
   waves.
5. **Heavy multi-subsection (~4):** leave for native source (PL-SOURCE-FILES).
6. **Promote to live ONLY when:** every spliced modern provision has either a BB
   witness or a confirming second read, AND the snapshot-diff (extended to modern /
   current-ndconst.org) is green. Then propagate prior versions upstream and rebuild
   (do NOT hand-edit live). Until then, modern stays scratch-only.

## 6. Key files
- `TODO-const-history-validation.md` — standing plan (read the 2026-06-14 progress block).
- `data/design-modern-const-versions-2026-06-14.md` — modern design, all decisions
  (splice-not-subdivide; BB gate mandatory; BB-as-base ruled out for degraded arts;
  heavy→native source).
- `data/constitution_amendments.json` — canonical historical amendment data (now
  includes the structural four). `.bak-pre-struct-2026-06-14`.
- `scripts/reconstruct_modern_versions.py` — clean-reprint path + `resolve_pdf`
  (fixed for `sl<year>.pdf`; still needs IMA glob).
- `triage/const-pilot-2026-06-14/`:
  - `apply_markup.py` — redline edit-list splicer; `bb_gate` (the witness);
    `ocr_quality` guard; `base_text` (BB-as-base) support.
  - `transcriptions.json` — the 6 earlier reconstructions' edit-lists.
  - `snapshot_diff.py` — the acceptance-test harness (1925/1954/1973; autojunk=False;
    coverage metric). Point `DB` at the target.
  - `markup_worklist.py`, `modern_bb_base.py`, `phase1-results.md`,
    `B-proof-widening-findings.md` — earlier mechanism + findings.
- `triage/const-modern-batch/`:
  - `PROPOSAL.md` (agent spec), `prep.py`, `verify_and_splice.py` (wave-1 edit-lists
    + verifier + splicer), `RESULTS-wave1.md`, `batch-*.json`, `png/`, `skipped.json`.
- Memory: `project_const_modern_pointintime.md`, `project_const_history_ingest.md`.
- `CHANGELOG-data-primarylaw.md` — `const-struct-2026-06-14` (historical cutover).

## 7. Small open items
- **Amendment I** (Prohibition/§217 adoption) is a post-build insert in the live DBs,
  NOT in the JSON (the ingest has no event-only record type). A clean rebuild drops
  it. Fix: add an event-only adoption-record type to `ingest_constitution_history`.
- 54 modern provisions carry ndconst.org extraction artifacts (`])]`, stray `[`) in
  `text_content` — separate cleanup (agent VI §13's prior already strips its tail).
- Resolver still needs the `*IMA*` glob and giant-PDF locator (see §5.1).
