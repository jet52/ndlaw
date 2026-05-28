#!/usr/bin/env bash
# Build deploy/ndcourts.mcpb from the sources in this directory.
# An .mcpb file is just a zip with manifest.json at the root.
set -euo pipefail

cd "$(dirname "$0")"
out="../ndcourts.mcpb"

python3 -c "import json; json.load(open('manifest.json'))" \
  || { echo "manifest.json is not valid JSON" >&2; exit 1; }
node --check server/wrapper.js \
  || { echo "server/wrapper.js failed syntax check" >&2; exit 1; }

rm -f "$out"
zip -r "$out" manifest.json server -x ".*" >/dev/null

echo "built $out ($(stat -f%z "$out" 2>/dev/null || stat -c%s "$out") bytes)"
unzip -l "$out"
