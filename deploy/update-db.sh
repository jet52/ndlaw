#!/usr/bin/env bash
# Update the deployed databases from the latest GitHub release — multi-corpus,
# idempotent, and self-healing.
#
# Ships opinions.db PLUS the primary-law corpus DBs (constitution / rules /
# statutes / admincode). The server's corpus.attach_corpora() serves whatever
# corpus DBs are present, so the ONLY thing needed to light up a new corpus on
# the live server is to land its file where the installed package looks — which
# this script does by querying ndcourts_mcp.corpus.resolve_corpus_db_path (no
# systemd-unit/env change required, even though self-update.sh does not reinstall
# the unit).
#
# Behavior:
#   * opinions.db is REQUIRED — download / verify-sha256 / quick_check / row-floor;
#     a failure aborts before any swap (and the swap half auto-rolls-back).
#   * each corpus DB is OPTIONAL — if its release asset is absent (404) it is
#     skipped with a warning (so a release that ships only some corpora degrades
#     gracefully, and a corpus missed on one run is picked up on the NEXT run);
#     if present it is fully validated and a failure aborts.
#   * all validated DBs are staged first, then swapped in one service stop/start,
#     each keeping a .bak; a failed end-to-end health probe rolls ALL of them back.
#
#   deploy/update-db.sh             # pull latest, validate, swap
#   deploy/update-db.sh --dry-run   # download + validate only, no swap
#
# Overridable via env (defaults match deploy/SETUP.md's /srv/ndcourts layout):
#   APP_HOME, DB_PATH, VENV, SERVICE, PORT, MIN_OPINIONS, REPO_BASE
set -euo pipefail

APP_HOME="${APP_HOME:-/srv/ndcourts}"
DB_PATH="${DB_PATH:-$APP_HOME/opinions.db}"
VENV="${VENV:-$APP_HOME/ndcourts-mcp/.venv}"
SERVICE="${SERVICE:-ndcourts-mcp}"
PORT="${PORT:-8000}"
MIN_OPINIONS="${MIN_OPINIONS:-19000}"   # floor; current corpus ~19,792
REPO_BASE="${REPO_BASE:-https://github.com/jet52/ndlaw/releases/latest/download}"
DRY_RUN=0; [ "${1:-}" = "--dry-run" ] && DRY_RUN=1

if [ "$(id -u)" -ne 0 ]; then SUDO=sudo; else SUDO=; fi
say() { echo "[update-db] $*"; }
die() { echo "[update-db] ABORT: $*" >&2; exit 1; }

command -v sqlite3 >/dev/null || die "sqlite3 not found"
[ -x "$VENV/bin/python" ] || die "venv python not found at $VENV/bin/python"

# The systemd service runs as this user (no User= ⇒ root). Corpus DB paths are
# resolved per-user (platformdirs keys off $HOME), so they MUST be resolved as the
# SERVICE user — resolving as root (this script's user) places them under
# /root/.local/share where the ndcourts service cannot read them.
RUN_USER="$(systemctl show "$SERVICE" -p User --value 2>/dev/null)"
[ -n "$RUN_USER" ] || RUN_USER=root
RUN_HOME="$(getent passwd "$RUN_USER" | cut -d: -f6)"; [ -n "$RUN_HOME" ] || RUN_HOME=/root
as_run_user() { sudo -u "$RUN_USER" env HOME="$RUN_HOME" "$@"; }

# Resolve where the INSTALLED package expects a corpus DB (env -> bundled -> user
# data), AS THE SERVICE USER so $HOME-based user-data paths match what the running
# service opens.
resolve() { as_run_user "$VENV/bin/python" -c "from ndcourts_mcp import corpus; print(corpus.resolve_corpus_db_path('$1'))" 2>/dev/null; }

# Manifest rows: name|dbfile|count_sql|floor|required|dest
declare -a ROWS=()
ROWS+=("opinions|opinions.db|SELECT COUNT(*) FROM opinions|$MIN_OPINIONS|1|$DB_PATH")
# corpus alias : db filename : provisions floor
for spec in "const:constitution.db:150" "rule:rules.db:500" "ndcc:statutes.db:25000" "admin:admincode.db:12000"; do
  alias="${spec%%:*}"; rest="${spec#*:}"; file="${rest%%:*}"; floor="${rest##*:}"
  dest="$(resolve "$alias")" || dest=""
  [ -n "$dest" ] || { say "WARN: cannot resolve dest for corpus '$alias' — skipping"; continue; }
  ROWS+=("$alias|$file|SELECT COUNT(*) FROM provisions|$floor|0|$dest")
