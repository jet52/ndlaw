# Primary-Law Data Corrections Log

Changes applied to the primary-law databases (`constitution.db`, `constitution_history.db`, `statutes.db`, `rules.db`, `admincode.db`) after import. All corrections are also recorded in each corpus DB's `changelog` table.

## Batch `modern-text-corrections-2026-06-15` — fix art. VII §10 (ndconst.org served a 404 page)

The DB's current text for **art. VII § 10** (intergovernmental agreements) was a DokuWiki "topic does not exist" **404 HTML page** (`<!DOCTYPE html>…`, ~14 KB) — ndconst.org served a broken page and the scrape stored it. art. VII §10 was created 1983 (S.L. 1983 ch. 718, home-rule article) and is unchanged since; the verbatim text was taken from the 1983 creation measure's clean text layer and corroborated against the newly-acquired 1989 Blue Book. Corrected (482 chars) in live `constitution.db` + scratch via `scripts/apply_modern_text_corrections.py`; reproducible through `data/const_modern_text_corrections.json` + `ingest_constitution.apply_text_corrections`. Surfaced by the modern snapshot-diff (art. VII §10 was a hard mismatch vs the 1989 BB). New Blue Book scans archived for future witnesses: `~/refs/nd/const/raw/{1981,1989,1973}_blue-book_ndbb-*.pdf` (+ extracted constitution `processed/{1981_blue-book-ndbb,1989_blue-book}_constitution.md`).

## Batch `fix-amend164-effdate-2026-06-14` — art. XV effective date (measure states it)

Investigation of approval-vs-effective dating (full writeup: `triage/const-amendment-effective-dates-2026-06-14.md`). The default for an approved measure is **"the thirtieth day after the election, unless otherwise specified in the measure"** (N.D. Const. art. III § 8; rule established 1918 — before 1918 it was the date of the official canvass, per the § 25 history). A measure stating its own effective date controls. Confirmed the DB's effective dates all match the (user-reviewed) ndconst.org column and follow this rule; audited all 59 modern amendments.

**One error:** amendment **164** (art. XV term limits) was stamped at the **election date 2022-11-08**, but the measure's **Section 5** states it is "effective on the first day of January immediately following approval" → **2023-01-01**. Corrected amendment 164's `effective_date` and art. XV §§ 1-6 `effective_start` to 2023-01-01 (live + scratch, integrity 0/0). Reproducible via `AMENDMENT_EFFECTIVE_DATE_CORRECTIONS` in `ingest_constitution.py`. (163 ethics = 60-days-after-approval per art. XIV § 4, and 165 age limits = immediate, were verified correct.)

## Batch `fix-amend164-source-2026-06-14` — correct art. XV (term limits) source_url (initiated measure → IMA, not CAA)

art. XV §§ 1-6 (2022 term limits for the Legislative Assembly and Governor) is an **initiated** constitutional measure. ndconst.org pointed amendment **164**'s `source_url` at `…/68-2023/session-laws/documents/caa.pdf` — wrong file (CAA = legislative *referrals*) and a 404. The measure is **S.L. 2023 ch. 594, "INITIATED MEASURES APPROVED"** — public file `…/68-2023/session-laws/documents/ima.pdf` (IMA = Initiated Measures Approved; also in the on-disk `~/refs/nd/sess/sl2023.pdf` p. 2279). Verified the measure: "A new article … is created and enacted as follows: Section 1. Term limits for legislators…" — a **CREATE**, so art. XV §§ 1-6 are correct single-version provisions (no point-in-time reconstruction needed).

- **Reproducible:** `AMENDMENT_SOURCE_URL_CORRECTIONS` in `ingest_constitution.py` overrides amendment 164's source_url to the IMA file. Applied to live + scratch; `affected` (art. XV §§ 1-6) was already correct.
- **OPEN — effective-date discrepancy (not yet changed):** the DB stamps art. XV at **2022-11-08** (election/approval date), but the measure's Section 5 makes it effective **2023-01-01** ("the first day of January immediately following approval"). ndconst.org's modern chronology appears to use approval/election dates as effective dates; this may be systemic across the modern layer and affects point-in-time boundary accuracy. Flagged for a decision before live promotion.

## Batch `modern-ix-stale-text-2026-06-14` — correct stale CURRENT text for art. IX §§ 12-13 (ndconst.org didn't apply amend. 166)

**Served-law correctness fix.** ndconst.org's current snapshot for **art. IX § 12 and § 13** still carries **pre-2024 terminology** ("deaf and dumb", "an institution for the feebleminded", "insane", "mentally ill"), even though the const DB records **amendment 166** (2023 SCR 4001, "Updated Terminology", approved 2024-11-05, effective 2024-12-05) as applied. So the stored "current" text was actually the *pre-2024* version — `lookup_authority` returned outdated text. The enacted modern terminology ("hard of hearing", "a facility for individuals with developmental disabilities", "care of individuals with mental illness") was verified against the enacting measure (bill 23-3015) at 450 dpi.

