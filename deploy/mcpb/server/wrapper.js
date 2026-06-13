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

console.error(`[ndcourts-wrapper] starting (node ${process.version}, pid ${process.pid})`);

if (!url) {
  console.error(
    "[ndcourts-wrapper] missing MCP_URL. " +
    "Check the extension's configuration in Claude Desktop."
  );
  process.exit(2);
}

const mcpRemoteEntry = path.join(
  __dirname, "..", "node_modules", "mcp-remote", "dist", "proxy.js"
);

if (!fs.existsSync(mcpRemoteEntry)) {
  console.error(`[ndcourts-wrapper] bundled mcp-remote not found at ${mcpRemoteEntry}`);
  process.exit(4);
}

// Rewrite process.argv so mcp-remote's argv parsing sees the args we want.
// argv[0] = node-like path, argv[1] = script path, then mcp-remote's own args.
// The URL is a capability URL — the secret path segment IS the credential,
// so no Authorization header is needed.
process.argv = [
  process.execPath,
  mcpRemoteEntry,
  url,
];

console.error(`[ndcourts-wrapper] importing bundled mcp-remote in-process`);

import(pathToFileURL(mcpRemoteEntry).href).catch((err) => {
  console.error(`[ndcourts-wrapper] import failed: ${err && err.message}`);
  if (err && err.stack) console.error(err.stack);
  process.exit(5);
});
