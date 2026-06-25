# Synopsis-leakage — deferred tail (after 2026-06-25 passes)

After the v2 (281), adjudicated-81 (75), and long-217 (201) passes, 25 opinions carried a live
`Synopsis` label. All three classes (A lost-syllabus-header ×20, B order-text recovery ×3,
C verify-first ×2) were RESOLVED 2026-06-25 (below). **The synopsis-leakage queue is now CLOSED
— 0 live `Synopsis` labels remain corpus-wide (720/720 cleared).**

## A. Lost-syllabus-header / numbered-point (20) — RESOLVED 2026-06-25 (batch `recover-lost-syllabus-header-2026-06-25`)

`text_content` started `Synopsis\n2. ...` (or `\n3.`/`\n4.`) — the West-doc parse dropped the
`Syllabus by the Court` header **and** the leading syllabus point(s), leaving the numbered
court syllabus points with a stray `Synopsis` label on top. The surviving points and the
opinion body were intact; the full syllabus was in the authoritative West .doc.

RESOLVED by `scripts/recover_lost_syllabus_header.py`: prepended the dropped
`*NNN Syllabus by the Court.` header + the missing leading point(s) 1..(first-1) from the West
.doc, removing the stray `Synopsis` label. The doc's point `first` was alignment-checked
(quote-normalized) against the DB's first surviving point; everything from that point onward
left byte-identical. Doc curly quotes normalized to straight (corpus convention); em/en-dash,
§, nbsp, embedded star-pages preserved. Format matches the canonical intact form
(`*NNN Syllabus by the Court.\n1. ...\n\xa0\n2. ...`).

IDs: 6418, 6420, 6424, 6427, 6439, 6441, 6450, 6458, 6471, 7249, 7459, 7503, 13150, 13266,
13532, 13618, 13633, 13781, 13875, 14029. (15 missing point 1; 6418/13532/13875 missing 1-2;
13633/13781 missing 1-3.)

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
