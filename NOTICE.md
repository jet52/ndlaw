# NOTICE — Sources, Redistribution Scope, and Authorization

*Last updated: 2026-06-15*

This file describes what this project redistributes, where the underlying
material comes from, and the basis for its use of each source. The code in
this repository is released under the CC0 1.0 Universal dedication in
[`LICENSE`](LICENSE). The data files in the bundled `opinions.db` — and in
the four primary-law databases (`constitution.db`, `statutes.db`, `rules.db`,
`admincode.db`) — are described below.

## Redistribution scope

The `text_content` field in the database contains, and only contains:

- **Opinions of the North Dakota Supreme Court.** Judicial opinions of state
  courts are not protected by copyright; they enter the public domain on
  authorship. This includes the opinion body, separate concurrences and
  dissents, and rehearing material when published with the opinion.
- **Court-authored syllabus material.** Pre-1953 opinions in the bound
  *North Dakota Reports* series include a "Syllabus by the Court" section
  authored by the court itself as the official restatement of the holding.
  This is part of the court's published work and is retained.
- **Factual record items.** Court of origin, presiding judge, attorneys of
  record, dates, parties, dispositions. These are facts and are not
  copyrightable. See *Matthew Bender & Co., Inc. v. West Publishing Co.*,
  158 F.3d 674 (2d Cir. 1998), holding that case reports describing court of
  origin, attorneys, judges, and disposition are not protected expression.
- **Opinions of the North Dakota Attorney General** (in `ag_opinions.db`).
  These are official written opinions of a state executive officer, prepared
  and published as government works; like judicial opinions they are edicts of
  government not protected by copyright. Retrieved from the Attorney General's
  own public opinions-search site (see Sources below).
- **Opinions of the North Dakota Judicial Ethics Advisory Committee** (in
  `jeac_opinions.db`). Advisory opinions of a committee established under the
  Supreme Court's authority, published as public documents on the court's own
  website (ndcourts.gov); government works of the same character. The `digest`
  field reproduces the committee page's own question summaries.

The `text_content` field does NOT contain:

- **West editorial headnotes** or key-number content. These are
  proprietary editorial work of Thomson Reuters and are filtered out during
  ingest.
- **West editorial Synopsis stubs** or holding summaries. These are removed
  during ingest, which preserves the court's narrative statement of facts when
  the Synopsis section contains one but strips the West editorial wrapper
  around it.

## Sources

### CourtListener (Free Law Project)

