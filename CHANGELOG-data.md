# Data Corrections Log

Changes applied to the opinions database after import from CourtListener and ndcourts.gov sources. All corrections are recorded in the `changelog` SQLite table and can be reverted with `python -m ndcourts_mcp.cleanup revert <batch>`.

---
## ▶ Release v1.1.1 (2026-06-27) — correction release

Corpus 19,807 opinions (unchanged count; text corrections only). **2,623 corrections** this
cycle: corpus-proofing fleet rounds P37+P38 (94+71 opinions), full triage of all P37+P38 agent
flags (signatures restored, markers de-duplicated/repaired, citation/statute OCR fixed,
image-verified high-risk numbers), garbled-marker queue closed, and two deterministic sweeps —
**1,323 star-page word-splits rejoined** (991 opinions) and **51 inline 2026-scraper page-footers
removed** (13 opinions). New tooling: `marker_triage.py`, `fix_2026_page_footers.py`,
`fix_starpage_word_splits.py`. Invariants 24 ok / 0 regressed; detector 176/0; 79 tests.
Pending queues (markup cohort decision, structural-markers, fleet continuation) in
`TODO-validation.md`. Batch detail below.

---

## Batches `*-2026-06-27` (16918, 2017 ND 112) — flag misdiagnosis corrected + cleanup

Worked the P37 flags for 2017 ND 112. The fleet flagged `[¶15]` as "entirely missing"
(DB jumps 14→16) — **misdiagnosis**: the DB had a **duplicate `[¶16]`**, the first of which
("In *Donovan* this Court held…") is the PDF's `[¶15]`, mislabeled. Inserting the
described paragraph would have DUPLICATED the Donovan holding. Fix = renumber the first
`[¶16]`→`[¶15]` (`p37-marker-renumber-2026-06-27`); sequence now 1–22 contiguous. (Lesson:
verify every "missing_text" flag against the PDF before restoring.) Also in 16918:
- stored-twice dup deleted (`dedup-storedtwice-marker-2026-06-27`): corrupted `(¶ 10]`
  copy (paren marker, `Teso-ro`/`is not.` artifacts) + clean `[¶10]` copy.
- 6 party-name line-break de-hyphenations (`hyphenation-name-2026-06-27`): `Te-soro`/
  `Teso-ro`→`Tesoro` (×4), `Cey-nars`→`Ceynars` (×2); PDF has 32 Tesoro / 26 Ceynars,
  zero hyphenated. (Multiple occurrences → global replace, logged per name.)

Note: `marker_triage.py` does NOT catch paren-corrupted `(¶ N]` markers (ANCHOR matches
`[¶`/`*[¶` only) — candidate enhancement. Detector 176/0, invariants 24 ok/0, 76 tests.

## Batches `fix-2026-page-footers` + `fix-starpage-word-splits` (2026-06-27) — two deterministic queue sweeps

**2026 page-footer leak** (`fix-2026-page-footers-2026-06-27`, `scripts/fix_2026_page_footers.py`):
the 2026 scraper folded centered page-footer numbers inline ("noted 4 the"). Deterministic fix —
for each PDF centered lone-digit footer, take the exact bracketing words and remove only that
"W1 F W2"->"W1 W2" match. **51 leaks across 13 opinions** (2026 ND batch). Reusable for future scrapes.

**Star-page word-splits** (`fix-starpage-word-splits-2026-06-27`, `scripts/fix_starpage_word_splits.py`):
discovered the `\n\n *NNN\n\n` form is the NORMAL pre-1953 star-page rendering (6,660 correct
word-boundary markers), NOT a defect. Only genuine mid-word splits are defects ("re *287 demption"
= "redemption"). Fixed **1,323 splits across 991 opinions** with a two-part genuine-split test
(joined token appears whole elsewhere in the opinion AND neither fragment is a common word) +
**marker-before-word convention** (pincite-safe; CONVENTION CHOICE — revertible by batch if a
different placement is preferred). 91 common-word-fragment cases deferred (ambiguous: "in *214
forming"). Subsumes the prior 27-item star-page queue. Detector 176/0, invariants 24 ok/0, 79 tests.

## Batches `p38-flags-*-2026-06-27` — P38 flags triaged (45 substantive; 30 markup→cohort)

Worked all 75 P38 agent flags. 30 markup "other" → markup cohort. Of 45 substantive:
- **Names/abbrev/punct** (`p38-flags-ocr`): 16863 ROMANICK→Romanick / N.D.C.G.→N.D.C.C. /
  Ku-kowski→Kukowski; 16877 Dale Y.→Dale V. Sandstrom; 16887 Freeman v.→period / $…,66→.66;
  16906 Detonáis→Delonais ×17 / Albert-son→Albertson / Ad-dai→Addai; 16857 statute
  52-01-01(17)(a)(l)→(1) ×11 (em-dash + letter-l; NDCC uses no "(l)").
- **Image-verified high-risk** (`p38-flags-num`, `strip-injected-parallels`): 16877 "2.6 years"→
  "2.5 years" (image p6), 16890 "820 acres"→"320 acres" (image p3); 16905 stripped injected
  S.Ct./L.Ed.2d parallels off Strickland & Hill (court prints U.S.-only, image-confirmed).
- **Signatures** (`sig-restore`): 16858 [¶26], 16871 [¶27] restored verbatim from PDF.
- **Dups** (`dedup-storedtwice-marker`): 16857 [¶18]-copy-of-[¶13] deleted (same trap; NOT renumber).
- **Captions** (`p38-flags-caption`): 16878 (strip markdown '#' + de-all-caps), 19236 & 19226
  (designation reorders, PDF-verified); 16890 legal-description fractions (SEjiNEji→SE1/4NE1/4,
  SféSW/Q→S1/2SW1/4, SE]4→SE1/4, image-confirmed).
- **2026 page-footer leak** (`p38-flags-pagenum`): 20531 (2026 ND 126) — 5 inline page numbers
  removed (`needed 1 Stephanie`→`needed Stephanie`, `Jacobs- 3 Raak`→`Jacobs-Raak`, etc.).
  ⚠ Possible systemic 2026-scraper artifact — spot-check other new-2026 opinions.

**No-action:** 19212/19224/19225 filing-date stamps (intentionally stripped — strip_clerk_stamps
policy); 16868/16892 (already fixed in P38 main). **Deferred:** star-page word-splits 16838/16901/
16916×2/16886 → queue (now 27); cosmetic ellipsis 16890/16903, ampersand-markup 16858, quote
"good'. and" 16890. Detector 176/0, invariants 24 ok/0, 79 tests.

## Batch `corpus-proofing-p38-2026-06-27` — fleet round P38 (330 edits / 71 opinions)

Fleet round P38 = next 120 uncovered (the 14 new 2026 ND ~117–129 folded in + continuation
2017 ND ~91 → 2017 ND 1). 119/120 returned (1 dropped: 2017 ND 84, re-run separately); 442
proposals, 75 flags, 38 clean. Verifier → consolidate triple-evidence autosafe gate passed **323**
(ocr_char 188, split_join 99, whitespace 24, other 6, ocr_digit 4, missing_text 1, +1 heading
`Ill`→`III`), all PDF-confirmed. Examples: `reyenues`→`revenues`, `Bur gum`→`Burgum`,
`Rath-bun`→`Rathbun`, `(N.D.1995)`→`(N.D. 1995)`, `[[Image here]]`→`....`, and a PDF-verified
prose reconstruction (id16829 garbled pro-hac-vice clause).
- **7 captions** (`corpus-proofing-p38-captions-2026-06-27`, PDF-caption-verified): de-all-caps
  16866 (City of Grand Forks), 16904 (Gonzalez/State); designation reorders 19216 (Snyder=Appellee),
  19219 (Lowe=Appellant), 19227 (EduCap=Plaintiff/Appellee).
- **3 HEADING "renumbers" were actually stored-twice dups** (same trap as 16918): 16868/16892 a
  `[¶18]` copy of `[¶13]`, 16896 a `[¶8]` copy of `[¶3]` — DELETED the dup (renumber would have
  created a duplicate), not renumbered. (`dedup-storedtwice-marker-2026-06-27`.)
- **13 deferred**: 12 star-page word-splits → star-page rejoin queue (now 22); the 13th was the
  Ill→III heading (applied).

Detector 176/0, invariants 24 ok/0 regressed, 79 tests. 1 agent (2017 ND 84) re-running.

## Batch `ocrchar-flags-2026-06-27` — P37 ocr_char/split_join/whitespace/caption flags (26)

Worked the 26 remaining P37 flags. **11 applied** (each corroborated by DB internal consistency,
our own metadata, or PDF image — not a lone stale PDF):
- 16972 `N.D.O.C.`→`N.D.C.C.` (DB has N.D.C.C. ×71 vs N.D.O.C. ×1);
- 16974 `27-20-44(l)(c)(l)`→`(1)(c)(1)` (trailing `(2)` confirms numbered subsections);
- 16985 `l/4th`→`1/4th` ×2 (one-fourth interest); 17022 `[¶15]-North`→`[¶15] North`;
- 17006 `Tamavsky`→`Tarnavsky` (rn→m; our index has Tarnavsky v. Rankin = 2009 ND 149);
- 17028 `Cfi`→`Cf.` (fi-ligature for period in the signal);
- 17013 `New-field`→`Newfield` ×8 (DB has Newfield ×21 unhyphenated);
- 17039 `¾`→`'is` (PDF p141: "review 'is to determine"; straight quote per policy);
- **16925 `Alimón`→`Allmon` ×38** (systematic party-name OCR ll→li/o→ó; confirmed 3 ways:
  caption image "Angela R. Allmon / Aaron D. Allmon", CL case_name "Allmon v. Allmon", pdftotext ×46).

