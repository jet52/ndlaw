#!/usr/bin/env bash
# One-command DB push: publish a new GitHub release from the local opinions.db,
# then have the deployed server pull + validate + swap it.
#
# Run from the repo root on your laptop. Wraps the two halves:
#   1. scripts/make_release.sh --publish   (gates + zips + sha256 + gh release)
#   2. ssh <server> 'deploy/update-db.sh'  (safe pull/validate/swap/rollback)
#
# Set the SSH target (no default — your server):
#   NDCOURTS_SSH=jerod@mcp.ndconst.org deploy/push-db.sh
# Override the remote command if your layout differs:
#   NDCOURTS_REMOTE_CMD='sudo /path/to/deploy/self-update.sh'
set -euo pipefail
cd "$(dirname "$0")/.."

: "${NDCOURTS_SSH:?set NDCOURTS_SSH=user@host (the deployed server)}"
# Drive the same self-update.sh the nightly timer uses: it pins the repo to the
# just-published tag, REINSTALLS the (non-editable) package — which update-db.sh
# alone does NOT do — then swaps the DB, restarts, and health-probes. Needs root
# (it systemctls + writes /srv/ndcourts); the SSH login user must have NOPASSWD
# sudo for self-update.sh (see deploy/SETUP.md §8a).
REMOTE_CMD="${NDCOURTS_REMOTE_CMD:-sudo /srv/ndcourts/ndcourts-mcp/deploy/self-update.sh}"

# Preflight: make_release aborts on an existing tag — but only after zipping
# 548MB. Catch it here first. Each push needs a fresh version: bump `version`
# in pyproject.toml and commit (the build also requires a clean git tree).
VERSION="$(grep -m1 '^version' pyproject.toml | sed -E 's/.*"([^"]+)".*/\1/')"
TAG="v${VERSION}"
if gh release view "$TAG" >/dev/null 2>&1; then
  echo "ERROR: release $TAG already exists. Bump 'version' in pyproject.toml and commit, then retry." >&2
  exit 1
fi
if [ -n "$(git status --porcelain | grep -vE '\.bak|opinions\.db\.zip')" ]; then
  echo "ERROR: git tree not clean (make_release requires it). Commit your changes, then retry." >&2
  exit 1
fi
echo "=== push-db: releasing $TAG -> $NDCOURTS_SSH ==="

echo "=== push-db: 1/2 publish release ==="
scripts/make_release.sh --publish

echo "=== push-db: 2/2 update server ($NDCOURTS_SSH) ==="
# Login shell so PATH/sudo behave; the remote script does its own validation + rollback.
ssh "$NDCOURTS_SSH" "bash -lc '$REMOTE_CMD'"

echo "=== push-db: done ==="
