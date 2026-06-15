# HANDOFF — orphan tails, then live promotion (for a fresh session)

Written 2026-06-15. Two tasks, in order: **(1) finish the orphan tails** of the modern
constitution point-in-time layer, then **(2) promote the modern layer to live.**

Read this fully before acting. Deep background: `triage/const-modern-batch/HANDOFF.md` (the
canonical campaign handoff). Other key docs: `NEEDS-BASE-SOURCE-PLAN.md`, `ARTIV-CROSSWALK-PLAN.md`,
`CHANGELOG-data-primarylaw.md` (every batch logged), memory `project_const_modern_pointintime.md`.

---

## 0. Where things stand (2026-06-15)

The ND Constitution `constitution.db` has a **historical layer (1889–1980, LIVE/validated)** and
a **modern layer (1981–present)**. The modern layer was a flat one-version-per-provision snapshot;
this campaign reconstructed its point-in-time depth. **All substantive modern reconstruction is
DONE** — single-amendment splices, multi-amendment chains, the art IV (1986) and art V (1997)
renumbering crosswalks, art XIII §1, art VIII §6, second-read pass, and the needs-base-source
bucket (Group A + B). **182 multi-version provisions, 711 versions, integrity 0 gaps, quick_check ok.**

**Two databases (critical):**
- **LIVE: `constitution.db`** (repo root, gitignored build artifact). Still has the FLAT modern
  layer — **none of the reconstructions are live yet.** It has the historical layer + the
  amendment-chronology/text corrections only.
- **SCRATCH: `/tmp/const-scratch.db`** — the working copy with ALL reconstructions. **⚠ /tmp is
  ephemeral.** If gone, rebuild with: `bash scripts/rebuild_const_modern.sh` (it copies
  `constitution.db`→scratch, replays every committed splice script in order, and asserts the
  rebuilt content-signature == the validated scratch; last good sig `55b6b2f2e77a1b0f`, 711
  versions). It does NOT re-fetch ndconst.org and does NOT write constitution.db. Use `.venv/bin/python`.

**Reproducibility is PROVEN** — `scripts/rebuild_const_modern.sh` regenerates the entire layer
from the base DB. This is the promotion mechanism (see Task 2).

**Decision already made (user):** hold live promotion until the layer is complete; local build +
verify only until then. The user has now authorized: finish orphans → then proceed to live.

---

## 1. TASK 1 — Orphan tails

### 1a. What an "orphan tail" is
Three modern articles were **repealed-and-recreated**, REUSING section numbers for new content:
art IV (eff 1986-12-01), art V (eff 1997-07-01), and art VII (the 1982/83 home-rule recreation).
We reconstructed the [1981, recreation) prior text for the citations that survive into the current
scheme (the crosswalks). What's LEFT are the "tails":
- **(A) citation [1981,start) gaps** — current citations whose [1981, recreation) window is still
  uncovered because the old section there was a judicially-void stub or because the article's whole
  pre-recreation state wasn't reconstructed.
- **(B) dropped-section orphans** — old sections that had NO post-recreation citation at all (so no
  current provision exists for them); they need new [1981, recreation)-only provisions.

### 1b. The inventory (verified 2026-06-15)
**IMPORTANT — first re-run the systematic sweep** to confirm nothing has shifted:
```
.venv/bin/python - <<'PY'
import sqlite3,re
from collections import defaultdict
con=sqlite3.connect('/tmp/const-scratch.db')
rows=con.execute("""SELECT p.citation, MIN(pv.effective_start) e FROM provisions p
 JOIN provision_versions pv ON pv.provision_id=p.id WHERE p.corpus='const'
 AND p.citation LIKE 'N.D. Const. art. %§%' AND p.citation NOT LIKE '%amend%'
 GROUP BY p.id HAVING e>'1981-01-01' ORDER BY e""").fetchall()
for c,e in rows: print(e,c)
PY
```
Of the 42 provisions that start after 1981, **most are GENUINELY NEW** (created after 1981 — correct
as-is, NOT orphans): art X §§22-27, art XI §§27-29, art XIII §4, art I §25, art II §3, and the whole
of art XIV (2019), art XV (2023), art XVI (2024). **Leave those alone.**

