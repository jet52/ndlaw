# NOTICE — Sources, Redistribution Scope, and Authorization

*Last updated: 2026-05-13*

This file describes what this project redistributes, where the underlying
material comes from, and the basis for its use of each source. The code in
this repository is released under the CC0 1.0 Universal dedication in
[`LICENSE`](LICENSE). The data files in the bundled `opinions.db` are
described below.

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

The `text_content` field does NOT contain:

- **Westlaw editorial headnotes** or key-number content. These are
  proprietary editorial work of Thomson Reuters and are filtered out at
  ingest time (see `ndcourts_mcp/ingest_westlaw.py` and the validators in
  `ndcourts_mcp/merge_westlaw_text.py`).
- **Westlaw editorial Synopsis stubs** or holding summaries. These are
  removed by `ndcourts_mcp/strip_westlaw_synopsis.py`, which preserves the
  court's narrative statement of facts when the Synopsis section contains
  one but strips the Westlaw editorial wrapper around it.

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

### Westlaw (Thomson Reuters)

Bound *North Dakota Reports* entries (volumes 1–79, 1890–1953) and
N.W.2d-era opinions for the 1953–1996 range were retrieved manually from
Westlaw by a user with authorized Westlaw access — for pre-1953 as the
primary bound text, and for 1953–1996 to supply or cross-check opinions
not otherwise court-sourced. The Westlaw `.doc`/`.rtf` files themselves
are not redistributed in this repository. Only the public-domain content
(court opinion text and court-authored syllabi), filtered by the rules
above — Westlaw editorial headnotes, Synopsis stubs, and "Procedural
Posture" lines removed — has been extracted and is included in
`opinions.db`. No automated retrieval from Westlaw is performed by any
code in this repository; the `ingest_westlaw.py` and `receive_westlaw.py`
tools only read files that the user has placed on disk.

## Citation format

Citations included in the `citations` table are facts about where opinions
appear in published reporters (volume, page, neutral citation, parallel
citations). They are not copyrightable. Star pagination markers in
`text_content` (e.g., `*1080`) indicate the page-break locations as they
appeared in the bound volume; see *Matthew Bender* (above) for the holding
that page numbering is also not protected expression.

## Authoritative-text aspiration, not authoritative status

This corpus is offered as a working tool, not as an authoritative or
official text. The text has been validated against multiple sources and
every correction is recorded in the `changelog` SQLite table and
[`CHANGELOG-data.md`](CHANGELOG-data.md), but errors remain and are
ongoing work. Most of the 1953–1996 era now carries court-sourced
(archive.ndcourts.gov) and/or Westlaw bound text; a residual pre-~1965
slice (roughly 1,200 opinions) remains single-source CourtListener
N.W.2d OCR pending manual Westlaw acquisition. See
[`TODO-validation.md`](TODO-validation.md) for the current state of
validation work.

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
