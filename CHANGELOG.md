# Changelog

Public releases of the North Dakota primary-law databases and the minimal MCP
server that serves them. Each release ships the validated database assets on the
[Releases](https://github.com/jet52/ndlaw/releases) page; the code in this
repository is the serve-only runtime and its deployment/auto-update tooling.

Per-release database corrections are summarized in the corresponding GitHub
Release notes. This repository does not carry the development-correction history.

## v3.4.1 — 2026-09-04

- **The Constitution's paragraph structure is fixed.** 174 provisions stored
  the ndconst.org wiki's editing line-wrap rather than its paragraphs, so
  art. IV, § 13's seven paragraphs rendered as forty and `lookup_authority`
  returned the same ragged text; 1,589 stored lines are now 311 paragraphs.
  The structure comes from the upstream's own rendered page, which already
  settles it — a lone newline is nothing there, a blank line is a paragraph
  break — while every character is re-cut from the text the corpus already
  held, so the change is whitespace-only. Justification multi-space runs
  (`board  of  higher  education`) collapse in the same pass.
- **DokuWiki markup no longer appears as constitutional text.** Ten provisions
  (art. XIV §§ 1–4, art. XV §§ 1–6) opened with a `===== Section N. =====`
  wiki heading that `lookup_authority` returned as part of the section; five
  more carried `<WRAP indent>` markers, which now render as real indentation
  (art. I § 25, Marsy's Law, gains 23 paragraphs with its lettered rights
  indented; art. VIII § 6, art. X §§ 22 and 24).
- **Five new Attorney General opinions** — 2026-O-15 through 2026-O-19, all
  open records and meetings, issued August 28 and 31, 2026. AG opinions now
  number 6,758.
- **Those five also exposed, and fixed, an OCR-lineage defect.** Their PDFs are
  scans whose text layer is Acrobat's own OCR, which the pipeline could not
  distinguish from born-digital text. Read against the page images, all five
  carried errors: **2026-O-17 was missing its entire second page** (that page
  has no text layer at all, so the loss was silent), two lost their signature
  blocks, and every opinion number and cross-reference read with a digit zero
  in place of the letter O. All corrected. Extraction now identifies an OCR
  text layer from the PDF producer and flags any page that yields no text, so
  this class cannot enter the corpus unmarked again.
- **Opinions — 764 corrections across 688 opinions in 36 batches.** The
  CAP-diff guard-hold queue completed (402 of 566 sites applied, every one
  image-read); the 2020s reflow arc drained its named holds across two more
  rounds; four text-furniture classes were decided against the slip PDFs' own
  text layer (inline page numbers, LaTeX escape runs, `[.]` fragments, glued
  headings); the run-on signature-block queue closed; and the first two
  batches of a new bound-volume OCR pass landed 105 corrections in
  N.W.2d vols 56–61, each confirmed by two independent reads of the page
  image.
- **Court rules — 111 corrections**, including the September 2026 amendment
  cycle's remaining provisions, the Criminal Procedure appendix form headings
  taken from the court's own index, and Form 8's version history restored from
  two pages the court files under Form 7(a).
- **Web — rule-set index pages.** `/rules` lists every rule set with its
  provision count, and `/rule/{set}` indexes that set's rules, tables and
  appendix forms. Cross-references stored in rule text now render as links,
  and inline pipe tables render as tables.

## v3.4.0 — 2026-08-30

**Public history and release assets restart at this version.** The public
repository was deleted and recreated on 2026-08-30 after the distribution
copy was redefined on 2026-08-28 (a stripped copy of every database is what
ships; the working databases never do). Earlier release assets (v2.0.0 through
v3.3.3) carried local working-tree paths and internal batch ledgers and were
withdrawn; the full development history remains in the private dev repository.
The corpus itself is unchanged by the restart — every correction listed in
earlier entries below is in this release.

- **45 court rules the corpus never had are now served** — every rule
  whose page the court dates `01/01/0001` (N.D.R. Proc. R., N.D.R. Local Ct.
  Pr., Continuing Legal Education, Limited Practice by Law Students, most of
  the Judicial Conduct Commission rules' front and back matter, Admin. R. 4
  and 10, N.D.R.Crim.P. 40, the Crim.P. and Ev. tables of statutes, and the
  N.D.R.Ct. 8.3/8.3.1 form appendices). They carry "effective date not
  published by the court" (`effective_start` null) rather than an invented
  date; `as_of_date` lookups treat them as current for any date.
- **Six court-rules documents that the mirror had misfiled or never captured
  are now served under their own citations**: N.D.R.Civ.P. Table A (was
  stored over Rule 81's file), N.D.R.Ct. 8.3.1, N.D.R.Ct. Appendices F and K
  and Appendix A to Rule 8.9, and N.D.R.App.P. Tables (new). Rule 81's and
  Rule 8.3's headings were the misfiled documents' and are corrected. Root
  cause fixed in the scraper (page identity read from the title's leading
  designator only).
- **`search_authority` excerpts are now matched-passage snippets.** Each hit's
  `excerpt` is the passage around the matching terms, marked `>>>term<<<`
  (the `search_opinions` convention), instead of the first 280 characters of
  the provision whether or not the match was there. A hit whose only match is
  in the citation or heading returns that field marked. The key name is
  unchanged.
- **Court rules current through the September 1, 2026 cycle.** Amendments
  to N.D.R.App.P. 4 and 28 and N.D.R.Ct. 3.1, 11.2 and 8.2; N.D.R.Ct. 11.10
  is now Reliable Electronic Means Proceedings (transferred from Admin. R.
  52) and the former 11.10 is 11.11; new N.D.R.Ct. 9.2 (transferred from
  Admin. R. 16); Admin. R. 16 and 52 carry the court's transfer notation and
  status `superseded`. Point-in-time lookups (`as_of_date`) return the prior
  text before September 1.
- **Corpus full-text indexes are now derived from the shipped text.** The
  `provisions_fts` index in every primary-law DB is rebuilt from the
  distribution copy's own text at build time and verified against it
  (FTS5 `integrity-check` with content comparison) before the asset ships.
  Search results are unchanged; the index was previously carried over from
  the working database and could not be rebuilt or verified.

## v3.3.3 — 2026-08-26

- **Data — the CAP-diff sweep completed.** Two passes over the
  `gap_1953_1996` West-`.doc` lineage, every applied site image-read against
  the printed page. Tier 1 (8,883 sites / 1,294 opinions): section symbols
  restored where the lineage had typed `s`, paragraph marks restored,
  signature-block stamps rebuilt. Tier 2 (5,248 sites / 1,647 opinions):
  keyed word errors — dropped words, wrong function words, inflection slips,
  typos, misspelled names. A correction was applied only where the reader
  ratified the independent witness word-for-word; 1,088 sites were held
  rather than guessed. Five caption-alignment slips that reached the corpus
  were reverted byte-exact the same day, and 12 corrections falling inside
  inline tables were propagated to `tables.db`.
- **Dates ruled from the print.** Murphy 1914-12-12 → 09-12 (the official
  reporter governs), Quam 1950-06-29 → 06-28, Otto's rehearing date, and
  Stark / Heart River 1953-05-25 → 05-23; a 16-row clerk-vs-print class was
  ruled KEEP after reading the bound volumes.
- **Clerk-corrected opinions now carry their own date.** New `date_modified`
  and `modified_kind` columns, 40 backfilled from the archive filed span,
  13,562 markers repaired.
- **Citations**: full graph rebuild under jetcite 2.13.0 (unresolved gap
  1,717 → 1,369), 339 parallel cites backfilled from later citing opinions,
  and 4 Spencer West `.doc` witnesses filed carrying 2 new N.W.3d citations.
- **First prose table in the corpus**: 2026 ND 34 ¶ 14, reconstructed from
  the slip PDF.

## v3.3.2 — 2026-08-21

- **Data**: the week's ruling-queue waves — West Synopsis residue stripped
  (911 sites, body-guarded), West-added parallel citations stripped (2,475
  sites / 780 opinions), West editorial rewrites restored to the court's
  words, nested blockquotes to print depth (35 opinions), Reporter's Notes
  reordered to print (20), space-led separators normalized (134), caption
  comma-glue (11). Caption arc completed: party/label rows regrouped (1,484
  opinions) and row geometry ruled to the slip (206 + head-span 83). OCR:
  corpus-wide JOIN/possessive repair (~900 sites) and the two-witness
  lineage repair (247 opinions / 715 sites). Signature-panel restorations
  (~190 opinions). G2 shatter eyeball tier drained (184 → 0).
- **Corrections pipeline**: clerk-corrected opinions now detected
  automatically — a repaired ndcourts.gov link means the Clerk replaced the
  PDF; the new weekly probe diffs the re-issued slip and files findings.
  First catch applied same-day: 2026 ND 111 (treatise-cite period) and
  2026 ND 123 (No. 20260172 caption respondent).
- **Citation graph**: full rebuild under jetcite 2.12.0.
- **Web**: footer now reports the data-refresh date and
  opinions-current-through date on every page.
- **N.D.A.C.**: 20 chapter-repeal sections applied (state-PDF-confirmed).
- Corpus: 20,105 opinions, current through 2026-08-20.

## v3.3.1 — 2026-08-14

- **Data**: block-quote restoration arc — Tier 1 (2019 zero-tab cohort) and
  archive-authorized Tier 2 slices applied; CourtListener word-order
  scrambles restored; mid-citation paragraph breaks joined under Contract
  13. CL-markdown paragraph-shatter repair began (pilot + G12 per-seam
  wave). Orphan-bracket residue drained. Caption furniture stripped with
  related-docket harvest; missing/one-line signature panels restored.
- **Citation graph**: short-form rule cites re-extracted.
- **N.D.A.C.**: db-vs-mirror sweep confirmed admincode current.

## v3.3.0 — 2026-08-10

- **Data**: header apparatus drained corpus-wide (CourtListener citation
  headers, glued caption headers, Court of Appeals headers — ~1,050
  opinions); 2020+ reflow holds released after engine gate fixes;
  mid-citation breaks joined; self-citation-edge audit closed 4 defects.
- **Citation graph**: jetcite 2.10.1 — archaic bare reporter forms
  (`16 Pac. 931`, `1 Sup. Ct. 389`) newly extracted, ~9,000 sites.
- **N.D.A.C.**: July 2026 supplement applied, including the emergency
  kratom scheduling (§ 61-13-01-03) spliced from the published chapter
  PDFs.

## v3.2.0 — 2026-08-07

- **Data**: NW2d-era syllabus gap closed — "Syllabus by the Court" restored
  to ~1,012 opinions (5,182 paragraphs) from the bound reports; table-page
  opinions ingested (corpus → 20,098); 2020+ reflow engine's first
  5,200-opinion sweep applied.
- **Statutes**: N.D.C.C. repeal modeling ratified — repealed sections carry
  a closed prior version plus an open repeal-notation version (3,506 rows),
  matching print.

## v3.1.0 — 2026-08-01

- **Web**: citation-URL interface serves **all 18 rule sets** (v3.0.x
  hardcoded six, leaving 310 rule provisions with no URL), plus a short
  URL form for every provision in all four corpora (`/ndrappp4`,
  `/ndcc12.1-20-03`, `/ndconstarti8`, `/ndac75-02-04.1-01`); 44,104 of
  44,104 provisions now resolve. `/cited` pages list every cited
  authority type, grouped, and resolve 1889-numbering constitutional
  cites through the crosswalk. Subdivision cites resolve at any depth.
- **Citation graph**: N.D. Sup. Ct. Admin. Order cites newly extracted
  (jetcite 2.7.4), incl. the COVID-19 jury-trial suspension (Order 25);
  N.D.R. Proc. R. pattern fixed; 9 Lawyer Sanctions standards re-cited
  (`1 0` → `1.0`), unblocking 258 orphaned graph citations.
- **Data**: ~90 print/PDF-verified text corrections queued since
  v3.0.1 — five inside-pool hold classes closed (atomic
  sibling-divergence, bracket/invisible/italics seams, digit-letter
  confusables) and head-pool atomic tranches 1–10 (21 opinions:
  bunched-label lists restored to N.D.C.C. § 28-32-46 and others,
  West-inserted parallels removed from quotes, deposition Q./A. blocks
  reassembled).
- **AG opinions**: 2026-L-02 and 2026-L-03 ingested (6,753 total).
- **Ops**: weekly pipeline gains AG/JEAC freshness watches and a
  figure watch (embedded images in new opinions' PDFs); update-db.sh
  learns the tables.db corpus.
- 527 tests, 102 invariants (2 new: `short_key_unique`,
  `provision_has_web_url`).

## v3.0.1 — 2026-07-30

- Deploy fix over v3.0.0: the public `pyproject.toml` had missed the
  ndcourts→ndlaw rename (caught by the cutover health probe). v3.0.0
  retracted.

## v3.0.0 — 2026-07-30

- **Citation-URL web interface** (ndlaw.org): every opinion and
  provision addressable by citation-shaped URL across all 7 corpora;
  ratified disclaimer + official-source links; renderer fixes.
- ~460 data corrections; full citation-graph rebuild (357,944 outbound
  / 126,821 inbound edges).

## v2.2.0 — 2026-07-28

Data release. No new opinions (the court filed none this cycle). The work is text
fidelity, filing dates, and the internal identifier sequence.

**Cited case names restored (439 spans, 274 opinions).** Where a reporter shortened
the name of a case the court *cites* — `State ex rel. Standish v. Nomland` printed as
`State v. Nomland`, `Bank of Park River v. Norton` as `Bank v. Norton`, `New York L.
Ins. Co. v. Fletcher` as `Insurance Co. v. Fletcher` — the court's own wording is
restored. Each restoration was confirmed twice: against a transcription of the bound
volume and against the volume's printed page itself, and applied only where both
agree. The reporter citation inside each span was never missing, so no citation
changed; what improves is the party name the court actually wrote.

Sixteen were held back rather than applied — twelve where the splice point was not
unique, four where restoring one site would have left the opinion spelling a name two
ways.

**Filing dates corrected (385).** A systematic reconciliation of every opinion's
filing date against the printed page, the reporter's own metadata, and — where they
exist — the court's published opinion page and its position in the court's own
`YYYY ND n` sequence. Agreement across the compared set rose from 97.3% to 99.6%.

The method matters for trust: no date was changed on a single source. A printed date
line and a transcription of that same line are not independent witnesses, so
corrections required a genuinely separate one — the span of dates in the surrounding
reporter volume, an independent editorial file, or, for 1997 and later, the court's
own sequence, where the opinions numbered *n−1* and *n+1* bracket the date opinion *n*
must fall in. That test reversed several corrections that the printed page alone would
have gotten wrong.

**Nine printed date errors registered rather than "fixed".** Where the volume itself
carries an impossible date — one opinion prints "Nov. 14, 2000" above a body
discussing 2007 events and its own 2007 docket number — the printed text is preserved
verbatim and the error recorded, so the served date is right without misrepresenting
what the reporter published.

**Panel membership (10 opinions).** A district judge sitting by designation —
"GEO. THOM, JR., District Judge" — had been parsed as two separate justices, giving
those opinions a six-member panel on a court that seats five. Corrected in both the
panel and the voting record.

**Internal identifiers resequenced.** The provisional `YYYY ND n` identifiers assigned
to pre-1997 opinions are ordered by filing date and reporter page; the date
corrections above moved that ordering, so the sequence was recomputed in full (3,632
identifiers). These remain provisional editorial identifiers, distinct from the
court's native neutral citations, and are marked as such.

**Citation graph rebuilt** against the corrected text: 358,215 extracted citations and
126,709 resolved links.

## v2.1.2 — 2026-07-24

Data release: nine new opinions, a panel-data correction, and continued
text-fidelity cleanup. Adds one server tool (`get_opinion_tables`) and one new
database asset (`tables.db`); all other changes ship in `opinions.db`.

**New opinions.** The nine opinions filed 2026-07-23 (**2026 ND 145–153**):
*State v. Quam*, *Wano Township v. North Dakota Public Service Commission*,
*State v. Eastgate*, *State v. Fox*, *Interest of M.W.*, *Childers v. Childers*,
*Paola v. State*, *State v. Engelking*, and *Interest of R.W.* Corpus now 19,832
opinions.

**Panel data corrected (justice names).** Restored 1,174 panel fields across
1,001 opinions where a metadata-merge bug had reverted verified panel corrections
to their raw source values — e.g. Justice Mary Muehlen Maring reverting to the OCR
typo "Making", with her middle name splitting into a phantom panel member. The
merge write-guard now protects panel membership and voting records, so the
reversion cannot recur.

**Leaked page numbers removed (mid-paragraph).** 2,101 running PDF page numbers
stranded inside paragraphs by the text-extraction era — the complement to last
release's clean-boundary sweep — removed from 431 opinions, with the split
sentences rejoined. Each removal is gated on the court PDF (the number must equal
that page's sequential number *and* sit at that page's text boundary), so footnote
markers and citation digits are never touched. (First observed in *State v.
Boger*, 2021 ND 152.)

**Wrapped citations rejoined.** 256 neutral-cite years and reporter volumes that
extraction had stranded on their own line (`Varty v. Varty, / 2019 / ND 49` →
`2019 ND 49`; `… Ins. Co., / 256 / F.3d 587` → `256 F.3d 587`) merged back into
the citation. Whitespace-only — the opinion token streams are unchanged.

**Numeric tables reconstructed, plus a new tool.** 34 tables across 15 opinions
that flat extraction had linearized into one-value-per-line runs were rebuilt as
aligned fixed-width blocks in the opinion text. A new **`get_opinion_tables`**
tool serves them as structured data (markdown / HTML / cells) from the new
**`tables.db`** release asset.

## v2.1.1 — 2026-07-23

Data-correction release. No server-code changes; every correction ships in the
database assets (`opinions.db`).

**Citation graph fully reconciled.** 604 citation edges adjudicated across the
citation-reconcile and antecedent-witness review queues — nearly all confirmed,
with a handful re-pointed to the correct target and a few false cross-state
edges (shared reporter page) suppressed. The manual review queues are now empty.

**Text-flow cleanup.**
- 2,112 leaked PDF page numbers removed from 474 opinions (each a page number
  glued onto the following page's first line by the text-extraction era);
  genuine footnotes preserved.
- 1,543 PDF-aligned mid-sentence page-break gaps rejoined (whitespace-only; the
  opinion token streams are unchanged).

**Footnote recovery (Phase 2c).** Recovered footnote numbers and de-garbled/
de-interleaved footnotes in a set of 1978–2014 opinions, all verified against
the court PDFs and West reporter sources (e.g. 1999 ND 143's 23 footnotes,
2014 ND 197's dissent footnote and microgram OCR fixes).

**`[[Image here]]` restorations complete.** Closed the last 36 image-extraction
placeholders across 24 opinions — dropped section headings, omission-asterisk
rows, a legal land description, four numeric caseload tables (verified
cell-by-cell), and a footnote whose content the court's own PDF prints as
"[IMAGES IN ORIGINAL OPINION NOT REPRODUCED HERE.]". Every restoration is
court-PDF-verified; zero placeholders remain corpus-wide.

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
