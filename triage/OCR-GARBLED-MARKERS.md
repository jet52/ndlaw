# OCR-garbled paragraph markers (35) — follow-up queue

After the corpus-wide `[¶ N]`→`[¶N]` despacing (batch `despace-paragraph-markers-2026-06-25`,
85,109 markers), 35 paragraph markers remain where the number itself is OCR-garbled (a digit
misread as letters). These were intentionally left untouched by the digit-anchored despacer —
they need per-item OCR-digit correction, image-verified against the bound PDF (do NOT trust the
PDF text layer for digits — see [[project_digit_flip_ocr_class]]).

List: `triage/ocr-garbled-paragraph-markers.json` (opinion_id + marker).

Likely readings (verify against image before applying):
- `[¶ IB]` ×7 → `[¶18]`     - `[¶ S]` ×6 → `[¶5]`      - `[¶ ll]` ×5 → `[¶11]`
- `[¶ l]` ×4 → `[¶1]`       - `[¶ IS]` ×3 → `[¶15]`    - `[¶ i]`/`[¶ I]` → `[¶1]`
- `[¶ T2]` → `[¶12]`        - `[¶ Í0]` → `[¶10]`       - `[¶ Í4]` → `[¶14]`
- `[¶ IQ]` → `[¶10]`        - `[¶ ÍÓ]` → `[¶10]`       - `[¶ TO]` → `[¶10]`
- `[¶ Í5]` → `[¶15]`        - `[¶ [¶4]` → doubled marker (`[¶4]`), check context

Each needs: render the opinion's PDF page (`mutool draw -r 300`), read the actual paragraph
number, confirm sequence continuity with surrounding markers, then correct.
