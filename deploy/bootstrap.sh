#!/usr/bin/env bash
# One-shot bootstrap for ndcourts-mcp on a fresh Ubuntu 22.04/24.04 droplet.
# Run as root. Idempotent: re-running after a partial failure is safe.
#
# Required env vars (skip all four if MCP_SKIP_CADDY=1):
#   MCP_DOMAIN     e.g.  mcp.example.com   (must already resolve to this VPS)
#   MCP_EMAIL      e.g.  you@example.com   (Let's Encrypt account)
#   MCP_USER       e.g.  teammate1         (initial Basic Auth user)
#   MCP_PASSWORD   e.g.  s3cret            (its plaintext password; bcrypted here)
#
# Optional:
#   MCP_SKIP_CADDY        set =1 to install only the app + systemd unit (no
#                         Caddy, no Caddyfile, no fail2ban-for-Caddy). Use this
#                         when nginx/Apache/etc. is already fronting :80/:443
#                         and you'll reverse-proxy to 127.0.0.1:8000 yourself.
#   MCP_REPO              default: https://github.com/jet52/ndlaw.git
#   MCP_DB_URL            default: <repo>/releases/latest/download/opinions.db.zip
#   MCP_FORCE_CADDYFILE   set =1 to overwrite an existing /etc/caddy/Caddyfile
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/jet52/ndlaw/main/deploy/bootstrap.sh \
#     | MCP_DOMAIN=mcp.example.com MCP_EMAIL=you@example.com \
#       MCP_USER=teammate1 MCP_PASSWORD='...' bash

set -euo pipefail

# ---------- preflight ----------
[[ $EUID -eq 0 ]] || { echo "must run as root" >&2; exit 1; }
. /etc/os-release
[[ "${ID:-}" == "ubuntu" ]] || { echo "this script targets Ubuntu (got $ID)" >&2; exit 1; }

if [[ "${MCP_SKIP_CADDY:-0}" != "1" ]]; then
  for v in MCP_DOMAIN MCP_EMAIL MCP_USER MCP_PASSWORD; do
    [[ -n "${!v:-}" ]] || { echo "missing required env var: $v" >&2; exit 1; }
  done
fi

MCP_REPO="${MCP_REPO:-https://github.com/jet52/ndlaw.git}"
MCP_DB_URL="${MCP_DB_URL:-https://github.com/jet52/ndlaw/releases/latest/download/opinions.db.zip}"
APP_HOME=/srv/ndcourts
APP_DIR=$APP_HOME/ndcourts-mcp
DB_PATH=$APP_HOME/opinions.db

log() { printf '\n\033[1;36m==>\033[0m %s\n' "$*"; }
as_ndcourts() { sudo -u ndcourts -H bash -lc "$1"; }

# ---------- 1. base packages ----------
log "apt update + base packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
  ca-certificates curl git unzip \
  ufw fail2ban \
  debian-keyring debian-archive-keyring apt-transport-https gnupg

# ---------- 2. swap (1GB box → add 2GB swap) ----------
log "swap file"
if ! swapon --show 2>/dev/null | grep -q /swapfile; then
  if [[ ! -f /swapfile ]]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile >/dev/null
  fi
  swapon /swapfile
fi
grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab

# ---------- 3. system user ----------
log "system user 'ndcourts'"
if ! id -u ndcourts &>/dev/null; then
  useradd --system --create-home --home-dir "$APP_HOME" \
          --shell /usr/sbin/nologin ndcourts
fi
mkdir -p "$APP_HOME"
chown ndcourts:ndcourts "$APP_HOME"

# ---------- 4. uv (per-user) ----------
log "uv installer"
if [[ ! -x "$APP_HOME/.local/bin/uv" ]]; then
  as_ndcourts 'curl -LsSf https://astral.sh/uv/install.sh | sh'
fi

# ---------- 5. clone / update repo ----------
log "repo $MCP_REPO"
if [[ -d "$APP_DIR/.git" ]]; then
  as_ndcourts "cd '$APP_DIR' && git pull --ff-only"
else
  as_ndcourts "git clone '$MCP_REPO' '$APP_DIR'"
fi

# ---------- 6. venv + install ----------
log "venv + pip install"
if [[ ! -x "$APP_DIR/.venv/bin/ndcourts-mcp" ]]; then
  as_ndcourts "cd '$APP_DIR' && ~/.local/bin/uv venv"
fi
as_ndcourts "cd '$APP_DIR' && ~/.local/bin/uv pip install ."

# ---------- 7. opinions.db ----------
# skip download if a plausibly-complete DB already sits in place.
log "opinions.db"
need_db=1
if [[ -f "$DB_PATH" ]]; then
  size=$(stat -c%s "$DB_PATH")
  (( size > 524288000 )) && need_db=0  # > 500 MB → assume complete
fi
if (( need_db )); then
  as_ndcourts "cd '$APP_HOME' && \
    curl -fL --retry 3 -o opinions.db.zip '$MCP_DB_URL' && \
    unzip -o opinions.db.zip && rm opinions.db.zip"
