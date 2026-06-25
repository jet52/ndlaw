# Garbled paragraph markers — remaining queue (after 2026-06-25 passes)

This session fixed **52 garbled paragraph markers** across several classes:
- 85,109 spaced `[¶ N]`→`[¶N]` (`despace-paragraph-markers`)
- 30 glyph-garbled numbers `[¶ IB]`→`[¶13]` etc. (`ocr-garbled-markers`, sequence-determined)
- 5 deferred resolved (`dedup-storedtwice-marker` + `ocr-garbled-markers`): 4 stored-twice
  duplicate paragraphs (garbled copy) + id12623's 4 `]`→`J` markers
- 17 closing-bracket/prefix garbles `[¶7}`/`[¶9J`/`[¶'8]`→`[¶N]` (`ocr-garbled-markers-batch2`,
  sequence-verified)

**26 malformed markers remain** (`triage/garbled-markers-remaining.json`), in classes that need
a dedicated careful pass — NOT mechanical:

## markup-split (16) — entangled with markup contamination
`[¶\n *N]*` — the marker is split across a newline with `*…*` markdown emphasis around the
number (`[¶\n *2]*\n The relevant…`). The number is readable, but the fix must also strip the
`*…*` markup, so these belong with the **markup cohort** cleanup ($…$ / \P / <sup> / ### /
`*N]*`), not a standalone marker fix. IDs: 12624, 12791, 13177, 13562, 13641, 13857, 13948,
14609, 15105, 15107, 16396, 16655, 16659, 16766, 16815, 17024.

## digit-ambiguous (8) — need image verification / sequence reconciliation
- id12773 `[¶3'1]` (→[¶31]?), id16656 `[¶1G]` (→[¶16]?), id16775 `[¶103` (between [¶9] and
  [¶10] — possible stored-twice dup), id14532 `[¶15J` (prev=12 — markers 13-14 also off),
  id16777 `[¶'29]` (prev=27 — 28 missing), id13911 `[¶]14, 660 N.W.2d` (a CITATION, not a
  marker — likely leave), id14010 `[¶*\n 1]` (star+split), id7514 `[¶3, Decree` (reference).

## no-number (2) — marker with no number
- id12932 `[¶ Here, the declarant…`, id16531 `[¶ Here the hearing…` — the paragraph number is
  absent entirely; need the PDF image + sequence to determine it.

## XREF (5) — NOT markers, leave alone
`[¶N of syllabus`, `[¶N of H.B.`, `[¶N, Decree` in pre-1997 opinions (id6739×2, 6751, 6915,
9656) — these are cross-references to a paragraph ("¶3 of the syllabus, 144 N.W.2d…"), part of
the court's text, not in-text markers.
