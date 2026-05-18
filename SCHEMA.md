# SCHEMA.md — data contracts

> **STATUS: partial.** This file currently documents only the two contracts
> ratified 2026-05-17 (`citations.reporter` taxonomy and `citations.is_primary`).
> The full per-table/per-column data dictionary is TODO-validation.md §11,
> sequenced after the data-correctness items so it documents settled contracts.

## Field-identity warning (read first)

Three distinct fields share value strings like `ND` / `NW2d` and are routinely
confused. They are **independent axes** and must never be conflated in code:

| field | axis | governs |
|---|---|---|
| `citations.reporter` | which **reporter series** a citation string belongs to | citation classification (this doc) |
| `citations.is_primary` | which **citation** is the official one to cite the case *by* | citation convention (this doc) |
| `opinions.source_reporter` / `opinion_sources.source_reporter` | provenance of the **text** | which source the opinion *text* came from (westlaw / NW2d / NW / ND / archive / court-archive); governed by the `primary_source_unique` / `source_reporter_matches_primary` invariants — **out of scope here** |

A change to `citations.reporter` must not touch `source_reporter` logic
(e.g. `ingest.py:229-233`, `backfill_sources.py:139` are `source_reporter`).

## Contract 1 — `citations.reporter` taxonomy (ratified 2026-05-17)

Closed enumeration. Each citation row's `reporter` is exactly one of:

| value | citation form | class | notes |
|---|---|---|---|
| `ND-neutral` | `YYYY ND N` | **official, precedential** | medium-neutral cite; native 1997+; or §10 back-assigned synthetic (flagged as synthetic per §10). *Was mislabeled `ND`.* |
| `ND` | `<v> N.D. <p>` | **official, precedential** | official North Dakota Reports state reporter, vols 1–79 (~1890–1953). *Was mislabeled `NDold`.* |
| `NW` | `<v> N.W. <p>` | regional, precedential **parallel** | North Western Reporter, 1st series |
| `NW2d` | `<v> N.W.2d <p>` | regional, precedential **parallel** | North Western Reporter, 2d series |
| `ALR` | `<v> A.L.R. <p>` | **secondary, non-precedential** | American Law Reports annotation reprint. *Currently misfiled under `NW2d`/`NW`.* |
| `LRA` | `<v> L.R.A. <p>` | **secondary, non-precedential** | Lawyers' Reports Annotated (A.L.R. predecessor). *Misfiled.* |
| `US` / `SCT` / `LED` | `<v> U.S./S.Ct./L.Ed. <p>` | **foreign, non-precedential** | U.S. Supreme Court reporters; appear only as rare cross-refs; never primary |

`reporter` is NOT NULL and must be one of the above (currently 79 NULL +
~590 secondary/foreign cites misfiled as `NW2d` — both driven to 0 by the
correction pass). The classifier (`ingest._classify_reporter`) and all
citation-INSERT paths must emit only these values.

## Contract 2 — `citations.is_primary` (ratified 2026-05-17)

**Definition:** `is_primary=1` marks the single citation by which the case is
officially cited. **Exactly one** citation row per opinion has `is_primary=1`
(never zero, never >1).

**Selection ladder** (highest available wins):

1. `ND-neutral` (medium-neutral) — native 1997+, or §10 synthetic once assigned
2. `ND` (official North Dakota Reports) — pre-1997 opinions, vols 1–79
3. `NW2d` (regional) — gap-era 1953–1996 and any opinion lacking 1–2
4. `NW` (regional) — earliest era / fallback

`ALR`, `LRA`, `US`, `SCT`, `LED` are **never** `is_primary`.

**Interim (pre-§10):** pre-1997 opinions have no neutral cite yet, so their
primary is rung 2 (`ND` official Reports) where it exists, else the earliest
regional (`NW2d`→`NW`). When §10 assigns synthetic neutral cites, the synthetic
`ND-neutral` becomes primary and the prior primary demotes to parallel.

Matches ND Supreme Court citation convention (neutral cite official since 1997;
bound N.D. Reports official before; N.W./N.W.2d the regional parallel).

## Invariants enforcing these

- `citation_row_unique_per_opinion` — no `(opinion_id, citation)` dup rows (added 2026-05-17).
- `citation_single_primary_per_opinion` — **TODO**: exactly one `is_primary=1` per opinion (currently 817 violations; becomes baseline→0 after the correction pass).
- `reporter_in_taxonomy` — **TODO**: every `citations.reporter` ∈ the Contract-1 enum (currently 79 NULL + ~590 misfiled).
- `secondary_never_primary` — **TODO**: no `is_primary=1` row with reporter ∈ {ALR,LRA,US,SCT,LED}.

## Implementation plan (NOT yet applied)

1. **Classifier** (`ingest._classify_reporter`): rewrite to the Contract-1
   enum incl. A.L.R./L.R.A./U.S./S.Ct./L.Ed. detection; rename `NDold`→`ND`,
   `ND`(neutral)→`ND-neutral`.
2. **Consumers** keying on old strings — update in lockstep: `audit.py`
   (3), `quality_scan.py:228`, `webapp.py` (cite-selection, ~6),
   `ingest_westlaw.py:780`, plus citation-INSERT paths
   (`ingest_nwcite`, `insert_supplemental_opinions`, `receive_westlaw`,
   `scrape_archive`). Leave all `source_reporter` code untouched.
3. **Data migration** (changelog-tracked batch): `UPDATE citations SET
   reporter` to the new taxonomy; reclassify the ~590 misfiled
   secondary/foreign rows; resolve 79 NULL.
4. **is_primary recompute** (changelog-tracked): apply the ladder to every
   opinion — fixes the 817 multi-primary AND the systemic "regional is
   primary instead of official" (≈5k post-1997 opinions whose primary
   flips N.W.2d→neutral; pre-1997 official-N.D.-Reports promoted over
   N.W. where present). Large but changelog-revertible.
5. **Invariants**: add the three TODO checks above; drive to 0.
6. Snapshot before 3–4; `align_primary_source`/invariants/0-orphan after.
