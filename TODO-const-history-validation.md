# Work Plan — Finish Validation of the Historical Constitution

**Goal:** a `constitution.db` that reliably returns the constitutional text in effect at **any moment in time**, from **either** citation scheme (1889 original §1–§217 or modern art./§), across the 1981 reorganization — to a standard the ND Supreme Court could adopt as authoritative.

Scoped 2026-06-13. This consolidates the const-specific items from `TODO-primarylaw.md` (PL-CONST-*) plus two validation pieces those items do not yet capture (#4, #5). The PL-CONST-* entries remain the per-item detail; this file is the sequenced plan.

---

## State of play (what is already solid — do NOT redo)

- **Text faithfulness of the 1889–1980 layer is essentially complete.** Segments 1–4 + the Blue-Book series (amend. LXV–CVIII) all reconciled against session laws / official compilations; round-2, round-3, and Blue-Book `needs_fix` buckets each have matching fix commits; the 138-variant cross-publication log was hardened against clean 1925 marker OCR. Enacted session-law text governs throughout. Artifacts: `data/const_revalidation_round{2,3}_2026-06-08.json`, `data/const_bluebook_revalidation_2026-06-08.json`, `data/const_history_judgment_calls.md`.
- **Merge into the served DB is done.** `constitution.db` = 466 provisions / 622 versions; historical layer = 421 versions spanning 1889-11-02 → 1980-12-04; cite-disjoint from the modern art./§ layer (0 collisions). Build sequence (NOT idempotent) documented in `TODO-primarylaw.md` PL-CONST-MERGE-B.
- **Within-provision timeline integrity is clean** (verified 2026-06-13): 0 provisions with timeline gaps, 0 with overlapping versions, 0 with >1 open-ended ("current") version, 0 with zero versions. The per-provision point-in-time machinery is sound. The remaining work is corpus-level, not per-provision text.

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

### 1. The 1981 reorganization seam — THE load-bearing gap  *(= PL-CONST-CROSSWALK)*
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
- **Build:** either splice the full enclosing-provision text per amendment, or subdivide art. LIV into subsection provisions; add partial-repeal modeling for LXXXI. Apply upstream in `ingest_constitution_history`, then re-run build steps 2+3.
- Independent of the crosswalk — can proceed immediately.

### 3. Amendment-event reconciliation / dedup  *(= PL-CONST-AMEND-RECONCILE)*
Same amendment now appears twice: from ndconst.org annotations (keyed to modern provisions) and from the historical session-law layer (keyed to 1889 numbering). `get_authority_history` will show two parallel chronologies per provision. Dedup so each provision shows one coherent timeline.
- **Depends on the crosswalk** (#1): can't reconcile old §82 with modern art. V §2 until they're linked.

### 4. Amendment census / completeness audit — NOT yet a TODO item
Every item above validates text we *have*. None confirms we're not **missing an amendment entirely** — the most dangerous silent error (a missed amendment = confidently-wrong text for its whole window). The segment/Blue-Book passes covered ranges piecemeal; nothing proves the union is complete and gap-free across 1889→present, including post-1981 ballot measures.
- **Build:** one reconciled master amendment table — `(number, ratification/effective date, affected old-§, affected modern art./§, present-in-DB y/n)` — covering the full official Roman-numeral series (I–CVIII+) AND every post-1981 measure. Cross-check against an authoritative enumeration (official ND Blue Book amendment list / Secretary of State measure history / ndlegis constitutional measure index).
- Cheap, no dependencies. Run **first** — tells you whether the corpus is even complete before building machinery on it. Its output doubles as the crosswalk's skeleton (#1) and the dedup key (#3).

### 5. Point-in-time snapshot-diff harness — the capstone acceptance test, NOT yet a TODO item
The definitive test of "text in effect at moment T" is corpus-level, not per-provision: **reconstruct the entire constitution as of date T from the DB, then diff against the official compilation published near T.** Inputs already on hand: clean OCR of the **1925, 1954, and 1973** official/Blue-Book compilations (`~/refs/nd/const/...`), plus current ndconst.org.
- **Build:** for each snapshot date, assemble every provision's then-effective version, render full text, diff against that year's printed compilation. Every seam error, wrong effective date, missed amendment (#4), or coverage hole surfaces as a diff. Green diffs at 1925 / 1954 / 1973 / current = validation complete.
- This is the single strongest evidence the point-in-time claim is reliable. Scaffolding is independent (can build alongside 1/2); it runs meaningfully only after 1–4 land.

---

## Recommended sequence

Dependency chain forces most of the order:

1. **Amendment census (#4)** — cheap, no deps; gates everything; output seeds #1 and #3.
2. **Structural amendments (#2)** — independent of crosswalk; clears 4 known holes; mechanical given captured text.
3. **Crosswalk (#1)** — critical path; A2 schema; sourced from 1981 disposition tables.
4. **Amendment-event dedup (#3)** — unblocked by #1.
5. **Snapshot-diff harness (#5)** — acceptance test; green diffs = done.

Steps **1, 2, and #5 scaffolding are parallelizable**; **3 → 4** are the serial critical path. After each data change, re-run the integrity checks above and the standard build sequence (`ingest_constitution --apply` → `rm -f constitution_history.db; ingest_constitution_history --apply` → `merge_const_history.py --apply` → `make_release.sh`).

## Crux (resolve before timelining the crosswalk)

The whole effort's cost turns on **step 3's source**: does a complete, authoritative 1889→1981 **disposition table** exist in the convention/revision materials?
- **If yes:** crosswalk is mechanical; full validation is a few focused sessions.
- **If no:** crosswalk becomes a manual ~217-provision reconciliation — the real cost driver.

**First action of the next session:** confirm whether that disposition table exists in the reference materials (1972 Constitutional Convention records, 1979–80 revision materials, 1981+ Blue Books) before committing a timeline. The amendment census (#1) can run in the same session regardless.