done
# AG opinions is a separate immutable-doc DB (not in corpus.CORPORA); resolve via
# ag_corpus and count ag_opinions rather than provisions.
ag_dest="$(as_run_user "$VENV/bin/python" -c "from ndcourts_mcp.ag_corpus import resolve_ag_db_path; print(resolve_ag_db_path())" 2>/dev/null)" || ag_dest=""
if [ -n "$ag_dest" ]; then
  ROWS+=("ag|ag_opinions.db|SELECT COUNT(*) FROM ag_opinions|6000|0|$ag_dest")
else
  say "WARN: cannot resolve dest for AG opinions DB — skipping"
fi

STAGE="$(mktemp -d "${TMPDIR:-/tmp}/ndcourts-db.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT
cd "$STAGE"

# ---- Phase 1: download + validate everything into staging (no swaps yet) ----
declare -a SWAP=()   # "stagefile|dest|name"
for row in "${ROWS[@]}"; do
  IFS='|' read -r name dbfile sql floor required dest <<<"$row"
  zip="$dbfile.zip"; url="$REPO_BASE/$zip"
  say "fetch $name ($zip)"
  if ! curl -fL --retry 3 -o "$zip" "$url" 2>/dev/null; then
    [ "$required" = "1" ] && die "required asset missing: $url"
    say "  $name not in release (skip; will retry next run)"; continue
  fi
  curl -fL --retry 3 -o "$zip.sha256" "$REPO_BASE/$zip.sha256" || die "$name: sha download failed"
  sha256sum -c "$zip.sha256" >/dev/null 2>&1 || die "$name: sha256 mismatch — download corrupt/truncated"
  unzip -oq "$zip"
  [ -f "$dbfile" ] || die "$name: zip did not contain $dbfile"
  qc="$(sqlite3 "$dbfile" 'PRAGMA quick_check;' 2>&1 | head -1)"
  [ "$qc" = "ok" ] || die "$name: quick_check failed: $qc"
  n="$(sqlite3 "$dbfile" "$sql" 2>/dev/null || echo 0)"
  [ "$n" -ge "$floor" ] 2>/dev/null || die "$name: row count $n below floor $floor (wrong/empty/truncated DB?)"
  rm -f "$dbfile-wal" "$dbfile-shm"
  say "  $name ok (quick_check ok, rows=$n) -> $dest"
  # Integrity here is quick_check + sha256 + row-floor above; the corpus itself
  # is validated (invariants + audit gates) in the private build before release.
  [ "$name" = "opinions" ] && rm -f "$STAGE/$dbfile-wal" "$STAGE/$dbfile-shm"
  SWAP+=("$STAGE/$dbfile|$dest|$name")
done
say "validated ${#SWAP[@]} database(s)"

if [ "$DRY_RUN" = "1" ]; then
  say "dry-run: validated — not swapping (staging cleaned on exit)"; exit 0
fi

# ---- Phase 2: stop service, swap all (keeping .bak), clean WAL ----
say "stop service, swap"
$SUDO systemctl stop "$SERVICE"
declare -a BAK=()
for s in "${SWAP[@]}"; do
  IFS='|' read -r src dest name <<<"$s"
  $SUDO mkdir -p "$(dirname "$dest")"
  if [ -f "$dest" ]; then $SUDO cp -f "$dest" "$dest.bak"; BAK+=("$dest"); fi
  $SUDO rm -f "$dest-wal" "$dest-shm"     # stale sidecars from the old DB
  $SUDO cp -f "$src" "$dest"
  # The service user must be able to read the DB and create WAL/-shm sidecars in
  # its directory (SQLite WAL mode writes them even for read-only use).
  $SUDO chown "$RUN_USER:" "$(dirname "$dest")" "$dest" 2>/dev/null || true
done
$SUDO systemctl start "$SERVICE"

# ---- Phase 3: health probe; roll ALL back on failure ----
say "health probe"
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
  say "DONE — service healthy on ${#SWAP[@]} updated DB(s). Prior copies kept at <db>.bak"
else
  say "health probe FAILED — rolling back ${#BAK[@]} DB(s)"
  $SUDO systemctl stop "$SERVICE"
  for dest in "${BAK[@]}"; do
    $SUDO rm -f "$dest-wal" "$dest-shm"
    $SUDO cp -f "$dest.bak" "$dest"
  done
  $SUDO systemctl start "$SERVICE"
  die "rolled back; check: journalctl -u $SERVICE -n 50"
fi
