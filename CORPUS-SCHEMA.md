# CORPUS-SCHEMA.md — versioned primary-law data contracts

> Companion to `SCHEMA.md` (which covers the **opinions** database). This file
> documents the **primary-law corpora**: the ND Constitution, court rules,
> statutes (N.D.C.C.), and administrative code (N.D.A.C.).

## Model

Opinions are immutable point-in-time events and live in `opinions.db`. The four
primary-law sources are *living, amendable* documents, so each is a **separate
SQLite file** with an identical, shared schema (defined once in
`ndcourts_mcp/corpus.py::create_corpus_schema`). The MCP server `ATTACH`-es
whichever corpus files are present onto the opinions connection, so one session
answers cross-corpus, point-in-time questions.

| corpus | DB file | ATTACH alias | citation form | ingester | source | point-in-time |
|---|---|---|---|---|---|---|
| `const` | `constitution.db` | `const` | `N.D. Const. art. I, § 8` | `ingest_constitution.py` | ndconst.org (CC0 wiki) | current text; **full amendment chronology** (1889–present) |
| `rule` | `rules.db` | `rules` | `N.D.R.Civ.P. 56` | `ingest_rules.py` | `~/refs/rule` git repo | **full** (every commit = a version, commit date = effective date) |
| `ndcc` | `statutes.db` | `statutes` | `N.D.C.C. § 12.1-20-03` | `ingest_statutes.py` | `~/refs/statute/NDCC` | **current text only** (no local historical editions) |
| `admin` | `admincode.db` | `admin` | `N.D.A.C. § 75-02-04.1-02` | `ingest_admin.py` | `~/refs/reg/NDAC` | **current text only** |

The `corpus` column on `provisions` carries the short key (`const` / `rule` /
`ndcc` / `admin`); the registry mapping key → file/alias/label is
`corpus.CORPORA`. Corpus DB files are gitignored (data ships separately, like
`opinions.db`); resolution order is `NDCOURTS_<KEY>_DB` env var → repo root →
per-user data dir (`corpus.resolve_corpus_db_path`).

## Field-identity warning (read first)

The citation lives in **three** related-but-distinct forms; do not conflate them:

| field | what it is | use |
|---|---|---|
| `provisions.citation` | the canonical, display citation (`N.D. Const. art. I, § 8`) | what the MCP returns and what jetcite's `text_citations.normalized` equals — the cross-link key to opinions |
| `provisions.cite_key` | a normalized lookup key (`nd const art i 8`) | fuzzy citation resolution; see `corpus.cite_key` |
| `provisions.hierarchy` | structural path as JSON (title/chapter/section, etc.) | grouping/navigation only — never for lookup or citation |

**Cross-link contract:** `provisions.citation` is built to equal jetcite's
`text_citations.normalized` form for the same authority, so "opinions construing
X" is an exact-string match. The six core rule sets, all statutes, all admin
sections, and all constitutional provisions follow this. (N.D.A.C. cites are
`cite_type='regulation'` in `text_citations`, not `'admin'`.)

## Tables

### `provisions` — one row per stable provision (section / rule / article-section)

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | |
| `corpus` | TEXT NOT NULL | `const` \| `rule` \| `ndcc` \| `admin` |
| `citation` | TEXT NOT NULL | canonical display citation (cross-link key) |
| `cite_key` | TEXT NOT NULL | normalized lookup key (`corpus.cite_key`) |
| `hierarchy` | TEXT (JSON) | structural path; nullable; navigation only |
| `heading` | TEXT | catchline / rule title; nullable |
| `status` | TEXT NOT NULL | `active` \| `repealed` \| `superseded` (default `active`) |
| `current_version_id` | INTEGER FK → `provision_versions(id)` | the version in force now |
| | | **UNIQUE(`corpus`, `cite_key`)** |

### `provision_versions` — dated text versions (valid-time history)

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | |
| `provision_id` | INTEGER NOT NULL FK → `provisions(id)` | |
| `effective_start` | TEXT (ISO date) | when this text took effect; NULL = unknown/original |
| `effective_end` | TEXT (ISO date) | NULL = **currently in force** |
| `text_content` | TEXT NOT NULL | the provision text for this version |
| `source_authority` | TEXT | enacting/amending authority or "as published" note |
| `source_url` | TEXT | official source link (see per-corpus notes below) |
| `source_path` | TEXT | local source file, where applicable |
| `added_at` | TEXT | ingest timestamp (default now) |
| `batch` | TEXT | ingest batch id (provenance) |

