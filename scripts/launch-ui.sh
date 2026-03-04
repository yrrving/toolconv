#!/bin/zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PORT="3000"
PID_FILE="/tmp/borstbindare-wenman-ui.pid"
LOG_FILE="$HOME/Library/Logs/BorstbindareWenman.log"
URL="http://127.0.0.1:${PORT}"

mkdir -p "$(dirname "$LOG_FILE")"

if ! command -v node >/dev/null 2>&1; then
  osascript -e 'display alert "Borstbindare Wenman" message "Node.js saknas. Installera Node.js och prova igen." as warning'
  exit 1
fi

if [ -f "$PID_FILE" ]; then
  EXISTING_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$EXISTING_PID" ] && kill -0 "$EXISTING_PID" >/dev/null 2>&1; then
    open "$URL"
    exit 0
  fi
fi

(
  cd "$PROJECT_DIR"
  nohup node ./bin/toolconv.js serve --port "$PORT" >>"$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
)

sleep 1
open "$URL"
