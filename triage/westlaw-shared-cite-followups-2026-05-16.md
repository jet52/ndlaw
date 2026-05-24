# Westlaw shared-cite followups (2026-05-16)

Genuine multi-opinion N.W.2d pages where the worklist's `nw_cite` dedup listed
only ONE of the opinions sharing the page. The omitted opinion(s) will NOT be
populated by `receive_westlaw.py` (it matches listed `nw_cite`→opinion_id),
even though the single Westlaw fetch returns ALL opinions on that page in one
document. Action: after receiving the page, also extract/assign the omitted
opinion(s) from the same downloaded doc, or list them in a later batch.

Distinct from `court-archive-shared-cite-pages-2026-05-15.md` (those are
disposition-table noise; these are real, separate opinions).

| N.W. cite | listed (batch) | omitted — needs population |
|-----------|----------------|----------------------------|
| 167 N.W.2d 754 | oid 6781 *Aune v. City of Mandan* (1969-04-24), batch 2026-05-16 | oid 6780 *Tri-state Insurance Co. v. Lubbock Machine & Supply Co.* (1969-04-10) — **RESOLVED: downloaded separately by user as its own file; populate 6780 from that file at receive time** |

Adjacent dup-row noise (Task #21 §6, not blocking): oid 6770 *Aune v. City of
Mandan* (1969-03-18) and oid 6838 *Tri-State Ins. v. Lubbock* (1970-03-25) —
likely rehearing/supplemental or true-dup rows; let the §6 dedup pass adjudicate.

## Block 3 shared cites (4 pairs, batch 2026-05-16) — RESOLVED, all 8 obtained

"Do Not Deliver" was just Westlaw's third selector option (select-first /
select-second / do-not-deliver). User selected **first** for each in the
batch-2026-05-16 download, and collected the **second** of each pair in a
**separate file** (a second Westlaw batch). All 8 opinions are in hand; no
alternate source needed.

Receive caveat: the worklist's `nw_cite` dedup listed only ONE oid per cite, so
`receive_westlaw.py` will auto-match only that one. The page-mate must be
populated manually from its file. "first file" = the select-first download in
the 2026-05-16 batch doc; "second file" = the separate select-second download.

| N.W. cite | oid in "first" file | oid in "second" file | listed in batch (auto-matched) |
|-----------|---------------------|----------------------|--------------------------------|
| 352 N.W.2d 628 | 9170 *Eisenzimmer v. City of Balfour* (1984-07-18) | 9169 *In re Disc. Action v. Dronen* (1984-07-11) | 9170 |
| 355 N.W.2d 798 | 9208 *Patzer v. Glaser* (1984-10-23) | 9209 *Allegree v. Jankowski* (1984-10-23) | 9209 |
| 418 N.W.2d 789 | 10043 *In re Teevens* (1988-02-09) | 10044 *Matter of Montgomery* (1988-02-09) | 10044 |
| 507 N.W.2d 61 | 11510 *State v. Fredericks* (1993-10-26) | 11509 *Disc. Bd. v. Dosch* (1993-10-20) | 11510 |

Note: for 355 N.W.2d 798 the auto-matched oid (9209 Allegree) is in the
*second* file, not the first — receive must not assume listed-oid == first file.

**RESOLVED 2026-05-16 (hand-adjudication, part a):** all 4 promoted by exact
caption+date to explicit oids — 9208 Patzer (j=0.78), 9209 Allegree (j=0.82),
10043 Teevens (j=0.65), 10044 Montgomery (j=0.71). src=westlaw, vstate=corrected,
invariants 0 regressed. (The batch-(6) "Montgomery v Montgomery" was an unrelated
divorce case; the real *In re Bruce R. Montgomery* disciplinary order was in the
4-items select-second zip.) Revert: `cleanup revert westlaw-receive-2026-05-16`.

## Block 4 shared cite (1 pair, batch 2026-05-16) — RESOLVED, both obtained

| N.W. cite | oid in "first" file | oid in "second" file | listed in batch (auto-matched) |
|-----------|---------------------|----------------------|--------------------------------|
| 71 N.W.2d 770 | 14447 *Scherbenske v. Maier* (1955-08-27) | 14446 *Gunsch v. Gunsch* (1955-08-25) | 14447 |

Auto-matched oid (14447) == first file — receiver maps correctly; 14446 needs
manual population from the separate second file.

## Part (b) — ambiguous-queue outcome (2026-05-16)

64 ambiguous from receive_westlaw-2026-05-16. **18 resolved**: 12 surname
clear-wins (`resolve_westlaw_clearwins`, now reads today's report via new
`--report` arg) + 6 hand-adjudicated (the 4 part-a stragglers + 356 N.W.2d 897
Bauer→9241 + 79 N.D. 550 Littlejohn→12694). All jaccard 0.65–0.99, invariants
0 regressed throughout.

**Remaining 46 are all §6 duplicate-row pairs** (same opinion under two CL
naming conventions, row-to-row jaccard 0.60–0.99) → `triage/westlaw-receive-
manual-queue-2026-05-16.md`, blocked on Task #21 §6 dedup. Not hand-adjudicable:
the Westlaw doc matches BOTH rows of each pair; promoting before dedup just
fills one duplicate. After §6 collapses each pair, a receive re-run resolves
them automatically.
