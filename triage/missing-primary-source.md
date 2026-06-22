# Missing / incorrect primary-source PDFs

Log of opinions whose **official primary source of authority** (the ndcourts.gov
PDF, for the neutral-cite/PDF era) is **missing from `~/refs/nd/opin/pdfs/`** or
**misfiled** (the file under that name contains a *different* opinion).

Discovered 2026-06-22 while triaging the `refs_diff` CONTENT_LOSS bucket
(`triage/sig-drops-classified.csv`). Key finding: in every CONTENT_LOSS "major"
case checked, the **DB `text_content` is the correct, complete opinion** and the
`~/refs` *source markdown* is the contaminated/bloated/wrong-opinion copy — so
these are **source-tree defects, not DB defects.** No DB body needs restoring.
The action here is to obtain the correct official PDF for the source tree.

Verification method: `mutool draw -F txt <pdf>` → compare the PDF's caption /
neutral cite / docket against the DB record; compare DB body length+tail to the
PDF (or, pre-PDF, to the archive `.htm`).

---

## A. Misfiled PDF — RESOLVED 2026-06-22 ✓

Same docket produced two neutral-cited opinions (court retained jurisdiction and
ruled again under the same case number). The scraper saved the **earlier**
opinion's PDF under the later opinion's filename. For Queen the two were in fact
**transposed** in the tree (`pdfs/2022/2022ND178.pdf` held 2023 ND 32 and
`pdfs/2023/2023ND32.pdf` held 2022 ND 178). DB bodies were correct throughout;
only the source PDFs were misnamed.

User obtained correct copies (2026-06-22); filed after verifying each misfiled
original is preserved under its correct name. Where two copies existed, kept the
**C-Track** (ND Supreme Court cTrack — court-native) over the **BitMiracle**
third-party re-render; for 2023 ND 32 the two were byte-identical in body text.

| 8-digit docket | neutral cite | oid | case | was on disk | now filed (source) |
|---|---|---|---|---|---|
| **20110136** | 2015 ND 15 | 16397 | Nemec v. Disciplinary Board | 2011 ND 128 (preserved at `pdfs/2011/2011ND128.pdf`) | `pdfs/2015/2015ND15.pdf` ✓ C-Track, filed 2015-01-15; Westlaw `.doc` cross-check clean (PER CURIAM, 858 N.W.2d 326) |
| **20220121** | 2023 ND 32 | 18142 | Queen v. Martel | 2022 ND 178 ⇄ 2023 ND 32 transposed | `pdfs/2023/2023ND32.pdf` ✓ C-Track (2023ND32b), filed 2023-02-23; `pdfs/2022/2022ND178.pdf` ✓ corrected too |

## B. No PDF in tree — archive `.htm` present (1997; lower priority)

For 1997 the court's primary *electronic* source is the archive HTML (filed under
the 6-digit docket), which **is present** for all of these; the scraper simply
never collected a PDF. N.W.2d reporter is the print authority. DB bodies verified
clean & complete; `~/refs` source markdown is the bloated/garbled copy.

| 8-digit docket | neutral cite | oid | case | archive .htm |
|---|---|---|---|---|
| 19960070–79 (consol.) | 1997 ND 1 | 12360 | State v. Kenner | 960070/960071/960079.htm ✓ |
| 19960226 | 1997 ND 40 | 12392 | Sickler v. Kirkwood | 960226.htm ✓ |
| 19960215 | 1997 ND 59 | 12397 | Austin v. Towne | 960215.htm ✓ |
| 19960235 | 1997 ND 50 | 12398 | Owan v. Owan | 960235.htm ✓ |
| 19960329 | 1997 ND 72 | 12415 | Mosbrucker v. Mosbrucker | 960329.htm ✓ |
| 19960243 | 1997 ND 102 | 12455 | State v. Ost | 960243.htm ✓ |
| 19970039 | 1997 ND 156 | 12514 | State v. Sisson / Miekels v. Hallock | 970039.htm ✓ |

## C. PDF present but text layer unusable (degraded; lowest priority)

| 8-digit docket | neutral cite | oid | case | issue |
|---|---|---|---|---|
| 19980094 | 1998 ND 171 | 12747 | Kouba v. Febco | `pdfs/1998/1998ND171.pdf` text layer is two-column-scrambled OCR; page image is fine. DB body clean & complete. |

---

## Action

- **A (2 cases):** fetch the correct official PDF by neutral cite from
  ndcourts.gov and replace the misfiled file. These are the real "obtain correct
  PDF" tasks. Tracked in `TODO-audit.md`.
- **B (7 cases):** optional — backfill 1997 PDFs if/when available; primary
  source already covered by archive `.htm` + N.W.2d.
- **C (1 case):** optional re-OCR; no data loss.

These are **not** DB corrections — no `changelog` entry. The DB bodies are
already correct.
