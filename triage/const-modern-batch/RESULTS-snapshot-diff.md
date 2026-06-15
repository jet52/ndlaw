# Modern-layer snapshot-diff — results (2026-06-15)

Harness: `snapshot_diff_modern.py`. The modern-scheme counterpart of the historical
acceptance test — reconstruct each modern provision (`art. ROMAN, § N`) as of date T
from the scratch DB (version effective at T) and diff against a modern-scheme printed
compilation near T. Only one post-reorg compilation is on disk (the **1981 Blue
Book**), so **T = 1981-01-01** is the anchor.

## Result (T = 1981-01-01, vs the 1981 Blue Book)

```
DB modern provisions at T: 133    compilation sections parsed: 177
MATCH 79 · NEAR 24 · MISMATCH 6 · NOT_IN_COMP 6 · BEYOND_COVERAGE 18
match-or-near (within BB coverage): 103/115 = 89.6%
```

**89.6% match-or-near** against an OCR'd, partially-truncated witness — the modern
reconstruction's [1981, d1) heads + unchanged-since-reorg provisions substantially
agree with the printed 1981 text. (norm() collapses the BB's pervasive letter-spacing
OCR — "p ai d ou t" → "paidout" — so most letter-spaced sections still MATCH/NEAR.)

## Triage of the non-matches

- **BEYOND_COVERAGE (18) — not errors.** The 1981 BB markdown on disk is **truncated
  at art. XII § 1** (file ends mid-section). art. XII §§ 2-17 and art. XIII have no
  witness. *Acquire a complete 1981 BB to extend coverage.*
- **NOT_IN_COMP within coverage (6): BB parse misses, not reconstruction gaps.**
  I§18, IX§13, VIII§3, X§8, XI§4, XI§22 — the DB has them; the BB section marker
  wasn't captured (e.g. VIII§3's marker is mid-line: "…given as Section 3. far as
  practicable…"; others are letter-spacing edge cases). Witness-parse limits.
- **MISMATCH (6):**
  - **art. IV §§ 9, 10, 11 — REAL FINDING (the 1985 art. IV recreation).** At T=1981
    the DB has only these three art. IV sections (the rest were *created* 1986); but
    they carry **post-1986-renumbering content** (§9/§10 stamped 1889-10-01 as
    "unchanged"; §11's chain head predates 1986). The 1985 measure renumbered art. IV,
    so the 1981 §§9-11 were different provisions. **The modern layer does not model
    the art. IV [1981,1986) content for these carried sections** → point-in-time for
    art. IV in that window is wrong. Follow-up: reconstruct the pre-1986 art. IV from
    the 1985 measure + 1981 BB (akin to the art. V replacement case).
  - **art. IX §7 (0.9), art. VI §12 (0.5), art. XII §1 (0.78): OCR / truncation, not
    real.** Same opening text as the BB; depressed ratios from BB char-corruption and,
    for XII §1, the BB section is itself cut off (truncation).

## Status & use
The harness is the **modern acceptance test** — re-run after each splice (`python
triage/const-modern-batch/snapshot_diff_modern.py`). Add `(file, T, ceiling)` rows to
`COMPS` as more compilations are acquired. To strengthen validation: (1) a **complete
1981 BB** (current copy truncates at art. XII §1); (2) a **mid-era modern compilation**
(1990s/2000s) for a true interior point-in-time check — none is on disk. The lone
reconstruction issue surfaced is the **art. IV §§9-11 / 1985-recreation gap**.
