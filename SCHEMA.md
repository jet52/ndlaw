# SCHEMA.md — data contracts

> **STATUS: partial.** The two contracts below (`citations.reporter` taxonomy
> and `citations.is_primary`) were ratified **and applied** 2026-05-17
> (batches `reporter-taxonomy-2026-05-17`, `is-primary-recompute-2026-05-17`;
> see CHANGELOG-data.md). All three enforcing invariants are green at 0.
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

### `opinion_sources.source_reporter` provenance values

Text-bearing sources (one is `is_primary=1`, its text is in
`opinions.text_content`): `westlaw`, `ND`, `NW2d`, `NW`, `archive`,
`court-archive`.

Non-text validation sources — convention added 2026-05-18:

| value | meaning | rules |
|---|---|---|
| `NW-image` | a **scanned page image** of the bound N.W. Reporter for the opinion's `<vol> N.W. <page>` (path `NW/<vol>/<page>.pdf`, image-only PDF, no extractable text) | **never `is_primary`** (`text_length=0`; carries no text — does not feed `text_content` or the multi-source text-diff); counts as an *independent human-verifiable witness* toward the §9 two-source/authoritative-text bar. The underlying scans are Westlaw-delivered: the PDFs live only in `~/refs` and are **excluded from the public release** (the DB row is a refs-relative path reference; the bytes never enter the repo or `opinions.db`). |

`*-image` rows are inert w.r.t. the `primary_source_unique` /
`source_reporter_matches_primary` / `source_path_matches_primary`
invariants because those join only `is_primary=1` rows.

## Contract 1 — `citations.reporter` taxonomy (ratified 2026-05-17)

Closed enumeration. Each citation row's `reporter` is exactly one of:

| value | citation form | class | notes |
|---|---|---|---|
| `ND-neutral` | `YYYY ND N` | **official, precedential** | medium-neutral cite; native 1997+; or §10 back-assigned synthetic (flagged as synthetic per §10). *Was mislabeled `ND`.* |
| `ND` | `<v> N.D. <p>` | **official, precedential** | official North Dakota Reports state reporter, vols 1–79 (~1890–1953). *Was mislabeled `NDold`.* |
| `NW` | `<v> N.W. <p>` | regional, precedential **parallel** | North Western Reporter, 1st series |
| `NW2d` | `<v> N.W.2d <p>` | regional, precedential **parallel** | North Western Reporter, 2d series |
| `NW3d` | `<v> N.W.3d <p>` | regional, precedential **parallel** | North Western Reporter, 3d series (live continuation, ~2023+). *Added 2026-05-17; absent from initial draft enum.* |
| `ALR` | `<v> A.L.R. <p>` | **secondary, non-precedential** | American Law Reports annotation reprint. *Currently misfiled under `NW2d`/`NW`.* |
| `LRA` | `<v> L.R.A. <p>` | **secondary, non-precedential** | Lawyers' Reports Annotated (A.L.R. predecessor). *Misfiled.* |
| `US` / `SCT` / `LED` | `<v> U.S./S.Ct./L.Ed. <p>` | **foreign, non-precedential** | U.S. Supreme Court reporters; appear only as rare cross-refs; never primary |

`reporter` must be one of the above and is enforced non-NULL by the
`reporter_in_taxonomy` invariant (no DB-level NOT NULL constraint added —
avoids a risky ALTER). The classifier (`ingest._classify_reporter`) and all
citation-INSERT paths emit only these values; INSERT paths no longer fall
back to `source_reporter` (a different axis).

**Applied 2026-05-17** (`reporter-taxonomy-2026-05-17`): the prior 79 NULL
were resolved by reclassification; the misfiled secondary cites became
`ALR` (300) / `LRA` (69). A *third*, unanticipated residue surfaced —
**461 rows** whose citation string is a foreign/specialty reporter outside
this entire universe (South Western, Am. St. Rep., A.F.T.R., Oil & Gas
Rep., L.R.R.M.): mis-scraped cross-references that belong in
`text_citations`, not `citations`. Per the ratifying user's decision these
**461 were deleted** (0 were any opinion's sole cite — no orphaning;
snapshot- and changelog-audited). Result: 0 NULL, 0 out-of-taxonomy. No
`US`/`SCT`/`LED` citation rows exist — those reporters appear only inside
opinion text, never as a parallel-cite row.

