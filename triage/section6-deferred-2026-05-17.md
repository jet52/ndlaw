# §6 deferred — borderline trio + multi-row clusters (2026-05-17)

Deferred from the `section6-handadj-2026-05-17` clean-14 merge pass. These
were held back deliberately: the clean tranche was simple 2-row pairs at
j≥0.55 with an unambiguous keep. The items below need a per-item human read
before any `merge_pair` — they are either same-caption/same-date with
suspiciously low text overlap (true-dup-with-stub vs lead+rehearing vs
distinct disposition is undecidable from jaccard alone) or >2-row clusters
that the pairwise keep policy can't safely resolve mechanically.

All oids verified present post-merge (corpus 20242). Jaccard = 4-word
shingle Jaccard of body text (frontmatter stripped).

## Borderline trio — RESOLVED 2026-05-17 (batch section6-handadj-trio-2026-05-17)

All three read in full → **all true duplicates** (verbatim judicial text;
low jaccard was the attorney/caption header block on one row + short
opinions). Merged; all 3 survivors then auto-promoted to Westlaw bound
text via receive re-run. Corpus 20242→20239. See CHANGELOG-data.md.

| cite | kept | dropped | j | outcome |
|---|---|---|---|---|
| 344 N.W.2d 489 *Anderson v. State* | 9059 | 9058 | 0.70 | merged — true dup (PER CURIAM, Civ. 10509) |
| 489 N.W.2d 885 *Dibble v. Backes* | 11201 | 11200 | 0.54 | merged — true dup (Levine, Civ. 920066) |
| 539 N.W.2d 869 *City of Dickinson v. Powell* | 12028 | 12027 | 0.39 | merged — true dup (consolidated 7-def. double-jeopardy; the "lean distinct" call was wrong — jaccard misled by the long multi-party caption) |

## Multi-row clusters — RESOLVED 2026-05-17 (batch section6-handadj-clusters-2026-05-17)

All texts read → every internal pair a clean true-dup; cross-case pairs
genuine distinct page-mates (kept). 6 deletions, corpus 20239→20233,
invariants 0 regressed, 0 orphan refs. See CHANGELOG-data.md.

- **57 N.W.2d 242** 3→1: keep 12544 (westlaw, Syllabus by the Court);
  merged 12545, 12546. One probate opinion captioned two ways.
- **521 N.W.2d 643** 4→2: keep 11740 *Hosman* + 11741 *Ferris* (distinct
  Bulman-tort cases sharing page); merged 11738→11740, 11739→11741.
- **489 N.W.2d 886** 4→2: keep 11204 *Woessner* + 11205 *Putney*
  (distinct Backes DUI cases sharing page); merged 11202→11204,
  11203→11205.

Payoff: 12544, 11740, 11741 auto-promoted to Westlaw bound text;
11204/11205 de-duped, await a future doc pull.

Original plan (kept for reference):

### 57 N.W.2d 242 — 3-row true-dup cluster (1953-01-23)
- 12544 *United States v. State* — **westlaw** cb1  ← keep (authoritative bound text)
- 12545 *United States v. State* — NW2d cb1
- 12546 *In Re Heiden's Estate* — NW2d cb1

