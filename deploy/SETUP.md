# Public VPS deployment (Ubuntu)

Serve `ndcourts-mcp` over Streamable HTTP from an Ubuntu server on the open
internet, with **TLS + HTTP Basic Auth + rate limiting + fail2ban**. The
opinion data is public (CC0), so auth here is access control and abuse
prevention, not secrecy.

```
Internet ──TLS──▶ Caddy :443 ──localhost──▶ ndcourts-mcp 127.0.0.1:8000
                  basic_auth                 NDCOURTS_TRANSPORT=http
                  rate_limit                 read-only opinions.db
ufw: 22/80/443 only   ·   fail2ban bans repeated 401s
```

Files in this dir: `bootstrap.sh`, `Caddyfile`, `ndcourts-mcp.service`,
`fail2ban/`, `mcp-apache.conf` (for the [alternative](#alternative-alongside-an-existing-web-server)).

## 0. Assumptions

- Ubuntu 22.04 / 24.04, with `sudo`.
- A domain name (e.g. `mcp.yourdomain.com`) with an **A record pointing at
  the VPS IP** — required for automatic Let's Encrypt TLS.
- Replace `mcp.yourdomain.com` and `you@example.com` throughout.

## Quick install (one-shot bootstrap)

On a **fresh** Ubuntu droplet with no web server already on :80/:443,
[`deploy/bootstrap.sh`](bootstrap.sh) wraps sections 1–6 into a single
idempotent run. From a root shell:

```bash
curl -fsSL https://raw.githubusercontent.com/jet52/ndcourts-mcp/main/deploy/bootstrap.sh \
  | MCP_DOMAIN=mcp.yourdomain.com \
    MCP_EMAIL=you@example.com \
    MCP_USER=teammate1 \
    MCP_PASSWORD='change-me' \
    bash
```

The script adds a 2 GB swapfile (helpful on 1 GB droplets), creates the
`ndcourts` user, installs the app and database, sets up the systemd unit,
installs Caddy with the rate-limit plugin, renders the Caddyfile from
your env vars, opens the firewall, and installs the fail2ban jail. Safe
to re-run after a partial failure. Skip SSH hardening (§5) is deliberate
— do that yourself after confirming key-based login works.

If you're co-existing with an existing web server, see the
[alternative](#alternative-alongside-an-existing-web-server) at the end,
which uses the same script with `MCP_SKIP_CADDY=1`.

The sections below are the manual walk-through equivalent.

## 1. System user and layout

```bash
sudo useradd --system --create-home --home-dir /srv/ndcourts --shell /usr/sbin/nologin ndcourts
sudo mkdir -p /srv/ndcourts && sudo chown ndcourts:ndcourts /srv/ndcourts
```

## 2. Install the app + database

```bash
# uv (fast Python manager) for the ndcourts user
sudo -u ndcourts bash -lc 'curl -LsSf https://astral.sh/uv/install.sh | sh'

# clone + venv + install
sudo -u ndcourts bash -lc '
  cd /srv/ndcourts
  git clone https://github.com/jet52/ndcourts-mcp.git
  cd ndcourts-mcp
  ~/.local/bin/uv venv
  ~/.local/bin/uv pip install .
'

# download the database release asset (~528 MB zip, ~1.1 GB unzipped)
sudo -u ndcourts bash -lc '
  cd /srv/ndcourts
  curl -L -o opinions.db.zip https://github.com/jet52/ndcourts-mcp/releases/latest/download/opinions.db.zip
  unzip -o opinions.db.zip && rm opinions.db.zip
'
```

> The DB directory must stay writable by the `ndcourts` user: SQLite WAL mode
> creates `opinions.db-wal` / `-shm` files next to it even when only reading.

## 3. Run it as a service

```bash
sudo cp /srv/ndcourts/ndcourts-mcp/deploy/ndcourts-mcp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ndcourts-mcp
# verify it bound to localhost and answers MCP:
curl -sL -X POST http://127.0.0.1:8000/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}'
```

You should see a JSON-RPC result naming the `ndcourts` server.

## 4. Caddy (TLS + Basic Auth + rate limit)

```bash
# install Caddy from the official apt repo
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install -y caddy

# add the rate-limit plugin (swaps in a custom Caddy build), then restart
sudo caddy add-package github.com/mholt/caddy-ratelimit
sudo systemctl restart caddy
```

> No-plugin alternative: drop the `rate_limit` block from the Caddyfile and
> rely on fail2ban + (optionally) Cloudflare, or use nginx `limit_req`.

Configure it:

```bash
# create a bcrypt hash for each user
caddy hash-password            # prompts for the password, prints the hash

sudo cp /srv/ndcourts/ndcourts-mcp/deploy/Caddyfile /etc/caddy/Caddyfile
sudo nano /etc/caddy/Caddyfile  # set email, domain, and paste the hash(es)
sudo mkdir -p /var/log/caddy && sudo chown caddy:caddy /var/log/caddy
sudo systemctl reload caddy
```

## 5. Firewall + SSH hardening

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80,443/tcp
sudo ufw enable
```

Lock SSH to keys only — edit `/etc/ssh/sshd_config`: set
`PasswordAuthentication no` and `PermitRootLogin no`, then
`sudo systemctl restart ssh`. (Confirm you have a working key first.)

## 6. fail2ban

```bash
sudo apt install -y fail2ban
sudo cp /srv/ndcourts/ndcourts-mcp/deploy/fail2ban/filter.d/caddy-ndcourts.conf /etc/fail2ban/filter.d/
sudo cp /srv/ndcourts/ndcourts-mcp/deploy/fail2ban/jail.d/caddy-ndcourts.conf  /etc/fail2ban/jail.d/
sudo systemctl restart fail2ban
sudo fail2ban-client status caddy-ndcourts
```

## 7. Connect a client

Preset the credential header so the client never hits the 401 challenge
(some MCP clients try to start OAuth on a bare 401):

```bash
claude mcp add --transport http ndcourts https://mcp.yourdomain.com/mcp \
  --header "Authorization: Basic $(printf 'teammate1:thepassword' | base64)"
```

Claude Desktop and other clients: see [CLIENTS.md](CLIENTS.md) for
per-client setup (Claude Code, Claude Desktop on macOS / Linux /
Windows, and notes on the web/mobile clients).

The endpoint is **`/mcp`** (no trailing slash — `/mcp/` 307-redirects).

## 8. Updating the database

The DB ships as a GitHub release asset (`opinions.db.zip` + `.sha256`). Updating
is a publish-then-pull: cut a release from your build machine, then have the
server pull, validate, and swap it.

**One command, from the repo on your build machine:**

```bash
NDCOURTS_SSH=ndcourts@mcp.YOURDOMAIN.com deploy/push-db.sh
```

This runs `scripts/make_release.sh --publish` (gates on invariants + redistribution
scope + clean tree, zips, sha256s, creates the `v<version>` GitHub release) and
then SSHes in to run `deploy/update-db.sh` on the server.

**Server side only** (if you publish the release separately, or want to pull on
the box): `deploy/update-db.sh` downloads the latest release, **verifies the
sha256**, validates the staged DB (`PRAGMA quick_check` + opinions-count floor),
then **stops the service, swaps atomically (keeping `opinions.db.bak`), clears
stale `-wal`/`-shm`, restarts, and runs an end-to-end `/mcp` probe — auto-rolling
back to `.bak` if the probe fails**. Preview without swapping:

```bash
sudo -u ndcourts deploy/update-db.sh --dry-run   # download + validate only
sudo deploy/update-db.sh                          # validate, swap, health-check
```

> Don't `unzip -o` over the live `opinions.db` by hand: it overwrites an open
> WAL database in place and orphans its `-wal`/`-shm` sidecars. Use the script —
> it stops the service first and cleans the sidecars.

The update is a few seconds of downtime (a restart drops live MCP sessions).

## Alternative: alongside an existing web server

If the droplet already runs a website behind **nginx**, **Apache**, or
another reverse proxy, you don't want a second TLS terminator fighting
for :80/:443. Instead: install only the app + systemd service, leave
your existing server in charge of TLS and auth, and add a vhost (or
location) that proxies to `127.0.0.1:8000`.

**App side** — bootstrap with `MCP_SKIP_CADDY=1`:

```bash
curl -fsSL https://raw.githubusercontent.com/jet52/ndcourts-mcp/main/deploy/bootstrap.sh \
  | MCP_SKIP_CADDY=1 bash
```

This runs sections 1–3 only: swap, user, app, database, systemd unit.
No Caddy, no Caddyfile, no fail2ban-for-Caddy. The service binds
`127.0.0.1:8000` — invisible from the public internet until you
reverse-proxy it.

**Front-end side — Apache.** A drop-in vhost template lives at
[`deploy/mcp-apache.conf`](mcp-apache.conf); its header comments cover
the full install (enable modules, create htpasswd, render the file with
`sed`, issue the cert with `certbot certonly --apache`). The template
guards its `:443` block with `<IfFile>` so Apache starts cleanly before
the cert exists. It runs as an independent vhost on a dedicated
subdomain, so your existing site is untouched.

**Front-end side — nginx.** The same idea with nginx is roughly:

```nginx
server {
    listen 443 ssl http2;
    server_name mcp.yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/mcp.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.yourdomain.com/privkey.pem;

    auth_basic           "ndcourts MCP";
    auth_basic_user_file /etc/nginx/mcp.htpasswd;

    location / {
        proxy_pass       http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_buffering  off;            # don't buffer SSE
        proxy_read_timeout 120s;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

`certbot --nginx -d mcp.yourdomain.com` issues the cert.

**fail2ban — Apache.** Apache's built-in `apache-auth` filter recognises
failed Basic Auth attempts in the per-vhost error log:

```ini
# /etc/fail2ban/jail.d/apache-mcp.conf
[apache-mcp]
enabled  = true
filter   = apache-auth
port     = http,https
logpath  = /var/log/apache2/mcp.yourdomain.com-error.log
maxretry = 5
findtime = 5m
bantime  = 1h
```

**fail2ban — nginx.** Equivalent jail using `nginx-http-auth`:

```ini
# /etc/fail2ban/jail.d/nginx-mcp.conf
[nginx-mcp]
enabled  = true
filter   = nginx-http-auth
port     = http,https
logpath  = /var/log/nginx/error.log
maxretry = 5
findtime = 5m
bantime  = 1h
```

**Path-mount vs. subdomain.** A subdomain (`mcp.yourdomain.com`) is the
clean default: independent vhost, independent cert, independent auth, no
risk of colliding with the parent site's routing. Path-mounting (e.g.
`yourdomain.com/mcp`) saves you a DNS record and a cert at the cost of
splicing the proxy block into the parent vhost — workable, but watch out
for rewrite rules that catch `/mcp` and for SSE buffering imposed by the
parent site's config.

## Notes

- **TLS is mandatory** — Basic Auth credentials ride every request; Caddy
  provides it automatically.
- **Rate limit is your main DoS guard**: full-text/boolean search is the
  costliest path. Keep the limit generous enough for real sessions but low
  enough to blunt a flood.
- **Revoking access** = remove a user's line from `basic_auth` and
  `systemctl reload caddy`.
- For stronger protection you can front Caddy with Cloudflare (free tier:
  DDoS/bot/rate rules, hides origin IP) — but its proxy buffering/100s
  timeout can interfere with MCP's SSE streaming, so test before relying on
  it. Going direct to Caddy avoids that question.
