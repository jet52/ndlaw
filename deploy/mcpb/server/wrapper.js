#!/usr/bin/env node
// ndcourts-mcp .mcpb wrapper.
// Reads URL + credentials from env (populated by user_config in manifest.json),
// derives the Basic Auth header, and execs the bundled mcp-remote with the
// SAME Node interpreter (process.execPath) and an absolute path — so we don't
// depend on `npx` or PATH inside Claude Desktop's spawned environment.

const path = require("path");
const { spawn } = require("child_process");

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

const auth = Buffer.from(`${username}:${password}`).toString("base64");

// mcp-remote is bundled inside this extension at <root>/node_modules/mcp-remote.
// __dirname here is <root>/server, so the package sits one directory up.
const mcpRemoteEntry = path.join(
  __dirname, "..", "node_modules", "mcp-remote", "dist", "proxy.js"
);

console.error(`[ndcourts-wrapper] spawning ${process.execPath} ${mcpRemoteEntry}`);

const child = spawn(
  process.execPath,
  [mcpRemoteEntry, url, "--header", `Authorization: Basic ${auth}`],
  { stdio: "inherit" }
);

child.on("spawn", () => {
  console.error(`[ndcourts-wrapper] mcp-remote spawned (pid ${child.pid})`);
});

child.on("error", (err) => {
  console.error(`[ndcourts-wrapper] spawn error: ${err.code} ${err.message}`);
  process.exit(1);
});

child.on("exit", (code, signal) => {
  console.error(`[ndcourts-wrapper] mcp-remote exited (code=${code} signal=${signal})`);
  process.exit(code ?? 0);
});
