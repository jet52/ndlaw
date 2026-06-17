#!/usr/bin/env bash
# Scheduled self-update for the deployed MCP server.
#
# Polls GitHub for the latest release tag (via the releases/latest redirect —
# no API token, no rate-limit concern). When the tag differs from what's
# deployed, it:
#   1. pins the repo to that tag's commit (as the service user) and reinstalls
#      the package — REQUIRED because the venv is a non-editable install, so a
#      bare `git checkout` does NOT change the running code;
#   2. activates the new code, one of two ways:
#        * DB release (ships *.db.zip assets): runs deploy/update-db.sh to
#          download + verify + validate + swap the DBs and restart the service
#          (with its own health-probe + auto-rollback of the DBs);
#        * code-only release (NO DB assets — a patch that changes only server
#          code, so no ~600 MB DB re-upload is needed): restarts the service to
#          load the new code and health-probes it, rolling the CODE back to the
#          previously-deployed tag and restarting if the probe fails;
#   3. records the new tag and emails the result.
# When already current it exits silently (no download, no restart, no email).
#
# Runs as ROOT so it can systemctl and write under /srv/ndcourts; git/uv steps
# and the corpus-DB path resolution drop to the service user (the unit's User=,
# e.g. ndcourts) via sudo, since corpus DBs resolve per-$HOME.
#
# Config via env (defaults match deploy/SETUP.md's /srv/ndcourts layout):
#   APP_HOME, REPO, RUN_USER, SERVICE, SLUG, MARKER, MAIL_TO, MAIL_FROM, LOCK
# Set MAIL_TO (and configure a sendmail-compatible MTA) to get email; without
# it, results go to journald only (journalctl -u ndcourts-update).
set -euo pipefail

APP_HOME="${APP_HOME:-/srv/ndcourts}"
REPO="${REPO:-$APP_HOME/ndcourts-mcp}"
RUN_USER="${RUN_USER:-ndcourts}"
SERVICE="${SERVICE:-ndcourts-mcp}"
SLUG="${SLUG:-jet52/ndlaw}"
MARKER="${MARKER:-$APP_HOME/.deployed-release}"
MAIL_TO="${MAIL_TO:-}"
MAIL_FROM="${MAIL_FROM:-ndcourts-update@$(hostname -f 2>/dev/null || hostname)}"
LOCK="${LOCK:-/run/ndcourts-update.lock}"
PORT="${PORT:-8000}"                                       # local health-probe port
REPO_BASE="${REPO_BASE:-https://github.com/$SLUG/releases/latest/download}"

log() { echo "[self-update] $*"; }

notify() {  # subject, body
  local subject="$1" body="$2" sm
  log "$subject"
  [ -n "$MAIL_TO" ] || { log "no MAIL_TO set — emailing skipped"; return 0; }
  sm="$(command -v sendmail || echo /usr/sbin/sendmail)"
  if [ -x "$sm" ]; then
    printf 'To: %s\nFrom: %s\nSubject: %s\n\n%s\n' \
      "$MAIL_TO" "$MAIL_FROM" "$subject" "$body" | "$sm" -t \
      || log "WARN: sendmail failed — see journald for the result"
  else
    log "WARN: no sendmail found — cannot email '$subject'"
  fi
}

# Reinstall the package at a git ref as the service user (non-editable venv ⇒
# checkout alone does not change the running code). Used for both the forward
# install and the code-only rollback. Returns nonzero on any step's failure.
reinstall_code() {
  sudo -u "$RUN_USER" git -C "$REPO" -c advice.detachedHead=false checkout --quiet "$1" \
    && sudo -u "$RUN_USER" bash -lc "cd '$REPO' && PATH=\"\$HOME/.local/bin:\$PATH\" uv pip install . >/dev/null 2>&1"
}

# True if the latest release ships DB assets (so update-db.sh has something to
# fetch). A one-byte ranged GET of opinions.db.zip: 200/206 ⇒ present, 404 ⇒
# code-only release. GitHub honors Range on release assets, so this does not
# pull the ~600 MB file. update-db.sh remains the authority on DB validation;
# this only routes between the DB path and the code-only path.
release_has_db_assets() {
  curl -fsSL -r 0-0 -o /dev/null "$REPO_BASE/opinions.db.zip" 2>/dev/null
}

# Health-probe the local service (mirrors update-db.sh's probe). Returns 0 once
# an MCP initialize handshake succeeds within ~15s, else 1.
health_probe() {
  local i
  for i in $(seq 1 15); do
    if curl -fsS -X POST "http://127.0.0.1:$PORT/mcp" \
         -H 'Content-Type: application/json' \
         -H 'Accept: application/json, text/event-stream' \
         -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"self-update","version":"0"}}}' \
         >/dev/null 2>&1; then return 0; fi
    sleep 1
  done
  return 1
}