All-pairs j 0.85–0.92 → one probate opinion captioned both ways. Plan:
merge 12545→12544 and 12546→12544 (keep the Westlaw row per the
authoritative-text refinement). canonical_name needs the human caption
pass — `_canonical_name` would yield `Estate of Heiden`, but the reported
caption is `United States v. State` (a/k/a *In re Heiden's Estate*); pick
in the §1 case-name pass, don't guess here.

### 521 N.W.2d 643 — 4 rows: 2 dup pairs sharing a page (1994-09-13)
- Hosman pair: 11738 / 11740 *Hosman v. NDSU* — j=0.62 → true dup
- Ferris pair: 11739 / 11741 *Ferris v. ND Centennial Comm'n* — j=0.51 → borderline dup (read)
- Hosman ≠ Ferris (cross-j 0.20–0.32) → distinct page-mates, keep one survivor each

Plan: merge within each pair (Hosman: 11740→11738; Ferris: read then
11741→11739 if confirmed), end with 2 distinct survivors on the shared
page. Hosman pair is the safer of the two.

### 489 N.W.2d 886 — 4 rows: 2 borderline dup pairs sharing a page (1992-10-01)
- Woessner pair: 11202 / 11204 *Woessner v. Backes* — j=0.51
- Putney pair: 11203 / 11205 *Putney v. Backes* — j=0.47
- Woessner ≠ Putney (cross-j 0.12–0.21) → distinct page-mates

Backes DUI-license companion cases. Both internal pairs sub-0.55 — same
read-before-merge caveat as 489 N.W.2d 885. End with 2 distinct survivors.

## "9 distinct page-mates" — RESOLVED 2026-05-17 (batch section6-handadj-pagemates-2026-05-17 + westlaw-receive-2026-05-17-pagemates)

The "9" was stale/misclassified. Reading the texts: 6 cites already
resolved by the earlier category-A pass (both page-mates have bound
text); 2 dissolved by the trio/cluster merges. Genuine remainder
resolved three ways:
- **Misclassified true-dups → merged** (CL double-ingest, date drift):
  `109 N.W.2d 249` 6148→6147 (kept correct decision date 1960-11-16),
  `263 N.W.2d 114` 7819→7818 (kept 1978-02-16). Both then auto-promoted
  to Westlaw bound text. Corpus 20233→20231.
- **Genuine distinct, docs in hand → explicit-promoted**:
  `489 N.W.2d 886` Woessner→11204, Putney→11205 (both now westlaw).
- **Genuine distinct, no doc → left correctly queued** (not blocked,
  awaiting own Westlaw pull via pool-aging re-list): `356 N.W.2d 897`
  9240 *Calavera v. Vix* (9241 *Bauer* done); `536 N.W.2d 354`
  11968 *Sletten* + 11969 *Moosbrugger* (distinct disciplinary).

- **481 N.W.2d 225** *Disc. Bd. v. Johnson* 11076 — RESOLVED 2026-05-17
  (batch `s6-481-johnson-resolve-2026-05-17`). Not a data error: 11076
  already has the complete clean disbarment order; the Westlaw doc is the
  same opinion (docket 920029, date, signatures verbatim) but `_parse`
  yields only the editorial Synopsis for the ORDER-format → spurious
  LOW_SIM. Cross-source confirmed; flag cleared, crosscheck_state→
  corrected, no text swap (CL order is complete; doc synopsis stripped
  per policy anyway).

§6-deferred queue is now **empty**. Open follow-up:
- **Parser gap (corpus-wide):** disciplinary "ORDER OF DISBARMENT/
  SUSPENSION" docs (no Opinion/Justice-author header) → `_parse` returns
  `opinion_text=''` + Synopsis-only `full_bound_text`, causing spurious
  LOW_SIM on receive. Hit 2 docs in the 2026-05-17 incoming: 37 Johnson
  (resolved) and **44 Schmidt = `505 N.W.2d 749` oid 11479** (the other
  batch LOW_SIM — almost certainly the same situation; verify the CL
  order is complete then resolve identically). Root-cause fix: add an
  order-format body extractor to the Westlaw parser (body after
  headnotes/synopsis, ending at justice signatures).

## How to resume

1. Read both (all) texts per item; classify dup / lead+rehearing / distinct.
2. True dups → `merge_pair(keep, drop, canonical, apply=True, batch=...)`,
   keep = Westlaw row if exactly one side is `source_reporter='westlaw'`,
   else more `cited_by` (tie → longer text). canonical = `_canonical_name(keep)`.
3. Distinct page-mates → de-flag, route to own Westlaw pull.
4. Snapshot first (DELETE is snapshot-only revertible) → apply →
   `align_primary_source --apply` → invariants 0-regressed → 0-orphan-ref →
   `receive_westlaw` re-run to fill survivors with bound text.
