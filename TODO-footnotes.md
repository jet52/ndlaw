# TODO — Footnote handling (parser coverage + data recovery)

Planning doc for the footnote work surfaced during the 2026-06 footnote-pinpoint
arc (see `project_footnote_pinpoints`, `project_westlaw_footnote_loss`). Captures
the design decision (normalize at *read* time, not in stored bytes) before any
code. Sequence: **Phase 1 (parser) → Phase 2 (data recovery + analyzer fix)**.

## Problem

The footnote-aware pinpoint feature (v1.1.0) resolves footnote quotes to `¶ N
n.X`, but only for one of several storage formats, and the underlying text has
genuine footnote losses.

Surfaced by a citation-graph scan (`triage/footnote-pincite-losses-2026-06-23.tsv`):
for every `YYYY ND N, ¶ X n.Z` pincite in the corpus, check the cited case for
footnote Z. Of 286 unique references —

| Result | Count | Meaning |
|---|---:|---|
| Present (period format) | 198 | tool detects it |
| Present but **tool-blind** | 63 | footnote stored in `NOTES\n[N]` format the parser can't read |
| **Truly missing** | 16 | footnote gone from our copy entirely |

Footnotes appear in ≥3 storage formats across the 1997+ corpus:

| Format | Rendering | ~Opinions | Lineage | Parser |
|---|---|---:|---|---|
| `period` | ` N\n\n. body` (West "N." split by OCR) | 649 | NW2d / West .doc | ✅ handled |
| `NOTES[N]` | `NOTES\n[1] body\n[2] body` | 228 | ndcourts markdown | ❌ blind |
| `FOOTNOTES:N` | `FOOTNOTES\n\n1:\n\nbody` (often OCR-garbled, e.g. 2017 ND 146 → `0:\n\nュボĖ`) | some | ndcourts markdown | ❌ blind |

The "truly missing" set spans **1999 → 2024** and is all ndcourts-markdown-sourced.
Verified against the authoritative PDF: **2024 ND 99**'s PDF carries footnote 1
("Section 29-32.1-09, N.D.C.C., was amended effective Aug. 1, 2023…"); our
markdown-derived text dropped it. So this is an **active ingest gap**, not legacy —
the loss is ongoing in new opinions and recoverable from the PDFs.

## Design principle — three layers; consistency lives above the bytes

Treat each opinion as three layers and only ever touch two of them:

1. **Content** — the court's actual words. Immutable, verbatim (incl. typos
   present in both PDF and reporter — `feedback_preserve_source_typos`).
2. **Structure** — *our* annotations: `[¶N]` markers, footnote call→body linkage,
   `*NNN` star pages. Navigational; may be canonicalized.
3. **Artifact** — pipeline noise: OCR soft-hyphens, the ` 1\n\n. ` period-split,
   the garbled `FOOTNOTES\n\n0:\n\nュボĖ`. Errors; should be removed.

**Rule:** normalize/parse the structure layer, delete the artifact layer, never
touch the content layer. The acceptance test for any change is a *word-level diff
against the authoritative PDF* — whitespace/delimiter/marker-only changes are
safe; a change to a character of the court's words is not.

## Normalization decision

- **Canonical *read* interface — YES.** `proofread.footnote_structure()` is the
  single point that maps every storage format to one structured output
  `{num, call_paragraph, body_span}`. Consumers see uniform data regardless of how
  it's stored. A read-time parser is stateless and reversible by nature — nothing
  to changelog, revert, or re-verify, and a new format is one parser change, not a
  data migration.
- **Rewriting stored `text_content` to one format — NO** (except garbles, below).
  It edits historical bytes for cosmetic gain and would need changelog +
  reversibility + PDF re-verification per edit. The read-time parser already
  delivers the consistency.
- **OCR-*garbled* footnote sections — surgical fix, verified vs PDF.** The
  `0:`/`ュボĖ` class is artifact cleanup (same discipline as the Lyon OCR fix,
  batch `lyon-ocr-2026-06-22`), not reformatting.
- **Recovered footnotes (Phase 2c) — write canonically.** When we add a footnote
  the analyzer dropped, we author those bytes, so we write them in one clean form
  (` N\n\n<body>` standalone, which the parser links for free). Consistency where
  we author; preservation where the source spoke.

## Phase 1 — parser coverage (contained, zero data risk)

Extend `proofread.footnote_structure()` to recognize, in addition to `period` and
the tail-after-last-`[¶]` rule:

