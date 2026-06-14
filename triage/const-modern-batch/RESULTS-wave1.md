# Multi-agent redline campaign — Wave 1 results (2026-06-14)

9 general-purpose agents, 18 provisions, main-context verification. All outputs in
`verify_and_splice.py` (RESULTS dict) + agent transcripts in the orchestration log.

## Outcome
- **13 REDLINE reconstructed + spliced to scratch** (`modern-redline-agent-2026-06-14`),
  integrity 0/0. Point-in-time verified (e.g. art XI §25 multi-state-lottery 2002).
  - **3 independently BB-witnessed (full confidence):** art X §9 (BB-PASS),
    X §17 (BB-NEAR 0.99), XI §25 (BB-PASS). The agent reads matched the 1981 Blue
    Book exactly — strong evidence the team is reliable (the solo hand-read error
    rate was 40%; the BB-checkable agent subset was 0%).
  - **10 mechanically-valid, high-confidence, NO clean-BB witness** (articles
    III/VI/IX/XII/XIII are letter-spacing-degraded in the BB): art III §5/6/7,
    VI §13, IX §4/6/10, XII §2/6, XIII §2. Spliced to SCRATCH only — **flagged
    `needs-2nd-read`: require a confirming second independent agent read before any
    LIVE cutover.**
- **2 CREATE_SECTION (no prior, single version correct):** art V §6 (1997 executive
  article rewrite), XI §29 (2012 farming/ranching — new section). No splice needed.
- **2 medium-confidence (image failed → text-layer only) → re-read queue:**
  art XII §1, XIII §1.
- **1 blocked → re-prep:** art V §7 — prep attached the WRONG measure (a 1996
  *disapproved* measure); the real source is HCR 3009 (1997 art. V rewrite) =
  CREATE_SECTION like §6.

## Prep bugs the agents found (fix before Wave 2)
1. **AcroForm render (CRITICAL):** these session-law PDFs store body text in
   form-field XObjects; `pdftoppm`/`pdftotext` DROP it, leaving only strike/underline
   rules → blank-looking pages. **FIXED:** `prep.render()` now uses `mutool draw`
   (flattens fields). The good agents had already worked around it with mutool.
2. **`find_pages` mis-mapping:** several records pointed at the wrong page/measure
   in multi-chapter PDFs (art X §9 → art IX pages; art V §6 → art VIII §6 measure;
   art V §7 → a disapproved measure). Needs a stronger locator (match the article
   AND section reprint, verify the measure preamble).
3. **Resolver gaps:** initiated measures (`IMA.pdf`) not globbed (art I §1, XI §25);
   whole-session PDFs (2021+, 2400pp) stall the page scan (7 provisions skipped).

## Remaining (Wave 2+)
- 10 `needs-2nd-read` (confirming read) + 2 re-read + 1 re-prep from this wave.
- ~50 not yet prepped (page-not-located / IMA / giant-PDF) → re-prep with the fixed
  render + locator + resolver, then 8–10-agent waves.
- 22 multi-amendment provisions (intermediate reprints) — later waves.
- ~4 heavy multi-subsection → native source (PL-SOURCE-FILES).

## Scratch coverage after Wave 1
Modern provisions versioned: **19** (6 earlier + 13 this wave). Nothing to live —
the live constitution.db still has the historical fixes only; modern reconstructions
remain scratch-only pending second reads + completion of the campaign.
