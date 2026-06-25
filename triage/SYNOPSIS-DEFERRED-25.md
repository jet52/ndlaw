# Synopsis-leakage — final deferred 25 (after 2026-06-25 passes)

After the v2 (281), adjudicated-81 (75), and long-217 (201) passes, **25 opinions still carry
a live `Synopsis` label**. Each needs handling beyond a mechanical strip. Three sub-classes:

## A. Lost-syllabus-header / numbered-point (20) — NOT a synopsis problem

`text_content` starts `Synopsis\n2. ...` (or `\n3.`/`\n4.`) — the West-doc parse dropped the
`Syllabus by the Court` header **and** the leading syllabus point(s), leaving the numbered
court syllabus points with a stray `Synopsis` label on top. These read as genuine court
syllabus propositions (numbered, legal holdings), terminated by `Attorneys and Law Firms`.

**Remediation (per item):** check the court PDF / bound volume for the missing
`Syllabus by the Court` header and point `1.` (and any others before the first surviving
number); restore them; remove the stray `Synopsis` label. Do NOT blindly label-strip — that
leaves the bigger header/point-1 defect.

IDs: 6418, 6420, 6424, 6427, 6439, 6441, 6450, 6458, 6471, 7249, 7459, 7503, 13150, 13266,
13532, 13618, 13633, 13781, 13875, 14029.
(6441/6458/7249/13781 were the short ones deferred from the adjudicated-81 pass; the other 16
are long.)

## B. No-terminator West disciplinary summaries (3)

West holding-summaries (`Attorney disciplinary proceeding was brought. The Supreme Court
held...`) where `boundary()` found no following court element (no `Syllabus`/`Attorneys`/
star-page/`Opinion\n` marker) — the disbarment ORDER likely follows in a form the detector
misses. Need a custom terminator (e.g. `ORDER OF DISBARMENT` / `PER CURIAM` / `IT IS ORDERED`)
then full-strip.

IDs: 9351, 10797, 20482.

## C. Mixed / verify-first (2)

- **id2312** — `Synopsis\nRobinson, J., dissenting.\n \nAppeal from District Court, McHenry
  County; A. G. Burr, Judge.` Mixed: the dissent notice is West editorial, but the
  `Appeal from District Court...` line is often part of the reported opinion header. Split:
  strip the dissent line, keep/relocate the appeal-from line.
- **id7135** — `Synopsis\nStrutz, C.J., deeming himself disqualified, did not participate.`
  A non-participation note. Verify it repeats in the opinion body before stripping — if it is
  the ONLY record of who did not participate, that is a court fact to preserve, not strip.

## Done this date (for context)
695 distinct opinions cleared across all batches (138 on 2026-05-13 + 281 v2 + 75
adjudicated-81 + 201 long-217). 695 + 25 deferred = 720 (the original worklist).