fi

# ---------- 8. systemd unit ----------
log "systemd unit"
install -m 0644 "$APP_DIR/deploy/ndcourts-mcp.service" /etc/systemd/system/ndcourts-mcp.service
systemctl daemon-reload
systemctl enable --now ndcourts-mcp

# wait briefly for the socket, then probe
for _ in 1 2 3 4 5 6 7 8 9 10; do
  ss -ltn 'sport = :8000' 2>/dev/null | grep -q LISTEN && break
  sleep 1
done
if ! curl -fsS -X POST http://127.0.0.1:8000/mcp \
      -H 'Content-Type: application/json' \
      -H 'Accept: application/json, text/event-stream' \
      -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"bootstrap","version":"0"}}}' \
      >/dev/null; then
  echo "WARN: local MCP probe failed — check: journalctl -u ndcourts-mcp -n 50" >&2
fi

if [[ "${MCP_SKIP_CADDY:-0}" != "1" ]]; then

# ---------- 9. Caddy ----------
log "Caddy"
if ! command -v caddy >/dev/null; then
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
    | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
    > /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -qq
  apt-get install -y -qq caddy
fi

# rate-limit plugin (rebuilds /usr/bin/caddy via xcaddy; takes ~1 min)
if ! caddy list-modules 2>/dev/null | grep -q '^http.handlers.rate_limit'; then
  caddy add-package github.com/mholt/caddy-ratelimit
  systemctl restart caddy
fi

# ---------- 10. Caddyfile ----------
log "Caddyfile"
mkdir -p /var/log/caddy && chown caddy:caddy /var/log/caddy

write_caddyfile=0
if [[ ! -f /etc/caddy/Caddyfile ]] \
   || grep -q 'YOURDOMAIN\|YOUR_EMAIL\|REPLACE_WITH_BCRYPT_HASH' /etc/caddy/Caddyfile \
   || [[ "${MCP_FORCE_CADDYFILE:-0}" == "1" ]]; then
  write_caddyfile=1
fi

if (( write_caddyfile )); then
  hash=$(printf '%s' "$MCP_PASSWORD" | caddy hash-password)
  # render from the template, substituting only the three placeholders
  sed \
    -e "s|YOUR_EMAIL@example.com|$MCP_EMAIL|" \
    -e "s|mcp.YOURDOMAIN.com|$MCP_DOMAIN|" \
    -e "s|teammate1 REPLACE_WITH_BCRYPT_HASH|$MCP_USER $hash|" \
    "$APP_DIR/deploy/Caddyfile" > /etc/caddy/Caddyfile
  systemctl reload caddy || systemctl restart caddy
else
  echo "  /etc/caddy/Caddyfile already customized — leaving alone (set MCP_FORCE_CADDYFILE=1 to overwrite)"
fi

# ---------- 11. firewall ----------
log "ufw"
ufw allow OpenSSH >/dev/null
ufw allow 80,443/tcp >/dev/null
ufw status | grep -q "Status: active" || ufw --force enable

# ---------- 12. fail2ban ----------
log "fail2ban (Caddy jail)"
install -m 0644 "$APP_DIR/deploy/fail2ban/filter.d/caddy-ndcourts.conf" /etc/fail2ban/filter.d/caddy-ndcourts.conf
install -m 0644 "$APP_DIR/deploy/fail2ban/jail.d/caddy-ndcourts.conf"   /etc/fail2ban/jail.d/caddy-ndcourts.conf
systemctl enable --now fail2ban
systemctl restart fail2ban

fi  # end of MCP_SKIP_CADDY guard

# ---------- done ----------
if [[ "${MCP_SKIP_CADDY:-0}" == "1" ]]; then
cat <<EOF

\033[1;32mApp install complete (Caddy skipped).\033[0m

  ndcourts-mcp is listening on 127.0.0.1:8000 — wire your existing web
  server to it as a reverse proxy. See deploy/mcp-apache.conf for an
  Apache vhost template, or apply the equivalent in nginx.

  Useful:
    systemctl status ndcourts-mcp
    journalctl -u ndcourts-mcp -f
    ss -ltnp 'sport = :8000'
EOF
else
cat <<EOF

\033[1;32mBootstrap complete.\033[0m

  Endpoint:  https://$MCP_DOMAIN/mcp
  User:      $MCP_USER

  Probe from your laptop:
    claude mcp add --transport http ndcourts https://$MCP_DOMAIN/mcp \\
      --header "Authorization: Basic \$(printf '$MCP_USER:<password>' | base64)"

  Useful:
    systemctl status ndcourts-mcp caddy fail2ban
    journalctl -u ndcourts-mcp -f
    tail -f /var/log/caddy/ndcourts-mcp.log
    fail2ban-client status caddy-ndcourts

  Reminder: harden SSH separately —
    /etc/ssh/sshd_config:  PasswordAuthentication no   PermitRootLogin no
    systemctl restart ssh
EOF
fi
