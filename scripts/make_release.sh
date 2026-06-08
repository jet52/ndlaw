#!/usr/bin/env bash
# Build (and optionally publish) the release assets: opinions.db PLUS the
# primary-law corpus DBs (constitution / rules / statutes / admincode).
#
# Bakes the pre-release gates into tooling so the editorial-leak
# near-miss of 2026-05-15 cannot recur silently:
#   1. invariants must be clean (0 regressed)                      [opinions]
#   2. redistribution-scope scan must be 0 (no Westlaw editorial:
#      West Headnotes / Procedural Posture / Thomson Reuters / KeyCite
#      / End of Document)                                          [opinions]
#   3. git working tree must be clean
#   4. every shipped DB passes quick_check + a row floor
# Only then does it zip each DB, write per-file sha256, and — with
# --publish — create the GitHub release (all assets) for the pyproject tag.
#
# Usage:
#   scripts/make_release.sh            # build + verify locally only
#   scripts/make_release.sh --publish  # also create the GitHub release
set -euo pipefail

cd "$(dirname "$0")/.."
PUBLISH="${1:-}"

# Shipped databases:  name : dbfile : count_sql : floor
#   opinions is the anchor; the four corpora are the primary-law expansion.
DBS=(
  "opinions|opinions.db|SELECT COUNT(*) FROM opinions|19000"
  "constitution|constitution.db|SELECT COUNT(*) FROM provisions|150"
  "rules|rules.db|SELECT COUNT(*) FROM provisions|500"
  "statutes|statutes.db|SELECT COUNT(*) FROM provisions|25000"
  "admincode|admincode.db|SELECT COUNT(*) FROM provisions|12000"
)

[ -f opinions.db ] || { echo "ERROR: opinions.db not found" >&2; exit 1; }

VERSION="$(grep -m1 '^version' pyproject.toml | sed -E 's/.*"([^"]+)".*/\1/')"
TAG="v${VERSION}"
echo "=== make_release: ${TAG} ==="

echo "[1/6] invariants (opinions)"
uv run python -m ndcourts_mcp.invariants 2>&1 | grep -E 'Invariants:' \
  | grep -q ' 0 regressed' \
  || { echo "ABORT: invariants regressed" >&2; exit 1; }

echo "[2/6] redistribution-scope scan (opinions)"
SCOPE=$(uv run python - <<'PY'
import sqlite3
c = sqlite3.connect("opinions.db")
markers = ["West Headnotes", "Procedural Posture(s):", "Thomson Reuters",
           "KeyCite", "End of Document"]
total = 0
for m in markers:
    n = c.execute("SELECT COUNT(*) FROM opinions WHERE text_content LIKE ?",
                  (f"%{m}%",)).fetchone()[0]
    if n:
        print(f"  {m}: {n}")
    total += n
print(total)
PY
)
echo "$SCOPE" | sed '$d' | grep . && true
[ "$(echo "$SCOPE" | tail -1)" = "0" ] \
  || { echo "ABORT: redistribution-scope scan found editorial content; "\
"run strip_westlaw_headnotes / strip_westlaw_synopsis first" >&2; exit 1; }
echo "  scope clean (0 editorial markers)"

echo "[3/6] git clean"
[ -z "$(git status --porcelain | grep -vE '\.bak|\.db\.zip')" ] \
  || { echo "ABORT: git working tree not clean" >&2; exit 1; }

echo "[4/6] validate each shipped DB (quick_check + row floor)"
ASSETS=()
for spec in "${DBS[@]}"; do
  IFS='|' read -r name dbfile sql floor <<<"$spec"
  if [ ! -f "$dbfile" ]; then
    echo "    SKIP $name: $dbfile not present (will not ship this corpus)"; continue
  fi
  qc="$(sqlite3 "$dbfile" 'PRAGMA quick_check;' 2>&1 | head -1)"
  [ "$qc" = "ok" ] || { echo "ABORT: $name quick_check failed: $qc" >&2; exit 1; }
  n="$(sqlite3 "$dbfile" "$sql" 2>/dev/null || echo 0)"
  [ "$n" -ge "$floor" ] 2>/dev/null \
    || { echo "ABORT: $name row count $n below floor $floor" >&2; exit 1; }
  echo "    $name ok (quick_check ok, rows=$n)"
  ASSETS+=("$dbfile")
done

echo "[5/6] zip + sha256 each shipped DB"
RELEASE_FILES=()
for dbfile in "${ASSETS[@]}"; do
  zip="$dbfile.zip"; sha="$dbfile.zip.sha256"
  rm -f "$zip" "$sha"
  zip -9 -q "$zip" "$dbfile"
  shasum -a 256 "$zip" > "$sha"
  echo "    $dbfile  $(du -h "$dbfile" | cut -f1)  ->  $zip  $(du -h "$zip" | cut -f1)"
  RELEASE_FILES+=("$zip" "$sha")
done

echo "[6/6] release"
if [ "$PUBLISH" = "--publish" ]; then
  if gh release view "$TAG" >/dev/null 2>&1; then
    echo "ABORT: release $TAG already exists" >&2; exit 1
  fi
  # Pin the tag to THIS commit. `gh release create` defaults the tag to the
  # remote branch tip, so if the version-bump commit isn't pushed yet the tag
  # silently lands on the prior commit (v0.10.0 hit this on 2026-06-02). Push
  # the release commit first, then create the tag explicitly at its SHA.
  BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  HEAD_SHA="$(git rev-parse HEAD)"
  git push origin "$BRANCH"
  gh release create "$TAG" "${RELEASE_FILES[@]}" \
    --target "$HEAD_SHA" \
    --title "$TAG" \
    --notes "ND primary-law database release — ${TAG}. Ships opinions.db plus the primary-law corpus DBs (constitution, rules, statutes, admincode) as separate assets. See CHANGELOG-data.md for corrections in this cycle. Verify each: shasum -a 256 -c <asset>.sha256"
  echo "  published $TAG at $HEAD_SHA with ${#ASSETS[@]} DB asset(s): ${ASSETS[*]}"
else
  echo "  built locally only (${#ASSETS[@]} DB asset(s): ${ASSETS[*]}). To publish:"
  echo "    scripts/make_release.sh --publish"
fi
