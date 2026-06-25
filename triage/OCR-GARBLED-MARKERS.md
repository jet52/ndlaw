# OCR-garbled paragraph markers — 30 FIXED, 5 deferred (2026-06-25)

35 paragraph markers had the number itself OCR-garbled (digit misread as letters), left by the
despacing pass. Fixed by **sequence continuity**: the value is determined by the neighbours
(preceding marker N-1, following N+1, target value absent → garbled = N), which is independent
of the glyph. Spot-verified against PDF images (1997 ND 7, 2008 ND 115 confirm `[¶N]` no-space;
id16543 confirmed S→3; id12931 region).

## FIXED (30) — batch `ocr-garbled-markers-2026-06-25`
Sequence-determined, gap of exactly one integer, target value not already present. Examples:
`[¶ IB]`→`[¶13]` (×7), `[¶ ll]`→`[¶11]`, `[¶ l]`/`[¶ i]`/`[¶ I]`→`[¶1]`, `[¶ S]`→`[¶3]`/`[¶8]`
(by position), `[¶ IS]`→`[¶13]`/`[¶18]`/`[¶19]`, `[¶ IQ]`/`[¶ TO]`→`[¶10]`, `[¶ Í4]`→`[¶14]`,
`[¶ Í5]`→`[¶15]`, `[¶ [¶4]`→`[¶4]` (doubled bracket collapsed).

## DEFERRED (5) — `triage/marker-fix-defer.json` — need per-opinion renumber reconciliation
These failed the strict gap-of-one rule (no integer fits between neighbours) because the
opinion's numbering is itself anomalous relative to the court PDF:
- **id12623** `[¶ ll]` — prev=8, next=12 (paras 9-11 region gap; ambiguous which value).
- **id13427** `[¶ T2]` — prev=11, next=12 (no gap; final-disposition paragraph + footnote markers).
- **id15794** `[¶ Í0]` — prev=9, next=10. **Court PDF has a DUPLICATE `[¶10]`** (two consecutive
  paragraphs numbered 10) and the DB markers are off-by-one around it. (under user review 2026-06-25)
- **id16543** `[¶ S]` — prev=2, next=3. Image shows the S-paragraph IS `[¶3]`, but DB already has a
  separate `[¶3]` after → off-by-one renumbering, not a simple glyph fix.
- **id16642** `[¶ ÍÓ]` — prev=9, next=10. Section heading `HI` (="III") + duplicate-ish `[¶10]`.

Each needs the full opinion renumbered against the court PDF image, not a single-marker fix.
