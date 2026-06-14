# Pilot reconstruction — N.D. Const. art. X, § 21 (coal severance permanent trust fund)

Read-only proof of the modern point-in-time reconstruction pipeline (TODO #0).
Current DB state: ONE version (eff 1994-07-14, open). Reconstructed: THREE versions.

## Reconstructed timeline

| Version | Effective interval | Amendment | Source | Endpoint of text |
|---|---|---|---|---|
| v1 | 1981-01-01 → 1990-06-30 | CIX (gen. ballot 1980-11-04) | 1981 CAA ch. 657 (creation: "adding thereto the following article") | ends "…credited to the general fund of the state." |
| v2 | 1990-07-01 → 1994-07-13 | CXXV (primary 1990-06-12) | 1991 CAA ch. (SCR, "amended and reenacted") | + "Up to fifty percent…lignite research, development, and marketing as provided by law." |
| v3 | 1994-07-14 → (open) | CXXIX (primary 1994-06-14) | 1995 CAA ch. 640 | + "An additional twenty percent…clean coal demonstration projects…" = **current DB text** |

Clean monotonic accretion — each amendment appended one sentence.

## Gate result
Extracted CXXIX (1995 CAA) text == current DB text: **EQUAL (172/172 tokens)** after
normalization. Raw byte-equality fails ONLY on fi-ligature OCR damage in the 1995
CAA text layer (`ftrst`→first, `ftfty`→fifty). The 1991 CAA text layer was clean.

## Pipeline lessons (for scaling to ~96 provisions)
1. **Locate by content, not the `#page` anchor or a fixed "section N of article X" string.**
   CIX *created* the provision ("adding thereto the following article") and never names
   art. X §21; later amendments use "section 21 of article X … amended and reenacted."
   The locator must handle creation / amend-reenact / repeal phrasings.
2. **Text-layer quality varies per PDF** (1991 clean, 1995 fi-ligature damaged). Prior-version
   text extracted from CAA PDFs needs normalization + a ligature-repair pass before storage.
3. **Keep the DB's clean current-version text as-is.** Use CAA PDFs only for PRIOR versions.
   The gate is SUBSTANTIVE (normalized) equality confirming the amendment chain is complete
   and correctly terminated — not byte-equality, and not a reason to overwrite current text.
4. Use `effective_date` for interval boundaries (the measure text itself states the effective
   date); `election_date` is informational.
5. `amendment_number` rows are duplicated per affected section — dedup before grouping.

## Proposed DB splice (PENDING APPROVAL — not yet written)
Convert art. X §21 from 1 version → 3 versions as tabled above (v3 text unchanged).
Per the build-sequence discipline this must be done UPSTREAM (in `ingest_constitution`,
not hand-edited into `constitution.db`) so a rebuild reproduces it, with a changelog batch.
