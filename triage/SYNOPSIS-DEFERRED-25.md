# Synopsis-leakage — deferred tail (after 2026-06-25 passes)

After the v2 (281), adjudicated-81 (75), and long-217 (201) passes, 25 opinions carried a live
`Synopsis` label. Class B (3, order-text recovery) and Class C (2, verify-first) were RESOLVED
2026-06-25 (below), leaving **20 deferred — all Class A (lost-syllabus-header)**.

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

## B. No-terminator West disciplinary summaries (3) — RESOLVED 2026-06-25

NOT a strip problem: each opinion's ENTIRE `text_content` was the West `Synopsis` — the
court ORDER body was never ingested (the West-doc parser dropped the ORDER for ORDER-format
docs, same class as Disc. Bd. v. Johnson 481 N.W.2d 225). Full-stripping would have emptied
them. Fixed by RECOVERING the full court order from each authoritative West .doc (batch
`recover-disc-order-text-2026-06-25`); West furniture stripped, provenance unchanged
(source_reporter stays `westlaw`). The Lince .doc was more complete than CourtListener's NW2d
markdown (it carries the justice signature block).

- id9351 (Lince) — `*444 ORDER OF DISBARMENT` + signatures, 177 -> 1159 chars.
- id10797 (Goetz) — `*480 ORDER OF INTERIM SUSPENSION`, 296 -> 1225 chars.
- id20482 (McMahon) — `*372 ORDER OF DISBARMENT` + concur line, 386 -> 1220 chars. (Shares
  N.W.2d page 298/372 with Boedecker v. St. Alexius Hospital, id8266 — its `372.md` is
  Boedecker, so the West .doc order body is the authoritative source here, not the page md.)

## C. Mixed / verify-first (2) — RESOLVED 2026-06-25 (batch `synopsis-verify-first-2026-06-25`)

- **id2312** — verified the Robinson dissent is in the opinion body (`ROBINSON, J.\n\nI dissent
  on the ground that...`), so the synopsis notice was redundant. Partial strip: removed
  `Synopsis\nRobinson, J., dissenting.`, KEPT the `Appeal from District Court, McHenry County;
  A. G. Burr, Judge.` line (court record, appears only here).
- **id7135** — verified the non-participation fact repeats more fully in the opinion's
  signature block (`ALVIN C. STRUTZ, C.J., deeming himself disqualified, did not participate;
  NORBERT J. MUGGLI, District Judge ... sitting in his stead.`). Full strip of the redundant
  West synopsis note; star-page + `Syllabus by the Court` preserved.

## Done this date (for context)
695 distinct opinions cleared across all batches (138 on 2026-05-13 + 281 v2 + 75
adjudicated-81 + 201 long-217). 695 + 25 deferred = 720 (the original worklist).
