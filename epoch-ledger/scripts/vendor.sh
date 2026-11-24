#!/usr/bin/env bash
# Fetch the third-party runtime files an Epoch Ledger HyperFrames workspace needs.
# Usage: epoch-ledger/scripts/vendor.sh WORKSPACE
# GSAP and Three.js come from the jsDelivr CDN; Fraunces and Inter (SIL OFL) from
# @fontsource on the npm registry. Already-present files are left alone.
set -euo pipefail
WS="${1:?usage: vendor.sh WORKSPACE}"
KIT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$WS/vendor" "$WS/fonts"
fetch() { [ -s "$2" ] || curl -sSfL -o "$2" "$1"; }
fetch https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js "$WS/vendor/gsap.min.js"
fetch https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js "$WS/vendor/three.min.js"
cp "$KIT/kit/vault3d.js" "$WS/vendor/vault3d.js"
need=0
for f in fraunces-latin-600-normal fraunces-latin-800-normal inter-latin-500-normal inter-latin-700-normal; do
  [ -s "$WS/fonts/$f.woff2" ] || need=1
done
if [ "$need" = 1 ]; then
  TMP="$(mktemp -d)"
  (cd "$TMP" && npm pack -s @fontsource/fraunces @fontsource/inter >/dev/null)
  for t in "$TMP"/*.tgz; do mkdir -p "$TMP/x" && tar -xzf "$t" -C "$TMP/x" && cp "$TMP"/x/package/files/{fraunces-latin-600,fraunces-latin-800,inter-latin-500,inter-latin-700}-normal.woff2 "$WS/fonts/" 2>/dev/null || true; rm -rf "$TMP/x"; done
  rm -rf "$TMP"
fi
for f in "$WS"/vendor/gsap.min.js "$WS"/vendor/three.min.js "$WS"/fonts/inter-latin-700-normal.woff2 "$WS"/fonts/fraunces-latin-800-normal.woff2; do
  [ -s "$f" ] || { echo "missing $f" >&2; exit 1; }
done
echo "vendor files ready in $WS"
