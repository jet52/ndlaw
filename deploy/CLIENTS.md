# Connecting Claude clients to a remote ndcourts-mcp

The server (see [SETUP.md](SETUP.md)) speaks Streamable HTTP behind TLS.
Access is by **capability URL**: the URL the admin sends you contains an
unguessable path segment, and that segment is the only credential. You
need exactly one thing from the admin:

- **URL** — `https://mcp.example.com/<token>/mcp`

Treat the URL like a password: don't post it publicly, don't commit it
to a repository. (The underlying data is public CC0 — the token exists
to keep bots and scrapers off a small shared server, not to protect the
content.)

## Compatibility

| Client | Supported | How |
|---|---|---|
| Claude Code (CLI, any OS) | yes | `claude mcp add --transport http` |
| Claude Desktop (macOS, Linux, Windows) | yes | `.mcpb` bundle or `mcp-remote` bridge |
| claude.ai web | yes | Settings → Connectors → Add custom connector (paste URL) |
| Claude iOS / iPad / Android | yes | connectors added on web are available on mobile |

---

## Claude Code (CLI)

One command — paste the URL the admin sent:

```bash
claude mcp add --transport http ndlaw https://mcp.example.com/<token>/mcp
```

Verify with `claude mcp list`. Tools appear as `mcp__ndlaw__*` after a
session restart.

**Project-scoped alternative.** If a repo's collaborators should all
use this MCP, add it to the project's `.mcp.json`:

```json
{
  "mcpServers": {
    "ndlaw": {
      "type": "http",
      "url": "https://mcp.example.com/<token>/mcp"
    }
  }
}
```

⚠ Only commit `.mcp.json` with the real URL to a **private** repo —
the URL is the credential.

---

## claude.ai web (and mobile)

Settings → **Connectors** → **Add custom connector** → paste the URL →
Add. The connector then shows up in the tools menu in chats, and on the
mobile apps as well. No OAuth flow appears because the server doesn't
require one.

---

## Claude Desktop — easiest path (.mcpb bundle, any OS)

A pre-built **MCP Bundle** is in the repo at
[`deploy/ndlaw.mcpb`](ndlaw.mcpb). It contains a manifest and a tiny
Node wrapper that proxies to the remote server. Works on macOS, Linux,
and Windows with one set of instructions.

**For colleagues:**

1. Download the bundle:
   <https://github.com/jet52/ndlaw/raw/main/deploy/ndlaw.mcpb>
2. Double-click it. Claude Desktop opens the install dialog asking for
   one field:
   - **Server URL** — paste what the admin sent you
3. Click **Install**. Restart Claude Desktop if it doesn't auto-pick
   the new extension up. Confirm in Settings → Extensions that
   "North Dakota Law (primary law)" is enabled.

**Requirements:** Node.js (any recent version). The bundle ships
`mcp-remote` inside it. If you don't have Node, install via
`brew install node` (macOS) or `winget install OpenJS.NodeJS.LTS`
(Windows).

**Updating / re-installing:** download a newer `.mcpb` from the same
URL and double-click again. Claude Desktop replaces the previous
version in place.

**For the admin (maintaining the bundle):** the source lives at
`deploy/mcpb/`. Edit `manifest.json` or `server/wrapper.js`, bump
the `version` field, run `deploy/mcpb/build.sh`, commit both the
source changes and the rebuilt `deploy/ndlaw.mcpb` together.

---

## Claude Desktop — manual config (.mcpb alternative)

If the `.mcpb` route doesn't fit (no Node, locked-down machine,
custom config required), edit the config JSON directly. Claude
Desktop's MCP loader only accepts **stdio** servers, so we proxy
through `mcp-remote` (an npx package that runs locally and forwards
to the HTTP endpoint).

**Prerequisites:** Node.js (`node --version` to confirm). Install via
`brew install node` (macOS), your package manager (Linux), or
`winget install OpenJS.NodeJS.LTS` (Windows).

**Config file location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Open via Settings → Developer → **Edit Config**, or edit directly.
Add the following inside `mcpServers` (preserve anything already there):

```json
"ndlaw": {
  "command": "npx",
  "args": [
    "-y",
    "mcp-remote",
    "https://mcp.example.com/<token>/mcp"
  ]
}
```

Save, fully quit Claude Desktop (⌘Q on macOS, right-click tray → **Quit**
on Windows — a window-close isn't enough), reopen. Settings → Developer
→ MCP servers should show `ndlaw` connected.

---

## Troubleshooting

- **403 Forbidden** on every request: the token segment of the URL is
  missing or mistyped. Re-copy the exact URL from the admin — every
  character of the path matters.
- **"Some MCP servers could not be loaded"** on Desktop start: the
  entry shape is wrong. Use the stdio shape above (`command` + `args`).
  `{"type": "http", ...}` is accepted by Claude Code but rejected by
  Claude Desktop.
- **Hanging on "Connecting…"** for 30+ seconds on first launch: the
  one-time `npx -y mcp-remote` download. Wait it out. If it persists,
  run the command manually in a terminal to see errors:
  ```bash
  npx -y mcp-remote https://mcp.example.com/<token>/mcp
  ```
- **Reachability check** (any OS): `curl -I https://mcp.example.com/`
  should return `403 Forbidden` (the server is up; you're outside the
  token path — that's expected). Connection refused or timeout = DNS/
  networking issue, not the MCP config.
- **Suddenly banned?** Repeated requests to wrong paths (or more than
  ~100 requests/minute from one IP) trigger a temporary fail2ban ban
  (10 minutes for rate, 6 hours for wrong-path junk). Fix the URL,
  wait it out, or ask the admin to `fail2ban-client set <jail> unbanip <IP>`.

---

## Revoking access

There are no per-user credentials. To revoke, the admin changes the
token in the Apache vhost, reloads Apache, and re-shares the new URL
with everyone who should still have access. Old URLs start returning
403 immediately.
