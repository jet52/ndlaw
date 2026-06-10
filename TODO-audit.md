# TODO — Cross-Corpus Audit & Systematic-Error Checks

Project plan from the 2026-06-09 review. Two parts: (1) a snapshot index of what
remains toward "fully validated" (authoritative detail lives in the per-area TODOs —
do not let this index drift; update the source docs); (2) the audit-check catalog —
systematic-error detectors runnable in Python, prioritized cheapest-first.

## Part 1 — Path to fully validated (snapshot index, 2026-06-09)

Authoritative sources: `TODO-validation.md` (opinions), `TODO-primarylaw.md`
(const/rules/statutes/admin), `TODO-distribution.md` (release/update system).

**Opinions — substantial workstreams:**
1. §5 court-report diff residue (the court's own cTrack export as independent
   authority): (a) 1,808 case_name diffs to subcategorize; (b) ~101 >31d date holds;
   (c) ~25 author no-byline; (d) ~36 cite-mismatches; (e) 94 cite-collisions;
   (f) Nature-of-Action → case_type; (g) corpus-wide docket cross-check.
2. §2 gap-era Westlaw worklist (~400+ pool, 1953–1996 Quick Check — bound-text
   quality/syllabi; era is already ~99% two-source).
3. Priority #2/§3 cTrack PDF acquisition (court PDFs where we lack one; 1997 era
   especially). Dockets recovered → unblocked.
4. §13 constitutional-cite coverage (wire `nd_const_phrases` into `cite_extract`;
   jetcite old-form recognizers; 1889 crosswalk; phrase-table buildout).
5. §14 forward-graph remainder: (d) `antecedent_name` coverage (re-measure post
   jetcite-2.3.0 rebuild), (e) `parallel_group` for out-of-corpus parallels,
   (g) recognizer omissions, (h) garbage-volume cites.

**Opinions — closeout/small:** §10 (28 NW2d-era shared-page orders; bracketed
synthetic display in `lookup_opinion`; publish freeze); §8 (11 pre-1953 OCR
residuals; LEXIS/L.R.A. removal decision incl. A.L.R. + scope questions; pre-1997
judges-panel rebuild); §7 (1997ND5/1998ND22 markdown recovery); §1 (Hassen v. Salem
50 N.D. 825-vs-813; syllabus cutoff year); §6 (130 dup-candidate bookkeeping);
`detect_cite_swap` .doc-row refinement; **oid 12500 caption: *Longtine v. Yeado* →
*State v. Herrick*, 1997 ND 155** (confirmed live 2026-06-09 — text+cites are
Herrick; real Longtine is oid 12507). Pipeline: freshness heartbeat; scraper
letter-spacing cleanup; marker escalation; pilcrow detection at ingest.

**Primary-law DBs:**
1. PL-1(b)/(c) **footgun**: regenerate `~/refs/statute/NDCC` markdown with the fixed
   converter + commit `scrape_nd_code.py` in code-mirror — until then a statutes
   re-ingest re-corrupts the DB.
2. PL-VALIDATE validators (folded into Part 2 below; none built before 2026-06-09).
3. Constitution: PL-CONST-CROSSWALK (1889↔modern); PL-CONST-AMEND-RECONCILE;
   PL-CONST-STRUCTURAL (LXXVIII/XCVI/XC-2nd/LXXXI).
4. PL-3 table-section converter weakness (low; DB hand-corrected).

**Cross-cutting:**
- §9's "% fully validated by decade" metric — specified, never wired into
  `get_database_stats`.
- `invariants.py` covers opinions.db only; the 4 primary-law DBs have no standing
  invariant dashboard (audit.py Part 2 is the seed).
- TODO-distribution.md system (orthogonal to validation; gates public usefulness).

## Part 2 — Audit-check catalog

