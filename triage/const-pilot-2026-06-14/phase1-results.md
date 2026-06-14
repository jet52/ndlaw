# Phase 1 results — `scripts/reconstruct_modern_versions.py` vs scratch DB

Read-only against `/tmp/const-scratch.db` (copy of constitution.db). Phase 1 =
amend-reenact-section, pure single-section provisions only.

## Pipeline: works, idempotent, write path verified
resolve_pdf (refs tree `~/refs/nd/sess/<yr>_sl/*CAA*.pdf` → download fallback) →
pdftotext-layout → content-based locator (`section N of article R … as follows:
Section N. …`) → classify/gate vs current text → idempotent splice + changelog +
integrity self-test. Applied the safe (all-CLEAN) splices to scratch:
**integrity gaps/overlaps=0, >1-open=0.** Write path proven.

## The headline finding: CAA reprints are mostly legislative MARKUP
Of 35 pure-single-section provisions, the locator reaches 15 (20 LOCATE_FAIL are
mostly recent new-article measures — art XV/XVI 2022–24, out of phase-1 scope —
plus a few resolver misses). Classifying each by its LATEST amendment vs current text:

| latest-amendment class | n | meaning |
|---|---|---|
| CLEAN (exact token match) | 5 | clean reprint — pdftotext sufficient |
| MARKUP (current ⊆ extract) | 5 | strike/underline reprint, mild |
| MISMATCH (concatenations break subset) | 5 | strike/underline reprint, heavy |
| LOCATE_FAIL | 20 | recent-format / new-article / out of scope |

**~2/3 of located measures (MARKUP+MISMATCH = 10/15) are strike/underline markup.**
The session laws print amendments as legislative redlines: struck text = deleted,
underlined text = added. pdftotext linearizes both, mashing them together —
`departmentbranches` (struck "department" + added "branches"), `noany`, `shallmay`.

## Extraction escalation — RESOLVED which tool handles markup
Tested all three on the art. XI §4 markup page (2013 CAA, ch. 517):
- **pdftotext** → `departmentbranches`/`noany`/`shallmay` (flattened). ✗
- **marker OCR** → IDENTICAL flattening `departmentbranches`/`noany`/`shallmay`. ✗
  marker's models do not capture strike/underline formatting.
- **Claude direct read** (rendered page image) → strike vs underline plainly visible;
  yields BOTH the clean post-amendment text (matches current DB) AND the prior
  version (keep struck, drop underlined). ✓ **Only method that resolves markup.**

**Conclusion:** markup measures (~2/3) cannot be auto-extracted by either OCR tool.
They require a Claude-direct-read step. This is manual but bounded and fits the
authoritative-text bar; it also yields the prior text for free (the redline IS the
diff between consecutive versions).

## Corrections to the design (data/design-modern-const-versions-2026-06-14.md)
1. Escalation ladder step 3: marker does NOT handle strike/underline — only
   Claude-direct-read does. Reorder: pdftotext → (clean?) splice; (markup?) →
   Claude-direct-read (skip marker for markup; marker stays only for the rare
   ligature/scanned-image case).
2. New per-amendment classifier needed: CLEAN reprints take the pdftotext path;
   MARKUP/MISMATCH route to a Claude-read queue. The latest-amendment-vs-current
   gate is the cheap detector (CLEAN vs not); a concatenation heuristic
   (`[a-z]{6,}` tokens that split into two dictionary words, doubled function
   words) flags markup priors that have no current-text reference.
3. Bonus: because the redline encodes the diff, one Claude-read of a markup page
   produces TWO versions (before + after) — efficient for multi-amendment chains.

## Markup step — BUILT + RUN (2026-06-14)
`markup_worklist.py` (isolates each redline page) + `apply_markup.py` (edit-list
splicer). Faithfulness method: do NOT re-transcribe authoritative text. Read the
redline, record the small per-amendment EDIT LIST `(after_phrase → before_phrase)`,
and reverse-apply it to the gate-verified current DB text to derive each prior
version. The after-text is gate-checked; every prior is anchored to authoritative
text + a reviewable diff (`transcriptions.json`).

**Scope refinement — the "markup" bucket (10) decomposes into 3 classes:**
- **Whole-section redline → reconstructable (ALL 5 DONE):** art XI §4, IV §11,
  III §2, IX §3, XI §16.
- **Create-section (no prior, single version already correct):** art XI §29
  ("created and enacted as follows" — new 2012 section). Exclude.
- **Large multi-subsection amendment (defer to subsection modeling, like the
  structural four; reprinted as subsections 1/2/3… spanning multiple pages):**
  art VIII §6 (subs. 2 & 4 of a 1,671-tok section), art IX §12, **art VI §13
  (judicial vacancies, subs. 1–3+)**, **art X §24 (foundation aid, subs. 1–2 a/b)**.
  VI §13 and X §24 were initially taken for whole-section redlines but the reads
  showed multi-subsection structure spanning pages → reclassified here.

**Reconstructed end-to-end (applied to scratch, gate PASS, integrity 0/0):**
| provision | amendment | prior→current tok | point-in-time verified |
|---|---|---|---|
| art XI §4 | 2012 oaths | 124 → 125 | yes |
| art IV §11 | 2000 vacancies | 21 → 20 | yes |
| art III §2 | 2004 fiscal-impact | 86 → 131 | yes (2003 vs 2010) |
| art IX §3 | 1986 board membership | 84 → 80 | yes |
| art XI §16 | 2006 militia | 81 → 103 | yes (2005 vs 2008) |

Each went from 1 flat version → a real 2-version timeline `[1981 → d)` + `[d → open)`,
verified by `lookup as of <date>`. 5 changelog rows (batch
`modern-versions-markup-2026-06-14`). **All 5 whole-section redlines in phase-1
scope are complete.**

## What phase 1 spliced
Only single-amendment all-CLEAN provisions auto-spliced (no prior versions to add).
NO genuine multi-version reconstruction completed automatically, because every
multi-amendment provision in scope has ≥1 markup or create-article prior. The clean
multi-version case (art. X §21) is blocked only by its 1981 create-article base
(phase 2) — its 1991/1995 reenacts are clean. Unlocking real reconstruction depends
on the Claude-read markup step, exactly as the proof-widening predicted.
