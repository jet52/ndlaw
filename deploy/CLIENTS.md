# Connecting Claude clients to a remote ndcourts-mcp

The server (see [SETUP.md](SETUP.md)) speaks Streamable HTTP behind
TLS + HTTP Basic Auth. You'll need from the admin:

- **URL** — `https://mcp.example.com/mcp`
- **Username** — assigned to you
- **Password** — shared via a secure channel

## Compatibility

| Client | Supported | How |
|---|---|---|
| Claude Code (CLI, any OS) | yes | `claude mcp add --transport http` |
| Claude Desktop (macOS, Linux, Windows) | yes | `mcp-remote` stdio→HTTP bridge |
| claude.ai web | no | requires OAuth, not Basic Auth |
| Claude iOS / iPad / Android | no | same as web |

The web/mobile clients use Anthropic's Custom Connectors, which speak
MCP-over-OAuth. This server uses Basic Auth, so those clients can't
talk to it today. Adding OAuth is a future-work item.

---

## Claude Code (CLI)

One command — replace the placeholders:

```bash
claude mcp add --transport http ndlaw https://mcp.example.com/mcp \
  --header "Authorization: Basic $(printf '<username>:<password>' | base64)"
```

The base64 is computed locally before being saved. Verify with
`claude mcp list`. Tools appear as `mcp__ndcourts__*` after a session
restart.

**Project-scoped alternative.** If a repo's collaborators should all
use this MCP, add it to a project's `.mcp.json` instead of the user-
level config:

```json
{
  "mcpServers": {
    "ndlaw": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "Authorization": "Basic <base64-of-user:pass>"
      }
    }
  }
}
```

⚠ Don't commit `.mcp.json` with real credentials. Either commit a
template and have each user add their own header locally, or keep the
file untracked.

---

## Claude Desktop — easiest path (.mcpb bundle, any OS)

A pre-built **MCP Bundle** is in the repo at
[`deploy/ndcourts.mcpb`](ndcourts.mcpb) (~2 KB). It contains a
manifest and a tiny Node wrapper that proxies to the remote server.
Works on macOS, Linux, and Windows with one set of instructions.

**For colleagues:**

1. Download the bundle:
   <https://github.com/jet52/ndlaw/raw/main/deploy/ndcourts.mcpb>
2. Double-click it. Claude Desktop opens the install dialog showing
   the extension name and asking for three fields:
   - **Server URL** — paste what the admin sent you
   - **Username** — from the admin
   - **Password** — from the admin (input is masked, stored in the OS
     keychain)
3. Click **Install**. Restart Claude Desktop if it doesn't auto-pick
   the new extension up. Confirm in Settings → Extensions that
   "ND Courts (Supreme Court Opinions)" is enabled.

**Requirements:** Node.js (any recent version). The bundle calls
`npx -y mcp-remote` under the hood, which auto-installs the remote
proxy on first use. If you don't have Node, install via
`brew install node` (macOS) or `winget install OpenJS.NodeJS.LTS`
(Windows).

**Updating / re-installing:** download a newer `.mcpb` from the same
URL and double-click again. Claude Desktop replaces the previous
version in place.

**For the admin (maintaining the bundle):** the source lives at
`deploy/mcpb/`. Edit `manifest.json` or `server/wrapper.js`, bump
the `version` field, run `deploy/mcpb/build.sh`, commit both the
source changes and the rebuilt `deploy/ndcourts.mcpb` together.

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
    "https://mcp.example.com/mcp",
    "--header",
    "Authorization: Basic <base64-of-user:pass>"
  ]
}
```

Generate the base64 once:

- **macOS / Linux:** `printf '<username>:<password>' | base64`
- **Windows PowerShell:** `[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('<username>:<password>'))`

Save, fully quit Claude Desktop (⌘Q on macOS, right-click tray → **Quit**
on Windows — a window-close isn't enough), reopen. Settings → Developer
→ MCP servers should show `ndcourts` connected.

---

## Troubleshooting

- **"Some MCP servers could not be loaded"** on Desktop start: the
  entry shape is wrong. Use the stdio shape above (`command` + `args`).
  `{"type": "http", ...}` is accepted by Claude Code but rejected by
  Claude Desktop.
- **401 Unauthorized** on first request: bad credentials. The base64
  of `<username>:` (empty password) starts with `dXNlcjo=`-style; a
  real cred is longer. Recompute and replace.
- **Hanging on "Connecting…"** for 30+ seconds on first launch: the
  one-time `npx -y mcp-remote` download. Wait it out. If it persists,
  run the command manually in a terminal to see errors:
  ```bash
  npx -y mcp-remote https://mcp.example.com/mcp --header "Authorization: Basic <base64>"
  ```
- **Reachability check** (any OS): `curl -I https://mcp.example.com/mcp`
  should return `401 Unauthorized` with a `WWW-Authenticate: Basic`
  header. Connection refused or timeout = DNS/networking issue, not
  the MCP config.

---

## Revoking access

The admin removes your line from `/etc/apache2/mcp.htpasswd` on the
server and reloads Apache. Your client will start getting 401s on its
next request; remove the entry from your local config when convenient.
