#!/usr/bin/env bash
# Run uvicorn + Cloudflare quick tunnel; update stable GitHub Pages redirect when URL changes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PORT:-8000}"
LOG="$(mktemp)"
STABLE="https://finelogicscore-maker.github.io/iskon_ai/"

cleanup() {
  rm -f "$LOG"
}
trap cleanup EXIT

if ! curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null; then
  echo "Start the API first, e.g.:"
  echo "  cd \"$ROOT\" && source venv/bin/activate && uvicorn main:app --host 127.0.0.1 --port ${PORT}"
  exit 1
fi

echo "Opening Cloudflare tunnel → http://127.0.0.1:${PORT}"
echo "Stable URL to share: $STABLE"
echo ""

cloudflared tunnel --url "http://127.0.0.1:${PORT}" 2>&1 | tee "$LOG" &
CF_PID=$!

URL=""
for _ in $(seq 1 45); do
  URL="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | head -1 || true)"
  if [[ -n "$URL" ]]; then
    break
  fi
  sleep 1
done

if [[ -z "$URL" ]]; then
  echo "Could not read tunnel URL from cloudflared log."
  kill "$CF_PID" 2>/dev/null || true
  exit 1
fi

echo ""
echo "Tunnel URL (changes each run): $URL"
"$ROOT/scripts/set-public-redirect.sh" "$URL"
echo ""
echo "Leave this running. Press Ctrl+C to stop the tunnel."

wait "$CF_PID"