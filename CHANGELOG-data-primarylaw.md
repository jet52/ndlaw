# Primary-Law Data Corrections Log

Changes applied to the primary-law databases (`constitution.db`, `constitution_history.db`, `statutes.db`, `rules.db`, `admincode.db`) after import. All corrections are also recorded in each corpus DB's `changelog` table.

## Batch `ndcc-fix-29-15-21-subsec3-2026-06-08` — restore dropped clause in N.D.C.C. § 29-15-21(3)

`statutes.db` · provision/version 11275 · field `text_content`

Subsection 3 had an **extraction gap**: a full clause dropped between "pursuant to section" and "considered a proceeding separate," leaving a dangling, ungrammatical sentence with no statutory cross-reference.

- **Was:** "…or child support pursuant to section⏎considered a proceeding separate…"
- **Now:** "…or child support pursuant to section **14-05-24 or an order for child custody pursuant to section 14-05-22 must be** considered a proceeding separate…"

The 17 missing words include both governing cross-references (the alimony/property/child-support modification statute § 14-05-24 and the child-custody statute § 14-05-22) and the operative verb phrase "must be." Without them the subsection failed to identify which modification proceedings are treated as separate from the original action for change-of-judge purposes.

Verified verbatim against the official current text, [N.D.C.C. ch. 29-15 PDF, ndlegis.gov](https://ndlegis.gov/cencode/t29c15.pdf#nameddest=29-15-21) (in force eff. 2025-07-01). `authority` recorded in the changelog table. Confidence: high (two independent reads of the official PDF agree).


## Batch `const-history-merge-2026-06-08` — fold historical layer into served constitution.db

`constitution.db` · +265 provisions / +421 versions (via `scripts/merge_const_history.py --apply`)

Merged the point-in-time historical layer (`constitution_history.db`, original 1889 numbering §§1–217 + Schedule, eff. 1889–1980) into the served `constitution.db` (modern art/§ numbering). The two are citation-disjoint (0 cite_key collisions), so the historical provisions are additive. Served DB went 201→466 provisions, 201→622 versions.

Effect: `lookup_authority` now answers point-in-time historical queries by original citation, e.g. `lookup_authority("N.D. Const. § 82", as_of_date="1945-01-01")` → the 1940 Art. 57 (LVII) text; modern queries unchanged; `search_authority` FTS indexes the historical text. Integrity: quick_check ok, FTS integrity-check ok.

This is Approach B (additive). NOT yet connected across the 1981 reorganization — see TODO-primarylaw.md PL-CONST-CROSSWALK (renumbering crosswalk), PL-CONST-AMEND-RECONCILE, PL-CONST-STRUCTURAL, and the BUILD-ORDER note (ingest_constitution → ingest_constitution_history → merge_const_history → make_release).