**No-action:** 16918 (Te-soro/Cey-nars already fixed earlier); 17010 (caption multi-line
*formatting* only, text correct); 17013 "ultimate liability" (already correct, no comma).
**Deferred — star-page rejoin** (`triage/p37-defer-starpage-2026-06-27.json`, now 10): 16957 ×2
(Peter|son, chil|dren across *919/*921), 16964 (pro|cess across *339).
**Deferred — cosmetic** (blank-line-run / ellipsis pass): 16983, 16993, 16996, 17013 ×2 (3+ blank
lines), 16961 (3-dot vs 4-dot ellipsis). **Deferred — complex:** 16998 (quoted §28-32-46 list:
item numbers 1–8 split from their text; needs PDF-based reconstruction).

Detector 176/0, invariants 24 ok/0, 79 tests.

## Batch `strip-injected-parallels-2026-06-27` — ingest-added U.S.-cite parallels removed (2)

16966 (2017 ND 153) and 16996 (2017 ND 190): the DB carried factually-correct S.Ct./L.Ed.2d
parallels on two U.S. Supreme Court cites that the court's opinion does NOT print (image-verified
PDF p5/p7 + user inspection: court cites only "Kansas v. Crane, 534 U.S. 407 (2002)" and
"United States v. Young, 470 U.S. 1, 11 (1985)"). Stripped the ingest-added parallels for fidelity
to the court's text. **Class note:** ~1,937 opinions carry a `U.S. N, N S.Ct.` parallel pattern,
but the large majority are legitimate (the court printed them); the contamination is only the
PDF-divergent subset, which the proofing fleet flags per-opinion (these 2 came from P37). NOT
bulk-strippable. Detector 176/0, invariants 24 ok/0, 79 tests.

## Batch `ocrdigit-safe-2026-06-27` — P37 ocr_digit/citation flags (ALL 11 resolved: 8 fixed, 3 no-action)

Worked the 11 P37 `ocr_digit`/`citation` flags with rule-4 discipline (citation digits verified
independently; internal DB consistency weighted over a lone PDF digit). **5 applied** (each
corroborated by the DB's own text, not a possibly-stale `~/refs` PDF):
- 16956 `at ¶ IB.`→`at ¶ 13.` (OCR letters; pincite sequence ¶12,¶13);
- 16985 `[¶80]`→`[¶30]` (DB's own marker sequence: gap at 30 + stray 80);
- 17008 `8,4,`→`8.4.` (rule-cite punctuation; DB renders 8.4 correctly elsewhere);
- 17011 `§ 65-04-83(2)`→`§ 65-04-33(2)` (DB has 65-04-33 ×22 vs 65-04-83 ×1);
- 17022 `27-10-01.4(l)(e)`→`27-10-01.4(1)(e)` (DB uses 27-10-01.4(1) ×8);
- 17008 `1.8(1)`→`1.8(l)` (ndlaw MCP: N.D.R. Prof. Conduct 1.8 is lettered (a)–(l); subsection
  (l) is the lawyer-as-fiduciary prohibition matching the cite context — DB digit-1 → letter-l).

**3 no-action — DB already correct, flag wrong:**
- 16955 (Foster): flag/pdftotext/`~/refs` render said "2015 ND 143", but the **official PDF
  (user-confirmed, docket 20150143) and our graph say 2015 ND 114** (Foster = 114 = 863 N.W.2d
  241; 2015 ND 143 is *State v. Smith*). The `~/refs` copy is a stale/typo'd version. DB right.
- 17030 (Lee): same pattern — DB "2015 ND 157" matches Lee + 864 N.W.2d 764 in our graph; the
  `~/refs` render's "182" is *Howe reinstatement*. DB right.
- 17036: DB "Rule 1.16" correct; pdftotext misreads digit-1 as letter-l.

  Lesson: a DB cite matching BOTH case name AND parallel reporter in our curated graph outweighs
  a single PDF's rendered digit (court typo or stale `~/refs` version). Do not "correct" a
  graph-consistent cite from one PDF.

**16966 + 16996** (DB-added U.S.-cite parallels) resolved separately — see
`strip-injected-parallels-2026-06-27` above. Detector 176/0, invariants 24 ok/0, 79 tests.

## Batches `parenmarker-repair` + `*-2026-06-27` — marker_triage paren/curly patch + finds

Patched `marker_triage.py` to catch mismatched-bracket marker corruptions `(¶ N]` / `{¶ N]`
(broadened ANCHOR + `norm_para`; a legit `(¶ N)` parenthetical cross-ref is routed to
not_marker, not flagged). Added 3 test cases (13 total) + fixed an out-dir-creation bug.
The patch immediately surfaced 7 corpus defects the old version missed:
- **6 paren-marker glyph repairs** (`parenmarker-repair-2026-06-27`): `(¶ N]`→`[¶N]`
  (digits intact, sequence-confirmed, not duplicated) — ids 14274, 15988, 16482, 16567,
  16796, 16898.
- **1 stored-twice dedup** (`dedup-storedtwice-marker-2026-06-27`): 15040 garbled `(¶ 6]`
  copy (`Const,`/`YI` artifacts) + clean `[¶6]`.
Post-fix sweep: 0 auto / 0 dedup / 1 needs_pdf (the deferred OCR-rotten 12932) / 0 unknown.
Detector 176/0, invariants 24 ok/0, 79 tests.

## Batches `*-2026-06-27` — P37 paragraph_seq + heading_seq flags (16 flags / 15 opinions)

Worked all 16 P37 `paragraph_seq`/`heading_seq` flags to closure; every opinion now has a
contiguous, dup-free marker sequence. Same duplicate-vs-missing discipline (PDF-verified):

- **3 more dropped signature blocks restored** (`sig-restore-2026-06-27`, verbatim from PDF):
  17010 `[¶51]` (Tufte, Crothers Acting C.J., Neumann S.J., Herauf D.J., El-Dweek D.J.),
  17017 `[¶24]`+`[¶25]` (VandeWalle C.J. panel + Paulson note; `*805` star-page preserved),
  17007 `[¶36]` (Tufte, McEvers, Kapsner S.J., Graff S.J., VandeWalle C.J.). 16984 also had
  its `[¶25]` signature misplaced mid-opinion + a bare end-tail — relocated to the end, full
  block restored.
- **8 stored-twice / mislabeled-duplicate deletions** (`dedup-storedtwice-marker-2026-06-27`,
  `paraseq-mixed`): 17009 (¶2), 17020 (`{¶ 20]` curly), 17034 (`[ITS]`→¶8 dup), 17031 (first
  `[¶36]` dups ¶35), 17010 (`[¶18] Rule 24` dups ¶13), 17011 (`[¶28] Section` dups ¶23),
  16983 (¶2), 16984 (`[¶28]` dups ¶23).
- **Renumbers** (`paraseq-mixed`, `16983-fix`): 16983 early `[¶48]`→`[¶43]` (fills the gap).
- **Heading fixes**: 16952 `HI`→`III` (OCR); 17023 `IV` moved from after `[¶27]` to before it
  (PDF order).
- **No action**: 17024 (already fixed in the P37 batch); 16918/17025 (done earlier).

Note: ~half these `paragraph_seq` flags were duplicate/mislabeled markers, not true gaps —
restoring would have duplicated text. `marker_triage.py` gap: it misses paren/curly-corrupted
`(¶`/`{¶` markers (anchor matches `[¶`/`*[¶`). Detector 176/0, invariants 24 ok/0, 76 tests.

## Batch `missingtext-rest-2026-06-27` — remaining P37 missing_text flags resolved

Worked the last of the 9 P37 `missing_text` flags. Genuine restorations (2):
- **16982** (2017 ND 171) — missing section heading `II` before `[¶7]` inserted (DB had
  I,III,IV,V; PDF I,II,III,IV). Sequence now I–V.
- **16993** (2017 ND 195) — `[[Image here]]` (WPD image placeholder) → `...`, the compact
  ellipsis the PDF prints for the omitted Rule 801(d)(1)(A) subsection (lines 130-133).

Misdiagnosed by the fleet (no text was missing) — corrected, not restored:
- **16996** (2017 ND 190) — **false alarm**: DB markers 1–23 contiguous, [¶14]–[¶19] match
  PDF verbatim ([1115]→[¶15] already fixed in the P37 batch). No action.
- **17010** (2017 ND 201) — not truncated: "expenses" is split across N.W.2d star-page
  (`ex` `*260` `penses`), "penses" present. → star-page rejoin queue
  (`triage/p37-defer-starpage-2026-06-27.json`, now 7), NOT a restoration.

**Tally of the 9 missing_text flags: 6 genuine fixes** (4 signature blocks +1 heading
+1 ellipsis), **3 misdiagnosed** (16918 duplicate-marker renumber, 16996 false alarm,
17010 star-page split). ~⅓ misdiagnosis rate — reinforces: verify every missing_text
flag against the PDF before restoring (a naive restore duplicates text). Detector 176/0,
invariants 24 ok/0 regressed, 76 tests.

## Batch `sig-restore-2026-06-27` — dropped signature blocks restored (4)

Restored four dropped/incomplete signature blocks flagged by the P37 fleet
(`triage/p37-flags-2026-06-27.json`), each VERBATIM from the court PDF (justice names +
designations, 6-space continuation indent per corpus convention); marker sequences now
contiguous:
- **17025** (2017 ND 213) — missing `[¶20]` (McEvers, Crothers, Tufte, Kapsner S.J.,
  VandeWalle C.J.) inserted before the `[¶21]` surrogate note.
- **16989** (2017 ND 182) — DB had only the trailing "Lisa Fair McEvers"; restored the
  `[¶16]` marker + VandeWalle C.J./Crothers/Kapsner/Tufte above it.
- **16980** (2017 ND 167) — DB had only "Gerald W. VandeWalle, C.J."; restored `[¶28]` +
  Kapsner/McEvers/Tufte/Crothers above it.
- **16959** (2017 ND 148) — missing `[¶16]` (Crothers, Tufte, Paulson S.J., Merrick S.J.,
  McEvers Acting C.J.) inserted before the `\*11[¶17]` surrogate note (the `\*11`
  star-page escape left for the markup pass). Surrogate panel (Paulson/Merrick S.J.).
Detector 176/0, invariants 24 ok/0 regressed, 76 tests.

## Batch `corpus-proofing-p37-2026-06-27` — fleet round P37 (789 edits / 92 opinions)

Resumed the corpus-proofing fleet from the date-DESC cursor (2017 ND 223 → 2017 ND 92,
offset 2244, 120 opinions). 118/120 agents returned (2 dropped on connection errors —
2017 ND 204/216 — re-run separately); 912 proposals + 118 flags, 10 clean opinions.
Verifier routed AUTO 12 / REVIEW 783 / REJECT 117; consolidate triple-evidence autosafe
gate passed **788** (whitespace 135, ocr_char 483, split_join 154, ocr_digit 7,
missing_text 5, other 4), all PDF-confirmed (new_exact verbatim in PDF, old not in PDF,
net-word-removal ≤ 2). Examples: `Amo u nt`→`Amount`, `Dis-cipl,`→`Discipl.`,
`holding- a suppler mental`→`holding a supplemental`, `[1126]`→`[¶26]` (garbled marker),
`•[¶11]`→`[¶11]`, a PDF-verified dropped signature block restored (id17033 `[¶30]`).
Plus: id16993 (one redundant overlapping proposal dropped + 1 residual `declar-ant`
line-break fix the agent missed, PDF-verified) and id16957 (`[¶26]`→`[¶25]` renumber
fixing a duplicate-26/missing-25 sequence, PDF-confirmed, no cascade). **6 deferred**
(split_join across an N.W.2d star-page, e.g. `ap *225 pealed`→`appealed`): the naive
rejoin deletes the functional `*NNN` pincite marker — routed to a star-page-aware rejoin
pass. The 2 dropped agents (2017 ND 204/216) were re-run (`--ids`) and folded in (+18
edits → batch total **807 edits / 94 opinions**). The 120 agent FLAGS (anomalies the
gate did not auto-fix) are captured in `triage/p37-flags-2026-06-27.json`: 58 markup
(separate pass) + 59 structural/citation routed to `STRUCTURAL-MARKERS-QUEUE.md` (incl.
PDF-verified dropped signature blocks + 10 high-risk `ocr_digit` citation flags).
Detector 176/0, invariants 24 ok/0 regressed, 76 tests.

## Batches `*-2026-06-27` — garbled-marker remaining queue CLOSED (23 fixed)

Worked the 26 deferred malformed markers (`triage/GARBLED-MARKERS-REMAINING.md`) to closure:
**23 fixed, 2 correctly left alone, 1 deferred.**

- **8 stored-twice duplicates deleted** (`dedup-storedtwice-marker-2026-06-27`,
  `garbled-marker-clean-2026-06-27`): the garbled `[¶\n *N]` / `[¶3'1]` / `[¶103` marker headed a
  corrupted FIRST copy (OCR errors, markdown `*…*`, page-number artifacts) immediately followed
  by a clean `[¶N]` copy of identical text. Deleted the garbled copy. Surfaced when the
  "markup-split" triage was re-checked against the paragraph sequence — 6 of the 16 nominal
  markup-split items were actually dups, plus 12773 (¶31) and 16775 (¶10). ids 12624, 13857
  (2-para block, OCR `trader`→`trailer`), 15105, 16655, 12791, 17024, 12773, 16775.
- **15 marker repairs** (`markup-split-marker-repair-2026-06-27`, `garbled-marker-clean-2026-06-27`,
  `garbled-marker-pdf-2026-06-27`): 10 markdown-emphasis-split `[¶\n *N]*`→`[¶N]`
  (sequence-confirmed, surrounding case-name italics left for the markup-cohort pass); 14010
  `*[¶*\n 1]`→`[¶1]`; and 4 PDF-image-verified: 16531 `[¶ `→`[¶28]`, 16656 `[¶1G]`→`[¶10]` (G=0),
  16777 `[¶'29]`→`[¶29]`, 14532 `[¶15J`→`[¶15]` (J=]).
- **2 left alone** (not in-text markers): 7514 `[¶3, Decree of Dissolution.]` (cross-reference to
  a decree) and 13911 `2003 ND 69, [¶]14, 660 N.W.2d 593` (pincite to a cited case; citation
  class — routed to a citation pass).
- **1 deferred**: 12932 (1999 ND 138) — pervasive OCR corruption (`declar-declar-must`,
  `subjecLto`, markers garbled as `[2] 9]` / `[3][¶`); piecemeal marker surgery unsafe, deferred
  to a full re-proof.

Newly surfaced adjacent **structural-marker defects** (missing/duplicate `[¶N]`, NOT garbled
glyphs) logged to `triage/STRUCTURAL-MARKERS-QUEUE.md` for a focused pass. Detector 176/0,
invariants 24 ok/0 regressed, 66 tests.

## Batch `trio-defer-applied-2026-06-25` — trio P34-36 deferred items worked (6 applied)

Worked the 52 trio-deferred items (`triage/PROOFING-P34-36-DEFERRED.md`). **6 applied**: id19320
(removed spurious "introduction of", PDF-verified), id19335 (leading-newline strip), 3 ellipsis
compactions (`. . . .`→`....`, the allowed direction over-deferred by the gate), id19332 (MOVED
section heading "II" to its own line — PDF-confirmed centered heading, not a delete). **45
no-action**: 35 star-page removals rejected (the `*NNN` are real N.W.2d page markers, verified
vs each cite — keep for pincites), 4 ellipsis widenings rejected (ND compact), 1 §-cite
space-insertion rejected, and 3 "Filed by Clerk" restorations rejected (user decision: keep
stripped per strip_clerk_stamps.py policy). **2 deferred**: id19311/id19314 (headings mashed
mid-paragraph; markdown has same mashing — need PDF heading reconciliation). Detector 175/0,
invariants 24/0, 66 tests.

## Batches `dedup-storedtwice-marker-2026-06-25` + `ocr-garbled-markers-batch2-2026-06-25` — deferred markers resolved + comprehensive marker sweep

**The 5 deferred garbled markers, hand-reviewed against the court PDFs:**
- id15794, id16543, id16642 — **stored-twice duplicate paragraphs**: the garbled marker headed
  a corrupted second copy of a clean adjacent paragraph (PDF-image-verified the court has ONE
  such paragraph, not two). Deleted the duplicate copy; sequences now contiguous.
- id13427 — duplicate disposition sentence under garbled `[¶ T2]`; removed the dup + marker,
  **footnotes 1-2 preserved**, clean `[¶12]` kept (PDF 2001 ND 154 verified).
- id12623 — 4 markers garbled by `]`→`J` (`[¶ lJ`/`[¶9J`/`[¶ lOJ`/`[¶ ll]`→`[¶1]`/`[¶9]`/`[¶10]`/
  `[¶11]`); all paragraph text present (verified complete vs markdown + PDF image).

**Comprehensive sweep** (`ocr-garbled-markers-batch2`) caught a class the first scan missed
(closing `]` garbled to `J`/`}`/`)`/`j`, or prefix `'`/`.`): **17 fixed**, all sequence-verified
(`[¶7}`/`[¶9J`/`[¶'8]`/`[¶341 Dale`→`[¶N]`). **26 malformed markers remain deferred**
(`triage/GARBLED-MARKERS-REMAINING.md`): 16 markup-split `[¶\n *N]*` (belong with the markup
cohort), 8 digit-ambiguous, 2 no-number, plus 5 XREF non-markers (`[¶3 of syllabus` — leave).
Detector 175/0, invariants 24/0, 66 tests.

## Batch `ocr-garbled-markers-2026-06-25` — fix OCR-garbled paragraph markers (30 of 35)

After despacing, 35 markers had the number itself OCR-garbled (digit misread as letters, e.g.
`[¶ IB]`, `[¶ ll]`, `[¶ S]`). Fixed 30 by **sequence continuity** — the value is fixed by the
neighbours (preceding N-1, following N+1, target absent ⇒ garbled = N), independent of the
glyph; a duplicate-guard required the target number to be absent. Spot-verified against PDF
images. Fixes: `[¶ IB]`→`[¶13]` (×7), `[¶ ll]`→`[¶11]`, `[¶ l]`/`[¶ i]`/`[¶ I]`→`[¶1]`,
`[¶ S]`→`[¶3]`/`[¶8]`, `[¶ IS]`→`[¶13]`/`[¶18]`/`[¶19]`, `[¶ IQ]`/`[¶ TO]`→`[¶10]`,
`[¶ Í4]`→`[¶14]`, `[¶ Í5]`→`[¶15]`, `[¶ [¶4]`→`[¶4]`. **5 deferred** (`triage/OCR-GARBLED-MARKERS.md`):
id12623/13427/15794/16543/16642 — the opinion's numbering is itself off-by-one/duplicated
relative to the court PDF (id15794's PDF has a genuine duplicate `[¶10]`), needing a full
per-opinion renumber, not a single-marker fix. Detector 175/0, invariants 24/0, 66 tests.

## Batch `despace-paragraph-markers-2026-06-25` — normalize `[¶ N]`→`[¶N]` corpus-wide (3,789 opinions)

The court prints in-text paragraph markers with no space inside the brackets (`[¶1]`) —
image-verified against the bound PDFs (1997 ND 7 shows `[¶1]`/`[¶2]`/`[¶3]`; 2008 ND 115). The
spaced form `[¶ N]` was an extraction artifact, proven by 1,360 opinions carrying BOTH forms
within a single document. `scripts/despace_paragraph_markers.py` collapsed the space(s) between
¶ and the paragraph number: **85,109 markers across 3,789 opinions** (2,429 spaced-only + 1,360
mixed). Digit-anchored (`\[¶ +\d`), so ~40 OCR-garbled forms (`[¶ IB]`, `[¶ ll]`, `[¶ l]` —
digit misreads) are untouched, left for the OCR-digit pass. Marker count invariant held per
opinion (only spaces removed). Corpus now uniform: 0 residual spaced digit-markers. Detector
175/0, invariants 24/0, 66 tests.

## Batches `corpus-proofing-p34-36-*-2026-06-25` — proofing fleet round (815 edits / ~146 opinions, 2019 ND 27 → 2017 ND 225)

Proofing fleet trio P34/P35/P36 (offsets 1870/1990/2110, 360 opinions, ~17.6M tokens). 1,092
proposals (100% source_quote), routed through `scripts/verify_proofing_proposals.py` (7 guards)
then `scripts/consolidate_proofing_trio.py` into apply / heading / caption / defer buckets.

- **`corpus-proofing-p34-36-2026-06-25`** (755 edits / 134 opinions) — triple-evidence autosafe
  gate (new ⊆ source_quote ⊆ PDF, net-word-removal ≤ 2, class ∈ {ocr_char, ocr_digit,
  missing_text, split_join, whitespace, other}, not ellipsis-spacing, not a star-page change,
  not a filing-stamp). ocr_char 392 (markup/italic strip, em-dash, `Tufté`→`Tufte`, OCR garbage),
  whitespace 203, split_join 122 (cite-reflow rejoins), other 25, ocr_digit 9, missing_text 4
  (incl. a recovered payment table and a dropped concurrence byline).
- **`corpus-proofing-p34-36-headings-2026-06-25`** (56 / 9) — `[¶ N]`→`[¶N]` marker spacing
  matched to the authoritative markdown source (verified the source uses no-space markers) + 6
  PDF-verified heading/marker moves (misplaced `[¶N]` to paragraph start; restored section
  heading `V`).
- **`corpus-proofing-p34-36-captions-2026-06-25`** (4 / 3) — de-all-caps party names
  (`OIEN`→`Oien`, `STATE`→`State`, `MBULU`→`Mbulu`) + party-designation relocation, all
  triple-evidence (new ⊆ source_quote ⊆ PDF).

Deferred (52, `triage/PROOFING-P34-36-DEFERRED.md`): filing-stamp restorations (intentional
strips), ellipsis-spacing, star-page-touching, net-removal>2/no_pdf, and 3 heading delete-vs-move
traps (id19332/19311/19314). ~226 rejected by guards (digit-in-cite, ellipsis-widen,
db-matches-pdf, confabulation). Detector 175/0, invariants 24/0, 66 tests.

## Batch `recover-lost-syllabus-header-2026-06-25` — restore dropped syllabus headers (20 opinions) — SYNOPSIS QUEUE CLOSED

The last 20 synopsis-leakage items (Class A in `triage/SYNOPSIS-DEFERRED-25.md`): `text_content`
began `Synopsis\n2.` (or `\n3.`/`\n4.`) because the West-doc parse dropped the
`*NNN Syllabus by the Court` header and the leading court syllabus point(s), leaving a stray
West `Synopsis` label atop the surviving numbered points. NOT a strip — a restoration.

`scripts/recover_lost_syllabus_header.py` prepended the dropped header + missing leading
point(s) 1..(first-1) from the authoritative West .doc, removing the stray label. Per-opinion
safety: the .doc's point `first` was alignment-checked (quote-normalized) against the DB's first
surviving point; everything from that point onward is byte-identical (only the header + missing
leading points were added). Doc curly quotes → straight (corpus convention); em/en-dash, §,
nbsp, and embedded star-pages preserved; output matches the canonical intact form
(`*NNN Syllabus by the Court.\n1. ...\n\xa0\n2. ...`). 15 opinions were missing point 1;
6418/13532/13875 missing points 1-2; 13633/13781 missing 1-3.

Detector 175/0, invariants 24/0, 66 tests. **The West synopsis-leakage queue is now CLOSED:
720/720 cleared, 0 live `Synopsis` labels corpus-wide** (138 on 2026-05-13 + 281 v2 + 75
adjudicated-81 + 201 long-217 + 3 order-recovery + 2 verify-first + 20 syllabus-header).

## Batch `synopsis-verify-first-2026-06-25` — West Synopsis, verify-first tail (2 opinions)

The two "verify-first" deferrals from `triage/SYNOPSIS-DEFERRED-25.md`, each resolved by
reading the opinion body first:
- **id2312** (*Strand v. Larson*, 1920) — confirmed the Robinson dissent is in the body
  (`ROBINSON, J.\n\nI dissent on the ground that...`); the synopsis notice was redundant.
  Partial strip: removed `Synopsis\nRobinson, J., dissenting.`, KEPT the `Appeal from District
  Court, McHenry County; A. G. Burr, Judge.` line (court record, appears only here).
- **id7135** (*Application of Christianson*, 1972) — confirmed the non-participation fact
  repeats more fully in the signature block (`ALVIN C. STRUTZ, C.J. ... did not participate;
  NORBERT J. MUGGLI, District Judge ... sitting in his stead.`); full strip of the redundant
  West synopsis note, star-page + Syllabus preserved.

Element-count invariants gated both. Detector 175/0, invariants 24/0, 66 tests. Synopsis-
leakage now **700/720 cleared**; 20 deferred, all Class A (lost-syllabus-header — needs PDF
header/point-1 recovery), tracked in `triage/SYNOPSIS-DEFERRED-25.md`.

## Batch `recover-disc-order-text-2026-06-25` — recover dropped ORDER bodies (3 opinions)

Three disciplinary opinions (id9351 *Lince*, id10797 *Goetz*, id20482 *McMahon*) whose ENTIRE
`text_content` was the West `Synopsis` — the court ORDER body was never ingested (the West-doc
parser dropped the ORDER for ORDER-format docs, the Disc. Bd. v. Johnson 481 N.W.2d 225 class).
These surfaced as the 3 "no-terminator" items in `triage/SYNOPSIS-DEFERRED-25.md` (full-strip
would have emptied them). Recovered the full court order from each authoritative West .doc
(`*NNN ORDER OF …` body, West furniture stripped), matching the corpus West-doc order
convention (id11076/id11239). Provenance unchanged (source_reporter stays `westlaw`, the West
.doc stays primary — respecting the 2026-06-22 restore-source-reporter-westlaw decision). Lince
177→1159 chars (incl. the justice signature block, which CourtListener's NW2d markdown lacked),
Goetz 296→1225, McMahon 386→1220. McMahon shares N.W.2d page 298/372 with *Boedecker v. St.
Alexius Hospital* (id8266) — that page's markdown is Boedecker, so the West .doc is the correct
source. Detector 175/0, invariants 24/0, 66 tests.

## Batch `synopsis-long-217-2026-06-25` — West Synopsis-leakage, long blocks (201 opinions)

Worked the 217 long (≥400 char) Synopsis blocks (`triage/synopsis-217-decisions.json`), where
the `Synopsis` label precedes a long span. Read each via `strip_synopsis_adjudicated.py`:

- **193 label-only** — court-voice statement of the case ("This is an action…", "The facts are
  not in dispute…", "Plaintiff, a minor…", "Action to determine adverse claims…"). The factual
  record is in scope ([[project_redistribution_scope]]); removed ONLY the orphan `Synopsis`
  label (9 chars), preserving all text.
- **8 full strips** — long West holding-summaries (e.g. "In disciplinary proceedings… the
  Supreme Court, Sand, J., held…", "On certified questions from the District Court…",
  id14645's modern "Background:" block). Each removed span verified to terminate at a real
  court element (`Syllabus by the Court` / `Attorneys and Law Firms`), removing the full West
  summary + disposition + dissent notes; element-count invariants gated every write.
- **16 deferred** — `Synopsis\n2.`/`\n3.` openings that turned out to be a *lost-syllabus-
  header* defect (West parse dropped the `Syllabus by the Court` header and point 1, leaving
  numbered court syllabus points under a stray label). Needs PDF-based header/point-1 recovery,
  not a label strip. Logged with the rest of the deferred tail in `triage/SYNOPSIS-DEFERRED-25.md`.

Detector 175/0, invariants 24/0, 66 tests. Synopsis-leakage queue: **695 of 720 cleared**
(138 + 281 + 75 + 201); **25 deferred** (20 lost-syllabus-header, 3 no-terminator disciplinary
summaries, 2 mixed/verify-first) — see `triage/SYNOPSIS-DEFERRED-25.md`.

## Batch `synopsis-adjudicated-81-2026-06-25` — West Synopsis-leakage, per-item adjudication (75 opinions)

Per-item pass over the 81 short Synopsis blocks the strict v2 whitelist held back
(`triage/synopsis-81-decisions.json`). Each read against its terminator and adjudicated via
`scripts/strip_synopsis_adjudicated.py` (same structural invariants as v2: removed span
contains no court element; syllabus-variant / star-page / `Attorneys` counts byte-identical
before/after):

- **49 full strips** — whole block is West editorial the regex classifier missed:
  dispositions the v1 patterns skipped (`Order denying a new trial reversed, and a new trial
  ordered.`, `Judgment of the district court reversed and action dismissed.`), separate-opinion
  notices (`Burke, J., dissented.`, `Teigen, J., dissented in part and filed opinion.`),
  motions/answers (`Questions answered.`, `Motion to dismiss appeal denied...`), West
  procedural-posture synopses (`The District Court of X County, [Judge], J., entered judgment
  ... appealed. The Supreme Court held...`), and the two disbarment holding-summaries. The
  court Syllabus / ORDER preserved verbatim in every case.
- **26 label-only strips** — removed ONLY the orphan `Synopsis` label (9 chars), preserving
  the court-voice factual record (`This is an action...`, `Defendant was informed against...`,
  `Facts:...`) and counsel-appearance blocks that West mislabeled `Synopsis`. The label is
  West's section furniture; the text it wrapped is in scope ([[project_redistribution_scope]]).
- **6 deferred** — structural oddities needing a closer read: 4 where `Synopsis` sits *inside*
  a numbered syllabus point (id6441/6458/7249/13781), a mixed dissent+appeal-from line
  (id2312), and a non-participation note (id7135, verify it repeats in the body before strip).

Detector 175/0, invariants 24/0, 66 tests. Synopsis-leakage queue: 494 cleared across all
batches (138 on 2026-05-13 + 281 v2 + 75 here), 226 remaining (217 long factual-record-bearing
+ 6 deferred here + 3 no-marker).

## Batch `strip-west-synopsis-v2-2026-06-25` — West Synopsis-leakage strip, deferred set (281 opinions)

Stripped residual West editorial `Synopsis` blocks from 281 West-sourced opinions — the
deferred half of the synopsis-leakage scan (`triage/SYNOPSIS-LEAKAGE-SCAN.md`) that v1
(`strip_west_synopsis.py`) could not handle. v1 only stripped blocks bounded *directly* by
`Attorneys and Law Firms` with no court Syllabus between; the larger set has the West
`Synopsis` note sitting immediately before the court `Syllabus by the Court` or a star-page.

New applier `scripts/strip_west_synopsis_v2.py` generalizes the terminator to the FIRST
following court element — a Syllabus label (incl. OCR variants `S[uy]l+[ai]bus`, e.g.
`Sullabus`), a star-page (`**52`/`*329`), `Attorneys and Law Firms`, or `Opinion` — and
preserves it verbatim. Removed spans are West editorial only: bare `Synopsis` labels (132),
disposition notes (`Affirmed.`, `Judgment reversed and case remanded with directions.`),
separate-opinion notices (`Burke, J., dissented.`), cross-references (`See, also, 167 N. W.
366.`, `For former opinion, see 27 N. D. 391.`), and rehearing notes. Selection was strict:
any block resembling a factual statement of the case (`This is an action...`, `Defendant was
informed against...`, `Facts:...`) was held back for individual handling, per
[[project_redistribution_scope]] (factual record stays) and [[project_court_syllabus]] (court
Syllabus stays).

Hard invariants gated every write: the removed span contains no court element, and the
counts of syllabus-variants, star-pages, and `Attorneys and Law Firms` are byte-identical
before and after — so only West editorial matter could be removed, never court text.
Dry-run + per-terminator spot-checks (star-/attorneys-/opinion-terminated, 32 cases where the
Synopsis block sits after the syllabus) confirmed clean joins. Of the 582 live-Synopsis
opinions, 281 stripped here; the remainder (long blocks containing factual record, and ~80
factual/ambiguous short blocks) stay deferred for per-item reading. Detector 175/0,
invariants 24/0, 66 tests.

## Batches `caption-residual` + `ellipsis-compact-2026-06-24` — manual-residual drain (11 opinions)

Drained the 188-item manual queue from fleet rounds P28-33 (see
`triage/RESIDUAL-DISPOSITION-2026-06-24.md`). Applied: 9 captions (designation relocation +
`LAVALLIE`->`Lavallie`, triple-evidence verified) and 2 ellipsis compactions (DB spaced
`. . . .` -> compact `....`, the valid direction). Resolved-no-action: 41 ellipsis-WIDEN
(pdftotext column-padding artifact; ND prints compact) + 21 signature-indent (corpus is
1-space) + stale Grenz heading-deletes (superseded by heading_move). ~66 genuine-judgment
items (scrambles/missing_text/deletions failing the triple-evidence gate) documented for a
focused pass. Detector 175/0, invariants 24/0, 66 tests.

## Batch `corpus-proofing-p31-33-2026-06-24` + `heading-moves-p31-33` — fleet round 2 (63 opinions, 2020 ND 80 → 2019 ND 9)

Second concurrent fleet round (offsets 1510-1870; re-run after the monthly-spend cap was
lifted mid-round — failed agents re-run via `--ids`, the 71 successes reused). 360 opinions
proofed; **source_quote 100%**. First round fully driven by the mechanized pipeline:

- **60 opinions** auto-applied via the triple-evidence gate (`new ⊆ source_quote ⊆ PDF`,
  net-removal ≤2): ocr_char (markdown/LaTeX markup removal `*State v. X*`->`State v. X`,
  `$State\ v.\ Tupa$`->`State v. Tupa`), split_join word-restorations/scramble reorders,
  missing_text, whitespace.
- **3 opinions / 5 section-heading MOVES** via `heading_move.py` (incl. fused `III[¶7]`).
- Guards auto-routed the rest: `guard_digit_in_cite`, `guard_unverified_quote` (×2
  confabulations — the source_quote binding catching fabricated reconstructions),
  `guard_probable_heading_move`. 25 cite-reflows already cleared by rejoin v2.

**Two gate improvements made mid-round (both caught in dry-run spot-checks, nothing bad
applied):**
1. **Ellipsis-widen exclusion** — 44 proposals widening `...`->`. . .` were routed away from
   auto-apply. ND prints compact ellipses; pdftotext's spaced `. . .` is column-padding, so
   the spaced form passes the `⊆ PDF` test but is an artifact (image-verify, don't auto-apply).
2. **Broadened `guard_digit_in_cite` `_CITE`** to a generic `VOL REPORTER PAGE` matcher
   covering regional/state reporters. Caught id 17521 changing `81 Cal.App.3d 614` ->
   `146 Cal. Rptr. 535` — a citation digit change the ND/federal-only pattern missed.

Detector 175/0, invariants 24/0, 66 tests (after each apply).

## Batch `citation-rejoin-v2-2026-06-24` — fragmented-citation rejoin v2 (2,416 opinions)

Mechanization #1 to drain the per-round cite-reflow queue. Extended
`scripts/rejoin_citations.py` with three patterns v1 missed (the dominant residual):
PAREN_FRAG (`446\n (quoting` -> `446 (quoting` — a citation number/`)` orphaned from a
following indented parenthetical), ID_PAREN (`Id.\n (` -> `Id. (`), REPORTER_NUM
(`915 N.W.2d\n106` -> `915 N.W.2d 106`). Broadened the candidate scan to the whole corpus
(the alpha+digit multiset gate guarantees content-preservation, so a broad scan is safe).
Validated against the deferred reflow set (20/38 rejoined, 0 multiset violations; the rest
were other classes — hyphenation/headings/signatures — correctly untouched) and sampled
5,929 PAREN_FRAG + 525 REPORTER_NUM firings (all legitimate citation parentheticals,
`(1961)`/`(3d Cir`/`N.D.\n1946`). Applied: **2,416 opinions, 0 skipped on the multiset
gate, 7,264 stray chars removed.** Detector 175/0, invariants 24/0, 66 tests.

## Batch `heading-moves-2026-06-24` — automated section-heading MOVES (5 opinions, 17 headings)

Mechanization #2 (`scripts/heading_move.py`). Converts the recurring delete-vs-move trap
into a safe automatic MOVE: drives off the court PDF's standalone-heading SET (robust to
older PDFs that render ¶ numbers in the margin with no inline `[¶N]`), scans the DB for a
heading letter merged onto the line before its `[¶N]`, and relocates it to its own line —
never deletes. Verified: 0 false positives on already-fixed opinions (Dearinger 19647);
the OCR-garbage letters (`T`, `$` in id 19509 Grenz) aren't heading-shaped so aren't
matched, and a non-heading `VII` (id 19622, likely a "Title VII" reference) was correctly
excluded as not-in-PDF-heading-set. Applied A/B/C/I/II/III/V moves across id 17766, 19405,
19509 (Grenz, 7), 19522, 19629. Detector 175/0, invariants 24/0, 66 tests.

## Batch `corpus-proofing-p28-30-2026-06-24` — concurrent fleet P28-30 (35 opinions, 2021 ND 165 → 2020 ND 75)

First round on the hardened pipeline (3 fleets concurrent, 360 opinions, 228 clean).
Proposals now carry `source_quote` (100% compliance). Applied 35 opinions' worth of
**double-evidenced** content fixes via a triple gate: `new_exact ⊆ source_quote ⊆ court PDF`
AND net-word-removal ≤ 2 (excludes deletions/scrambles needing judgment). Classes:
ocr_char, ocr_digit (prose), missing_text, split_join (word-restoration/reorder), whitespace,
other. Detector 175/0, invariants 24/0, 66 tests.

The verifier guards auto-handled ~48 items this round: **12 `guard_digit_in_cite`** (citation
digit corruptions auto-rejected — incl. several that would have changed correct cites),
**1 `guard_unverified_quote`** (a confabulated reconstruction caught by the source_quote
binding — invisible to deterministic guards), **13 `guard_probable_heading_move`** (stray
section-letter deletes flagged as moves, incl. the id 19509 Grenz multi-heading opinion),
and 21 `guard_whitespace_convention` (signature indents demoted).

Deferred (not applied this round): 38 content-preserving citation reflows ->
citation-rejoin v2 (`triage/p28-30-defer-rejoin.json`); 70 items needing judgment
(heading-moves, captions, multi-word deletions, items failing the triple gate) ->
`triage/p28-30-manual.json`. A net-deletion gate-hole was caught in dry-run (a `". $9,000
... Despite"->"."` deletion matched the weak `new⊆source_quote` test trivially); fixed by
adding the net-word-removal guard before any apply.

## Batch `corpus-proofing-p27-2026-06-24` — proofing fleet P27 (11 opinions, 2022 ND 47 → 2021 ND 166)

Low-noise cycle (96/120 clean). Verifier: 12 auto / 16 review / 12 reject. Applied 15 fixes
across 11 opinions after the consolidated triage; all PDF-verified.

- **2022 ND 35** (id 19698, Pavlicek): scramble — restored `commercial general liability
  insurance (CGL)` (¶1 had dropped `liability insurance`, with `liability` orphaned after the
  byline and `insurance` trailing ¶1). PDF lines 43-44 confirm.
- **2021 ND 226** (id 19619, Brown): scramble — `(citing N.D.R.Ev. 1101(d)(3)(C))` parenthetical
  was displaced into the middle of `do not apply ... to preliminary hearings`; restored to the
  end with `Id.`
- **2021 ND 171** (id 19603, Continental): two scrambles — `seized or possessed of the premises
  in question within twenty years before the commencement`, and `Unjust enrichment requires:
  (1) an enrichment; (2) an impoverishment; (3) a connection`.
- **2021 ND 183** (id 17886, Kerzmann): `Section 14-09-06.6(6)(b) requires` -> `...(6)(b),
  N.D.C.C., requires` (PDF ¶12).
- **2021 ND 189** (id 19608, A.S.F.): heading `III` moved from after [¶13] to before it (PDF).
- **2022 ND 33** (id 19696, Goldade-Jose): caption reorder (`and` repositioned; word-multiset
  preserved).
- **2022 ND 27** (id 19694): removed stray OCR `4` (`under the 4 influence`).
- **2022 ND 24** (id 17950): `2 022 ND 24`->`2022 ND 24`, caption `V.`->`v.`, `Logist`->`Logistics`.
- **2021 ND ?** (id 17911): OCR `does not Srender`->`does not render`.
- Whitespace (id 19700 trailing space; id 17903 blank-line collapse around page numbers).

Not applied:
- **id 17945 (2022 ND 16, Pomarleau) REJECTED** — agent proposed `2000 ND 203, ¶ 14, 621 N.W.2d
  314` -> `619 N.W.2d 501` from the PDF text layer, but the actual 2000 ND 203 opinion (id 13291)
  self-cites as **621 N.W.2d 314** — the DB is correct; the change would corrupt it. Digit-class
  trap (never trust the text layer for digits).
- **id 17940 (2022 ND 5) REJECTED** — proposed splitting the statute number `§ 29-32.1-12` across
  a line (`29-32.1-\n12`); the DB's joined form is correct.
- **id 19614 (2021 ND 206, Chase) DEFERRED** — agent's reconstructed word `allege` appears nowhere
  in the PDF; needs correct reconstruction.
- 4 signature-indent auto items (id 17884) rejected (corpus 1-space convention); 5 citation/`Id.`
  reflows deferred to citation-rejoin v2 (`triage/p27-defer-rejoin.json`).

## Batch `west-synopsis-strip-2026-06-24` — strip residual West Synopsis blocks (138 opinions)

Acting on the corpus-wide synopsis-leakage scan (`triage/SYNOPSIS-LEAKAGE-SCAN.md`): 720
opinions carried a residual West `Synopsis` block (West editorial — case summary, procedural
posture, disposition restatement, or separate-opinion list) the earlier
`strip-westlaw-synopsis-2026-05-13` batch missed. Stripped the **conservatively safe subset**
only — 116 post-1953 + 22 pre-1953 = **138 opinions** — via `scripts/strip_west_synopsis.py`.

Strip fired ONLY when the Synopsis block was immediately bounded by `Attorneys and Law
Firms` (the West header position), ≤400 chars, with **hard gates**: contains no
`Syllabus by the Court` (incl. OCR variants — see below), no opinion-body marker; and the
court Syllabus + body paragraph fingerprint must be byte-identical before/after. Examples
removed: `Synopsis\nReversed, and a new trial ordered.`, `Synopsis\nMeschke, J., filed a
concurring opinion.`, `Synopsis\nSee, also, 26 N. D. 77, 143 N. W. 764...`. Counsel, byline,
syllabus, and body untouched. Detector 175/0, invariants 24/0, 66 tests pass.

**Landmine caught:** id 12215's block was `Synopsis\nOrder affirmed.\n\nSullabus by the Court.\n
An action under the declaratory judgment...` — the court's syllabus **OCR-misspelled as
"Sullabus"**, so the literal `Syllabus by the Court` gate missed it. Hardened the gate to
`(?i)s[uy]ll?ab[uo]s` + `by the Court`; id 12215 correctly skipped (syllabus preserved).

**Not stripped (582, deferred to individual handling):** blocks >400 chars / no clean
`Attorneys` boundary (the Synopsis content has no clean end before the body — e.g. id 559's
18k-char span), Synopsis-before-Syllabus (Syllabus-bounded, 293), and 43 where the
body/syllabus fingerprint would change. These need per-opinion boundary work; the safe
automated subset is done. Worklist: `triage/synopsis-leakage-worklist.json`.

## Batch `west-furniture-strip-2026-06-24` (part 1) — star-pages + header labels (44 opinions)

First step of the West-furniture-strip pass over the 45 modern (≥1997) West-`.doc`-sourced
opinions identified in the audit (`triage/WESTDOC-MODERN-AUDIT.md`). **Wholesale
re-derivation from the court markdown was rejected** after analysis: it would discard heavy
curation (footnote `[N]` resolution, self-cite/keynote stripping, quote-norm — 12 of 43
carry `[N]` footnotes that feed the detector) and import the scraper's raw `<sup>`/scramble
artifacts, regressing the footnote detector. Instead, strip the residual West editorial
furniture from the curated text (user-approved).

This step removed, from 44 opinions (1 noop): West N.W. **star-page markers** (`*NNN`,
e.g. `district court postponed *103 Nelson's`) inserted for reporter pagination, and the
`Attorneys and Law Firms` / `Opinion` **section labels** where they sat at the header start.
Per-opinion safety gates (all passed): `[¶N]`/`[¶ N]` marker count unchanged, `[N]`
footnote-call count unchanged, no star-page may remain, no new double-/leading-spaces.
Counsel names and the justice byline are court text and were kept. Detector 175/0
(no regression), invariants 24/0, 66 tests pass. Tool: `scripts/strip_west_furniture.py`.

### Part 2 (batch `west-furniture-strip-pt2-2026-06-24`) — Synopsis blocks + mid-header labels (30 opinions)

The 31 opinions with complex West headers carried a West **Synopsis** block (18 with the
full `Background:`/`Holdings:` summary the earlier strip batch missed; the rest a residual
`Synopsis` label) and/or West subsequent-history notes (`Opinion, 14 N.W.3d 45,
superseded.`) and a West reporter caption (id 19532: `950 N.W.2d 761 (Mem) / Supreme Court
of North Dakota. / STATE of...`), all sitting before the counsel block. Removed everything
from the start of `text_content` up to and including the `Attorneys and Law Firms` label —
**only** when that prefix is unmistakably West editorial (begins with `Synopsis`, a reporter
cite, or contains `Supreme Court of North Dakota.`) **and** contains no opinion-body
paragraph marker. 30 opinions stripped (34–1,951 chars each); counsel + byline + body kept.

**Excluded: id 20044 (2024 ND 70, H.J.J.N.)** — its pre-label prefix is the court's own
`Appeal from the Juvenile Court...` jurisdiction line, not synopsis; the guard correctly
left it untouched. It belongs to the deferred H.J.J.N. provenance fix.

After both parts: across the 45, **0 star-pages, 0 Synopsis blocks, 0 `Background:`/
`Holdings:`** remain; the only residual `Attorneys and Law Firms` label is on the deferred
id 20044. Detector 175/0 (no regression), invariants 24/0, 66 tests pass.

## Batch `westdoc-cleanup-2026-06-24` — strip West-added parallel citations (2023 ND 231)

- **2023 ND 231** (id 19804, State v. Bearce): removed 5 West-editor-added parallel
  citations (`, 967 N.W.2d 765`) appended to short-form references to *State v. Neilan*,
  2021 ND 217. The court's published text (verified against `2023ND231.pdf` and
  `markdown/2023/2023ND231.md`) cites the case in full once (¶15: `State v. Neilan, 2021
  ND 217, 967 N.W.2d 765`) and uses short forms (`Neilan, 2021 ND 217, ¶ X` / `Id.`)
  thereafter. The West `.doc` rendering (the row's `source_path`) had appended the parallel
  reporter to ¶¶ 2, 4/13, 22, 23, 23. The single legitimate first-cite parallel is kept.
  (The agent's original proposal caught only 3 of the 5; verified all instances.)

### Deferred finding — H.J.J.N. provenance (NOT applied)

Investigating the second "West-doc item" (a `*776` star-page removal in id 20044) surfaced
a provenance issue rather than a cleanup: **id 20044 = 2024 ND 70** (interim, retain
jurisdiction, 5 N.W.3d 775) and its sibling **id 19877 = 2024 ND 132** (post-remand, 9
N.W.3d 656) — two decisions sharing docket 20240060 — both store the **West `.doc`
rendering** as `text_content` (West star-pages `*776`/`*777`/`*657`, "Attorneys and Law
Firms"/"Opinion" section labels, West citation forms) even though authoritative court PDFs
exist. The court PDFs are **misfiled/swapped**: `pdfs/2024/2024ND70.pdf` contains 2024 ND
132 and `pdfs/2024/2024ND132.pdf` contains 2024 ND 70; `markdown/2024/2024ND70.md` also
contains 2024 ND 132. Proper fix = re-derive both opinions' `text_content` from the correctly
identified court source (and correct the misfiled PDF/markdown names). Tracked in
`triage/ocr-cleanup-dispositions-2026-06-24.json`. Not band-aided with a single star-page
deletion.

## Batch `headings-2026-06-24-b` — ambiguous heading reformats (3 opinions, 13 edits)

The three heading opinions deferred from the first heading pass (ambiguous: parallel
A/B/C sequences and encoding-artifact glyphs). Each resolved against its PDF.

- **2022 ND 85** (id 19709, Energy Transfer): the `A An` ambiguity — `A` is the subsection
  heading (PDF line 272), `An administrative agency...` is the block-quote text. Moved `A`
  to its own line before [¶14]; moved `B` before [¶22]. (Agent proposed deleting `A`.)
- **2025 ND 61** (id 20271, Jones v. Jones): two parallel A/B/C sequences (under II: A→¶6,
  B→¶11, C→¶15; under III: A→¶17, B→¶18, C→¶24). All six moved to their own lines, mapped
  to the correct paragraph via the PDF. `B`→¶11 had been pulled into the paragraph
  (`provides, B If`); restored as a heading before [¶11], leaving `provides, If`.
- **2024 ND 171** (id 19920, Mitzel v. Vogel Law Firm): five section headings stored as
  encoding/markup artifacts (also a markup-cohort member), all standalone in the correct
  position but wrong glyph: `В` (Cyrillic Ve)→`B` at ¶14/¶37, `$\mathsf{C}$` (LaTeX)→`C` at
  ¶17/¶46, `Α` (Greek Alpha)→`A` at ¶35. The agent had proposed `Α`->`C`; PDF line 490
  confirms the heading before [¶35] is `A`.

## Batch `scramble-bucket-2026-06-24` — pdfminer column-scrambles (3 opinions, 8 edits)

Manual reconstruction of three scrambled opinions the reconciler couldn't auto-fix (its
per-paragraph pure-reorder gate doesn't fire on cross-boundary scrambles or scrambles
mixing citations into prose). Each repaired against the opinion's PDF; all token-conserving
(displaced fragments relocated, not deleted).

- **2023 ND 179** (id 19765, Williamson v. State): cross-boundary — `confidential
  attorney-client` was dangling at the end of ¶1; restored to ¶2's quote
  (`"appropriate confidential attorney-client communication"`).
- **2022 ND 145** (id 19658, Lovro v. City of Finley): the phrase `is to "prevent judicial
  'second-guessing' of` was displaced (and internally reordered) to before [¶13]; restored
  to its place after `the discretionary function exception`.
- **2023 ND 78** (id 19830, Fietzek v. Fietzek): two scrambles. (1) The citation `2008 ND
  58, ¶ 15` was scrambled (as `2008 ND 15, 58, ¶`) into `wasted asset` and dropped from the
  `Hitz, ... 746 N.W.2d 732` cite; restored to `Hitz, 2008 ND 58, ¶ 15, 746 N.W.2d 732` and
  `wasted asset` cleaned. (2) `fact subject to the` was displaced after `10 years.`;
  restored to `finding of fact subject to the clearly erroneous standard`.

## Batch `ocr-cleanup-2026-06-24` — deferred-queue OCR/cleanup (12 fixes, 11 opinions)

Worked the genuinely-actionable OCR/cleanup items from the deferred queues (after an
inventory found 72 of 115 live items were already owned by rejoin-v2 or the markup
cohort). Every fix PDF-verified against the opinion's correct PDF (cites re-derived from
`source_path`, not guessed). Two agent proposals were reversed from DELETE to MOVE, and
one was rejected outright (see below).

Applied:
- **2022 ND 103** (id 18024): removed prepended markdown metadata header (title/court/
  citation/date) — not part of the published opinion.
- **2022 ND 183** (id 18082): `SW1/4` -> `SW¼` (typographic fraction, PDF line 78).
- **2023 ND 154** (id 18224): OCR'd neutral-cite header `2023 IN 1) 154` -> `2023 ND 154`;
  removed adjacent OCR garbage line `2020 * T n -`.
- **2023 ND 11** (id 19717): removed a FILED/docket stamp OCR-spliced mid-sentence before
  `report` (joins cleanly to `...filed a report`).
- **2023 ND 16** (id 19744): scramble MOVE — `to be` was displaced before `The agreement`;
  restored to `The agreement does not appear to be substantively`. (Agent proposed
  deleting `to be`, which would have lost it.)
- **2023 ND 97** (id 19837): caption party-separator OCR garbage `V. D.C. 1 1 A 11` -> `v.`
- **2024 ND 68** (id 20041): removed OCR garbage line `0004 NIT 00`.
- **2022 ND 231** (id 18114): restored corrupted citation `(quoting Willprecht, 2020 ND at
  ¶ 11)` -> `(quoting Willprecht v. Willprecht, 2021 ND 17, ¶ 11, 954 N.W.2d 707)` (PDF
  line 234).
- **2023 ND 130** (id 19730): heading MOVE — `V` was misplaced before the signature block
  [¶22]; relocated before the disposition [¶21] (PDF line 313). Paired edits.
- **2023 ND 182** (id 19768): caption — reordered displaced `Respondents` / `Respondent and
  Appellant` labels to the PDF two-column layout (pure reorder, word-multiset preserved).
- **2024 ND 207** (id 19960): caption — restored dropped `Petitioner` and `Respondent`
  party designations (PDF-confirmed).
- **2025 ND 49** (id 20257): caption MOVE — `Petitioner`/`Respondent` were orphaned after
  `Per Curiam.`; relocated into the caption parties. (Agent proposed deleting them, which
  would have lost the designations.)

Rejected / deferred:
- **2024 ND 122** (id 19866) **rejected**: the agent proposed deleting `In November 2023,
  the district court amended child support and entered judgment.` — but this is legitimate
  ¶8 factual text, appearing once in both DB and PDF (the empty `new_exact` passed the
  verifier only because an empty string trivially matches). Deleting would corrupt ¶8.
- **2022 ND 183** (id 18082) `V.`->`v.` deferred — flagged landmine (PDF has ` V.` twice;
  possible middle initials, needs image verification).
- **2023 ND 179** (id 19765) deferred to the scramble bucket (dangling `confidential
  attorney-client` fragment; not a clean delete).

## Batches `headings-2022ND132-2026-06-24` + `headings-2026-06-24` — section-heading reformat queue (3 opinions, 11 headings)

Draining the recurring heading-reformat queue. Section/subsection headings (I, II, A,
B, C, ...) were merged onto the end of the preceding line during ingestion; the proofing
agents proposed DELETING the stray letters, which would lose the court's section
structure. Correct action is MOVE to the heading's own line (verified against each
opinion's PDF). All edits conserve text (letters relocated, not removed).

- **2022 ND 132** (id 19647, State v. Dearinger): A/B/C. 'A' had been scrambled into the
  middle of ¶10 (after 'preliminary hearings:'); moved before ¶10. B before ¶15, C
  before ¶17 (the agent's proposal missed C — found via full structural reconciliation).
- **2022 ND 157** (id 19669, State v. Pulkrabek): A before ¶11, B before ¶13.
- **2023 ND 150** (id 18222, Black Elk v. State): I/II/III/IV/V. 'II' had been OCR'd as
  'H' and merged onto the prior sentence (restored to 'II' on its own line before ¶5);
  I before ¶2, III before ¶6, IV before ¶15, V before ¶20.

Note on method: the original agent proposals named the wrong PDF stems for two of these
(neutral cite != filing-year sequence); cites were re-derived from `source_path` before
verifying. Deferred (ambiguous, need individual treatment): **2022 ND 85** (id 19709,
"A An" — heading vs. spurious dup) and **2025 ND 61** (id 20271, two parallel A/B/C
subsection sequences under II and III).

## Batch `corpus-proofing-p26-2026-06-24` — proofing fleet P26 (40 opinions, 2022 ND 90→48)

Low-noise cycle (31/40 clean). Verifier: 6 auto / 7 review / 4 reject. Only 2 items
applied after the consolidated triage; pytest + detector clean.

- **2022 ND 58** (id 17991, heading_seq): consolidated-caption docket header
  ` No. 20220027-20220030` -> `Nos. 20220027-20220030`. PDF (`2022ND58.pdf` line 77)
  shows `Nos.` for the combined caption (each individual case is `No.`).
- **2022 ND 43** (id 19701, caption): reflowed the blank-line-mangled caption to the
  PDF two-column reading, word-multiset-preserving: `Howard Malloy and Great Plains
  Potato Production, LLP, Plaintiffs and Appellees / v. / James Behrens, Defendant and
  Appellant`.

Not applied:
- **4 signature-indent items** (id 17981, auto:whitespace_only) **rejected** — they would
  re-indent the justice signature lines to 5 spaces to match the PDF's centered layout,
  but the corpus convention is 1 leading space (604 vs 8 in a 2022 sample). Applying
  would make the opinion an outlier; the DB deliberately normalizes presentational
  indentation. (Triage lesson: `auto:whitespace_only` can still diverge from a
  corpus-wide whitespace convention the verifier can't see.)
- **11 citation/`Id.` reflow split_joins** (ids 17977, 17981, 17987, 18000, 18009, 18011,
  19705) deferred to the citation-rejoin v2 worklist (`triage/p26-deferred-citemangle.json`)
  per rule 10 — fragmented citations are owned by the systematic rejoin pass, not applied
  ad hoc. These are the `\d\n (paren` / `,\n\n` residual rejoin v1 doesn't yet catch.

## Batch `scramble-2025ND92-2026-06-24` — 2025 ND 92 column-scramble repair (1 opinion, 3 edits)

Manual-review item from `p567-flagged-manual.json`. The agent's original proposal
("strip the stray phrase `interpretation, pure questions of`") was a delete-should-be-MOVE
error: broader context showed ¶26–¶27 are pdfminer column-scrambles (the
`modern_scramble` class), and that 4-word fragment is displaced *Kadlec*-quotation text
belonging in ¶27, not garbage. Repaired against `2025ND92.pdf` (pdftotext -layout),
all court text conserved:

- **¶26 internal reorder** (block quote from *Garaas*): `preserves agency judicial
  efficiency. The exhaustion authority and promotes requirement recognizes` ->
  `preserves agency authority and promotes judicial efficiency. The exhaustion
  requirement recognizes`.
- **¶26 -> ¶27 fragment move**: removed `interpretation, pure questions of` from the end
  of ¶26 (after `Garaas, ¶ 10 (cleaned up).`) and reinserted it into the *Kadlec*
  quotation in ¶27 (`statutory interpretation, pure questions of law`).
- **¶27 internal reorder**: `"depends on a mixed limited to, expertise of 'including,
  but not bundle of considerations, administrative bodies, statutory law` -> `"depends
  on a mixed bundle of considerations, 'including, but not limited to, expertise of
  administrative bodies, statutory interpretation, pure questions of law`.

Companion manual-review items checked the same cycle, no action needed: **2025 ND 202**
(id 20191) and **2025 ND 116** (id 20095) were already correct in the DB (proposals
stale — fixed by the rejoin pass / a prior batch); **2025 ND 134** (id 20115, 4 malformed
`<sup>&</sup>lt;sup>N</sup>` entities) deferred to the footnote/markup cohort — it carries
8 `<sup>` HTML tags plus a mid-sentence footnote-text splice in ¶38, so an isolated
entity fix would be a half-measure.

## Batch `proofing-review-approved-2026-06-24` / `corpus-proofing-2026-06-24` — proofing fleet P20-P22 (30 opinions)

Batches P20-P22 (120 opinions, 2023 ND 86 -> 2022 ND 211), first cycle on the
quote-normalized text with prompt rule 9 (agents correctly ignored straight-vs-curly
differences). Applied 51 items across 30 opinions after the hardened triage; pytest
clean (no regression).

- **3 spelling fixes, each PDF-text-layer-verified SAFE** (per the sumbitted lesson):
  martial->marital (2023 ND 86), administrate->administrative (2023 ND 77),
  serous->serious (2023 ND 40) — text-layer shows the corrected form, not the typo.
- OCR/case-name fixes verified against PDF: GMD->GMR Transp. (2022 ND 205, party
  name; PDF shows GMR), Judge->Judicial Referee (2023 ND 79; PDF confirms), doubled
  "for for" (2023 ND 41), "compensable injury" restore (2023 ND 17), carry over->
  carryover (2023 ND 86).
- 2023 ND 39 section III move: add before [¶22] + remove the misplaced copy after the
  signature block (agent's remove-half had a stale \n\n anchor; rebuilt to the actual
  \n single-newline). III now appears once, in position.
- 41 clean reorder/respace items.

Deferred (250, NOT applied): **239 markdown citation-linebreak mangle** (this era is
almost entirely this class), 8 LaTeX, 3 digit. Plus 2 markdown-mangle deletions
(2023 ND 78, 2023 ND 16) held to the citation cohort. Detector 175/0; invariants
24 ok / 2 known / 0 regressed; 66 tests pass.

## Batch `proofing-review-approved-2026-06-24` / `corpus-proofing-2026-06-24` — proofing fleet P23-P25 (21 opinions)

Batches P23-P25 (120 opinions, 2022 ND 209 -> 83), first cycle after the citation-
rejoin pass + prompt rules 10-12. NOISE DROPPED SHARPLY: REVIEW 44 (was 281 last
cycle); clean rate 25-31/40 per batch. Applied 27 items across 21 opinions (clean
reorder/move/punct + 2 PDF-verified scrambles: 2022 ND 202 "placed into question
the professional competence", 2022 ND 150 "argues it has identified"). pytest clean.

DEFERRED (conservative, integrity-first):
- Heading-letter deletes (2022 ND 157 A/B, 132 A/B, 85 "A An") -> manual reformat
  queue; NOT deleted (avoids the delete-should-be-move error class; PDF-standalone
  inconclusive).
- 2022 ND 183 " V."->" v." held: PDF has " V." 2x (possible middle initials, not
  just citation connectors) — letter-case change needs image confirmation.
- 2022 ND 145 complementary quoted-passage move (probe not PDF-confirmed).
- 15 residual cite-mangle (patterns the rejoin pass did not target, e.g. "303\n ("),
  1 ellipsis-WIDEN (". . . ." -> ".   .   ." = pdftotext column padding, NOT real;
  correctly rejected), 1 digit.

Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

## Batch `citation-rejoin-2026-06-24` — rejoin fragmented citations (1,629 opinions)

Markdown/reporter-sourced opinions ingested citations split across lines with stray
newlines and isolated commas (e.g. "Vondell,\n2017 ND 158, ¶ 4\n,\n897\nN.W.2d 334").
`scripts/rejoin_citations.py` applied four conservative, citation-internal transforms:
lone-comma line (\n,\n -> ", "), number->reporter split (967\nN.W.2d -> 967 N.W.2d),
case-name->neutral-cite (Name,\nYYYY ND -> Name, YYYY ND), and digit->close-punct
(737\n. -> 737.).

PROVABLY content-preserving: across all 1,629 candidates the alphabetic-word multiset
AND the digit multiset are UNCHANGED (only whitespace / a comma's position moves) — no
letter or number altered anywhere. Validated 148/149 against the proofing agents' own
PDF-verified cite-mangle proposals (the 1 outlier was a caption, not a cite). 1,261 were
additionally PDF-cite-verified; 350 are 1997-98 opinions whose SCANNED PDF text layers
are themselves OCR-garbage ("ller y. Bragg ... ~2. 559 N.W.2d") and can't confirm a
correct rejoin — applied anyway on the content-preserving guarantee; 18 had no PDF.
Hard gate = alpha+digit multiset identical (0 skipped). FTS auto-synced.
Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

This resolves the dominant deferred class of the reporter/markdown era. The proofing
prompt gained rule 10 (ignore fragmented citations — this pass owns them), rule 11
(ignore markup contamination), and rule 12 (spelling is high-risk: image-verified).

## Batch `quotes-straight-2026-06-24` — normalize curly quotes to straight ASCII (13,492 opinions)

User policy decision: the authoritative edition uses straight ASCII quotes and
apostrophes. `scripts/normalize_quotes_straight.py` mapped the four curly quote
characters corpus-wide — “ U+201C / ” U+201D -> ", and ‘ U+2018 / ’ U+2019 -> ' —
across 13,492 opinions (~692,662 chars: “168,735 ”164,563 ‘44,906 ’314,458).
Per-opinion gate confirmed the ONLY change was those four chars. 0 skipped; 0 curly
quotes remain. FTS auto-synced via the opinions_au trigger.

This is intentionally LOSSY (open/close direction discarded). The user was advised
of the trade-offs (irreversible directional loss; divergence from the curly-quoted
published PDFs; that the modern straight-quote cohort was itself an ingestion
flattening) and chose straight for uniformity/portability/searchability, noting no
semantic difference. Directional data remains recoverable from the court PDFs;
changelog rows record per-opinion substitution counts. OUT OF SCOPE / left as-is:
primes ′″ (14/20 opinions), grave ` (393), guillemets «» (15/22) — not curly
quotes; separate review if desired. Detector 175/0; invariants 24 ok / 2 known /
0 regressed; 66 tests pass.

## Batch `proofing-review-revert-2026-06-24` — preserve-source-typo revert (2023 ND 177)

REVERTED an applied "OCR typo" fix that was actually correcting the COURT'S OWN
published typo. P17 applied 2023 ND 177 (id19763) "sumbitted"->"submitted" on the
counsel line "for plaintiff and appellee; sumbitted on brief." A 300-DPI render
(mutool draw) of the published PDF confirms the court's text genuinely reads
"sumbitted" (the NEXT counsel line correctly reads "submitted"). The proofing
agent falsely claimed the visual render showed "submitted"; the triage's "corrected
word appears in the PDF" check passed only because "submitted" occurs on the other
line. Restored to "sumbitted" per the preserve-source-typos rule.

LESSON: letter-level ocr_char "spelling fixes" are NOT safe on a text-layer / word-
appears-elsewhere check — they can silently correct the court's own typos. Such
fixes require glyph-level PDF confirmation (render the region) at the SPECIFIC
location, or should be FLAGGED not fixed. Other session ocr_char spelling fixes
(e.g. Willison->Williston, M.V V.->M.W.) need the same re-audit.

## Batch `proofing-review-approved-2026-06-24` / `corpus-proofing-2026-06-24` — proofing fleet P17-P19 (31 opinions)

Batches P17-P19 (120 opinions, 2023 ND 207 -> 92), first run on post-cleanup text
(YAML/clerk-stamps/form-feed/FILED-OFFICE already stripped; clean rate up early in
the range). Applied 8 clean AUTO (NNBSP->space, trailing/leading space) + 40 review
items after hardened triage; pytest clean (no regression).

- Stray-letter/OCR-garbage removals (2023 ND 206 "papers B", 2023 ND 97 "affirm. T"
  / "served. TTT"), OCR typos (sumbitted->submitted, " V."->" v."), missing words
  (entry of [judgment] for), capitalization-per-PDF (Section->section), a
  displaced-fragment move (2023 ND 188 "requests for"), 2 heading reformats
  (2023 ND 181 A/B, corrected from agent deletes).

Deferred (171 proposals, NOT applied) - this era is dominated by the markdown-
sourced records:
- **markdown citation-linebreak mangling (149 proposals / 24 opinions)** - citations
  fragmented across lines with stray newlines/commas (e.g. "2017 ND 158, ¶ 4\n,\n897
  N.W.2d 334"). A distinct systematic class warranting a dedicated citation-rejoin
  pass (overlapping anchors make piecemeal apply fragile). IDs: 18192-18221 range +
  19768.
- 17 LaTeX-markup cohort, 5 digit-change (high-risk, per-item).

Also flagged (not acted): a corpus-wide straight-vs-curly apostrophe encoding
question (DB U+0027 vs PDF U+2019) — pervasive, stylistic; needs a policy decision.

Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

## Batch `yaml-frontmatter-2026-06-24` — strip embedded YAML frontmatter (17,593 opinions)

The largest text_content cleanup in the corpus (user-approved). Markdown/reporter-
sourced opinions were ingested with their `---\ntitle: ...\n---` frontmatter block
embedded at the start of text_content — pure metadata (title, title_full, court,
date_filed, citations, judges, cluster_id), all duplicated in the structured
columns/tables, and indexed by FTS / returned by get_opinion_text / shipped in the
released DB. `scripts/strip_yaml_frontmatter.py` removed ONLY the single leading
frontmatter block (opening `---` through the first closing `---` fence + trailing
blank line); any `---` inside the body untouched. Gated per opinion: must start
with `---\n`, the block must contain a `title:` key, closing fence must exist, and
the remaining body must be >= 40 chars (never blank an opinion). 17,593 OK / 0
skipped. FTS index auto-synced via the opinions_au trigger (verified: the
YAML-only term "cluster_id" now returns 0 FTS hits). Detector 175/0; invariants
24 ok / 2 known / 0 regressed; 66 tests pass.

## Batch `filed-office-2026-06-24` — strip FILED-IN-OFFICE page-headers (301 headers)

Removed `FILED IN THE OFFICE OF THE CLERK OF SUPREME COURT <date> STATE OF NORTH
DAKOTA` clerk filing page-headers fused into text_content — a clerk-stamp variant
the earlier pass missed (often leads text_content; leading-docket / trailing-
running-header fusions). `scripts/strip_filed_office.py`, same gate model as
strip_clerk_stamps (stamp-vocab word-multiset + PDF fallback for mid-word fusion).
301 headers removed (177 strict + 124 PDF-verified fusion), 0 skipped; 181
lowercase "filed in the office of the clerk" matches were legitimate prose and
correctly left. Numeric + month-name dates, optional "THE", OCR stray-char
tolerated. 0 all-caps headers remain. Detector 175/0; 66 tests pass.

## Batch `proofing-review-approved-2026-06-24` / `corpus-proofing-2026-06-24` — proofing fleet P14-P16 (53 opinions)

Batches P14-P16 (119 opinions, 2024 ND 77 -> 2023 ND 208; crosses into the
reporter/markdown-sourced era). Applied 199 items across 53 opinions (50 AUTO
citation-newline + signature joins, 126 clean reorder/respace, 19 verified
judgment, 4 corrected). Triage HARDENED post-P13: items touching LaTeX (`$`/`\ `),
the FILED-IN-OFFICE header, footnote-calls `[N]`, or digit runs are pulled to
deferred/manual regardless of alpha-word-delta. pytest run after apply (66 pass).

- Word-order scrambles, Greek/Cyrillic heading-letter OCR (`Ι`->`I`, `П`->`II`,
  `В`->`B`), OCR fixes (2024 ND 9 caption de-garble; 2023 ND 249 Willison/
  acknowledged), missing-text restorations.
- 5 heading reformats (corrected from agent deletes), incl. TWO concurrence/dissent
  section headers (2024 ND 73 "Bahr, J., concurring specially." / "Tufte, J.,
  concurring in part and dissenting in part.") moved to their own line, and a
  PDF-confirmed section IV inserted before 2024 ND 66 ¶14.

3 opinions skipped (18237/18240/18232): overlapping citation-newline edits in
markdown-sourced records -> defer to the citation/markdown systematic cleanup.

### THREE systematic text_content findings surfaced (NOT yet acted on)
- **YAML frontmatter in 17,593 opinions** — markdown/reporter-sourced records carry
  their `---\ntitle: ...\n---` header inside text_content (modern PDF-sourced ones
  do not). Largest text_content contamination in the corpus; affects FTS/display/
  redistribution. Architectural decision for the user.
- **`FILED IN THE OFFICE OF THE CLERK OF SUPREME COURT <date> STATE OF NORTH DAKOTA`
  page-headers in 482 opinions** — a clerk-stamp variant the earlier remover did not
  match (often leads text_content or is fused mid-body). Dedicated pass warranted.
- **LaTeX-encoded citations / `\ ` escapes in ~34 opinions** (e.g. `$Swanson\ v.\
  Swanson\ , 2019\ ND\ 25, \ 9, ...$`; the `$\P$`/`$\mathsf{}$` family). The `¶`
  is lost in the encoding. Needs a careful deterministic decoder, not ad-hoc agent
  edits (one agent wrongly proposed ADDING spaces around `$\P$`).

Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

## Batch `proofing-review-approved-2026-06-24` / `corpus-proofing-2026-06-24` — proofing fleet P11-P13 (49 opinions)

Batches P11-P13 (120 opinions, 2024 ND 198 -> 78). Gate: 11 AUTO / 79 REVIEW /
87 REJECT (the bad `$\P$`-spacing proposals correctly rejected). Applied 6 AUTO +
78 review items after word-delta + PDF triage:

- 16 word-order scrambles (incl. complex page-break descrambles: 2024 ND 194
  "make it impossible for this Court to issue relief"; 2024 ND 81 summary-judgment
  descramble; 2024 ND 154 disposition reassembly).
- **6 citation fidelity fixes (2024 ND 97)** — removed `, 5 N.W.3d 489` that
  ingestion wrongly appended to short-form Hillestad cites; VERIFIED the PDF
  contains that reporter zero times (the court used short form).
- 11 OCR-char (Greek/Cyrillic/LaTeX heading letters), 6 heading reformats
  (incl. corrected A/B from agent deletes), 17 paragraph_seq, 8 missing-text,
  8 whitespace, 4 captions.
- 3 agent-error corrections (2024 ND 158 sentence move — agent's remove-half had a
  bad anchor and would have duplicated; 2024 ND 175 / 2024 ND 130 heading reformats).

**Regression caught + reverted** (`proofing-review-revert-2026-06-24`): an edit
"9.9[1] years" -> "9.91 years" in 2024 ND 147 (id19893) merged a FOOTNOTE-CALL
marker `[1]` into the number (corrupting both the figure and the call). It slipped
the consolidated triage because the alpha-word-delta gate does not guard digits or
bracketed footnote-calls. Caught by test_footnote_pinpoints, reverted; a corpus
scan of all session batches found this was the ONLY such occurrence.
TRIAGE LESSON: treat `[N]` (non-`[¶N]`) bracket changes and digit changes as
high-risk regardless of alpha-word-delta.

Deferred: 2024 ND 171 (Greek-Alpha heading, ambiguous), 2024 ND 84 (`weigh[ ]`
anchor unconfirmed). Detector 175/0; invariants 24 ok / 2 known / 0 regressed;
66 tests pass.

## Batch `clerk-stamps-2026-06-24` — court-clerk filing-stamp removal (1,864 opinions)

Removed court-clerk filing metadata fused into text_content (administrative stamps,
not the court's authored opinion) — user-approved after dry-run review. Two forms:
standalone (`Filed M/D/YY by Clerk of Supreme Court`, usually paragraph-padded) and
a per-page WATERMARK (`Corrected Opinion Filed MM/DD/YY by Clerk of the Supreme
Court`) injected mid-word at every page break. `scripts/strip_clerk_stamps.py`.

Date forms covered: numeric (M/D/YY, MM/DD/YYYY) and month-name (`April 5, 2024`),
before and/or after "by Clerk", plus one OCR typo ("Courst"). Per-opinion gate: the
alpha-word multiset removed must be ONLY stamp vocabulary; mid-word-fusion cases
(stamp glued to a real word, e.g. "Supreme Courtnoticed" -> "noticed") that fail the
strict gate are accepted only when the PDF confirms every rejoined token is real.

Result: ~1,955 stamps removed across 1,864 opinions (1,810 strict-gate + 51
PDF-verified fusion + 2 typo/comma variants + 1 hand-fixed). 2024 ND 218 (id19716)
had a genuine caption/body merge ("DAKOTA"+"O'Neal") — hand-fixed with a paragraph
break (not auto-stripped). Remaining match (id3419) is legitimate text (the LIKE
spanned unrelated "Clerk of ..." and "Supreme Court" mentions), left as-is.
Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

## Batch `proofing-review-approved-2026-06-24` — proofing fleet P8-P10 + gap (46 opinions)

Batches P8-P10 (123 opinions, 2025 ND 81 -> 2024 ND 199) + re-run of 3 P5-dropped
opinions (2025 ND 166/187/201 — recovered, 1 fix). Combined gate: 0 AUTO / 83
REVIEW / 40 REJECT. 76 review items applied after word-delta + PDF triage:

- **33 word-order scrambles** (e.g. 2025 ND 28 "Conducting a comprehensive
  assessment of the circumstances"; 2025 ND 37 Keller block-quote restoration;
  2025 ND 41 financial-info scramble).
- **9 OCR character fixes** — section-heading letters mis-encoded in the wrong
  Unicode block: Greek Iota `Ι`->`I`, Cyrillic `П`->`II`, Greek `Α`->`A`, LaTeX
  `$\mathsf{C}$`->`C`.
- **10 heading reformats** — merged A/B/C/D subheadings moved to their own line
  (corrected from the agent's proposed delete; PDF-confirmed as headings).
- 11 paragraph_seq (incl. complementary signature/section moves), 4 caption
  reorders, 4 missing-text restorations, misc.

**Deferred** (`triage/p8910-deferred.json`): 3 caption word-changes (2025 ND 49,
2024 ND 207) + 1 check (2025 ND 61) for closer review; 3 clerk filing-stamp items
folded into the corpus-wide clerk-stamp pass (see below).

Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

### Open finding — clerk filing-stamps (~1,772 opinions, remover being built)

`Filed MM/DD/YY by Clerk of Supreme Court` and `Corrected Opinion Filed ... by
Clerk of the Supreme Court` administrative stamps are fused into text_content
across ~1,772 opinions — court-clerk metadata, not the authored opinion. User
approved building a deterministic remover (dry-run for sign-off, like form-feed).

## Batches `corpus-proofing-2026-06-24` / `proofing-review-approved-2026-06-24` — proofing fleet P5-P7 (51 opinions)

Batches P5-P7 (117 opinions, 2025 ND 203 -> 82), run in parallel on the v2 prompt
(0 form-feed proposals; agents now correctly cite ND's compact ellipsis style).
Combined gate: 3 AUTO / 73 REVIEW / 44 REJECT.

- **AUTO (3):** paragraph spacing, narrow-no-break-space -> space, trailing space.
- **REVIEW (68 applied, user-approved after word-delta + PDF triage):** 25 word-order
  scrambles (e.g. 2025 ND 199 "erred in concluding Chapter 12.1-19.1 is
  unconstitutionally vague"; 2025 ND 171/168/164), 13 paragraph_seq, 7 caption
  reorderings, 13 whitespace (compact ellipses + spacing), 5 missing-text, 5
  ocr_char (incl. 2025 ND 134 `$\P$` LaTeX -> `¶`).
- **3 agent-error corrections (delete -> move):** 2025 ND 137 (section IV moved
  before ¶36), 2025 ND 116 (¶2 marker moved + orphan joined, no dup), 2025 ND 202
  (¶1 orphan absorbed + removed, no dup). Verified vs PDF.
- **5 deferred to manual** (`triage/p567-flagged-manual.json`): 2025 ND 134 four
  garbled `<sup>` footnote-call tags (footnote/markup pipeline, not this lane);
  2025 ND 92 "interpretation, pure questions of" mid-sentence displacement
  (complex reconstruction).

Triage method (reusable): the verify gate's "NEW in PDF" is necessary but not
sufficient; per item also check the word-multiset delta — pure reorder/respace
(delta 0) + PDF-confirmed = safe batch; word-count change = verify individually;
an agent "delete" of displaced structure usually needs a MOVE instead.

Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

## Batch `corpus-proofing-2026-06-24` / `proofing-review-approved-2026-06-24` — proofing fleet P4 (18 opinions)

Fourth proofing batch (40 opinions, 2026 ND 6 -> 2025 ND 204; first to cross into
2025). v2 prompt clean (0 form-feed proposals). Gate: 2 AUTO / 26 REVIEW / 8 REJECT.

- **AUTO (2):** case-number joins (`51-2025-JV- 00037` -> `51-2025-JV-00037`).
- **REVIEW (26, user-approved after PDF verification):** 11 word-order scrambles
  (e.g. 2026 ND 1 restored a garbled district-court oral ruling; 2025 ND 216 had
  several), 6 paragraph_seq (heading moves + signature reflows), 3 caption
  reorderings (2025 ND 234/231/204), 2 missing-text restorations (2025 ND 216
  "the"/"It"), 2 compact-ellipsis fixes, 1 stray-word delete.
- **Agent-error caught + corrected:** 2025 ND 208 section heading `II` was
  misplaced inside a quoted statute; the agent proposed deleting it (would drop
  section II from the I-V sequence). Corrected to MOVE it before `[¶4]` per the PDF.

Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

## Batch `proofing-review-approved-2026-06-24` — P2/P3 review queue cleared (18 opinions)

User-reviewed and approved the meaning-affecting P2/P3 proposals (all byte-exact,
all confirmed verbatim against the court PDF):

- **9 word-order scrambles** (split_join) the deterministic reconcile missed —
  e.g. 2026 ND 69 "If necessary to protect the welfare of the child…", 2026 ND 66
  "Richard immediately received $50,500.00", 2026 ND 19 "engaged in \"deliberate
  illegal treatment\"". Two are complementary fragment-moves (2026 ND 19, ND 69).
- **5 section-heading position fixes** (paragraph_seq) — `III`/`IV` moved before
  their ¶ marker (2026 ND 44, 30) and signature-block reflows.
- **5 caption reorderings** — smushed `Party, v. Designation` restored to the
  PDF's `Party, Designation v. Party, Designation` (2026 ND 22/48/54/55/58).
- **5 ellipsis respacings** — `. . . . .` → `....`; ND's PDFs use the compact
  four-dot form, so the DB's spaced version was the ingestion artifact.

With the agent-error corrections batch, the entire 31-item P2/P3 REVIEW queue is
resolved. Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

## Batch `proofing-review-corrected-2026-06-24` — P2/P3 review: agent-error corrections (5 opinions)

Hand-verified corrections from the P2/P3 REVIEW queues where the agent's proposal
was wrong; each rebuilt and confirmed against the court PDF (user-approved):

- **Section-heading letters (4)** — 2026 ND 35 (`A` before ¶7, `B` before ¶12),
  2026 ND 61 (`B` before ¶10), 2026 ND 70 (`B` before ¶13). Ingestion merged the
  one-letter section heading onto the end of the prior citation line
  (`…850. A

[¶7]`). The agent proposed DELETING the letter (would lose the
  heading); corrected to REFORMAT it onto its own line (`…850.

A

[¶7]`),
  matching the PDF.
- **2026 ND 34 (move, not delete)** — `the due process and constitutional` was
  scrambled out of ¶11 to the end of ¶10. Agent proposed deleting it (text loss);
  corrected to MOVE it back into ¶11 (`This Court has discussed the due process
  and constitutional considerations`), per the PDF.
- **2026 ND 75 (statute join)** — `§ 12-44.1-32` was line-wrapped to `12-44.1- 32`
  (stray space). Agent matched the PDF line-break; corrected to JOIN to
  `12-44.1-32` (one section number).

Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

## Batch `corpus-proofing-2026-06-24` — proofing fleet P3 AUTO (1 opinion)

Third proofing batch (40 modern opinions, 2026 ND 7-45), first run on the v2
prompt. The v2 changes landed: 0 form-feed proposals (rule 8 worked), clean rate
21/40 (vs P2 8/40), 24 proposals total. Gate: 1 AUTO / 14 REVIEW / 9 REJECT.

Applied (AUTO): 2026 ND 42 (id 20349) `732 N.W.2d 389.[¶4]` -> `389. [¶4]`
(missing space at a paragraph transition; matches the opinion's own norm). The
tightened gate correctly routed the two ellipsis-respacing proposals
(`; . . . .` -> `; ....`) to REVIEW instead of AUTO.

REVIEW queue (14 items / 10 opinions): `triage/proofing-p3-REVIEW.md` — split_join
scrambles, paragraph_seq (heading III vs [¶10] order), the 2 ellipses, caption.
Awaiting user sign-off; NOT applied. Detector 175/0; invariants 24 ok / 2 known /
0 regressed; 66 tests pass.

## Batch `formfeed-furniture-2026-06-24` — page-furniture removal (120 opinions)

Resolved the open form-feed finding from the P2 proofing batch (user-approved
2026-06-24). `pdftotext` emits a 0x0C at every page break; ingestion preserved
it across 120 opinions (1998–2026, incl. the current pipeline).
`scripts/strip_formfeed_furniture.py` removed, per opinion and behind gates:

- **118 running-header blocks** — `\x0c<short case name>\n<docket>\n\n` (e.g.
  `Brooks v. State / No. 20250426`, `Zarrett v. Zarrett / Civil No. 970178`),
  appellate page furniture duplicating the page-1 caption. A header is removed
  ONLY when its docket number is independently confirmed earlier in the text
  (the caption), proving it redundant; both the older blank-line and the 2026
  single-newline header layouts are handled. The leading `\n\n` paragraph break
  is kept, so the attorney block flows into the author line.
- **1,105 bare 0x0C bytes** — lone page-break control chars at paragraph/line
  boundaries; the byte is non-text and is dropped, surrounding whitespace kept.

Gate: per-opinion alphabetic word-multiset must equal the original MINUS exactly
the removed-header words — 120/120 passed, 0 skipped, 0 unverified-docket flags.
Result: 0 opinions contain 0x0C. Detector 175/0; invariants 24 ok / 2 known /
0 regressed; 66 tests pass. (The corpus-proofing v2 prompt now tells agents to
ignore form-feed furniture so this artifact is not re-surfaced.)

## Batch `corpus-proofing-2026-06-24` — proofing fleet P2 AUTO (12 opinions)

Second proofing batch (40 modern opinions, 2026 ND 46–85). Agents proposed
transcription-fidelity fixes verified against the court PDFs; the deterministic
gate (`verify_proofing_proposals.py`) routed 26 → AUTO, 14 → REVIEW, 37 → REJECT.

**Applied (AUTO, 23 proposals / 12 opinions):** whitespace-only, PDF-confirmed,
ws-equivalent — letter-spaced headers (`I N   T H E   S U P R E M E   C O U R T`
→ `IN THE SUPREME COURT`), double-space collapses in "Appeal from the District
Court …" / attorney lines, trailing-space-before-newline, and a signature-block
reflow (justices onto separate lines).

**Gate tightening:** 3 proposals the loose `_ws_equiv` test admitted to AUTO were
hand-pulled to REVIEW because whitespace is semantic there — a statute number
reflowed across a line (`12-44.1- 32` → `12-44.1-\n   32`, matches PDF *layout*
not cleaner text) and two quoted-transcript ellipses respaced (`. . . . .` →
`....`). Logged for the v2 prompt/gate refinement.

**REVIEW queue (17 items / 13 opinions):** `triage/proofing-p2-REVIEW.md` —
PDF-confirmed but meaning-affecting (split_join scrambles, caption, paragraph_seq,
the 3 held-back ws items). Awaiting user sign-off; NOT applied.

**REJECT (37):** 15 are the form-feed running-header cases (agents anchored on the
literal `^L`; DB holds a real 0x0C byte) — see the form-feed furniture note below;
the rest were bad-anchor / db-already-matches-pdf / unverified.

Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

### Open finding — form-feed page-furniture (120 opinions, NOT yet treated)

`pdftotext` emits a 0x0C form-feed at every page break; ingestion preserved it.
120 opinions carry one (98 carry several), across 1998–2026 (incl. the current
2026 pipeline). Most are followed by a running header (`<short case name>` +
`Civil No. <docket>`) that duplicates the page-1 caption — appellate page
furniture, not published text; a few are bare mid-sentence breaks. Treatment
(byte-only strip vs. full furniture removal vs. leave) is a corpus-wide structural
decision deferred to the user; tracked here, not auto-applied.

## Batch `footnote-editpair-apply-2026-06-23` — West-doc residue re-pass 3 (17 opinions)

A third pass over the 20 remaining `westlaw_doc` `SRC_MORE` opinions (1978–1988),
whose footnotes are PRESENT in the DB but parser-undetected (bare-line orphan
bodies + unbracketed call digits). Agents proposed byte-exact bracket/number
edit-pairs against the authoritative `.doc` footnote sets; `heal_footnote_anchors.py`
fixed 19 curly-quote/nbsp misses. **17 opinions repaired.**

The applier is atomic per opinion, and these tail cases hit a sequential-edit
**overlapping-anchor** hazard: when one footnote's body sits at the next footnote's
call site, applying the first edit invalidates the second's byte anchor (count→0).
Rather than lose an opinion's good edits over one bad anchor, a num-grouped prune
dropped only the conflicting footnote (and its paired call/body object) per opinion,
keeping the rest — a pruned footnote simply stays unmarked (present, not lost).

**Result:** `SRC_MORE` 28 → 19 (westlaw_doc 20 → 11); MATCH 508 → 517. Detector
175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass. (Rows share the
batch name with the archive batch-4 apply — same applier, hardcoded `BATCH`.)

**11 westlaw_doc remain** (`triage/westdoc-footnote-residue-manual.json`, 39
undetected footnotes total) — documented tail, NOT loss:
- 1985 ND 40 (0/12) + 1979 ND 119 (0/7): workflow connection-dropped both passes;
  a 2-opinion retry returned actions with no edit-pairs / one drop → nothing
  applyable.
- 1979 ND 141 (1/9): agent misread; anchors systematically count=0.
- 1979 ND 30 (9/12), 1986 ND 104 (19/21), 1978 ND 27 (3/5), and the rest: 1–3
  footnotes each blocked by the overlapping-anchor hazard; partially repaired.
Further gains need hand-built non-overlapping anchors; deferred as polish.

## Batch `footnote-editpair-apply-2026-06-23` — archive worklist COMPLETE (batch 4)

Closed the archive-backed `SRC_MORE` worklist. Batch 4 ran the final 43 archive
opinions through propose → heal → gated-apply: **38 repaired** (31 direct + 5
healed/marker-fixed + a 2-opinion tail whose call markers were lost, where the
present orphan bodies were numbered so the parser indexes them, `call_para` left
None — no fabricated calls). The `scripts/heal_footnote_anchors.py` single-glyph
splice cleared every curly-quote/nbsp anchor miss (0 unhealed).

Two agent over-reaches the gates/▸review caught and I corrected by hand:
- **2011 ND 166** — agent bundled an OCR fix `N.D.R.Civ.PASCa)` → `P.43(a)` into a
  call edit; marker_only gate blocked it. Re-did as bracket-only, leaving the
  scan garble verbatim (preserve-source-typos).
- **2017 ND 117** — agent's `recover_body_absent` proposed appending a body not
  confirmable against the source; deferred rather than append unverified text.

**Final archive tally:** 8 opinions remain `SRC_MORE`, all accounted for in
`triage/footnote-deferred-manual.md` — 7 deferred for manual review (genuinely
ambiguous multi-footnote / lost-call / OCR-garbled structure; footnotes present,
not lost) + 1 engine false positive (2016 ND 142, header misread as a footnote).
Detector 175/0; invariants 24 ok / 2 known / 0 regressed; 66 tests pass.

## Batch `modern-pdf-reconcile-2026-06-23` — deterministic scramble repair from PDF

After fixing the scraper's extractor (pdfminer -> poppler pdftotext), modern
opinion text is reconciled against the now-correct PDF WITHOUT a wholesale
re-derivation that would revert corrections. scripts/reconcile_modern_pdf.py
aligns DB<->PDF by the court's [¶N] markers and replaces a paragraph ONLY when
the DB text is a PURE REORDER of the PDF (identical word multiset, different
sequence) -- provably safe (no words added/dropped, just restored to the
authoritative order), and safe over corrected paragraphs (the corrected words
survive in the multiset). Footnote-marker and content-change paragraphs are
flagged, never auto-replaced.

2026 pilot: 116 opinions, 20 with scrambles -> 22 paragraph fixes applied. E.g.
2026 ND 60 ¶3 "affirm the divorce 35.1(a)(2), (4), and (7). judgment under
N.D.R.App.P." -> "affirm the divorce judgment under N.D.R.App.P. 35.1(a)(2),
(4), and (7)."; 2026 ND 112 ¶9 restored. Reversible by batch.

## Batch `corpus-proofing-2026-06-23` — proofing fleet P1 (calibration, 2026)

First corpus-proofing batch: 30 most-recent opinions, each agent diffing the DB
against the authoritative court PDF. Layer-C gate (verify_proofing_proposals.py)
PDF-confirms each proposal (byte-exact DB anchor + reconstruction verbatim in PDF).
 - **AUTO 11 applied** (6 opinions): whitespace-only / layout fixes — letter-spaced
   "I N   T H E   S U P R E M E   C O U R T" -> "IN THE SUPREME COURT", double-space
   and blank-line collapses, signature-block reflow to match the PDF. Reversible.
 - **REVIEW 21** (PDF-confirmed, awaiting sign-off): see triage/proofing-p1-REVIEW-QUEUE.md.
 - REJECT 13: 10 bad-anchor (mostly redundant overlapping descriptions of a scramble
   already caught) + 2 unverified + 1 false-positive (DB already matched PDF).

KEY FINDING — systemic word-scrambling in modern opinions. The PDF->markdown
analyzer (~/code/scraper/analyzer) scrambles word order at line-break boundaries,
often making text nonsensical. Confirmed against PDFs, e.g. 2026 ND 112 ¶9 stores
"probable involving statutory cause decision presents purely a interpretation" for
the PDF's "probable cause decision presents purely a legal question involving
statutory interpretation". 21 such scrambles across the 30-opinion batch -> pervasive.
The authoritative PDF carries the correct text. Open strategic question logged:
deterministic re-derivation of modern text from PDFs vs. agent-patching.

## Batch `footnote-editpair-apply-2026-06-23` — corpus scaling, archive batches 2-3 (45 opinions)

Scaled the propose -> gated-apply loop across the archive-backed `SRC_MORE`
worklist (footnotes present-but-malformed in the DB vs the court archive HTML).
**Batch 2** (30 opinions, 1999 ND 129 -> 2002 ND 188) and **batch 3** (first 15 of
the next 30) repaired; same atomic gates as Phase 2b (marker-only, word-multiset,
parser-detects-each-footnote, call_para, false-absent). Logged per footnote.

Reconciliation of gate skips this run (the gates earning their keep):
- **Curly-quote byte-anchor misses** — agents emitted ASCII `("Name")N` where the
  DB holds Unicode `(“Name”)N`; a sharpened re-pass (copy curly glyphs byte-exact;
  treat bodies as already-present unnumbered orphans, not absent) cleared them.
- **2000 ND 170** — agent proposed `recover_body_absent` for the Andrew Burke
  footnote claiming the body was missing; it was in fact present as an unnumbered
  orphan. The false-absent + marker-only gates **blocked the bad re-insertion**;
  applied manually as 5 numbered orphans incl. a verified `*.*` -> `. ` body marker
  fix (archive 990353.htm prints "2. A review of case law...").
- Minor hand-corrections: one agent bracket typo (`)1`->`)[1]` not `)[1`), advisory
  `call_para` mismatches dropped, apostrophe-glyph anchors shortened.
- **1999 ND 129** + **2001 ND 137** (no agent return) hand-built; footnote counts
  cross-checked against archive `FN_N_` anchors (2 and 3 respectively).

Batch-3 residue (12 skips + 3 no-return) pending: bare-line orphan format
(1997 ND 165/169), West key-number residue interleaved with bodies (1999 ND 137),
and further byte-anchor misses. Detector 175/0 throughout; invariants 24/2/0.

## Batch `footnote-stragglers-2026-06-23` — close out the citation-confirmed list (detector 0 missing)

Hand-built exact edit-pairs (gated applier) for the last three confirmed losses the
batch agents missed on exact-string precision:
- **1997 ND 145** fns 1-3 (fn1 n.1, call ¶6) — nbsp-malformed body markers.
- **1997 ND 149** fns 1-4 (fn4 citation-confirmed) — nbsp-malformed body markers.
- **1998 ND 228** fns 1-3 — KEPT ALL THREE per the published N.W.2d reporter
  (Curiously ¶21 n.1, "Citing no authority" ¶24 n.2, "As one author" ¶26 n.3); the
  earlier plan to strip "Citing no authority" was reversed on finding it is a
  coherent footnote (call at ¶24 + on-point body), not OCR noise. Also repaired 3
  scan page-break artifacts (the scan's own page numbers 1/2/3 dropped at form-feeds,
  e.g. "466 N.W.2d ⟨1⟩ 141" -> "466 N.W.2d 141"; verified vs archive) that were
  hijacking the footnote-call detection.
Citation-graph footnote-loss detector now **0 missing** (was 17 at arc start).

## Batch `footnote-editpair-apply-2026-06-23` — first automated footnote repairs (Phase 2b)

First end-to-end run of the propose -> validate -> gated-apply pipeline. Agents
(read-only) emitted self-verified exact `old_exact -> new_exact` edit pairs from
the court archive HTML; the applier replaced + gated each opinion atomically:
marker-only edits (no letters/non-marker punctuation changed), alphabetic-token
multiset preserved (+ appended body words only), parser detects each footnote,
call_para matches, invariants 24/2/0. **17 of 28 archive-backed opinions repaired**
(incl. **1997 ND 98** n.1-3, recovering a citation-confirmed loss); 11 skipped
atomically (exact-string miss or a non-marker over-correction caught by the gate
— e.g. 1997 ND 43 fn3 comma->period). 1998 ND 228 held for manual renumber/strip
(decided). Each footnote logged. Scripts: `scripts/apply_footnote_editpairs.py`
(+ `footnote_source_diff.py`, `validate_footnote_proposals.py`).

## Batch `west-keynote-strip-2026-06-23` — strip West key-number headnote markers (corpus pass Phase 1)

West/CL-lineage opinions retained West key-number `[N]` headnote markers (runs like
`[1] [2]` at paragraph starts), which collide with footnote call `[N]` markers.
Stripped the **case-(a) marker-only** form (line-start `[N]` runs embedded before the
opinion's own prose / before `[¶N]`) across the **1,092** WEST_HEADNOTE-bucket
opinions — **8,503 markers** removed. Inline `[N]` footnote calls (after a word/
punctuation), `[¶N]` paragraph markers, and all prose are untouched: asserted
corpus-wide that the alphabetic-token multiset and `[¶]` counts are unchanged for
every opinion. Residual West headnote *topic text* (case-b, e.g. "Topic - Subtopic")
lives in other buckets and is handled in the source-vs-DB diff phase. Script:
`scripts/strip_west_keynotes_2026-06-23.py`; one changelog row per opinion (reversible).

## Batch `footnote-inline-call-retrofit-2026-06-23` — align 1999 ND 2 / 2011 ND 122 to inline [N] (Phase 2c)

The two footnotes restored earlier this arc used a bare-line call marker (Route A).
Both call digits actually survived attached in the prose (`material fact1`,
`costs.1`); retrofit to the ratified inline-[N] convention by bracketing the
attached digit and removing the redundant bare-line marker. **1999 ND 2** → ¶ 5 n.1;
**2011 ND 122** → ¶ 1 n.1. Body numbering unchanged; alphabetic-token sequence
asserted identical. Script: `scripts/retrofit_inline_call_2026-06-23.py`.

## Batch `footnote-body-marker-fix-2026-06-23` — normalize malformed footnote-body markers (Phase 2c)

Footnotes present in the text but parser-invisible because the period-form body
marker (`\nN\n\n. body`) was malformed — the space after the period dropped
(`.In`) or the whole `. ` marker dropped (`\n body`). Inserted only the missing
punctuation/space (asserted: identical alphabetic-token sequence); each body
verified verbatim against the court archive HTML. **1998 ND 94**: the opinion's
footnotes run 1–12 but only 2–5,7–10,12 were detected; fixed **fn6** (¶ 18 n.6,
citation-confirmed), **fn11** (¶ 27), and **fn1** (body present, call superscript
not preserved → call_para None) so the sequence is contiguous 1–12. (West N.W.2d
lineage uses bare-line call markers, kept here for within-opinion consistency.)
**1998 ND 225**: footnotes run 1–5 but fn4 had `.The` (space dropped) — fixed →
¶ 14 n.4 (citation-confirmed); sequence now contiguous 1–5. **2018 ND 132**: lone
footnote — body was an unnumbered ` . ` orphan amid section-heading/¶-continuation
look-alikes (`. III`, `. [¶ 18]`) and a block quote, all correctly left untouched;
numbered fn1 → ¶ 9 n.1 (bare-line call already present in ¶9). Script:
`scripts/fix_footnote_body_markers_2026-06-23.py`.

## Batch `orphan-footnote-restore-2026-06-23` — number period-orphan footnotes + inline [N] call (Phase 2c)

Citation-graph-confirmed footnotes whose BODY is present as a number-less period
orphan (`\n\n. body` — ndcourts-markdown lineage dropped the body number). The call
survived attached to the prose (e.g. `arrested in the past.2`). Per the ratified
convention, the call digit is bracketed inline `[N]` at the exact call site
(cross-checked against an authoritative source), and the orphan body is numbered in
place; the standalone parser links body → ¶ via the unique inline `[N]`. Only
structure markers added — asserted: identical alphabetic-token sequence. Restores
ONLY the citation-confirmed footnote per opinion (uncited sibling orphans are left
for the separate hand-verified backlog pass). Recovered: **1997 ND 9** → ¶ 17 n.2;
**1999 ND 103** → ¶ 32 n.2; **1998 ND 149** → ¶ 21 n.2 (call after § 32-12.2-04(1)); **1999 ND 216** → ¶ 15 n.3;
**1999 ND 154** → all 8 footnotes (1–8 number-dropped orphans; orphan-i==fn-i verified
vs archive FN_N_ bodies; fn4 ¶ 8 n.4 + fn8 ¶ 25 n.8 citation-confirmed, fns 1–3,5–7
restored for contiguity); **1999 ND 156** → all 3 footnotes (fn1 ¶ 8 n.1
citation-confirmed — its call ¶ was unknown, recovered ¶8 from the attached digit)
(each call site confirmed vs the court archive HTML `<sup>(N)</sup>`). Contiguity pass (no skipped footnote numbers): also numbered the sibling fn1 in **1997 ND 9**, **1999 ND 103**, **1998 ND 149**, and fn1+fn2 in **1999 ND 216** (each call digit survived attached; orphan-i==fn-i by sequence + archive). Script:
`scripts/restore_orphan_footnotes_2026-06-23.py`.

## Batch `modern-footnote-recover-2026-06-23` — restore modern footnotes mashed inline (Phase 2c)

Modern (1997+) footnotes the analyzer mashed **inline** into the running text rather
than detaching them (upstream `pdf_processor` regression; 2024-era opinions lose all
footnotes — see `TODO-footnotes.md` Phase 2d). Each is citation-graph-confirmed
(another opinion pincites `<cite>, ¶ X n.N`). The footnote body sat inline in/across
the call paragraph and the call superscript was OCR'd to an attached ASCII digit.
Recovery (ratified convention 2026-06-23): the inline call is **denoted by
bracketing the surviving digit** → `[N]` (kept in the prose where the court placed
it — the standalone parser resolves `call_para` from a unique inline `[N]`); the
body is excised from the prose and **appended verbatim at the opinion end** in period
form (1999 ND 2 convention). Body relocated, not altered — asserted: identical
alphabetic-token **multiset**, body verbatim vs the ND PDF; only a non-alphabetic
digit was wrapped in brackets. Parser change: `_standalone_footnotes` now fills a
missing `call_para` from a unique inline `[N]` preceding the body (gated: confirmed
body + uniqueness, so bracketed quote-alterations can't false-positive). Recovered:
**2024 ND 99** → ¶ 6 n.1 (body at paragraph end); **2022 ND 136** → ¶ 6 n.1 (body
split mid-sentence "…will not reverse unless the [footnote] findings are clearly
erroneous"; rejoined); **2024 ND 147** → ¶ 32 n.1 (body interleaved into ¶33; the
call superscript had merged into the figure — PDF prints "9.9¹ years" but it was
extracted as "9.91 years", so the duration figure was restored to **9.9 years** with
the call denoted `[1]`, verified against the rendered PDF page). The body span is
sliced from the DB by ASCII anchors so the
appended text is byte-identical to the (PDF-derived) stored text. Script:
`scripts/restore_modern_footnotes_2026-06-23.py`.

## Batch `footnote-number-restore-2026-06-23` — restore dropped footnote numbers (body present)

Citation-graph-confirmed footnotes whose BODY was already present in the text as a
number-less orphan (`\n\n. body` — the analyzer kept the body, dropped the `N`).
Each confirmed by another opinion's pincite (`<cite>, ¶ X n.N`), which establishes
the footnote exists, its number, and its call paragraph. Restored structure only —
inserted the number before the body (period form) + a standalone call marker at the
confirmed call ¶ — so the parser links body → ¶ X. The court's words are unchanged
(asserted: identical alphabetic-token sequence; only bare-number marker lines added).
Single-orphan opinions only (unambiguous match): **1999 ND 2** → ¶ 5 n.1,
**2011 ND 122** → ¶ 1 n.1. Multi-orphan + body-absent cases need per-PDF
verification (tracked in `triage/footnote-pincite-losses-2026-06-23.tsv`). Script:
`scripts/restore_footnote_numbers_2026-06-23.py`.

## Batch `footnote-degarble-2026-06-23` — 8 garbled `FOOTNOTES 0:` markers fixed

The ndcourts markdown analyzer failed to OCR the footnote superscript number in 8
opinions, emitting `FOOTNOTES\n\n0:\n\n<junk glyph>` (CJK / ToUnicode garbage —
same root cause as the digit-flip class) where the number belongs. The footnote
**body is intact** (verified present in both stored text and the PDF); only the
marker was garbage. Replaced each garbage marker with its canonical positional
number (`1:`, `2:` — footnote numbering is sequential, so a lone footnote is 1 and
two are 1/2; structural, not a glyph read). Body asserted byte-identical modulo the
removed marker lines. Now parser-detectable (`in_footnote`, verbatim). Opinions:
2013 ND 57, 2013 ND 99, 2013 ND 192, 2015 ND 94, 2015 ND 222, 2016 ND 189,
2017 ND 146, 2017 ND 285. Script: `scripts/fix_garbled_footnotes_2026-06-23.py`.

## Batch `westlaw-footnote-restore-2026-06-22` — 2 substantive footnotes dropped at Westlaw ingest

`_parse_westlaw_doc` cut opinions at the "All Citations" footer; the Westlaw
Footnotes section prints *after* it, so footnote bodies were silently dropped
(`scripts/audit_westlaw_footnotes_2026-06-22.py` →
`triage/westlaw-footnote-audit.tsv`). The corpus-wide audit of all 7,297
westlaw-sourced opinions found the loss touched almost entirely **West editorial
apparatus** ("Reported in full in the New York Supplement…", bare parallel cites,
"Rehearing pending.") — only **2** genuinely substantive court footnotes were lost:

- **2222** (43 N.D. 156, *Northern Pacific Ry. v. Sargent County*) — fn 1, a
  record note on a drain-petition filing-date discrepancy.
- **4906** (69 N.D. 290, *Petters v. Charlson Estate*) — fn 1, legislative
  history of 1937 Chapter 161 (Senate/House vote tallies).

Both pre-1953 (no `[¶]` markers), restored verbatim from the Westlaw `.doc` and
appended in ` N\n\n<body>` form (`scripts/add_westlaw_footnotes_2026-06-22.py`).
Going forward, `_parse_westlaw_doc` now re-attaches substantive numbered footnotes
and filters editorial ones (`_extract_footnotes`/`_is_editorial_footnote`), so the
bug cannot recur on new Westlaw ingests. A bulk re-ingest was deliberately NOT
done (payoff = 2 opinions; would reattach 104 editorial notes and risk reverting
other corrections).

## Batch `lyon-ocr-2026-06-22` — 9 surgical OCR fixes, Lyon v. Ford Motor Co., 2000 ND 12 (id 13068)

Character-level OCR garbles in the CL/West-OCR body, each verified against the
clean Westlaw `.doc` (604 N.W.2d 453) and each a unique single occurrence:
`satisfaclion`→satisfaction, `aecrudble`→accruable, `supersede-as`→supersedeas,
`Scholl-meyer`→Schollmeyer, `Cla'rys`→Clarys, `N.D.RApp.P.`→N.D.R.App.P.,
`$10,-360.84`→$10,360.84, `be- enforced`→be enforced, and the section heading
`Ill`→`III`. Script: `scripts/fix_lyon_ocr_2026-06-22.py`. The standalone ` 1`
footnote-call line was deliberately left intact so the pinpoint parser still
resolves footnote 1 to `¶ 7 n.1`. Surfaced by the Cowan v. Slann citation review;
chosen over a full Westlaw re-merge, which would have dropped footnote 1's body
(`_parse_westlaw_doc` cuts at "All Citations" — see TODO-validation).

## Batch `restore-source-reporter-westlaw-2026-06-22` — final 109 provenance reversions

The last reverted-correction class: 109 opinions where the `westlaw-text-merge` /
`westlaw-syllabus-recovery` batches set `source_reporter='westlaw'` (the body now
derives from the Westlaw `.doc`, which carries the court syllabus) but a later
re-ingest silently clobbered the scalar back to `'NW'`/`'NW2d'`. The bodies stayed
at the maintained Westlaw-merged version — verified that none of the 109 had a body
reverted to its pre-Westlaw NW old_value, so `westlaw` is the correct provenance for
all. Restored `source_reporter='westlaw'` (changelog-logged), then `align_primary_source`
flipped `opinion_sources.is_primary` to the westlaw row and rewrote `source_path` to
the `.doc` (108 path rewrites + 108 flips, then 1 more for 10882).

**10882** (Weiss v. Stormon, 78 N.D. 10 / 47 N.W.2d 527) was the lone edge case: the
re-ingest dropped not just the scalar but its `opinion_sources` westlaw row. Re-registered
the row pointing to `N.D./78/0010-In-re-McIntyre's-Estate.doc` (the estate caption of the
same single opinion — no separate McIntyre record exists), then restored + aligned.

`corrections_not_reverted` **109→0** — zero known silent reversions corpus-wide; the
invariant baseline is lowered to 0 (now an `OK`). Source invariants
(`source_reporter_matches_primary`, `source_path_matches_primary`, `primary_source_unique`)
all clean; 24 ok / 2 known / 0 regressed.

## Batch `restore-sig-review-2026-06-22` — REVIEW cohort (multi-opinion, 19)

The REVIEW cases were held back because each is multi-opinion: the DB kept a
SEPARATE writing (a "concur in the result" notation or an orphan signature) while
dropping the `[¶N]` MAJORITY panel that precedes it. Phase-4's divergence guard
(DB-trailing-justice ⊆ source-panel) correctly refused them — here the surviving
concurring justices are DISJOINT from the dropped majority. With every court PDF
signature block in hand the structure is unambiguous; `fix_sig_review_2026-06-22.py`
inserts the majority panel before the surviving concurrence (or restores a full
panel over an orphan last name), with a guard that every inserted surname appears
in the court PDF.

- **13 majority-panel inserts** before a separate concurrence (e.g. 2002 ND 170 →
  `[¶14]` Neumann/Maring/Kapsner/VandeWalle before "I concur in the result. Dale V.
  Sandstrom"; 2014 ND 229, 2015 ND 229 similar with "We concur in the result").
- **3 orphan last-name restorations** (2017 ND 107/119/131): the DB kept only the
  panel's final name — replaced with the full `[¶N]` panel (also fixed OCR
  "Gerald'W."→"Gerald W.").
- **1 surrogate-note** (1998 ND 161): inserted `[¶12]` panel (incl. Georgia Dawson,
  D.J.) before the Dawson disqualification note.
- **2 head-dropped West concur lines** (2000 ND 49, 2010 ND 142): the DB kept the
  *tail* of the concur line; prepended the dropped head + `[¶N]` marker, verified
  against West / CourtListener (op 896526 / 898762, court `.wpd`).

Remaining REVIEW = **1 false positive, 2000 ND 203** (oid 13291): DB already carries
the complete `[¶48]` panel; the source `[¶478]` is an OCR-garbled duplicate marker.

**Signature cohort milestone:** sigscan now flags 24, all non-defects — 22
CONTENT_LOSS (source-tree contamination, DB bodies correct) + 2 false positives
(17858 numbering, 13291 garbled-dup). Every genuine DB signature defect is fixed;
invariants 23/3/0.

## Batch `fix-marker-garbled-2026-06-22` — final MARKER_GARBLED cohort (7)

Heterogeneous despite the shared label; each verified against the court PDF (and,
where the PDF text layer was wrong/ambiguous, West / CourtListener from the court
`.wpd`):
- **2 true marker garbles** (text complete): 2000 ND 121 `[¶ *11]*`→`[¶ 11]` (two stray
  page-break asterisks); 2003 ND 156 `[1123]`→`[¶ 23]` (the double "WILLIAM A. NEUMANN"
  is in the source — preserved).
- **2 missing markers**: 2009 ND 111 add `[¶ 8]` to the Sandstrom "unavoidably absent"
  participation note; 2017 ND 289 the dissent signature dropped "Gerald W. VandeWalle,
  C.J." and its `[¶36]` marker — prepended.
- **3 dropped panels** (genuine truncations the label hid): 2002 ND 86 and 2010 ND 236
  dropped the `[¶N]` majority panel and mislabeled the trailing surrogate note one number
  early — inserted the panel, renumbered the note; 2008 ND 184 dropped the `[¶27]` majority
  block while keeping a separate `[¶15]` concur block (West/CL op 898372: "[¶27] VANDE
  WALLE, C.J., MARING, SANDSTROM and KAPSNER, JJ., concur").

Remaining: **1 false positive — 2021 ND 144** (oid 17858): the DB carries the complete
`[¶14]` panel; its paragraph numbering merely runs one behind the official PDF (`[¶15]`).
No signature missing; to be baselined when the sigscan gap is promoted to an invariant.
sigscan MARKER_GARBLED 8→1 (the false positive); invariants 23/3/0.

## Batch `restore-sig-truncation-oneoffs-2026-06-22` — final 8 TRUE_TRUNCATION one-offs

The TRUE_TRUNCATION cohort's irreducible tail — the 8 the general fixers correctly
skipped (dateline-in-source, surrogate D.J./S.J. outside the modern-surname roster,
roman-numeral section heading fused into the panel, and the 16311 divergence).
Hand-built, each justice name verified against the court PDF
(`scripts/fix_sig_truncation_oneoffs_2026-06-22.py`):

- **3 datelines appended** (1998 ND 58 / 98 / 136 — judgeship-vacancy orders): the
  `[¶N+1]` panel followed the `[¶N] Dated at Bismarck…` line; 1998 ND 136 uses
  spelled-out roles ("Chief Justice"/"Justice").
- **4 panel-before-note inserts** (1998 ND 143, 2000 ND 79, 2000 ND 225, 2014 ND 201):
  disposition text was present; only the `[¶N]` majority panel dropped while a
  surrogate/participation note survived. 2014 ND 201 also had its garbled note marker
  `[1126]→[¶26]` and `KAPS-NER→KAPSNER` repaired; 2000 ND 225 also needed its
  trailing-note `[¶28]` marker restored.
- **16311 (2014 ND 148, Rustad) RESOLVED — the DB was correct.** The phase-4 divergence
  guard had flagged this (DB "Sandstrom concurs in the result" vs the `~/refs` source's
  "Crothers concurs"). Independent authority settles it: **West 849 N.W.2d 607 /
  CourtListener op 2684722**, both sourced from the court's own `.wpd`
  (`ndcourts.gov/wp/20140014.wpd`), read "GERALD W. VANDE WALLE, C.J., DANIEL J.
  CROTHERS and CAROL RONNING KAPSNER, JJ., concur. DALE V. SANDSTROM, J., concurs in
  the result." (McEvers authored.) The C-Track slip PDF's text layer erroneously
  duplicated "Daniel J. Crothers" for the concurrence and dropped Sandstrom — a
  PDF-generation artifact, **not** a court typo to preserve. Inserted the authoritative
  `[¶27]` majority line before the DB's (correct) Sandstrom concurrence.

sigscan TRUE_TRUNCATION 8→0; invariants 23/3/0. Remaining sig cohort: MARKER_GARBLED 8
(cosmetic), CONTENT_LOSS 22 (dispositioned — not DB defects; see
`triage/missing-primary-source.md`), REVIEW 20.

## Batch `restore-sig-truncation-phase4-2026-06-21` — positional insertion of dropped majority panels

The bulk of the multi-opinion truncations share one shape: the **majority panel was dropped while a trailing element survived** in the DB — a "X, J., concurs in the result" notation, a participation note, or a separate-writing signature. The panel belongs BEFORE that trailing element. Because the dropped span is the opinion's consecutive tail (panel + trailing element) and the DB's last paragraph IS that element, inserting the panel immediately before it reconstructs source order.

`fix_sig_truncation_phase4_2026-06-21.py` does the surgical insert, gated by a **divergence guard**: every justice named in the DB's trailing element must also appear in the dropped source signature region. This is load-bearing — it rejected 2014 ND 148 (oid 16311), where the DB says "Sandstrom concurs in the result" but the source panel has Crothers concurring (factually different texts). The inserted panel is the source signature lines whose justice the DB does not already render (so a notation already present is never duplicated), every name corroborated against the court PDF. A subsumed-surname fix (don't let "Sand" match inside "Sandstrom") cleared ~43 false divergences without weakening the 16311 catch.

**77 majority panels inserted** (e.g. 1997 ND 204 → `[¶ 17]` Maring/Neumann/Sandstrom/VandeWalle before "MESCHKE, J., concurs in the result."). TRUE_TRUNCATION 92 → 10. (Two more via a trailing dangling-notation/footnote-digit strip: 1998 ND 55, 2013 ND 13.) Invariants 23/3/0.

Rescue passes (added 19 to this batch): a **short-surname fix** (exact-substring match for surnames <5 chars — an edit-distance window had matched "Sand" inside "**VAND**eWalle") cleared 9 false "Sandstrom" divergences; a **two-paragraph trailing element** handler (when "I concur in the result." and the signing name land in separate paragraphs) plus stripping a trailing roman-numeral section divider cleared 5 more; a third pass stripped roman-numeral SECTION HEADINGS that OCR floated into the signature run (PDF-confirmed via 2017 ND 265 / 2012 ND 58) for 5 more + 1 orphan. The genuine 16311 divergence stays excluded.

## Batch `restore-sig-truncation-phase5-2026-06-21` — orphan-name signature replacement

The original Whetsel pattern in the prose-tail remainder: the DB kept ONLY the panel's last justice name as a bare trailing line. Phase 1 skipped these because the source panel ends with a footnote-reference digit ("... Jerod E. Tufte 1") that broke the parser. `fix_sig_truncation_phase5_2026-06-21.py` strips the trailing digit and replaces the orphan with the full `[¶N]` panel, guarded so the orphan must equal the panel's last member and no other member already sits in the DB tail (a preceding-paragraph-concurrence check routes split positional cases to phase 4 instead). **5 replaced** (2017 ND 165/166/190/265/281; the 265 panel followed a stray trailing “III” section heading). Invariants 23/3/0.

**Still NOT auto-fixed (manual worklist, `triage/sig-drops-classified.csv`):** 8 TRUE_TRUNCATION (3 datelines, 2 surrogate-in-panel, 2 complex intertwined, 1 genuine divergence = 16311) + 22 CONTENT_LOSS + 7 MARKER_GARBLED + 20 REVIEW.

## Batch `restore-sig-truncation-phase6-2026-06-21` — participation-note truncations

The clean shapes among the surrogate/participation cases: a panel dropped before a participation note (insert the panel before the note — 2009 ND 111), or the note dropped after an existing panel (append it — 2003 ND 9). `fix_sig_truncation_phase6_2026-06-21.py` handles only panels that parse to >=3 KNOWN justices (surrogate-in-panel cases like 2000 ND 225 / 2014 ND 201 left to manual), PDF-corroborated. **2 fixed.** Invariants 23/3/0.

## Batch `restore-sig-truncation-phase2-2026-06-21` — append dropped separate-writing signatures (multi-opinion)

Phase 2 of the signature-truncation repair, covering the TRUE_TRUNCATION cases Phase 1 skipped as multi-opinion. These split into (A) **append-safe** — the DB body ends with a concurrence/dissent's prose and is missing only that separate writer's trailing signature — and (B) **positional** — the dropped paragraph is the *majority* panel, which belongs before a separate writing the DB already carries.

`fix_sig_truncation_phase2_2026-06-21.py` applies only (A), gated to a **single-justice** dropped signature (a lone separate-writer signing after their opinion), with no name overlap with the DB tail and every name PDF-corroborated; the dropped paragraph is appended in source order.

**6 appended** (e.g. 1997 ND 6 → `[¶ 29] Gerald W. VandeWalle, C.J.`; 2003 ND 200 → `[¶ 32] Mary Muehlen Maring` after a dissent). Invariants 23/3/0.

**Deliberately NOT auto-fixed (92, manual worklist in `triage/sig-drops-classified.csv`):** 74 multi-name majority panels needing positional insertion, 15 unparseable (spelled-out "Chief Justice", embedded section markers), 3 dateline/surrogate. The single-signature guard caught 2014 ND 148 (oid 16311), whose dropped paragraph is the majority panel AND whose DB body **substantively diverges** from the current source (DB: "Sandstrom concurs in the result"; source: "Crothers concurs") — proof these older multi-opinion bodies require per-case PDF arbitration, not a bulk rule.

## Batch `fix-marker-garbled-2026-06-21` — repair OCR-garbled signature paragraph markers

The MARKER_GARBLED class from the sigscan triage (see next batch): the signature panel is **complete** in the DB body, but its `[¶N]` marker is OCR-garbled (`[IT 29]`, `[¶ 21J`, `[1111]`, `[f 13]`, `(¶ 8]`, `[UlO]`, `[VIS]`) or absent — so the marker regex undercounts the paragraph sequence.

`fix_marker_garbled_2026-06-21.py` repairs the marker only: in the trailing signature paragraph it strips the leading garbled-marker token via a bounded regex (so a justice name can never be consumed — an early name-anchored approach was caught dropping "VANDE WALLE, C.J." in dry-run, because the space-split surname didn't match) and substitutes `[¶ {src_max}]`, the number the complete source carries. The replacement is a **surgical in-place substring swap** (deltas −1…+7 chars; no whitespace renormalization), and every panel name is corroborated against the court PDF.

**24 markers repaired.** 7 skipped to manual review: 4 already carry a valid `[¶N]` marker (surrogate-judge notes / wrong-but-present number), 2 single-name dissent tails, 1 panel split across a `*NNN` page-break artifact. MARKER_GARBLED 31 → 7. Invariants 23/3/0. NB: justice-name OCR garbles in the panels themselves (NEU-MANN, MAKING, YANDE WALLE, McEYERS) are left as-is — a separate cleanup, not this marker fix.

## Batch `restore-sig-truncation-2026-06-21` — restore signature blocks dropped from modern opinion bodies

A corpus-wide body-integrity sweep found that the modern DB `text_content` was ingested *verbatim* (`ingest.py`) from an **older clean-format markdown** whose analyzer had collapsed the final `[¶N]` signature paragraph down to a single trailing justice name (e.g. *State v. Whetsel*, 2017 ND 237, ended `Jon J. Jensen` where the panel is VandeWalle C.J. + four). The current `~/refs` markdown is a newer, complete regeneration that matches the court PDF, but re-ingest would regress formatting — so the fix is a surgical splice, not re-extraction.

Detection method (the prior word-ratio detector was 73% false-positive and missed 242 real cases):
- **`refs_diff sigscan`** (new) — flags opinions where the DB body's max `[¶N]` marker is below the complete source's (length-independent; 273 flagged).
- **`classify_sig_drops_2026-06-21.py`** — segments the 273 with OCR-tolerant, date-agnostic justice-name matching (hard tenure dates in `justices.py` are unreliable — Jensen's start year is wrong and justices sit as surrogates): **MARKER_GARBLED 31** (signature present, only the `[¶N]` marker OCR-garbled — *not* truncation), **TRUE_TRUNCATION 200** (panel genuinely absent), **CONTENT_LOSS 22** (substantive paragraphs lost; overlaps the 1997 contamination), **REVIEW 20**.

This batch fixes the **safe subset of TRUE_TRUNCATION** (`fix_sig_truncation_2026-06-21.py`, strict guards): gap == 1, single-signature opinion (multi-opinion concurrence/dissent cases need positional insertion → manual), plain-panel source (no concurrence/dateline/footnote mixed in), and **every restored justice name corroborated against the court PDF**. The orphan name fragment is replaced with `[¶ M+1] <panel, one justice per line>` rebuilt verbatim from the source (or appended when the signature was dropped whole, preserving any `Dated at…` dateline paragraph).

**102 bodies restored** (median +81 chars, all signature-sized; zero anomalies). 95 skipped to manual review (74 multi-opinion, 14 non-plain-panel, 7 unusual formats). 102 changelog rows (`text_content`), revertible via `cleanup revert`; these bodies are now protected from future silent re-ingest by the Phase 0 guard. TRUE_TRUNCATION 200 → 98 remaining. Invariants 23/3/0.

**Still open:** MARKER_GARBLED (31, marker-repair batch), remaining TRUE_TRUNCATION (98, multi-opinion/positional), CONTENT_LOSS + REVIEW (42, manual triage).

## Batch `restore-reverted-corrections-2026-06-21` — recover work lost to silent re-ingest reversions

Tracing why the `casename-docket-decontam` dockets had reverted revealed the systemic cause: **the DB is the source of truth, but `merge_nd_metadata` (run by the weekly pipeline) re-read the `~/refs` JSON and blindly overwrote corrected fields with the source value, without logging** — silently undoing prior corrections on every merge. (The `1997_opinions.json` source is itself contaminated for a 1997 batch — misfiled content, e.g. `1997ND16.md` holds 1997 ND 15 — so the overwrite re-applied *wrong* values.)

New tooling to make corrections durable:
- **`reconcile_corrections.py`** — reconstructs each correction's intended value from `changelog` (latest `new_value` per opinion×field) and compares to the live DB: INTACT / REVERTED (back at the pre-correction value) / DIVERGED. Found **418 silently-reverted** scalar corrections + 337 diverged (`text_content` excluded — its changelog rows are descriptions, not literal values).
- **invariant `corrections_not_reverted`** — counts REVERTED; any increase = a new silent reversion surfaces on the dashboard.
- **merge write-guard** — `merge_nd_metadata` now consults `corrected_values()` and keeps/restores a logged correction instead of clobbering it (a dry-run guards 517 writes / restores 495). Closes the leak for all future merges.

**Restored 309 reverted content corrections** (this batch): docket_number 189, case_name 47, author 20, date_filed 20, judges 16, opinion_url 14, per_curiam 3 — each rewritten to its changelog-intended value and re-logged. `corrections_not_reverted` 418 → **109**; the remaining 109 are `source_reporter` (provenance, coupled to opinion_sources/`source_reporter_matches_primary`) and are deferred to the `align_primary_source` path. Invariants 23/2/0. The 337 DIVERGED stay queued for human review (some intentional). NB: several restores re-fixed case_name contaminations that had a prior logged correction (e.g. 12438 *Symington*→**Edwards v. Edwards**).

## Batch `casename-docket-decontam-1997-2026-06-20` — 11 mislabeled 1997 opinions

Surfaced by a new `refs_diff selfcheck` triage of the major text-divergence bucket (DB self-consistency: does the body state its own neutral cite + party surnames?) and **narrowed by cross-checking the court's own opinion-report spreadsheet** (`input-data/court-opinions-report-2026-05-30.xlsx`): of 25 self-check candidates, the court Title **confirmed 14 "Interest of X (CONFIDENTIAL)" cases were correctly named** (classifier false positives on anonymized captions — no body surname to match), leaving **11 genuine contaminations**. Each carried a *neighbor's* case_name (e.g. 1997 ND 16 *Frafjord v. Ell* was labeled "State v. Ertelt", the real name of 1997 ND 15) plus a cite-shaped docket placeholder (`1997ND16`).

Every correct name is **triple-sourced** — the court's own published caption in the opinion body, CourtListener, and the body's in-body neutral cite matching its label. Dockets are the real court file numbers from the opinion body in 8-digit `19YYNNNN` form (matching the **reverted** `docket-cite-shaped-2026-06-10` values — see process note), Herrick's consolidated range comma-joined:

| cite | was | now | docket |
|---|---|---|---|
| 1997 ND 16 | State v. Ertelt | Frafjord v. Ell | 19960097 |
| 1997 ND 30 | Wishnatsky v. Huey | Borr v. McKenzie County Public School District No. 1 | 19960157 |
| 1997 ND 33 | Orgaard v. Orgaard | Huesers v. Huesers | 19960218 |
| 1997 ND 40 | Ingalls v. Paul Revere Life Insurance Group | Sickler v. Kirkwood | 19960226 |
| 1997 ND 50 | In the Matter of the Estate of Ruben J. Peterson | Owan v. Owan | 19960235 |
| 1997 ND 59 | Traynor v. Leclerc | Austin v. Towne | 19960215 |
| 1997 ND 62 | City of Williston v. Hegstad | Sumra v. Sumra | 19960129 |
| 1997 ND 71 | Disciplinary Board v. Leier | State v. Breiner | 19960298 |
| 1997 ND 72 | Joseph D. Moch, Personal Representative… | Mosbrucker v. Mosbrucker | 19960329 |
| 1997 ND 138 | McCabe v. North Dakota Workers Compensation Bureau | Reimche v. Reimche | 19960239 |
| 1997 ND 155 | Longtine v. Yeado | State v. Herrick | 19970019, 19970020, 19970021 |

22 changelog rows (case_name + docket_number), revertible via `cleanup revert`. Invariants 23/2/0.

**Process note (open):** the canonical dockets for these were already computed by `docket-cite-shaped-2026-06-10` (e.g. 12346 → `19960097` in that batch's changelog) but the current values had **reverted to cite-shaped placeholders**, and the case_names were scrambled — evidence that a later re-ingest/scraper pass **overwrote prior corrections** for a swath of the 1997 cohort. The contamination almost certainly extends **beyond these 11** (a wrong case_name doesn't cause text divergence, so most won't appear in the major bucket); a corpus-wide caption-vs-`case_name` audit is queued.

## Batch `cite-spacing-review-2026-06-20` — the 21 held cite-spacing spots, adjudicated individually

The needs-review spots `cite-spacing-rejoin` correctly held back, each verified against the slip PDF (`scripts/fix_cite_spacing_review_2026-06-20.py`; every pattern requires internal whitespace so it can't touch a clean copy of the same cite). **19 fix-entries / 21 occurrences across 18 opinions:**

- **8 N.D.C.C. — slip page number injected mid-citation across a page break.** The section number straddled a page boundary and the PDF→markdown extraction dropped the page number into the middle of it (`§ 65-01-`·`5`·`02(5)(c)` → the print reads `§ 65-01-02(5)(c)`). Reconstructed the true cite, dropping the stray page digit: 16049 `59-12-15`, 16230 `25-03.3-01`, 16672 `32-03.2-02`, 16784 `28-34-01`, 17747 `34-03-01`, 17898 `19-03.4-01`, 18109 `14-02.4-02`, 18192 `65-01-02`. All 8 now resolve in the graph.
- **1 N.D.A.C.** (19426) de-spaced to the court's predominant print form `§ 33-15-07-2(1)`; the authority is already in the graph via the canonical `§ 33-15-07-02` occurrence in the same opinion.
- **1 range** (17642) `§§ 28-32-42-49`: closed the page-wrap but **kept a space before the range hyphen** — `28-32-42 -49` — so the first cite stays a complete 3-part section and isn't mistakable for a 4-part N.D.A.C. number (court convention; the `28-32-42` head now resolves).
- **9 historical / out-of-jurisdiction** de-spaced to true form (won't enter the ND graph): 16462 `47-1901` (**1943 N.D. Revised Code — ND primary law**, the NDCC's predecessor; no corpus yet), 17539 `59-6a201` (Kan.), 18998/19992×3/20117 (Fargo Municipal Code), 19841 `2-117`/`2-115` (U.P.C.), 19912 `13-3101` (Ariz.), 20075 `19-4902` (Idaho).

**Left as-is:** 11715 (`§§ 27-20-30 -32`, 1994, no PDF) — a range that already carries the disambiguating space before the range hyphen, by the same convention applied to 17642. Invariants 23/2/0.

## Batch `cite-spacing-rejoin-2026-06-20` — stray whitespace inside N.D.C.C./N.D.A.C. section numbers

Surfaced by a new DB-vs-`~/refs` integrity audit (`refs_diff citespaces`): **1,222 spots in 645 opinions** where a section number carried a stray space or newline around a hyphen (`§ 28-32- 46`, `§ 12.1-16-\n01`). Root cause confirmed against the slip PDFs — the court's print **wraps the section number across a line**; the PDF→markdown derivation rendered the wrap as whitespace inside the number. Not the court's text, a typesetting artifact.

Effect on the citation graph: of the 1,222, **1,067 (87%) had still extracted correctly** (jetcite tolerated the space); **155 were lost** — that exact section was absent from the opinion's `text_citations`. jetcite's gap was positional (it tolerated a space after the first group but not before the final group, and broke on any newline).

Two-layer fix:
1. **jetcite hardened to ≥2.5.4** (`patterns/states/nd.py`): inter-group separators in the NDCC/NDAC section + chapter patterns changed from the loose `[^.\w]{1,2}` / single `[^.\w]` to a shared `_SEP = \s*[dash]\s*` that absorbs surrounding whitespace/newlines and *requires* an actual dash — which also drops a latent comma false positive. 478 existing tests pass + 3 new regressions.
2. **Text cleaned** (`fix_cite_spacing`, this batch): **1,201 high-confidence rejoins across 639 opinions** — whitespace removed only inside a number matching a strict N.D.C.C./N.D.A.C. grammar (title 1-2 digits, every later group exactly 2 digits + optional decimal); no digit ever altered. The dry-run's strict grammar correctly **held 21 needs-review** spots that would have corrupted: foreign statutes caught by a bare `§` (Kan./Ariz./U.P.C./Fargo Municipal Code/1943 Revised Code), true ranges (`27-20-30 to -32`), and numbers the extractor truncated. Those 21 are left verbatim for manual adjudication (`triage/cite-spacing-rejoin.md`).

Re-extracted the 639 changed opinions: **130 of the 155 previously-lost section cites recovered**; statute cites 38,914 → **39,052**. The remaining 25 absent = the 21 held cases + a handful of well-formed *bare-`§`* cites whose text is now clean but which jetcite declines to extract without a nearby "N.D.C.C."/"section" cue (a separate signal-scope question, not spacing). Snapshot `opinions.db.bak-pre-cite-spacing-2026-06-20`; `cited_by` rebuilt (print_anomalies overrides applied); invariants 23/2/0.

## Batches `docket-cite-shaped-2026-06-10` + `parallel-backfill-witnessed-2026-06-10` — docket queue closed; 8 witnessed parallels

**Dockets:** all **198 cite-shaped `docket_number` values** (`1997ND155`-style, the Herrick-class systemic sibling; 158 from 1997) fixed, plus 2 side-catches → **200 corrections, 0 cite-shaped remain**. Sources, in priority: the court's own cTrack report (36 unique joins by neutral/N.W. cite incl. the consolidated Beylund/Wojahn pair `20140133, 20140315`), opinion frontmatter/caption file numbers for the 1997 cohort (`Civil 960144` → `19960144`, ranges expanded per the Herrick comma-join convention), and caption `No. 20230123` for the 2023 NECJD chambering. Side-catches: **17035 carried its neighbor's docket** (Vacancy No. 3 NECJD is 20170270 per the report; it had 17046's 20170327) and 17046's `No. ` prefix stripped.

**Parallels:** re-ran the witnessed-backfill gates over the current parallel_pair queue: **8 AUTO adds** (2018–2025 opinions whose N.W.2d/3d parallel never arrived from CL — 2 to 11 independent citing witnesses each, volume date-window verified, no conflicts, cited row had no N.W. parallel). `parallel_pair` 597→**556** (the 11-witness *Interest of Skorick* group alone cleared 11 flags). Remaining queue = single-witness holds, the shared-table-page family (multiple summary affirmances legitimately sharing one N.W.2d page), and the ~25 CL/Westlaw clusters. Invariants 23/2/0.

## Batch `rules-missing-appendices-2026-06-10` (rules.db) — appendices c, d, e, l, m added

The five N.D.R.Ct. appendices on the live index but absent from the mirror repo and the DB (surfaced by the version-interval surgery). Fetched + converted with the **rules-scraper's own extractor/HTML→markdown converter** (same provenance as the rest of the corpus): **Appendix C** (Rule 8.3 Informational Statement), **D** (Pretrial Conference Statement), **E** (Confidential Property and Debt Listing), **L** (Rule 8.3.1 Informational Statement), **M** (Rule 8.3.1 Scheduling Order). Single current versions each; `effective_start=NULL` — the site's own version table carries a placeholder date (01/01/0001), so the adoption date is honestly unknown rather than invented. FTS indexed; lookups verified. The mirror-repo/scraper gap stays filed under TODO-audit 14b (a future full re-ingest must include them or it would silently drop these provisions).

## Batches `dedup-ramstad-12824-2026-06-10` + `marker-style-dotted-2026-06-10` — check #6 run corpus-wide; the dotted-marker blind spot

Ran the **shingle self-similarity detector** (audit check #6 proper — the body-duplication scan the marker-keyed stored-twice sweep couldn't extend to markerless texts) over all 19,793 opinions. Result: **pre-1997 is clean**; 2 flags, both modern. *Statoil* 16959 (0.564) is legitimate — consolidated-case party/lease lists genuinely repeat. ***Ramstad* 12824 (0.37) was a real markerless stored-twice**: CL OCR copy + analyzer copy, undetected because the analyzer copy's markers use a **dotted style `[¶ 1.]`** that no marker regex in the pipeline matches — the opinion was invisible to para_continuity entirely. Dropped the CL copy (rehearing-keyword scan clean), normalized markers to the PDF's `[¶N]` style; result ¶1–38 contiguous, exactly matching the PDF.

The dotted style swept corpus-wide: **6 more carriers, all from the same early-1999 ingest run** (1999 ND 24–35). All normalized to the PDF style (`marker-style-dotted-2026-06-10`); 12825 additionally had its ¶10–11 missing (signature block + Meschke-retirement note) — spliced verbatim from the PDF, now ¶1–12 contiguous. para_continuity 521→**520**; invariants 23/2/0.

## Batch `print-anomalies-registry-2026-06-10` — durable registry of typos in the COURT'S print + citation-graph overrides

New shipped table **`print_anomalies`** (35 rows: 25 in-corpus citation typos + 10 out-of-corpus citation/date typos), recording every print-verified instance where the **authoritative document itself** contains an apparent error. Policy (ruled 2026-06-10): (1) `text_content` stays **verbatim to the print** — typos preserved; (2) the **citation graph resolves to the intended case** — `cite_extract.apply_print_anomaly_overrides` runs on every `cited_by` rebuild, deleting mis-resolved edges (e.g. *Paulson* printed "1998 ND 7" had been crediting *Lohstreter*; *Smestad* printed "2001 ND 91" crediting *McDowell*) and ensuring the intended edge exists; (3) each row carries a **follow-up note**: West sometimes publishes corrections and the court submits corrected pages, so our slip-PDF text could miss a court-approved correction — not assumed, but flagged for review against West advance sheets / bound volumes.

Verified post-rebuild: all 8 previously mis-resolved edges removed; every intended pair present. Two corrections fell out of building the registry: **15948 restored to "599 N.W.3d 323"** (the print genuinely reads N.W.3d at the ¶20 short form — 4× glyph render; the same-day "impossible series" fix violated the verbatim policy and is reverted; the override resolves it to *Svedberg*), and **12605 `case_name` "Wodrich v. Bauske" → "Paulson v. Bauske"** (the caption is "Rebecca J. PAULSON, n/k/a Rebecca J. Wodrich v. Raymond J. BAUSKE"; the n/k/a surname had been used as the case name; courts cite it as *Paulson*). Audit baselines (`_KNOWN_COURT_PAIRS`/`_KNOWN_COURT_PINCITES`) now note the table as the authoritative registry.

## Batch `parallel-pair-textfixes-2026-06-10` — triage of the parallel_pair flags surfaced by the digit batches

Worked the citing-side slice of the newly visible parallel_pair flags (the digit fixes made these cites parse, exposing pre-existing issues). **4 citing-text junk tokens fixed** (print/oracle verified): Hagerty "5801 N.W.2d 139"→"580 ..." (glued digit), Hawkinson "591 N.W.2d144"→"591 N.W.2d 144" (missing space), Svedberg "599 N.W.3d 323"→"N.W.2d" (series OCR — N.W.3d did not exist in 1999) ***[REVERTED same day — the print genuinely reads N.W.3d; see `print-anomalies-registry-2026-06-10`]***, Haugrose "265 N.W.2d 677"→"765 ..." (volume flip, case-volume invariance + print of the full cite). **5 more court typos print-verified and baselined**: *Lee* cited "1999 ND 218" (is 1998), *Ebach* "689 N.W.2d 566" (589), *Datz* "346 N.W.2d 724" (846), *Harmon* "1997 ND 223" (233), *Gibson* with Moch's parallel "578 N.W.2d 129". `parallel_pair` 606→**597**. The remaining batch-surfaced flags are the cited-side cluster class (shared-page summary affirmances, cross-wired parallels — Witzke/Swearingen/Hirsch etc.) and stay in the standing §parallel queue with the ~25 CL/Westlaw clusters. Invariants 23/2/0.

## Batches `digit-flips-pass3-2026-06-10` + `digit-flips-residue-2026-06-10` — final 23 fixes; the digit-flip sweep is DRY

**Pass 3** re-swept the whole analyzer era with looser pairing (2-digit diffs and ±1-length tokens, BOTH-side context match required): 22 candidates in 20 opinions — the expected residue tail (multi-digit corruptions like `688886`→`68886`, `714`→`617`, `1881`→`1331` that single-flip pairing cannot propose). **All 22 personally read against rendered print crops** (`triage/flipverify-corpus/pass3/`); all 22 confirm; applied. **Residue batch**: completed the Jones cite in 15869 ¶8 — the court's print miscites *State v. Jones* as "812 N.W.2d 484" (true 817 N.W.2d 313); the corpus batch had applied the volume half, this applies the page half + drops a stray analyzer period, making the text verbatim-faithful to the print.

A striking sub-class surfaced: in **9 of the 22, the print itself carries the typo** and the DB had been silently "correct" (matching the true cite — these texts likely passed through CL's editorial corrections): *Paulson* printed as "1998 ND 7" (is ND 17), *Dakutak* "652 N.W.2d 750" (562), *Stout* "506 N.W.2d 903" (560), *Rockwell* "579 N.W.2d 406" (597), *Henderson* "640 N.W.2d 617" (714), *Lyon* "604 N.W.2d 543" (453), *Howe* "842 N.W.2d 64" (646), *Jones* (above), and a literal "718 N.W.2d 01". Per [[feedback_preserve_source_typos]] the slip print governs: text now matches the print verbatim, the `citations` table keeps the true parallels, and all 9 are baselined in `_KNOWN_COURT_PAIRS`. Cite graph re-scanned (tc 333,760, cb 114,354, 0 unresolved collisions); `parallel_pair` 607→**606** net; pinpoint_range 0; invariants 23/2/0.

**The analyzer-era digit-corruption sweep is now dry**: cite layer (310) + cohort (70) + corpus single-flip (618) + pass-3/residue (23) = **1,021 print-verified corrections**; remaining known exposure is only the 130 no-PDF opinions (1997–98 pre-scraper, Westlaw-witness only).

## Batch `digit-flips-corpus-2026-06-10` — 618 digit fixes in 499 opinions; the analyzer-era digit-flip class CLOSED corpus-wide

Scaled the print-verified digit-flip method to the **entire analyzer era**: 6,965 markdown-source opinions scanned (130 no PDF), **129,160 ¶s digit-compared** against their court PDFs (`triage/digit_compare_corpus_2026-06-10.py`, 10-way parallel) → 31,336 raw-mismatch ¶s (24% star-pagination/footnote noise) → **621 context-matched single-digit candidates in 502 opinions** (1997–2017, falling to ~zero after — exactly the OCR-era signature). Only overlap with the 2026-06-09 cohort: the 2 known text-layer rejects, confirming the 70 prior fixes now match their PDFs.

**Verification (three layers):** (1) 3× print crops rendered for all 619 (`triage/flipverify-corpus/`); (2) **21-subagent fan-out read every crop** → 581 CONFIRM / 38 UNCLEAR / 0 REJECT; (3) personal review: a deterministic **10% sample of confirms (57/57 agree)** plus **all 38 UNCLEARs re-cropped and read personally** (35 confirm, 1 REJECT — oid 17281's printed footnote marker is ¹ where the text layer says 7, the third ToUnicode case — and 2 special-cased). The special pair: oid 14743 ¶46 quotes the disbursement statute with items printed "**10.**/**11.**" where the DB read "3./4." — multi-digit loss the single-flip pairing mis-paired (proposed 9/9); fixed with context-anchored replacements from the print.

Applied **618 token fixes in 499 opinions**: flipped dates, dollar amounts, statute/rule numbers, ¶ pincites, and cites. Cite graph re-scanned for the 499 (tc 333,811→333,753; **cb 114,287→114,352** and **xref 809→759** — corrected cites now resolve). The corrected text also **surfaced 4 court typos** previously invisible (print-verified, true case identified by name+parallel, baselined in `_KNOWN_COURT_PINCITES`/`_KNOWN_COURT_PAIRS`): *Dvorak* cited "2006 ND 6" (is 2000 ND 6), *Henry* "1999 ND 141" (1998), *Rist* "2003 ND 133" (113), *Clark* "1998 ND 155" (153) — plus 17 newly-visible cited-side parallel issues joining the standing parallel_pair queue (594→607 net of baselines). 5 adjacent multi-digit divergences noted by verifiers queued in `triage/digit-flip-followup-2026-06-10.tsv`. Invariants 23/2/0. Snapshot `opinions.db.bak-pre-corpus-flips`. **With this batch the known analyzer-era digit-flip exposure is closed**: citation layer (2026-06-09), cohort non-citation (70), corpus non-citation (618).

## Batch `rules-version-surgery-2026-06-10` (rules.db) — version_intervals 11→0; 5 provisions created, 7 versions relocated, 9 deleted

Worked the `version_intervals` audit queue (11 zero-width `START_GE_END` intervals). Every involved page was fetched live from ndcourts.gov and classified by its **H1 title + Effective Date** — the zero-widths were symptoms of three ingest defects:

**A. Foreign pages filed as rule versions.** The rules ingest followed version-history links to documents that are not the rule. Relocated to their own (new) provisions, intervals set from the pages' own effective dates: **N.D.R.Ct. appendix k** (2 versions, was inside Rule 3.5 — its H1 is "APPENDIX K. RULE 3.5 ELECTRONIC FILING REQUIREMENTS"), **N.D.R.Ct. appendix f** (2, was inside 8.8), **N.D.R.Ct. appendix a to rule 8.9** (1, was inside 8.9), **N.D.R.Civ.P. Table A** (2, was inside Rule 81 — and Rule 81's `current_version_id` pointed at the Table A page), **N.D.R.Ct. 8.3.1** (2, was inside 8.3 — 8.3.1 is a distinct rule, adopted eff 3/1/2018). Admin **Order** 21 carried five Admin **Rule** 21 pages — byte-identical duplicates of provision 505's own rows → deleted. Home timelines restitched (3.5, 8.8, 8.9, 81, 8.3, Order 21).

