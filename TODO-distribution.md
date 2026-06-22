# TODO — Database Distribution & Update System

> **⚠️ SUPERSEDED (audited 2026-06-22).** This entire base+patch+`meta`+auto-updater
> plan was never built and has been replaced by a simpler **full-DB-zip-per-release**
> model that is live and shipping: `scripts/make_release.sh` builds each `gh release`
> with `opinions.db.zip` + `.sha256` (gated on invariants, redistribution-scope,
> git-clean, quick_check, row-floor), and the live server pulls it via
> `deploy/update-db.sh` (sha256 verify, quick_check, atomic swap + `.bak` rollback +
> health probe). 16 releases shipped (v0.1.0→v1.0.1). None of the items below exist
> (no `ndcourts_mcp/release/`, no `updater.py`, no `meta` table, no manifest, no
> Actions workflow, no `update` CLI), and the ~800 MB patch-delta motivation is moot
> (the zip ships full each time). **Action: retire or rewrite this file to the shipped
> model; do not treat the checklist below as live work** — it's kept only as a record
> of the abandoned design.

How to ship `opinions.db` (~800 MB, growing) to end users and keep it current with monthly updates. Build after data validation work stabilizes (TODO-validation.md §5 in particular — scraper fix and new-opinions pipeline).

## Design decision

**Annual base + monthly SQL patches**, distributed via GitHub Releases. Not Git LFS (bandwidth quota), not full-DB-per-month (workflow friction on MCP startup).

- **Base release** (e.g., `v2026-base`): full `opinions.db.zst` asset, ~200–250 MB compressed. Cut annually, or mid-year on destructive schema change / long patch chain.
- **Patch release** (e.g., `v2026.04`): tiny `patch.sql.gz` asset (<1 MB expected) plus a `manifest.json`. One release per calendar month, or skipped months if no new opinions and no corrections.
- **Preconditions enforced**: a patch declares the schema_version and data_version it expects; updater refuses to apply across mismatches and falls back to full base download.

FTS5 is external-content with triggers on `opinions` (ndcourts_mcp/db.py:201–216), so patches that INSERT/UPDATE rows in `opinions` maintain the FTS index automatically. No custom FTS sync in the patch format.

## Schema additions

New `meta` table (key/value, one row per key):

| key | type | meaning |
|-----|------|---------|
| `schema_version` | int | bumped on any DDL change; forces rebase |
| `data_version` | text | e.g. `2026.04`; bumped by every applied patch |
| `base_version` | text | which base this DB descends from, e.g. `2026-base` |
| `last_patch_sha256` | text | hash of the last successfully applied patch |

Bootstrap: add `meta` during the next ingest cycle with `schema_version=1`, `data_version` derived from today's date, and `base_version=bootstrap`.

## Patch format

Gzipped SQL file, fully self-contained (no client-side re-run of `cite_extract` / `quality_scan`):

```sql
-- patch 2026.04
-- requires schema_version=1, data_version=2026.03
BEGIN;

-- Precondition check (fails the whole txn if not met)
SELECT CASE WHEN
    (SELECT value FROM meta WHERE key='schema_version') = '1'
    AND (SELECT value FROM meta WHERE key='data_version') = '2026.03'
  THEN 1 ELSE RAISE(ABORT, 'patch precondition not met') END;

-- New opinions (triggers maintain opinions_fts automatically)
INSERT INTO opinions (id, case_name, date_filed, ...) VALUES (...), (...);
INSERT INTO citations (...) VALUES (...);
INSERT INTO opinion_sources (...) VALUES (...);

-- Derived data for new opinions (pre-computed at release time)
INSERT INTO text_citations (...) VALUES (...);
INSERT INTO cited_by (...) VALUES (...);
INSERT INTO quality_scores (...) VALUES (...);

-- Corrections (replayed from changelog table of the release-building DB)
UPDATE opinions SET case_name='...' WHERE id=...;
INSERT INTO changelog (...) VALUES (...);  -- preserve audit trail

-- Version bump
UPDATE meta SET value='2026.04' WHERE key='data_version';
UPDATE meta SET value='<sha256 of this file>' WHERE key='last_patch_sha256';

COMMIT;
```

Rationale: monthly volume is ~10–40 new opinions + a handful of corrections. A self-contained patch with all derived data is still tiny and spares users from running `cite_extract` (multiprocessing, slow). The `changelog` table remains the audit of record.

## Manifest format

`manifest.json`, attached to each patch release and to each base release:

```json
{
  "kind": "patch",
  "base_version": "2026-base",
  "prior_data_version": "2026.03",
  "data_version": "2026.04",
  "schema_version": 1,
  "patch_url": "https://github.com/.../releases/download/v2026.04/patch.sql.gz",
  "patch_sha256": "abc...",
  "result_sha256": "def...",
  "published_at": "2026-04-01T00:00:00Z"
}
```

