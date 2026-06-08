# Primary-Law Data Corrections Log

Changes applied to the primary-law databases (`constitution.db`, `constitution_history.db`, `statutes.db`, `rules.db`, `admincode.db`) after import. All corrections are also recorded in each corpus DB's `changelog` table.

## Batch `ndac-extraction-fix-2026-06-08` — fix the same two extraction bugs in the admin code (646 sections)

`admincode.db` · 646 sections · fields `heading` + `text_content`

The N.D. Administrative Code was extracted by the **same** `scrape_nd_code.py` converter as the N.D.C.C. statutes (`ingest_admin.py` reads its `### §` markdown), so it carried **both** bugs fixed there: dropped cross-reference lines and phantom-duplicate headers. A scan found **117** phantom-duplicate section numbers in the NDAC markdown (13,980 headers vs 13,838 provisions) and **287** sections with dropped-cross-reference seams; `admincode.db` had **0 duplicate citations** because the ingest's first-wins dedup silently kept whichever occurrence parsed first — so corrupted sections held garbage (e.g. § 10-16-03-12's DB heading was the body sentence "If the prize allocated to each claimant is less than six hundred dollars, at" with text starting mid-sentence).

Both bugs are already fixed in the converter (code-mirror `ce5af93`); the fix transfers to NDAC unchanged (4-part section numbers, article/chapter file layout) — confirmed on sample chapters including the 1,169-section hazardous-waste chapter 33.1-24-05, which has **0 phantom dups** after the fix.

**Application:** re-extracted all 2,131 NDAC chapter/article PDFs with the fixed converter (`~/code/code-mirror/rebuild_ndac_md.py`, parallel; `/tmp/ndac_fixed`, 0 phantom dups), parsed identically to the ingest (`ingest_admin.section_files` + `parse_sections`, first-wins), and for every admin section whose DB heading or text differed, replaced both with the clean re-extraction's (`triage/apply_ndac_fix_2026-06-08.py`). **651 sections differed; 646 applied** (59 heading corrections — garbled sentence-fragment headings → proper catchlines, e.g. § 10-16-03-12 → "Delay of paying a prize"; 609 grew where the DB was truncated/fragmented, 37 shrank where the DB had absorbed garbage). Verified in both directions on a sample (e.g. § 75-02-06-26 DB 19,002 garbled chars → 1,221 "Reconsiderations"; § 31-13-05-style shrinks all DB-garbled).

**5 sections HELD** for manual review (`33.1-24-02-42`, `33.1-24-05-235`, `33.1-24-05-280`, `33.1-24-06-14`, `33.1-24-08-64`) — all inside the enormous embedded "Treatment Standards" tables in the hazardous-waste chapters, where **both** the old and new extraction misjudge the section boundary and the re-extraction's heading came out as a body sentence; auto-overwrite was suppressed (a guard holds any section whose re-extracted heading is sentence-like). **1 spurious section** (`33.1-24-06-235`, heading "33") is a phantom-only entry the clean re-extraction does not produce — left in place, flagged for deletion. Both groups tracked in TODO-primarylaw.md PL-3.

`authority` recorded per section; heading+text logged; FTS re-indexed; changelog-revertible. DB backup `admincode.db.bak-pre-ndacfix-2026-06-08`. Integrity `quick_check ok`, FTS `integrity-check ok`, 0 duplicate citations. After this batch `admincode.db` equals the clean re-extraction for every non-held section.

## Batch `ndcc-fix-29-15-21-subsec3-2026-06-08` — restore dropped clause in N.D.C.C. § 29-15-21(3)

`statutes.db` · provision/version 11275 · field `text_content`

Subsection 3 had an **extraction gap**: a full clause dropped between "pursuant to section" and "considered a proceeding separate," leaving a dangling, ungrammatical sentence with no statutory cross-reference.

- **Was:** "…or child support pursuant to section⏎considered a proceeding separate…"
- **Now:** "…or child support pursuant to section **14-05-24 or an order for child custody pursuant to section 14-05-22 must be** considered a proceeding separate…"

