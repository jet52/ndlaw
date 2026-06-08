# TODO — Primary-Law Corpora Validation

Validation backlog for the primary-law databases (`constitution.db`, `constitution_history.db`, `statutes.db`, `rules.db`, `admincode.db`). Opinions-corpus work lives in `TODO-validation.md`; const-history ingest notes live in `data/const_history_*.md`.

## Open

### PL-1 · Investigate dropped-line extraction bug in `ingest_statutes.py` and re-validate all of `statutes.db`

**Trigger:** N.D.C.C. § 29-15-21(3) was found with a full clause missing — 17 words dropped between "pursuant to section" and "considered a proceeding separate," removing both cross-references (§ 14-05-24, § 14-05-22) and the verb "must be." Fixed under batch `ndcc-fix-29-15-21-subsec3-2026-06-08` (see `CHANGELOG-data-primarylaw.md`); the official text was verified against the ndlegis.gov cencode PDF.

**Why it's systematic, not one-off:** the missing words — "14-05-24 or an order for child custody pursuant to section 14-05-22 must be" — are **exactly one wrapped physical line** in the source PDF (`https://ndlegis.gov/cencode/t29c15.pdf`). The drop sits at a line boundary (`section⏎considered`), which points at a line-join / wrap-handling defect in PDF text extraction rather than a content-specific fluke. If the extractor drops a line under some repeatable condition (page break, column artifact, specific wrap pattern), there are likely **other affected sections among the 29,107** ingested (batch `statutes-ingest-2026-06-07`, source `~/refs/statute/NDCC`, via `ingest_statutes.py`).

**Two tasks:**

1. **Root-cause** the extraction path in `ingest_statutes.py` (and whatever PDF-text layer it calls). Reproduce on § 29-15-21, find the exact condition under which the line was dropped, and determine its blast radius. Fix the extractor so a re-ingest is clean.

2. **Re-validate the corpus** for similar drops. Candidate detectors (cheap → thorough):
   - **Cheap heuristics over current `text_content`:** dangling cross-references ("pursuant to section" / "under section" / "in section" immediately followed by a non-numeric token or newline); sentences with no terminal punctuation before a subsection marker; abnormally short lines mid-sentence; lowercase-after-line-break where a clause looks severed.
   - **Authoritative diff:** re-extract all sections from the source PDFs with a corrected/independent extractor and diff against DB `text_content` section-by-section (the same diff-QA method used for the const amendments). This is the definitive check; the heuristics just triage where to look first.

   Apply any corrections as their own changelog batches + `CHANGELOG-data-primarylaw.md` entries, each verified against the official ndlegis.gov text. Note that this bug is **not idempotent-safe to ignore** — if the extractor is at fault, the same drops will recur on the next statutes re-ingest until §1 is fixed.

**Confidence the bug is systematic:** moderate. One confirmed instance with a structural (line-boundary) signature; blast radius unknown until §1.
