#!/usr/bin/env bash
# ONE-TIME server cutover for the v3.0.0 rename (ndcourts-mcp -> ndlaw-mcp).
# Run as ROOT, once, when deploying the first v3.x release. Idempotent-ish:
# every step checks its precondition; aborts on the first failure.
#
# What it does (brief outage between stop and the health probe):
#   1. verifies the repo checkout is at a v3.x tag (fetch+checkout FIRST,
#      as the service user, before running this);
#   2. stops ndcourts-mcp.service, disables ndcourts-update.timer;
#   3. moves /srv/ndcourts/ndcourts-mcp -> /srv/ndcourts/ndlaw-mcp and
#      REBUILDS the venv (a moved venv keeps absolute paths to the old dir);
#   4. installs ndlaw-mcp.service (+resources drop-in) and
#      ndlaw-update.{service,timer}; retires the old units;
#      moves /etc/ndcourts-update.env -> /etc/ndlaw-update.env;
#      rewrites the ndcourts-selfupdate sudoers entry -> ndlaw-selfupdate;
#   5. refreshes the static landing page, starts ndlaw-mcp, enables the
#      timer, health-probes, records the tag in the deploy marker.
#
# Manual rollback if the probe fails and you need the old world back:
#   systemctl disable --now ndlaw-mcp ndlaw-update.timer
#   mv /srv/ndcourts/ndlaw-mcp /srv/ndcourts/ndcourts-mcp
#   (restore old unit files from the previous tag's deploy/ dir, checkout the
#    previous tag, rebuild the venv, daemon-reload, start ndcourts-mcp)
set -euo pipefail

APP_HOME="${APP_HOME:-/srv/ndcourts}"
OLD="$APP_HOME/ndcourts-mcp"
NEW="$APP_HOME/ndlaw-mcp"
RUN_USER="${RUN_USER:-ndcourts}"
PORT="${PORT:-8000}"

log() { echo "[cutover-v3] $*"; }
die() { echo "[cutover-v3] ABORT: $*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run as root"
[ -d "$OLD" ] || die "$OLD not found — already cut over?"
[ ! -e "$NEW" ] || die "$NEW already exists — half-finished cutover? resolve by hand"

# 1) The checkout must already be at the v3.x tag (done by the operator or
# push-db's normal flow BEFORE cutover):
#   sudo -u ndcourts git -C "$OLD" fetch --tags origin
#   sudo -u ndcourts git -C "$OLD" checkout vX.Y.Z
tag="$(sudo -u "$RUN_USER" git -C "$OLD" describe --tags --exact-match 2>/dev/null || echo none)"
case "$tag" in
  v3.*) log "checkout is at $tag" ;;
  *) die "checkout is at '$tag', expected a v3.x tag — fetch + checkout first" ;;
esac
[ -f "$OLD/deploy/ndlaw-mcp.service" ] || die "renamed deploy files missing from the checkout"

# 2) Stop the old world.
log "stopping ndcourts-mcp.service, disabling ndcourts-update.timer"
systemctl stop ndcourts-mcp 2>/dev/null || true
systemctl disable --now ndcourts-update.timer 2>/dev/null || true

# 3) Move the checkout; rebuild the venv (absolute paths inside break on mv).
log "moving $OLD -> $NEW and rebuilding the venv"
mv "$OLD" "$NEW"
sudo -u "$RUN_USER" bash -lc \
  "cd '$NEW' && rm -rf .venv && ~/.local/bin/uv venv >/dev/null && ~/.local/bin/uv pip install . >/dev/null" \
  || die "venv rebuild failed — service is DOWN; see rollback notes in the header"

# 4) Swap the systemd surface.
log "installing ndlaw-mcp + ndlaw-update units, retiring the old ones"
cp "$NEW/deploy/ndlaw-mcp.service" /etc/systemd/system/
mkdir -p /etc/systemd/system/ndlaw-mcp.service.d
cp "$NEW/deploy/ndlaw-mcp-resources.conf" /etc/systemd/system/ndlaw-mcp.service.d/resources.conf
cp "$NEW/deploy/ndlaw-update.service" "$NEW/deploy/ndlaw-update.timer" /etc/systemd/system/
if [ -f /etc/ndcourts-update.env ] && [ ! -f /etc/ndlaw-update.env ]; then
  mv /etc/ndcourts-update.env /etc/ndlaw-update.env
fi
rm -f /etc/systemd/system/ndcourts-mcp.service \
      /etc/systemd/system/ndcourts-update.service \
      /etc/systemd/system/ndcourts-update.timer
rm -rf /etc/systemd/system/ndcourts-mcp.service.d
systemctl daemon-reload

if [ -f /etc/sudoers.d/ndcourts-selfupdate ]; then
  sed "s#$OLD#$NEW#g" /etc/sudoers.d/ndcourts-selfupdate > /etc/sudoers.d/ndlaw-selfupdate
  chmod 440 /etc/sudoers.d/ndlaw-selfupdate
  rm -f /etc/sudoers.d/ndcourts-selfupdate
  log "sudoers entry rewritten -> ndlaw-selfupdate"
fi

# 5) Landing page, start, probe, record.
if [ -d /var/www/ndlaw.org ]; then
  cp "$NEW"/deploy/ndlaw-landing/* /var/www/ndlaw.org/ || log "WARN: landing refresh failed"
fi

log "starting ndlaw-mcp + enabling ndlaw-update.timer"
systemctl enable --now ndlaw-mcp
systemctl enable --now ndlaw-update.timer

probe_ok=""
for _ in $(seq 1 20); do
  if curl -fsS -X POST "http://127.0.0.1:$PORT/mcp" \
       -H 'Content-Type: application/json' \
       -H 'Accept: application/json, text/event-stream' \
       -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"cutover","version":"0"}}}' \
       >/dev/null 2>&1; then probe_ok=1; break; fi
  sleep 1
done
[ -n "$probe_ok" ] || die "health probe FAILED — service is up but not answering; journalctl -u ndlaw-mcp -n 50"

echo "$tag" > "$APP_HOME/.deployed-release"
log "DONE: $tag live as ndlaw-mcp.service from $NEW"