The 17 missing words include both governing cross-references (the alimony/property/child-support modification statute § 14-05-24 and the child-custody statute § 14-05-22) and the operative verb phrase "must be." Without them the subsection failed to identify which modification proceedings are treated as separate from the original action for change-of-judge purposes.

Verified verbatim against the official current text, [N.D.C.C. ch. 29-15 PDF, ndlegis.gov](https://ndlegis.gov/cencode/t29c15.pdf#nameddest=29-15-21) (in force eff. 2025-07-01). `authority` recorded in the changelog table. Confidence: high (two independent reads of the official PDF agree).

## Batch `ndcc-dropline-fix-2026-06-08` — restore dropped cross-reference lines corpus-wide (627 sections)

`statutes.db` · 627 sections · field `text_content`

Corpus-wide remediation of the systemic bug whose surfacing instance was § 29-15-21(3) above. **Root cause** (found in `~/code/code-mirror/scrape_nd_code.py`, the PDF→markdown converter `ingest_statutes.py` reads from): the `_text_to_markdown` table-of-contents filter skipped any line matching `NN-NN-NN ` + non-period text — intended for the section-analysis TOC at the top of each chapter PDF, but it also ate **wrapped body lines that begin with a section cross-reference** (e.g. a line wrapping to start `14-05-24 or an order for child custody…`). pdfplumber extracted the text correctly; the converter dropped it. **Fix:** gate the TOC filter to the pre-first-section region only (a `seen_section` flag); once section bodies begin, a line starting with a section number is body text and is kept.

**Isolation method (so only this bug's effect is applied):** re-extracted all 2,526 chapter PDFs twice — with the old converter and the fixed one — and diffed per section (`triage/apply_dropline_fix_2026-06-08.py`). Applied a section only when ALL held: (1) exactly **one** `### §` header for it corpus-wide (not entangled with the separate phantom-duplicate-header bug — see TODO-primarylaw.md PL-2); (2) the change is **strictly additive** (new = old with whole lines inserted only — never a deletion or modification, so only dropped lines are restored); (3) the DB currently holds the pre-fix text. 644 sections differed; **627 met all three and were applied**, 16 were held as PL-2-entangled, 1 (29-15-21) was already fixed. Each restored line is a section cross-reference (e.g. § 10-04-04 "…exempt under section **10-04-05**", § 12.1-32-09.1 "…as provided under section **12-48.1-02**").

The re-extraction derives from the official ndlegis.gov cencode chapter PDFs; `authority` so recorded; FTS re-indexed per section (external-content delete+reinsert); changelog-revertible. DB backup `statutes.db.bak-pre-dropline-2026-06-08`. Integrity: `quick_check ok`, FTS `integrity-check` ok. The seam-detector (`triage/detect_dropped_xrefs_2026-06-08.py`) fell 600 → 202 hits; the residual is **not** TOC drops — 10 are PL-2 phantom-dup holds and ~178 are detector false positives / genuine source danglers that appear identically in a fresh re-extraction (verified new == DB for them).

## Batch `ndcc-phantom-header-fix-2026-06-08` — fix sections fragmented by phantom-duplicate headers (258 sections)

`statutes.db` · 258 sections · fields `heading` + `text_content`

Corpus-wide remediation of the **second** extraction bug (PL-2), discovered while isolating the dropped-line fix. **Root cause** (same trigger as the dropped-line bug, opposite symptom): `scrape_nd_code.py`'s section detector `^([\d.]+(?:-[\d.]+){2,})\.\s+(.+)` matched any line beginning `NN-NN-NN. Word`. A **body cross-reference that ends a sentence and wraps to a line start** — e.g. `…in section 10-19.1-30. Unless reserved by the articles…` wrapping so a line begins `10-19.1-30. Unless reserved…` — was mis-parsed as a new section header, **fragmenting the section and creating a phantom duplicate** of that section number. At the 2026-06-07 ingest the `INSERT OR IGNORE` kept whichever occurrence parsed first, so some sections silently held a garbage fragment (e.g. § 65-01-02 "Definitions" held a 208-char fragment of another section; § 14-15-16 held `"14-15-16."`, 9 chars). **168 sections** had phantom duplicates corpus-wide.

**Fix** (`~/code/code-mirror/scrape_nd_code.py`, `_real_header_indices`): a chapter's real section headers run in strictly increasing section-number order, so accept as headers only the **longest strictly-increasing subsequence** of candidates (LIS — robust to both backward and forward phantom cross-references, where a streaming monotonic check would be poisoned by a forward reference), after first dropping candidates whose number does **not belong to the chapter** (numeric sort-key prefix, zero-padding-insensitive so a legitimately zero-padded header like `01-03-19` in chapter `1-03` is kept). Phantoms are demoted to body text and merged back into the section they interrupted. Result: **0 phantom-duplicate headers corpus-wide** (was 168); header count 29,291 → 29,107 (exactly one per real section).

**Application:** re-extracted all chapters with both fixes (`/tmp/ndcc_v2`, 0 phantom dups), then for every ndcc section whose DB heading or text differed from the clean re-extraction, replaced both with the re-extraction's (`triage/apply_phantom_fix_2026-06-08.py`). **258 sections updated** (72 heading corrections — garbled sentence-fragment headings → proper catchlines, e.g. § 10-19.1-84 "The term includes a record of all issuances…" → "Books and records - Inspection"). The divergent sections were spot-verified in both directions (DB-longer *and* DB-shorter) to confirm the re-extraction is the coherent/correct text and the DB held the garbled/bloated version — e.g. § 31-13-05's DB text started mid-sentence and ran into unrelated sex-offender-registration text (12,398 chars) vs the correct 896-char "DNA database established" section. **After this batch DB == the clean re-extraction for all 29,107 ndcc sections** (0 diffs). `authority` so recorded; heading+text logged per section; FTS re-indexed; changelog-revertible. DB backup `statutes.db.bak-pre-phantom-2026-06-08`. Integrity `quick_check ok`, FTS `integrity-check ok`, 0 duplicate citations, seam-detector 202 → 41 (residual all source/FP).

**Note:** this batch also resolved the 16 PL-1 dropped-line sections that had been held as phantom-entangled. **Caveat for reproducibility:** the served DB is now correct, but the `~/refs/statute/NDCC` markdown source still reflects the old buggy converter — regenerate it (`~/code/code-mirror/rebuild_ndcc_md.py`) before any re-ingest, or the corruption returns. The `scrape_nd_code.py` fix is in the working tree, not yet committed.


## Batch `const-history-merge-2026-06-08` — fold historical layer into served constitution.db

`constitution.db` · +265 provisions / +421 versions (via `scripts/merge_const_history.py --apply`)

Merged the point-in-time historical layer (`constitution_history.db`, original 1889 numbering §§1–217 + Schedule, eff. 1889–1980) into the served `constitution.db` (modern art/§ numbering). The two are citation-disjoint (0 cite_key collisions), so the historical provisions are additive. Served DB went 201→466 provisions, 201→622 versions.

Effect: `lookup_authority` now answers point-in-time historical queries by original citation, e.g. `lookup_authority("N.D. Const. § 82", as_of_date="1945-01-01")` → the 1940 Art. 57 (LVII) text; modern queries unchanged; `search_authority` FTS indexes the historical text. Integrity: quick_check ok, FTS integrity-check ok.

This is Approach B (additive). NOT yet connected across the 1981 reorganization — see TODO-primarylaw.md PL-CONST-CROSSWALK (renumbering crosswalk), PL-CONST-AMEND-RECONCILE, PL-CONST-STRUCTURAL, and the BUILD-ORDER note (ingest_constitution → ingest_constitution_history → merge_const_history → make_release).