[CourtListener](https://www.courtlistener.com) is a project of the
[Free Law Project](https://free.law), a 501(c)(3) non-profit. CourtListener
publishes a large corpus of public-domain opinion text along with curated
metadata (cluster IDs, parallel citations, judge fields, etc.). The bulk of
this database was originally built from CourtListener's North-Western
Reporter (N.W. and N.W.2d) coverage for North Dakota. Free Law Project
publishes its data for free public use, and we thank them for it.

### ndcourts.gov (North Dakota Court System)

[ndcourts.gov](https://www.ndcourts.gov) is the official site of the North
Dakota Court System. Opinions published there since 1997 are the canonical
text for that era. `archive.ndcourts.gov` also hosts an N.W.-citation index
(`/opinions/cite/`) of the court's own HTML opinions reaching back to the
mid-1960s; that court-sourced text is the **primary** `text_content` for
roughly 4,800 opinions in the 1953–1996 range (and a cross-check source for
1997–2019). A small number of North Dakota Court of Appeals decisions
reached this way are also included, tagged `court = "North Dakota Court of
Appeals"`. The project's scraper uses standard polite practices (low rate,
identification in the User-Agent) and only retrieves publicly-listed
materials.

### West reporters (Thomson Reuters)

The court's own opinion text — as published by West in the *North Dakota
Reports* (volumes 1–79, 1890–1953) and the *North Western Reporter*
(N.W./N.W.2d), in bound and electronic form — supplies the primary text
for the pre-1953 era and supplements or cross-checks the 1953–1996 range
where opinions are not otherwise court-sourced. That published opinion
text and the court-authored syllabi are edicts of government not protected
by copyright; only that public-domain content is extracted and included in
`opinions.db`. West's proprietary editorial content — headnotes,
key-number material, Synopsis stubs, and "Procedural Posture" lines — is
removed (see the strip/merge validators), and West's own document files
are not redistributed in this repository.

### attorneygeneral.nd.gov (ND Office of Attorney General)

The opinions in `ag_opinions.db` were scraped from the Attorney General's
public opinions-search page (`/opinions-search/`) and the opinion PDFs it
links. The AG publishes these opinions for public use; only the public-domain
opinion text is extracted (via `pdftotext`, with OCR for scanned PDFs). The
AG-opinions scraper reads only the public index and the PDFs it links, at a
polite single-connection pace.

## Primary law: Constitution, statutes, court rules, administrative code

Beyond the opinions corpus, the project ships four primary-law databases —
`constitution.db`, `statutes.db` (N.D.C.C.), `rules.db` (North Dakota court
rules), and `admincode.db` (N.D. Administrative Code). Their
`provision_versions.text_content` holds the text of North Dakota's government
edicts, with effective-date metadata for point-in-time (`as_of_date`) queries.

**Redistribution scope.** Edicts of government — constitutions, statutes,
regulations, and court rules — carry the force of law and are not protected by
copyright, regardless of who compiled or published them. See *Banks v.
Manchester*, 128 U.S. 244 (1888), and *Georgia v. Public.Resource.Org, Inc.*,
590 U.S. 255 (2020). These databases redistribute only that official edict
text together with its amendment/effective-date metadata. They do **not**
include commercial-publisher annotations, case notes, headnotes, or other
editorial apparatus from any annotated edition.

**Sources.**

- **Constitution** (`constitution.db`) — the current article/section text and
  the amendment chronology are from [ndconst.org](https://ndconst.org), a
  DokuWiki edition of the North Dakota Constitution dedicated to the public
  domain (CC0). The point-in-time layers — the original 1889 numbering in
  force 1889–1980, and the modern 1981–present reconstruction across the
  1981/1986/1997 reorganizations and later amendments — were built from
  official North Dakota primary sources: the *Constitutional Amendments
  Approved* compilations and Session Laws of the North Dakota Legislative
  Branch ([legis.nd.gov](https://www.legis.nd.gov)), the *North Dakota Blue
  Book* compilations (Office of the Secretary of State), the 1889/1895/1913/1925
  official printings, and a public-domain 1889 base transcription (validated
  against the official 1889 publication and the State Constitutions Project).
- **Statutes** (`statutes.db`) — the official North Dakota Century Code
  (N.D.C.C.), published by the North Dakota Legislative Branch at
  [ndlegis.gov](https://ndlegis.gov) (current text as of 2025-07-01).
- **Court rules** (`rules.db`) — the North Dakota court rules, published by the
  North Dakota Supreme Court at [ndcourts.gov](https://www.ndcourts.gov),
  including the court's own explanatory notes and amendment history.
- **Administrative Code** (`admincode.db`) — the North Dakota Administrative
  Code (N.D.A.C.), published by the North Dakota Legislative Branch at
  [ndlegis.gov](https://ndlegis.gov) (current text as of 2025-07-01).

As with the opinions corpus, these are offered as a working tool, not an
authoritative or official text; consult the official publications above for
authoritative text. The primary-law corpora are newer and less exhaustively
validated than the opinions corpus.

## Citation format

Citations included in the `citations` table are facts about where opinions
appear in published reporters (volume, page, neutral citation, parallel
citations). They are not copyrightable. Star pagination markers in
`text_content` (e.g., `*1080`) indicate the page-break locations as they
appeared in the bound volume; see *Matthew Bender* (above) for the holding
that page numbering is also not protected expression.

## Authoritative-text aspiration, not authoritative status

This corpus is offered as a working tool, not as an authoritative or
official text. As of 2026-07-16 every opinion carries an earned
verification status against its best available source (court PDF, West
bound text, the court's archive HTML, or bound-volume scan) — 100.0% in
all fourteen decades — and corrections are summarized in the per-release
notes. Errors can remain (a residual segment of 584 pre-1997 opinions is
capped at the quality of its single OCR source), and metadata validation
is ongoing. The editorial rules — source precedence, verbatim doctrine,
and the project's structural conventions — are applied consistently across
the corpus and maintained with the development pipeline.

For an authoritative source of any specific opinion, consult the published
opinion at [ndcourts.gov](https://www.ndcourts.gov) or the bound *North
Dakota Reports* or *North Western Reporter* volume.

## Code license

All code in this repository is dedicated to the public domain under the
[CC0 1.0 Universal dedication](LICENSE). Use it however you want.

## Contact

If you believe any redistributed content here is outside the scope
described above, or if you represent a source named in this notice and
have a concern about how the project uses your material, please open an
issue on the GitHub repository.
