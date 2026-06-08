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

**Confidence the bug is systematic:** ~~moderate~~ → **HIGH. Confirmed systematic by heuristic sweep 2026-06-08.**

**Heuristic sweep results (2026-06-08):** scanned all 29,107 current `text_content` rows for the tight bug signature — a bare "section"/"subsection" preceded by a cross-reference preposition (`of`/`under`/`in`/`to`/`by`/`with`/`or`/`and`/`pursuant`) and **not** followed by a digit or spelled number. After stripping the land-description false-positive class (`section, township, range`): **607 hits across 555 distinct sections.** A ~55-context eyeball sample read as **>90% true positives** — only residual FPs were "section line" (road term) and "part of section" (property-tax land refs).

**Refined signature (sharper than the original line-drop guess):** the drop almost always **begins at a section-number cross-reference** and frequently **bleeds the referenced section's heading/catchline** in where the number should be — e.g. § 12.1-06-01 "under section **guilty of committing**…", § 11-28-06 "as provided in section **construction, equipping, and maintaining**…", § 45-20-01 "of section **partnership business**…", § 54-52.1-03.2 "pursuant to section **education who elect**…". § 29-15-21(3) is the same bug with a longer span (it swallowed a full line). **Working hypothesis:** the ndlegis.gov cencode PDFs render section cross-references as hyperlinks/named destinations (`#nameddest=…`); the extractor drops the link's anchor text (the number) and sometimes adjacent runs, occasionally substituting the destination's heading. Root-cause should focus on hyperlink/annotation handling in the PDF text layer, **or** switch to a cross-reference-clean source.

**Magnitude:** ~600 corrupted cross-references across ~555 sections (≈1.9% of the corpus) — each silently drops a statutory cross-reference, the highest-stakes kind of error for an authoritative text. This is NOT a hand-fixable tail; it needs the extractor fix + full re-ingest + re-validation, not per-section patches. (29-15-21 was patched individually only because it was the surfacing instance.)

**Detector:** the tight-pattern query is the triage tool; save it as `triage/` script when §1 begins. The full authoritative diff (re-extract vs DB) remains the definitive check — the heuristic only finds drops that leave an ungrammatical seam, not clean substitutions.

---

### PL-CONST-MERGE-B · DONE 2026-06-08 — historical layer merged into served `constitution.db`

`scripts/merge_const_history.py --apply` folded `constitution_history.db` (265 provisions / 421 versions, 1889 numbering, eff. 1889–1980) into the served `constitution.db` (now 466 provisions / 622 versions). Cite-disjoint from the modern art/§ provisions (0 collisions). `lookup_authority("N.D. Const. § 82", as_of_date="1945-01-01")` now returns the historical point-in-time text; modern queries unchanged; FTS indexes the historical text. This is Approach B (additive, original-numbering). The items below are the remaining integration work.

**⚠️ BUILD-ORDER NOTE (important):** `constitution.db` is a regenerable artifact and the merge is NOT part of `ingest_constitution.py`. The correct build sequence on the build machine is:
1. `python -m ndcourts_mcp.ingest_constitution --apply`   (rebuild modern, from ndconst.org)
2. `python -m ndcourts_mcp.ingest_constitution_history --apply`   (rebuild historical layer; `rm -f constitution_history.db` first — not idempotent)
3. `python scripts/merge_const_history.py --apply`   (fold history into constitution.db)

then `scripts/make_release.sh`. If you rebuild `constitution.db` (step 1) without re-running step 3, the served DB loses the historical layer. The merge refuses to run twice (guards on the 1889 scheme), so re-running after a fresh step 1 is safe. **Corrections to historical text go upstream into `constitution_amendments.json` → re-run steps 2+3**, not edited directly in `constitution.db`.

### PL-CONST-CROSSWALK · 1889↔modern renumbering crosswalk (Approach A — the real integration)

After PL-CONST-MERGE-B, the two citation spaces are served but NOT connected: a **modern** cite for a **pre-1981** date returns nothing, a **1889** cite for a **post-1981** date returns nothing, and historical versions end at the 1980-12-31 reorg cap. To give continuous point-in-time history across the 1981 reorganization from either citation, build a crosswalk mapping each original §1–§217 + Schedule provision → its modern article/§ (≈217 mappings; some split/merge/repealed).
- **Source** the mapping from the 1981 reorganization "disposition tables" / the 1972 Constitutional Convention + 1979–80 revision materials (some Blue Books print old↔new comparison tables). This is the load-bearing artifact.
- **Then** either (A1) carry both citations on one provision's version timeline (old cite pre-1981, modern cite 1981+), or (A2) keep separate provisions linked by a `successor`/`lineage` table (old §82 → modern art. V §2). A2 is the smaller schema change.
- Wire the crosswalk into `merge_const_history.py` (or a successor step) so the merged historical versions attach to / link from their modern counterparts.

### PL-CONST-AMEND-RECONCILE · dedup amendment events across the two sources

`constitution.db` already carried amendment *events* from ndconst.org annotations (keyed to modern provisions); the merged historical layer carries the session-law *text* of each pre-1981 version plus its own `amendments` rows (keyed to 1889 provisions). The same amendment (e.g. the 1940 §82 / Art. 57 change) is now represented from both sources. Once the crosswalk exists, reconcile/dedup the `amendments` rows so `get_authority_history` shows one coherent chronology per provision rather than two parallel ones.

### PL-CONST-STRUCTURAL · 4 structural pending amendments (still unserved)

`constitution_history.db` still has 3 `status:"pending"` amendments + 1 deferred change that the whole-provision ingest can't apply (so they're absent from the merged served DB too): **LXXVIII** (amends only subdivision (d) of subsection 6 of amend. art. LIV), **XCVI** (subsections 2 & 4 of art. LIV), **XC's 2nd change** (subsection 1 of art. LIV), and **LXXXI** (partial repeal of only the 10th paragraph of §25). amend. art. LIV is stored as ONE provision; these need either the full enclosing-provision text spliced per amendment or art. LIV subdivided into subsection provisions, plus partial-repeal modeling for LXXXI (note §25 was wholly repealed by CV in 1979, so LXXXI governs only the 1964–1979 window). Verbatim text already captured in `data/const_amend_session_law_extraction_2026-06-08.md`. Apply upstream (ingest_constitution_history), then re-run steps 2+3 of the build sequence above.