**B. Same-date republication twins** (two site pages, same effective date, near-identical text): non-current twin deleted — Admin R. 13 (identical), Admin R. 48 (ratio 0.909), Admin R. 7 (0.820), N.D.R.Ct. appendix a (0.999). Full rows preserved in the snapshot.

**C. Renumber/repeal pages carrying the successor's date** → prior text gets `effective_start=NULL` (schema: unknown/from −inf), end = supersession: **N.D.R.Ct. 4.1** pre-repeal text [NULL→2000-03-01], repeal notice now the operative version, provision status → `repealed` (an `as_of` lookup today previously returned the repealed rule's text as current!); **5.3** pre-renumber text (page titled "RULE 8.1 RECEIVERS") [NULL→2013-03-01]; **appendix b** pre-2000 form [NULL→2000-03-01].

`current_version_id` repointed (81, 8.3, appendix a, appendix b, Order 21, 4.1); external-content FTS maintained (delete + re-add with the new citation). Verified: `version_intervals` **0**; point-in-time spot-checks correct (3.5@2018-06 → rule text not appendix; 4.1@1999 → pre-repeal text, 4.1@today → repeal notice; Order 21 → minority-justice order); **0 active provisions without an open version** corpus-wide. Snapshot `rules.db.bak-pre-version-surgery-2026-06-10`. Tool `triage/rules_version_surgery_2026-06-10.py`.

