#!/usr/bin/env node
// ndcourts-mcp .mcpb wrapper.
//
// Loads the bundled mcp-remote IN-PROCESS via dynamic import, after rewriting
// process.argv to look like mcp-remote was invoked directly. This avoids
// spawning a child process, which fails inside Claude Desktop because the
// "built-in Node" is actually the Claude Helper Electron binary —
// process.execPath does NOT point at a real Node executable, so
// spawn(process.execPath, [...]) hangs indefinitely.

const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

const url = process.env.MCP_URL;
const username = process.env.MCP_USERNAME;
const password = process.env.MCP_PASSWORD;

console.error(`[ndcourts-wrapper] starting (node ${process.version}, pid ${process.pid})`);

if (!url || !username || !password) {
  console.error(
    "[ndcourts-wrapper] missing MCP_URL, MCP_USERNAME, or MCP_PASSWORD. " +
    "Check the extension's configuration in Claude Desktop."
  );
  process.exit(2);
}

// Guard against a Claude Desktop bug: when a user_config field is marked
// `sensitive: true`, Desktop stores `__encrypted__:<ciphertext>` but
// substitutes that same encrypted string into the env var. Our manifest
// avoids `sensitive: true` on credentials for this reason; if a future
// Desktop / manifest change re-triggers it, surface a clear error.
if (password.startsWith("__encrypted__:") || username.startsWith("__encrypted__:")) {
  console.error(
    "[ndcourts-wrapper] credential is encrypted ciphertext, not the actual " +
    "value. This is a Claude Desktop bug with sensitive user_config fields."
  );
  process.exit(3);
}

const auth = Buffer.from(`${username}:${password}`).toString("base64");

const mcpRemoteEntry = path.join(
  __dirname, "..", "node_modules", "mcp-remote", "dist", "proxy.js"
);

if (!fs.existsSync(mcpRemoteEntry)) {
  console.error(`[ndcourts-wrapper] bundled mcp-remote not found at ${mcpRemoteEntry}`);
  process.exit(4);
}

// Rewrite process.argv so mcp-remote's argv parsing sees the args we want.
// argv[0] = node-like path, argv[1] = script path, then mcp-remote's own args.
process.argv = [
  process.execPath,
  mcpRemoteEntry,
  url,
  "--header",
  `Authorization: Basic ${auth}`,
];

console.error(`[ndcourts-wrapper] importing bundled mcp-remote in-process`);

import(pathToFileURL(mcpRemoteEntry).href).catch((err) => {
  console.error(`[ndcourts-wrapper] import failed: ${err && err.message}`);
  if (err && err.stack) console.error(err.stack);
  process.exit(5);
});
