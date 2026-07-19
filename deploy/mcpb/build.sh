#!/usr/bin/env bash
# Build deploy/ndlaw.mcpb from the sources in this directory.
# An .mcpb file is a zip with manifest.json at the root. We bundle mcp-remote
# (~7 MB on disk, ~3 MB zipped) so the wrapper can invoke it via absolute path
# rather than relying on `npx`, which fails to resolve inside Claude Desktop's
# spawned Node environment.
set -euo pipefail

cd "$(dirname "$0")"
out="../ndlaw.mcpb"

python3 -c "import json; json.load(open('manifest.json'))" \
  || { echo "manifest.json is not valid JSON" >&2; exit 1; }
node --check server/wrapper.js \
  || { echo "server/wrapper.js failed syntax check" >&2; exit 1; }

# Refresh bundled dependencies (mcp-remote). --omit=dev keeps prod-only.
echo "installing dependencies..."
npm install --no-save --omit=dev --silent

[ -f "node_modules/mcp-remote/dist/proxy.js" ] \
  || { echo "node_modules/mcp-remote/dist/proxy.js missing after npm install" >&2; exit 1; }

rm -f "$out"
zip -rq "$out" manifest.json server node_modules package.json -x ".*"

size=$(stat -f%z "$out" 2>/dev/null || stat -c%s "$out")
echo "built $out ($((size / 1024)) KB)"
unzip -l "$out" | tail -3