**Ingest gaps surfaced for follow-up** (TODO-audit.md): the live N.D.R.Ct. index lists appendices a–m, but provisions exist only for a/b/g/i/j (+f/k/8.9-appendix created here from rule-history strays) — **c, d, e, l, m are absent from the DB entirely**; the rules ingest needs (1) an H1-vs-provision guard so foreign pages can't join a rule's timeline, and (2) full appendix coverage from the index.

## Batch `digit-flips-pdfverified-2026-06-09` — 70 non-citation-layer digit flips fixed, every one verified against the printed page

The first systematic audit of the **non-citation digit-flip exposure** (memory class: 3↔8/5↔6 flips in analyzer-era texts, invisible to character scans). Scope: the 226 substantive-missing-¶ cohort — the texts with demonstrated analyzer extraction failures. Method (`triage/digit_compare_2026-06-09.py` + `digit_flip_candidates_2026-06-09.py`): per ¶ present in both DB and court PDF, compare ordered digit-token sequences; candidate = same-length token pair differing in exactly one digit with matching ±12-char context AND the DB token absent from the PDF ¶ entirely (so every DB occurrence is a flip). 5,014 ¶s compared → 1,640 raw mismatches (mostly star-pagination/footnote noise) → **72 context-matched candidates**.

**Every candidate was verified against the printed glyphs** — `triage/render_flip_crops_2026-06-09.py` rendered a 3× crop of each location from the court PDF (the pixels, not the text layer), all 72 read individually. Result: **70 confirmed, 2 REJECTED where the PDF's embedded text layer itself is wrong** (ToUnicode errors — print reads `N.D.C.C. § 31-11-06` and `§ 9-09-06`; the DB was already correct; the text layer says 41-11-06/9-01-06). The rejections prove the text layer alone cannot certify these fixes.

