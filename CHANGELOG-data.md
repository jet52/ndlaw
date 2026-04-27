# Data Corrections Log

Changes applied to the opinions database after import from CourtListener and ndcourts.gov sources. All corrections are recorded in the `changelog` SQLite table and can be reverted with `python -m ndcourts_mcp.cleanup revert <batch>`.

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

Residuals (137 opinions with a westlaw .doc still not migrated):
- 110 — parser couldn't extract opinion text from the .doc (`SKIP: could not parse opinion text from Westlaw doc`)
- 27 — Westlaw text suspiciously short vs. existing DB text (`REJECT: < 30%` rule)

These are candidates for a manual triage pass — separate batch, do not auto-apply. After this batch, 5,598 opinions are westlaw-primary (out of 5,735 with a westlaw source linked).

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

## Batch: refs-migration-nd-opin (14,877 rows)

Applied 2026-04-18. Not a correction — a path-rewrite migration to align `source_path` values with the move of the source tree from `~/refs/opin/` to `~/refs/nd/opin/` (the canonical path documented in `~/refs/CLAUDE.md`).

Rewrite rules:
- Relative `ND/<year>/<file>.md` → `markdown/<year>/<file>.md` (7,408 rows across both tables). The `ND/` directory was renamed to `markdown/` to match the canonical layout.
- Absolute `/Users/jerod/refs/opin/...` → `/Users/jerod/refs/nd/opin/...` (74 rows, all Westlaw .doc files).

Tables touched: `opinions.source_path` (7,429 rows), `opinion_sources.source_path` (7,448 rows). Every row logged in changelog. No content changed, only paths.

Filesystem moves were atomic `mv` operations within the same filesystem. Backward-compat symlinks at `~/refs/opin/{ND,NW,NW2d,NW3d,N.D.,archive}` point into the new tree so other consumers (jetmemo-skill, jetcite, etc.) continue working through the symlink.