The actual tail work:

**(A) [1981,1986) gaps in art IV — stubs §2, §5, §11.** These three still start 1986-12-01. In the
1981 Blue Book the pre-1986 old §2/§5/§11 are printed "[Unconstitutional.]" (judicially void —
the 1960s reapportionment cases — but not textually repealed until the 1986 recreation). DECISION
NEEDED (see 1d). Whatever the representation, prepend a `[1981-01-01, 1986-11-30]` version so the
window is covered. (The other 13 art IV §§ already have their [1981,1986) prepend, batch
`modern-artiv-crosswalk-1981-1986-2026-06-15`.)

**(B) dropped-section orphans:**
- **art IV §§ 17, 18, 20–46** — repealed by the 1986 recreation (old §19→§11; §46 repealed earlier,
  1982; §26 didn't exist at 1981). No modern citation. Create `art IV § N` provisions valid
  `[1981-01-01, 1986-11-30]` only, status repealed/superseded. Text source: the **1981 Blue Book**
  (the legislative article ran §§1-46; L142–L293 of `1981_blue-book_constitution.md`) + the
  **historical layer** for clean text (the art IV §N→1889 §M crosswalk is in `ARTIV-CROSSWALK-PLAN.md`;
  e.g. §17→1889 §39, §20→§42, §21→§43, … and §27-45 map to 1889 §§48-70-ish). Many old §§ map to a
  historical §M whose 1980-state text is clean & validated — same technique as
  `splice_artiv_crosswalk_1981.py`.
- **art V § 13** — pre-1997 executive-officers powers/duties section; no post-1997 §13. Create
  `art V § 13` valid `[1981-01-01, 1997-06-30]`. Source: the marker 1989 BB (see §3) executive
  article had a §13; also historical §83 (`The powers and duties of the secretary of state, auditor…`).

**(C) art VII (1982 home-rule recreation) — INVESTIGATE FIRST.** art VII §§1-11 all start 1982-07-08.
At 1981 the citation "art VII §N" currently returns nothing. Determine from the 1981 BB whether a
DIFFERENT old art VII existed in the [1981,1982) reorg-scheme window:
  - If old art VII existed [1981,1982): it's a reorganization like art IV/V → prepend old content
    to §1-11 (crosswalk) and/or create dropped orphans. (Also check **art XI §26** @1982-07-08,
    the legislative-compensation section former art IV §46 → art XI §26 — same 1982 window.)
  - If art VII genuinely did not exist until 1982 (no predecessor at that citation): then nothing is
    the correct [1981,1982) answer and there is NO work — document and move on.
  Check the 1981 BB article order (it had art IV legislative §§1-46, art V executive, art VI judicial,
  then …). RESULTS-wave2.md classified art VII §1-11 as CREATE (home rule) — consistent with "old
  art VII repealed" — but the [1981,1982) predecessor was never examined. Resolve it.

### 1c. Method (mirror the existing splicers)
For each orphan, write a small gated splicer in `triage/const-modern-batch/` following the pattern
of `splice_artiv_crosswalk_1981.py` / `splice_artv_pre1997.py`:
- For a DROPPED orphan with no provision: `INSERT INTO provisions` (corpus='const', citation, cite_key,
  hierarchy, heading, status='repealed', current_version_id) then one `provision_versions` row
  `[1981-01-01, <recreation-1day>]`. Look at how historical/merged provisions set those columns
  (`PRAGMA table_info(provisions)`; copy a sibling's hierarchy/cite_key style).
- For a [1981,gap) prepend on an existing provision: same as the crosswalk splicers.
- **Source clean text from the validated historical layer** via the §N→1889 §M crosswalk where it
  carries verbatim (1981 BB is the numbering witness, often OCR-garbled; the historical layer +
  the marker 1989 BB are cleaner). Gate each: despaced witness match ≥0.95/containment; integrity 0.
- Batch-scope every change (`batch='modern-orphans-<date>'`) and log to `changelog` (see any splicer).
- After each splicer, ADD it to `scripts/rebuild_const_modern.sh` (so the build stays reproducible)
  and re-run the orchestrator to confirm REPRODUCIBLE YES + integrity 0.

### 1d. The "[Unconstitutional.]" stub decision (art IV §2/5/11) — RAISE WITH USER
These were held unconstitutional by the courts but remained textually in the constitution until 1986.
Options: (i) store the marker "[Unconstitutional.]" as the BB printed it; (ii) store the original
section text with a status/heading note that it was judicially void; (iii) leave §2/5/11 uncovered for
[1981,1986) and document why. This is a judicial-representation judgment — **ask the user** before
choosing. (Same question would apply to any other "[Unconstitutional.]" entries found in the sweep.)

### 1e. Verification (per orphan + at the end)
- Integrity 0 gaps; `quick_check ok`.
- Point-in-time spot-checks across each boundary (e.g. `art IV §40 as of 1983` returns the old text;
  `as of 1990` returns nothing/repealed).
- Run `snapshot_diff_modern.py` — the new [1981,1986)/[1981,1997) versions should match the 1981 BB
  / marker witnesses where parseable.
- Build reproducibility: `bash scripts/rebuild_const_modern.sh` → REPRODUCIBLE YES.
- Commit each batch (scratch-only) with a changelog entry, like every prior batch.

---

## 2. TASK 2 — Live promotion (after orphans are complete & verified)

Goal: make the reconstructed modern point-in-time layer LIVE (served by the MCP server and shipped
in the public release). Doctrine: **never hand-edit live; rebuild reproducibly.**

### 2a. Pre-flight gates (all must hold)
- Every reconstructed/orphan provision has a witness or confirming read (§1.e; the second-read pass
  is done for the original 44 — re-confirm any new orphan splices).
- `snapshot_diff_modern.py` is green: 1989 ≈ 96% match-or-near (the residual VI§12/X§5 are pre-existing
  OCR/formatting, not data errors — confirm they're still just those); 1981 MISMATCH 0.
- Integrity 0 gaps, `quick_check ok` on scratch.
- `scripts/rebuild_const_modern.sh` → **REPRODUCIBLE YES** (this is the proof the layer regenerates
  from committed scripts — the prerequisite for a clean rebuild).

### 2b. The promotion mechanism (decide, then execute)
The reconstructions live in committed splice scripts; `rebuild_const_modern.sh` replays them onto a
copy of the base `constitution.db` WITHOUT re-fetching ndconst.org. Two ways to make them live:
- **RECOMMENDED (simplest, proven):** run `rebuild_const_modern.sh` against the current
  `constitution.db`, confirm REPRODUCIBLE YES, then **back up and promote**: `cp constitution.db
  constitution.db.bak-pre-promote-2026-06-XX && cp /tmp/const-scratch.db constitution.db`. The
  reconstructions are reproducible from the committed scripts, so this satisfies "rebuild, not
  hand-edit." (Do NOT re-run `ingest_constitution` first unless you intend to re-fetch ndconst.org —
  that risks source drift; the current base is already validated. If you DO re-fetch, expect the
  base text to possibly change and re-verify everything.)
- **OPTIONAL hardening (declarative snapshot):** snapshot the reconstruction layer to
  `data/const_modern_versions.json` + an idempotent applier (mirroring
  `data/const_modern_text_corrections.json` + `scripts/apply_modern_text_corrections.py`), and fold
  it into the official build. More robust to future base drift; defer unless the user wants it. The
  splice scripts remain the provenance either way.

### 2c. Verify the promoted constitution.db (local, before anything outward-facing)
- `quick_check ok`; integrity 0 gaps; version/provision counts match scratch.
- Point-in-time via the ACTUAL MCP path: `mcp__ndcourts__lookup_authority` with `as_of_date` for a
  few reconstructed provisions (e.g. art XII §7 as of 2000 = poll-tax-era text vs as of 2010 =
  Repealed; art IV §14 as of 1983 = bribery vs 1990 = sessions-open; art VIII §6 across its 4 versions).
- Confirm modern current-text queries are unchanged (no regression to the served current text).

### 2d. OUTWARD-FACING steps — CONFIRM WITH THE USER before each
These publish/deploy and are hard to reverse. Per standing instructions, **confirm before doing them**
even though the user authorized "proceed to live":
1. **Public GitHub release** — `scripts/make_release.sh` then `--publish`. It bakes pre-release gates
   (invariants, redistribution-scope scan, clean git tree, quick_check + row floor for every shipped
   DB: opinions/constitution/rules/statutes/admincode). Requires a version bump in `pyproject.toml`.
   Constitution text is public-domain primary law (no copyright concern), but run the gates. The
   release ships `constitution.db.zip` (the public download).
2. **Live MCP server deploy** — host `ndconst`, `/srv/ndcourts`; run `update-db.sh` as root (memory
   `project_server_deploy_ops`: invariants warn benignly with no refs tree, sqlite3 CLI required).
Present the local-verify results and get explicit go-ahead for (1) and (2) separately.

### 2e. Build sequence reference (full rebuild incl. history — NOT idempotent for history)
`ingest_constitution --apply` (re-fetch — usually SKIP, see 2b) → `rm constitution_history.db;
ingest_constitution_history --apply` → `merge_const_history --apply` → `rebuild_const_modern.sh` (or
the JSON applier) → `make_release.sh`.

---

## 3. Key files & facts
- **Orchestrator:** `scripts/rebuild_const_modern.sh` (the reproducible rebuild; lists every splice
  script in order). Splicers: `triage/const-modern-batch/splice_*.py`, `fix_*.py`,
  `reconstruct_ix_stale.py`; `scripts/{fix_amend167_legacyfund_2024,apply_modern_text_corrections}.py`.
- **Validation:** `triage/const-modern-batch/snapshot_diff_modern.py` (COMPS: 1981 BB + the
  marker-1989 BB). `second_read_check.py`.
- **Witnesses (refs data tree, not in repo):** `~/refs/nd/const/processed/` —
  `1989_blue-book-marker_constitution.md` (the reliable 1989 witness; marker OCR re-extraction,
  complete & clean), `1981_blue-book_constitution.md` (microfilm, OCR-garbled but has art IV §§1-46),
  `1925_official_constitution.md`, etc. Regenerate marker: `~/.local/bin/marker_single
  ~/refs/nd/const/raw/1989_blue-book_ndbb-6361.pdf --page_range "66-97" --disable_image_extraction
  --output_dir <dir>` (0-indexed; PDF pages 67-98 = the constitution). marker beats the direct text
  layer (which has letter-spacing on some pages and dropped art XIII §1's page-97 tail).
- **Redline source PDFs** (AcroForm + text layer; render `mutool draw -r 450`): `~/refs/nd/sess/<year>_sl/`.
- **Ingest/build:** `ndcourts_mcp/ingest_constitution.py` (modern + correction overlays),
  `ingest_constitution_history.py` (1889 layer), `scripts/merge_const_history.py`, `scripts/make_release.sh`.
- **Doctrine/gotchas:** §9 of `HANDOFF.md` (mutool not pdftotext for AcroForms; resolve PDFs by exact
  source_url filename; "#1 read error = keeping an ADDED span"; preserve source verbatim; FTS is
  external-content — delete via the 'delete' command, not DELETE FROM; modern witnesses govern the
  modern-era version over older compilations).
- **Per-task verification is non-negotiable** (main context gates every subagent result — this caught
  the 1989-BB truncation trap and an art IX §7 bad reversal this campaign).

## 4. Commit/workflow
Campaign commits directly to `main` (the user's repo; established pattern, ~20 commits this campaign).
Commit each batch with a changelog entry. Scratch-only until the promotion step. Commit message
trailer: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
