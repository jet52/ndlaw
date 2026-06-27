# Garbled paragraph markers — queue CLOSED 2026-06-27

The 26 deferred malformed markers were worked to closure on 2026-06-27:
**23 fixed, 2 correctly left alone, 1 deferred to full re-proof.**
See `CHANGELOG-data.md` batches `*-2026-06-27`.

## Disposition
### markup-split (16) — RESOLVED
Re-checking each `[¶\n *N]*` against the paragraph sequence revealed two sub-classes:
- **6 stored-twice duplicates** (deleted garbled copy): 12624, 13857, 15105, 16655,
  12791, 17024. The garbled marker headed a corrupted first copy immediately followed
  by a clean `[¶N]` copy of identical text.
- **10 genuine repairs** `[¶\n *N]*`→`[¶N]` (sequence-confirmed; surrounding case-name
  italics left for the markup-cohort pass): 13177, 13562, 13641, 13948, 14609, 15107,
  16396, 16659, 16766, 16815.

### digit-ambiguous (8) — RESOLVED
- **dedups**: 12773 (`[¶3'1]`→clean ¶31 dup), 16775 (`[¶103`→clean ¶10 dup).
- **repairs**: 14010 `*[¶*\n 1]`→`[¶1]`; 14532 `[¶15J`→`[¶15]` (PDF); 16656 `[¶1G]`→`[¶10]`
  (PDF, G=0); 16777 `[¶'29]`→`[¶29]` (PDF).
- **left alone (not in-text markers)**: 7514 `[¶3, Decree of Dissolution.]` (cross-ref to
  a decree); 13911 `2003 ND 69, [¶]14, 660 N.W.2d 593` (pincite to a cited case — citation
  class, routed to a citation pass).

### no-number (2) — RESOLVED / DEFERRED
- 16531 `[¶ Here the hearing`→`[¶28]` (PDF, single seq gap).
- 12932 (1999 ND 138) — **DEFERRED**: pervasive OCR corruption, markers entangled with
  rotten text (`[2] 9]` / `[3][¶`); needs a full re-proof. → `STRUCTURAL-MARKERS-QUEUE.md`.

### XREF (5) — left alone (as before)
`[¶N of syllabus` / `[¶N of H.B.` / `[¶N, Decree` in pre-1997 opinions (6739×2, 6751,
6915, 9656) — cross-references in the court's text, not in-text markers.

## Spillover
Fixing the garbled glyphs exposed pre-existing missing/duplicate-marker (sequence)
defects in several opinions → new `triage/STRUCTURAL-MARKERS-QUEUE.md`.
