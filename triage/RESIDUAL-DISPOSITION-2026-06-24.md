# Manual-residual disposition (fleet rounds P28-33), 2026-06-24

188 items accumulated in the manual queue across the P28-30 and P31-33 concurrent fleet
rounds (the items the mechanized pipeline routed to manual). Drained as follows.

## Resolved — APPLIED (verified)
- **9 captions** (`caption-residual-2026-06-24`): party-designation relocation to the PDF
  two-column layout + a name-case fix (`LAVALLIE`->`Lavallie`). All passed triple-evidence
  (`new ⊆ source_quote ⊆ PDF`).
- **2 ellipsis compactions** (`ellipsis-compact-2026-06-24`): DB spaced `. . . .` -> compact
  `....` (the valid direction per the ND-compact-ellipsis doctrine).
- Section-heading residual: already cleared by `heading_move.py` in the round commits
  (the no-PDF-heading ones remain below).

## Resolved — REJECTED (correct non-action, DB already right)
- **41 ellipsis-WIDEN** (`...` -> `. . .`): pdftotext renders spaced dots from column
  padding, but ND prints **compact** ellipses; the DB's compact form is correct. Widening
  would import the extraction artifact. No action. (Doctrine: compacting valid, widening reject.)
- **21 signature-indent** (`guard_whitespace_convention`): proposals re-indenting justice
  signature lines to the PDF's 5-6 space centering; corpus convention is 1 leading space.
  No action.
- Stale **Grenz (id 19509) heading-deletes** in the "other-manual" bucket: superseded by the
  `heading_move.py` MOVES already applied; anchors no longer match. No action.

## Remaining — genuine judgment queue (deferred to a focused per-item pass)
These failed the triple-evidence auto gate (new not fully in source_quote, source_quote not
in PDF, or net-word-removal > 2) and need per-item PDF reading — they are NOT safe to
auto-apply:
- **~50 scrambles / missing_text / ocr_char** (`triage/residual-other-manual.json`) — e.g.
  id 19590 `748 N.W.2d In an appeal...` (dropped page + displaced text), id 19511 statutory
  list reconstruction. Real fixes, but each needs the PDF read to reconstruct correctly.
- **12 deletions** (`triage/residual-deletion.json`) — verify each is genuine garbage vs a
  delete-should-be-MOVE before acting.
- **4 signature-block mashes** (`triage/residual-sig-block-mash.json`) — justice names run
  onto one line; a signature-reformat helper (with the 1-space corpus convention) would
  mechanize these, but the convention/format needs a decision first.
- **no-PDF-heading opinions** — heading_move couldn't extract PDF headings (margin-¶ layout);
  manual.

Net: of 188, **11 applied + 62 resolved-no-action = 73 cleared**; ~66 genuine-judgment items
documented for a focused pass. The reject-classes (ellipsis-widen, sig-indent) recur every
round — candidates to encode as verifier guards so they never reach the manual queue.
