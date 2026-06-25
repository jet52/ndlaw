# Proofing trio P34-36 (2019 ND 27 → 2017 ND 225) — deferred items

## RESOLUTION 2026-06-25 (batch `trio-defer-applied-2026-06-25`)
Worked the 52 deferred items:
- **6 applied**: id19320 (`the three introduction of the challenged exhibits`→`the three
  challenged exhibits`, PDF-verified), id19335 (leading-newline strip), 3 ellipsis COMPACTIONS
  (`. . . .`→`....`, the allowed direction the gate over-deferred), and id19332 (section heading
  `II` MOVED to its own line — PDF 2018 ND 62 confirmed it's a centered heading mashed onto
  `(4).`; the agent's *delete* was wrong).
- **45 rejected / no-action**: 35 star-page removals (the `*NNN` are REAL N.W.2d page markers —
  verified vs each opinion's N.W.2d cite, e.g. id17269 @ 918 N.W.2d 371 has *374-*381; keep for
  pincite resolution), 4 ellipsis WIDENINGS (ND prints compact), id19289 §-cite space-insertion
  (would break a statute number), and the **3 filing-stamp restorations** (user decision
  2026-06-25: keep stripped — clerk stamps are procedural metadata, per strip_clerk_stamps.py).
- **2 deferred**: id19311, id19314 — section headings (`III`, `V`) mashed mid-paragraph; the
  authoritative markdown has the same mashing, so they need careful PDF-based heading
  reconciliation (delete-vs-move trap), not the agent's delete. Tracked here.

---

## Original buckets (for reference)

Round applied 815 edits across ~146 opinions (755 autosafe + 56 heading/marker + 4 caption).
Deferred for a focused manual pass (NOT applied):

## Consolidation defer (49) — `triage/proofing-trio-defer.json`
- **Filing-stamp restorations (missing_text)**: `Filed M/D/YY by Clerk of Supreme Court` — held
  back; clerk stamps were intentionally stripped corpus-wide (`strip_clerk_stamps.py` /
  `strip_filed_office.py`). Re-applying would revert that decision. Confirm policy before any apply.
- **Ellipsis-spacing**: compact `....` ↔ spaced `. . . .` changes — excluded from autosafe per
  the ND-compact-ellipsis doctrine (G7 already rejected the widen direction).
- **Star-page touching**: any proposal adding/removing a `*NNN` pincite marker — held for the
  star-page-aware pass (markers are functional for pincite resolution; do not blanket-strip).
- **net-word-removal > 2 / no_pdf**: larger deletions or proposals without PDF confirmation.

## Heading delete-vs-move defer (3) — `triage/proofing-trio-heading-defer.json`
- **id19332** (deletes `II`), **id19311** (deletes `III`), **id19314** — `guard_probable_heading_move`
  flagged these as section headings that likely need MOVING, not deleting. Need `heading_move.py`
  SET-based handling / PDF read.

## Rejects (~226 across the trio)
Routed REJECT by the verifier guards (`.reject.json` per batch): ellipsis-widen, digit-in-cite,
bad-anchor, db-matches-pdf, unverified, whitespace-convention, unverified-quote. No action — the
guards caught proposed corruption (digit changes inside cites, confabulations, pdftotext padding).

## Applied batches (audit)
- `corpus-proofing-p34-36-2026-06-25` (755 edits / 134 opinions) — autosafe triple-evidence.
- `corpus-proofing-p34-36-headings-2026-06-25` (56 / 9) — `[¶ N]`→`[¶N]` source-matched marker
  spacing + 6 PDF-verified heading/marker moves.
- `corpus-proofing-p34-36-captions-2026-06-25` (4 / 3) — de-all-caps party names + designation
  relocation (triple-evidence).
