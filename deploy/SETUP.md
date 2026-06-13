# Public VPS deployment (Ubuntu)

Serve `ndcourts-mcp` over Streamable HTTP from an Ubuntu server on the open
internet. The opinion data is public (CC0), so access control here is abuse
prevention, not secrecy. Two access models:

- **Capability URL (recommended)** — no credentials; the endpoint lives at
  an unguessable path (`https://mcp.example.com/<token>/mcp`) and the URL
  itself is what you share. Works with every client including claude.ai
  custom connectors (which don't support Basic Auth). The Apache variant
  below implements this; pair it with the `apache-mcp-*` fail2ban jails
  (junk-ban + per-IP rate cap). See [CLIENTS.md](CLIENTS.md).
- **HTTP Basic Auth** — per-user credentials at the proxy. The Caddy
  walk-through below implements this; claude.ai connectors can't use it.

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
curl -fsSL https://raw.githubusercontent.com/jet52/ndlaw/main/deploy/bootstrap.sh \
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
  git clone https://github.com/jet52/ndlaw.git
  cd ndcourts-mcp
  ~/.local/bin/uv venv
  ~/.local/bin/uv pip install .
'

# download the database release asset (~528 MB zip, ~1.1 GB unzipped)
sudo -u ndcourts bash -lc '
  cd /srv/ndcourts
  curl -L -o opinions.db.zip https://github.com/jet52/ndlaw/releases/latest/download/opinions.db.zip
  unzip -o opinions.db.zip && rm opinions.db.zip
'
```

> The DB directory must stay writable by the `ndcourts` user: SQLite WAL mode
> creates `opinions.db-wal` / `-shm` files next to it even when only reading.

> **Primary-law corpora.** Besides opinions, the server also serves the ND
> Constitution, court rules, N.D.C.C. statutes, and Administrative Code from
> separate per-corpus DBs (`constitution.db`, `rules.db`, `statutes.db`,
> `admincode.db`). These ship as additional release assets and are fetched +
> validated automatically by `deploy/update-db.sh` (and the nightly
> self-update) — see §8. The server's `attach_corpora()` serves whatever corpus
> DBs are present, each placed where the installed package resolves it, so no
> extra config is needed. To pull them on first install, run
> `sudo /srv/ndcourts/ndcourts-mcp/deploy/update-db.sh` once the service is up.

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
claude mcp add --transport http ndlaw https://mcp.yourdomain.com/mcp \
  --header "Authorization: Basic $(printf 'teammate1:thepassword' | base64)"
```

Claude Desktop and other clients: see [CLIENTS.md](CLIENTS.md) for
per-client setup (Claude Code, Claude Desktop on macOS / Linux /
Windows, and notes on the web/mobile clients).

The endpoint is **`/mcp`** (no trailing slash — `/mcp/` 307-redirects).

## 8. Updating the databases

The databases ship as GitHub release assets — `opinions.db.zip` plus one per
primary-law corpus (`constitution.db.zip`, `rules.db.zip`, `statutes.db.zip`,
`admincode.db.zip`), each with a `.sha256`. Updating is a publish-then-pull: cut
a release from your build machine, then have the server pull, validate, and swap.

`deploy/update-db.sh` is multi-corpus, idempotent, and self-healing: `opinions.db`
is required, and each corpus is optional — a corpus whose asset isn't in the
release is skipped (and picked up on a later run once it ships), so new corpora
roll out without a script change. Each corpus DB is placed exactly where the
installed package resolves it, so the server serves it with no unit/env change.

Publishing is the deliberate editorial gate; everything downstream is mechanical
and gated (sha256 verify, `quick_check`, count floor, live `/mcp` probe, rollback).

**One command, from the repo on your build machine:**

```bash
NDCOURTS_SSH=jerod@mcp.YOURDOMAIN.com deploy/push-db.sh
```

This runs `scripts/make_release.sh --publish` (gates on invariants + redistribution
scope + clean tree; zips; sha256s; **pushes the release commit and pins the tag to
it**; creates the `v<version>` GitHub release) and then SSHes in to run
`deploy/self-update.sh` on the server, which pins the code to the new tag,
reinstalls, swaps the DB, restarts, and health-probes.

> **The venv is a non-editable install** (`uv pip install .`, not `-e .`), so a
> `git pull`/`checkout` alone does **not** change the running code — you must
> `uv pip install .` again. `self-update.sh` does this; a bare `update-db.sh`
> does not (it only swaps the DB). If you ever pull code by hand, reinstall:
> `sudo -u ndcourts bash -lc 'cd /srv/ndcourts/ndcourts-mcp && uv pip install .'`
> then `sudo systemctl restart ndcourts-mcp`.

**Server side only** (publishing the release separately, or pulling on the box).
`deploy/update-db.sh` downloads each shipped DB from the latest release,
**verifies its sha256**, validates each staged DB (`PRAGMA quick_check` + a
per-DB row floor), then **stops the service once, swaps all atomically (keeping a
`<db>.bak` each), clears stale
`-wal`/`-shm`, restarts, and runs an end-to-end `/mcp` probe — auto-rolling back
to `.bak` if the probe fails**. Run it as **root** (the `ndcourts` home is not
readable by your login user, so `sudo -u ndcourts` fails its venv preflight):

```bash
sudo /srv/ndcourts/ndcourts-mcp/deploy/update-db.sh --dry-run   # download + validate only
sudo /srv/ndcourts/ndcourts-mcp/deploy/update-db.sh             # validate, swap, health-check
```

> Don't `unzip -o` over the live `opinions.db` by hand: it overwrites an open
> WAL database in place and orphans its `-wal`/`-shm` sidecars. Use the script —
> it stops the service first and cleans the sidecars. `sqlite3` (the CLI) must be
> installed: `sudo apt-get install -y sqlite3`.

The update is a few seconds of downtime (a restart drops live MCP sessions).

## 8a. Optional: scheduled self-update

Let the server poll GitHub nightly and deploy any new release on its own, with
an email on each deploy/rollback. Publishing stays the human gate; the box does
the rest. Components live in `deploy/`: `self-update.sh`, `ndcourts-update.service`,
`ndcourts-update.timer`.

```bash
# 1. systemd units
sudo cp /srv/ndcourts/ndcourts-mcp/deploy/ndcourts-update.{service,timer} /etc/systemd/system/

# 2. (optional) email target — kept out of the repo
echo 'MAIL_TO=you@example.com' | sudo tee /etc/ndcourts-update.env

# 3. seed the marker with the currently-deployed tag so the first run is a no-op
#    until something newer ships
echo "$(curl -fsS -o /dev/null -w '%{url_effective}' -L \
  https://github.com/jet52/ndlaw/releases/latest | sed 's#.*/##')" \
  | sudo tee /srv/ndcourts/.deployed-release

# 4. enable the timer
sudo systemctl daemon-reload
sudo systemctl enable --now ndcourts-update.timer
systemctl list-timers ndcourts-update.timer        # confirm next fire time

# dry test (forces a real check now; no-op if already current):
sudo systemctl start ndcourts-update.service && journalctl -u ndcourts-update -n 20 --no-pager
```

**Email** uses the `sendmail -t` interface, so any MTA works. Lightweight option —
msmtp as the system sendmail, relaying through Gmail with an app password:

```bash
sudo apt-get install -y msmtp msmtp-mta        # provides /usr/sbin/sendmail
# /etc/msmtprc (chmod 600): account with host smtp.gmail.com, port 587, tls on,
# user <you>@gmail.com, password <app-password>, and `aliases /etc/aliases`.
```

Without an MTA, deploys still happen — results just go to journald
(`journalctl -u ndcourts-update`) instead of email.

**Laptop one-command path** (`deploy/push-db.sh`) SSHes in and runs
`sudo self-update.sh`. For that to work non-interactively, give the SSH login
user passwordless sudo for just that script:

```bash
echo 'jerod ALL=(root) NOPASSWD: /srv/ndcourts/ndcourts-mcp/deploy/self-update.sh' \
  | sudo tee /etc/sudoers.d/ndcourts-selfupdate
sudo chmod 440 /etc/sudoers.d/ndcourts-selfupdate
```

> **Scope of autonomy:** auto-deploy runs only *after* you publish a release, and
> the `/mcp` health probe auto-rolls-back the DB on gross failure — but it cannot
> catch subtle data errors. The build-time gates and your pre-publish review remain
> the control for data correctness. Keep `gh release create` a human act. OS/kernel
> patching is a separate track (`unattended-upgrades`).

## Alternative: alongside an existing web server

If the droplet already runs a website behind **nginx**, **Apache**, or
another reverse proxy, you don't want a second TLS terminator fighting
for :80/:443. Instead: install only the app + systemd service, leave
your existing server in charge of TLS and auth, and add a vhost (or
location) that proxies to `127.0.0.1:8000`.

**App side** — bootstrap with `MCP_SKIP_CADDY=1`:

```bash
curl -fsSL https://raw.githubusercontent.com/jet52/ndlaw/main/deploy/bootstrap.sh \
  | MCP_SKIP_CADDY=1 bash
```

This runs sections 1–3 only: swap, user, app, database, systemd unit.
No Caddy, no Caddyfile, no fail2ban-for-Caddy. The service binds
`127.0.0.1:8000` — invisible from the public internet until you
reverse-proxy it.

**Front-end side — Apache.** A drop-in vhost template lives at
[`deploy/mcp-apache.conf`](mcp-apache.conf); its header comments cover
the full install (generate the token, render the file with `sed`,
enable modules, issue the cert with `certbot certonly --apache`). It
uses the capability-URL model: only `/<token>/…` proxies to the app,
everything else is denied at Apache. Install the matching fail2ban
jails from [`deploy/fail2ban/jail.d/apache-mcp.conf`](fail2ban/jail.d/apache-mcp.conf)
(junk-ban for scanners + a per-IP rate cap on real traffic). The
template guards its `:443` block with `<IfFile>` so Apache starts
cleanly before the cert exists. It runs as an independent vhost on a
dedicated subdomain, so your existing site is untouched.

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
