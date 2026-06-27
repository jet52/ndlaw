# Structural paragraph-marker defects — queue (opened 2026-06-27)

A DIFFERENT class from the now-closed garbled-marker queue. These markers are
well-formed `[¶N]` glyphs, but the **sequence** is wrong: a number is missing
(gap) or repeated (duplicate). Surfaced while closing the garbled-marker queue —
fixing the garbled glyphs left some opinions with a visible gap/dup that predated
the glyph defect.

## Confirmed-real members (found adjacent to garbled-marker fixes, PDF-checked)
- **12932** (1999 ND 138) — pervasive OCR corruption; markers garbled as `[2] 9]` /
  `[3][¶`; needs a FULL re-proof, not marker surgery. (Deferred from garbled queue.)
- **14532** (2006 ND 116) — `[¶13]`/`[¶14]` markers missing (text present per PDF);
  signature ¶15 also shows a lead-author/order discrepancy (DB starts "CAROL RONNING
  KAPSNER", PDF "[¶15] Gerald W. VandeWalle, C.J., …") — verify signature content.
- **16777** (2016 ND 168) — duplicate `[¶6]` (two paragraphs both marked 6) + missing
  `[¶28]` (PDF confirms the run goes …27, 28, 29). Resolve dup-vs-restart and the gap.
- **12624** (¶4 missing), **13562** (dup ¶16 + missing ¶17), **14609** (¶17 missing),
  **16766** (¶4, ¶21 missing) — pre-existing gaps/dups confirmed present before the
  garbled-marker edits; verify against PDF.

## Corpus-wide scan (heuristic — `triage/structural-markers-scan-2026-06-27.json`)
- **339 GAP candidates** (missing N in a ≥85%-monotone marker stream)
- **148 DUP candidates** (a number repeated)
- 26 opinions in both buckets

**The scan is noisy — do NOT bulk-apply.** Known false-positive sources:
1. **Quoted numbered orders / restarts** (rule 7): an opinion quoting a numbered
   document legitimately repeats/restarts `[¶N]`. These show as dups but are correct.
   Check resume + differing text + quote-intro context (see
   `feedback_paragraph_restart_discrimination`).
2. **Long missing-runs** (e.g. 12365 missing 32–81, 12396 missing 31–80): max number
   far exceeds present count — likely markers lost in bulk during ingestion, OR a
   high pincite mis-captured. Investigate before trusting the "gap" framing.
3. Single-gap, high-monotone cases (e.g. 12386 missing ¶21, 12395 missing ¶8,
   12402 missing ¶16) are the most likely genuine, tractable fixes — start here.

## Method (per item)
Sequence alone is NOT sufficient (restart trap). For each: read the DB region,
pull the court PDF (`~/refs/nd/opin/pdfs/<yr>/<cite>.pdf`, `pdftotext -layout`),
confirm whether the printed opinion has that paragraph number, then MOVE/INSERT the
marker or delete the duplicate copy. A missing marker whose paragraph text is also
absent is a `missing_text` defect (restore VERBATIM from PDF or flag). Log every
edit to `changelog` + `CHANGELOG-data.md`; run detector + invariants + tests after.

## High-confidence members from the P37 fleet (PDF-verified, 2026-06-27)
`triage/p37-flags-2026-06-27.json` — the fleet agents FLAGGED (did not auto-fix) 59
non-markup structural anomalies, each already checked against the court PDF. These
beat the noisy corpus scan as a starting worklist. Includes several **dropped
signature blocks** (missing_text — high value for an authoritative edition): id17025
(missing `[¶20]` signature), id17017 (missing `[¶24]`/`[¶25]` signature), plus
duplicate-marker cases (id17034 dup `[¶8]`, id17031 two `[¶36]`, id17020 malformed
curly-brace dup) and 10 `ocr_digit` CITATION flags (high-risk — verify per rule 4,
do not apply from the text layer alone). Work these before the corpus scan.

## Recommended sequencing
This class is large enough to fold into the corpus-proofing fleet (the per-opinion
agents already verify against the PDF and can propose marker MOVE/INSERT). The
standalone single-gap subset (#3 above) is a good warm-up batch to refine the
detector's restart-exclusion before a full pass.