For base releases, `kind: "base"`, no `prior_data_version`, and `db_url` / `db_sha256` instead of `patch_*`.

## Components to build

### 1. Release-build pipeline (maintainer side)

- [ ] `ndcourts_mcp/release/build_base.py` — compresses the current `opinions.db` with zstd, computes sha256, writes `manifest.json`, invokes `gh release create`. Run annually or when a rebase is needed.
- [ ] `ndcourts_mcp/release/build_patch.py` — given a prior release tag: clone the DB from that release into a scratch dir, diff against current DB row-by-row for the tables that matter (`opinions`, `citations`, `opinion_sources`, `text_citations`, `cited_by`, `quality_scores`, `changelog`), emit a SQL patch, verify by applying it to the prior DB and comparing the result hash to the current DB.
- [ ] Add a `verify` step that applies the patch to a copy of the previous release's DB in /tmp and confirms the result hash matches the running DB. Never publish a patch whose verification fails.
- [ ] GitHub Actions workflow (or a local `make release-patch` / `make release-base`) to automate the above.

Patch generator tradeoff: diffing full tables is simpler but slower than tailing the `changelog` table. Start with the changelog-tail approach — it already captures every edit that matters for patches; reserve full-table diff as a fallback/verification strategy.

### 2. Client-side updater

- [ ] `ndcourts_mcp/updater.py` with:
  - `check()` — fetch latest manifest from GitHub Releases API, compare to local `meta.data_version`, return what's needed (nothing / chain of patches / full base).
  - `apply_patches(manifests)` — download, verify sha256, apply in order inside a single transaction per patch, verify `result_sha256` after each.
  - `fetch_base(manifest)` — download full DB, verify sha256, atomically swap in (rename old to `.bak`, rename new to `opinions.db`, delete `.bak` on success).
  - Network failures, partial writes, mid-apply crashes all leave a recoverable state (use a temp file + rename; never edit the live DB file in place during a base swap).
- [ ] `ndcourts-mcp update` CLI entry point in `pyproject.toml` scripts.
- [ ] On-startup check, 24h stamp-file throttled, runs in a detached subprocess so MCP server startup stays instant. Skip if `NDCOURTS_NO_AUTO_UPDATE=1`.
- [ ] Log update activity to `~/.local/state/ndcourts-mcp/update.log` (or platform equivalent) for debuggability.

### 3. Install UX

- [ ] First-run: `pip install` → user runs `ndcourts-mcp update` → downloads latest base + any patches newer than it. No need to ship any DB in the Python package itself (keep the wheel small).
- [ ] Document in README: "After install, run `ndcourts-mcp update` once. The server auto-checks for updates daily thereafter."
- [ ] Optional: pin `NDCOURTS_DB_PATH` env var so the user can relocate the DB off the install dir.

### 4. Edge cases

- [ ] Schema-change patches: if `schema_version` bumps, patch must include `ALTER TABLE` DDL. Run before the data INSERTs. Update `meta.schema_version` as part of the same transaction.
- [ ] Stale chain: if user is >6 patches behind, fetch the latest base instead of the patch chain. Cheaper and removes patch-replay risk.
- [ ] User has made local edits to the DB: updater checks for local `changelog` entries with batches not present in the release history and warns before overwriting. (Edge case — most users won't edit the DB. Probably a `--force` flag suffices.)
- [ ] Offline use: server must work fine if update check fails (network down, GitHub rate limit). The check is best-effort.

### 5. Migration from current state

- [ ] Add `meta` table + bootstrap values in the next ingest cycle.
- [ ] Cut the first base release once `meta` is populated and current validation work is at a stable point.
- [ ] Start monthly patches from there.

## Deferred / out of scope

- Progressive/compact-page encoding (e.g., sqlite-web-style virtual tables). Overkill for monthly updates.
- Binary delta (xdelta/bsdiff). Tested poorly against SQLite FTS5 page churn in early sizing — SQL patches win on both size and auditability.
- CDN other than GitHub's. Releases already fronted by a CDN; no need to add one.
- Signed releases (cosign / minisign). Nice-to-have later; start with sha256 verification only.

## Open questions to lock in before building

- Release cadence: monthly on a fixed day of the month, or rolling whenever a patch is worth shipping? (Leaning monthly + ad-hoc for critical corrections.)
- One patch per month, or one patch per correction batch? (Leaning one-per-month — matches how users will experience updates.)
- Keep all historical patches as release assets, or prune old patches once a new base is cut? (Leaning keep-forever; they're small and give a complete audit trail.)
