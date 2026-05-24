# §10 shared-page image worklist — 2026-05-24

**Purpose.** Determine the true *on-page publication order* of opinions that share a
bound page, so each can get its synthetic `YYYY ND nnn` sequence number. Per the
reporter-order guard (2026-05-24): pull **both** the N.D. Reports page image and the
N.W. Reporter page image for each cluster — the two series may print same-page
opinions in different order. The synthetic cite is an **ND** cite, so **N.D. Reports
order governs**; where the printed date is the same and the reporters disagree,
manually adjudicate.

**Scope.** The 11 *genuinely-distinct* same-(date, N.D.-page) bound clusters. The
~18 high-jaccard `Re X` twin pairs at these same pages are NOT here — they are
pending a separate de-dup merge (one opinion, double-ingested), which removes them
from the ordering problem entirely.

**Status legend.** N.D. `.doc` is on disk for all 11 (bound-entry text, but one file
per opinion — does not by itself reveal physical on-page order). N.W. image on disk
only where noted.

| # | N.D. page | N.W. page | N.W. img on disk? | opinions (oid — caption) — all same date |
|---|-----------|-----------|:-----------------:|-------------------------------------------|
| 1 | 3 N.D. 538 | 58 N.W. 339 | no | 5274 *Kellogg, Johnson & Co. v. Gilman*; 5275 *Globe Investment Co. v. Boyum* (1894-02-19) |
| 2 | 9 N.D. 608 | 84 N.W. 1117 | **yes** | 5754 *Emmons County v. Davidson*; 20489 *Emmons County v. Cranmer* (1900-11-13) |
| 3 | 9 N.D. 609 | 84 N.W. 1117 | **yes** | 5753 *…v. Couch*; 20490 *…v. Baker*; 20491 *…v. Davidson* (1900-11-13) |
| 4 | 9 N.D. 610 | 84 N.W. 1117 | **yes** | 5752 *…v. Kelly*; 20492 *…v. Cranmer*; 20493 *…v. Ganger* (1900-11-13) |
| 5 | 9 N.D. 612 | 84 N.W. 1118 | no | 5750 *…v. Mellon*; 20495 *…v. McKenzie*; 20496 *…v. McLean* (1900-11-13) |
| 6 | 9 N.D. 613 | 84 N.W. 1118 | no | 5749 *…v. Robinson*; 20497 *…v. Mellon* (1900-11-13) |
| 7 | 19 N.D. 57 | 120 N.W. 874 | no | 499 *State ex rel. McCue v. Minneapolis, St. P. & S.S.M. Ry.*; 20498 *State ex rel. McCue v. Great Northern Ry.* (1909-04-16) |
| 8 | 20 N.D. 370 | 127 N.W. 78 | no | 674 *State v. McAndress*; 675 *State v. Koch* (1910-06-03) |
| 9 | 34 N.D. 601 | 159 N.W. 74 | no | 1640 *Tallmadge v. Weber*; 1641 *Mercer County State Bank of Manhaven v. Hayes* (1916-08-08) |
| 10 | 44 N.D. 247 | 173 N.W. 475 | no | 2171 *Nelson v. Middlewest Grain Co.*; 20499 *Lammadee v. Middlewest Grain Co.* (1919-06-21) |
| 11 | 61 N.D. 179 | 237 N.W. 709 | no | 4184 *First State Bank of Granville v. Bond*; 4185 *First State Bank v. Bond* (1931-07-14) |

**Flags to resolve while pulling:**
- **#11 (61 N.D. 179):** `First State Bank of Granville v. Bond` vs `First State Bank v. Bond` — same defendant, jaccard 0.40. Could be the *same* case double-ingested (a de-dup, not an ordering case) — the image should settle whether there are one or two distinct opinions here.
- **#2–6 Emmons County (9 N.D. 608–613):** a dense block of one-paragraph memorandum decisions, multiple per page, same date. The N.W. images for 608–610 are already on disk (`~/refs/nd/opin/NW/84/1117.pdf`); 612/613 need `84 N.W. 1118` pulled. These are the highest-density on-page-order cases.

**Need-images count:** N.W. Reporter pages to pull = 8 (all but the three 84 N.W. 1117 pages already on disk): `58 N.W. 339`, `84 N.W. 1118`, `120 N.W. 874`, `127 N.W. 78`, `159 N.W. 74`, `173 N.W. 475`, `237 N.W. 709`. N.D. Reports bound pages to pull for the order-disagreement check: all 11.

**Deferred (separate lists, not pulled yet):** 22 bound clusters that order by *distinct* N.W. page (verify against N.D. order later per the guard); 14 NW2d-era (1953–96) shared-page clusters (need de-dup triage first, then Westlaw NW2d page pulls).
