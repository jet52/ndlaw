# Corpus-wide proofing — plan (draft for review)

Goal: raise the whole 19,793-opinion corpus toward an **authoritative** digital
edition the ND Supreme Court could adopt. A fleet of read-agents proofs every
opinion (backward from present), validates against the authoritative source for
its era, and **proposes** corrections; a gated layer applies only what's verified.

## 0. The crux (read this first)
The entire effort lives or dies on one rule: **a false correction to authoritative
text is far worse than a missed one.** Everything below is built around that.
- Agents fix **transcription fidelity only** — places where our DB diverges from
  what the court actually printed. They do **not** edit the court's grammar,
  spelling, punctuation, or style. If the printed source has a typo, it stays
  (preserve-source-typos; a hard rule we already follow).
- Agents **propose + cite evidence + label confidence**; they never apply.
- Numbers, citations, quotations, dates, party names → **FLAG, don't auto-fix**
  unless the source positively shows the correct value. (Digit-flips burned us
  before: never from a single noisy text layer — 3/693 ToUnicode rejects.)

## 1. Corpus map & where the value is
| era | opinions | authoritative source on disk | error profile | ROI |
|-----|---------:|------------------------------|---------------|-----|
| 2015+        | 3,013 | court PDF (`pdfs/<yr>/<cite>.pdf`) | clean; structural only | low |
| 1997–2014    | 4,190 | court PDF | PDF-era; ingestion gaps, paragraph/heading seq | medium |
| 1953–1996    | 6,068 | N.W.2d reporter (`NW2d/`), West `.doc` | OCR (reporter scans) | **high** |
| pre-1953     | 6,522 | N.D. Reports + West `.doc`, page images | heavy OCR + syllabus | **high** |

