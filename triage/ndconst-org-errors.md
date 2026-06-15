# ndconst.org data errors — running list (for later upstream correction)

ndconst.org is the source for the modern constitution layer (text + the `:amendments`
chronology). The reconstruction campaign's verification gates double as a data-quality
audit of that source. Each error below was **confirmed against primary sources** (the
enacting measure and/or the constitutional text) and **corrected in our DBs**
(reproducibly, via overlays in `ingest_constitution.py` or the corrections data file).
"Upstream" = whether ndconst.org itself has been fixed.

Legend — Upstream: ☐ not yet reported · ☑ fixed by user on ndconst.org

| # | Where (ndconst.org) | Error | Correct value | Primary source | Our fix | Upstream |
|---|---|---|---|---|---|---|
| 1 | `:amendments` row 167 (Legacy Fund, HCR 3033) | `affected` = "art. XVI, §§ 1-5" (copied from row 165) | **art. X § 26** | bill 23-3092 ("amend … section 26 of article X") | `AMENDMENT_AFFECTED_CORRECTIONS` (`fix-amend167-legacyfund-2024-06-14`) | ☐ |
| 2 | art. IX § 12 **and** § 13 page text | **Stale current text** — pre-2024 terminology ("deaf and dumb", "feebleminded", "insane", "mentally ill"); amendment 166 recorded but never applied | the post-2024 "Updated Terminology" text | bill 23-3015 (SCR 4001), verified 450 dpi | `data/const_modern_text_corrections.json` + `apply_text_corrections` (`modern-ix-stale-text-2026-06-14`) | ☐ |
| 3 | `:amendments` row 164 (term limits) | `source_url` → `…/68-2023/…/caa.pdf` (wrong file type + 404); it's an **initiated** measure | `…/68-2023/…/ima.pdf` (S.L. 2023 ch. 594) | sl2023.pdf p.2279 "INITIATED MEASURES APPROVED" | `AMENDMENT_SOURCE_URL_CORRECTIONS` (`fix-amend164-source-2026-06-14`) | ☐ |
| 4 | `:amendments` row 164 (term limits) | `effective_date` = 2022-11-08 (election date) | **2023-01-01** | art. XV § 5 ("effective on the first day of January immediately following approval") | `AMENDMENT_EFFECTIVE_DATE_CORRECTIONS` (`fix-amend164-effdate-2026-06-14`) | ☑ (user fixed 2026-06-14) |

## Suspected / low-confidence (not yet corrected — needs verification)

| # | Where | Suspected issue | Note |
|---|---|---|---|
| S1 | `:amendments` rows 119 & 120 (art. IV recreation) | `election_date` looks wrong (1984-06-12 / 1984-11-06 for 1985-session measures, effective 1986-12-01) | CREATE provisions; effective date is plausible, only the election-date *metadata* looks off. Verify against S.L. 1985 ch. 706/707 before changing. Low priority. |

## How more get found
The campaign gate "latest amendment's enacted text == DB current text" is the
**staleness detector** (it caught #2). Provisions not yet reconstructed haven't been
gate-checked, so additional stale-text or mis-mapping errors may surface as
reconstruction proceeds. A systematic sweep = run that gate across all amended
provisions.
