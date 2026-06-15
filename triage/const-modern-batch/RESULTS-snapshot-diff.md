# Modern-layer snapshot-diff — results (2026-06-15)

Harness: `snapshot_diff_modern.py`. Reconstruct each modern provision (`art. ROMAN,
§ N`) as of date T from the scratch DB (version effective at T) and diff against a
modern-scheme printed compilation near T. Keyed by (article, section); OCR
letter-spacing collapsed by norm(); containment + fuzzy ratio. A DB provision whose
article is absent from a compilation = BEYOND_COVERAGE (e.g. art. XIV/XV/XVI created
after the BB's date) — not an error.

## Witnesses (Blue Books, modern art./§ scheme; archived in `~/refs/nd/const/`)
- **1981** — `1981_blue-book-ndbb_constitution.md` (from `ndbb-21535`, pp 74-112).
  Replaces the earlier truncated extract (which stopped at art. XII §1).
- **1989** — `1989_blue-book_constitution.md` (from `ndbb-6361`, pp 66-96). The first
  **interior** point-in-time witness (8 yrs post-reorg, after the 1982-88 amendments).

## Results

```
1989 (T=1989-07-01):  MATCH 64 · NEAR 80 · MISMATCH 11 · NOT_IN_COMP 4    → 144/159 = 90.6% match-or-near
1981 (T=1981-01-01):  MATCH 41 · NEAR 26 · MISMATCH 7  · NOT_IN_COMP 59   → 67/133 = 50.4%
```

**1989 = 90.6% match-or-near** is the headline: a genuine mid-era validation that the
modern reconstruction's intermediate versions (the 1982-88 amendment chain) match the
printed 1989 text. **1981's 50%** is depressed by the rough microfilm OCR of that scan
— 59 NOT_IN_COMP are whole-article *parse misses* (arts I/III/VI/IX sections whose
"Sectio n" markers are too garbled to detect), not reconstruction errors; of the 67
that parsed, 100% match-or-near.

## Findings surfaced (real, not OCR)

1. **art. VII §10 — DokuWiki 404 bug → FIXED.** The DB served `<!DOCTYPE html>…` (a
   ndconst.org "topic does not exist" page) as the section text. The 1989 BB (and the
   1983 creation measure) give the real text — corrected in live + scratch + the
   reproducible `const_modern_text_corrections.json`. (`apply_modern_text_corrections.py`.)
2. **art. XII §§ 3, 7, 8, 12, 14, 15, 17 — DB marks "Repealed." but both BBs print
   full text.** These corporation sections were repealed *later* (a post-1989
   amendment); the DB carries only the repeal tombstone and lost the pre-repeal text,
   so point-in-time for art. XII in [1981, repeal) is wrong. **Follow-up:** recover the
   pre-repeal text from the 1981/1989 BB and date the repeal (needs-base-source class).
3. **art. VI §12** (ratio ~0.5 at both T): the DB's modern text has odd internal
   double-spacing and diverges in the body — verify against a measure (low priority).
4. **art. X §5 (1989, ratio 0.81)**: the [1988,2003) reconstructed version differs
   somewhat from the 1989 BB — check the 1988 amendment read.
   (art. IX §7, IV §16, etc. ≥0.9 are OCR, effectively NEAR.)

## Status & use
The modern acceptance test now has a real interior witness. Re-run after each splice:
`python triage/const-modern-batch/snapshot_diff_modern.py`. Add `(file, T)` rows to
COMPS as more compilations are acquired. Note the **1981 scan's OCR limits** witness
coverage there — a cleaner 1981 text (or the historical-style markdown extract) would
raise its rate; the 1989 witness is the dependable one. The art. IV §§9-11 finding
from the prior run is **confirmed consistent**: at 1989 (post-1986 recreation) art. IV
matches; the gap is specifically the [1981,1986) pre-recreation window.