Sources fail in characteristic ways — CL OCR (char errors, co-party captions, date
drift, double-ingest, cite contamination), pdfminer-from-PDF (broken ToUnicode,
two-column interleave, misnamed files), Westlaw (editorial leak, shared-cite
mispairing), pdfplumber/code-mirror (dropped link-anchor lines, phantom headers,
table splits). The best cheap checks exploit internal redundancy — the corpus
witnessing itself.

Implementation home: `ndcourts_mcp/audit_corpus.py` (read-only dashboard + TSV
triage outputs, `python -m ndcourts_mcp.audit_corpus`; `audit.py` is the older
missing-opinions audit).

### Tier 1 — pure SQL/Python over existing tables

Citation graph as self-witness:
- [x] **1. Temporal sanity** (`cite_temporal`) — citing.date_filed ≥ cited.date_filed
  for every `cited_by` edge (same-day OK: companions). A wrong date on a much-cited
  case violates many edges at once. *Built 2026-06-09.*
- [ ] **2. Antecedent-name witness** — `text_citations.antecedent_name` (the citing
  court's own naming) vs our `case_name` on the resolved oid (surname containment).
  Catches CL co-party mistitles using the court as authority. Coverage grows with
  §14(d).
- [x] **3. Pinpoint-range** (`pinpoint_range`) — a cite to `YYYY ND n, ¶ P` where our
  copy of that opinion has max ¶ < P ⇒ truncation (or pincite garble). The cheapest
  silent-truncation detector. *Built 2026-06-09.*
- [x] **4. Cross-corpus resolver** (`xref_resolve`) — every NDCC/NDAC/rule/const cite
  in `text_citations` resolves to a provision in the matching corpus DB (via
  `corpus.cite_key`); bucketed by opinion era (old opinions legitimately cite
  repealed/renumbered law). Two corpora witness each other. *Built 2026-06-09.*

Text integrity:
- [x] **5. ¶-marker continuity** (`para_continuity`) — `[¶1]..[¶N]` strictly
  ascending, no gaps/dups/restarts, per modern opinion. Gap = dropped paragraph.
  *Built 2026-06-09.* **GAP classification WORKED 2026-06-09**
  (`triage/para-gap-classified-2026-06-09.tsv`): 341 CORRUPT_TOKEN → **287
  markers fixed** (`para-marker-ocr-variants-2026-06-09`). GAPs 1,206→1,056.
  **Remaining queues (measured):**
  - **TEXT_MISSING — WORKED 2026-06-10** (`text-missing-measured-2026-06-09.tsv`):
    **473 signature-only spliced** (`sig-splice-2026-06-09`; 15 stale) +
    **219 substantive spliced** (`substantive-missing-2026-06-09`; 7 held —
    5 stale, Wodrich 12605 known-correct, **Helbling 17357 page-rotated PDF
    missing ¶22–32, queued per-item**). Digit-flip exposure for the cohort
    audited: 5,014 ¶s compared, **70 flips fixed PDF-print-verified**
    (`digit-flips-pdfverified-2026-06-09`; crops in `triage/flipverify/`;
    2 PDF text-layer ToUnicode rejections; 2 court typos preserved+baselined).
    `para_continuity` 1,086→521. Remaining: 74 PDF-lacks-marker rows
    (per-item) + 14 opinions with no PDF. **Helbling 17357 RESOLVED 2026-06-10
    as a false positive** — the "missing ¶22–32" are the divorce settlement
    agreement's own numbered paragraphs quoted verbatim (opinion is ¶1–21
    complete); baselined with Wodrich/Carlsen/Simpson in
    `audit_corpus._KNOWN_QUOTED_DOC_MARKERS`.
  - **106 NO_MARKER_TEXT**: 5 fixed by PDF-opener matching
    (`para-marker-restore-2026-06-09`); the rest defeat exact matching via
    OCR drift/footnote structure — needs fuzzy alignment; ALSO includes an
    almost-clean-marker variant (`[.¶ 23]`) the classifier misjudged as clean —
    extend the variant fixer.
  - NONMONO-only flags include the legitimate embedded-quoted-order class
    (20124/20408 — the court's own PDFs print restarting sequences).
- [ ] **6. Body-duplication detector** — repeated long substring / shingle
  self-similarity within one text_content (the 13240 stored-twice class; guards
  merge concatenation).
- [ ] **7. Truncation heuristics** — body ends w/o terminal punctuation or signature
  block; short body vs PDF page count.
- [ ] **8. Char-histogram regression scan, all 5 DBs** — non-ASCII inventory per
  corpus; alarm on new entrants (statutes/rules/admin/const never had one).
- [ ] **9. Two-column interleave detector** — Neset-style mis-extraction (another
  opinion's caption/docket mid-body; coherence breaks). Owed from §3 re-audit.

Metadata cross-field consistency:
- [ ] **10. Reporter-volume↔date window invariant** — derive each N.W./N.W.2d/N.W.3d
  volume's window from corpus medians; flag >60d outliers. Plus: neutral-cite year ==
  year(date_filed); docket YYYYNNNN prefix vs filing year; synthetic ordering
  monotonic vs (date, page). *Partially exists as `volume_date_check` — extend.*
- [ ] **11. Roster fuzzy-match** — author/judges within edit distance 1–2 of a known
  justice but not equal = probable OCR typo (per the surrogate-judges rule: hunt
  near-miss names, don't tenure-validate).
- [ ] **12. case_name lint** — digits, unbalanced parens/quotes, double spaces,
  trailing connectors, residual ALL-CAPS, artifact chars.
- [ ] **13. Frontmatter-vs-citations sync** — measure the known cosmetic lag.

Primary-law structural (ex-PL-VALIDATE):
- [x] **14. provision_versions interval integrity** (`version_intervals`) — start<end;
  no overlaps per provision; ≤1 open version; `current_version_id` points at it.
  *Built 2026-06-09.* **Queue WORKED 2026-06-10, 11→0**
  (`rules-version-surgery-2026-06-10`): zero-widths were foreign pages filed as
  rule versions (appendix-k/f/8.9-appendix/Table A/Rule 8.3.1 + Admin Rule 21
  dups inside Admin Order 21), same-date republication twins, and
  renumber/repeal pages carrying the successor's date (4.1 was serving repealed
  text as current). 5 provisions created, 7 relocated, 9 deleted; verified vs
  live ndcourts.gov H1 titles + effective dates.
- [ ] **14b. Rules-ingest hardening (from the surgery's root causes):**
  (a) H1-title-vs-provision guard — a version page whose H1 names a different
  instrument must not join the rule's timeline; (b) ingest the N.D.R.Ct.
  appendices missing as provisions entirely (**c, d, e, l, m** per the live
  index; a–m exist there, DB had only a/b/g/i/j); (c) same-date republication
  twins need a dedup rule (keep current-slug page); (d) repealed rules: page
  title `[REPEALED ...]` → provision.status='repealed' + repeal-notice version.
- [ ] **15. Enumeration continuity** — subsection 1,2,3…/subdivision a,b,c… gaps
  (dropped enumerated blocks read grammatically); syllabus-point numbering in
  pre-1953 opinions.
- [ ] **16. Doubled-token + seam detectors as standing scans** (PL-1/PL-2 triage
  tools re-run after any re-ingest; baseline 41 source/FP).
- [ ] **17. Heading/body split sanity** — headings ending mid-abbreviation, bodies
  starting lowercase.
- [ ] **18. Section-number sequence within chapters** — gaps must correspond to
  repealed/reserved dispositions.

Process integrity:
- [x] **19. Changelog reconciliation** (`changelog_doc_sync`) — every DB changelog
  batch has a CHANGELOG-data*.md mention (caught `altenbrun-date-fix` missing by
  hand 2026-06-09); referenced snapshot files exist. *Built 2026-06-09.*
- [ ] **20. FTS sync check, all 5 DBs** — rowcount + random-sample equality between
  FTS index and base tables.

### Tier 2 — external fetch required (still scriptable)

- [ ] **21. Section-inventory cross-check** vs ndlegis.gov indexes / PDF bookmarks —
  the only check that catches whole missing sections.
- [ ] **22. Second-engine extraction diff** (PyMuPDF vs pdfplumber per section) —
  certifies faithfulness to the PDF, not within-engine consistency.
- [ ] **23. Upstream-correction watch** — re-hash sampled live ndcourts.gov PDFs vs
  stored; watch the index for corrected/substitute labels. Nothing currently
  detects an upstream correction post-ingest.
- [ ] **24. CL metadata re-diff** by cluster_id (our drift + CL's corrections).
- [ ] **25. Per-year count time series** vs the court's published annual statistics.
- [ ] **26. Statute currency heartbeat** — flag when a new session's effective dates
  arrive with no re-ingest.

### Follow-up queues from the 2026-06-09 pinpoint work

- [x] **Parallel-pair scan promoted to permanent check — DONE 2026-06-09**
  (`audit_corpus.check_parallel_pair`; court typos baselined in
  `_KNOWN_COURT_PAIRS`). Reads 608 = exactly the enumerated held queues
  (singles/conflicts/window + unverified sibling clusters + OTHER); shrink it
  by working those, alarm on growth.
- [ ] **~25 mixed/single-witness parallel clusters** (`triage/class3-clusters-2026-06-09.tsv`)
  — per-item verification vs CL/Westlaw before any move/add. Includes the
  `622 N.W.2d 432` three-claimant tangle (Lee 2000 ND 215 header / Matrix
  2000 ND 213 witnesses ×6 / Syvertson 2000 ND 211 current holder) and
  Chinquist/Jaste sharing `679 N.W.2d 257` (Boedecker/McMahon-style shared
  page vs contamination). Mirror-image clusters where the holder dominates
  (Laib 6/1, Ceynar 5/1, Noack 43/1) are single court typos — no DB change.
- [x] **`DB_NO_PARALLEL` backfill — WORKED 2026-06-09** (`parallel-backfill-witnessed-2026-06-09`):
  **387 parallels added** (246 window-gated + 141 interpolation-gated for absent
  volumes; garbage `003 N.W.3d 122` correctly rejected). Pair consistency
  2,455→610 mismatches (98.9%). **Residue queued** in
  `triage/backfill-parallel-candidates-2026-06-09.tsv`: 125 single-witness
  (need CL/Westlaw — a lone witness may itself carry a digit flip), 24
  WINDOW:OUT, 20 CONFLICT.
- [ ] **242 `OTHER` mismatch rows** (`triage/parallel-pair-classified-2026-06-09.tsv`)
  — sample & classify (regex artifacts vs deeper tangles vs >1-digit corruption).
- [ ] **199 cite-shaped `docket_number` values** (`YYYYNDn` in the docket field;
  159 from 1997 — found via the 12500 Herrick fix 2026-06-09). The #1 docket
  recovery closed *empty* dockets; these are *wrong* ones. Recover from the
  frontmatter/body `Criminal/Civil NNNNNN` lines like `recover-dockets-2026-05-27`.
- [x] **Stored-twice opinions — WORKED 2026-06-09** (`dedup-storedtwice-2026-06-09`):
  the 31 marker-flagged seeds led to a corpus sweep finding **563**; **549 fixed**
  (4-gate surgery incl. jaccard≥0.5 so appended rehearings can't be deleted).
  para_continuity 1,818→1,269. **All 41 holds RESOLVED same day** (see CHANGELOG
  held-queue closeout): 27 flip-explained drops; archive-arbitered marker
  fixes/splices (incl. Clayburgh's missing ¶37 signature, Lawrence archive
  rebuild); Fisk page-rotation re-extract; 2 false positives (court PDFs print
  the restart — embedded quoted orders). **Self-audit caught 8 dropped
  `## On Rehearing` blocks → restored** (`rehearing-restitch-2026-06-09`);
  the rehearing-below-max gate hole is why future dedups must scan dropped
  text for rehearing/amendment keywords. Final: para_continuity 1,240,
  xref 811, parallel_pair 595, invariants 23/2/0.
  **Check #6 still owed for pre-1997** — the sweep keys on [¶N]/## Opinion;
  markerless old texts need shingle self-similarity. (Also note 20124/20408:
  embedded quoted orders with own ¶ numbering are a legitimate NONMONO class.)
- [x] **Digit-flip exposure beyond citations — CLOSED corpus-wide 2026-06-10**
  (`digit-flips-corpus-2026-06-10`; method proven on the 226-cohort first,
  `digit-flips-pdfverified-2026-06-09`). Full analyzer era: 6,965 opinions /
  129,160 ¶s digit-compared vs PDFs → 621 candidates → all print-verified
  (21-agent crop fan-out + 10% personal spot-check 57/57 + personal read of all
  38 unclears). **618 fixes in 499 opinions; 3 text-layer ToUnicode rejects
  (never apply from the text layer alone); 4 more court typos baselined.**
  Residue: `triage/digit-flip-followup-2026-06-10.tsv` (5 adjacent multi-digit
  divergences the single-flip pairing can't propose — extend pass-2 to
  2-digit/length-change diffs for a final small sweep); 130 opinions have no
  PDF (pre-scraper 1997–98 era — Westlaw cross-check is their only witness);
  17 newly-visible cited-side parallel issues joined the parallel_pair queue.

### Build order

Done 2026-06-09: 1, 3, 4, 5, 14, 19 (the top-tier set). Next by yield-per-effort:
2 (antecedent witness — pairs with the §14(d) re-measure), 10 (volume-window
invariant), 6+7 (duplication/truncation), 8 (char histogram, primary-law DBs),
20 (FTS sync). Tier 2 as sessions allow; 23 belongs in the weekly pipeline.

### First-run baseline (2026-06-09, TSVs in `triage/audit-*-2026-06-09.tsv`)

| Check | Flagged | Read |
|---|---|---|
| cite_temporal | **0** | graph temporally clean after today's rebuild |
| pinpoint_range | **0** (was 59) | WORKED 2026-06-09: root cause = **OCR digit flips (3↔8, 5↔6) in analyzer-era texts** — invisible to artifact-char cleanup. 310 cite/pincite corrections (PDF-verified) + 1 re-extract (2011 ND 242 markers) + 14 witness-attested parallel additions + 3 court typos preserved (one baselined in `_KNOWN_COURT_PINCITES`). See CHANGELOG `citeflip-surgical-*-2026-06-09`. |
| para_continuity | **1,876** (1,297 GAP) | spot-check Ertelt 1997 ND 15: ¶2 text present but marker OCR'd `[IF 2]` → pinpoint-navigation defect, not lost text; only ~25 carry the literal `[IF/lf N]` signature — classify the rest by source/gap-shape before bulk action |
| xref_resolve | **848** modern-citer unresolved (2,328 total distinct) | three classes: (a) repealed/recodified law (ch. 27-20 juvenile) — statutes.db is a current snapshot, suggests a repealed-section disposition layer; (b) genuine rules.db gap: N.D. Stds. Imposing Lawyer Sanctions (88 modern citers); (c) cross-tag oddities (`N.D.C.C. ch. 75-02` = NDAC-shaped number) |
| version_intervals | **11** | zero-length rule versions (start==end) in rules.db — ingest artifact |
| changelog_doc_sync | **0** (was 110) | the 7 June batches got narratives same day (incl. the `nd-consolidate-nestos`→`-state` doc/DB name fix); the 103 pre-policy/narrated-elsewhere batches are grandfathered in `_KNOWN_UNNARRATED`(`_RE`) — shrink that list as narratives are backfilled, never grow it unchecked |