Applied 70 token fixes in 51 opinions (`digit-flips-pdfverified-2026-06-09`): flipped dates ("August 80, 2011"→30; "1:80 a.m."→1:30), dollar amounts ($8,561,398→$3,561,398; $54,681→$54,631; $817→$317/mo), statute refs (§ 82-04-04→32-04-04; § 39-24-09(5)→(1); § 10-19.1-58(8)→53(3)), and case cites to *other* opinions (581→531 N.W.2d 284 *Marshall*; 869→369 N.W.2d 109 *Radspinner*; 864→364 N.W.2d 56 *Cloverdale*; 708 N.W.2d 806→703 N.W.2d 306 *Parisien*, a double flip) — a class the parallel-pair detector can't reach. Citation-class fixes were additionally corroborated by the corpus itself (the corrected cite resolves to the named case; the flipped one resolves to nothing).

**Two court typos preserved verbatim** (print verified, baselined in `_KNOWN_COURT_PAIRS`): 16184 prints "*Hoffman*, 2013 ND 137, **835 N.W.2d 836**" (true parallel 834 N.W.2d 636) and 16917 prints "*Johnson v. Hovland*, 2011 ND 64, **795 N.W.2d 194**" (true parallel 795 N.W.2d 294 per CL pagination) — the DB text now matches the print, the `citations` table keeps the true parallels. Markdown patched in step; cite graph re-scanned for the 51 (tc 333,814→333,811, cb 114,280→114,287); invariants 23/2/0. Verification crops retained in `triage/flipverify/`.

## Batch `substantive-missing-2026-06-09` — 219 opinions' substantive missing ¶s spliced from court PDFs

The SUBSTANTIVE class from `text-missing-measured-2026-06-09.tsv` (opinions missing real prose paragraphs, not just signature blocks). Full-body pdfminer re-extract was evaluated first but these are CL-frontmatter texts without the `Filed/IN THE SUPREME COURT` body anchor, so all 226 took the **surgical splice path**: each missing ¶ re-extracted from the court PDF at apply time, page-footer digit lines at `\x0c` breaks joined, trailing bare digit/roman artifact lines trimmed, spliced `[¶ N] <prose>` immediately before the next present marker (footnote-safe, order-preserving), markdown patched in step. **219 applied, 7 held**: 5 stale (now contiguous — fixed by earlier marker batches), 12605 *Wodrich* (known block-quote false positive, verified against archive 2026-06-09), and **17357 *Helbling* 2019 ND 27 — its PDF text layer extracts pages out of order AND lacks ¶22–32 (the Fisk page-rotation class); queued for individual repair**. Cite graph re-scanned for the 219 (tc 333,803→333,814 — the restored paragraphs carry 11 net cites); `para_continuity` 614→**525** (remainder = NO_MARKER_TEXT queue, PDF_LACKS_MARKER rows, restarts); invariants 23/2/0. Tool `triage/fix_substantive_missing_2026-06-09.py`.

## Batch `sig-splice-2026-06-09` — 473 missing signature-block ¶s spliced verbatim from court PDFs

The SIGNATURE class from `text-missing-measured-2026-06-09.tsv`: opinions whose **only** missing paragraph is the justices' signature block (the Clayburgh ¶37 class at scale — names only, <160 chars, no prose words). For each, the ¶ body was **re-extracted from the court PDF at apply time** and spliced as `[¶ N] <names>` immediately **before the next present marker** — order-preserving and footnote-safe (footnote blocks sitting between the flanking markers stay attached to the preceding paragraph, matching analyzer layout). pdfminer page artifacts swept into the block when the signature spans a page break — bare page-number lines at `\x0c` breaks and bare roman-numeral section headings (verified already present in the DB text) — were stripped; the names themselves are verbatim PDF text. Per-document marker spacing style (`[¶N]` vs `[¶ N]`) preserved.

Applied **473 of 488** (every row flanked by markers on both sides; zero unflanked). 15 skipped as already whole — concur-style signature ¶s recovered by earlier marker fixes after the worklist was built. On-disk markdown patched in step where it too lacked the ¶; for ~½ the set the markdown already carried the signature paragraph (space-joined names) — the divergence was DB-only, and the spliced names match. Re-scanned the 473 through `cite_extract` (12,936 citations deleted/re-extracted, totals unchanged at tc 333,803 / cb 114,280 — signature blocks carry no cites, as expected). `para_continuity` 1,086→**614**; invariants **23 ok / 2 known / 0 regressed**. Tool `triage/splice_signatures_2026-06-09.py`; snapshot `opinions.db.bak-pre-sig-splice-2026-06-09.zst`.

## Batch `para-marker-ocr-variants-2026-06-09` — 287 more OCR-mangled ¶ markers recovered (gap classification pass)

