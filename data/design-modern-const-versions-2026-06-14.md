# Design — modern constitution point-in-time reconstruction (TODO-const #0)

Status: DRAFT 2026-06-14. Implements item **0** of `TODO-const-history-validation.md`
(found via the amendment-census prototype): the modern reorg layer (1981–present)
has no point-in-time depth — every modern provision has exactly one version, and the
~59 post-1981 amendments are recorded in `amendments` but never spliced into the
version timeline. Pilot (`triage/const-pilot-2026-06-14/`) proved the extract-and-
splice pipeline end-to-end on art. X §21 and mapped the hard cases.

## 0. Where it plugs in

`ingest_constitution.build()` already (a) writes ONE version per provision with
`effective_start = ORIGINAL_ADOPTION` (overwritten to the *latest* linked amendment
date by `ingest_amendments`), and (b) records the full 167-row chronology in
`amendments` with `effective_date` + `source_url` (CAA PDF + `#page`). The docstring
calls prior-version capture "a future enhancement." This design adds that step.

**Decision: a separate script, not inside `build()`.** `scripts/reconstruct_modern_versions.py`
run as **build step 1.5**, mirroring `scripts/merge_const_history.py`. Rationale:
PDF extraction is slow and source-bound (refs tree), the step must be independently
re-runnable and idempotent, and `build()` should stay a clean ndconst.org mirror.

Build sequence (updated):
1. `ingest_constitution --apply`            (modern mirror; 1 version/provision)
2. **`reconstruct_modern_versions --apply`**  ← NEW: splice post-1981 prior versions
3. `ingest_constitution_history --apply`    (`rm` first; historical 1889 layer)
4. `merge_const_history --apply`            (fold history into const.db)
5. `make_release.sh`

Step 2 only touches modern provisions' version timelines; it is independent of 3–4.

## 1. Source of truth (provenance-aligned)

Primary source = the canonical refs tree, already on disk:
`~/refs/nd/sess/<year>_sl/CAA.pdf` (Constitutional Amendments Approved) and
`.../CMA.pdf` (pre-1981 Constitutional Measures Approved). Newer cycles use other
names/paths (`55-1997/ranch/SL7CNSTM.pdf`, `66-2019/.../caa.pdf`) — a per-year
**source resolver** maps an amendment's `effective_date`/`source_url` to the on-disk
file, downloading into refs only on a miss. The `amendments.source_url` (public
ndlegis.gov link + `#page`) is retained as the citable pointer in each version row.

## 2. Version model & splice algorithm

For a modern provision with linked amendments at dates `d1 < d2 < … < dk`
(dk = current `effective_start`, set by `ingest_amendments`):

- The existing current version `V0 = [dk, ∞)` already holds the clean current text.
  **Keep it** (text + start). The gate (§4) confirms `CAA(dk) ≈ current text`.
- Insert priors `V_i = [d_i, d_{i+1})` for i = 1..k-1, `text = locate(CAA(d_i))`,
  `effective_end = d_{i+1} − 1 day`.
