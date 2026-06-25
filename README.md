# ndcourts-mcp

A Model Context Protocol (MCP) server for North Dakota Supreme Court
opinions, 1890–present (plus a small number of North Dakota Court of
Appeals decisions). Built on SQLite with FTS5 full-text search and
served via [FastMCP](https://github.com/jlowin/fastmcp). Includes a web
opinion browser with multi-source diff/merge tools.

The opinions corpus currently contains **~19,800 opinions** with **114,000+
citation links** between them, with every correction recorded in an
auditable, revertible changelog. Where the court's own print contains an
apparent typo, the text is preserved verbatim and the case is recorded in a
shipped `print_anomalies` table (with the apparent intended reading and
evidence); the citation graph resolves those cites to the intended case.

It also serves North Dakota **primary law** — the Constitution (a point-in-time
layer spanning 1889–present), N.D.C.C. statutes, court rules, and
the Administrative Code — from separate per-corpus databases. See
[Primary law](#primary-law-constitution-court-rules-ndcc-statutes-admin-code)
below for what each database contains.

This is a working tool, not an authoritative text. See
[`NOTICE.md`](NOTICE.md) for sources, redistribution scope, and
attribution; see [`TODO-validation.md`](TODO-validation.md) for the
current state of data validation.

To install it, jump to [Quick start](#quick-start) below.

---

## MCP tools exposed

| Tool                  | Purpose                                                                         |
|-----------------------|---------------------------------------------------------------------------------|
| `lookup_opinion`      | Retrieve an opinion by any citation (neutral, N.W.2d, N.W.)                     |
| `get_opinion_text`    | Read opinion text in paginated chunks                                           |
| `search_opinions`     | Full-text search with date/author filters                                       |
| `list_opinions_by_date` | Browse opinions by date range                                                 |
| `get_database_stats`  | Corpus summary, source breakdown, quality stats, provenance                     |
| `justice_info`        | Voting record for a case, or aggregate stats for a justice                      |
| `search_by_case_type` | Filter by case type (criminal, civil, etc.)                                     |
| `get_citing_opinions` | Find opinions that cite a given opinion                                         |
| `verify_citation`     | Confirm a cite/case name and return its canonical form + Redbook-ordered cites; flags name drift |
| `get_parallel_citations` | Return a case's full parallel-cite set (synthetic IDs bracketed separately)  |
| `verify_quotation`    | Confirm a quoted passage is verbatim (typography-tolerant) and return the pinpoint ¶ |
| `get_pinpoint`        | Resolve a paragraph number to its text, or a quote to the ¶ it lives in          |
| `check_treatment`     | Citator: citing opinions with citing-sentence context + a conservative, non-authoritative treatment signal |
| `get_cited_authorities` | Outbound authorities a case relies on (cases, statutes, rules, constitution), grouped with source links |
| `case_summary`        | One-call bench-memo front matter: cites, panel, voting, disposition, ¶ count, syllabus points |
| `get_subsequent_history` | Related opinions sharing the docket (rehearings, supplemental, companions)   |
| `authoring_justice_on_issue` | A justice's authored opinions matching an issue (predictive bench-memo signal) |
| `search_boolean`      | Westlaw-style Boolean/proximity search (`&` `\|` `%` `/N` `/s` `/p` `!`), translated to FTS5 |
| `search_faceted`      | Filter by date, author, case type, disposition, dissent/concurrence, unanimity (+ optional full text) |
| `find_opinions_construing` | Every opinion citing an N.D.C.C. section or court rule, with the official source link |
| `more_like_this`      | Doctrinally similar opinions (hybrid co-citation + keyword ranking)             |
| `detect_overruled_in_draft` | Scan a draft's cited cases through the citator; flag possible negative treatment (with citing context) |

### Primary law (Constitution, court rules, N.D.C.C. statutes, Admin. Code)

Beyond opinions, the server serves North Dakota primary law from separate
per-corpus SQLite databases, each `ATTACH`-ed onto the opinions connection at
startup (the server serves whatever corpus DBs are present). All use a shared
point-in-time *versioned-provision* schema, so `lookup_authority` accepts an
`as_of_date` to return a provision's text as it stood on a given date.

| Database | Corpus | Contents (approx.) |
|----------|--------|--------------------|
| `opinions.db`     | ND Supreme Court opinions (+ some Court of Appeals) | ~19,800 opinions, 114,000+ citation links, 1890–present |
| `constitution.db` | ND Constitution | ~496 provisions / 774 dated versions, **point-in-time across the full 1889–present span**: a modern article/§ layer (1981–present, with the 1981/1986/1997 article reorganizations and post-1981 amendments reconstructed) + a historical layer in the original 1889 numbering (§§ 1–217 + Schedule + amendment articles, in force 1889–1980), plus the amendment chronology |
| `statutes.db`     | N.D.C.C. (statutes) | ~29,100 Century Code sections |
| `rules.db`        | ND court rules | ~650 rule provisions |
| `admincode.db`    | ND Administrative Code | ~13,800 provisions |

Each ships as its own GitHub release asset (`<name>.db.zip` + `.sha256`) — see
[Quick start](#quick-start) to install them locally and `deploy/SETUP.md` for the
server-side multi-corpus delivery. Both constitutional layers are
`as_of_date`-queryable: the modern layer by its article/§ citation (e.g.
`lookup_authority("N.D. Const. art. VIII, § 6", as_of_date="1990-01-01")`) and the
historical layer by its original 1889 citation (e.g. `lookup_authority("N.D.
Const. § 82", as_of_date="1945-01-01")`); the two numbering schemes are not yet
cross-linked. The primary-law corpora are newer and less validated than the opinions corpus —
see [`TODO-primarylaw.md`](TODO-primarylaw.md).

| Tool                  | Purpose                                                                         |
|-----------------------|---------------------------------------------------------------------------------|
| `lookup_authority`    | Text of a constitutional / rule / statute / admin-code provision (with `as_of_date` for the version in force) |
| `search_authority`    | Full-text search across the primary-law corpora                                 |
| `get_authority_history` | Amendment / version history of a provision                                    |
| `constitutional_amendments` | The ND Constitution's amendment chronology                                |

See [Quick start](#quick-start) to install the server and [Connecting to
Claude](#connecting-to-claude) to wire it into an MCP client.

---

## What's in the database

Counts below are as of 2026-06-25 (v1.1.0); rerun
`sqlite3 opinions.db "SELECT COUNT(*) FROM opinions"` to get the live total
(~19,793, of which 44 are North Dakota Court of Appeals decisions and the
rest North Dakota Supreme Court).

The "primary text source" is the source whose text is stored in
`text_content`; other sources for the same opinion are recorded in
`opinion_sources` for cross-checking.

| Era         | Opinions | Primary text source | Notes |
|-------------|----------|---------------------|-------|
| 1890–1952   | ~6,520   | Bound N.D. Reports (vols 1–79, ~5,700); CourtListener N.W./N.W.2d OCR for the rest | court-authored "Syllabus by the Court" recovered from the bound reports |
| 1953–1996   | ~6,070   | Court-sourced archive.ndcourts.gov (N.W.2d index, ~vol 139+ ≈ 1966 on, ~4,800) and court text from bound volumes; CourtListener N.W.2d OCR for the residual pre-~1965 slice (~1,200) | incremental validation of the residual is ongoing (see TODO-validation.md) |
| 1997–2019   | ~5,620   | ndcourts.gov | archive.ndcourts.gov and CourtListener N.W.2d cross-recorded |
| 2020–present| ~1,585   | ndcourts.gov | N.W.2d where available |

See [`NOTICE.md`](NOTICE.md) for what each source contributes and what is
and isn't redistributed in `text_content`. See
[`TODO-validation.md`](TODO-validation.md) for known data-quality gaps and
the current validation roadmap.

---

## Web opinion browser

The FastAPI app at `http://localhost:8765` provides:

- A sortable opinion table (date, author, citations, quality score, cited-by count)
- A reader pane with opinion text, voting record, citing opinions, and side-by-side multi-source comparison
- A meld-style diff/merge tool for source comparison and deduplication
- Quality filters, a duplicate-review queue, and a flag system
- Keyboard navigation (vim-style `j`/`k`, `Tab` for hunks, `Space` to toggle)

---

## Quick start

### The easy way: let Claude do it

If you're already a Claude user, the simplest install is to ask Claude to
do it for you. Paste the prompt below into **Claude Code** (CLI),
**Claude Desktop** (Mac/Windows), or **Claude on the web** (claude.ai).
Claude will read this repository's `README.md` and `NOTICE.md`, detect
your platform, walk you through the steps, and — if running in an
environment with shell access (Claude Code, or Claude Desktop with
appropriate MCP servers) — run them for you. After install it will add
the server to your Claude MCP config and verify it works.

> Please help me install the `ndcourts-mcp` server from
> `https://github.com/jet52/ndlaw` on my computer. Read the
> repository's `README.md` and `NOTICE.md` first so you understand what
> it is and what it redistributes. Then walk me through (or run for me,
> if you can) the install steps for my platform, download the latest
> `opinions.db` release asset, smoke-test it, and add the server to my
> Claude MCP config. Stop and ask me before any step that needs a
> decision.

If you'd rather do it by hand, the manual instructions follow.

### 1. Prerequisites — all platforms

- **Python 3.12 or newer**
- **git**
- ~1 GB of free disk space (for the database)
- An MCP-capable client (e.g. Claude Desktop, Claude Code) — optional, only
  needed if you want LLM integration

### 2. Install the code and database

Pick your platform. The commands install [`uv`](https://docs.astral.sh/uv/),
clone the repo, download the latest release of the database, and install
the Python dependencies.

#### Windows (PowerShell)

```powershell
# Install uv (a fast Python package manager) — skip if already installed
irm https://astral.sh/uv/install.ps1 | iex

git clone https://github.com/jet52/ndlaw.git
cd ndcourts-mcp

# Download + extract every database release asset (opinions + primary-law corpora).
# The corpus DBs ship from v0.11.0 on; opinions.db is the only one in older releases.
foreach ($db in "opinions","constitution","statutes","rules","admincode") {
  Invoke-WebRequest `
    -Uri "https://github.com/jet52/ndlaw/releases/latest/download/$db.db.zip" `
    -OutFile "$db.db.zip"
  Expand-Archive "$db.db.zip" -DestinationPath . -Force
  Remove-Item "$db.db.zip"
}

uv sync
```

#### macOS

```bash
# Install uv — skip if already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/jet52/ndlaw.git
cd ndcourts-mcp

# Download + extract every database release asset (opinions + primary-law corpora).
# The corpus DBs ship from v0.11.0 on; opinions.db is the only one in older releases.
for db in opinions constitution statutes rules admincode; do
  curl -LO "https://github.com/jet52/ndlaw/releases/latest/download/$db.db.zip"
  unzip -o "$db.db.zip" && rm "$db.db.zip"
done

uv sync
```

#### Linux

```bash
# Install uv — skip if already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/jet52/ndlaw.git
cd ndcourts-mcp

# Download + extract every database release asset (opinions + primary-law corpora).
# The corpus DBs ship from v0.11.0 on; opinions.db is the only one in older releases.
for db in opinions constitution statutes rules admincode; do
  curl -LO "https://github.com/jet52/ndlaw/releases/latest/download/$db.db.zip"
  unzip -o "$db.db.zip" && rm "$db.db.zip"
done

uv sync
```

### 3. Smoke test

Confirm the database is wired correctly:

```bash
sqlite3 opinions.db "SELECT COUNT(*) FROM opinions"          # ~19,800
# Primary-law corpora (if you downloaded them):
sqlite3 constitution.db "SELECT COUNT(*) FROM provisions"    # ~496
sqlite3 statutes.db     "SELECT COUNT(*) FROM provisions"    # ~29,100
```

### Updating to a newer database release

When a new database release is published, replace the local copy:

```bash
# macOS / Linux — refresh every database (or list just the ones you use)
for db in opinions constitution statutes rules admincode; do
  rm -f "$db.db"
  curl -LO "https://github.com/jet52/ndlaw/releases/latest/download/$db.db.zip"
  unzip -o "$db.db.zip" && rm "$db.db.zip"
done
```

```powershell
# Windows PowerShell
foreach ($db in "opinions","constitution","statutes","rules","admincode") {
  Remove-Item "$db.db" -ErrorAction SilentlyContinue
  Invoke-WebRequest `
    -Uri "https://github.com/jet52/ndlaw/releases/latest/download/$db.db.zip" `
    -OutFile "$db.db.zip"
  Expand-Archive "$db.db.zip" -DestinationPath . -Force
  Remove-Item "$db.db.zip"
}
```

Then `git pull` to pick up any code changes since the release was cut.

### 4. Run

**MCP server (stdio mode, for Claude Desktop / Claude Code):**

```bash
uv run ndcourts-mcp
```

**Web browser (FastAPI app on localhost):**

```bash
uv run ndcourts-web
# Then open http://localhost:8765 in a browser
```

For read-only mode (no edits via the web UI):

```bash
# macOS / Linux
NDCOURTS_READONLY=1 uv run ndcourts-web
```

```powershell
# Windows PowerShell
$env:NDCOURTS_READONLY=1; uv run ndcourts-web
```

---

## Connecting to Claude

The server can run under any MCP client. The two most common are Claude
Code (CLI, all platforms) and Claude Desktop (Mac and Windows only — no
Linux build is shipped today).

Throughout the snippets below, replace `/absolute/path/to/ndlaw`
with the full path to your cloned repo. On Windows you can use forward
slashes in JSON strings (`C:/Users/you/ndlaw`) — they work fine and
avoid double-backslash escaping.

### Claude Code (Windows, macOS, Linux)

One-liner from any directory:

```bash
claude mcp add ndlaw -- uv --directory /absolute/path/to/ndlaw run ndcourts-mcp
```

This stores the server in your user-level Claude Code config and makes it
available in every project. Restart any active Claude Code session and the
`ndcourts` server's tools will be available.

Alternative: a project-scoped `.mcp.json` in any project where you want
ndcourts available. Create the file with:

```json
{
  "mcpServers": {
    "ndlaw": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/ndlaw",
               "run", "ndcourts-mcp"]
    }
  }
}
```

### Claude Desktop (macOS)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ndlaw": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/ndlaw",
               "run", "ndcourts-mcp"]
    }
  }
}
```

Then quit and restart Claude Desktop (Cmd-Q, not just close the window).

### Claude Desktop (Windows)

Edit `%APPDATA%\Claude\claude_desktop_config.json`. Same JSON shape, but
specify the absolute paths to both `uv` and your repo. If `uv` is on your
PATH (it is by default after the install script), `"command": "uv"` works;
otherwise use the full path, e.g.
`"C:/Users/you/.local/bin/uv.exe"`.

```json
{
  "mcpServers": {
    "ndlaw": {
      "command": "uv",
      "args": ["--directory", "C:/Users/you/ndlaw",
               "run", "ndcourts-mcp"]
    }
  }
}
```

Then quit and restart Claude Desktop from the system tray.

### Linux

Claude Desktop is not available on Linux. Use Claude Code (above).

### Verifying the connection

Once connected, try a prompt like:

> Use ndcourts to look up *State v. Boger*, 2021 ND 152.

The tool call should return the case metadata and (with `include_text=true`)
the opinion text. For the full set of tools, see the
[MCP tools exposed](#mcp-tools-exposed) table near the top.

---

## Remote / team deployment

By default the server speaks **stdio** — each user runs their own copy and
their MCP client launches it as a subprocess (the configs above). To serve a
whole team from one host instead, the same server can run over **Streamable
HTTP**. The opinion data is public (CC0), so the goal of auth here is access
control, not secrecy; the recommended posture is **work-network / VPN-only
with a bearer token**, with TLS and the token check handled by a reverse
proxy in front of the app.

The only thing the app itself needs is three environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `NDCOURTS_TRANSPORT` | `http` (Streamable HTTP) or `sse`; anything else = stdio | `stdio` |
| `NDCOURTS_HOST` | bind address — keep `127.0.0.1` so only the local proxy can reach it | `127.0.0.1` |
| `NDCOURTS_PORT` | bind port | `8000` |
| `NDCOURTS_DB` | path to `opinions.db` on the server | bundled / app-data |
| `NDCOURTS_CONST_DB` | path to `constitution.db` (ND Constitution corpus) | bundled / app-data |
| `NDCOURTS_NDCC_DB` | path to `statutes.db` (N.D.C.C. corpus) | bundled / app-data |
| `NDCOURTS_RULE_DB` | path to `rules.db` (court-rules corpus) | bundled / app-data |
| `NDCOURTS_ADMIN_DB` | path to `admincode.db` (Admin. Code corpus) | bundled / app-data |

The MCP endpoint is **`/mcp`** (no trailing slash — `/mcp/` issues a 307
redirect, which some clients mishandle on POST).

The tools are read-only (search / lookup / citation analysis); the
data-editing CLIs are not exposed over MCP.

### Run it as a service (systemd)

```ini
# /etc/systemd/system/ndcourts-mcp.service
[Unit]
Description=ndcourts-mcp (Streamable HTTP)
After=network.target

[Service]
User=ndcourts
WorkingDirectory=/srv/ndcourts/ndcourts-mcp
Environment=NDCOURTS_TRANSPORT=http
Environment=NDCOURTS_HOST=127.0.0.1
Environment=NDCOURTS_PORT=8000
Environment=NDCOURTS_DB=/srv/ndcourts/opinions.db
ExecStart=/srv/ndcourts/ndcourts-mcp/.venv/bin/ndcourts-mcp
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Terminate TLS and enforce the token (Caddy)

```
mcp.court.example {
    # only requests carrying the shared token reach the app
    @authorized header Authorization "Bearer REPLACE_WITH_A_LONG_RANDOM_TOKEN"
    handle @authorized {
        reverse_proxy 127.0.0.1:8000
    }
    respond "Unauthorized" 401
}
```

For revocable, per-person access, give each user a distinct token and add a
matching `@authorized` line per token. Restrict the host's firewall so the
proxy port is reachable only from the VPN subnet.

### What each team member runs

```bash
claude mcp add --transport http ndlaw https://mcp.court.example/mcp \
  --header "Authorization: Bearer REPLACE_WITH_A_LONG_RANDOM_TOKEN"
```

(Claude Desktop: add an equivalent `"type": "http"` server with a `headers`
block in `claude_desktop_config.json`.) Users connect to the VPN first, then
the client reaches the server.

### Updating the deployed database

The weekly pipeline regenerates `opinions.db`. Because it is served
read-only, deploying an update is just: copy the new file to the server,
then `systemctl restart ndcourts-mcp`.

### Public VPS test (open internet)

The model above is VPN-only with a bearer token. To instead expose the
server on the public internet for a quick test — with **TLS + HTTP Basic
Auth + rate limiting + fail2ban** — use the ready-to-run Ubuntu templates in
[`deploy/`](deploy/):

- [`deploy/SETUP.md`](deploy/SETUP.md) — step-by-step Ubuntu 22.04/24.04
  walkthrough (system user, `uv` install, database download, systemd, Caddy
  with the rate-limit plugin, `ufw`, SSH hardening, fail2ban, client config).
- [`deploy/Caddyfile`](deploy/Caddyfile) — auto-HTTPS, per-IP `rate_limit`,
  `basic_auth`, and `flush_interval -1` so MCP's SSE streaming isn't buffered.
- [`deploy/ndcourts-mcp.service`](deploy/ndcourts-mcp.service) — hardened
  systemd unit bound to localhost.
- [`deploy/fail2ban/`](deploy/fail2ban/) — filter + jail that ban IPs on
  repeated `401`s.

The data is public (CC0), so this auth is access control and abuse
prevention, not secrecy.

---

## Working on the data

A separate CLI is built into the package for ingesting new opinions,
running quality scans, building citation graphs, and applying validation
batches. See [`BUILD.md`](BUILD.md) for the full rebuild flow and
[`TODO-validation.md`](TODO-validation.md) for the current work-in-progress
list.

| Command                                                          | Purpose                                          |
|------------------------------------------------------------------|--------------------------------------------------|
| `uv run python -m ndcourts_mcp.ingest [--rebuild]`               | Ingest opinions from `~/refs/nd/opin/`           |
| `uv run python -m ndcourts_mcp.merge_nd_metadata`                | Merge ndcourts.gov JSON metadata                 |
| `uv run python -m ndcourts_mcp.cleanup apply`                    | Apply pending corrections                        |
| `uv run python -m ndcourts_mcp.cleanup revert <batch>`           | Revert a correction batch                        |
| `uv run python -m ndcourts_mcp.cite_extract`                     | Extract citations and build cited-by graph       |
| `uv run python -m ndcourts_mcp.quality_scan [--rescan]`          | Score text quality for all opinions              |
| `uv run python -m ndcourts_mcp.dedup_scan`                       | Detect duplicate opinions                        |
| `uv run python -m ndcourts_mcp.audit [--save]`                   | Audit for missing opinions and data gaps         |
| `uv run python -m ndcourts_mcp.multisource_diff`                 | Compare opinions with multiple linked sources    |
| `uv run python -m ndcourts_mcp.invariants`                       | Run integrity invariants over the DB             |
| `uv run python -m ndcourts_mcp.scrape_archive --all --ingest`    | Scrape `archive.ndcourts.gov`                    |

---

## Sources, redistribution scope, and license

Code: dedicated to the public domain under [CC0 1.0 Universal](LICENSE).
Use it however you want.

Data: the opinions database redistributes only the court's own published
work (opinions and court-authored syllabi) plus factual record content
(parties, dates, attorneys, dispositions, citations). See
[`NOTICE.md`](NOTICE.md) for full source attribution to
[CourtListener](https://www.courtlistener.com) (Free Law Project), the
[North Dakota Court System](https://www.ndcourts.gov), and the rules
governing how Westlaw bound-volume entries are used for validation
without redistributing Westlaw editorial content.

---

## Contributing

This corpus is being actively validated toward a goal of two-source
verification for every opinion. If you want to help — running diff audits,
reviewing duplicate candidates, contributing parser fixes, or just trying
the database against your own queries and reporting errors — open an issue
or PR on the GitHub repository.

## Reference files

| File                                          | Purpose                                              |
|-----------------------------------------------|------------------------------------------------------|
| [`BUILD.md`](BUILD.md)                        | Step-by-step database rebuild instructions           |
| [`CHANGELOG-data.md`](CHANGELOG-data.md)      | Log of every correction batch                        |
| [`MISSING_OPINIONS.md`](MISSING_OPINIONS.md)  | Audit report of citation gaps and data anomalies     |
| [`NOTICE.md`](NOTICE.md)                      | Sources, attribution, redistribution scope           |
| [`TODO-validation.md`](TODO-validation.md)    | Roadmap for full corpus validation                   |
| [`TODO-distribution.md`](TODO-distribution.md)| Roadmap for DB distribution and monthly updates      |
| `ndcourts_mcp/justices.py`                    | All 52 elected ND Supreme Court justices since 1889  |
