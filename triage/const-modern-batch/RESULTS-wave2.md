# Multi-agent redline campaign — Wave 2 results (2026-06-14)

Prep v2 (anchor + render-all + filename-honoring resolver) recovered the 51
Wave-1 skips. 8 read-agents over 49 newly-prepped provisions + 1 agent doing
confirming second reads of Wave-1's 10 `needs-2nd-read` + 1 adjudication agent.
Main-context verification (mechanical + agreement + 3rd-read) on every result.

## Prep v2 fixes (all in `prep.py` / `scripts/reconstruct_modern_versions.py`)
- **resolve_pdf honors the exact source_url filename** (case-insensitive): a
  session dir holds many measure files (CAA vs IMA vs INITM/CNSTM); blind
  CAA-glob mis-resolved initiated-measure cites (art I §1, X §25, XI §28).
- **Locate by `#page=N` anchor, or render the whole file when small (≤12pp).**
  Replaces the pdftotext content-scan, which blanked because these session-law
  PDFs store body text in AcroForm field XObjects pdftotext drops. mutool draw
  flattens them; agents read the images. 49/56 located (7 giants remain).
- **Render slug prefixed with the session dir** — fixed a collision where 1985
  CAA and 1991 CAA both wrote `CAA-p01.png` (second overwrote first).

## Disposition of the 59 read provisions
- **REDLINE, reconstructed → scratch (13):** art II §1, III §5/6/7, VI §13,
  IX §4/6/7/10, XII §1/2/6, XIII §2. All MECH-passed (apply(edit_list,current)==prior).
- **CREATE_SECTION — single version already correct, NO reconstruction (34):**
  art I §25; II §3; IV §1/2/7/8/12/14/15/16; VII §1-7,9,10,11; X §22/23/25/26/27;
  XI §26/27/28/29; XIII §4; XIV §1-4. (art VII = new home-rule article 1983,
  old art VII repealed; art IV = renumber-create 1985; the rest are new sections.)
- **needs-base-source → native-source / crosswalk bucket (12):** art V §2-11
  (1997 full executive-article REPLACEMENT — prior not in the measure), art I §1
  (1985 clean reprint, no markup), art X §6 (2012 bare repeal), art XIII §1
  (1996 — struck subsections 2-3 absent from current_text; can't rebuild from current).

## Second reads — independent agreement on Wave-1's 10
All 10 re-read independently (fresh agent, 450-dpi crops). MECH ok on all 10.
- **7 AGREE with Wave-1** outright: art III §5/6/7, IX §4/6, XII §6, XIII §2 → confirmed.
- **3 DISAGREE → 3rd-read adjudication (450 dpi, image evidence):**
  - **art XII §2 → second read correct.** Wave-1 prior was grammatically broken
    ("but the *All corporations* existing… hold the charter"); the added 2006
    sentence "All corporations existing or hereafter chartered hold the charter…"
    is underlined. **Scratch text CORRECTED** to the second read.
  - **art VI §13 → Wave-1 correct.** All three subsection numbers "1./2./3." are
    underlined (added in 1998); prior is one unnumbered paragraph (drop the "1.").
  - **art IX §10 → Wave-1 endorsed** but the 3rd-read reasoning on the tiny
    "And the. The" / "rental[,] and disposal" span was internally shaky →
    **kept Wave-1, flagged for a final pre-live check.**
  Net: all 10 second-reads adjudicated — 9 stand on Wave-1 text, XII §2 corrected.

## Splice (scratch only — `/tmp/const-scratch.db`)
- Corrected art XII §2 prior (batch `modern-redline-wave2-2026-06-14`).
- Spliced 3 NEW redlines (art II §1, IX §7, XII §1) — MECH-passed, single read,
  no clean-BB witness → flagged `needs-2nd-read`.
- **Modern reconstructed coverage: 19 → 22 provisions.** Integrity 0/0.

## Data-quality findings (separate cleanup, logged for the DB owner)
- **art VII §10 `current_text` is a DokuWiki "topic does not exist" 404 HTML page**
  — a bad ndconst.org scrape; needs the real §10 text.
- art XI §29: session law reads "farmers and ranches" where DB has "ranchers" —
  preserve-source question (the measure is the enacted text).
- art XI §26: source "co-equal" vs DB "coequal".
- art IV §16 `current_text` ends with a codifier note "Sections 17 and 18. Repealed."
- art VI §13 `current_text` carries a stray " ])]" extraction artifact (dropped in prior).

## What's left (later waves)
- **~22 multi-amendment provisions** — need each intermediate version's reprint,
  chained (see art X §21 in `transcriptions.json` for the 3-version pattern).
- **7 giants** (art XV §1-6 = new 2022 article; art IX §12 = 2023) — almost
  certainly CREATE; confirm after downloading the whole-session PDFs.
- **12 needs-base-source** + the heavy multi-subsection class (art VIII §6, etc.)
  → PL-SOURCE-FILES (request native session-law text from Legislative Council).
- **Promotion to live** still gated: every spliced provision needs a BB witness
  or a confirming second read (the 3 new Wave-2 redlines + art IX §10 flag remain),
  AND a modern snapshot-diff. Modern stays scratch-only until then.