- **Reproducible:** the corrected current text lives in `data/const_modern_text_corrections.json`; `ingest_constitution.apply_text_corrections` overrides the modern mirror's current-version text after build (FTS reindexed via the external-content `'delete'` command). A clean rebuild now reproduces the correction (validated on a simulated fresh scrape). Remove the entries once ndconst.org's snapshot reflects amendment 166.
- **Applied to built DBs** via `triage/const-modern-batch/reconstruct_ix_stale.py`: live `constitution.db` current text corrected (flat layer); the modern-reconstruction scratch additionally got the full point-in-time chains — **§12** 2 versions ([1981→2024-12-04] old terminology / [2024-12-05→] current), **§13** 3 versions ([1981→1982-12-01] / [1982-12-02→2024-12-04] / [2024-12-05→] current, the 1982 change = amend 114 "removes obsolete references"). Each prior reconstructed by an agent reading the session-law redlines; gated mechanically (apply==before), by chain continuity, and against the stored stale text. Integrity 0/0 on both.
- *Detection:* the campaign's "latest amendment's text == DB current" gate is the staleness detector; among reconstructed provisions only §12/§13 failed it. A systematic check would run that gate across all amended provisions.

## Batch `fix-amend167-legacyfund-2024-06-14` — correct the 2024 Legacy Fund amendment mis-mapping (amend. 167)

ndconst.org's `:amendments` table lists amendment **167** (Legacy Fund, 2023 HCR 3033, ballot measure approved 2024-11-05, effective 2024-12-05) as affecting **`art. XVI, §§ 1-5`** — that cell was copied from amendment 165 (the June-2024 initiated measure that *created* art. XVI, "Congressional Age Limits"). The enacted measure (bill 23-3092) **amends section 26 of article X** (legacy-fund spending/transfers). Verified against the bill text and against amendment 166 (SCR 4001, "Updated Terminology") which correctly targets art. IX §§ 12-13.

