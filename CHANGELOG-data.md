# Data Corrections Log

Changes applied to the opinions database after import from CourtListener and ndcourts.gov sources. All corrections are recorded in the `changelog` SQLite table and can be reverted with `python -m ndcourts_mcp.cleanup revert <batch>`.

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
