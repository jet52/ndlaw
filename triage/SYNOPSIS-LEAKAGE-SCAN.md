# Corpus-wide West synopsis-leakage scan (run 2026-06-24)

**Question:** beyond the 45 modern West-doc opinions, how much West editorial material
(synopsis, headnotes, labels, star-pages) has leaked into `text_content` corpus-wide?
(Triggered by finding full `Background:`/`Holdings:` synopsis still present in modern
opinions during the furniture-strip pass.)

## Headline findings (19,793 opinions scanned)

| Marker | Opinions | Read |
|---|---|---|
| `Background:` / `Holdings:` (full West synopsis body) | **1** | prior strip batches cleared it — good |
| standalone `Synopsis` label + content | **720** | **residual West synopsis leakage** (see below) |
| `Attorneys and Law Firms` label | 7,056 | West section label — standard on West-sourced opinions |
| `Opinion` section label | 6,964 | West section label |
| star-page markers (`*NNN`) | 11,563 | West N.W. pagination — also used for pincite resolution (do NOT blanket-strip) |
| `(Mem)` West caption | 1 | cleared |

The `Background:`/`Holdings:` synopsis bodies are essentially gone corpus-wide — the
remaining leakage is the **`Synopsis` label + a short West editorial note**.

## The 720 Synopsis-leakage opinions

`text_content` carries a standalone `Synopsis` line followed by a West editorial note —
one of: a case summary (`Synopsis\nAction by Halvor J. Hagen against Severin Sacrison...`,
id 559), a procedural posture (`Synopsis\nError to district court, Traill county...`,
id 5096), or a separate-opinion list (`Synopsis\nMeschke, J., filed a concurring opinion.`,
id 12492). This is West's copyrightable editorial matter, not the court's text — strippable
per [[project_redistribution_scope]]. The earlier `strip-westlaw-synopsis-2026-05-13` batch
missed these.

- **715 pre-1997**, 5 modern (1997 West-doc opinions in the audit's "no-court-source"
  bucket).
- **499 also contain the court's `Syllabus by the Court`** — which is **court text and must
  be preserved** ([[project_court_syllabus]]). Synopsis and Syllabus are distinct sections;
  ordering varies (297 Synopsis-before-Syllabus, 227 after), so a strip needs **per-opinion
  boundary detection**, not a fixed-position rule.
- **221 Synopsis-only** (no Syllabus) — the opinion body is intact; the Synopsis is a West
  add-on summary.

Worklist (id, era, `has_syllabus`, `synopsis_head`) in `triage/synopsis-leakage-worklist.json`.

## Recommendation

Run a gated synopsis-strip pass over the 720: remove the block from the `Synopsis` label to
the next section boundary (`Attorneys and Law Firms`, the justice byline, or — when Synopsis
precedes it — `Syllabus by the Court`), with hard gates: the `Syllabus by the Court` block
and the opinion body (`[¶N]` / numbered paragraphs) must be byte-identical before/after, and
no court text may be removed. Validate a sample against the bound-volume scans for the very
old (pre-1953) opinions, where the "statement of the case" could blur with West's synopsis.

Out of scope for synopsis-leakage (separate decisions): the 7,056 atty-labels / 6,964
opinion-labels (cosmetic West section labels) and 11,563 star-pages (functional for pincite
resolution — keep).
