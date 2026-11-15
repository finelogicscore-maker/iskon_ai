#!/usr/bin/env bash
# Write the current trycloudflare URL for GitHub Pages redirect (docs/).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URL="${1:-}"
JSON="$ROOT/docs/tunnel-url.json"
STABLE="https://finelogicscore-maker.github.io/iskon_ai/"
PUSH="${AUTO_PUSH_REDIRECT:-1}"

if [[ -z "$URL" ]]; then
  echo "Usage: $0 <https://....trycloudflare.com>"
  exit 1
fi

if [[ ! "$URL" =~ ^https://[a-z0-9-]+\.trycloudflare\.com/?$ ]]; then
  echo "Expected a trycloudflare.com HTTPS URL, got: $URL"
  exit 1
fi

URL="${URL%/}"
TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$(dirname "$JSON")"
cat > "$JSON" <<EOF
{
  "url": "$URL",
  "updated_at": "$TS"
}
EOF

echo "Updated redirect target → $URL"
echo "Stable public link (share this): $STABLE"

if [[ "$PUSH" != "1" ]]; then
  exit 0
fi

cd "$ROOT"
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git repo; skipped push."
  exit 0
fi

git add docs/tunnel-url.json
if git diff --staged --quiet; then
  echo "tunnel-url.json unchanged; nothing to push."
  exit 0
fi

git commit -m "Update public redirect to Cloudflare tunnel"
git push origin main
echo "Pushed — $STABLE will point to the new tunnel within ~1 minute."