- **Head interval `[base, d1)`** depends on provision origin:
  - **Created at d1** (measure says "adding/creating a new article/section"; e.g. CIX
    created art. X §21 in 1981): no head interval — the provision begins at d1. Set
    `status` history accordingly.
  - **Carried from pre-1981** (existed at reorg, amended later): the `[1981-01-01, d1)`
    text is NOT derivable from CAA alone. **#0 leaves it as a flagged `pending_base`
    head-gap, closed by the crosswalk (#1)** linking to the historical old-§ provision,
    or optionally backfilled from the 1981 Blue Book (on disk; OCR — see Open decisions).

Unchanged-since-reorg provisions (105, single version, no linked post-1981 amendment)
are left as-is — their one version is correct.

## 3. The locator — `locate(pdf, citation, amendment) -> EnactedText | Unhandled`

The core new logic. Classify the measure by its preamble/operative verbs, then extract:

| Class | Signature | Extraction |
|---|---|---|
| **amend-reenact-section** | "Section N of article R … amended and reenacted to read as follows: Section N. …" | text from `Section N.` to next `SECTION`/`Approved`/effective-date marker |
| **create-article** | "create and enact a new article R … Section 1 … Section 2 …" (+ "repeal the present article R") | split into sections; route each to `art. R § i`; mark prior article's sections `superseded` at this date |
| **repeal-section** | "repeal … section N of article R" | provision → `status=repealed`, repeal-notice version |
| **described-edit** | "by adding the words … / by omitting the words …" (no reprint) | **Unhandled → bespoke queue** (pre-1981 structural four only; never in the modern bulk path) |

Locate by **content, not the `#page` anchor** (anchors are approximate; a measure may
create a provision without ever naming its final art./§ — CIX). Match on the resolution's
"amendment of section N of article R" preamble + the operative "Section N." reprint.

**Extraction escalation (REVISED after phase 1, 2026-06-14):**
1. `pdftotext -layout` — clean for ~1/3 of measures (those that reprint clean text).
2. **Markup detection** — ~2/3 of CAA reprints are legislative redlines (struck =
   deleted, underlined = added). pdftotext AND marker both FLATTEN these
   (`departmentbranches`, `noany`, `shallmay`) — neither captures strike/underline.
   Detect via the latest-amendment-vs-current gate (CLEAN vs MARKUP/MISMATCH) +
   a concatenation heuristic for priors.
3. **Claude direct read** of the rendered page — the ONLY method that resolves
   markup. Yields the clean post-amendment text AND the prior text in one read
   (the redline is the diff between consecutive versions). Use for every markup
   measure, not just edge cases.
4. marker OCR — reserve ONLY for the rare fi-ligature / scanned-image case
   (e.g. 1995 CAA); it does not help with markup.

Normalization before storage: collapse justification word-splits, repair the known
`fi`→`ft` ligature class, normalize whitespace. Preserve the court's text otherwise.

## 4. The gate (substantive, not byte) & failure policy

For each provision, `normalize(locate(CAA(dk))) == normalize(current_version_text)`
(token sequence, ligature-repaired). Pilot: 172/172 tokens.

- **Pass** → splice priors (§2). The current version's known-good text is never
  overwritten; CAA is used only for priors.
- **Fail** → **do not splice.** Preserve the provision's single current version, write
  the provision to `triage/modern-recon-gatefail-<date>.tsv` with both texts for review.
  Rationale: we never degrade authoritative current text because of an extraction defect
  or a locator miss. A gate fail means either a locator bug or a chronology/affected
  mismatch — both need eyes, not an automated write.

## 5. Idempotency

History ingest is NOT idempotent; this step **is**, by construction:
- All reconstructed versions carry `batch = 'modern-versions-<date>'`.
- On `--apply`, for each provision in scope: `DELETE FROM provision_versions WHERE
  provision_id=? AND batch LIKE 'modern-versions-%'`, restore the current version's
  `effective_start` to dk and `effective_end` to NULL, then re-splice. Upsert keyed on
  `(provision_id, effective_start)`.
- Re-running on an already-reconstructed DB reproduces it exactly (same refs PDFs).

## 6. Validation, provenance, changelog

- Each reconstructed version row: `text_content` (normalized CAA extract),
  `source_authority` = e.g. `"S.L. 1993, ch. 662 (amend. CXXIX)"`, `source_url` =
  the CAA `#page` link, `source_path` = the refs PDF, `batch`.
- One `changelog` row per inserted version (`field='version_splice'`, `new_value` =
  interval + amendment number, `authority` = session law). Honors "log every data change."
- `provenance` row summarizing counts + source tree.
- **Self-test after apply** — re-run the three integrity queries from
  TODO-const-history-validation.md (gaps / overlaps / >1-open) over `corpus='const'`.
  They become non-trivial once provisions are multi-version. Expected residue: the
  `pending_base` head-gaps for carried provisions (§2) — enumerated, not silent.

## 6a. Multi-subsection class + the verification decision (added 2026-06-14)

**Modeling DECISION: section-granularity whole-section versioning. No schema
change. No subsection-provisions.** A section like art. VIII §6 (10,630 chars,
amended at subsections 2 & 4 by 1994/1996/2000) is NOT a distinct modeling
problem. The DB already holds the full current section; an amendment — whole or
partial-subsection — is captured as an edit list reverse-applied to the full
current text, and the unchanged subsections carry through untouched. So
"multi-subsection" = the SAME edit-list-on-whole-section method already proven on
the 5 whole-section redlines (several of which changed multiple clauses). The
only differences are operational: the measure reprints only the changed
subsections (possibly across multiple pages → multi-page reads) and the edit
lists are larger.

**This resolves PL-CONST-STRUCTURAL's open "subdivide vs splice" question → SPLICE.**
Subsection-provisions would force a schema change, fracture FTS/citation/point-in-time
logic, require a subsection-citation scheme ND does not use canonically, and gain
nothing (point-in-time returns the whole section anyway). The structural four
(art. LIV subdivisions, §25 ¶10) get the same whole-provision splice in the
historical layer.

**Verification DECISION: the 1981 Blue Book independent gate is MANDATORY.**
- The markup splicer's internal gate (`after-newest == current`) is **vacuous** —
  trivially true, since priors are reverse-applied FROM current.
- Hand-reading redlines is error-prone: the 1981-BB gate **caught 2 of 5 (40%)**
  reconstructions with errors (art XI §16 and XI §4 each missed an underlined
  ADDITION, wrongly kept in the prior). Both fixed; all 5 now pass.
- The 1981 BB (`~/refs/nd/const/processed/1981_blue-book_constitution.md`) carries
  the renumbered constitution as of Jan 1981, so every single-amendment-since-1981
  provision's `[1981, d1)` base must appear verbatim (normalized substring). Wired
  into `apply_markup.bb_gate`.
- **Multi-amendment chains** (art VIII §6 = 1994/1996/2000): verification = (a) the
  `[1981, d1)` base matches the 1981 BB AND (b) the edit chain connects base→current
  (current is authoritative DB text). Intermediate versions are deterministic
  reverse-apply waypoints, consistent by construction. Residual risk: mis-attributing
  an edit to the wrong amendment date (correct base+current, wrong split) — mitigated
  by reading each amendment's measure separately.

**Validation status (present-day → 1981 chain confirmed 2026-06-14):**
- **CONFIRMED end-to-end:** art X §21 — a clean 3-version chain
  `[1981 create → 1990 → 1994 → present]`, base verified verbatim against 1981 BB
  §21. Plus the 5 single-amendment redlines, all 1981-BB-PASS. Global scratch
  integrity 0/0. The chain mechanism + independent gate work present→1981.
- **art VIII §6 = the boundary case + a process refinement.** Read all 3 measures
  (130/1994, 133/1996, 139/2000). 139 and 133 are clean full-subsection-2 reprints
  (139's only change: "one person"→"two persons"; 133: term 7→4 yrs + two-term
  limit + nominating-committee expansion). **130 (1994) massively rewrote
  subsection 2** with archaic transitional language (1939–1946 staggered terms) in
  heavily-OCR-garbled struck text. Reverse-applying ~30 hand-read edits through
  that is too error-prone for the authoritative bar.
  **REFINEMENT: for the heaviest sections, source the `[1981,d1)` base DIRECTLY
  from the 1981 Blue Book** rather than redline-reverse-apply. BB-as-base mechanism
  BUILT (`apply_markup`: a `base_text` transcription entry sets the prior directly,
  with an `ocr_quality` guard that refuses letter-spacing-degraded BB OCR >0.15).
  - **But for art VIII §6 specifically, BB-as-base FAILS too (found 2026-06-14):**
    the 1981 BB's subsection-2 of §6 is OCR-degraded at **ocr_quality 0.606** (60%
    single-char letter-spacing: `com;int o f seve n members`, + char corruption
    `nn d`, `sh.t l 1`). The 1994 strikethrough (the other source) is equally
    garbled in the text layer + dense archaic 1939–1946 transitional language.
    **So both PDF/OCR sources are below the authoritative bar for §6's 1981 base.**
  - **DECISION: dense, heavily-amended sections (art VIII §6 class) require
    NATIVE-SOURCE acquisition** — the 1979–80 session-law enacted text (ties to
    PL-SOURCE-FILES). They are NOT bulk-reconstructed from PDFs; the OCR guard
    routes them to a native-source queue. Redline-reverse-apply (small/medium) and
    BB-as-base (heavy-but-clean-BB) remain for everything else.
