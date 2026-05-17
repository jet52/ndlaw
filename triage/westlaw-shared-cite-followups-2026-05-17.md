# Westlaw shared-cite followups (batch 2026-05-17)

291 opinions listed (`westlaw_requests.doc_batch='2026-05-17'`), 273 unique
N.W.2d cites. **15 cites carry >1 listed oid.** `receive_westlaw.py` matches
`nw_cite -> opinion_id`; one Find&Print returns the whole page, so for these
the single returned doc must populate MORE THAN ONE oid. The worklist listed
the cite once per oid, so all oids below are recorded as listed.

User downloads ONE doc per cite. Two categories:

## A. Genuine distinct page-mates — populate each oid from the one doc

Separate opinions sharing a N.W.2d page (companion cases, consecutive-day
disciplinary orders, or a lead opinion + later rehearing/supplemental at the
same page). All real, all need their own text from the same returned doc.

| N.W. cite | oids (date) — case |
|-----------|--------------------|
| 109 N.W.2d 249 | 6147 (1960-11-16) N.D. Workmen's Comp. Bureau v. S.A. Healy Co. + 6148 (1961-05-26) Claim of S.A. Healy Co. — likely lead + rehearing/supplemental; verify dates on doc |
| 176 N.W.2d 522 | 6846 Fuchs v. Engelhardt + 6847 Giese v. Engelhardt (both 1970-03-20) — user flagged; getting first in this batch |
| 378 N.W.2d 678 | 9519 (1985-12-19) In re Disc. Action v. White + 9520 (1985-12-20) In re Disability of Williams |
| 404 N.W.2d 50 | 9875 (1987-03-26) In re Disc. Action v. Garcia + 9878 (1987-04-16) City of Williston v. Miller |
| 456 N.W.2d 772 | 10656 Disc. Bd. v. Britton + 10657 Disc. Bd. v. Palda (both 1990-06-28) |
| 519 N.W.2d 311 | 11698 (1994-07-20) Disc. Bd. v. Voigt + 11699 (1994-08-03) Disc. Bd. v. Nassif |
| 525 N.W.2d 250 | 11803 Morehouse v. Morehouse + 11804 Kieffer v. Huebner (both 1994-10-27) |
| 525 N.W.2d 251 | 11805 (1994-10-31) Smith v. City of Grand Forks + 11806 (1994-11-16) Dakutak v. Dakutak |

## B. §6 dup-row pairs — BLOCKED on §6 dedup (do not promote before)

Same opinion under two CL naming conventions (parties vs "In Interest of" /
ALLCAPS / identical). Westlaw doc matches BOTH rows; promoting before §6
collapses each pair just fills one duplicate. After §6 dedup + receive re-run
these auto-resolve. Same mechanism as the 46 stranded pairs in
`triage/westlaw-receive-manual-queue-2026-05-16.md`.

| N.W. cite | oids — same opinion, two rows |
|-----------|-------------------------------|
| 385 N.W.2d 102 | 9610 C.H. v. M.E. / 9611 In Interest of Cme (1986-04-10) |
| 489 N.W.2d 885 | 11200 / 11201 Dibble v. Backes (1992-10-01, identical name) |
| 489 N.W.2d 886 | TWO distinct opinions each dup'd: 11202/11204 Woessner v. Backes; 11203/11205 Putney v. Backes (all 1992-10-01) — A+B mixed: 2 page-mates, each a dup pair |
| 496 N.W.2d 24 | 11316 / 11317 Lang v. Burleigh County Sheriff's Dep't (1993-02-23, ALLCAPS variant) |
| 519 N.W.2d 301 | 11694 Stave v. T.S. / 11695 In Interest of Ts (1994-07-18) |
| 521 N.W.2d 643 | 11739 / 11741 Ferris v. N.D. Centennial Comm'n dup pair (1994-09-13); 11738 Hosman v. NDSU is a DISTINCT page-mate (cat. A) |
| 539 N.W.2d 869 | 12027 / 12028 City of Dickinson v. Powell (1995-11-30, identical name) |

Net: of 291 listed oids, ~273 are clean single-oid auto-promotes; the rest are
covered above. Process category A at receive time (multi-oid populate from one
doc); leave category B for the §6 pass + receive re-run.

---

## RESOLVED 2026-05-17

Receive applied: 249 auto-promoted + 2 clear-wins (337 N.W.2d 160→8950,
496 N.W.2d 24→11317). Invariants 13 ok / 0 regressed.

Hand-adjudication (batch `westlaw-receive-2026-05-17-handadj`,
changelog-revertible): **19 category-A docs promoted by explicit oid**, each
caption+date confirmed with decisive text-jaccard separation:
- 73 N.W.2d 782: Gunsch→14732, Karabensh→14733
- 176 N.W.2d 522: Fuchs→6846, Giese→6847 (DB rows were tiny CL stubs; low
  jaccard is the stub being replaced by full bound memo — mapping is
  caption/docket-decisive: Civ. 8581 Fuchs vs 8580 Giese)
- 378 N.W.2d 678: White→9519, Williams→9520
- 383 N.W.2d 813: United Bank v. Boehm→9594, Kautzman→9595
- 404 N.W.2d 50: Garcia→9875, Williston v. Miller→9878
- 456 N.W.2d 772: Britton→10656, Palda→10657
- 469 N.W.2d 801: Ebach→10874, Schumacher→10873
- 519 N.W.2d 311: Voigt→11698, Nassif→11699
- 525 N.W.2d 250: Morehouse→11803, Kieffer→11804
- 472 N.W.2d 914: Rorvig→10933 only

**Still HELD (not promoted, manual):**
- 472 N.W.2d 914 Johnson doc — §6 dup-row pair 10931/10932 (same 1991-04-29
  order, two CL names); both j≈0.83. §6-blocked.
- 481 N.W.2d 225 Johnson doc — §6 dup pair 11075/11076 AND doc j=0.004 vs both
  (no text overlap; doc may be a different Johnson order). Manual.
- 109 N.W.2d 249 Healy doc — name says 6148 (Claim of S.A. Healy, 1961-05-26),
  parsed date says 6147 (Bureau, 1960-11-16); j non-decisive (0.91/0.90).
  Lead-vs-rehearing ambiguity; needs the bound volume to split.
- 505 N.W.2d 749 Schmidt oid 11479 — LOW_SIM j=0.01, flagged by receive.
- All category-B §6 dup-row pairs above — blocked on §6 dedup + receive re-run.

**Scherle/Kaiser (356 N.W.2d 890) — RESOLVED, no DB change.** Westlaw's bare
N.W.2d Find&Print returned the Nebraska *State v. Kaiser* (218 Neb. 556) for
356 N.W.2d 890; receive correctly rejected it (non-ND). DB is CORRECT: oid 9237
*First Federal S&L v. Scherle* sits in a coherent ND pagination run —
356 N.W.2d 889 *Lawson* / **890 Scherle** / 893 *Bauer* — a Nebraska case
cannot interleave there. oid 9237 already carries full ND opinion text from CL
(9.6k ch, real caption/panel), so it is not a data gap, just an
un-cross-validated §2 single-source row. Action: re-pull Scherle by exact case
name (not bare cite) in a future §2 targeted batch. (State v. Kaiser's own
N.W.2d parallel is likely 356 N.W.2d 872; "890" inside its doc is a cited
case.)