main() {
  # Serialize: a slow run must not overlap the next timer tick.
  exec 9>"$LOCK"
  flock -n 9 || { log "another run holds the lock — exiting"; exit 0; }

  command -v git  >/dev/null || { log "ABORT: git not found"; exit 1; }
  command -v curl >/dev/null || { log "ABORT: curl not found"; exit 1; }

  # Latest release tag from the releases/latest redirect target.
  local latest_url tag deployed
  latest_url="$(curl -fsS -o /dev/null -w '%{url_effective}' -L \
    "https://github.com/$SLUG/releases/latest")" \
    || { log "ABORT: cannot reach GitHub"; exit 1; }
  tag="${latest_url##*/}"
  case "$tag" in
    v[0-9]*) ;;
    *) log "ABORT: unexpected tag '$tag' from '$latest_url'"; exit 1 ;;
  esac

  deployed="$(cat "$MARKER" 2>/dev/null || echo none)"
  if [ "$tag" = "$deployed" ]; then
    log "already at $tag — nothing to do"
    exit 0
  fi
  log "new release detected: $deployed -> $tag"

  # 1) Pin code to the tag and reinstall (non-editable venv ⇒ reinstall is mandatory).
  sudo -u "$RUN_USER" git -C "$REPO" fetch --tags --prune --quiet origin \
    || { notify "ndcourts deploy FAILED ($tag): git fetch" \
         "git fetch failed on $(hostname) deploying $tag. No change made."; exit 1; }
  sudo -u "$RUN_USER" git -C "$REPO" -c advice.detachedHead=false checkout --quiet "$tag" \
    || { notify "ndcourts deploy FAILED ($tag): git checkout" \
         "git checkout $tag failed on $(hostname). No change made."; exit 1; }
  sudo -u "$RUN_USER" bash -lc "cd '$REPO' && PATH=\"\$HOME/.local/bin:\$PATH\" uv pip install . >/dev/null 2>&1" \
    || { notify "ndcourts deploy FAILED ($tag): pip install" \
         "uv pip install . failed on $(hostname) deploying $tag. Code is checked out at $tag but not installed; service still on prior code. Investigate."; exit 1; }

  # 2) Activate the new code. Two paths, chosen by whether the release ships DBs.
  if release_has_db_assets; then
    # DB release: update-db.sh verifies sha256, validates, swaps (keeping .bak),
    # restarts the service (loading the new code), health-probes, and
    # auto-rolls-back the DB on probe failure.
    if "$REPO/deploy/update-db.sh"; then
      echo "$tag" > "$MARKER"
      local n
      n="$(sudo -u "$RUN_USER" sqlite3 "$APP_HOME/opinions.db" 'SELECT COUNT(*) FROM opinions;' 2>/dev/null || echo '?')"
      notify "ndcourts deployed $tag" \
        "Server $(hostname) is now on $tag (opinions=$n). Code pinned to the tag and reinstalled; DB swapped and health-probed OK. Prior DB kept at $APP_HOME/opinions.db.bak."
    else
      notify "ndcourts deploy FAILED ($tag): update-db rolled back" \
        "update-db.sh failed/rolled back on $(hostname) deploying $tag; DB restored from .bak. NOTE: code is already at $tag, so code and DB may be mismatched — investigate before the next run. Logs: journalctl -u $SERVICE -n 50."
      exit 1
    fi
  else
    # Code-only release (no DB assets): the DBs are unchanged, so just restart
    # the service to load the reinstalled code and health-probe it. On failure,
    # roll the CODE back to the previously-deployed tag (the DBs were untouched).
    log "code-only release (no DB assets) — restart service + health-probe"
    systemctl restart "$SERVICE"
    if health_probe; then
      echo "$tag" > "$MARKER"
      notify "ndcourts deployed $tag (code-only)" \
        "Server $(hostname) is now on $tag. Code reinstalled and the service restarted + health-probed OK; databases unchanged (no DB assets in this release)."
    else
      log "health probe FAILED after code-only deploy — rolling code back to $deployed"
      if [ "$deployed" != "none" ] && reinstall_code "$deployed"; then
        systemctl restart "$SERVICE"
        notify "ndcourts deploy FAILED ($tag): code rolled back to $deployed" \
          "Health probe failed after the code-only deploy of $tag on $(hostname); rolled the code back to $deployed and restarted. Marker left at $deployed. Logs: journalctl -u $SERVICE -n 50."
      else
        notify "ndcourts deploy FAILED ($tag): ROLLBACK FAILED — service may be down" \
          "Health probe failed deploying $tag and the code rollback to '$deployed' also failed on $(hostname). The service may be DOWN — investigate now. Logs: journalctl -u $SERVICE -n 50."
      fi
      exit 1
    fi
  fi
}

main "$@"