Effect of the upstream error: amendment 167 was spliced onto art. XVI §§ 1-5 (5 spurious rows; those provisions' `effective_start` stamped 2024-12-05 instead of the 2024-06-11 create date), and **art. X § 26 lost its 2024 amendment event** (left stamped at its 2011 creation).

- **Reproducible fix:** `AMENDMENT_AFFECTED_CORRECTIONS` in `ndcourts_mcp/ingest_constitution.py` overrides amendment 167's `affected` to `art. X, § 26` before linking, so a clean rebuild reproduces the correction (we cannot edit ndconst.org).
- **Applied to built DBs** (`constitution.db` live + the modern-reconstruction scratch) via `scripts/fix_amend167_legacyfund_2024.py` (idempotent): deleted the 5 wrong amendment-167 rows, inserted one correct row on art. X § 26, reset art. XVI §§ 1-5 `effective_start` → 2024-06-11, set art. X § 26 → 2024-12-05. Integrity 0/0/0 on both. art. X § 26 is now correctly a two-amendment provision (2011 create + 2024 amend) queued for point-in-time reconstruction; art. XVI §§ 1-5 are correct single-version creates. Live server picks this up on the next release rebuild.

## Batch `const-struct-2026-06-14` — close the 4 structural constitutional amendments + Amendment I; build & validate the historical point-in-time layer

Closed the long-standing PL-CONST-STRUCTURAL gap: four amendments that the whole-provision ingest could not apply because they touch **sub-provisions** are now applied as whole-provision version splices (the ratified "splice, don't subdivide" decision), reconstructed from session-law text and propagated into the canonical `data/constitution_amendments.json`.

- **art. LIV trio** — `amend. art. LIV` (Board of Higher Education) went from 1 version (1938–1980) to **4 versions**: base[1938-07-28→1964] → **LXXVIII** (1964-07-30, subdiv (d) of subsec 6 — agricultural-experiment-station budget separation) → **XC's 2nd change** (1972-10-05, subsec 1 — Ellendale constitutional status removed, items renumbered; text acquired from `~/refs/nd/sess/1973_sl/CAA.pdf`, which was **not** in the 2026-06-08 extraction doc) → **XCVI** (1976-12-02, subsec 2 "alumnus or former student"→"graduate" & subsec 4 compensation rewrite). Each amendment provides the full reconstructed art. LIV text; the ingest chains them chronologically. Independent check: art. LIV v1976 vs modern `art. VIII §6` = 0.89 similarity (residual = post-1981 student-member amendments — confirms the LIV→§6 lineage).
- **LXXXI** (1964-12-03) — partial repeal of the 10th paragraph of **§25** (publicity-pamphlet clause). Re-modeled from `type:repeal` (which would have tombstoned all of §25) to an `amend` with §25's full ¶10-removed text. §25 now **5 versions** ([1918→1964) with ¶10 / [1964→1978) without). **Snapshot-validated: §25 vs the 1973 Blue Book improved 0.88 → 0.984.**
- **Amendment I** — identified as the **Prohibition Article (Art. 20 / §217)**, separately submitted on the 1889 ballot (Schedule §20), adopted on statehood, repealed 1932 by Amend. XLVII. §217's text/timeline were already correct; only the adoption *event* was missing → recorded as an `amendments` row. Encoded in `constitution_amendments.json` as a new `type:"event"` record (no version change — writes only the amendments-table row), and `ingest_constitution_history` grew an event-only branch to apply it, so a clean rebuild now reproduces it (verified field-for-field against the prior hand insert; 265 prov / 425 vers / 161 amends, integrity 0/0).

**Build & cutover:** propagated into `constitution_amendments.json` (JSON backup `…json.bak-pre-struct-2026-06-14`), rebuilt `constitution_history.db` (0 pending / 0 unresolved; amends 110→113), and rebuilt the full served `constitution.db` (`ingest_constitution` → `merge_const_history`) to a test path, validated, then swapped live (backups `constitution.db.bak-pre-struct-2026-06-14`, `constitution_history.db.bak-pre-struct-2026-06-14`). Live now **466 provisions / 626 versions** (+4 vs prior, = the structural splices); modern layer unchanged (201, no regression).

**Validation — the new point-in-time snapshot-diff harness** (`triage/const-pilot-2026-06-14/snapshot_diff.py`, the never-built #5 acceptance test): reconstructs the constitution as of T and diffs each §-numbered section against the printed compilation. Against the served DB: **1925 = 99.5%**, **1973 = 98%** match-or-near; residual is print-style numeral variants, repeal-notice wording (both agree repealed), and compilation OCR — **no real DB point-in-time errors**. Integrity 0/0. The 1889–1980 historical layer is now independently validated against the official printed record.

## Batch `ndac-extraction-fix-2026-06-08` — fix the same two extraction bugs in the admin code (646 sections)

`admincode.db` · 646 sections · fields `heading` + `text_content`

The N.D. Administrative Code was extracted by the **same** `scrape_nd_code.py` converter as the N.D.C.C. statutes (`ingest_admin.py` reads its `### §` markdown), so it carried **both** bugs fixed there: dropped cross-reference lines and phantom-duplicate headers. A scan found **117** phantom-duplicate section numbers in the NDAC markdown (13,980 headers vs 13,838 provisions) and **287** sections with dropped-cross-reference seams; `admincode.db` had **0 duplicate citations** because the ingest's first-wins dedup silently kept whichever occurrence parsed first — so corrupted sections held garbage (e.g. § 10-16-03-12's DB heading was the body sentence "If the prize allocated to each claimant is less than six hundred dollars, at" with text starting mid-sentence).

Both bugs are already fixed in the converter (code-mirror `ce5af93`); the fix transfers to NDAC unchanged (4-part section numbers, article/chapter file layout) — confirmed on sample chapters including the 1,169-section hazardous-waste chapter 33.1-24-05, which has **0 phantom dups** after the fix.

**Application:** re-extracted all 2,131 NDAC chapter/article PDFs with the fixed converter (`~/code/code-mirror/rebuild_ndac_md.py`, parallel; `/tmp/ndac_fixed`, 0 phantom dups), parsed identically to the ingest (`ingest_admin.section_files` + `parse_sections`, first-wins), and for every admin section whose DB heading or text differed, replaced both with the clean re-extraction's (`triage/apply_ndac_fix_2026-06-08.py`). **651 sections differed; 646 applied** (59 heading corrections — garbled sentence-fragment headings → proper catchlines, e.g. § 10-16-03-12 → "Delay of paying a prize"; 609 grew where the DB was truncated/fragmented, 37 shrank where the DB had absorbed garbage). Verified in both directions on a sample (e.g. § 75-02-06-26 DB 19,002 garbled chars → 1,221 "Reconsiderations"; § 31-13-05-style shrinks all DB-garbled).

**5 sections HELD** for manual review (`33.1-24-02-42`, `33.1-24-05-235`, `33.1-24-05-280`, `33.1-24-06-14`, `33.1-24-08-64`) — all inside the enormous embedded "Treatment Standards" / instrument-wording tables in the hazardous-waste chapters, where **both** the old and new extraction misjudge the section boundary and the re-extraction's heading came out as a body sentence; auto-overwrite was suppressed (a guard holds any section whose re-extracted heading is sentence-like). **1 spurious section** (`33.1-24-06-235`, heading "33") is a phantom-only entry the clean re-extraction does not produce. **Both groups are now resolved (2026-06-08):**

- Batch `ndac-delete-spurious-2026-06-08` — deleted § 33.1-24-06-235 (provision+version+FTS, changelog-logged). Admin provisions 13,838 → **13,837** (matches the re-extraction).
- Batch `ndac-held-tablesections-2026-06-08` — reconstructed all 5 held sections directly from the official chapter PDFs by bounding each from its real (non-sentence) section header to the next section header, then applying the converter's page-header/footer line filters. Each now has its true catchline and full body, ending at the official "History / Law Implemented" footer (a boundary check). E.g. § 33.1-24-02-42 5,062c garbled → **121,316c** "Wording of the instruments"; § 33.1-24-06-14 961c → **25,165c** "Permit modification at the request of the permittee"; § 33.1-24-05-280 → 153,329c "Applicability of treatment standards" (it legitimately contains a 3,592-line embedded treatment-standards table). `authority` = manual reconstruction from the ndlegis.gov PDF. **Caveat:** the fixed converter still mis-splits these 5 table sections, so the `~/refs/reg/NDAC` markdown is wrong for them — the DB reconstruction is authoritative; a future converter table-handling fix (TODO PL-3) would reconcile the markdown.

After all three batches: **0 sentence-like headings remain in the 33.1-24-* chapters** (one apparent residual, § 33.1-24-03-70 "Where and when to make the hazardous waste determination…", is a legitimate long wrapped catchline — the cosmetic PL-VALIDATE #6 heading-split, not corruption). Integrity `quick_check ok`, FTS `integrity-check ok`, 0 duplicate citations.

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

## Batch `modern-xii-corp-repeal-2006-2026-06-15` — recover pre-repeal text for 7 art. XII corporations sections (SCRATCH)

`constitution.db` (scratch `/tmp/const-scratch.db`) · 7 provisions · +7 prior-text versions, 7 repeal-tail effective-date corrections

ndconst.org served art. XII §§ 3, 7, 8, 12, 14, 15, 17 (Corporations Other than Municipal) as a bare "Repealed." stamped with the ingest-default effective date **1889-10-01** — i.e. the DB served "Repealed." across the *entire* 1889→present timeline, losing the pre-repeal text and mis-dating the repeal. Both the **1981 Blue Book** and the **1989 Centennial Blue Book** print full text for all seven; they were repealed only in **2006**.

**Repeal date** = 2006-07-01. Authority: the ND Legislative Council's official codified history note for art. XII ("The repeal of this section, effective July 1, 2006, was approved at the primary election in 2006"). Same cleanup measure (S.L. 2005, ch. 623) amended surviving §§ 1, 2, 6 (approved June 13, 2006 primary). Residual: whether the measure stated July 1 vs. the 30-day default — a 12-day mid-2006 window, immaterial to point-in-time correctness; confirm against the measure before live promotion.

**Pre-repeal text** triangulated across three independent witnesses: PRIMARY 1981 Blue Book (high-res ndbb scan, modern art. XII numbering, clean); WITNESS 1989 Blue Book (same words; OCR spacing garble; dropped "be" in §15, corrected); CROSS the 1925 official constitution orig. Art. VII (= same content, renumbered by the reorg) — word-level ratio 1.000 for five sections. Two modern-era variants where **both** Blue Books govern over the 1925 reading: §12 "franchises" (1925 sing.) + "...this section, by..." comma; §14 "...cross any other, and..." (1925 semicolon).

**Model:** each section's existing "Repealed." version moved 1889-10-01 → 2006-07-01; new prior full-text version inserted [1981-01-01 → 2006-06-30] (modern-layer head convention). Integrity 0 gaps. FTS untouched (current text unchanged). Per-version changelog rows written; idempotent (batch-scoped).

**Validation:** modern snapshot-diff flipped all 7 from MISMATCH to MATCH at both witnesses — **1981 MISMATCH 7→0**; **1989 MISMATCH 10→3** (residual 3 = pre-existing art IV §16 / VI §12 / X §5 formatting NEAR-misses, unrelated), match-or-near **91.2% → 95.6%**. Point-in-time spot-checked across the boundary (full text through 2006-06-30; "Repealed." from 2006-07-01). **Scratch only** — not promoted to live (campaign doctrine: promote via upstream rebuild once witnessed + green).


## Batch `modern-artiv-renumber-1986-2026-06-15` — correct art. IV §§ 9-11 false citation origin (SCRATCH)

`constitution.db` (scratch `/tmp/const-scratch.db`) · 3 provisions · 3 effective-start corrections (no text change)

Article IV (Legislative Branch) was repealed-and-recreated effective **1986-12-01** (approved at the June 12 & Nov 6, 1984 elections; S.L. 1983 ch. 728/730, 1985 ch. 706/707). Per the ND Legislative Council codified note at the beginning of art. IV: "Sections 14, 15 and 19 of Article IV, which were not repealed, have been renumbered as sections 9 to 11, inclusive." So former § 14 (bribery) → § 9, former § 15 (disqualification) → § 10, former § 19 (writs/vacancy) → § 11; the §9/§10/§11 *citations* began 1986-12-01 (former §§ 9-13 were repealed).

**The bug:** ingest stamped § 9 and § 10 at the default 1889-10-01 (claiming statehood origin) and the earlier §11 markup reconstruction used the modern floor 1981-01-01 — all three falsely placed the citation before its 1986-12-01 renumber origin. **Fix:** moved each section's earliest version effective_start → 1986-12-01. No text change (the renumber preserved text; current text matches the 1981 BB former §§ 14/15/19). §11 retains its 2000 amendment split ([1986-12-01→2000-07-12] writs; [2000-07-13→] "provide by law a procedure").

**Witness:** dual-source — codifier note + 1981 Blue Book, where former § 14 = bribery/solicitation, § 15 = "expelled for corruption … convicted of bribery, perjury or other infamous crime", § 19 = "governor shall issue writs of election" (despaced-substring match against the microfilm OCR).

**Validation:** point-in-time now truthful — §§ 9-11 return nothing before 1986-12-01 (citation did not exist), full text from 1986-12-01, §11's 2000 amendment fires correctly. Snapshot-diff 1981 NOT_IN_COMP 59→56 (the 3 correctly drop from "DB provisions in force at T", matching the 1981 BB which has no §9-11); 1989 unchanged at 95.6% (no regression). Integrity 0 gaps.

**Scope note:** this removes the false pre-1986 claims; it does NOT add a [1981,1986) layer for the old art IV numbering. "art IV § 9 as of 1983" correctly returns nothing (the text was former § 14). Full pre-1986 art IV coverage under old numbers = the separate PL-CONST-CROSSWALK task. **Scratch only.**


## Batch `modern-ix7-secondread-2026-06-15` — second-read pass over the modern reconstructions (SCRATCH)

`constitution.db` (scratch `/tmp/const-scratch.db`) · 1 text correction (art. IX § 7 head) + validation of 9 others

Ran the pre-promotion second-read pass: every reconstructed modern version owed an independent witness (a BB distinct from the redline PDF + 1981 BB the agents originally used, or — for created/short-lived versions — the originating measure). Checker: `triage/const-modern-batch/second_read_check.py` (reuses the snapshot-diff BB parser).

**10 owed items → all now validated:**
- **BB-witnessed (8):** art I §16 (both chain versions ✓ vs 1981 & 1989 BB), II §1 (1989 ✓), IX §1 (both ✓), IX §2 (head contained in 1925 official; later ver contained @1989), **IX §10 (1981 BB 0.992 — resolves the prior "3rd-read flag")**, IX §12 (both ✓), IX §13 (head 0.981 vs 1981 BB + later @1989), XII §1 (both ✓1.0).
- **Measure-witnessed (1):** art X §26 [2011,2024) head — created provision, no BB witness; re-extracted the 2011 CAA.PDF (ch. 518) via mutool, head matches at overlap 1.0; the measure's own EFFECTIVE DATE clause ("effective for oil and gas produced after June 30, 2011") independently confirms the 2011-07-01 start.

**Real error caught and fixed — art IX § 7 [1981-01-01,1982-12-01) head** (`fix_ix7_head_secondread.py`): the wave-2 reversal of the 1982 amendment kept an ADDED span (the "#1 read error"). 1982 changed "All lands MENTIONED IN THE PRECEDING SECTION shall be appraised" → "All lands RECEIVED BY THE STATE FOR ANY SPECIFIC EDUCATIONAL OR CHARITABLE INSTITUTION shall be appraised"; the agent restored the struck phrase but failed to drop "for any specific educational or charitable institution", and wrote a comma for the original semicolon. Flagged because the head scored 0.859 vs the 1981 BB (every other head ≥0.971). Corrected to the pre-1982 text — **quadruple witness**: 1981 BB + 1925 official (orig § 160) + 1954 BB + 1973 BB, all identical. Text-only change to a non-current version; FTS untouched.

**After this pass:** all modern reconstructions (44 provisions) carry an independent second witness or measure confirmation → §3.4 of the campaign HANDOFF is cleared. Snapshot-diff unchanged (1981 MISMATCH 0; 1989 95.6%); integrity 0 gaps; quick_check ok. **Scratch only.**


## Batch `modern-artiv-crosswalk-1981-1986-2026-06-15` — art IV [1981,1986) crosswalk, shared §§1-16 (SCRATCH)

`constitution.db` (scratch `/tmp/const-scratch.db`) · 13 provisions · +13 prior versions

Art IV was repealed-and-recreated 1986-12-01, REUSING the §1-16 citation numbers for new content. So for [1981-01-01, 1986-11-30] "art IV § N" denoted the OLD §N. Prepended that prior version to each of the 13 clean shared sections, sourcing the OLD text from the validated historical layer (1889 numbering) via the derived crosswalk (`ARTIV-CROSSWALK-PLAN.md`): §1→1889§52, §3→§27, §4→§28, §6→§30, §7→§31, §8→§32, §9→§33, §10→§34, §12→§36, §13→§37, §14→§40, §15→§38, §16→§41. Each match confirmed against the 1981 Blue Book (right-numbering witness, ratio ≥0.92); each old text verified ≠ the new (recreated) text. The historical §M version in force at 1980 == the [1981,1986) content (no art IV amendments 1981-86 besides the §46 repeal). This recovered the crosswalk WITHOUT the NDCC Replacement Vol 13 disposition table.

**Renumber crux verified end-to-end:** art IV §14 = bribery in 1983 (old §14) → sessions-open in 1990 (new §14); art IV §9 = representatives'-term in 1983 (old §9) → bribery in 1990 (renumbered survivor, former §14). The bribery text correctly migrates §14→§9 across the 1986-12-01 boundary.

**DEFERRED:** §§2, 5, 11 — "[Unconstitutional.]" stubs in the 1981 BB (judicially void, not textually repealed — representation is a separate judgment call). §§17-46 — repealed-only, no modern citation (optional pass).

**Validation:** integrity 0 gaps, quick_check ok, 691 versions. Snapshot-diff 1989 unchanged at 95.6% (prior versions not in force at 1989 → no regression); 1981 picked up the art IV [1981,1986) content (MATCH 48→49) but the harness flags 2 false MISMATCHes (art IV §1/§4) — these are `parse_comp` mis-attributing the garbled 1981-BB microfilm OCR across an undetected article header, NOT data errors (§1 DB text = "The Senate and House of Representatives jointly shall be designated…", which the codifier note quotes verbatim as "Former Article IV, § 1, as originally adopted"). Build reproducibility re-verified (REPRODUCIBLE YES, sig 26c3f13b1e907899) with the splice folded into `scripts/rebuild_const_modern.sh`. **Scratch only.**


## Batch `modern-groupa-clean-2026-06-15` — needs-base-source Group A (clean single-amendment) (SCRATCH)

`constitution.db` (scratch) · 2 provisions · +2 prior versions

The "needs-base-source" bucket was classified before the 1989 Blue Book was acquired; most of it is reconstructable from the 1981/1989 BBs + the validated historical layer. Group A = the two trivial single-amendment members:

- **art I § 1** (inalienable rights): #116 (eff 1984-12-06, "Establishes the right to bear arms") was a full restatement adding the keep-and-bear-arms clause and modernizing "men"→"individuals". Prepended prior [1981-01-01, 1984-12-05] = historical § 1 ("All men are by nature equally free…"; == 1981 BB, contained). Verified: 1982→"men", 1990→"individuals".
- **art X § 6** (poll tax): #154 (eff 2012-12-06, "Elimination of annual poll tax") repealed it. Prepended prior [1981-01-01, 2012-12-05] = historical § 180 (poll tax) with the editorial "($1.50)" dropped to match BOTH modern BB witnesses (modern witnesses govern the modern-era version, cf. art XII §12/§14). Verified: 1990→poll tax, 2015→Repealed.

Clean source = validated historical layer (1889 numbering, in force 1980 = the [1981, change) content), each confirmed present (despaced) in the modern-scheme Blue Book. Integrity 0 gaps; build re-verified REPRODUCIBLE (sig b90148005a643b3a, 693 versions). **Deferred to Group B: art XIII § 1** (turns out to be a 3-subsection 1996 drop, not trivial). **Scratch only.**


## Batch `modern-artxiii1-compact-1996-2026-06-15` — art XIII §1 pre-1996 Compact (Group B) (SCRATCH)

`constitution.db` (scratch) · 1 provision · +1 prior version (~11.4 KB, 3 subsections)

Amendment #132 (eff 1996-07-11, "eliminates outdated language … settling of territorial debts") kept only subsection 1 (modernized) and DELETED subsections 2 (federal public-lands disclaimer) and 3 (the 1889 territorial-debt settlement). Prepended the full pre-1996 text [1981-01-01, 1996-07-10].

Reconciled (subagent + gated): sub1 (toleration) identical across 1895/1913/1925/1989 BB; sub2 (disclaimer) = the POST-1958 version with the "provided, however … acceptance of such jurisdiction" clause, **verified == historical § 203** (ratio 0.998); sub3 (debt settlement, ~7.6 KB obsolete bond-list) transcribed from the 1913 official, all 14 dollar amounts cross-verified across 1895/1913/1925.

**Verification caught a witness trap:** the 1989 BB processed file is TRUNCATED mid-sub3 at a page break ("…discharge and exempt the"), so it can't witness sub3's full extent. Re-gated against the COMPLETE 1913 official compact: s1+s3 overlap 0.976, the only gap being the 189-char 1958 clause (legitimately in s2). Point-in-time verified: 1990 → full 3-subsection Compact; 2000 → toleration only. Integrity 0; build REPRODUCIBLE (sig 29a93c557d500027, 694 versions). **Scratch only.**


## Batch `modern-artv-pre1997-2026-06-15` — art V [1981,1997) crosswalk, 10 single-step sections (Group B) (SCRATCH)

`constitution.db` (scratch) · 10 provisions · +10 prior versions

The 1997 measure (#135) replaced/reorganized the executive article, reusing §-numbers for new content (a renumbering, like art IV). Prepended the pre-1997 ("old") content [1981-01-01, 1996-06-30] to the 10 single-step shared sections (§§ 2, 3, 4, 5, 6, 7, 8, 9, 10, 11). Pre-1997 text transcribed+reconciled from the 1989 Blue Book (the [1981,1997) witness) cross-checked vs the 1973 BB (subagent), gated here by overlap ≥0.97 against the 1989 BB section + old≠new. Verified: §3 1990→eligibility (governor age 30) / 2010→election of governor; §7 1990→lt-governor president of senate / 2010→powers of governor.

NOT in this batch: **§1, §12** (also carry a 1986 amendment → 3-version chains, next) and **§13** (pre-1997 only — no post-1997 citation; orphan). Integrity 0; build REPRODUCIBLE (sig 4a38f787cdea9c96, 704 versions). **Scratch only.**


## Batch `modern-artv-chains-1986-2026-06-15` — art V §1 & §12 3-version chains (Group B) (SCRATCH)

`constitution.db` (scratch) · 2 provisions · +4 versions

§1 and §12 changed twice in the modern era (1986 amendment #121/#122, then the 1997 replacement #135). Built each chain: [1981-01-01,1986-12-03] pre-1986 (validated historical layer §1←§71, §12←§82); [1986-12-04,1997-06-30] post-1986 (1989 BB, overlap 1.000/0.999); [1997-07-01,) current. 1986 transitions confirmed (§1 "year 1965"→"1988" + Dec-15 commencement sentence; §12 drops the "tax commissioner … no party ballot" sentence). pre≠post and post≠current both verified. Integrity 0; build REPRODUCIBLE (sig 1f9e987822580f9c, 708 versions).

**art V §§1-12 now fully covered for [1981,present).** Remaining: §13 (pre-1997 executive-officers section with no post-1997 citation — orphan, deferred like art IV §§17-46). **Scratch only.**


## Batch `modern-artviii6-chain-2026-06-15` — art VIII §6 Board of Higher Ed 4-version chain (Group B, FINAL) (SCRATCH)

`constitution.db` (scratch) · 1 provision · +3 versions (was a single [2000-07-13,open); all of [1981,2000) had been uncovered)

Built the full chain across the three modern amendments:
- [1981-01-01, 1994-12-07] base — marker-OCR 1989 Blue Book (the clean complete re-extraction)
- [1994-12-08, 1996-12-04] after #130 (1994 student member: 7→8 board, rewrote subsec 2 + 4)
- [1996-12-05, 2000-07-12] after #133 (1996: one-graduate→one bachelor's; 3→5 nominating committee; 7yr→4yr terms + two-term limit; "balanced and representative" sentence)
- [2000-07-13, open) current (#139: bachelor's cap one person→two persons)

Redlines read by subagent (1995 CAA p5 / 1997 SL7CNSTM p10 / 2001 CAA p1, rendered 450 dpi; the subagent verified base+#130+#133+#139==current forward, ratio 1.0). Intermediates rebuilt HERE by reverse-applying the localized #139 then #133 edits to the whitespace-normalized clean current text (so unchanged ~90% stays byte-identical), then independently gated: (a) v1996 vs current differs by exactly the one↔two-persons cap; (b) v1994 vs v1996 overlap 0.996 (the #133 bundle); (c) v1994's #130-untouched subsections (3,5) match the 1989 BB base verbatim. PIT verified across all three boundaries (1990: 7 members/7yr/no student; 1995: 8/+student; 1998: 4yr terms; 2005: two-persons cap). Integrity 0; build REPRODUCIBLE (sig 55b6b2f2e77a1b0f, 711 versions).

**Group B COMPLETE** (art XIII §1, art V §§1-12, art VIII §6). Remaining modern-layer tails are orphans only (art IV §§17-46, art V §13, art IV §§2/5/11 unconstitutional stubs — no/orphan modern citation). **Scratch only.**


## Batch `modern-artiv-stubs-1981-1986-2026-06-15` — art IV §§2/5/11 "[Unconstitutional.]" stubs (ORPHAN TAILS) (SCRATCH)

`constitution.db` (scratch) · 3 provisions · +3 prior versions

The 1981 Blue Book retained three legislative-apportionment sections (1960-amended frozen-district scheme, struck down in the 1960s reapportionment litigation) only as renumbered placeholders, printing each `Section N. [Unconstitutional.]` with no text (BB editorial note: "sections that have been declared unconstitutional have been retained and renumbered"). Those are new §§2, 5, 11. Per **user decision (2026-06-15): original text + void note** (not the bare marker, not an uncovered gap).

Prepended a `[1981-01-01, 1986-11-30]` version to each = a bracketed void note (resting on the BB's own "[Unconstitutional.]" designation + the 1986-12-01 recreation/repeal — no unverified case named) followed by the verbatim 1960 text from the validated historical layer. Crosswalk pinned positionally by the surrounding clean sections (1981 BB §3→1889 §27, §4→§28, [§5→§29], §6→§30 … [§11→§35] … §13→§37; §2→§26 before §3): **§2→1889 §26** (senate composition), **§5→§29** (senatorial districts), **§11→§35** (house apportionment); 1981 BB confirmed to print exactly §2/§5/§11 as "[Unconstitutional.]" at those positions. PIT verified: §2 as of 1983 → void note + apportionment text; as of 1990 → recreated text. Integrity 0; build REPRODUCIBLE. **Scratch only.**


## Batch `modern-artiv-dropped-1981-2026-06-15` — art IV §§17-46 dropped-section orphans (ORPHAN TAILS) (SCRATCH)

`constitution.db` (scratch) · 27 provisions created · +54 versions

art IV was repealed-and-recreated 1986-12-01 with a SHORTER article (§§1-16); old §§17-46 were repealed and not recreated, so no modern citation resolves to "art IV § N" for N in 17-46. Created each as a repealed provision (heading 'Repealed', status 'repealed', a final "Repealed." sentinel as current_version_id — matching the art X §6 / art XII §3-9 convention) with one content version covering the [1981-01-01, 1986-11-30] window it actually denoted. Text from the validated historical layer (1889 numbering) via the ARTIV-CROSSWALK-PLAN crosswalk, confirmed per section against the 1981 Blue Book (despaced ratio; 25 at ≥0.94, §25/§46 at 0.80/0.94 verified clean).

Created 27: old §§17,19-25,27-46. **§19 included** (its content survived by renumbering to new §11, but the *citation* "art IV §19" held the writs text only [1981,1986) and resolves to nothing today — parallel to §17/§18/§20+; §14/§15 citations are already covered via existing crosswalk prepends). Special cases: **§45** sourced from 1889 §202 ¶1 ONLY (the 1981 renumbering split §202 — its initiative-petition paragraph went elsewhere; full §202 ratio 0.49, ¶1 ratio 0.985); **§46** (member compensation, "five dollars per day") content window [1981-01-01, 1982-07-07] (repealed 1982, S.L. 1981 ch. 668; content moved to art XI §26). **§26 skipped** (did not exist at 1981 — the 1981 art IV jumps 25→27).

**DEFERRED (not created, documented in splice_artiv_dropped_1981.py):** §18 (governor/officer/manager interest in contracts — no clean 1889 §M carryover; likely a post-1889 addition whose only source is heavily space-garbled 1981 BB OCR) and §43 (enumerated special-legislation prohibition — its apparent 1889 source §69 was REPEALED effective 1980-10-02 per SCR 4006/1979 SL, so it may not have been in force at [1981,1986) at all; needs a clean witness to resolve). Deferred rather than risk fabricated/incorrect text in an authoritative DB. PIT verified (§25 as of 1983 → quorum; §46 as of 1981 → compensation, as of 1983 → Repealed; §17 as of 2020 → Repealed). Integrity 0; build REPRODUCIBLE. **Scratch only.**


## Batch `modern-artv13-orphan-2026-06-15` — art V §13 dropped-section orphan (ORPHAN TAILS) (SCRATCH)

`constitution.db` (scratch) · 1 provision · +2 versions

art V was repealed-and-recreated effective 1997-07-01 (measure #135); the recreated article has no §13. Created art V §13 (heading 'Repealed', status 'repealed') with a content version [1981-01-01, 1997-06-30] = the pre-1997 executive-officers powers/duties section ("The powers and duties of the secretary of state, auditor, treasurer … shall be prescribed by law …"), then "Repealed." [1997-07-01, open). Text from the validated historical layer 1889 §83 (clean; in force at the 1980 boundary), confirmed against the marker 1989 Blue Book executive §13 (despaced ratio 0.982 — the 1989 BB OCR has noise like "tudUor" for auditor). Integrity 0; build REPRODUCIBLE. **Scratch only.**

**Orphan tails COMPLETE** (art IV §§2/5/11 stubs, art IV §§17-46 dropped [27/29; §18/§43 deferred], art V §13). art VII §§1-11 + art XI §26 investigated: no [1981,1982) predecessor exists (data-confirmed — no art VII before the 1982 home-rule recreation), so genuinely new, no work. Modern point-in-time layer substantively complete: 494 provisions, 770 versions, integrity 0, quick_check ok, REPRODUCIBLE (sig 4970c645647d97cd). Snapshot-diff 1989 = 96.0% match-or-near (the marker-OCR witness); residual mismatches VI§12/X§5 (1989) and I§1/IV§1/IV§4/XIII§1 (1981) are PRE-EXISTING harness artifacts (correct DB text vs letter-spaced/mis-keyed comp — A/B verified zero new mismatches from this work). Also fixed snapshot_diff_modern.py to recognize the modern "Repealed." sentinel (REPEALED_OK 0→27 at 1989). **Scratch only — nothing promoted to live constitution.db.**


## Batch `modern-artiv-dropped-special-2026-06-15` — art IV §18 & §43 (the two formerly-deferred dropped sections) (SCRATCH)

`constitution.db` (scratch) · 2 provisions · +4 versions

Resolved the two sections deferred from `modern-artiv-dropped-1981-2026-06-15`, both with authoritative sources (user asked to source before live promotion):

- **§18** (anti-patronage, officer side: "The governor or any officer of this state … shall not appoint a member of the legislative assembly to any civil office … during the term …"). NOT in the 1889-numbered historical layer — it was added by amendment in 1938. Sourced from **N.D. Const. amend. art. LI** (1938-07-28→1980-12-31), verbatim/clean, ratio 0.991 vs the space-garbled 1981 BB §18. Companion to §17 (= 1889 §39, the legislator-side bar, already in the main batch). Created [1981-01-01,1986-11-30] → Repealed.

- **§43** (enumerated special-legislation prohibition). The main-batch deferral assumed 1889 §69 was fully repealed in 1980 — **incorrect**. **S.L. 1981 ch. 655 (SCR 4006, eff 1980-10-02), SECTION 2: "Subsection 6 of section 69 … is hereby repealed"** — ONLY subsection 6 (justices-of-the-peace/police-magistrate jurisdiction), collateral to abolishing county judges (§173). The other 34 enumerated items survived into [1981,1986) and were repealed only by the 1986 art IV recreation. Sourced from the validated historical layer 1889 §69 pre-repeal text MINUS subsection 6 (remaining items keep their original numbers — the session law renumbered nothing, so a gap at 6 is the faithful state; verified subsections present = 1-5,7-35). Full §69 (with sub 6) vs 1981 BB §43 = 0.98 (the BB is a pre-repeal snapshot). Created [1981-01-01,1986-11-30] → Repealed.

**⚠ Pre-existing historical-layer error found (flagged, NOT fixed here):** 1889 § 69's version [1980-10-02, 1980-12-31] is stored as "[Repealed effective 1980-10-02 …]" (FULL repeal) — overstating SCR 4006, which repealed only subsection 6. The correct post-1980 § 69 = the 34-item list (minus sub 6). This is in the LIVE/validated 1889 layer and wants a history-pipeline correction (ingest_constitution_history / const_history overlay), separate from this scratch modern-orphan work.

**art IV dropped sections now COMPLETE: 29/29** (old §§17-46 except §26, which did not exist at 1981). Modern point-in-time layer: 496 provisions, 774 versions, integrity 0, quick_check ok, REPRODUCIBLE (sig 9b62a5ece45a882c). Snapshot-diff 1989 = 96.1% match-or-near. **Scratch only — nothing promoted.**


## Fix `fix-s69-partial-repeal-2026-06-15` — 1889 § 69 was wrongly recorded as fully repealed (HISTORICAL LAYER)

`data/constitution_amendments.json` (source) + `constitution_history.db` + served `constitution.db`

Surfaced while sourcing art IV § 43 (above). Amendment CVII (SCR 4006, eff 1980-10-02) was coded in
constitution_amendments.json as a FULL repeal of § 69 (`action:"repeal"`, text `"[Repealed effective
1980-10-02]"`). The session law (S.L. 1981 ch. 655, SECTION 2) repealed only **subsection 6** of § 69
(jurisdiction of justices of the peace, police magistrates, constables), collateral to abolishing
county judges (§ 173). The other 34 enumerated special-law cases survived until the 1986 art IV
recreation.

Fix (canonical, at source): changed the CVII § 69 change to `action:"amend"` with text = the surviving
34-item list (subsections 1-5, 7-35; sub 6 removed, remaining numbers unchanged → gap at 6).
Regenerated constitution_history.db (`rm` + ingest_constitution_history --apply); a content diff vs the
backup confirmed ONLY § 69 changed (status repealed→active; the [1980-10-02,1980-12-31] version text).
Forward-synced the served constitution.db with `scripts/fix_s69_partial_repeal_2026-06-15.py` (avoids
re-fetching ndconst.org / a full re-merge; one provision, FTS reindexed; idempotent) — exactly what a
clean re-merge produces. A future full canonical rebuild reproduces it from the corrected JSON.

Verified: § 69 as of 1980-11-01 = the 34-item list (active); art IV § 43 as of 1983 = the same list;
despaced bodies equal — the 1889-numbering and 1981-numbering views now AGREE. § 69 as of 1950 still
has all 35 items (sub 6 present pre-repeal). Modern rebuild REPRODUCIBLE (sig 35528bd7c98f1cc9, 774
versions), integrity 0, quick_check ok.