Working backward from present (user's call) is good for **calibration** — modern
text is clean, so early batches are cheap and let us tune the prompt before
spending big tokens on the OCR-heavy eras where the real payoff is. Be explicit:
the early batches will have low yield; that's expected and useful.

Note: PDF and the modern markdown are **not independent** (markdown was derived
from the PDF). So for 1997+ a PDF↔DB diff catches *ingestion* errors, not OCR.
The genuine OCR hunting ground is 1889–1996 (reporter scans / West docs).

## 2. Three-layer architecture
**Layer A — deterministic pre-pass (cheap, whole-corpus, zero tokens).**
Run code detectors over every opinion first; their output is a per-opinion
*structural report* handed to the agent so it never burns tokens re-deriving what
code can find exhaustively:
- `[¶N]` paragraph-marker sequence (gaps / dupes / out-of-order) — extends invariants.
- section-heading sequence (I/II/III…, A/B/C…, numbered parts).
- star-page `*NNN` monotonicity.
- blank-line / whitespace anomalies (3+ newlines, mid-sentence hard breaks, double spaces).
- citation spacing & known-bad OCR glyph scan (£, ■, l/1/I runs, `rn`, ligatures) — extends `audit_corpus.py`.
- footnote structure (already have `proofread.footnote_structure`).
This layer alone is high-value and should run corpus-wide **before** any agents.

**Layer B — agent fleet read (the expensive core).**
One read-agent per opinion. Receives: DB text + structural report + era + the
authoritative source (PDF text via `pdftotext`, or the `.doc`/reporter markdown,
path from `opinion_sources`). Proofs across all error classes, verifies each
proposal against the source, returns structured proposals + flags. Prompt in
`corpus-proofing-prompt-v1.md`.

**Layer C — gated apply (per class).**
Reuse the footnote-pipeline discipline: byte-exact unique anchor, change confined
to its declared class, word-multiset preserved for single-char OCR swaps, sequence
actually restored. Tiered verification:
- T1 auto-gate: mechanical classes (whitespace, split/join, glyph swaps with
  word-multiset preserved) → gate-apply.
- T2 skeptic agent: a second agent re-verifies every numeric/citation/quotation/
  missing-text proposal against the source, prompted to **refute**.
- T3 human spot-check: you sample N per class per batch.
Everything logged to `changelog` + `CHANGELOG-data.md` (reversible by batch).

## 3. Batching & the refinement loop
- Batches of ~30–50 opinions, date-descending, **one era at a time** (the prompt
  specializes per era — modern = structure-first, pre-1953 = OCR + syllabus).
- After each batch the main loop: (a) tallies proposals by class + accept/refute
  rate, (b) updates the prompt — add newly-seen error patterns, suppress
  false-positive classes, tighten verify rules — bumping `prompt-vN`, (c) feeds
  the refined prompt to the next batch. Prompt is versioned; each batch records
  which version it ran.
- A running **coverage ledger** (`triage/corpus-proofing-coverage.tsv`): opinion
  id, era, prompt version, status (clean / proposals-pending / applied), counts.

## 4. Sources the agents may use (on disk + MCP — no live Westlaw)
- court PDF: `~/refs/nd/opin/pdfs/<yr>/<cite>.pdf` (7,038 on disk) via `pdftotext`/`mutool`.
- West `.doc` (RTF): `~/refs/nd/opin/N.W.2d|N.W./...` — use the RTF parser approach.
- reporter markdown: `NW2d/`, `NW/` ; bound N.D. Reports page images (`_bound-volume.pdf`, `mutool draw` ≥300dpi).
- MCP: ndlaw / CourtListener for cross-checking citations & parallel cites.
- `opinion_sources` table gives each opinion's available source files + is_primary.
"Westlaw" authoritative = the `.doc` files we already hold; there is no live login.

## 5. Cost & tiering (be honest)
Footnote read-agents ran ~40k tokens/opinion. A full proof (whole opinion + PDF
diff + multi-class) is heavier — est. **~50–70k tokens/opinion**. Whole corpus ≈
**1–1.4B tokens**. That is real even on a generous subscription. Recommended tiering:
- **2015+ (3k):** Layer-A deterministic only + a *cheap* (haiku) scan that escalates
  only flagged opinions to a full read. Don't full-read clean modern text.
- **1997–2014 (4.2k):** full read, PDF↔DB ingestion diff (sonnet).
- **1953–1996 + pre-1953 (12.6k):** full read + source OCR validation (sonnet/opus);
  this is where the budget should go.
Model choice per era is a lever; the prompt is identical, only `agentType`/model changes.

## 6. Pilot (recommended before committing the full run)
Two calibration batches, ~30 opinions each, run + fully reconciled:
1. **2024–2025** (cleanest) — calibrate structural detectors + false-positive rate.
2. **~1915 pre-1953** (hardest OCR + syllabus) — calibrate OCR/source-validation.
Deliver: yield per class, false-positive rate, tokens/opinion, refined prompt-v2,
and a go/no-go cost projection for each era. ~80–120k tokens total for the pilot.

## 7. Coordination
- **Footnotes are out of scope here** — handled by the active West-doc/archive
  pipeline. Agents only *flag* footnote anomalies, never edit them.
- Don't re-litigate closed classes (digit-flips corpus-closed; justice-name garbles
  done) except to flag residue.

## 8. Open decisions for you
1. **Scope/budget:** full corpus (~1–1.4B tok) vs OCR-heavy eras only (1889–1996,
   the high-ROize ~12.6k) vs modern-first calibration then decide. (I lean:
   pilot → then 1889–1996 → then decide on modern.)
2. **Apply policy:** confirm T1 auto-gate for mechanical classes, human review for
   all numeric/citation/quotation/missing-text. (I lean: yes.)
3. **Whitespace normalization** changes a LOT of bytes corpus-wide — do we want it,
   or treat blank-line cleanup as cosmetic and lower priority? (I lean: do split/join
   and mid-sentence rejoins; defer pure blank-line cosmetics.)
4. Model tiering per era as in §5? (I lean: yes.)
