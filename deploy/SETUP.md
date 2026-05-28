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

Files in this dir: `Caddyfile`, `ndcourts-mcp.service`, `fail2ban/`.

## 0. Assumptions

- Ubuntu 22.04 / 24.04, with `sudo`.
- A domain name (e.g. `mcp.yourdomain.com`) with an **A record pointing at
  the VPS IP** — required for automatic Let's Encrypt TLS.
- Replace `mcp.yourdomain.com` and `you@example.com` throughout.

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

Claude Desktop: add an `"type": "http"` server with a `headers` block
carrying the same `Authorization: Basic ...` value.

The endpoint is **`/mcp`** (no trailing slash — `/mcp/` 307-redirects).

## 8. Updating the database

The weekly pipeline regenerates `opinions.db`. To deploy a new copy:

```bash
sudo -u ndcourts bash -lc '
  cd /srv/ndcourts
  curl -L -o opinions.db.zip https://github.com/jet52/ndcourts-mcp/releases/latest/download/opinions.db.zip
  unzip -o opinions.db.zip && rm opinions.db.zip
'
sudo systemctl restart ndcourts-mcp
```

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
