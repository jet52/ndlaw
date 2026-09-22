# ndlaw

A Model Context Protocol (MCP) server for North Dakota Supreme Court
opinions, 1889–present (plus a small number of North Dakota Court of
Appeals decisions). Coverage is complete since statehood (November 2,
1889); the court issued its first opinions in 1890. Built on SQLite with
FTS5 full-text search and served via
[FastMCP](https://github.com/jlowin/fastmcp).

The opinions corpus currently contains **<!-- COUNT:opinions -->20,107<!-- /COUNT --> opinions** with **<!-- COUNT:citelinks -->127,217<!-- /COUNT --> citation links** between them, with per-release corrections summarized in the
release notes. Where the court's own print contains an
apparent typo, the text is preserved verbatim; where that typo is in a
citation, the citation graph still resolves it to the case the court meant.

It also serves North Dakota **primary law** — the Constitution (a point-in-time
layer spanning 1889–present), N.D.C.C. statutes, court rules, and
the Administrative Code — from separate per-corpus databases. See
[Primary law](#primary-law-constitution-court-rules-ndcc-statutes-admin-code)
below for what each database contains.

> **Not an official court product.** This is an independent, unofficial
> project. It is not published, endorsed, or maintained by the North Dakota
> Supreme Court, the North Dakota Court System, or any agency of the State of
> North Dakota, and nothing here is an official version of any opinion,
> statute, rule, or regulation. The official sources are the court's own
> publications ([ndcourts.gov](https://www.ndcourts.gov)) and the Legislative
> Branch's ([ndlegis.gov](https://ndlegis.gov)); verify there before relying
> on or filing anything.
>
> **No claim to official government works.** The opinions, statutes, rules,
> and regulations reproduced here are works of North Dakota's government,
> reproduced as public documents; this project claims no rights in them. What
> the project adds — the compilation, corrections, citation graph, and
> software — is released under CC0 (see [`NOTICE.md`](NOTICE.md)).

This is a working tool, not an authoritative text. See
[`NOTICE.md`](NOTICE.md) for sources, redistribution scope, and
attribution.

To install it, jump to [Quick start](#quick-start) below.

---

## MCP tools exposed

| Tool                  | Purpose                                                                         |
|-----------------------|---------------------------------------------------------------------------------|
| `lookup_opinion`      | Retrieve an opinion by any citation (neutral, N.W.2d, N.W.)                     |
| `get_opinion_text`    | Read opinion text in paginated chunks                                           |
| `search_opinions`     | Full-text search with date/author filters                                       |
| `list_opinions_by_date` | Browse opinions by date range                                                 |
| `get_database_stats`  | Corpus summary: totals, date range, coverage by decade, most-published authors  |
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
| `search_boolean`      | Boolean/proximity search (`&` `\|` `%` `/N` `/s` `/p` `!`), translated to FTS5 |
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
| `opinions.db`     | ND Supreme Court opinions (+ some Court of Appeals) | <!-- COUNT:opinions -->20,107<!-- /COUNT --> opinions, <!-- COUNT:citelinks -->127,217<!-- /COUNT --> citation links, 1889–present |
| `constitution.db` | ND Constitution | ~496 provisions / 774 dated versions, **point-in-time across the full 1889–present span**: a modern article/§ layer (1981–present, with the 1981/1986/1997 article reorganizations and post-1981 amendments reconstructed) + a historical layer in the original 1889 numbering (§§ 1–217 + Schedule + amendment articles, in force 1889–1980), plus the amendment chronology |
| `statutes.db`     | N.D.C.C. (statutes) | ~29,100 Century Code sections |
| `rules.db`        | ND court rules | ~650 rule provisions |
| `admincode.db`    | ND Administrative Code | ~13,800 provisions |
| `ag_opinions.db`  | ND Attorney General opinions | ~6,750 published opinions, 1942–present, cross-linked to the statutes/Constitution/rules/admin/opinions they cite (~35,000 citation links) |

Each ships as its own GitHub release asset (`<name>.db.zip` + `.sha256`) — see
[Quick start](#quick-start) to install them locally and `deploy/SETUP.md` for the
server-side multi-corpus delivery. Both constitutional layers are
`as_of_date`-queryable: the modern layer by its article/§ citation (e.g.
`lookup_authority("N.D. Const. art. VIII, § 6", as_of_date="1990-01-01")`) and the
historical layer by its original 1889 citation (e.g. `lookup_authority("N.D.
Const. § 82", as_of_date="1945-01-01")`). The two numbering schemes are
cross-linked through the official 1981 disposition tables (NDCC Replacement
Vol. 13): a modern cite at a pre-1981 date returns its original-section
predecessor, and an original §-cite at a post-1981 date returns its modern
successor — each answer carries provenance (`requested_citation`,
`returned_provision`, `relation`, a source note), and lookups that would land
past a wholesale article replacement (1982/1986/1997) say so rather than
implying content continuity. `get_authority_history` merges the pre- and
post-1981 amendment chronologies into one timeline per provision. The
primary-law corpora are newer and less exhaustively validated than the
opinions corpus, though the constitution layer has now been verified
section-by-section against the official annotated apparatus and every usable
printed compilation 1889–1989.

| Tool                  | Purpose                                                                         |
|-----------------------|---------------------------------------------------------------------------------|
| `lookup_authority`    | Text of a constitutional / rule / statute / admin-code provision (with `as_of_date` for the version in force) |
| `search_authority`    | Full-text search across the primary-law corpora                                 |
| `get_authority_history` | Amendment / version history of a provision                                    |
| `constitutional_amendments` | The ND Constitution's amendment chronology                                |
| `search_ag_opinions`  | Full-text search across ND Attorney General opinions (1942–present)             |
| `lookup_ag_opinion`   | An AG opinion by number (e.g. `2015-L-12`) + the authorities it cites           |
| `get_ag_opinions_citing` | AG opinions that cite a given statute / constitutional / rule / case authority |
| `get_court_opinions_citing_ag` | Court opinions that cite a given AG opinion (the inbound direction)              |

See [Quick start](#quick-start) to install the server and [Connecting to
Claude](#connecting-to-claude) to wire it into an MCP client.

---

## What's in the database

Counts below are as of 2026-08-21; the corpus total is
**<!-- COUNT:opinions -->20,107<!-- /COUNT --> opinions** (of which 80 are
North Dakota Court of Appeals decisions and the rest North Dakota Supreme
Court) — rerun `sqlite3 opinions.db "SELECT COUNT(*) FROM opinions"` for
the live total.

| Era          | Opinions | Notes |
|--------------|----------|-------|
| 1890–1952    | ~6,530   | includes the court-authored "Syllabus by the Court" that accompanies opinions of this era |
| 1953–1996    | ~6,300   | validation of a residual slice of the earliest N.W.2d years is ongoing |
| 1997–2019    | ~5,650   | neutral-citation era (`2019 ND 54`) |
| 2020–present | ~1,630   | |

The database ships the court's text and the citation graph over it. It does
not ship the development record behind that text — the correction history,
the working copies collated to produce it, or the pipeline's own bookkeeping.
Those are maintained separately and are not needed to read an opinion or to
verify a citation. See [`NOTICE.md`](NOTICE.md) for what is and isn't
redistributed in `text_content`, and the release notes for the corrections in
each published version.

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

> Please help me install the `ndlaw` server from
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
cd ndlaw

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
cd ndlaw

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
cd ndlaw

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
sqlite3 opinions.db "SELECT COUNT(*) FROM opinions"          # exact count
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
uv run ndlaw-mcp
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
claude mcp add ndlaw -- uv --directory /absolute/path/to/ndlaw run ndlaw-mcp
```

This stores the server in your user-level Claude Code config and makes it
available in every project. Restart any active Claude Code session and the
`ndlaw` server's tools will be available.

Alternative: a project-scoped `.mcp.json` in any project where you want
ndlaw available. Create the file with:

```json
{
  "mcpServers": {
    "ndlaw": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/ndlaw",
               "run", "ndlaw-mcp"]
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
               "run", "ndlaw-mcp"]
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
               "run", "ndlaw-mcp"]
    }
  }
}
```

Then quit and restart Claude Desktop from the system tray.

### Linux

Claude Desktop is not available on Linux. Use Claude Code (above).

### Verifying the connection

Once connected, try a prompt like:

> Use ndlaw to look up *State v. Boger*, 2021 ND 152.

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
| `NDLAW_TRANSPORT` | `http` (Streamable HTTP) or `sse`; anything else = stdio | `stdio` |
| `NDLAW_HOST` | bind address — keep `127.0.0.1` so only the local proxy can reach it | `127.0.0.1` |
| `NDLAW_PORT` | bind port | `8000` |
| `NDLAW_DB` | path to `opinions.db` on the server | bundled / app-data |
| `NDLAW_CONST_DB` | path to `constitution.db` (ND Constitution corpus) | bundled / app-data |
| `NDLAW_NDCC_DB` | path to `statutes.db` (N.D.C.C. corpus) | bundled / app-data |
| `NDLAW_RULE_DB` | path to `rules.db` (court-rules corpus) | bundled / app-data |
| `NDLAW_ADMIN_DB` | path to `admincode.db` (Admin. Code corpus) | bundled / app-data |
| `NDLAW_AG_DB` | path to `ag_opinions.db` (Attorney General opinions) | bundled / app-data |

The MCP endpoint is **`/mcp`** (no trailing slash — `/mcp/` issues a 307
redirect, which some clients mishandle on POST).

The tools are read-only (search / lookup / citation analysis); the
data-editing CLIs are not exposed over MCP.

### Run it as a service (systemd)

```ini
# /etc/systemd/system/ndlaw-mcp.service
[Unit]
Description=ndlaw-mcp (Streamable HTTP)
After=network.target

[Service]
User=ndcourts
WorkingDirectory=/srv/ndcourts/ndlaw-mcp
Environment=NDLAW_TRANSPORT=http
Environment=NDLAW_HOST=127.0.0.1
Environment=NDLAW_PORT=8000
Environment=NDLAW_DB=/srv/ndcourts/opinions.db
ExecStart=/srv/ndcourts/ndlaw-mcp/.venv/bin/ndlaw-mcp
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
then `systemctl restart ndlaw-mcp`.

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
- [`deploy/ndlaw-mcp.service`](deploy/ndlaw-mcp.service) — hardened
  systemd unit bound to localhost.
- [`deploy/fail2ban/`](deploy/fail2ban/) — filter + jail that ban IPs on
  repeated `401`s.

The data is public (CC0), so this auth is access control and abuse
prevention, not secrecy.

---

## Sources, redistribution scope, and license

Code: dedicated to the public domain under [CC0 1.0 Universal](LICENSE).
Use it however you want.

Data: the opinions database redistributes only the court's own published
work (opinions and court-authored syllabi) plus factual record content
(parties, dates, attorneys, dispositions, citations). Judicial opinions of
state courts are edicts of government and are not protected by copyright;
what is published here is the North Dakota courts' own text. See
[`NOTICE.md`](NOTICE.md) for the redistribution scope in full.

---

## Building one for another jurisdiction

Nothing here is North Dakota-specific except the sources and a few
tables. (This repository is the serve-only half; the ingest pipeline lives
in the development repository. The method is what transfers.) The shape:
raw sources kept as untouched witnesses, one SQLite database per corpus, a citation graph, a
correction log, and a thin MCP layer on top. This is the order that worked.

### 1. Decide what the corpora are, and what the unit of each one is

Two kinds of law need two data models. **Opinions** are immutable dated
documents: one row per opinion, parallel citations in a side table, text
searched with FTS5. **Codes** — constitution,
statutes, court rules, regulations — are *versioned provisions*: a stable
identity (`art. I, § 8`, `§ 28-32-46`, `Rule 12`) with dated text versions,
so a query can ask for the text in force on a given date. Decide
early how you will name every unit, because the citation graph resolves
cross-references by exact string match on that canonical name.

### 2. Locate the sources

For each corpus, find the official publisher first, then the independent
witnesses. What we used, and where the equivalents usually live:

| Corpus | Official | Independent witnesses |
|---|---|---|
| Opinions, modern | The court's own site: slip PDFs plus a neutral-citation index (`2019 ND 54`); weekly scrape | [CourtListener](https://www.courtlistener.com) bulk data and API (Free Law Project); the court's legacy archive if one exists |
| Opinions, pre-digital | The bound official reports (public domain for state government works) | CourtListener's historical case-law collection (texts and page scans); Google Books / HathiTrust scans of the reporter volumes; the regional reporter's own volumes |
| Statutes | The legislature. Look for a structured export before scraping HTML — North Dakota's Legislative Council publishes the whole code as JSON | Session laws (for point-in-time history); the archived prior editions |
| Constitution | Legislature or Secretary of State | A compiled amendment chronology (ballot measures, session laws) is what makes the history layer possible |
| Court rules | The court's rules page; amending orders carry effective dates | The orders themselves |
| Administrative code | Whoever publishes it (here, the Legislative Council) | The register / notices of adopted rules |
| Attorney General, ethics advisory opinions | The issuing office's site | — |

Read the terms of use and `robots.txt` for every source. Commercial
reporter text is subscriber content: it can serve as a
*validation* witness under your own subscription, but you cannot
redistribute it, and your shipped database must contain only the
government's own text plus factual record content. Write that scope down
before you ingest anything ([`NOTICE.md`](NOTICE.md) is ours).

### 3. Acquire, and keep the raw files forever

Everything lands in a witness tree (a `refs/<state>/…` directory outside
the repository) that the pipeline reads and never writes. A file there is
authoritative about what the *source said*, never about what the opinion *should* say; corrections live
only in the database and its changelog. Alongside each acquired file keep a
small provenance sidecar (URL, fetch date, checksum). Scrape politely, with
a fixed rate and a real user agent; some court sites sit behind Cloudflare
and need TLS impersonation (`curl_cffi`) rather than plain `requests`.
Automate the weekly pull (`launchd`/`cron`) from day one, because the
corpus is only ever as current as the last run.

### 4. Extract text with two witnesses per document

- **Born-digital PDFs**: `pdftotext -layout`, then a reflow pass that
  rejoins wrapped lines, keeps paragraph numbers, star pages, footnotes, and
  block quotes, and strips clerk stamps and page furniture.
- **Scanned pages**: OCR twice with different engines (we use tesseract via
  `ocrmypdf` as the baseline and a vision-language model, Surya, as the
  second witness) and accept a correction only where the two agree against
  the stored text, then read the page image for anything digit-bearing.
- **HTML**: a parser per site; the archive's `<u>` may be italics on one
  page and inserted text on another, so decide per element with the page in
  front of you.

Pick unambiguous in-text sigils for structure (`[¶12]`, `[*363]`, `[n3]`)
that cannot collide with the court's own bracketed material, and document
them where every consumer will see them. Preserve
the court's misprints verbatim and record them in a `print_anomalies`
table with the intended reading; the citation graph resolves to the
intended target while the text stays faithful.

### 5. Load, deduplicate, and link

Ingest each source separately, then merge by **parallel-citation
matching**: the same opinion appears in the regional reporter, the state
reports, the court's site, and CourtListener, and the citation set is the
join key. Record every source that contributed in a sources table so a
later audit can diff the stored text against each witness.
Extract citations with a parser that knows your
jurisdiction's reporters, rules, and statute forms — we use
[`jetcite`](https://github.com/jet52/jetcite) — into an outbound table
(document → authority) and derive the inbound side (cited-by, notes of
decisions) from it. Provision-to-provision cross-references get the same
treatment inside each code database, keyed to the version they appeared in.

### 6. Serve

[FastMCP](https://github.com/jlowin/fastmcp) turns plain functions into
tools; `ndlaw_mcp/server.py` attaches the per-corpus databases to one
connection and registers about forty. Name tools by the questions a lawyer
asks (`lookup_opinion`, `get_citing_opinions`, `lookup_authority` with
`as_of_date`, `check_draft`), keep responses paginated, and give every tool
an end-to-end test. Ship a `get_database_stats` tool that reports the
corpus counts and the date of the last update, so users can tell how
current an instance is.

### 7. Validate, log, release

Write integrity invariants and run them after every data batch; log every
correction as a batch with a reason and the witness it was checked against
(a data changelog, separate from the code changelog); and plan an
independent text-fidelity audit against the original sources. Release the databases as
versioned assets on a fixed cadence, separate from the code, with the
distribution copy stripped of anything you may not redistribute.

### What to fork and what to rewrite

Reuse as-is: the schemas, the server and web layers, the invariants
framework, the changelog and release tooling, the two-witness OCR gate.
Rewrite for your jurisdiction: the scrapers, the court-composition table
(justices and terms), the reporter taxonomy and citation patterns, the
text conventions of your court's print, and the redistribution scope.
Budget most of the effort for step 4: acquiring sources is a week, getting
the text right is the project.

---

## Reporting errors

This repository ships a validated, read-only corpus and the minimal server that
serves it; the data pipeline and its correction history are maintained
separately. If you find a text or metadata discrepancy against an official
source, please open an issue with the citation and the source you checked
against.
