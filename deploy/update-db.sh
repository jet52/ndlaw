#!/usr/bin/env bash
# Safely update the deployed opinions.db from the latest GitHub release.
#
# Replaces the old "unzip -o over the live DB and restart" recipe, which
# overwrote an open WAL database in place, left stale -wal/-shm files, and
# had no validation or rollback. This script:
#   1. downloads the release zip + its .sha256 and VERIFIES the hash
#   2. unzips to a staging file and gates on integrity:
#        - PRAGMA quick_check = ok
#        - opinions row count >= floor (catches a wrong/empty/truncated DB)
#      (invariants are re-checked as a soft warning; they were already a hard
#       gate at release-build time in scripts/make_release.sh)
#   3. stops the service, atomically swaps (keeping opinions.db.bak), deletes
#      stale WAL sidecar files, and starts the service
#   4. runs a real end-to-end MCP probe; on failure, AUTO-ROLLS-BACK to .bak
#
# Run on the server as a user that can sudo systemctl (or as root).
#   deploy/update-db.sh                 # pull latest, validate, swap
#   deploy/update-db.sh --dry-run       # download + validate only, no swap
#
# Overridable via env (defaults match deploy/SETUP.md's /srv/ndcourts layout):
#   APP_HOME, DB_PATH, VENV, SERVICE, DB_URL, SHA_URL, PORT, MIN_OPINIONS
set -euo pipefail

APP_HOME="${APP_HOME:-/srv/ndcourts}"
DB_PATH="${DB_PATH:-$APP_HOME/opinions.db}"
VENV="${VENV:-$APP_HOME/ndcourts-mcp/.venv}"
SERVICE="${SERVICE:-ndcourts-mcp}"
PORT="${PORT:-8000}"
MIN_OPINIONS="${MIN_OPINIONS:-19000}"   # floor; current corpus ~19,792
REPO_BASE="${REPO_BASE:-https://github.com/jet52/ndcourts-mcp/releases/latest/download}"
DB_URL="${DB_URL:-$REPO_BASE/opinions.db.zip}"
SHA_URL="${SHA_URL:-$REPO_BASE/opinions.db.zip.sha256}"
DRY_RUN=0; [ "${1:-}" = "--dry-run" ] && DRY_RUN=1

if [ "$(id -u)" -ne 0 ]; then SUDO=sudo; else SUDO=; fi
say() { echo "[update-db] $*"; }
die() { echo "[update-db] ABORT: $*" >&2; exit 1; }

command -v sqlite3 >/dev/null || die "sqlite3 not found"
[ -x "$VENV/bin/python" ] || die "venv python not found at $VENV/bin/python"

STAGE="$(mktemp -d "${TMPDIR:-/tmp}/ndcourts-db.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT
cd "$STAGE"

say "1/4 download + verify sha256"
curl -fL --retry 3 -o opinions.db.zip "$DB_URL"   || die "download failed: $DB_URL"
curl -fL --retry 3 -o opinions.db.zip.sha256 "$SHA_URL" || die "sha download failed: $SHA_URL"
# The .sha256 was produced by `shasum -a 256` (==sha256sum format): "<hash>  opinions.db.zip"
sha256sum -c opinions.db.zip.sha256 >/dev/null 2>&1 \
  || die "sha256 mismatch — download corrupt or truncated"
say "    sha256 ok"

say "2/4 unzip + validate staged DB"
unzip -oq opinions.db.zip
[ -f opinions.db ] || die "zip did not contain opinions.db"
NEW="$STAGE/opinions.db"

qc="$(sqlite3 "$NEW" 'PRAGMA quick_check;' 2>&1 | head -1)"
[ "$qc" = "ok" ] || die "quick_check failed: $qc"
n="$(sqlite3 "$NEW" 'SELECT COUNT(*) FROM opinions;' 2>/dev/null || echo 0)"
[ "$n" -ge "$MIN_OPINIONS" ] 2>/dev/null \
  || die "opinions count $n below floor $MIN_OPINIONS (wrong/empty DB?)"
say "    quick_check ok, opinions=$n"

# Soft re-check of invariants against the staged file (hard-gated at build time).
if NDCOURTS_DB="$NEW" "$VENV/bin/python" -m ndcourts_mcp.invariants 2>/dev/null \
     | grep -E 'Invariants:' | grep -q ' 0 regressed'; then
  say "    invariants clean"
else
  say "    WARNING: invariants not clean on staged DB (continuing; was gated at release build)"
fi
# Drop any WAL sidecars validation may have created next to the staged file.
rm -f "$NEW-wal" "$NEW-shm"

if [ "$DRY_RUN" = "1" ]; then
  say "dry-run: staged DB validated — not swapping (staging dir cleaned on exit)"
  exit 0
fi

say "3/4 stop service, swap, clean WAL"
$SUDO systemctl stop "$SERVICE"
# Keep the prior DB for instant rollback.
[ -f "$DB_PATH" ] && $SUDO cp -f "$DB_PATH" "$DB_PATH.bak"
$SUDO rm -f "$DB_PATH-wal" "$DB_PATH-shm"     # stale sidecars from the old DB
$SUDO cp -f "$NEW" "$DB_PATH"
$SUDO systemctl start "$SERVICE"

say "4/4 health probe"
ok=0
for i in $(seq 1 15); do
  if curl -fsS -X POST "http://127.0.0.1:$PORT/mcp" \
       -H 'Content-Type: application/json' \
       -H 'Accept: application/json, text/event-stream' \
       -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"update-db","version":"0"}}}' \
       >/dev/null 2>&1; then ok=1; break; fi
  sleep 1
done
if [ "$ok" = "1" ]; then
  say "DONE — service healthy on new DB (opinions=$n). Prior DB kept at $DB_PATH.bak"
else
  say "health probe FAILED — rolling back to $DB_PATH.bak"
  $SUDO systemctl stop "$SERVICE"
  $SUDO rm -f "$DB_PATH-wal" "$DB_PATH-shm"
  [ -f "$DB_PATH.bak" ] && $SUDO cp -f "$DB_PATH.bak" "$DB_PATH"
  $SUDO systemctl start "$SERVICE"
  die "rolled back; check: journalctl -u $SERVICE -n 50"
fi