Classified all 1,206 `para_continuity` GAP opinions by cause (`triage/classify_para_gaps_2026-06-09.py` → `para-gap-classified-2026-06-09.tsv`): **341 CORRUPT_TOKEN** (a bracketed token holding the missing ¶ number sits in the gap — the pilcrow OCR'd as `IT`, `1`, `II`, `f`, `t`, `V`, `IE`, TeX `$\\P$`, stray punctuation, or dropped entirely leaving bare `[n]`), **736 TEXT_MISSING** (paragraph genuinely absent; 722 have court PDFs), **106 NO_MARKER_TEXT** (text present, marker absent). All flagged opinions are `source_reporter='ND'` analyzer-era — the same scraper-OCR family as the digit flips.

Applied: **287 markers recovered across 265 opinions** — replacement gated on the token containing *exactly* the missing number between the gap's flanking markers; bare-digit `[n]` tokens additionally require paragraph-initial position outside footnote context (a footnote `[2]` can never be promoted to `[¶ 2]`). Source markdown patched in step. `para_continuity` GAPs 1,206→**1,056**; invariants 23/2/0. Tool `triage/fix_marker_variants_2026-06-09.py`.

**TEXT_MISSING measured against the court PDFs** (`triage/measure_text_missing_2026-06-09.py` → `text-missing-measured-2026-06-09.tsv`): of 722 opinions with PDFs, **488 are signature-only** (the missing ¶ is the justices' signature block — the Clayburgh ¶37 class; splice-from-PDF batch queued), **226 have substantive missing paragraphs** (splice/re-extract queue; prime digit-flip carriers), 74 missing-¶s aren't marked in the PDF either (per-item). **`para-marker-restore-2026-06-09`**: 5 NO_MARKER_TEXT markers re-inserted where the PDF's ¶-opening words matched uniquely at a paragraph boundary; the other 101 defeat exact matching (OCR drift / footnote structure / `[.¶ N]` almost-clean variants) — queued in TODO-audit.md.

## Held-queue closeout + `rehearing-restitch-2026-06-09` — the 41 stored-twice holds resolved; 8 dropped rehearing blocks caught and restored

**Self-audit finding (important):** scanning the 576 applied dedups' changelog old-texts showed the dropped OCR copies in **8 opinions** contained a genuine `## On Rehearing` block the kept copy lacked (rehearing ¶-numbers can sit *below* the dissent-inflated copy-1 max, slipping the max gate — e.g. *Farstveet* rehearing ¶26–33 vs dissent end ¶53). All 8 confirmed against the court's archive HTML and **re-appended** (`rehearing-restitch-2026-06-09`: Lohstreter 12603, Harmon 12636, Braunberger 13110, Syvertson 13283, Logan 13291, Farstveet 13407, Shiek 13574, Aasmundstad 15164). A 9th, *Hillerson* 16173, was caught pre-apply by the max gate (rehearing ¶44–45) and deduped-with-stitch. The `## Dissent`/`## Concurrence` headers in dropped copies are CL sectioning of content copy 1 carries inline (covered by the contiguity+max gates) — verified not lost.

**The 41 held rows, all resolved** (continuing batch `dedup-storedtwice-2026-06-09`):
- **27 class A** — copy-2 marker numbers digit-flipped above copy-1 max (`80`=30, `89`=39…); flip-explainability + jaccard 0.87–0.96 gates; dropped.
- **Class B (10), archive HTML as arbiter:** 4 copy-1 marker fixes (signature ¶s OCR'd: `[¶ 16]`→`[¶ 23]` Skadberg, →`[¶ 17]` Paul, `[¶ 31]`→`[¶ 32]` Phipps, `[¶ 5]`→`[¶ 35]` Kappenman) + Wodrich 12605 verified exact (its out-of-order ¶38/39/45 are a block quote, matching the archive); 13584 Clayburgh **spliced the missing `[¶ 37] Gerald W. VandeWalle, C.J.` signature**; 14938 Erickson restored a missing `[¶ 3]` marker (text present); 16373 Albrecht dissent markers renumbered ¶20–26; 16520 Martinez concurrence markers fixed; 13116 Lawrence **body rebuilt from archive HTML** (copy 1 missing ¶32–33 + the legitimately-quoted ¶13–17 block; now ¶1–39 per archive).
- **Class C (3):** Estate of Fisk 15505 had a **page-order-rotated body** (¶17–23 printed before ¶1–16) — pdfminer re-extract from the court PDF (`reextract-pdfminer-15505-2026-06-09`, PDF contiguous ¶1–23). 20124 *Anne Carlsen* and 20408 *Simpson* are **false positives**: their court PDFs print the same restarting sequences (embedded quoted orders with own ¶ numbering) — no change.

Post-work: graph rebuilt (`text_citations` 333,845→333,803; `cited_by` 114,280); invariants 23/2/0; `para_continuity` 1,269→1,240. Side note for the queued `622 N.W.2d 432` tangle: *Lunstad* 18358's archive-rebuilt header also claims that cite — now four claimants (Syvertson holds it; Matrix has 6 witnesses; Lee + Lunstad archive headers) — strengthens the suspicion of an archive-title stamp artifact for Dec-2000 opinions.

## Batch `dedup-storedtwice-2026-06-09` — 549 opinions had their body stored twice (clean copy + appended CL OCR copy)

The `[If N]` marker pass below held 31 opinions whose corrupted marker had a clean `[¶ N]` twin elsewhere in the text. Inspection showed the **whole opinion body stored twice**: frontmatter + `## Opinion` #1 + a clean analyzer copy (contiguous `[¶1..N]`, no star pagination) + `## Opinion` #2 + a CL/NW2d OCR copy (star pagination, letter-OCR'd markers, digit-flipped marker numbers, occasionally transposed blocks) — the 13240 *Johnson* class at scale. A corpus sweep (marker-sequence restart at ¶1, or doubled `## Opinion` headers) found **563 candidates**, far beyond the 31 marker-flagged ones.

**Surgery: truncate at the second `## Opinion`** (drop the OCR copy), gated four ways: exactly two `## Opinion` headers; the kept copy contiguous `¶1..N` with zero letter-OCR markers; kept max == doc max; **shingle-jaccard(copy1, copy2) ≥ 0.5** so an appended *rehearing/companion* (legitimately distinct content, the Watford class) can never be deleted — no candidate failed the jaccard gate. Applied: **23** (first pass, strict gates) + **4** manual-gate (copy2 marker numbers digit-flipped: `28`=23, `80`=30, `67`=57) + **522** (corpus batch) = **549 opinions**; on-disk markdown updated in step; full old text stored per row in `changelog` (revertible). Tools `triage/dedup_storedtwice{,_batch}_2026-06-09.py`.

**Effect:** `para_continuity` flags 1,818→**1,269**; `xref_resolve` 847→**815** and `text_citations` 334,169→**333,845** (junk cites in the dropped OCR copies are gone); `parallel_pair` 608→**598**; `cited_by` stable (114,279). Citation graph rebuilt; invariants **23 ok / 2 known / 0 regressed**. **41 held** (`triage/storedtwice-held-2026-06-09.tsv`): 28 kept-copy-max failures (mostly corrupted copy-2 marker numbers needing the manual gate), 10 non-contiguous first copies, 3 restart-without-headers formats — queued. Note the sweep keys on `[¶N]` markers and `## Opinion` headers, so pre-1997 texts (no markers) are NOT covered — a shingle-self-similarity detector (audit #6 proper) remains the general answer.

## Batches `fix-herrick-12500` / `para-marker-ocr-letters-2026-06-09` — Herrick row repair + letter-OCR'd ¶ markers

**`fix-herrick-12500-2026-06-09`** — oid 12500 (flagged by the `detect_overruled_in_draft` build 2026-05-24, confirmed live): `case_name` *Longtine v. Yeado* → **State v. Herrick** (text/title_full/cites are Herrick, 1997 ND 155, 567 N.W.2d 336; the real Longtine is oid 12507 = 1997 ND 166); `author` Maring → **VandeWalle** (body byline "VANDE WALLE, Chief Justice."; Maring merely concurred at ¶29); `docket_number` `1997ND155` (the cite, not a docket) → `19970019, 19970020, 19970021` (frontmatter "Criminal 970019-970021", consolidated, comma-join convention). **Surfaced a systemic sibling: 199 opinions carry cite-shaped docket_number values (`YYYYNDn`; 159 from 1997)** — queued in TODO-audit.md.

**`para-marker-ocr-letters-2026-06-09`** — **130 body ¶ markers in 124 opinions** recovered from letter-OCR corruption: `[IF n]`/`[If n]`/`[lf n]`/`[1f n]` → `[¶ n]` (the Ertelt `[IF 2]` class; same scraper-OCR family as the digit flips). Gate: the recovered number must fill a gap in the opinion's `[¶N]` sequence; the document's own marker spacing style preserved; source markdown patched in step. `para_continuity` GAPs 1,297→1,239. **31 held** — their `[If N]` instance has a `[¶ N]` twin elsewhere in the text because the opinion body is **stored twice** (one clean copy + one OCR copy, the 13240 Johnson class) — seeded as the body-duplication queue in TODO-audit.md. Tool `triage/fix_if_markers_2026-06-09.py`.

Also promoted the parallel-pair consistency scan to a permanent check (`audit_corpus.check_parallel_pair`, court typos baselined in `_KNOWN_COURT_PAIRS`; reads 608 = the enumerated held queues). Invariants 23/2/0.

## Batch `parallel-backfill-witnessed-2026-06-09` — N.W.2d/3d parallel-cite backfill from citing-opinion witnesses (DB_NO_PARALLEL queue)

Follow-on to the digit-flip work below: the parallel-pair scan's `DB_NO_PARALLEL` class (2,171 pairs) = opinions whose `citations` row carries **no N.W. parallel** while the court's later opinions print one. Grouped into 646 distinct (neutral, N.W.) candidates and gated (`triage/backfill_parallels_build_2026-06-09.py`): ≥2 independent citing-opinion witnesses, no conflicting claim, and date/volume coherence — **tier 1** (246 adds) by the N.W. volume's corpus date window; **tier 2** (141 adds) for volumes wholly absent from the corpus, by volume-sequence interpolation (nearest known volumes must bracket the target's date — this gate correctly rejected the one garbage cite `003 N.W.3d 122`). **387 N.W.2d/3d parallels added** (additive only, `is_primary=0`; ~25 are shared summary-disposition **table pages** — e.g. eight 2015 summary dispositions legitimately share `861 N.W.2d 172` — noted per row in the authority string).

**Effect:** parallel-pair mismatches 2,455 → **610** (consistency 98.9%); `cited_by` 114,224→**114,278** (+54 newly resolvable edges); shared-page collisions 856→888 (the new table-page cites await §6 antecedent disambiguation — expected). Citation graph rebuilt; invariants **23 ok / 2 known / 0 regressed**. **Held for later verification** (`triage/backfill-parallel-candidates-2026-06-09.tsv`): 125 single-witness candidates (need CL/Westlaw — one witness could itself carry a digit flip), 24 volume-window failures, 20 conflicting claims.

## Batches `citeflip-surgical{,-oddballs,-residual}` / `pincite-surgical` / `reextract-pdfminer-15762` / `parallel-add-witnessed-2026-06-09` — OCR digit-flip citation corruption (the pinpoint-queue root cause)

The new `audit_corpus` **pinpoint_range** check (59 flags: a cite to `YYYY ND n, ¶ P` where our copy of that opinion has max ¶ < P) root-caused to a previously invisible OCR class: **digit substitution (3↔8, 5↔6, 6↔9) in analyzer-era opinion texts** — same scraper-OCR origin as the `■`/`„` artifacts fixed 2026-06-09, but digit flips leave no artifact characters, so the artifact cleanup could not see them. Scoped corpus-wide with a **parallel-pair consistency scan** (`triage/parallel_pair_scan_2026-06-09.py`: a neutral cite and its adjacent N.W.2d/3d parallel inside one citation string must resolve to the same opinion — 57,749 pairs checked, 2,831 mismatched), then classified by digit-edit distance and **verified against the citing opinion's court PDF** (corrected cite present, corrupted absent — `triage/verify_flips_pdf_2026-06-09.py`).

**Text corrections (citing-side, all changelog-revertible; on-disk source markdown patched in step so a future full re-ingest doesn't resurrect the corruption):**
- `citeflip-surgical-2026-06-09` — **295 cite corrections across 260 opinions** (80 markdown files), every one PDF-verified (e.g. *Haugland II* citing Haugland I as `2012 ND 128` for **123**; `2018 ND 252` for **2013** ND 252 [Nguyen]; flips in both neutral and N.W.2d components).
- `pincite-surgical-2026-06-09` — **6 pincite digit flips** (`¶ 88`→`¶ 33`, `¶ 87`→`¶ 37`, …), each verified against the citing PDF's printed pincite (`triage/pincite_direction_2026-06-09.py`).
- `citeflip-surgical-oddballs-2026-06-09` — **5 per-item fixes** where the PDF was silent (prints no parallel) or image-OCR: verified by the named case's true parallel + era-impossibility (a 1998 opinion cannot cite `670 N.W.2d`; `599 N.W.3d 323` cannot exist in 1999).
- `citeflip-surgical-residual-2026-06-09` — **4 double-flip strings** (year+page corrupted together): Linser `2008 ND 195, … 672 N.W.2d 648`→`2003 ND 195, … 643`; Estate of Nelson `2016 ND 122, … 863 N.W.2d 621`→`2015 ND 122, … 521`; State v. Syvertson `1999 ND 187, … 697 N.W.2d 644`→`1999 ND 137, … 597`; Interest of J.S.L. `2009 ND 48, … 768 N.W.2d 783`→`2009 ND 43, … 763` — each PDF-verified or double-convergent on one real case.
- `reextract-pdfminer-15762-2026-06-09` — *State v. Mittleider*, 2011 ND 242: CL-format body had ¶ markers OCR'd as digits (`[118]` = `[¶18]`), star pagination, `MeCLINTOCK`; pdfminer re-extract from the court PDF recovered the full contiguous ¶1–20 (our copy had appeared to stop at ¶13 — five independent opinions legitimately cite ¶14).

**Three genuine court typos found and preserved verbatim** (the court's own PDF prints them; `feedback_preserve_source_typos`): oid 16446 "Jaste v. Gailfus, **2004 ND 87**, ¶ 18" (Jaste is 2004 ND 94; baselined in `audit_corpus._KNOWN_COURT_PINCITES`); oid 14127 *Muhammed* `674 N.W.2d 402` in one instance (675 in another); oid 16894 *Pace* `716 N.W.2d 535` once (713 twice).

**Cited-side discovery (`parallel-add-witnessed-2026-06-09`):** the "PDF has the 'bad' cite" bucket decomposed into **cross-wired/missing parallels on same-day sibling pairs** — e.g. `924 N.W.2d 87` sat on *State v. Gomez* (2019 ND 59) while **16 independent court opinions** print it as *Brewer v. State*'s (2019 ND 69) parallel. **Added 14 witness-attested N.W.2d parallels** to opinions that had no N.W. parallel at all (≥2 independent citing-opinion witnesses, zero witnesses pairing the current holder; additive only — the current holders keep their rows pending per-item verification, since same-page sharing is legitimate). Witness analysis: `triage/class3_witnesses_2026-06-09.py` → `triage/class3-clusters-2026-06-09.tsv`.

**Citation graph rebuilt** (twice, after the text fixes): `text_citations` 334,339→**334,170**, `cited_by` 114,389→**114,224**, unresolved collisions 871→**856** — the corrected cites now resolve to the right opinions. Invariants **23 ok / 2 known / 0 regressed**; `pinpoint_range` **59→0**; `cite_temporal` 0. Snapshot `opinions.db.bak-pre-citeflip-fixes-2026-06-09.zst`.

**Open follow-ups (TODO-audit.md):** ~25 mixed/single-witness parallel clusters need per-item verification (incl. the `622 N.W.2d 432` three-claimant tangle — *Lee* 2000 ND 215 header vs *Matrix* 2000 ND 213 witnesses vs *Syvertson* 2000 ND 211 current holder — and *Chinquist*/*Jaste* sharing `679 N.W.2d 257`); **2,173 `DB_NO_PARALLEL` pairs** = parallel-cite backfill opportunity (citing opinions print parallels our DB lacks); 242 `OTHER` mismatches to sample; promote the parallel-pair scan to a permanent `audit_corpus` check.

## Batch `citegraph-rebuild-2026-06-09` — full-corpus rebuild of text_citations + cited_by after the OCR/consolidation text replacements (§14)

Follow-up deferred from the 2026-06-09 OCR cleanup. That work replaced the **whole `text_content` body** of ~100 opinions — pdfminer re-extracts ×71 + garbled re-extracts ×21 (`ocr-reextract-pdfminer/garbled-2026-06-09`), marker re-OCR ×2 (`para-markers-reocr-2026-06-09`), and the 5 consolidation merges + 2 dedups (Nestos, Lincoln, Chester, Druey, Altenbrun, Coman, McIntyre) whose text was concatenated or repointed — leaving their citation-graph edges stale. **Rebuilt the entire graph from scratch against the current cleaned text + current jetcite (2.3.0)**, same method as `citegraph-rebuild-2026-06-01`: snapshot → `DELETE FROM text_citations / cited_by / cite_extract_progress` + `VACUUM` → `python -m ndcourts_mcp.cite_extract` (full scan, all 19,793 opinions, ~216 op/s; `cited_by` built inline with `antecedent_name` + citer-date shared-page disambiguation).

**Before → after:** `text_citations` 335,747 → **334,339** (−1,408, −0.4%); `cited_by` 114,446 → **114,389**; `jurisdiction='nd'` 225,635 → 224,824. The small net decline is expected — the ~840 surgical artifact strips and clean re-extracted bodies removed OCR junk that previously parsed as spurious cites, and the consolidation merges collapsed duplicate rows; nothing like the red-flag large drop the validation plan warned about. Validation: `cited_by` self-edges = **0**, every `cited_by` edge has a matching `text_citations` row (forward/reverse fully consistent), top-cited unchanged (*Power Fuels, Inc. v. Elkin*, 219 inbound). **871 shared-page collisions** unattributable (no antecedent-name match) skipped and logged to `triage/cited-by-unresolved-collisions.csv` for the §6 disambiguation pass (was 922 on 06-01).

Wholesale regeneration of derived tables (not per-row judgment corrections) → **snapshot-reversible**: `opinions.db.bak-pre-citegraph-rebuild-2026-06-09` (pre-counts tc=335,747/cb=114,446) with this narrative as the audit trail. Provenance row logged via `cite_extract.log_provenance`. Invariants 23 ok / 2 known / 0 regressed.

## Batches `nd-consolidate-{state,lincoln,chester}` / `dedup-{coman,mcintyre}-2026-06-09` — resolve the 5 N.D. Reports consolidation candidates (Law Library page images)

The ND Supreme Court Law Library (P. Amelsberg) supplied bound N.D. Reports + N.W. page images for the 5 candidates left in TODO §15. Reviewed each against the authoritative N.D. Reports page; **13 images filed** (`nd-images-paula-2026-06-09`): N.D. pages under `N.D./<vol>/<page>-slug.pdf` (`ND-image`), N.W./N.W.2d under `NW/<vol>/<page>.pdf` (`NW-image`), registered on the survivor rows.

**3 consolidations** (one appeal, opinions printed together in the N.D. Reports → one record; per the 2026-06-09 policy):
- **Nestos, 48 N.D. 894** (`nd-consolidate-state-2026-06-09` — the merge tooling slugged the batch from the caption's first word, *State ex rel. Bauer v. Nestos*): bound vol pp.903–904 print the main (Christianson, J.) and the per-curiam rehearing-denied together. Merged 20389→**2635**; parallels `187 N.W. 233` + `187 N.W. 619`; freed synthetic dropped.
- **Lincoln Addition v. Lenhart, 50 N.D. 25** (`nd-consolidate-lincoln`): caption reads "(195 N.W. 14, 33.)"; Robinson's special concurrence (195 N.W. 33) printed at the end of the report (pp.29–30) before *Baker v. Lenhart*. Merged 20390→**2863**; parallels `195 N.W. 14` + `195 N.W. 33`. **Author corrected** Birdzell→**Bronson** (the bound volume shows BRONSON, J. wrote the main; Birdzell merely concurred).
- **Chester v. Einarson, 76 N.D. 205** (`nd-consolidate-chester`): main + on-rehearing, both Gronna, J. Merged 20391→**9128**; parallels `34 N.W.2d 418` + `35 N.W.2d 137`.

**2 dedups** (bound volume shows a single opinion; the second DB row is a CourtListener double-ingest date-twin):
- **State v. Coman, 68 N.D. 310** (`dedup-coman`): bound vol shows ONE opinion (Christianson, Ch.J., filed **Apr 11, 1938**, governed by *State v. Young*). Merged the Apr-14 twin 4828→**4829**.
- **Weiss v. Stormon / In re McIntyre's Estate, 78 N.D. 10** (`dedup-mcintyre`): bound vol shows ONE **PER CURIAM** opinion, filed **May 7, 1951**. Merged the Apr-13 "In re McIntyre's Estate" twin 10881→**10882**; set `per_curiam=1`, cleared author (reporter shows no individual author). This closes the 3rd "ambiguous" from `westlaw-receive-2026-06-08`.

Each merge: `merge_pair` (edge repoint + delete) + text concatenation (merges) / survivor text kept (dedups), `(Mem)` suffix normalized, freed synthetic dropped, self-cite `text_citations` cleaned (§14b), `source_reporter`/`source_path`/`is_primary` aligned to the markdown text origin. Pre-batch snapshot; per-row changelog + provenance. Invariants 23 ok / 2 known / 0 regressed. **TODO §15 consolidation queue fully closed.**

**Satellite bookkeeping batches** (same session, small row counts — named here so every changelog batch has a narrative): `dedup-cleanup-2026-06-09` (dropped the freed duplicate synthetics `1938 ND 31` [Coman 4829] and `1951 ND 15` [Weiss/McIntyre 10882] + aligned 10882's source_path); `consolidate-cleanup-2026-06-09` (Chester 9128 source_path → the consolidated `N.D./76/0205` `.doc`); `primary-source-fix-2026-06-09` then `primary-source-align-2026-06-09` (two-step settling of the survivors' primary-source convention — first pointed Nestos/Lincoln/Coman at the authoritative `.doc` text, then re-aligned all five survivors' `source_reporter`/`source_path` to the markdown text-content origin; the **align** batch is the final state).

## Batches `ocr-artifact-surgical/reextract-pdfminer/reextract-garbled-2026-06-09` — fix the 926 modern OCR-flagged opinions from their court PDFs

The 926 OCR-flagged 1997+ `source='ND'` opinions carried `■`/`„`/`¡`/`¿`/`£` artifacts. Root cause: an **OCR pass** during original scraping (not pdfminer) baked garbage into the stored text (e.g. `[¶ IQ]` for `[¶ 10]`, missing `[¶8]`). The court PDFs are clean — fresh **pdfminer** re-extraction yields zero artifacts and complete `[¶1..N]` sequences. Scoped all 926 (`triage/pdf-reextract-scope.tsv`): **915 fixable from the PDF, 11 need marker OCR** (9 broken-pilcrow-font ¶-gaps + 2 image-only PDFs). Two-track fix by current body format:

- **Track B — surgical (823, `ocr-artifact-surgical-2026-06-09`):** archive/CL-format opinions (clean text, isolated artifacts). Mechanical in-place repair preserving the cleaner archive text: `■`/`¡` spurious char → space (newline-aware), `JJ„`/`J„` → `JJ.,`/`J.,` (OCR of the justice-block `.,`). 823 became fully artifact-free; the 21 with `¿`/`£` (garbled *letters*, not stray marks) were deferred to re-extract.
- **Track A — pdfminer re-extract (71, `ocr-reextract-pdfminer-2026-06-09`):** PDF-format opinions already pdfminer-derived + pervasively corrupted (artifacts at hyphenation/column joins). Body replaced with fresh pdfminer text (frontmatter + rebuilt `# Title/court/cites/Decided` header preserved); validated artifacts==0 and contiguous `[¶1..N]`.
- **Garbled re-extract (21, `ocr-reextract-garbled-2026-06-09`):** the archive-format opinions whose `¿`/`£` were garbled letters (`¿`=a/e, `£`=f/t/¶/[) — re-extracted from the PDF for correct text.

**Outcome:** corpus total OCR-artifact chars **1,480 → 45**; flagged opinions **939 → 22** (the 22 = 11 marker-OCR candidates + 11 pre-1953 NW/westlaw-sourced opinions out of scope for this PDF-era batch).

**Marker-candidate resolution (2026-06-09, batches `ocr-artifact-surgical-markercand` + `para-markers-reocr-2026-06-09`):** ran `marker --force_ocr` on the 11 candidates and validated each (`para_markers_lib.normalize_marker_md`, ¶-sequence + jaccard). Outcome split: **2 image-only PDFs** (1997 ND 58, 2011 ND 107 — pdfminer extracted only form-feeds) recovered cleanly by marker (complete `[¶1..N]`, 0 artifacts) → adopted. The other **9** (the broken-pilcrow ¶-gap set): marker actually produced a *less* complete ¶ sequence than the already-stored text (e.g. 1998 ND 24 — current has ¶1–40+, marker dropped 11), because those opinions' **current stored text is fine except for 1–2 stray `■`/`„` chars** (the fresh-pdfminer ¶-gaps that triggered the marker route were a pilcrow-font decode failure, not a defect in the stored text). So marker was rejected for the 9; **surgical artifact removal** on the current text fixed them instead. **Now 0 modern (1997+) opinions flagged**; corpus artifacts **45 → 33**, flagged **22 → 11** (all 11 remaining are pre-1953 NW/westlaw — separate residual). Invariants 23/2/0.

**Pre-1953 residual cleared (2026-06-09, batch `ocr-artifact-pre1953-2026-06-09`):** the last 11 flagged opinions (all pre-1953 NW/westlaw/NW2d CL-OCR) fixed with context-aware surgical edits — `£`→`$` in dollar amounts (mis-OCR; e.g. *Schlosser* 16 N.D. 185 "£700"→"$700", *Wells-Stone* 7 N.D. 460 "£>>>>4,000"→"$4,000"), `■` resolved by context (word-join "thereto■fore"→"theretofore", hyphenation "peti- ■ tioner"→"petitioner", else→space), `¡`→space. Each spot-checked. **Corpus OCR-artifact chars now 0; 0 opinions flagged.** Invariants 23/2/0. The OCR-artifact cleanup (begun at 1,171 flagged) is COMPLETE. 915 `text_content` replaced/repaired + matching `markdown/<year>/<cite>.md` rewritten; per-row changelog + provenance; pre-batch snapshots. Invariants 23 ok / 2 known / 0 regressed after each. **Follow-up:** the 92 wholesale-re-extracted bodies (Track A + garbled) changed enough to warrant a `cite_extract` refresh of their citation-graph edges (TODO §14); the 11 marker-OCR candidates pending (TODO §8).

## Batch `emmons-gauger-namefix-2026-06-09` — Emmons County tax-foreclosure cluster verified; one OCR name fix

Investigated the 9 N.D. 608–615 *Emmons County v. …* cluster (flagged in the shared-N.D.-cite audit as a possible duplicate mess). Censused the bound N.D. Reports vol 9 (PDF 708–725) against the DB: the **20 per-curiam per-parcel tax-foreclosure memoranda** (all 1900-11-13, disposing by reference to the lead *Emmons Co. v. Thompson*, 9 N.D. 598) **match the bound volume exactly** — 2–3 short memoranda per N.D. page (608: Cranmer, Davidson; 609: Davidson, Baker, Couch; 610: Cranmer, Gauger, Kelly; 611: Lilly, McKenzie, McKenzie; 612: McKenzie, McLain, Mellon; 613: Mellon, Mellon, Robinson; 614: Thistlewaite, Thistlewaite; 615: Wilson). They are **distinct appeals**, not duplicates (same-defendant repeats = separate parcels), already correctly modeled as separate records with N.D.-page primary cites and synthetic cites **1900 ND 66–85 in exact reporter order**. **No dedup or page corrections needed** — the audit's duplicate suspicion was a page-offset misread. Sole fix: OCR'd defendant **`Ganger` → `Gauger`** (Harry Gauger; oid 20493, case_name + frontmatter), confirmed against bound vol 9 p.610 at 250 dpi. Invariants 23/2/0.

## Batches `nd-consolidate-druey-2026-06-09` / `nd-consolidate-altenbrun-2026-06-09` — consolidate same-appeal opinions published together in the N.D. Reports

New consolidation policy (the **official N.D. Reports volume governs**): when one appeal's opinions (majority + separate/concurring/rehearing) are printed **together under one N.D. page**, they are **one record**; separate N.W.-series publications become **parallel cites**. Two distinct *appeals* (each its own judgment/notice of appeal), even if printed on the same N.D. page, remain **two records**. Verified against the bound N.D. volumes (`N.D./<vol>/_bound-volume.pdf`); N.W. page images and Westlaw `.docs` are corroborating witnesses. Full audit of all 43 shared-N.D.-cite groups in `triage/nd-consolidation-audit-2026-06-09.md`.

- **Druey v. Baldwin, 41 N.D. 473** (`nd-consolidate-druey-2026-06-09`): merged 20387 (Robinson, J. separate opinion, 182 N.W. 700) into **2125** (Bronson, J. majority, 172 N.W. 663). Bound vol 41 p.473–477 prints them together (Robinson's opinion follows Grace's concurrence-in-result). `merge_pair` re-pointed all edges + deleted 20387; then text_content set to the clean Westlaw Bronson opinion **concatenated** with Robinson's opinion (cleared the OCR flag, 16,378 chars); citations = `41 N.D. 473`(primary) · `172 N.W. 663` · `182 N.W. 700` · `1919 ND 13`; freed synthetic `1919 ND 14` deleted; judges → `Birdzell, Bronson, Christianson, Grace, Robinson`; 3 stale self-cite `text_citations` (Robinson's "For main opinion, see…" cross-ref) dropped (§14b).
- **Altenbrun v. First National Bank of Rock Lake, 47 N.D. 266** (`nd-consolidate-altenbrun-2026-06-09`): merged 20388 (Christianson, J. concurrence, 181 N.W. 908) into **2473** (Robinson, J. opinion, 181 N.W. 590). Bound vol 47 p.266–274 prints the concurrence within the report (p.272). 2473's CL text already contained both opinions; `merge_pair` deleted the redundant 20388; citations = `47 N.D. 266`(primary) · `181 N.W. 590` · `181 N.W. 908` · `1921 ND 17`; freed `1921 ND 18` deleted; judges OCR fixed (`Biedzbbb`→`Birdzell`); 2 self-cites dropped. **Body remains CL-OCR** (letter-level errors in the Robinson opinion) — pending Westlaw upgrade of `181 N.W. 590` (TODO §15). **UPGRADED 2026-06-09** (`altenbrun-westlaw-upgrade-2026-06-09`): user supplied the `181 N.W. 590` Westlaw `.doc` + N.W. page image; installed clean authoritative text on 2473 (Robinson C.J. main + Grace concurs + Bronson concurring specially [all 181 N.W. 590] + Christianson concurring specially [181 N.W. 908]), source_reporter→westlaw, filed `NW/181/590.pdf` + archived the `.doc`. Surfaced a **date discrepancy**: both primary sources read *Jan. 24, 1921* vs. the DB's CL-sourced `1921-01-28` — **corrected same day** (`altenbrun-date-fix-2026-06-09`): 2473 `date_filed` → `1921-01-24` (two concurring primary authorities — reporter image + Westlaw `.doc` — over CL metadata; changelog-revertible).

Both reversible (`cleanup revert <batch>`); pre-batch DB snapshots taken. Invariants 23 ok / 2 known / 0 regressed after each (one transient `no_self_citation` regression per merge, fixed by dropping the cross-reference self-cites). **Willis, 18 N.D. 76** was checked against bound vol 18 (p.81) and **kept as two records** — the memo is a *separate appeal* (own "Appeal from District Court" caption), not a separate opinion in one appeal. **Page-image registrations:** `nw-image-druey-2026-06-09` (West N.W. Reporter images `NW/172/663.pdf` + `NW/182/700.pdf` as `NW-image` sources on 2125) and `nw-image-willis-2026-06-09` (`NW/118/820.pdf` on 458, `NW/118/823.pdf` on 20386 — the witnesses behind the keep-two ruling).

## Batch `westlaw-receive-2026-06-08` — promote Westlaw bound text over CL OCR for 239 OCR-flagged opinions

OCR cross-check pull. The quality scan flagged 1,171 opinions carrying OCR-artifact characters (`¡¿■£„`). 220 were pre-1953 opinions whose `text_content` is CourtListener's OCR of the N.W. reporters (no born-digital court PDF behind them) and 18 were 1997 opinions that pre-date the PDF scraper — for these, the Westlaw bound text is the better authority. Pulled all 251 from Westlaw Find & Print (four batches: 100/100/45/6 items) and ingested via `python -m ndcourts_mcp.receive_westlaw --incoming ~/refs/nd/opin/westlaw-incoming/2026-06-08 --apply`.

**Result:** **239 promoted** (Westlaw text → primary, `source_reporter='westlaw'`, archived to `N.W./{vol}/` (221, 1st series) and `N.W.2d/{vol}/` (18); `validation_status='corrected'`), **2 duplicates dropped**, **2 out-of-state skipped**, **3 ambiguous deferred**, **5 parse-fails** (all out-of-state). 717 changelog rows (239 × text_content/source_reporter/source_path), provenance logged. Post-scan OCR-flagged count 1,171 → **939** (the remainder are modern born-digital opinions whose `■`/`„` are PDF→markdown conversion artifacts, to be fixed from the local court PDFs, not Westlaw).

**Three pipeline fixes were required** (`receive_westlaw.py`) — the tool was built for the 1953–65 N.W.2d gap era and this was the first pre-1900 / N.D.-Reports-primary batch:
- **N.W.-cite archive fallback** (`_db_nw_cite`): pre-1953 Westlaw docs lead with the N.D. Reports cite ("9 N.D. 538") and carry no N.W. cite in the header, so `_archive_doc` declined all 221 with `NO_ARCHIVE_PATH`. For a resolved match, fall back to the matched DB row's N.W. parallel cite to build the archive path.
- **Out-of-state CREATE guard** (`_FOREIGN_COURT`): shared N.W. reporter pages return foreign-state opinions under a pulled cite (e.g. 50 N.W. 969 → both *Gould v. Duluth*, 2 N.D. 216 **and** the Iowa *State v. Hays*). The base parser leaves a foreign court header in `case_name` ("Supreme Court of Iowa. …"); refuse to create such rows. Caught 2 Iowa *Hays* copies.
- **Duplicate vs. companion discrimination** (RECONCILE): when several docs resolve to one existing row, the loser was always demoted to CREATE as a "shared-page companion." When the user re-queues a shared-page cite by its N.D. parallel (here *Vidger v. Nolin* 10 N.D. 353 and *Edwards & McCulloch* 3 N.D. 170, each pulled twice), the loser is the **same opinion** and would have created a duplicate row. Now discriminated by text Jaccard (≥0.90 vs. the winner = same opinion → drop; distinct text → genuine companion → create).

Promote-similarity floor unchanged (Jaccard ≥ 0.20 vs. prior text); the 239 ran 0.49–0.95 (median 0.85). Low values are the heavily-garbled OCR rows — the highest-value replacements. Reversible: `python -m ndcourts_mcp.cleanup revert westlaw-receive-2026-06-08`. Invariants 23 ok / 2 known / 0 regressed.

**Open follow-ups:** 3 AMBIGUOUS (18 N.D. 76 *State ex rel. City of Minot v. Willis*, 41 N.D. 473 *Druey v. Baldwin*, 78 N.D. 10 *In re McIntyre's Estate*) need manual cite/party disambiguation; the ~925 modern OCR-flagged opinions await a fix-from-local-PDF pass (`triage/westlaw-receive-2026-06-08.tsv` has the full per-doc disposition).

## Batch `backfill-gov-urls-2026-06-06` — backfill ndcourts.gov `opinion_url` for 1997+ opinions missing one

`opinion_url` (the court's own ndcourts.gov page) is the official-source URL now preferred over the CourtListener `absolute_url` fallback by the new `server._best_url` helper. **26** opinions filed 1997+ had no `opinion_url` (the merge only sets it when the scraper JSON carried one; these were captured with `opinion_url=None` or had no JSON record). **Backfilled 14**, fetched live from ndcourts.gov's citation-addressable opinion search (`cit1=<year>&citType=ND&cit2=<num>`, via the scraper's Cloudflare-bypass `nd_get`) by `scripts/backfill_gov_urls.py`. `authority` = ndcourts.gov citation search; `old_value=NULL`; changelog-revertible.

Each write is gated on a **numeric cite match** of the returned row, never a "take the single result" guess — the search proved unreliable (intermittently returns an unrelated row; zero-pads some cites, e.g. `2021 ND 0216`, so `cit2=216` misses — handled by padded retry + numeric match). That guard caught two would-be mis-writes: **docket-sharing siblings** where the court's by-docket page belongs to the *other* row — docket 990130 *Webster v. Regan* `2000 ND 18` (oid 13074) vs `2000 ND 89` (oid 13136); docket 970363 *Neset* discipline `1997 ND 215` (oid 12581) vs `1998 ND 206` (oid 12782). Both siblings are legitimately distinct opinions (original + rehearing/later proceeding); the targets correctly keep the CL fallback, not their sibling's URL.

**12 left without a gov URL** (all correct): the 2 docket-siblings above; 7 early/special matters absent from the court's online opinion DB by both cite and docket (`1997 ND 1`, `1997 ND 5`, `1998 ND 22`, `1998 ND 171`, `2003 ND 39`, `2017 ND 234`, `2022 ND 69`); and 3 Court of Appeals cases with no neutral cite to search by (Ernst v. Tjon, In re N.B., In re K.N.H.). No DB cites were changed.

## Batch `citegraph-rebuild-2026-06-01` — full-corpus rebuild of text_citations + cited_by (§6 / TODO #6)

Priority TODO #6. The citation graph had been built incrementally over many ingest cycles and then patched in place (§14 self-cite strip, jurisdiction backfill, truncation-phantom strip) and re-extracted for only the 57 para-marker re-OCR opinions whose `text_content` was wholly replaced. **Rebuilt the entire graph from scratch against the current cleaned text + current jetcite (2.1.2)** so the forward (`text_citations` / `get_cited_authorities`) and reverse (`cited_by` / `get_citing_opinions`) indexes are uniformly derived from one source of truth.

**Method:** snapshot → `DELETE FROM text_citations / cited_by / cite_extract_progress` + `VACUUM` → `python -m ndcourts_mcp.cite_extract` (full scan, all 19,792 opinions, ~70s at ~284 op/s). The in-scan build reproduces every §14 guard from code rather than trusting the prior in-place edits: self-cites unique to an opinion are skipped at insert (§14b), a case cite resolving into this ND-only corpus is stored `jurisdiction='nd'` (§14f), and current jetcite no longer emits the old reporter-truncation phantoms (§14c). `cited_by` is built inline with the same `antecedent_name` + citer-date shared-page disambiguation as `--cited-by-only`.

**Before → after:** `text_citations` 307,438 → **335,538**; `cited_by` 108,242 → **114,376**; `jurisdiction='nd'` 215,954 → 225,635. The +28k text_citations is **more-complete extraction by jetcite 2.1.2** (not reintroduced junk), confirmed by validation: unique-to-opinion self-cites = **0** (§14b reproduced), `cited_by` self-edges = **0**, reporter-truncation phantoms 1,650(pre-§14)→**12** (genuine first-series cites, not artifacts), and **0** `cited_by` edges lack a matching `text_citation` row (forward/reverse fully consistent). Top-cited opinion *Power Fuels, Inc. v. Elkin* (219 inbound). **922 shared-page collisions** could not be attributed to a single cited opinion (no antecedent name match) and were skipped, logged to `triage/cited-by-unresolved-collisions.csv` for the §6 disambiguation pass.

This is a wholesale regeneration of derived tables (not a per-row judgment correction), so it is **snapshot-reversible** — `opinions.db.bak-pre-citegraph-rebuild-2026-06-01.zst` (388M, quick_check ok, pre-counts tc=307,438/cb=108,242) with this narrative as the audit trail — rather than ~335k per-row changelog entries. Provenance row logged via `cite_extract.log_provenance`. Invariants 23 ok / 2 known / 0 regressed; `no_self_citation` OK.

**Note — separate open item (#3 / §14a):** this rebuild fixes the *data*; the report that `get_cited_authorities` lists parallel cites twice is a **tool-layer** missing-`oid`-dedup defect, addressed under TODO #3, not here.

## Batch `fix-author-courtreport-byline-2026-06-01` — author corrections cross-checked against the court's official report (§5)

Priority TODO #5, first apply. The ND Supreme Court's own cTrack export `input-data/court-opinions-report-2026-05-30.xlsx` (12,329 opinions, ~1965–present) was joined to the DB by citation (ND-neutral → N.W.2d/N.W.3d → docket) — 11,444 matched 1:1 — and every field diffed (`triage/section5_court_report_diff_2026-06-01.py`, report under `triage/s5-report-diff-2026-06-01/`). The author column surfaced **425 disagreements**, of which **298 are the no-op `Gierke → Gierke III`** (DB keeps the surname-only convention — "Gierke" is unambiguous; the report's generational suffix is a style variant, not a correction) and 32 lacked a body byline or were ambiguous (deferred).

**Applied 104 author corrections** (two passes: 95, then +9 after the normalization fix below), each **triple-verified**: the court's official report AND the opinion-body byline ("Opinion of the Court by X", re-derived directly from `text_content`, not trusted from the diff) BOTH name a different justice than `opinions.author`. Two independent authorities agreeing against the DB clears the data-correction-verification bar without bulk-heuristic risk. **~64 were mis-attributed to "Erickstad"** (the gap-era ingest's apparent default to the then-Chief Justice; e.g. Erickstad→Paulson, →Strutz, →Teigen); the rest scattered (VandeWalle→Meschke, Burke→Strutz, Strutz→Jansonius, …). 0 had `per_curiam=1`. `authority` = report + body byline. Invariants 23/2/0.

**Normalization fix mid-run:** the report **zero-pads N.W. page numbers** (`154NW2d055`); the DB stores them bare (`154 N.W.2d 55`), so the first matcher silently missed every N.W. cite with a page <100. Stripping leading zeros (`int(page)`) lifted 1:1 matches **11,444 → 11,965** and dropped unmatched **799 → 270**, then surfaced the +9 authors / +26 dates re-applied in the second pass.

## Batch `fix-date-courtreport-le31d-pre1997-2026-06-01` — pre-1997 filing-date corrections from the court report (§5)

Priority TODO #5, same diff run. **Applied 179 `date_filed` corrections** (two passes: 153, then +26 after the zero-pad normalization fix), all pre-1997, where the report's "Filing Date" (the court's own record) differs from the DB date (sourced from CourtListener for this era) by ≤31 days. Per the ratified date policy (2026-05-24): for ≤31d disagreements the **court's filing date governs**. The overwhelming majority are exactly −1 day — CourtListener systematically recorded the day after the court's filing date for the cTrack era. `authority` = court report Filing Date. Invariants 23/2/0.

The **modern (1997+) date diffs and pre-1997 >31d holds (~101 total) were deliberately held** — the modern set is dominated by amended/substitute/on-remand opinions (e.g. the Birchfield/Beylund/Wojahn remands, multi-date orders) where the report's later date and the DB's original-filing date may both be legitimate, and the >31d band needs the N.W.2d volume-window arbiter (2026-05-25 refinement).

**Unmatched-rows finding (no corpus gap):** of the 270 report rows that matched no DB opinion by cite, **31 are Court of Appeals `ND App` cites**, ~36 are in the DB by name+date with a cite to reconcile, and **197 have no name match — but those 197 collapse to just 32 distinct N.W.2d pages** (one page shared by up to 13 unrelated cases), i.e. they are N.W.2d **"Decisions Without Published Opinion" table entries** (summary dispositions under N.D.R.App.P. 35.1, concentrated 1986–96), not published opinions, and are correctly absent. Only **2 single-page rows + 2 recent (2025) confidential adoption matters with no assigned cite** warrant a manual check. Net: **no evidence of missing published opinions.** Author no-byline residue (~25), the `case_name` (1,808) / cite-mismatch (36) / COA (31) buckets, and `Nature Of Action`→`case_type` mapping remain open §5 work.

## Batch `para-markers-reocr-2026-05-30` — recover missing body paragraph markers via marker re-OCR

Priority TODO #4. **57 full post-1997 authored opinions carried no `[¶N]` body paragraph markers** — their court PDFs embed the pilcrow `¶` in a font with a broken ToUnicode map, so every text extractor mis-decodes it (`[¶21]`→`[t4]`/`[$\P$ 21]`/`[$\quad 25$]`/`[928]`), and the analyzer recorded zero markers. Fixed by **image-based OCR**: `marker --force_ocr` re-OCR'd each court PDF (reads pixels, bypassing the font map), recovering the court's own text + markers. Validated **word-for-word against a 57-doc Westlaw batch** (the user's `Find And Print` export): each opinion's `[¶N]` sequence must be `1..N` and match Westlaw's paragraph count; a token-level diff (difflib) gated acceptance.

**Outcome:** all 57 recovered (e.g. *Sorum* 2020 ND 175 → 66 paragraphs). 46 auto-accepted; 11 had benign ratio diffs (footnote ordering + faithful court text). A three-way **marker / Westlaw / PDF-text-layer** pass classified every divergence: KEEP (marker matches the court PDF — preserved, incl. court typos like `statues` per the preserve-source-typos rule), MOVED (footnote ordering), FIX (real OCR misreads). Only **4 genuine OCR errors**, each confirmed against the PDF: `invitee` (2024 ND 40 ¶19) + the centered Roman-numeral section heading `I` misread as `T` (2020 ND 33, 2021 ND 70, 2023 ND 190).

**Written:** new markdown to `markdown/<year>/<cite>.md` (57); `text_content` replaced (57); the 57 Westlaw `.doc`s stored as second sources under `NW2d|NW3d/<vol>/<page>-slug.doc` with `opinion_sources(source_reporter='westlaw')`; **29 N.W. parallel citations recovered** from each Westlaw "All Citations" line and added (closing that gap). 143 changelog rows. Marker text adopted verbatim (homoglyph/markup/table/pilcrow normalization only — `triage/cite-audit-2026-05-29/para_markers_lib.py`); no court wording changed beyond the 4 confirmed fixes. Invariant `nd_modern_paragraph_markers` baseline 85→18 (0 full opinions now markerless; remainder are genuine per-curiam short orders); invariants 23/2/0. Snapshot `opinions.db.bak-pre-para-markers-2026-05-30.zst`; tools in `triage/cite-audit-2026-05-29/` (`finalize.py`, `validate_para_markers.py`, `threeway.py`, `write_back.py`).

## Batch `jurisdiction-backfill-2026-05-29` — tag in-corpus N.W. case cites as `nd` (§14f)

Fourth fix from the 2026-05-29 citation-graph audit. jetcite tags the N.W./N.W.2d/N.W.3d regional reporter as `jurisdiction='us'` (it's regional — ND/MN/SD/NE/IA/WI/MI), so N.W. citations to North Dakota cases were mis-tagged. But a specific volume+page is one unique case: any N.W. cite that resolves to an opinion in this (ND-only) corpus is definitionally an ND case.

**Set `jurisdiction='nd'` for 106,961** `cite_type='case'` text_citations whose normalized cite matches a corpus opinion's citation and wasn't already `nd` (N.W.2d 98,656 / N.W. 8,301 / N.W.3d 4). Out-of-corpus cites (federal, other-state, ND cases not in the corpus) keep their jetcite jurisdiction. Made **durable in `cite_extract`**: a case cite that resolves to a corpus opinion is now stored as `nd` at insert (verified by re-scan). Invariants 23/2/0.

**Logging note:** this is a deterministic, rule-based reclassification of ~107k rows, not a per-item judgment correction. Because the `changelog` table keys on `opinion_id` (an opinion has many cites) it can't precisely revert an individual text_citation's jurisdiction anyway, so this batch is **snapshot-reversible** (`opinions.db.bak-pre-jurisdiction-backfill-2026-05-29.zst`) with this narrative as the audit trail, rather than 107k per-row changelog entries. Tool `triage/cite-audit-2026-05-29/backfill_jurisdiction.py`.

## Batch `strip-truncation-phantoms-2026-05-29` — remove stale reporter-truncation phantoms (§14c)

Third fix from the 2026-05-29 citation-graph audit. An **older jetcite** tokenized `419 F.2d 1197` / `892 So. 2d 1075` / `43 F.4th 100` as reporter `F.`/`So.` + the *series digit* as the page, producing phantom rows like `419 F. 2` (real page lost). **Current jetcite 2.1.0 no longer does this** (verified by scanning the problem strings — `419 F.2d 1197` etc. parse correctly, and the genuine first-series `200 F. 100` is still caught), so **no jetcite change was needed**; the phantoms simply persisted because `cite_extract` uses `INSERT OR IGNORE` and never deletes superseded rows.

**Deleted 1,650 sibling-confirmed phantoms.** Conservative criterion: a candidate `VOL BASE. D` (`cite_type='case'`, D∈{2,3,4}) was deleted only when the *same opinion* also contained the correct full cite `VOL BASE.Dd|th …` (either spacing) — guaranteeing a truncation artifact, not a genuine first-series cite. Reporter families: F. (883), S.W. (195), So. (124), S.E. (116), Cal. (20), plus L. Ed./F. Supp./A./P. **Held 191** no-sibling rows untouched — they include real `S. Ct.` page-low cites, genuine first-series `N.W.`/`F.` cites, and a separate garbage-leading-zero-volume defect (`006 N.D. 3`) to be handled on its own. These are out-of-corpus cites with no `cited_by` edges, so this is forward-display only. `text_citations` 309,110→307,460; 1,650 changelog rows; invariants 23/2/0. Snapshot `opinions.db.bak-pre-strip-truncation-phantoms-2026-05-29.zst`; tool `triage/cite-audit-2026-05-29/strip_truncation_phantoms.py`.

## Batch `strip-self-citations-2026-05-29` — remove self-citations from text_citations (§14b)

First fix from the 2026-05-29 citation-graph audit (§14 of TODO-validation.md). A case cannot be an authority it cites, but the extractor scanned the whole `text_content` including the caption/header block — which prints the opinion's own neutral (and usually N.W.) cite — so essentially every opinion "cited" itself: **31,331 self-cite rows across 19,759 opinions**. `cited_by` already excluded these (0 self-edges); this cleans the forward `text_citations` table to match, and was visibly inflating `get_cited_authorities` (e.g. Rocket Dogs, 2023 ND 103, listed itself).

**Deleted 30,712 unambiguous self-cites** — rows whose normalized cite is unique to the opinion (definitionally the caption). **Left 619** whose cite is shared with another opinion (shared-page twins, e.g. *White v. Lauder* / *Willard* at `10 N.D. 400`): a match there may be a genuine companion reference, so it's deferred to the shared-page disambiguation pass rather than bulk-deleted. 30,712 changelog rows; `text_citations` 339,822→309,110.

**Recurrence prevented, not just cleaned:**
- `cite_extract._store_results` now skips inserting a `text_citations` row when the cite equals one of the opinion's own citations and is unique to it (mirrors the existing self-edge skip in the cited_by build). Verified: re-scanning 2024 ND 99 did not re-add its self-cite.
- New `invariants.py` check **`no_self_citation`** (baseline 0; excludes shared-page cites) — a regression now surfaces on the weekly run. Invariants **23 ok / 2 known / 0 regressed**.

Snapshot `opinions.db.bak-pre-strip-self-cites-2026-05-29.zst` (integrity-verified). Tools `triage/cite-audit-2026-05-29/strip_self_citations.py` (+ `REPORT.md`).

## Batch `backfill-dockets-2026nd101-107-2026-05-29` — docket_number for the 7 newly-scraped opinions

The 2026-05-29 weekly catch-up ingested **2026 ND 101–107** (Baker, Busche, Porteus, Craig, Shively, Reller, Rademacher) from freshly scraped court PDFs — recovered after fixing the scraper's Cloudflare block (curl_cffi Chrome TLS impersonation; see `scraper/nd_http.py`). These ingested with `docket_number` NULL because `merge_nd_metadata` sources dockets from CourtListener cluster JSON, which CL hasn't created yet for opinions this new — even though the scraped `2026_opinions.json` carries the docket from the published listing. **Backfilled 7** dockets from that listing JSON (8-digit `YYYYNNNN` form, matching the 1997+ convention): 101→20250258, 102→20250409, 103→20250450, 104→20260038, 105→20250374, 106→20250419, 107→20250304. Authority = ndcourts.gov opinion listing. Corpus 19,792; invariants 22/2/0. Tool `triage/backfill_dockets_2026nd101-107_2026-05-29.py`; revertible.

## Batch `recover-dockets-2026-05-27` — recover empty docket_number fields from published captions + normalize blank→NULL

Priority TODO #1. Of 5,604 empty `docket_number` fields (694 NULL + 4,910 blank-string), the recoverable target was the modern era (1997+ opinions all carry dockets) plus the 1953–96 gap; pre-1953 is genuinely docketless. Authoritative source = the **published opinion caption** (the markdown is court-PDF derived).

**Modern 1997+ — 465/465 recovered.** For each, read the `ND-neutral` markdown file (`markdown/<year>/<cite>.md`) and extracted the caption docket (`No./Nos. YYYYNNNN`), **year-validated** (8-digit `YYYY` prefix within `[filing year − 7, filing year]`; 0 mismatches). Stored bare 8-digit (matching the dominant existing form); **16 consolidated** cases comma-joined (`20160224, 20160225`). The 15 cases whose `text_content` is Westlaw-derived (no caption docket) were still recovered because the court-PDF markdown exists on disk.

**Gap 1953–96 — 56/67 recovered.** Where the court-archive filename docket (files are docket-named, e.g. `court-archive/209/8888.htm`) equalled the body caption `Civil/Criminal No.` (thousands-comma tolerant — `Civil No. 10,630` == `10630`), stored the native era form `Civ. NNNN` / `Cr. NNNN`. **11 deferred** (all Westlaw-sourced, no docket-named path and no body docket — mostly "In the Matter of…District Judge / Judicial Vacancy" administrative orders that are likely genuinely docketless).

**Normalization.** All remaining **4,910 blank-string** dockets → `NULL` (consistency; 694 were already NULL). Final empties = 5,083, all NULL (pre-1953 5,072 + 11 deferred gap; 1997+ now **0**).

521 recoveries + 4,910 normalizations = **5,431 changelog rows**; fully revertible. Corpus unchanged (19,785); invariants **22 ok / 2 known / 0 regressed**. Snapshot `opinions.db.bak-pre-docket-recovery-2026-05-27`; tool `triage/recover_dockets_2026-05-27.py`.

Note: the court's cTrack portal stores pre-1989 file numbers with a `1860` prefix (`Civ. 8888` → `18608888`); that portal-ID mapping is **not** stored here (published form retained per decision) — it belongs to the ctrack-fetch workstream (TODO #2).

## Batch `fix-docket-neutral-cite-2026-05-27` — docket-number scan; recovered real dockets stored as neutral cites

Scanned all `docket_number` values by shape and era. Formatting is otherwise clean — bare-number dockets split perfectly by era (3–5 digit = pre-1997, the 6-digit `YYNNNN` 1996–99 transition, 8-digit `YYYYNNNN` = 1997+), **zero** implausible 8-digit year-prefixes, **zero** no-digit/junk dockets. The one anomaly: **156 opinions stored a neutral citation in the `docket_number` field** (`1997ND10` instead of a docket) — 121 from 1997 (the scraper used the neutral cite as a placeholder) + ~35 scattered 2015–2025.

The archive files are docket-named and these opinions were ingested from them, so the real docket was recoverable. **Recovered 149** (cross-validated: source-path docket vs body-caption docket — 128 where both agree, plus archive-source-path or sane body-only matches; agreement accepted even across multi-year docketed→decided gaps). E.g. `1997ND10`→`960144`, `1997ND29`→`970037`, `2019ND64`→`20180122`. **Quarantined 7** (`triage/docket-neutral-cite-quarantine-2026-05-27.md`): source/body disagree (12463), source-only with a large year-gap and no body confirmation (17195, 17335), or neither recoverable (17047, 17390, 17459, 19363). Corpus unchanged (19,785); invariants 22/2/0. Snapshot `opinions.db.bak-pre-docket-recover-2026-05-27`.

## Batch `fix-neutral-cite-periods-2026-05-27` — citation-format scan; removed period-formatted neutral-cite duplicates

Scanned all 44,090 distinct citation strings against the canonical forms (`YYYY ND n`, `v N.W.2d p`, `v N.W. p`, `v N.D. p`). The corpus is highly consistent — the **only** malformatting found was **38 neutral citations written with periods** (`2003 N.D. 144` instead of `2003 ND 144`), clustered in 2003/2006/2009/2010. Each was an exact **duplicate** — the opinion already carried the canonical `ND` form — so the 38 period-formatted dups were deleted (none was the `is_primary` citation; canonical form retained). No N.W.2d/N.W./N.D.-Reports spacing or zero-padding issues exist. (Aside: 3 `N.W.3d` cites surfaced as "unrecognized" — they are legitimate; the North Western Reporter 3d series began ~2023, worth adding to cite recognizers.) Corpus unchanged (19,785); invariants 22/2/0. Snapshot `opinions.db.bak-pre-neutralperiods-2026-05-27`.

## Batch `fix-volume-date-2026-05-27` — corrections from the new volume↔date audit

Built `volume_date_check` (flags opinions whose `date_filed` is inconsistent with the date range of the reporter volume they're cited in; the reporter cite is independent of `date_filed`, so a mismatch reveals a contaminated date/cite/pairing). Initial run: 29 flags; **18 corrected, 11 quarantined** (`triage/volume-date-quarantine-2026-05-27.md`), corpus unchanged (19,785), invariants 22/2/0, cite-swap 0/0/0. Snapshot `opinions.db.bak-pre-voldate-fix-2026-05-27`.

**8 date fixes** (text "Decided/Filed" + neutral + N.W.2d cite all agreed on a year ≠ stored `date_filed`): Schnellbach **2007→2017** (oid 16931); Kostrzewski 2003→2004 (14038); Buchholz 2007→2006 (14645); Wold 2007→2008 (14896); Kieper 2007→2008 (14941); K&L Homes 2012→2013 (16020); and the **swapped Queen v. Martel pair** — 18077 2023-02-23→2022-10-04 and 18142 2022-10-04→2023-02-23 (each row's date_filed had been set to the other's).

**11 stray-cite drops** (date confirmed by the remaining cites/text; the dropped cite was a wrong-era contaminant, all `sharedby=1`): 6417 `134 N.W.2d 84` + `78 N.D. 1` (1912 *Johnson v. Bartron*; kept `134 N.W. 84`); 5888 `62 N.D. 767`; 5968 `62 N.D. 771`; 12623 `375 N.W.2d 203` (text says 575); 815 `50 N.D. 1`; 985 `139 N.W. 138` (typo of its 199 N.W. 138); 5270 `58 N.W. 1051`; 5352 `64 N.W. 563`; 15985 `826 N.W.2d 352`; 15757 `808 N.W.2d 205`. On 4 of these (6417/5888/5968/815) the dropped cite had been flagged citation-`is_primary`, so the primary was reassigned to the surviving N.W. reporter cite.

**11 quarantined** for 2nd-source review: six pre-1953 rows where two reporter cites agree on a *later* year than the stored date (date likely wrong, exact date not in the served text — Hart v. Evanson, the two First Nat. Bank of Hillsboro rows, Marshall v. Blaisdell, Bernier v. Preckel, Rufer v. Rufer); three date-vs-single/shared-cite cases (vacancy order 11760, App. for Transfer 16652, Lang v. Binstock 20474); and two off-by-one neutral-cite cases where the text-date agrees with the DB (Johnson Farms 13716, Boyda 20180).

## Batch `normalize-judges-ocr-2026-05-27` — normalized OCR-garbled justice names in opinions.judges

The pre-1953 OCR'd N.W.-reporter opinions carry heavily garbled justice surnames in the `judges` panel field (`Biedzell`/`Bikdzell`→Birdzell, `Cheistianson`→Christianson, `Yandewalle`→VandeWalle, `Geimson`→Grimson, `Bobinson`→Robinson, …). Mapped each garble back to its canonical justice (`triage/normalize_judges_ocr_2026-05-27.py`), then per-row replaced + de-duplicated panel tokens. **569 garble tokens → 32 justices; 4,444 rows updated.** Snapshot `opinions.db.bak-pre-judges-ocr-2026-05-27`; invariants 22/2/0.

Safeguards (per the surrogate-judge rule — justices appear outside their elected term, so dates aren't hard bounds): a garble maps only if it is edit-distance ≤2 from a **unique** nearest canonical justice, within that justice's corpus-derived era ±10y, and **either** the justice name is long (≥7 chars, where real-word collisions are vanishingly rare) **or** the garble carries an OCR signature (diacritic / internal caps / hyphen / no vowel). This deliberately quarantines the risky cases rather than guessing.

**255 tokens quarantined for 2nd-source / human review** (`triage/judges-ocr-doubtful-2026-05-27.md`) — and this proved essential: `Walle` (×839) and `Vande` (×203) are *VandeWalle* fragments that a looser rule would have mis-mapped to "Wallin"/"Sand"; `Dist` (×147), `Place`, `First`, `Son` are abbreviations/body words, not justices; plus genuine short-name garbles (`Buree`/`Bubke`→Burke, `Bisk`→Fisk) and real distinct surnames near a justice (Pedersen, Gross, Norris, Spaulding, Knudsen, Brothers, Buhr…) that could be legitimate surrogate **district** judges. **Separately flagged:** the OCR-era `judges` field also contains random body-word contamination (e.g. oid 2084: "Being, Express, Only, Pleaded, Validity") — a deeper extraction defect left for a future pass, not addressed here.

## Batch `fix-klose-twocol-primary-2026-05-27` — two-column mis-extraction sweep (the deferred Neset follow-up)

Ran the analyzer-markdown two-column mis-extraction sweep flagged in the Neset note below. Detector = mean body-line length < 18 over ≥40 lines (two-column PDF extraction shreds text into ~8-char column fragments). Across all 14,338 `markdown/` files, only **two** genuine corruptions exist, and a corpus-wide scan of every opinion's *served* `text_content` (cheap char/newline ratio) confirmed no other opinion serves scrambled text:

- **Neset 1998 ND 206 (oid 12782)** — already handled; corrupted `markdown/1998/1998ND206.md` is non-primary, the clean Westlaw `.doc` is primary. No change.
- **State v. Klose 2003 ND 39 (oid 13746)** — **fixed.** The corrupted `markdown/2003/2003ND39.md` (3,391 lines, mean 8.7 — two opinions' columns interleaved) was flagged `is_primary=1` and was `opinions.source_reporter='ND'`/`source_path=markdown/…`, *but the served `text_content` was already the clean, byte-identical `NW2d/657/276.md`* (mean line 168, intact `[¶N]`). So the served opinion was fine; only the primary pointer lied — a latent landmine (a future "rebuild text from primary" would have clobbered the clean text with the corrupted markdown). Repointed `source_reporter`→`NW2d`, `source_path`→`NW2d/657/276.md`; `align_primary_source --apply` flipped the primary flag (NW2d primary, corrupted ND markdown demoted to non-primary, archive non-primary). `text_content` unchanged. Snapshot `opinions.db.bak-pre-klose-source-fix-2026-05-27`.

Three served-text false positives were inspected and cleared (coherent text, short lines — not interleaving): *Everett v. State* 2019 ND 149 (inline citations split across lines), and the consolidated-juvenile captions *Interest of A.J.L.H.* 2012 ND 235 and *Interest of P.T.D.* 2019 ND 3 (multi-party captions listed one-per-line). The two corrupted markdown files are left on disk as non-primary sources (re-extractable from the court PDF later). Corpus unchanged (19,785); invariants 22/2/0; `detect_cite_swap` 0/0/0.

## Batch `register-nw-images-2026-05-27` — filed acquired bound volumes + page photos; registered 8 shared/Table-page images

Acquired imagery (user-supplied, `~/Downloads`) filed into the canonical source tree and, for the page photos, registered as `NW-image` cross-check sources:

- **N.D. Reports bound volumes 4, 5, 6, 8** (Google Books scans) → `~/refs/nd/opin/N.D./{4,5,6,8}/_bound-volume.pdf`. Fills four gaps; imaged N.D. vol set 21 → 25. (No DB rows — no shared pages fall in these volumes.)
- **8 N.W.2d shared/Table page photos** → `~/refs/nd/opin/NW2d/<vol>/<page>.pdf` (JPEG→PDF), each **registered as an `NW-image` source on the opinions it depicts** (16 rows; `is_primary=0`, `text_length=0`). These confirm shared-page citations that previously rested on docket-only evidence:

  | page | opinions confirmed sharing it |
  |---|---|
  | **789 N.W.2d 731** (Affirmances-by-Summary-Opinion Table) | State v. Delaney (15515) + Hoffner v. Job Service (20504) — *resolves the missing-image flag on the prior Delaney/Hoffner verification* |
  | 4 N.W.2d 224 | Arnold v. Cass County (9810) + McArthur v. Cass County (9811) |
  | 35 N.W.2d 137 | Chester v. Einarson (9128) + on-rehearing (20391) |
  | 42 N.W.2d 438 | Westerso v. City of Williston (10070) + Ophaug v. Hildre (10071) |
  | 47 N.W.2d 527 | In re McIntyre's Estate / Weiss v. Stormon (10881, 10882) |
  | 55 N.W.2d 576 | Barrett v. Bd. of Trustees of Teachers' Ins. & Retirement Fund (12212, 12213) |
  | 71 N.W.2d 770 | Gunsch v. Gunsch (14446) + Scherbenske v. Maier (14447) |
  | 73 N.W.2d 782 | Gunsch v. Bauer (14732) + Karabensh v. Grant (14733) |

  `NW-image` total 48 → 64; imaged page set 40 → 48; un-imaged shared-page inventory 241 → 233 (`triage/shared-page-no-image-2026-05-27.md`). Corpus unchanged (19,785); invariants 22/2/0. Snapshot `opinions.db.bak-pre-nwimage-register-2026-05-27`.

## Batches `fix-coa-court-nocite-2026-05-27` + `merge-juvenile-nocite-dups-2026-05-27` — resolved the post-1997 no-cite tail (11 → 3)

Closed out the 11-row post-1997 "no `YYYY ND n` cite" tail that prior passes had left as a low-value residual. Re-examination split it cleanly into two classes:

- **`fix-coa-court-nocite-2026-05-27` (3 rows).** *Ernst v. TJON* (oid 14343, dk 20040373CA), *In re Nb* (14344, dk 20040340CA), *In re Knh* (14341, dk 20050018CA) — CA-suffix-docket "Affirmed by summary opinion" stubs that CourtListener attributed to "Supreme Court of North Dakota." These have no genuine published "IN THE SUPREME COURT" caption (just CL's auto-attribution line), so per the 2026-05-25 COA-in-scope ruling the CA docket governs: `court` → **North Dakota Court of Appeals**. They correctly remain outside the `YYYY ND n` sequence (COA opinions cite as `ND App`). COA-labeled total 41 → 44. Snapshot `opinions.db.bak-pre-coa-court-fix-2026-05-27`.
- **`merge-juvenile-nocite-dups-2026-05-27` (8 merges).** The remaining 8 were anonymized juvenile-termination / mental-health summary dispositions (2018–2019) that CourtListener double-ingested: a **NW2d-sourced stub** carrying the N.W.2d cite + consolidated dockets under a `County Social Services v. [Initials]` caption, and a **CONFIDENTIAL twin** carrying the canonical `YYYY ND n` neutral cite + the authoritative ND/archive court text under an `Interest of [Initials]` caption. The prior matcher missed them because the twins share no N.W.2d page (neutral-cite only) and the captions diverge; the discriminator is **child initials + filing date**, confirmed by identical holding text (body jaccard up to 0.93). Merged each stub → its neutral-cited twin (survivor keeps the ND/archive authoritative text), absorbing the N.W.2d cite and carrying the stub's dockets onto the survivor; survivor caption set to the ND published `Interest of [Initials]` form with `(CONFIDENTIAL)`/`(consolidated …)` annotations stripped:

  | survivor | neutral cite | absorbed N.W.2d | child |
  |---|---|---|---|
  | 19252 | 2018 ND 151 | 913 N.W.2d 763 | Z.F.T. |
  | 19259 | 2018 ND 160 | 913 N.W.2d 768 | N.F.F. |
  | 19253 | 2018 ND 152 | 913 N.W.2d 769 | A.C. |
  | 19271 | 2018 ND 191 | 916 N.W.2d 112 | M.S.H. |
  | 19280 | 2018 ND 236 | 919 N.W.2d 340 | G.F. |
  | 19446 | 2019 ND 3 | 921 N.W.2d 176 | P.T.D. |
  | 19454 | 2019 ND 35 | 923 N.W.2d 105 | H.B. |
  | 19350 | 2019 ND 118 | 926 N.W.2d 709 | F.M.G. |

  Corpus **19,793 → 19,785**; `align_primary_source --apply` flipped 8 primaries (NW2d demoted, ND stays authoritative). Snapshot `opinions.db.bak-pre-juvenile-merge-2026-05-27`.

**Post-1997 no-cite tail is now 3, all correctly-labeled Court of Appeals summary affirmances** (cite-less by design). Invariants 22/2/0; `detect_cite_swap` 0/0/0.

## Batch `fix-berger-goetz-pairing-2026-05-27` — moved a wrong-paired court-archive (Goetz → Berger) + new court-archive audit

Closing the coverage gap flagged in `fix-ellis-reimers-archive-2026-05-27`: extended `fix_archive_pairings` with a **`--reporter court-archive` report-only audit**. Court-archive titles are pre-1997 (parallel N.W. cite only, no neutral) and the reporter prints many N.D.R.App.P. 35.1 summary dispositions on one shared "Table" page, so the neutral-cite logic used for `archive` rows does not apply. The new mode classifies by **page cardinality** — how many opinions own each cite the file's `<title>` asserts: `ok` (linked opinion uniquely owns a title cite), `shared_page` (a title cite is shared with another opinion — verify by docket), `title_elsewhere` (no title cite belongs to the linked opinion — verify the BODY, titles lie), `unresolved`. Run over all 4,837 court-archive rows: **ok 4822 / shared_page 2 / title_elsewhere 7 / unresolved 6** (report `triage/court-archive-pairing-audit-2026-05-27.md`). It is **report-only** because the fix requires reading the file body — the `<title>` tag is frequently contaminated with a sibling opinion's cite while the body is correct (proven below). This rule collapses the naïve name/cite-comparison's ~144 false positives (caption-convention divergence — `Disciplinary Action Against X` vs `Disciplinary Board v. X`, `Estate of X` vs `X v. Bank`, abbreviations, archive-title typos) to a clean, reviewable handful.

**Fix applied (2 changelog rows).** **City of Bismarck v. Berger** (oid 20487, N.D. **Court of Appeals**, docket 900255CA) — the file `court-archive/465/900255.htm` (body caption "City of Bismarck v. Leonard Berger", Criminal No. 900255CA) was attached to ***In re Goetz*** (oid 10797, an interim-suspension order, docket 900016). Page `465 N.W.2d 480` is a shared summary-disposition Table page (Goetz's order and Berger's COA disposition both sit there; the folder holds two Westlaw `.docs` — `0480-Unknown.doc` for Goetz and `0480-…BERGER.doc` for Berger), so the shared cite is correct and kept; only the per-case archive HTML was misattached. Moved court-archive row 40568 → 20487 and backfilled Berger's docket (`NULL` → `Criminal No. 900255CA`). Goetz keeps `NW2d/465/480.md` + its Westlaw order. The second COA collision in vol 465 — exact twin of Ellis/Reimers. Snapshot `opinions.db.bak-pre-berger-pairing-2026-05-27`.

**Verified, no change (titles contaminated, linkages correct).** The other `title_elsewhere` flags whose body was read: **Rogelstad** (oid 20428) — file body is genuinely the `226 N.W.2d 371` class-action opinion (bracket cites 226:371–376, Civil No. 9038); only its `<title>` carries the sibling's `224 N.W.2d 544` (oid 7351). **McKinnon** (oid 20472) — file body is genuinely the `264 N.W.2d 449` reinstatement opinion; `<title>` carries the sibling's `200 N.W.2d 62` (oid 7116). Both correctly linked.

Corpus unchanged at **19,794** for this batch; invariants 22/2/0. Snapshot `opinions.db.bak-pre-berger-pairing-2026-05-27`.

## Batch `merge-mckinnon-dup-2026-05-27` — merged a court-archive re-ingest dup (20472 → 7827)

Surfaced by the court-archive audit above. oid **20472** (*Disciplinary Action Against McKinnon*, court-archive only, `264 N.W.2d 449`, date **1972-03-28**, synthetic `1972 ND 19`) was a duplicate of oid **7827** (*Application of Roger A. McKinnon for Reinstatement to the Bar*, `264 N.W.2d 448`, date **1978-03-02**, docket Civ. 8785, NW2d + Westlaw). Same docket/case, text jaccard **0.874**; 20472's 1972 date was contaminated from the *other* McKinnon matter (7116) — the vol-264 neighbors (Vigen, Thorson, Landers…) are all filed 1978-03-02/03, confirming the reinstatement opinion is 1978. Merged `20472 → 7827` via `merge_opinions.merge_pair` (FK-safe): 7827 keeps its NW2d + Westlaw and gains `court-archive/264/8785.htm` as a secondary source; the contaminated cites `264 N.W.2d 449` (a within-opinion page, not the 448 start) and the wrong-year synthetic `1972 ND 19` were stripped from the survivor. `align_primary_source --apply` re-set the primary to Westlaw (1 flip). Corpus **19,794 → 19,793**. Snapshot `opinions.db.bak-pre-mckinnon-merge-2026-05-27`.

## Batch `fix-ellis-reimers-archive-2026-05-27` — moved a wrong-paired court-archive (Ellis → Reimers)

From reviewing the 2 optional diff-audit candidates. **Ellis** (oid 10796, *Disciplinary Board v. Cheryl L. Ellis*, 465 N.W.2d 175) had `court-archive/465/900333.htm` attached, which is actually ***Reimers Seed Co. v. Stedman*** (N.D. **Court of Appeals**, docket 900333CA) — a parallel-cite collision at `465 N.W.2d 175`. *Reimers* exists as its own row (oid 20480, correctly labeled COA) but held only its Westlaw `.doc`. Moved the court-archive row 40567 → 20480 and backfilled Reimers's docket (`NULL` → `Civil No. 900333CA`, stated in the archive body). Ellis keeps its correct `NW2d/465/175.md` + Westlaw order. (`fix_archive_pairings` missed this because it only scans `source_reporter='archive'`, not `court-archive` — a coverage gap worth closing.) Invariants 22/2/0; diff-audit real candidates 7 → 6. Script `triage/apply_ellis_reimers_2026-05-27.py`.

**Neset 1998 ND 206 (oid 12782) — no change needed.** The other optional candidate: its Westlaw primary `text_content` is the clean, complete "ORDER OF REINSTATEMENT"; the *fuller* ND court markdown (`markdown/1998/1998ND206.md`) is **corrupted** — a two-column PDF mis-extraction that interleaves a different opinion's text (a sua sponte-dismissal case) with a scrambled Neset order. So the Westlaw source is correctly primary and the served opinion is fine; the corrupted markdown is a latent analyzer-extraction bug (left visible as a non-primary source, not detached, since the court PDF could be re-extracted). *Worth a future sweep: find other two-column mis-extractions in the analyzer markdown.*

## Batches `fix-diffaudit-pairings-2026-05-27` + `fix-archive-mispair-2026-05-27` — wrong-paired source cleanup from a fresh multi-source diff audit

Re-ran the §3 multi-source diff audit (`triage/multisource-diff-2026-05-27.md`); the 2026-05-04 buckets (secondary_truncated 30 / primary_short 26 / primary_tiny 14 / unclear 8) were stale. The `<0.20` band was dominated by **non-diffable** pairs, not bugs: 121 unreadable Westlaw `.doc`, 48 NW-image page-scans, ~85 short-stub / multi-opinion-table pages. Hardened `multisource_diff` to categorize these out (new notes `multi-opinion page` / `short stub` / `secondary image`, gated below a 0.5 similarity ceiling and, for bundles, requiring the opinion's own cite present so a true wrong-pairing still surfaces), shrinking the actionable band from a polluted 240 → **7 real candidates** (4 are the documented 1915–17 truncated-NW1-OCR secondaries; 1 NW2d table entry; plus *Neset* 1998 ND 206 — Westlaw stub primary vs fuller ND markdown — and *Ellis* 465 N.W.2d 175, both optional). Two real wrong-pairing classes fixed:

- **`fix-diffaudit-pairings-2026-05-27` (12 changelog rows).** (a) **Johnson v. State name-collision** — oid 14179 (2005 ND 19, dk 20040252) had soaked up the parallel cites *and* NW2d source files of two other Johnson opinions. Moved `692 N.W.2d 784` + `NW2d/692/784.md` → oid 18544 (2005 ND 8, dk 20040203) and `709 N.W.2d 21` + `NW2d/709/21_4.md` → oid 18521 (2005 ND 197, dk 20050168) — both rightful owners had been missing their N.W.2d parallel — and deleted the two duplicate archives off 14179. (b) **Delaney** (oid 15515, 2010 ND 52) — detached Hoffner's per-docket `archive/2010/20090357.htm`. Both legitimately cite `789 N.W.2d 731 (Table)` (verified against the bound N.W.2d page image: a "SUPREME COURT OF NORTH DAKOTA — AFFIRMANCES BY SUMMARY OPINION" table page shared by ~12 same-term N.D.R.App.P. 35.1 dispositions), so the shared cite is correct and kept; only the per-docket archive was wrong. (c) **King v. Stark County** (oid 4746) — detached corrupt `NW/271/771.md` (HTML/CSS junk from a failed CL scrape; Westlaw `.doc` is the correct primary).
- **`fix-archive-mispair-2026-05-27` (3 changelog rows).** The neutral-cite-tightened `fix_archive_pairings` re-scan surfaced 3 archive HTMLs whose title neutral cite belongs to a *different* opinion, each an extra/duplicate on the lower-numbered opinion whose rightful owner already held the file → plain detach: `20070083.htm` (=Skarsgard 2007 ND 174) off 14837 (2007 ND 159); `20070369.htm` (=Torkelsen 2008 ND 137) off 15021 (2008 ND 141); `20090135.htm` (=Hanenberg 2010 ND 8) off 15508 (Everett 2010 ND 4). The Everett bad linkage had been *introduced* by the old parallel-tolerant `fix-archive-pairings-2026-05-04` (os row 37026). Remaining `fix_archive_pairings` flags are benign: 1 `move` is a source title-typo (`20170296.htm` reads "2018 ND 865" for Brekhus 2018 ND 86; correctly paired by docket) and 3 `verify` are parallel-only matches with docket-aligned files whose archive titles omit/blank the neutral number (1998 old format; 2018 "2018 ND ," glitch) — all docket-verified correct.

Corpus unchanged at **19,794** (no row adds/deletes — only source/cite re-attachment). Invariants 22/2/0; `detect_cite_swap` CITE/DOCKET/BODYDUP 0; `align_primary_source --apply` 0 changes. Snapshot `opinions.db.bak-pre-diffaudit-pairings-2026-05-27`. Scripts `triage/apply_diffaudit_pairings_2026-05-27.py`, `triage/apply_archive_mispair_2026-05-27.py`.

## Batches `section6-nocite-{v2,v3,v4,brekhus}-merge-2026-05-27` — 19 more no-cite NW2d dups merged via widened matching

Cleared the rest of the mergeable post-1997 no-cite NW2d duplicates the strict same-date/exact-name pass missed, in escalating passes (each followed by `align_primary_source --apply`; cite guard throughout = drop lacks ND-neutral, keep has one):
- **v2 (same-year + name/jaccard): 7** — e.g. fixed the earlier Johnson→*Matthews* mismatch to the correct Johnson→2005 ND 19; Skarsgard→2007 ND 159, Torkelsen→2008 ND 141, Curtis/Rutherford/Jelleberg→2006 ND 128/129/131.
- **v3 (distinctive-surname + same-year): 6** — Kessel→2007 ND 55, Grzeskowiak→2007 ND 150, Thompson→2007 ND 173, Bowman→2007 ND 200, Marler→2018 ND 238, Goldsack→2019 ND 36.
- **v4 (shared docket): 5** — resolved anonymized/ambiguous: In re N.B.→2006 ND 132, In re K.G.→2006 ND 130, Kram→2007 ND 151, Riemers→2008 ND 118, Johnson→2008 ND 168.
- **Brekhus (text jaccard 0.56): 1** — 17133→19336 (2018 ND 86); carried docket 20170296 onto the survivor (which had none).

Corpus 19,813 → **19,794**; invariants 22/2/0. **Post-1997 no-cite set 106 → 11 over the session** (95 cleared: 93 merged + 2 SD deleted). **Residual 11 (per-case, low-value tail):** 3 are ND **Court of Appeals** opinions (CA dockets 20040373CA/20040340CA/20050018CA — *Ernst v. TJON*, *In re Nb*, *In re Knh* — mislabeled `court='North Dakota Supreme Court'`, correctly outside the `YYYY ND n` sequence) and 8 are anonymized juvenile/social-services memorandum stubs (Grand Forks/Cass/McKenzie Soc. Servs., State v. P.T.D./H.B., In re F.M.G.) whose cited twins weren't findable by name, surname, docket, or text. Scripts `triage/match_nocite_dups_v{2,3,4}_2026-05-27.py`.

## Batch `delete-sd-contamination-2026-05-27` — removed 2 South Dakota opinions mislabeled as ND

Deleted the 2 foreign-jurisdiction opinions found by the contamination scan: **16005 *Young v. Oury*** (2013 SD 7, SD docket No. 26182) and **16006 *Thompson v. Avera Queen of Peace Hospital*** (2013 SD 8, SD docket No. 26296) — both KONENKAMP, J., South Dakota Supreme Court, in via the shared 827 N.W.2d volume and mislabeled `court='North Dakota Supreme Court'`. Confirmed not-ND by reading the opinions (SD justices, SD sequential dockets, SD facts) and 0 inbound `cited_by`. All FK references purged (citations, opinion_sources, text_citations, quality_scores, validation_status, cite_extract_progress, and 4 changelog audit rows); FTS updated by trigger; 0 orphans. Corpus 19,815 → **19,813**; invariants 22/2/0. Snapshot `opinions.db.bak-pre-sd-delete-2026-05-27` (row deletions revert via snapshot). Post-1997 no-cite set now 30 (all ND dups / juvenile / 1 ambiguous — next-step dedup).

## Batch `section6-nocite-high-merge-2026-05-27` — merged 74 no-cite NW2d duplicates; foreign-jurisdiction scan

Merged the 74 HIGH-confidence post-1997 no-neutral-cite NW2d duplicates into their cited markdown twins (`triage/merge_nocite_high_2026-05-27.py`; keep=cited twin, drop=no-cite NW2d stub; folds the N.W.2d parallel into the survivor). Guard: drop has no ND-neutral cite, keep does, and match is exact-name (≥0.9) or same-text (jaccard≥0.6). Corpus 19,889 → **19,815**; post-1997 no-cite 106 → 32. merge_pair left the older NW2d source flagged primary on the 74 survivors (tripped `source_reporter/path_matches_primary`); fixed with `align_primary_source --apply` (74 flips, `opinions.source_reporter` is ground truth). Invariants back to 22/2/0. Snapshot `opinions.db.bak-pre-nocite-high-merge-2026-05-27`.

**Foreign-jurisdiction contamination scan (2026-05-27):** two independent signals — SD-distinctive justices in `judges` (Gilbertson/Konenkamp/Zinter/Severson) and a foreign neutral self-cite in the text — plus a foreign-court-header sweep, all converge on **exactly 2** opinions mislabeled `court='North Dakota Supreme Court'`: **16005 *Young v. Oury* = 2013 SD 7** and **16006 *Thompson v. Avera Queen of Peace Hospital* = 2013 SD 8** (in via the shared 827 N.W.2d volume). No broader contamination. Deletion deferred for review.

## Post-1997 missing-neutral-cite investigation (2026-05-27) — sequence now gap-free; 2 opinions recovered; dedup + contamination surfaced

Investigated the 107 post-1997 opinions lacking an `ND-neutral` cite and audited the per-year neutral sequence (which must run 1→max with no gaps). Findings + fixes:

- **Sequence was gap-free 1997–2026 except three slots.** Fixed:
  - **2010 ND 149** (`fix-2010nd149-reporter-2026-05-27`): existed (oid 15479 *S.H.B. v. T.A.H.*) but its cite was mis-tagged `reporter='ND'`; reclassified → `ND-neutral`.
  - **2010 ND 54** *Hoffner v. Job Service North Dakota* and **2012 ND 196** *Bank of North Dakota v. Brown* (`recover-seq-gaps-2026-05-27`): **genuinely absent** — created from on-disk archive HTML (docket 20090357 / 20120145; per curiam; +789 N.W.2d 731 / +821 N.W.2d 385). Corpus 19,887 → **19,889**. All 1997–2026 sequences now gap-free; invariants 22/2/0.

- **The remaining 106 no-cite rows are NOT missing opinions — they're duplicates** (the sequence is complete, so each real opinion already holds its cite). They're CL/NW2d double-ingests that never merged into the markdown opinion and, carrying no neutral cite, never tripped `neutral_cite_uniqueness`. Dry-run matcher `triage/match_nocite_dups_2026-05-27.py` → `triage/nocite-dup-match-2026-05-27.tsv`: **74 HIGH** (same date + exact name), 16 MEDIUM, plus REVIEW/NOMATCH that split into (a) real twins with name-format/date variance (e.g. Kram→2007 ND 151, Skarsgard→2007 ND 174, Curtis/Rutherford/Jelleberg→2006 ND 128/129/131), (b) anonymized-juvenile twins (In re Knh/Nb/Kg), and (c) **foreign-jurisdiction contamination**: 16005 *Young v. Oury* = **2013 SD 7** and 16006 *Thompson v. Avera* = **2013 SD 8** (South Dakota justices, mislabeled `court='North Dakota Supreme Court'`, in via the shared N.W.2d reporter) + 14343 *Ernst v. TJON* (ambiguous, docket `...CA`). The dedup merge + a corpus-wide foreign-jurisdiction scan are deferred for review (no merges/deletes applied yet).

## Batches `fix-archive-rebuild-2001-2012-2026-05-27` + `fix-farok-lunstad-2026-05-27` — 18 more markdown-leak cite-swaps recovered; detector hardened

The `detect_cite_swap` DOCKET pass surfaced 17 rows (2001–2012) that the CITE pass was **blind to**: these markdown files lead with a `# Title\nNorth Dakota Supreme Court\nYYYY ND n; …` block (not YAML `---`), so the frontmatter stripper left the correct label cite visible and masked a body that had leaked a **different, nearby-numbered opinion** (e.g. 13527 labeled 2001 ND 172 *Farmers Elevator* held 2001 ND 176 *McDowell*). Metadata (cite, case_name, N.W.2d, docket) was correct; only `text_content` (and sometimes author/per_curiam — 15557 *Pizza Corner* Maring→Crothers, 15508 *Everett* Sandstrom→per curiam) had leaked.

**Recovered all 17 from on-disk archive HTML** (independent of the analyzer that produced the leak), via `scrape_archive.parse_opinion_page`, keeping the correct metadata and guarding that the archive title cites the DB label (normalized for the zero-padded `2010 ND 04` form). Archive made primary; leaked ND markdown detached. oids: 13527, 13713, 13552, 14128, 14412, 14868, 14837, 15112, 15246, 15217, 15557, 15508, 15515, 15642, 15743, 15656, 15850. Script `triage/fix_archive_rebuild_2001_2012_2026-05-27.py`; snapshot `opinions.db.bak-pre-archive-rebuild-2001-2012-2026-05-27`.

**Detector hardened** (`_body` now skips the `# Title` block to the real `IN THE SUPREME COURT` header) — which then surfaced 2 more:
- **13130 *State v. Farok* (2000 ND 48)** — genuine leak (held *DeCoteau* 2000 ND 44 text); rebuilt from `archive/2000/990326.htm`.
- **18358 *State v. Lunstad* (2000 ND 198)** — correct content, but the **archive HTML's own body header has a typo** printing "2000 ND 113" (echoing docket 20000113) instead of 2000 ND 198 (which collided with the real *Schiff* 2000 ND 113). Normalized the single in-body cite → 2000 ND 198. (Batch `fix-farok-lunstad-2026-05-27`; snapshot `…-pre-farok-lunstad-2026-05-27`.)

Corpus unchanged at **19,887** (all updates, no add/delete); invariants 22/2/0. `detect_cite_swap` now reads **CITE 0 / DOCKET 0 / BODYDUP 0** — the cite-swap workstream is fully clean (34 real flags at session start → 0, plus 18 additional leaks this batch the hardened detector caught).

## Batch `section6-2018nd246-dupmerge-2026-05-26` — merged the CL NW2d dup surfaced by the 2018 ND 246 rebuild

Rebuilding 19290 to the real 2018 ND 246 (prior batch) added its 920 N.W.2d 908 parallel, which surfaced a pre-existing duplicate: **17334** ("In re Provision of Legal Servs…", NW2d-sourced `NW2d/920/908.md`, same docket 20160436, same date 2018-11-15, per curiam) was the CourtListener NW2d copy of the same order (jaccard 0.87). Classic §6 CL double-ingest. Merged 17334 → **19290** (keep: carries the neutral cite 2018 ND 246 + authoritative Westlaw text + the fuller petition caption matching the sibling 2017 ND 1 / 2019 ND 1 rows), absorbing the NW2d source. Post-merge realigned the primary `opinion_sources` row to the Westlaw `.doc` (matches `text_content`) — the merge engine's `_fix_single_primary` had picked the older NW2d row, briefly tripping `source_reporter/path_matches_primary`. Corpus 19,888 → **19,887**; invariants 22/2/0. Snapshot `opinions.db.bak-pre-2018nd246-dupmerge-2026-05-26`.

**§6 status (2026-05-26):** the corpus dedup scan now shows **0 actionable merges** — the long-quoted "~530 DEFER_MODERN pairs" was stale (cleared in prior sessions). Remaining buckets are all correctly-held non-merges: 1 DEFER_MODERN (638 N.W.2d 45 = *Interest of J.S.* / *City of Fargo v. Tipler*, distinct shared page), 12 MERGE-HOLD-LOWJAC (shared-page distincts, different parties — e.g. Middlewest Grain, Cass County; *White v. Lauder* already ruled distinct), 57 needs_decision, 25 defer_multi (bound-volume multi-opinion pages). The `detect_cite_swap` refinement (this commit) also drove CITE 34→**0** and BODYDUP→**0** for the session (westlaw rows + cross-reference FPs excluded).

## Batch `section7-hjjn-swap-2026-05-26` — repaired the Interest of H.J.J.N. text-swap; CITE flags now all FPs

A fifth cite-swap (surfaced from the 19877 CITE flag): the two *Interest of H.J.J.N.* opinions (docket 20240060, a retained-jurisdiction sequence) had their texts swapped by the scraper name-scramble — 19877 (label 2024 ND 132) held the 2024 ND 70 text; 20044 (label 2024 ND 70) held the 2024 ND 132 text (jaccard 0.179 = distinct). Kept each row's existing neutral cite (20044 has 1 inbound cited_by as 2024 ND 70 — no repointing) and rebuilt each from the user-supplied Westlaw .doc:
- **20044 = 2024 ND 70** — McEvers, "Remanded; jurisdiction retained," filed **2024-04-18**, +**5 N.W.3d 775**; per_curiam 1→0; docket `2024ND70`→20240060; date `2024-01-01`(placeholder)→2024-04-18.
- **19877 = 2024 ND 132** — **per curiam** mem (post-remand affirm), filed **2024-07-05**, +**9 N.W.3d 656**; author McEvers→∅, per_curiam 0→1.

Invariants 22/2/0; corpus 19,888. Snapshot `opinions.db.bak-pre-hjjn-swap-2026-05-26`; script `triage/fix_hjjn_swap_2026-05-26.py`. **Cite-swap workstream now clean:** the 7 remaining `detect_cite_swap` CITE flags are all false positives — 6 Westlaw `.doc` rows whose body-first cite is a *cited authority* (19363/19750/19854/20064/20066/20068) + **19877**, whose 2024 ND 132 mem legitimately cites the prior 2024 ND 70 opinion it follows. Zero real mislabels remain (was 34 at session start). Detector `.doc`-and-cross-reference exclusion refinement still owed to silence these FPs.

## Batch `section7-inbody-citenorm-2026-05-26` — normalized 3 corrected-opinion in-body header cites

The three corrected-opinion rows correctly cited in the DB still carried the **phantom new-year cite** in their stored text's header self-cite line (the artifact the Court's reissued PDF prints). Per the Court's rule (the published citation never changes on correction, even when the corrected opinion is reissued in a later year), normalized each in-body header to the official cite — a single, header-only occurrence per row (verified: each phantom appeared exactly once; the official cite was absent):
- **Jesser v. NDDOT (19433):** body `2020 ND 287` → **2019 ND 287**
- **Nodak Electric Coop. (19690):** body `2023 ND 225` → **2022 ND 225**
- **Sanderson v. Agotness (19988):** body `2025 ND 232` → **2024 ND 232**

Invariants 22/2/0; `detect_cite_swap` CITE 10→**7**, BODYDUP 14→**12** collisions. Snapshot `opinions.db.bak-pre-inbody-citenorm-2026-05-26` (text edits revert via snapshot). The remaining 7 CITE flags are the 6 Westlaw `.doc` Group-C false positives + 19877 (2024 ND 132, unexamined).

## Batch `section7-groupA-rebuild-2026-05-26` — recovered 2 genuinely-missing opinions; reframed the "4 tangles"

Resolved the Group A cite-swap tangles. Key reframe (ruled this session): the ND Supreme Court's **corrected opinions keep their original neutral cite** — the new-year cite stamped on a reissue (e.g. a 12/2022 opinion corrected 02/2023 prints "2023 ND nnn") is a template artifact, not a second cite. That artifact, carried into the scraped text, is what made the detector flag three pairs. Net: only **two** of the four "tangles" were real, and both were genuinely-missing opinions whose rows held a duplicate of a later opinion.

- **2018 ND 246 (oid 19290)** rebuilt from the user-supplied Westlaw .doc (920 N.W.2d 908): a distinct **11/15/2018 per curiam** DAPL pro-hac-vice **extension** order (docket 20160436) — *not* the 01/18/2017 order (2017 ND 1) it had been holding a duplicate of. Set date 2017-01-18→**2018-11-15**, docket `2018ND246`→**20160436**, added parallel **920 N.W.2d 908**, westlaw primary, corrupt ND markdown detached.
- **State v. Pailing, 2019 ND 283 (oid 19429)** rebuilt from the Westlaw .doc (936 N.W.2d 78, docket 20190086, Crothers J., 12/12/2019): it had been holding a duplicate of *Jesser*. Added parallel **936 N.W.2d 78**, docket→**20190086**, westlaw primary, corrupt markdown detached.
- **Jesser v. NDDOT, 2019 ND 287 (oid 19433)** — already correctly cited; added the missing parallel **936 N.W.2d 102**. (Its body still prints the corrected-opinion artifact "2020 ND 287"; in-body normalization deferred pending review.)
- **NOT touched (corrected-opinion artifacts, cites already correct):** Nodak Electric Coop. = **2022 ND 225** (19690; body prints artifact "2023 ND 225"), Albertson v. Albertson = **2023 ND 225** (18237, the genuine 225th of 2023, 12/01/2023), Sanderson v. Agotness = **2024 ND 232** (19988; body prints artifact "2025 ND 232"), Bohe v. State = **2025 ND 232** (20224; placeholder date 2025-12-31 still needs the real filing date). The detector's BODYDUP flags on these pairs are **false positives** from the corrected-opinion stamp.

The `.docs` were archived to the canonical refs N.W.2d tree (`N.W.2d/920/0908-…doc`, `N.W.2d/936/0078-State-v-Pailing.doc`). Corpus unchanged at **19,888** (updates, no add/delete); invariants 22/2/0; `detect_cite_swap` CITE 12→**10**, BODYDUP 16→**14** collisions. Snapshot `opinions.db.bak-pre-groupA-rebuild-2026-05-26` (text swaps not changelog-revertible); script `triage/fix_groupA_rebuild_2026-05-26.py`. Remaining CITE flags: 3 corrected-opinion in-body artifacts (19433/19690/19988, pending normalization decision) + 6 Westlaw `.doc` Group-C false positives + 19877 (2024 ND 132, unexamined).

## Batch `section6-vol74-adams-2026-05-26` — merged the 74 N.D. 242 CL double-ingest (§10 vol 74); resequenced 1945

Resolved the lone genuinely-open pair in the legacy `duplicate_candidates` (dc id 1359). Confirmed against the user-supplied bound N.D. Reports vol 74 pp. 242–243 that **74 N.D. 242 is a single opinion** — *In re Adams* (File No. 6966), Burr, J.; Christianson Ch. J., Nuessle, Burke, Morris JJ. concur; 21 N.W.2d 351; filed 1945-08-08. (The case ending atop p. 242 is the separate *In re Hanson*, 74 N.D. 224 / 21 N.W.2d 341 = oid 7177, File 6965, holds 1945 ND 25 — distinct, untouched.)

Textbook §6 CL double-ingest: **keep 7180** (matter caption *In re Adams*, low cluster_id 3933583, correct per-opinion author Burr, `NW2d/21/351_2.md`); **drop 7179** (parties caption *Northern Pacific Railway Co. v. McDonald*, high cluster_id 6852041, CL-mis-defaulted author "Burke" — its own body text reads "BURR, Judge." — carrying the Westlaw `.doc` + `NW2d/21/351.md`). Both 0 inbound cited_by; tie broken by lower cluster_id. Survivor now consolidates all three sources. `merge_pair` carried the fuller panel from the drop; the OCR typo **Christxanson → Christianson** was fixed on the survivor from the bound volume (judges now `Burke, Burr, Christianson, Morris, Nuessle`).

The merge left the survivor with two synthetic neutral cites (1945 ND 26 + 1945 ND 27, the two pre-merge row assignments); deleted the surplus **1945 ND 27** row (Adams holds **1945 ND 26**, right after Hanson's 25). Re-ran `triage/section10_resequence_2026-05-24.py --apply`: the 1945 tail shifted down one (ND 28→45 → ND 27→44, 18 cites). Corpus 19,889 → **19,888**; invariants 22/2/0; `duplicate_candidates` open pair resolved (the remaining ~130 unreviewed are known-distinct shared-page clusters). Snapshot `opinions.db.bak-pre-vol74-adams-merge-2026-05-26` (row deletion NOT changelog-revertible); scripts `triage/merge_vol74_adams_2026-05-26.py` + the inline synthetic-dedup.

## Detector enhancement 2026-05-26 — `detect_cite_swap` BODYDUP pass (content-claims-wrong-cite class)

Added `scan_bodydup` to `ndcourts_mcp/detect_cite_swap.py` to catch the Albertson/Bohe class the CITE check is blind to (the wrong neutral cite baked into the stored text, so the row's label *matches* its wrong body). Self-contained: groups native-neutral (1997+) opinions by their body header self-cite and flags any `YYYY ND n` claimed by 2+ opinions. Run: 16 collisions / 32 rows. A "label absent from own text" discriminator separates REAL content-mislabels from cross-reference FPs. Findings:
- **REAL content-mislabels:** 2020 ND 287 (19429 *Pailing* + 19433 *Jesser*, both hold *Jesser*), 2023 ND 225 (19690 *Nodak* mislabeled 2022 ND 225 vs 18237 *Albertson*), 2025 ND 232 (19988 *Sanderson* mislabeled 2024 ND 232 vs 20224 *Bohe*), 2017 ND 1 (19290, the annual Petition matter). These need C-Track pulls of the displaced/true opinions.
- **False positives:** cross-reference cases where the flagged row is correctly labeled but cites the other early — 2000 ND 141, 2004 ND 115, 2011 ND 65, 2012 ND 148, 2017 ND 233, and **2022 ND 123 (A.C.)** (confirms the prior A.C. fix is intact: 18052 is properly 2022 ND 169). Plus the 6 Westlaw `.doc` Group-C rows, which always mistag because Westlaw bodies never restate the neutral self-cite.
- **Refinement owed:** exclude `.doc`-sourced rows from BODYDUP's REAL determination (their label is always "absent"), so the 6 Group-C docs stop mistagging.

## Batch `fix-ctrack-clean3-2026-05-26` — 3 clean PDF-era cite-swap fixes from C-Track PDFs

First repairs of the PDF-era (Group B) scramble, using correctly-named C-Track PDFs the user pulled (canonical tree `~/refs/nd/opin`). The C-Track parser is `triage/ctrack_pdf.py` (cite/docket/caption/date/author from page-1 text; the clerk file stamp gives the filing date — note some stamps are image-only and need a visual page-1 read). Snapshot `opinions.db.bak-pre-ctrack-clean3-2026-05-26`; `detect_cite_swap` CITE flags 16 → 12; invariants 22/2/0.

- **2021 ND 163 (oid 19599) rebuilt** — label was already correct; content was an *exact* dup (jaccard 1.0) of 19583 (2021 ND 106). Rebuilt text/case_name/date(2021-09-09)/docket(20210109)/author(Tufte) from `2021ND163.pdf`; copied the PDF into `pdfs/2021/` and wrote `markdown/2021/2021ND163.md`. Recovers a genuinely-missing opinion (*Interest of K.B.*).
- **Norberg swap (19652 ↔ 19711)** — *Norberg v. Norberg*: 19652 held 2023 ND 1 under label 2022 ND 139; 19711 the reverse. Swapped the neutral-cite labels + source_paths and renamed the misnamed on-disk md/pdf files (`2022ND139` ↔ `2023ND1`). Dates already matched content (2023-01-05 / 2022-07-21).
- **Legacie-Lowe swap (19736 ↔ 19833)** — *Legacie-Lowe v. Lowe*: 19736 held 2023 ND 88 under label 2023 ND 140; 19833 the reverse. Swapped labels/source_paths + on-disk files; corrected 19833's date 2023-05-09 → **2023-08-02** (real 2023 ND 140 date; 2023 ND 88 is correctly 2023-05-09). All four on-disk PDFs now match their filenames.

Remaining PDF-era flags (12) are the tangled/conflict cases needing more C-Track pulls + the true cites of detector-invisible mislabels: Nodak↔Albertson (2023 ND 225), Sanderson↔Bohe (2025 ND 232 = *Sanderson v. Agotness*, docket 20240054, per the C-Track PDF — so "Bohe v. State" at 20224 is also mislabeled), Jesser/Pailing (real 2019 ND 283 & 287; both 19429/19433 hold *Jesser* 2020 ND 287), and the annual Petition matter (2017/2018/2019 ND 1).

## Batch `fix-archive-rebuild-2026-05-26` — 3 mislabeled 2000/2003 opinions rebuilt from archive HTML

Same failure mode as the 1997 batch, extended to the archive era (2000–2003) via a year-generalized rebuild (`triage/fix_archive_rebuild_2026-05-26.py`). 18358 *State v. Lunstad* (2000 ND 198), 18361 *State v. Lee* (2000 ND 215), 18462 *Klingenstein v. Klingenstein* (2003 ND 165): here the `case_name`/`docket`/`date` were already correct — only `text_content` had leaked (from 2000 ND 113 / 2000 ND 171 / 2003 ND 116) — so the rebuild restored the right body; archive made primary, misnamed ND markdown detached. Corpus unchanged; invariants 22/2/0; `detect_cite_swap` CITE flags 19 → 16. Snapshot `opinions.db.bak-pre-archiverebuild-groupA-2026-05-26`. **All archive-era cite-swaps (1997/2000/2003, 19 rows) are now cleared.** Remaining 16 CITE flags are PDF-era (2018–2024): 10 ndcourts.gov markdown (need court-PDF verification) + 6 Westlaw `.doc` (likely synopsis-cite false positives).

## Batch `fix-1997-archive-rebuild-2026-05-26` — recovered 16 mislabeled 1997 opinions from their archive HTML

The `detect_cite_swap` scan flagged a contiguous 1997 batch (oids 18248–18280 + 12476) created by `refs-migration-nd-opin`: each row had the **correct neutral cite and a correctly-linked archive.ndcourts.gov HTML source**, but its `text_content`/`case_name`/`docket` had leaked from a misnamed markdown file (each leaked body duplicated another opinion already in the corpus). Verified all 16: the linked archive HTML holds the row's true opinion (`triage/verify_1997_archive_2026-05-26.py`). The 14 cites that looked "missing" were never missing — only the bodies leaked.

Per user direction (rebuild from on-disk archive HTML; leave N.W.2d parallels alone), rebuilt each row from its linked `archive/1997/<docket>.htm` using the project's canonical parser (`scrape_archive.parse_opinion_page` + the year index for the clean case_name): reset `text_content`, `case_name`, `docket_number`, `date_filed`, `author`, `per_curiam`; made the archive HTML the primary source; detached the misnamed ND markdown source. All 16 are short **per curiam** Rule 35.1 summary dispositions (meta "Author: PER CURIAM" + multi-justice signature blocks; parsed length ≈ full-strip length, so no truncation) — except 12476 (*Disciplinary Board v. Schmidt*, a longer per curiam). Citations untouched (12476 keeps `566 N.W.2d 407`, distinct from 1997 ND 129's `566 N.W.2d 406`, so not contamination).

Recovered (oid: cite → true case): 18248 1997 ND 106 *Wittmayer v. ND Workers Comp. Bureau*; 18249 1997 ND 12 *Interest of M.G.*; 18250 1997 ND 121 *State v. DeCoteau*; 18251 1997 ND 13 *State v. Goebel*; 18252 1997 ND 136 *Lange v. State*; 18270 1997 ND 26 *Sailer v. Goodno*; 18271 1997 ND 27 *Hulstrand Construction v. James Cape & Sons*; 18272 1997 ND 42 *Amrein v. Amrein*; 18274 1997 ND 53 *Dvorak v. AgriBank, FCB*; 18275 1997 ND 67 *State v. Holy Bear*; 18276 1997 ND 68 *Barnes v. Gates*; 18277 1997 ND 70 *Johnson v. Schmit Brothers Construction*; 18278 1997 ND 85 *Hintz v. Hintz*; 18279 1997 ND 86 *State v. Rieger*; 18280 1997 ND 87 *Huber v. Dooher*; 12476 1997 ND 132 *Disciplinary Board v. Schmidt*. Corpus 19,889 (unchanged — updates, no add/delete); invariants 22/2/0; `detect_cite_swap` CITE flags 34 → 19. Snapshot `opinions.db.bak-pre-1997archive-2026-05-26` (text_content swaps not changelog-revertible); script `triage/fix_1997_archive_rebuild_2026-05-26.py`. **Root-cause note:** the misnamed markdown files under `~/refs/.../markdown/1997/` remain corrupt (each holds a dup of another opinion); the DB now sources these 16 from archive HTML instead, so a future full re-ingest of the markdown tree could re-introduce the leak — the markdown tree itself needs repair (tracked with the C-Track PDF pull, §3).

## Batches `section6-contam-dup-2026-05-26` + `section6-logan-2000nd203-2026-05-26` — the last 3 neutral-cite collisions; `neutral_cite_uniqueness` → 0

The final 3 `neutral_cite_uniqueness` rows were not clean twins. All resolved; the invariant is now **0** (Δ=-258 from the 258 baseline). Corpus 19,892 → **19,889**; invariants 22/2/0; 0 orphans.

- **`section6-contam-dup-2026-05-26`** (snapshot `…-pre-contam-dup-…`) — two cross-cite *duplicates* of an already-correct row, mislabeled with another case's neutral cite + that case's markdown source (CL metadata error; the page-json `NW2d/820/134.json` itself carries the bad `2011 ND 161` parallel):
  - **2011 ND 161**: owner = 15703 *Holkesvig v. Welte*. 15904 was a NW2d copy of *Disciplinary Board v. Lawler* (real = 18870, **2012 ND 161**, markdown, **per curiam**). Stripped `2011 ND 161` + detached `markdown/2011/2011ND161.md` from 15904, nulled its misattributed "Kapsner" author (18870 body confirms per curiam), merged 15904→18870 — completing 18870's `820 N.W.2d 134` parallel.
  - **2018 ND 140**: owner = 17188 *Pettinger v. Carroll*. 17469 was a NW2d copy of *State v. Peterson* (real = 19355, **2019 ND 140**, markdown). Stripped `2018 ND 140` + detached `markdown/2018/2018ND140.md`, merged 17469→19355 — completing `927 N.W.2d 74` and setting Peterson's docket 20180422 (19355 had none).
- **`section6-logan-2000nd203-2026-05-26`** (snapshot `…-pre-logan-…`) — **2000 ND 203 *Logan v. Bush***: 13291 is the full Maring opinion (body: "December 7, 2000. Opinion Denying Rehearing January 30, 2001"); its `date_filed` 2001-01-30 was the rehearing-denial date. 13290 was a 1,689-char stub holding text **leaked from 2000 ND 199 *State v. Gehring*** (which exists independently, oid 18359). Merged 13290→13291; corrected the survivor's `date_filed` 2001-01-30 → **2000-12-07**. (This leaked-stub is another instance of the adjacent-cite content-swap pattern flagged in TODO §7.)

## Batch `section6-neutralcite-twins-2026-05-26` — 14 native-neutral-cite CL double-ingest twins

The `neutral_cite_uniqueness` invariant residue (native `YYYY ND n` cites shared by two opinions) was dominated by the recurring CL double-ingest twin: an ndcourts.gov markdown row (correct early date, ¶-marked) + a CourtListener row captioned "In re X" whose `date_filed` falls on the "-25th of a later month" (a CL/WL processing artifact, not a second decision). Verified read-only (`triage/verify_neutralcite_twins_2026-05-26.py`): same docket per pair, text jaccard 0.74–0.96, and the amended/supplemental/superseded markers appear *symmetrically* in both rows (opinion text, not an asymmetric rehearing). Merged 14, keeping the markdown row (`merge_pair` leaves `text_content` untouched). Corpus 19,906 → **19,892**; invariants 22/2/0; 0 orphans; `neutral_cite_uniqueness` 17 → **3**. Snapshot `opinions.db.bak-pre-neutralcite-twins-2026-05-26` (row deletions NOT changelog-revertible); script `triage/merge_neutralcite_twins_2026-05-26.py`.

- Pairs (cite, drop→keep): 1997 ND 11 Estate of Brown (12366→12365), 1997 ND 9 A.E. (12354→12353), 1999 ND 2 Allied Mutual (12809→12808), 2001 ND 10 J.S. (13304→13303), 2001 ND 7 Howe (13300→13299), 2002 ND 6 Swanson (13500→13499), 2002 ND 9 Crary (13498→13497), 2003 ND 11 Lee (13715→13714), 2004 ND 8 W.O. (13932→13931), 2004 ND 13 Wilkes (13939→13938), 2006 ND 2 McKechnie (14392→14391), 2007 ND 9 Hsu (14686→14685), 2008 ND 9 J.S. et al. (14889→14888), 2010 ND 9 B.B. (15326→15325).
- Survivor captions: fuller/period style, annotations stripped (`(CONFIDENTIAL)`, `(CON. W/...)`, `(consol. w/...)`); confidential juvenile matters included (dedup never de-anonymizes). `In the Matter of the Estate of Fern L. Brown…` → `Estate of Brown`; `In the Interest of A.E.` → `Interest of A.E.`
- Two survivor dockets had the neutral cite stuffed into the docket field; fixed from the merged CL twin's real docket: 12353 `1997ND9` → `Criminal No. 960079`; 12365 `1997ND11` → `Civil No. 960023`.
- **NOT merged** (the 3 remaining `neutral_cite_uniqueness` rows — not clean twins): 2000 ND 203 *Logan v. Bush* (13290 stub holds text leaked from 2000 ND 199 *Gehring*; full real Logan is 13291); 2011 ND 161 and 2018 ND 140 (cite contamination across distinct cases).

## Batch `section6-defermulti-2026-05-26` — the 3 verified dups among the 9 post-1997 shared-N.W.2d-page DEFER_MULTI clusters

Re-checked the 9 stale-worklist clusters (612/638/709/711/719/742/756/766/777 N.W.2d) against the live DB. **612 N.W.2d 278** and **766 N.W.2d 437** were already resolved (the dup twin merged in earlier work; the remaining 2 rows on each page are distinct opinions — 2000 ND 126 + 2000 ND 127; 2009 ND 91 + 2009 ND 104). **709/711/719/742/756** are NOT dups: distinct opinions sharing a summary-disposition N.W.2d page — their only defect is the missing neutral cite (tracked under the §6 no-neutral-cite item, not here). The remaining **3 were verified true CL double-ingests** (head/tail text read; same docket per pair; the CL row's own body states the *earlier* decision date — its later `date_filed` is a CL/WL processing artifact) and merged. Keep = the ndcourts.gov markdown row (authoritative ¶-marked text; `merge_pair` leaves `text_content` untouched). Corpus 19,909 → **19,906**; invariants 22/2/0; 0 orphans; `neutral_cite_uniqueness` 20 → 17. Snapshot `opinions.db.bak-pre-defermulti-2026-05-26` (row deletions NOT changelog-revertible); script `triage/merge_defermulti_2026-05-26.py`.

- **638 N.W.2d 45** — *In re J.S. / Pryatel v. J.S.* 2002 ND 7: merged 13504 (CL "2002 WL 49271", `date_filed` 2002-07-25; body says "January 15, 2002") → **13503** (markdown `2002ND7.md`, 2002-01-15). docket 20010314, VandeWalle C.J. Survivor caption `Interest of J.S.  (CONFIDENTIAL) (see Docket Memo)` → **`Interest of J.S.`** (annotation stripped per the modern-dedup caption policy; dedup never de-anonymizes).
- **777 N.W.2d 62** — *Matter of Hanenberg / Cass County State's Attorney v. Hanenberg* 2010 ND 8: merged 15333 (CL "2010 WL 114285", `date_filed` 2010-08-25; body says "January 12, 2010") → **15331** (markdown `2010ND8.md`, 2010-01-12). docket 20090135, Sandstrom J. (This is the page the earlier *Everett v. State* 2010 ND 4 contam-strip pointed to.)
- **2005 ND 75** — the deferred *Fire & Tornado Fund* pair (both captions mangled): merged 14224 (CL, `date_filed` 2005-04-06, `*227` star-pagination) → **14223** (markdown `2005ND75.md`). docket 20040228, Sandstrom J. Hand-picked canonical caption from CL cluster 8279538 / West: **`State ex rel. State Fire & Tornado Fund of the North Dakota Insurance Department v. North Dakota State University`**. Also fixed the survivor `judges` (was NULL in the column; merge set it to `Sandstrom`) → **`Jorgensen, Maring, Sandstrom, VandeWalle`** = the participating panel (VandeWalle C.J., Sandstrom J. auth., Maring J., Jorgensen D.J. for Kapsner who was disqualified; Neumann resigned/did not participate, per ¶¶ 35–37).

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


## Batch: const-history-pending-amendments-sessionlaw-2026-06-08 (10 finalized, 3 upgraded)

Applied 2026-06-08 to `data/constitution_amendments.json` + `constitution_history.db`
(script `scripts/apply_pending_amendments_2026-06-08.py`; full verbatim transcription
+ sources in `data/const_amend_session_law_extraction_2026-06-08.md`).

**Method change.** Retired the handoff's "backstop-first via Blue Books" workaround.
The ND Session Laws are local at `~/refs/nd/sess/` with **clean text layers** and are
the project's stated authoritative source. All 13 previously-pending amendments are now
transcribed **directly from the enacted session-law text** (the "Constitutional
Amendments / Measures — Approved" section in the volume following the ratification
election; proposed-resolution `CAP.pdf` used as a clean second witness where the
approved scan was OCR-dirty). Validated source rule: ratified year Y -> `sl(Y+1)` or
`(Y+1)_sl/{CMA,CAA}.pdf`. (Note: `1961_sl`/`1965_sl` approved file is `CMA.pdf`, not
`CAA.pdf`; legis.nd.gov has no `CAA.pdf` for those years.)

**FINALIZED (status:pending dropped, confidence high) — 10:** LV (§§167/170/172/173
amend + §171 repeal, Art. 55), LVI (new Art. 56, gasoline motor-fuel dedication —
*recovered, was "TEXT NOT FOUND"*), LVII (§82, Art. 57), LVIII (§158, Art. 58), LIX
(new Art. 59), LX (new Art. 60), LXI (§162, Art. 61), LXII (§173, Art. 62), LXIV (§138,
Art. 64), LXXIII (re-enacts amend. art. LVI, 1960).

**Source-of-truth metadata corrections:** LIX = **WWII veterans' adjusted-compensation**
bond ($27M), not "state building program"; LX = **State Medical Center** one-mill levy
at UND, not generic "state building"; LXI = **§162 permanent-school-fund investment**
(record previously had empty changes); LXII = **§173 county officers** (removes the
*sheriff* from the four-year-succession limit) — prior "school funds" heading belonged
to LXI; LVII effective_date 1940-06-25 -> **1940-07-25** (election + 30 days). ndconst.org
had LXI/LXII section numbers right but subject descriptions swapped. All effective dates
re-confirmed against the canvass vote tallies.

**UPGRADED (verified verbatim text + high confidence; STILL pending) — 3 structural:**
LXXVIII (amends only subdivision (d) of subsection 6 of amend. art. LIV), XCVI (amends
subsections 2 & 4 of amend. art. LIV), LXXXI (**partial** repeal — only the tenth
paragraph of §25). The ingest does whole-provision replacement and amend. art. LIV is a
single provision; these need the full enclosing-provision text assembled first. LXXXI
also: §25 already shows status='repealed' in the base — investigate before applying.

**DB rebuild:** `python -m ndcourts_mcp.ingest_constitution_history --apply` on a FRESH
db (the ingest is NOT idempotent — `build()` uses CREATE TABLE IF NOT EXISTS and
`apply_amendments` appends, so re-running on an existing db doubles every amendment;
delete `constitution_history.db` first). Result: provisions 243, adds 22, amends 110,
repeals 47, pending_skipped 3, unresolved 0. Verified: §82 chain 6 contiguous versions
(no dups/backwards), amend. art. LVI chains 1940->1960, point-in-time §162@1953 = LXI
text, 422 versions = 422 distinct (provision, effective_start) keys.


## Batch: const-history-bluebook-revalidation-2026-06-08 (8 corrections / 38 re-validated)

Applied 2026-06-08. Multi-agent workflow re-validated the 38 post-1955 Blue-Book-OCR-sourced
amendments (LXV-CVIII) against clean session-law text (CAA/CMA, with CAP as a clean second
witness). Scripts: validation = workflow `const-bluebook-revalidate`; verdicts archived in
`data/const_bluebook_revalidation_2026-06-08.json`; fixes = `scripts/fix_bluebook_revalidation_2026-06-08.py`.

**Result: 30 of 38 confirmed clean** (28 identical; 2 — LXXXVIII, XCIX — diverged only by OCR
noise in the session-law *scan*, stored text already correct). **8 had real errors:**

Substantive (body):
- **LXXIV (§215):** the amendment's operative rename was never applied in the stored text —
  paragraph Third still read "The Agricultural College at the City of Fargo"; corrected to
  "The North Dakota State University of Agriculture and Applied Science at the City of Fargo,
  in the County of Cass."
- **XC (§216):** stored text carried appended Blue Book editorial annotation as if enacted, plus
  3 punctuation/caps divergences; replaced with clean session-law §216. Chapter 526 SECTION 2 also
  amended subsection 1 of amend. art. LIV (Board of Higher Ed membership) — NOT applied (same
  single-provision art-LIV issue as LXXVIII/XCVI); flagged to the structural backlog.

Metadata/date:
- **LXXIX (§113):** authority chamber House -> Senate Concurrent Resolution "T"; dropped unsupported "(mislabeled T)".
- **XCIII / C:** added missing election_date (1974-11-05 / 1978-09-05).
- **CIV (§§121-129):** authority "Senate House Concurrent Resolution No. 3014" -> "House Concurrent Resolution No. 3014".
- **CV (art CV, §25, art XXXIII):** effective_date 1978-12-07 -> **1979-01-01** (express, SECTION 4 of ch. 696).
  This also **explains why §25 shows status='repealed' in the base**: CV repealed §25 (and art. XXXIII)
  and replaced it with the new Initiative/Referendum/Recall article. LXXXI's 1964 partial repeal of
  §25's tenth paragraph thus governed the 1964-1979 window — lineage consistent.
- **CVII (§173 + §69):** split effective dates — §173 amendment effective **1983-01-01** (delayed by
  SECTION 3), §69 repeal 1980-10-02. Required a 1-line ingest change (per-change `effective_date`
  override) plus a guard skipping changes effective after REORG_EVE (1980-12-31) — they belong to the
  post-1981 modern layer. The §173/1983 change is correctly `future_skipped` in the 1889-1980 layer.

**Ingest changes** (`ingest_constitution_history.py`): per-change `effective_date` override; skip
changes with eff > REORG_EVE (counter `future_skipped`). DB rebuild (rm first): provisions 243,
adds 22, amends 109, repeals 47, future_skipped 1, pending_skipped 3, unresolved 0; 0 versions with
start>end.

**Provenance upgrade:** these 38 records' authoritative basis is now documented as clean session-law
text, not dirty Blue Book OCR. Pre-1956 Blue-Book/marker-OCR amendments and the 45 marker-OCR set
remain for a later round (diff-QA).

## Batch: const-history-revalidation-round2-2026-06-08 (55 re-validated; LIV fix + 13 authority backfills)

Applied 2026-06-08. Workflow `const-revalidate-round2` diff-QA'd the 55 remaining pre-1956
amendments against cached session-law text. Verdicts archived in
`data/const_revalidation_round2_2026-06-08.json`; fixes in
`scripts/fix_revalidation_round2_2026-06-08.py`.

**33/55 confirmed clean** (17 identical + 16 OCR-only where the divergence was noise in the
session-law SCAN, not the stored text).

**Applied (survived scrutiny):**
- **LIV (art LIV):** restored the truncated tail of the enacted text (§6(d)-(e), §7, §8) from
  sl1939. The stored "[TEXT TRUNCATED ... NOT in source]" note was FALSE — the text is in the
  session law. (art LIV is the Board-of-Higher-Ed article the structural backlog depends on.)
- **Authority backfill, 13 records (XLIII-LXIII):** replaced the leaked placeholder
  `"Amendment ratified undefined"` with real session-law provenance (Article #, submitted-by,
  chapter/SL, approval date + vote tally); backfilled `election_date` where the session law
  states it. Zero "undefined"-authority records remain.

**Deliberately NOT changed (agent over-flagging caught on review):**
- **No effective_date changes.** The agents' six "date mismatch" flags compared the session-law
  APPROVAL date to the stored EFFECTIVE date; the dataset convention is effective = approval + 30
  days (e.g. amdt #2: election 1898-11-08 -> effective 1898-12-08), so the stored dates are correct.
- **#12 (§216) NOT changed — false positive.** The agent flagged a "lost rename" by matching a
  LATER §216 amendment in the wrong volume (sl1911, "Approved Feb 24 1911"). The real
  1909-proposed/1910-ratified text (sl1909) MATCHES the stored placeholder language
  ("A blind asylum ... in the county of Pembina"; forestry "at such place in one of the counties
  of McHenry, Ward, Bottineau or Rolette"; "namely"; "soldiers'"). Stored text is correct; applying
  the "fix" would have corrupted #12 with a different amendment's text.

**Deferred to the volume-corrected re-run (the 11 not_found + early-era body flags):** the early
amendments (1898-1912) print in the PROPOSING volume sl(E-1), not the sl(E+1) the workflow used
(the convention flipped ~1914-1918). So 11 came back not_found (volume miss, not data errors), and
the early-era body flags #1 (art I comma) and XXX (§177 "limitation(s)") / XXXVII (§121 "Second")
are unverified against the correct volume -> all fold into action 4.

DB rebuild: provisions 243, adds 22, amends 109, repeals 47, future_skipped 1, pending_skipped 3,
unresolved 0.

## Batch: const-history-revalidation-round3-2026-06-08 (14 early amendments, volume-corrected)

Applied 2026-06-08. Re-ran the 11 round-2 not_found + 3 early-era body flags (#1/XXX/XXXVII)
against BOTH the proposing sl(E-1) and approved sl(E+1) volumes with date-based disambiguation
(workflow `const-revalidate-round3`; verdicts in `data/const_revalidation_round3_2026-06-08.json`).
Volume fix worked: 14/14 located, 0 not_found.

Result: 10/14 clean (3 identical + 7 OCR-noise-only). Of 4 "substantive" flags, only ONE held up
on scrutiny:
- **APPLIED #1 (art I, lotteries):** removed an extraneous stored comma ("for any purpose, and" ->
  "for any purpose and"). Confirmed absent in BOTH sl1893 (proposing) and sl1895 (approved) — two
  independent witnesses, not OCR-dependent. High confidence.
- **HELD #3 (§76):** "board of pardons" (stored) vs "board of pardon" (singular, sl1899). Medium
  confidence, single-letter, old scan -> needs page-image confirmation before changing.
- **HELD XXX (§177):** "limitation" vs "limitations" read out of heavy OCR garble ("li111itatio11s").
  Medium -> needs image confirmation.
- **HELD #5&6 (§215):** agent "substantive" was capitalization ("City"->"city") + one comma;
  words/numbers identical. Cosmetic, not an error.

Also RETRACTED a round-2 false positive: **XXXVII (§121)** is OCR-only (stored "Second" is correct);
the round-2 "Second->second" flag was scan-related. Confirms the discipline of verifying early-era
"substantive" flags against the correct volume before applying.

This completes re-validation of the entire pre-1981 amendment corpus against session-law text
(rounds 1-3). Remaining: 4 structural pending (LXXVIII/XCVI/XC-subsec-1/LXXXI); optional image
confirmation of the 3 held items (#3/XXX/§5&6); optional early-record authority enrichment.

## Batch: const-history-held-items-2026-06-08 (page-image resolution of 3 held items)

Resolved the 3 round-3 held items by reading the actual session-law page images (300 dpi),
not OCR text:
- **APPLIED #3 (§76):** sl1899 pp. 256-257 clearly print "board of pardon" (SINGULAR) in BOTH
  places ("in conjunction with the board of pardon of which the governor shall be ex-officio a
  member"; "granted by the board of pardon, stating the name of the convict"). Corrected stored
  plural "board of pardons" -> "board of pardon" (2 occurrences). Now high confidence.
- **NO CHANGE — XXX (§177): FALSE POSITIVE.** sl1919 p. 519 (ARTICLE XXX) clearly prints
  "in addition to the limitation specified in Section 174" (SINGULAR). The rounds-2/3 agents
  misread a plural "s" out of the OCR garble "li111itatio11s"; the stored singular "limitation"
  is CORRECT. (Third OCR-based false positive caught, after #12 §216 and XXXVII §121.)
- **NO CHANGE — #5&6 (§215):** capitalization only ("City"/"County" vs session-law lowercase);
  cosmetic, not a textual error; left as-is.

Lesson reinforced: medium-confidence single-letter OCR diffs on old scans must be confirmed
against the page image before altering authoritative text. Page images render via
`pdftoppm -png -r 300 -f N -l N <pdf> <out>`.