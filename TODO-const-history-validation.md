# Work Plan — Finish Validation of the Historical Constitution

**Goal:** a `constitution.db` that reliably returns the constitutional text in effect at **any moment in time**, from **either** citation scheme (1889 original §1–§217 or modern art./§), across the 1981 reorganization — to a standard the ND Supreme Court could adopt as authoritative.

Scoped 2026-06-13. This consolidates the const-specific items from `TODO-primarylaw.md` (PL-CONST-*) plus two validation pieces those items do not yet capture (#4, #5). The PL-CONST-* entries remain the per-item detail; this file is the sequenced plan.

---

## State of play (what is already solid — do NOT redo)

- **Text faithfulness of the 1889–1980 layer is essentially complete.** Segments 1–4 + the Blue-Book series (amend. LXV–CVIII) all reconciled against session laws / official compilations; round-2, round-3, and Blue-Book `needs_fix` buckets each have matching fix commits; the 138-variant cross-publication log was hardened against clean 1925 marker OCR. Enacted session-law text governs throughout. Artifacts: `data/const_revalidation_round{2,3}_2026-06-08.json`, `data/const_bluebook_revalidation_2026-06-08.json`, `data/const_history_judgment_calls.md`.
- **Merge into the served DB is done.** `constitution.db` = 466 provisions / 622 versions; historical layer = 421 versions spanning 1889-11-02 → 1980-12-04; cite-disjoint from the modern art./§ layer (0 collisions). Build sequence (NOT idempotent) documented in `TODO-primarylaw.md` PL-CONST-MERGE-B.
- **Within-provision timeline integrity is clean** (verified 2026-06-13): 0 provisions with timeline gaps, 0 with overlapping versions, 0 with >1 open-ended ("current") version, 0 with zero versions. The per-provision point-in-time machinery is sound.
  - **⚠️ CAVEAT (found 2026-06-14): for the MODERN layer this is clean *trivially*.** All 201 modern reorg provisions (`art. ROMAN, § N`, excluding `amend. art.`) have **exactly one version each** (`multiversion=0`) — there are no intervals to gap or overlap. The modern constitution (1981–present) is served as a **flat current snapshot**, not a versioned timeline. See item **0** below — this is the actual load-bearing gap.

**Re-run these integrity checks at the end of any data change** (they are the regression guard):
```sql
-- gaps/overlaps between adjacent versions of a provision
WITH v AS (SELECT provision_id, effective_start, effective_end,
  LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) AS next_start
  FROM provision_versions)
SELECT count(*) FROM v WHERE next_start IS NOT NULL AND effective_end IS NOT NULL
  AND effective_end!='' AND date(effective_end)!=date(next_start)
  AND date(effective_end,'+1 day')!=date(next_start);          -- expect 0
-- >1 current version
SELECT count(*) FROM (SELECT p.id FROM provisions p JOIN provision_versions v ON v.provision_id=p.id
  WHERE p.corpus='const' AND (v.effective_end IS NULL OR v.effective_end='')
  GROUP BY p.id HAVING count(*)>1);                            -- expect 0
-- zero-version provisions
SELECT count(*) FROM provisions p WHERE corpus='const'
  AND NOT EXISTS (SELECT 1 FROM provision_versions v WHERE v.provision_id=p.id);  -- expect 0
```

---

## What's left — itemized

### 0. Modern point-in-time reconstruction — THE actual load-bearing gap  *(found 2026-06-14, census prototype)*
The modern reorg layer (1981–present) has **no point-in-time depth**: each of the 201 modern provisions carries a single version stamped with its last-change date. The **~59 post-1981 amendments (CIX–CLXVII, 1981–2024) are recorded as `amendments` rows but never applied as text versions.** A query for any modern cite "as of" a past date returns current text or nothing — the pre-amendment text simply does not exist in the DB. This is a bigger hole than the 1981 seam (#1) or the structural four (#2): it breaks the point-in-time claim for the entire era users care about most.

**Feasibility: extract-and-splice, NOT research (confirmed 2026-06-14).** Every post-1981 amendment row carries a `source_url` to its session-law Constitutional Amendment Act PDF (`legis.nd.gov/assembly/sessionlaws/YYYY/pdf/CAA.pdf#page=N`) — the enacted text, page-anchored — and its `affected` field is already in modern `art./§` form. Build path:
- ~96 provisions need reconstruction (35 stamped 1981–96 + 61 stamped 1997+); the 105 stamped pre-1981 are unchanged-since-reorg, single version defensible.
- Group post-1981 amendments by affected modern provision; for each, fetch the CAA PDF at its `#page`, extract the enacted section text = that provision's version effective on the amendment date.
- 1981 base text (1981 Blue Book / Replacement Vol 13, see #1) fills the head of each timeline.
- **Built-in gate:** the last CAA extraction per provision must equal the current DB text. Mirrors the historical-layer method (session-law text governs). Apply upstream in `ingest_constitution`, re-run build steps, re-run the integrity checks (which become non-trivial once provisions are multi-version).
- Note: `amendment_number` dedup needed — several amendments appear as multiple rows (one per affected section).

**Pilot DONE 2026-06-14** (`triage/const-pilot-2026-06-14/`): art. X §21 reconstructed 1→3 versions from CAA PDFs, gate passed 172/172 tokens; proof-widened across 6 varied measures (create+repeal, multi-section, cross-article, structural) — extraction is solved (pdftotext clean across 1965–2019; only the 1995 fi-ligature needs OCR, recovered by both marker + Claude direct read), the hard work is structural.

**Present→1981 CHAIN VALIDATED ON SCRATCH 2026-06-14** (6 provisions in `/tmp/const-scratch.db`, integrity 0/0): clean 3-version chain (art X §21, base = 1981 BB §21 verbatim) + 5 single-amendment redlines, **all passing the independent 1981 Blue Book gate** (which caught + forced fixes on 2 of 5 hand-read redlines — the gate is mandatory). **CLASSES that need work before live:** (1) **dense heavily-amended sections (art VIII §6 class) → NATIVE-SOURCE acquisition required** — both PDF sources for §6's 1981 base are OCR-degraded (BB subsection-2 ocr_quality 0.606; 1994 strikethrough garbled). Ties to PL-SOURCE-FILES. (2) resolver misses 2018–2024 session-law URL formats. (3) create-article (phase 2) + not-BB-gateable provisions (art VI §13, X §24) → census cross-check. Detail + decisions in `data/design-modern-const-versions-2026-06-14.md` §6a. **Full ingest-integration design: `data/design-modern-const-versions-2026-06-14.md`** (separate `scripts/reconstruct_modern_versions.py` as build step 1.5; content-based locator classifying amend-reenact / create-article / repeal / described-edit; substantive gate with preserve-on-fail; idempotent; sources from the on-disk `~/refs/nd/sess/<year>_sl/CAA.pdf` refs tree).

### 1. The 1981 reorganization seam — load-bearing for the *rewritten* provisions  *(= PL-CONST-CROSSWALK)*

**Crux RESOLVED 2026-06-14 (alignment prototype `triage/const_crosswalk_align_2026-06-14.py`).** Clean DB-to-DB shingle matching (old 1980 text → modern current text) recovers the crosswalk for verbatim-carried provisions but **not** for rewritten ones:
- **93 CONFIDENT** auto-matches (jaccard ≥0.55) — e.g. Declaration of Rights carries at 1.00 (old §2→art. I §2, §4→art. I §3, §9→art. I §4).
- **148 NOMATCH** = 47 repealed-pre-1981 (correct), 3 Schedule/amend-art, and **98 active bare-sections that genuinely have a modern home but were substantively rewritten** by the 1972 convention / 1979–80 revision. Proof: old §82 → modern art. V §2 scores only 0.08 yet both open *"…the qualified electors of the state at the times and places of choosing members of the legislative assembly…"* — same lineage, body rewritten. Text similarity has a ceiling here; no better matcher closes a 0.08.
- **Conclusion:** alignment gives the easy ~half for free + validates the disposition table on arrival, but the rewritten ~98 provisions **need the official 1981 disposition table — NDCC Replacement Volume 13 (1981)** (State Law Library / Legislative Council / HeinOnline). That artifact is NOT on disk; acquiring it is the real cost driver for #1, as the original Crux warned.

*(original framing of the seam follows)*
Two citation spaces are served but unconnected:
- A **modern** cite (`art. V, § 2`) at a **pre-1981** date returns nothing.
- An **1889** cite (`§ 82`) at a **post-1981** date returns nothing.
- Historical versions hard-stop at 1980-12-31; modern versions begin at the reorg.

No crosswalk links original §1–§217 + Schedule → modern art./§. Until it exists, ~half of all cross-1981 (date, citation) queries fail silently.
- **Build:** a crosswalk of ≈217 mappings (some split/merge/repealed). Recommend **schema A2** — a `lineage`/`successor` table (`old §82 → modern art. V §2`) over A1 (dual cites on one timeline); smaller schema change, resolves either cite at either date through the link.
- **Source (load-bearing):** the 1981 reorganization **disposition tables** — 1972 Constitutional Convention + 1979–80 revision materials; some Blue Books print old↔new comparison tables. **Confirm this artifact exists before committing a timeline** (see Crux).
- Wire into `scripts/merge_const_history.py` (or a successor step).

### 2. Four structural partial-amendments, unserved  *(= PL-CONST-STRUCTURAL)*
Whole-provision ingest can't represent amendments that touch a sub-part:
- **LXXVIII, XCVI, XC's 2nd change** — amend subdivisions/subsections of amend. art. **LIV**, stored as ONE undivided provision (confirmed: art. LIV has exactly 1 version, 1938-07-28 → 1980-12-31, no internal versions).
- **LXXXI** — partial repeal of only the **10th paragraph of §25**, governing the **1964–1979** window (note: §25 wholly repealed by CV in 1979, so LXXXI governs only 1964–1979). Confirmed missing: §25's chain jumps 1918-12-05 → 1978-12-31 with no LXXXI splice.
- Verbatim text already captured: `data/const_amend_session_law_extraction_2026-06-08.md`.
- **Build:** ~~either splice the full enclosing-provision text per amendment, or subdivide art. LIV into subsection provisions~~ **DECIDED 2026-06-14: SPLICE whole-provision versions (no subdivision, no schema change)** — see `data/design-modern-const-versions-2026-06-14.md` §6a. Subsection-provisions gain nothing and fracture FTS/citation/point-in-time. Add partial-repeal modeling for LXXXI. Apply upstream in `ingest_constitution_history`, then re-run build steps 2+3.
- Independent of the crosswalk — can proceed immediately.
- **Verification standard (set 2026-06-14):** every reconstructed prior version must pass the **1981 Blue Book independent gate** (normalized-substring match against `~/refs/nd/const/processed/1981_blue-book_constitution.md`). The splicer's internal `after==current` gate is vacuous; the BB gate caught 2 of 5 hand-read reconstructions with errors. For multi-amendment chains, gate the `[1981,d1)` base + rely on base→current edit-chain consistency. NOT-cleanly-BB-gateable provisions (art VI §13, X §24 — judicial/finance) route to the census external cross-check first.
- **Side finding:** 54 modern provisions carry ndconst.org extraction artifacts (`])]`, stray `[`) in `text_content` — separate data-quality cleanup.

### 3. Amendment-event reconciliation / dedup  *(= PL-CONST-AMEND-RECONCILE)*
Same amendment now appears twice: from ndconst.org annotations (keyed to modern provisions) and from the historical session-law layer (keyed to 1889 numbering). `get_authority_history` will show two parallel chronologies per provision. Dedup so each provision shows one coherent timeline.
- **Depends on the crosswalk** (#1): can't reconcile old §82 with modern art. V §2 until they're linked.

### 4. Amendment census / completeness audit — PROTOTYPE DONE 2026-06-14
`triage/const_amendment_census_2026-06-14.py` (read-only) builds the master table (`triage/const-census-2026-06-14.tsv`): normalizes amendment numbering across both DBs (arabic/Roman/compound), enumerates the series, and checks **event-recorded vs. text-applied**. Findings:
- **Span II(2)–CLXVII(167), no internal gaps**, but **amendment I (1) is absent below the floor** — needs external confirmation (likely a real missing first amendment).
- **~59 post-1981 amendments are event-recorded but text-unapplied** → this is what surfaced item **0** above (the headline finding).
- Reconfirms the structural four (LXXVIII/XCVI/XC-2nd/LXXXI) as event-rows-without-splices.
- **Still owed (the original external cross-check):** diff the held series against an authoritative enumeration (official ND Blue Book amendment list / Secretary of State measure history / ndlegis constitutional measure index) — the census proves *internal* completeness (ndconst.org is self-consistent II–CLXVII) but not that ndconst.org isn't itself missing a ratified amendment. Confirm amendment I and the top of the series (is CLXVII actually the latest?) against the external list.
- Master table's `affected modern art./§` column is the crosswalk skeleton (#1) and the dedup key (#3).

### ✅ 2026-06-14 progress (on scratch `/tmp/const-scratch.db`)
- **Amendment I FOUND + ADDED** (#4): it is the **Prohibition Article (Art. 20 / §217)**, separately submitted on the 1889 ballot (Schedule §20), adopted on statehood, repealed 1932 by Amend. XLVII. Text already in our sources + DB (§217 versions correct); only the adoption *event* was missing. Added as an `amendments` row (`const-amend-I-2026-06-14`). Series now I..CLXVII gap-free. **DONE 2026-06-14:** encoded in `constitution_amendments.json` as a `type:"event"` record + new event-only branch in `ingest_constitution_history`; a clean rebuild reproduces the row field-for-field (no longer a post-build hand insert).
- **LXXXI structural amendment DONE** (#2): §25 v470 [1918–1978] still carried the 10th paragraph (publicity-pamphlet clause) that LXXXI repealed 1964-12-03. Split into [1918,1964)/[1964,1978); §25 timeline now 5 clean versions. **Snapshot-validated: §25 vs 1973 print improved 0.88 → 0.984.** (`const-struct-LXXXI-2026-06-14`.) **Upstream TODO** + verify against the snapshot harness on rebuild.
- **Snapshot-diff harness BUILT + RUN** (#5 below): `triage/const-pilot-2026-06-14/snapshot_diff.py`. **1925: 213/215 = 99% match-or-near; 1973: 207/213 = 97%.** Residual = print-style variants (numerals vs words: §95 "600,000"), repeal-notice-format differences (both agree repealed), and compilation OCR/parsing (1954 OCR-degraded — weak witness). **No real DB point-in-time errors found.** The 1889–1980 historical layer is independently validated against the printed compilations.
- **ALL FOUR STRUCTURAL AMENDMENTS DONE (#2 CLOSED on scratch 2026-06-14):** art. LIV trio spliced (`const-struct-artLIV-2026-06-14`) — base[1938→1964] → LXXVIII[1964-07-30] (subsec 6(d) ag-budget sentence) → XC's 2nd change[1972-10-05] (subsec 1, Ellendale removed + renumbered; text from `1973_sl/CAA.pdf` — NOT in the extraction doc, acquired this session) → XCVI[1976-12-02] (subsec 2(a) alumnus→graduate, subsec 4 compensation rewrite). art. LIV now 4 clean versions, integrity 0/0. **Independent consistency check: art. LIV v1976 vs modern art. VIII §6 = 0.89 similarity** (differences = the post-1981 student-member amendments — confirms the LIV→§6 lineage + the reconstruction). Targeted edits, each asserted unique-match + chain sanity (Ellendale present-then-absent, $7.00 present-then-absent, etc.). **Upstream TODO:** apply in `ingest_constitution_history` + add XC's art-LIV text to the extraction doc.

### 5. Point-in-time snapshot-diff harness — the capstone acceptance test, NOT yet a TODO item
The definitive test of "text in effect at moment T" is corpus-level, not per-provision: **reconstruct the entire constitution as of date T from the DB, then diff against the official compilation published near T.** Inputs already on hand: clean OCR of the **1925, 1954, and 1973** official/Blue-Book compilations (`~/refs/nd/const/...`), plus current ndconst.org.
- **Build:** for each snapshot date, assemble every provision's then-effective version, render full text, diff against that year's printed compilation. Every seam error, wrong effective date, missed amendment (#4), or coverage hole surfaces as a diff. Green diffs at 1925 / 1954 / 1973 / current = validation complete.
- This is the single strongest evidence the point-in-time claim is reliable. Scaffolding is independent (can build alongside 1/2); it runs meaningfully only after 1–4 land.

### 6. Broad audit of the ndconst.org DokuWiki against the ndlaw MCP const data  *(scoped 2026-06-26)*
A standalone wiki at **ndconst.org** renders the ND Constitution as a DokuWiki, including a point-in-time `/date/<YYYY-MM-DD>/<article>/<section>` snapshot tree (**158 snapshot dates, 1889-11-02 → 2026-04-04**) plus ~1,149 current-text pages. **The wiki entirely predates the ndlaw MCP / `constitution.db` project.** Its content was produced by a mix of **hand fixing/editing and automated generation** — so it is an *independent* rendering of the same material, not derived from our pipeline, and may hold (a) hand-made corrections our DB lacks, or (b) errors our DB has since fixed. Either direction is worth surfacing.

- **Goal:** a bidirectional reconciliation — for each provision × effective-date, diff the wiki's then-effective text against the MCP's `lookup_authority(..., as_of_date=T)` output. Divergences feed both directions: real wiki corrections become candidate DB fixes; DB-correct/wiki-wrong cases confirm the DB and (if the wiki is kept) become wiki edits.
- **Method:** the wiki snapshots are populated at the **article level** (e.g. `/date/1998-12-03/artvi` renders Art. VI with all section headings; deeper `…/sec7` permutations are empty 200-renders — see the crawl-trap note below). Pull article-level page text per (article, date), map to provisions, diff against the as-of reconstruction. The 14 official compilations in #5 are the *authoritative* arbiter when wiki and DB disagree.
- **Source preservation:** do this audit (or at least archive the `/date/` tree) **before** any deletion/regeneration of the wiki snapshots. As of 2026-06-26 the `/date/` tree is de-indexed at the web layer (`robots.txt` + an `.htaccess` `RewriteRule ^date(/|$) - [G]` 410) to stop a crawler-trap load problem, but the pages are **not** deleted; the deletion-vs-regenerate-from-MCP decision is deferred pending this audit. If deleted, the step-1 tarball (`/root/dokuwiki-date-*.tar.gz` on the ndconst host) is the source of record.
- **Relation to #5:** this is a *second external snapshot ladder* — denser in dates than the printed compilations but lower-authority (independent provenance, partly hand-edited). Run it as a cross-check alongside the #5 harness, not as a substitute for the official compilations.

---

## Recommended sequence  *(re-ranked 2026-06-14 after the census/alignment prototypes)*

1. ~~**Amendment census (#4)**~~ — PROTOTYPE DONE 2026-06-14. Remaining: the external-enumeration cross-check (confirm amendment I + series top).
2. **Modern point-in-time reconstruction (#0)** — NEW top priority; the actual load-bearing gap. Extract-and-splice from the CAA `source_url`s; ~96 provisions / ~59 amendments. Highest user-facing value (fixes 1981–present point-in-time).
3. **Structural amendments (#2)** — independent; clears 4 known holes; mechanical given captured text. Fold into #0's apply pass.
4. **Acquire NDCC Replacement Vol 13 (1981) disposition table**, then **crosswalk (#1)** — alignment auto-fills the 93 confident mappings + validates the table; the table resolves the ~98 rewritten provisions. A2 (`lineage`) schema.
5. **Amendment-event dedup (#3)** — unblocked by #1.
6. **Snapshot-diff harness (#5)** — acceptance test; green diffs = done. Snapshot ladder is richer than first scoped: **14 compilations on disk 1889–1981** (`~/refs/nd/const/processed/*.md`: 1889, 1895×2, 1899, 1905, 1907, 1913×2, 1919, 1925, 1954, 1961, 1973, 1981), not just 1925/1954/1973.
7. **DokuWiki audit (#6)** — independent cross-check; low priority and lower-authority (partly hand-edited, predates the MCP). Run alongside #5; must precede any deletion of the ndconst.org `/date/` tree.

Prototypes built 2026-06-14: `triage/const_amendment_census_2026-06-14.py`, `triage/const_crosswalk_align_2026-06-14.py` (+ their TSVs). Read-only; no DB change, no changelog entry.

Steps **1, 2, and #5 scaffolding are parallelizable**; **3 → 4** are the serial critical path. After each data change, re-run the integrity checks above and the standard build sequence (`ingest_constitution --apply` → `rm -f constitution_history.db; ingest_constitution_history --apply` → `merge_const_history.py --apply` → `make_release.sh`).

## Crux (resolve before timelining the crosswalk)

The whole effort's cost turns on **step 3's source**: does a complete, authoritative 1889→1981 **disposition table** exist in the convention/revision materials?
- **If yes:** crosswalk is mechanical; full validation is a few focused sessions.
- **If no:** crosswalk becomes a manual ~217-provision reconciliation — the real cost driver.

**First action of the next session:** confirm whether that disposition table exists in the reference materials (1972 Constitutional Convention records, 1979–80 revision materials, 1981+ Blue Books) before committing a timeline. The amendment census (#1) can run in the same session regardless.
