#!/usr/bin/env node
// ndcourts-mcp .mcpb wrapper.
// Reads URL + credentials from env (populated by user_config in manifest.json),
// derives the Basic Auth header, and execs mcp-remote so Claude Desktop's
// stdio MCP loader talks to the remote Streamable HTTP endpoint transparently.

const { spawn } = require("child_process");

const url = process.env.MCP_URL;
const username = process.env.MCP_USERNAME;
const password = process.env.MCP_PASSWORD;

if (!url || !username || !password) {
  console.error(
    "ndcourts wrapper: missing MCP_URL, MCP_USERNAME, or MCP_PASSWORD. " +
    "Check the extension's configuration in Claude Desktop."
  );
  process.exit(2);
}

const auth = Buffer.from(`${username}:${password}`).toString("base64");

// `npx -y` auto-installs mcp-remote on first run. Subsequent launches use cache.
const child = spawn(
  "npx",
  ["-y", "mcp-remote@latest", url, "--header", `Authorization: Basic ${auth}`],
  { stdio: "inherit" }
);

child.on("error", (err) => {
  console.error(
    "ndcourts wrapper: failed to spawn npx — is Node.js installed? " +
    `Error: ${err.message}`
  );
  process.exit(1);
});

child.on("exit", (code) => process.exit(code ?? 0));
