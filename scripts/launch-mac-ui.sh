#!/bin/zsh

set -euo pipefail

PORT="4312"
PID_FILE="/tmp/borstbindare-wenman-ui-python.pid"
LOG_FILE="$HOME/Library/Logs/BorstbindareWenmanUI.log"
SERVER_SCRIPT="/Users/nicklaskarlsson/Desktop/toolconv/scripts/mac-ui-server.py"
URL="http://127.0.0.1:${PORT}"

mkdir -p "$(dirname "$LOG_FILE")"

if ! command -v python3 >/dev/null 2>&1; then
  osascript -e 'display alert "Borstbindare Wenman" message "python3 saknas. Installera python3 och prova igen." as warning'
  exit 1
fi

if [ ! -f "$SERVER_SCRIPT" ]; then
  osascript -e 'display alert "Borstbindare Wenman" message "UI-servern hittades inte i toolconv-mappen på skrivbordet." as warning'
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
  BORSTBINDAR_FFMPEG="/opt/homebrew/bin/ffmpeg" nohup python3 "$SERVER_SCRIPT" >>"$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
)

sleep 1
open "$URL"
