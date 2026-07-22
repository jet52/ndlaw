# Changelog

Public releases of the North Dakota primary-law databases and the minimal MCP
server that serves them. Each release ships the validated database assets on the
[Releases](https://github.com/jet52/ndlaw/releases) page; the code in this
repository is the serve-only runtime and its deployment/auto-update tooling.

Per-release database corrections are summarized in the corresponding GitHub
Release notes. This repository does not carry the development-correction history.

## v2.1.0 — 2026-07-22

Research-tools + citation-graph release, and the first release serving the
free public endpoint at **https://ndlaw.org/mcp** (no account required).

**New server tools:**
- **`get_notes_of_decisions`** — an annotated "Notes of Decisions" view of a
  provision: every citing opinion with its citing sentences (¶ pinpoints),
  subsection outline, and depth-of-treatment signals.
- **`check_draft`** — one-call cite-check of a draft opinion or brief:
  citation/quotation verification, citator pass, authority currency.
- **`get_provision_xrefs`** — the provision-to-provision cross-reference
  graph (what a provision cites and everything that cites it, across
  corpora).

**Citation graph (opinions + AG databases):**
- **Pre-1981 constitution cites captured.** 1,747 old-numbering (1889
  sequential) N.D. Const. cites extracted across the opinions corpus and 521
  across the Attorney General corpus. Constitution lookups now union these
  era-gated through the renumbering crosswalk: e.g. art. X, § 18 surfaces
  its § 185 anti-gift-clause line back to the 1890s (43 court opinions and
  132 AG opinions, up from 11/86); art. VI, § 5 correctly excludes pre-1976
  § 89 cites (a different provision before the judicial article).
  Old-form citations are labeled `cited_as` in results.
- ndcourts.gov opinion links repaired and backfilled (44 URLs; dead
  document-ids from court PDF re-uploads re-resolved).

**Public deployment (deploy/):**
- Apache vhost, fail2ban rate-limit jails, systemd resource caps, and
  landing page for an unauthenticated public endpoint; the server now
  advertises rate-limit etiquette to connected LLM clients when
  `NDCOURTS_RATE_NOTE=1`.

## v2.0.1 — 2026-07-20

Constitution corpus + server feature release; the other database assets are
rebuilt from the same validated data as v2.0.0.

**Server (constitution corpus):**
- **1889↔1981 renumbering bridged.** `lookup_authority` now follows the
  official 1981 disposition tables (NDCC Replacement Vol. 13): a modern
  article/§ cite at a pre-1981 date returns its original-section predecessor;
  an original §-cite or amendment-article cite at a post-1981 date returns its
  modern successor — each with provenance fields and a source note. Lookups
  that would land past a wholesale article replacement (art. VII 1982,
  art. IV 1986, art. V 1997) carry an explicit caveat instead of implying
  content continuity.
- **One amendment chronology per provision.** `get_authority_history` merges
  the pre-1981 (session-law) and post-1981 chronologies across the renumbering
  seam, deduplicated per measure, each event tagged with the numbering it was
  recorded under; a `reorganization` block lists renumbered-from/to.

**Constitution database:**
- 1981-era coverage completed: pre-1982 article VII (§§ 1–9), and the
  repealed art. V § 14 / art. IV § 26 added as dated provisions.
- The June 2026 single-subject amendment (Constitutional Measure No. 1)
  applied: art. III § 9 and art. IV § 16 current text effective 2026-07-09,
  with the prior versions preserved.
- Amendment-series corrections against official sources: the four 1976
  measures renumbered to the official enumeration; the first amendment
  identified per the official lists (1894); several effective dates and
  events corrected (art. XVI, art. II § 2, the never-operative 1980 § 173
  amendment recorded as an event).
- Text fix: art. XIII § 4 had stray wiki markup from an upstream source;
  corrected against the official print.
- Validation: the full live constitution (arts. I–XVI + transition schedule)
  verified section-by-section against the official annotated apparatus, and
  the amendment series audited against the official 1961/1973 Blue Book
  notes and the 1981 disposition tables.

**Deploy:** `update-db.sh` now also fetches `jeac_opinions.db` and
`figures.db`, so those tools work on auto-updating servers.

## v2.0.0 — 2026-07-19 — minimal public repository

First release of the minimal public repository: a clean, serve-only runtime and
deployment, distributed separately from the development pipeline. Ships the
validated corpus as release assets —

- **Opinions** (`opinions.db`): ~19,800 North Dakota Supreme Court and Court of
  Appeals opinions, 1889–present, with the bidirectional citation graph.
- **Primary law**: the North Dakota Constitution (point-in-time), N.D.C.C.
  statutes, court rules, and Administrative Code.
- **Attorney General opinions** (`ag_opinions.db`) and **Judicial Ethics
  Advisory Committee opinions** (`jeac_opinions.db`).
- **Reproduced figures** (`figures.db`).