### `amendments` — amendment *events* (chronology), distinct from full-text versions

We often know an amendment happened (date + authority) before we have captured
the prior text as a `provision_version`. `provision_id` is **nullable**: an event
may not map to a current provision (e.g. pre-1996 constitutional amendments under
the historical numbering).

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | |
| `provision_id` | INTEGER FK → `provisions(id)` | **NULL** if unmapped to a current provision |
| `version_id` | INTEGER FK → `provision_versions(id)` | the captured full text, where one exists |
| `action` | TEXT | `adopted` \| `amended` \| `repealed` \| … |
| `effective_date` | TEXT (ISO) | when the amendment took effect |
| `raw_date` | TEXT | the source's human date string, verbatim |
| `election_date` | TEXT (ISO) | date voted on (constitution), where known |
| `affected` | TEXT | affected section(s) as the source states them |
| `amendment_number` | TEXT | sequential amendment number, where known |
| `authority` | TEXT | enacting authority (e.g. `S.L. 1985, ch. 702`) |
| `source_url` | TEXT | link to the enacting instrument |
| `raw` | TEXT | the source annotation / subject, verbatim |
| | | **UNIQUE(`provision_id`, `raw`, `effective_date`)** |

### `provisions_fts` — FTS5 over version text

External-content FTS5 (`content='provision_versions'`, `content_rowid='id'`,
`tokenize='porter unicode61'`) indexing `citation`, `heading`, `text_content`.
Rows are inserted explicitly at ingest (`corpus.index_version_fts`), keyed to the
`provision_versions.id`, so every version (current and historical) is searchable;
point-in-time search filters by the effective window.

### `provenance` and `changelog`

Mirror the opinions-DB audit discipline. `provenance` logs each ingest run
(operation, command/batch, source, rows, notes). `changelog` records field-level
corrections (batch, provision_id/version_id, field, old/new, authority) for
auditability. Both are append-only.

## Contracts / invariants

1. **One identity per provision:** `UNIQUE(corpus, cite_key)`.
2. **Exactly one current version:** for each provision, exactly one
   `provision_versions` row has `effective_end IS NULL`, and it is the one named
   by `provisions.current_version_id`.
3. **Non-overlapping windows:** a provision's versions partition time;
   `effective_end[i]` == `effective_start[i+1]`. Point-in-time lookup selects the
   row with the greatest `effective_start <= as_of` (see
   `corpus.lookup_provision_version`).
4. **Citation == cross-link key:** `provisions.citation` equals jetcite's
   normalized form for the same authority (see Field-identity warning).

## Point-in-time semantics (per corpus)

- `rule`: true history — `effective_start` is the amendment's effective date from
  git; "silent correction" commits update the standing version without a new
  effective date.
- `const`: current text + the authoritative amendment chronology
  (`amendments`). Modern (post-1996) amendments link to current provisions and
  set their `effective_start`; pre-1996 amendments are stored unlinked (the 1996
  renumbering makes a reliable mapping impossible). Full prior *text* per section
  is not yet captured.
- `ndcc`, `admin`: **current text only.** `effective_start` is the publication
  date (~2025-07-01), `effective_end` NULL. A point-in-time query *before* that
  date returns the current text **with an explicit `warning`** that earlier text
  is not captured — never a silent substitution.

## `source_url` per corpus

- `const`: the ndconst.org section page; amendment `source_url` is the enacting
  session-law PDF.
- `rule`: the ndcourts.gov rule page (from the commit's `Source:` line).
- `ndcc`: the official ndlegis.gov chapter PDF **with a per-section named
  destination** — each `.` in the section number becomes `p`
  (`§ 12.1-20-03` → `…/t12-1c20.pdf#nameddest=12p1-20-03`).
- `admin`: the official ndlegis.gov chapter PDF (`…/acdata/pdf/<chapter>.pdf`).
  These PDFs carry **no** named destinations, so admin links are chapter-level.