## Contract 2 — `citations.is_primary` (ratified 2026-05-17)

**Definition:** `is_primary=1` marks the single citation by which the case is
officially cited. **Exactly one** citation row per opinion has `is_primary=1`
(never zero, never >1).

**Selection ladder** (highest available wins):

1. `ND-neutral` (medium-neutral) — native 1997+, or §10 synthetic once assigned
2. `ND` (official North Dakota Reports) — pre-1997 opinions, vols 1–79
3. `NW3d` (regional) — newest regional series
4. `NW2d` (regional) — gap-era 1953–1996 and any opinion lacking higher rungs
5. `NW` (regional) — earliest era / fallback

Ties within a rung break to the lowest citation id (deterministic).

`ALR`, `LRA`, `US`, `SCT`, `LED` are **never** `is_primary`.

**Interim (pre-§10):** pre-1997 opinions have no neutral cite yet, so their
primary is rung 2 (`ND` official Reports) where it exists, else the earliest
regional (`NW2d`→`NW`). When §10 assigns synthetic neutral cites, the synthetic
`ND-neutral` becomes primary and the prior primary demotes to parallel.

Matches ND Supreme Court citation convention (neutral cite official since 1997;
bound N.D. Reports official before; N.W./N.W.2d the regional parallel).

## Invariants enforcing these

- `citation_row_unique_per_opinion` — no `(opinion_id, citation)` dup rows (added 2026-05-17).
- `citation_single_primary_per_opinion` — exactly one `is_primary=1` per opinion. **Enforced, 0** (was 817; fixed by `is-primary-recompute-2026-05-17`).
- `reporter_in_taxonomy` — every `citations.reporter` ∈ the Contract-1 enum (NULL fails). **Enforced, 0** (was 79 NULL + ~590 misfiled + 461 foreign; fixed/deleted by `reporter-taxonomy-2026-05-17`).
- `secondary_never_primary` — no `is_primary=1` row with reporter ∈ {ALR,LRA,US,SCT,LED}. **Enforced, 0**.

All three read the enum/secondary set from `ingest` (single source of truth).
Dashboard 2026-05-17 post-apply: **18 ok, 2 known baseline, 0 regressed**.

## Implementation plan — APPLIED 2026-05-17

All six steps executed; see CHANGELOG-data.md for batch detail.

1. **Classifier** — `ingest._classify_reporter` rewritten to the enum
   (adds A.L.R./L.R.A./U.S./S.Ct./L.Ed. + `NW3d`; `NDold`→`ND`,
   `ND`→`ND-neutral`; dropped the `source_reporter` fallback). Added
   `PRIMARY_LADDER`/`SECONDARY_REPORTERS`/`REPORTER_TAXONOMY` and
   `recompute_primary(conn, oid)` as the single source of truth. ✅
2. **Consumers** updated in lockstep: `audit`, `audit_sources`,
   `backfill_sources` (path test only — `:139`/`:173` source_reporter
   untouched), `quality_scan:228`, `webapp`, `ingest_westlaw:780`, and the
   four citation-INSERT paths (now classify + `recompute_primary`). All
   `source_reporter` logic left untouched; `align_primary_source` dry-run
   after = 0 changes, confirming axis independence. ✅
3. **Data migration** `reporter-taxonomy-2026-05-17`: 14,568 reclassified,
   461 foreign cross-refs deleted (user-ratified), 79 NULL resolved →
   0 NULL / 0 out-of-taxonomy. ✅
4. **is_primary recompute** `is-primary-recompute-2026-05-17`: 24,183
   flips / 11,978 opinions → 0 multi-, 0 zero-, 0 secondary-primary. ✅
5. **Invariants**: the three checks added and green at 0. ✅
6. Snapshot `opinions.db.bak-pre-reporter-contract-2026-05-17` taken
   before 3–4; invariants 18/2/0, orphan checks ok, align clean. ✅

Migration tools retained for revert/audit: `migrate_reporter_taxonomy.py`,
`recompute_is_primary.py`.