- **Large-section gate:** the exact-substring 1981-BB gate doesn't survive OCR
  noise over a 1600-token section → `bb_gate` now falls back to a 0.97 fuzzy ratio
  (`NEAR`). For very large sections, prefer gating only the *changed* subsection.
- art VI §13 / X §24 also NOT cleanly BB-substring-gateable (judicial/finance
  divergence) → census external cross-check first; candidates for BB-as-base too.

## 7. Scope boundaries (what #0 does and does NOT do)

- **IN:** post-1981 amend-reenact-section + create-article splices for the ~96 amended
  modern provisions; gate; idempotent apply; gate-fail triage.
- **OUT → #1 (crosswalk):** the `[1981, d1)` head interval for carried provisions
  (needs the historical-layer link or 1981 base text).
- **OUT → #2 (structural four):** described-edit / subsection-level amendments of
  art. LIV & §25 (bespoke; art. LIV must first be subdivided or snapshot-modeled).
- **OUT:** amendment **I (1)** absence and the external-enumeration cross-check (census
  follow-up).

## 8. Phased rollout

1. **Single-class first:** amend-reenact-section only (the simple-accretion majority,
   like art. X §21). Run, gate, splice; measure gate pass-rate.
2. **create-article** (CX art. VII, CXXXV art. V) — adds article-split + prior-article
   supersession; verify against the section inventory.
3. **cross-article measures** (CXII) — measure-split routing.
4. Triage the gate-fails; iterate the locator.
5. Hand the structural four to #2; hand head-gaps to #1.

## Open decisions (for review before building)

1. **Head interval for carried provisions:** leave as flagged `pending_base` gap (clean,
   honest, defers to #1) — or backfill `[1981, d1)` now from the 1981 Blue Book OCR
   (closes the gap sooner but introduces OCR text ahead of #1)? *Recommend: flag, defer.*
2. **`pending_base` modeling:** a `provisions.status`/notes flag, or a sentinel version
   with `source_authority='pending-1981-base'`? *Recommend: sentinel version so the
   timeline is contiguous and the integrity check stays green, clearly marked.*
3. **Where the structural-four subdivision lands** — this design assumes art. LIV is
   handled in #2 upstream (ingest_constitution_history) before merge; confirm.
