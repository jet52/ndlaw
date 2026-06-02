#!/usr/bin/env bash
# Build (and optionally publish) the opinions.db release asset.
#
# Bakes the pre-release gates into tooling so the editorial-leak
# near-miss of 2026-05-15 cannot recur silently:
#   1. invariants must be clean (0 regressed)
#   2. redistribution-scope scan must be 0 (no Westlaw editorial:
#      West Headnotes / Procedural Posture / Thomson Reuters / KeyCite
#      / End of Document)
#   3. git working tree must be clean
# Only then does it zip opinions.db, write the sha256, and — with
# --publish — create the GitHub release for the pyproject version tag.
#
# Usage:
#   scripts/make_release.sh            # build + verify locally only
#   scripts/make_release.sh --publish  # also create the GitHub release
set -euo pipefail

cd "$(dirname "$0")/.."
DB="opinions.db"
ZIP="opinions.db.zip"
SHA="opinions.db.zip.sha256"
PUBLISH="${1:-}"

[ -f "$DB" ] || { echo "ERROR: $DB not found" >&2; exit 1; }

VERSION="$(grep -m1 '^version' pyproject.toml | sed -E 's/.*"([^"]+)".*/\1/')"
TAG="v${VERSION}"
echo "=== make_release: ${TAG} ==="

echo "[1/5] invariants"
uv run python -m ndcourts_mcp.invariants 2>&1 | grep -E 'Invariants:' \
  | grep -q ' 0 regressed' \
  || { echo "ABORT: invariants regressed" >&2; exit 1; }

echo "[2/5] redistribution-scope scan"
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

echo "[3/5] git clean"
[ -z "$(git status --porcelain | grep -vE '\.bak|opinions\.db\.zip')" ] \
  || { echo "ABORT: git working tree not clean" >&2; exit 1; }

echo "[4/5] zip + sha256"
rm -f "$ZIP" "$SHA"
zip -9 -q "$ZIP" "$DB"
shasum -a 256 "$ZIP" > "$SHA"
echo "  $DB  $(du -h "$DB" | cut -f1)  ->  $ZIP  $(du -h "$ZIP" | cut -f1)"
echo "  $(cat "$SHA")"

echo "[5/5] release"
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
  gh release create "$TAG" "$ZIP" "$SHA" \
    --target "$HEAD_SHA" \
    --title "$TAG" \
    --notes "ND Supreme Court opinion database — ${TAG}. See CHANGELOG-data.md for corrections in this cycle. Verify: shasum -a 256 -c ${SHA}"
  echo "  published $TAG at $HEAD_SHA"
else
  echo "  built locally only. To publish:"
  echo "    scripts/make_release.sh --publish"
  echo "  (or: gh release create $TAG $ZIP $SHA --title \"$TAG\" --notes ...)"
fi