- **`NOTES[N]`**: a `NOTES` header (or bare `[N]` note lines) → body keyed by N;
  call paragraph = paragraph of the inline `[N]` call (distinct from `[¶ N]`).
- **`FOOTNOTES:N`**: a `FOOTNOTES` header then `N:` openers → body keyed by N.

Contract unchanged: returns `{"bodies": [(num,start,end)], "call_para": {num:¶|None}}`,
so `locate_quote` / `get_pinpoint` / `verify_quotation` and the era tests need no
change. Add per-format fixtures to `tests/test_footnote_pinpoints.py`
(`NOTES[N]`: 1999 ND 134; `FOOTNOTES:N`: a clean exemplar). Re-run the citation-graph
scan afterward — the 63 "tool-blind" should flip to present, isolating the true
losses.

Files: `ndcourts_mcp/proofread.py`, `tests/test_footnote_pinpoints.py`.

## Phase 2 — data recovery + root cause (sequenced)

- **(a) Audit** all ~7,200 markdown (1997+) opinions: footnotes-in-text vs
  footnotes-in-PDF → categorize `PRESENT-ok` / `GARBLED` / `MISSING`. Generalizes
  `scripts/audit_westlaw_footnotes_2026-06-22.py`; PDF is the oracle
  (`feedback_verify_against_pdfs`). The citation-graph worklist
  (`triage/footnote-pincite-losses-2026-06-23.tsv`, 16 cases) is the floor, not
  the ceiling — it only catches footnotes another in-corpus opinion pincites.
- **(b) GARBLED** → surgical OCR fix vs PDF (changelog-logged, batch per cohort).
- **(c) MISSING** → recover the body from the PDF, append canonically, logged.
- **(d) Root cause — analyzer fix (lives in the `scraper` repo).** The PDF→markdown
  extraction drops/garbles footnotes at ingest, so new opinions keep losing them.
  **Main detail and tracking: `~/code/scraper/FOOTNOTE_EXTRACTION_FIX.md`**
  (likely site `scraper/pdf_processor.py`). This repo only *consumes* `~/refs`
  markdown; the fix must land upstream. Once fixed, re-extract affected opinions
  and re-ingest under the reconcile/write-guard (`project_silent_reversion_recovery`)
  so other corrections aren't clobbered.

## Pre-1997 footnotes anchor to the star page, not a paragraph

Pre-1997 opinions have no `[¶N]` markers, so `call_para` is always `None`
(`find_paragraph` over an empty marker list). The locational anchor there is the
**reporter star page**: the call sits on a `*NNN` page. Confirmed on 43 N.D. 156 —
0 `[¶]` markers, the call (`…May 28, 1905,1…`) is on `*812`
(`star_page_before(call) = 812`).

Design consequences:

- The structured contract should expose a **`call_page`** (`star_page_before(call_pos)`)
  alongside `call_paragraph`; pre-1997 pinpoints become "`<reporter> at <page> n.X`".
- **`call_page` is N.W., not N.D.** — the Westlaw `.doc` for bound N.D. Reports
  carries N.W. pagination (`project_bound_nd_reports_volumes`), so star pages are
  N.W. pages. An N.D.-Reports page pincite is NOT recoverable from this text; only
  "`<vol> N.W. at <page> n.X`". Don't promise an N.D. page.
- **Recovery placement (Phase 2c) must preserve page locality.** Appending a
  recovered footnote at end of text breaks the anchor: on 2222 the call is on
  `*812` but `star_page_before(end) = 817`. So insert the body at its print
  position (right after the call's star page) OR record `call_page` explicitly —
  never append at end. The two already-restored footnotes (batch
  `westlaw-footnote-restore-2026-06-22`, ids 2222/4906) need redoing under this
  rule, and aren't currently detected anyway (non-period append, no markers).

## Open questions

- Phase 2a categorizer: detect "this opinion *should* have footnotes" — rely on
  PDF footnote markers, or also mine in-text call markers? (PDF is authoritative.)
- Recovery linkage for pre-1997 (no `[¶]`): retention only, `paragraph=None`
  (as with the restored Westlaw footnotes).
- Whether to record per-opinion footnote format + coverage in `quality_scores` /
  `print_anomalies` so the gap is tracked, not silent.

## Cross-references

- Upstream analyzer fix (Phase 2d): `~/code/scraper/FOOTNOTE_EXTRACTION_FIX.md`
- Memory: `project_footnote_pinpoints`, `project_westlaw_footnote_loss`
- Worklist: `triage/footnote-pincite-losses-2026-06-23.tsv`
