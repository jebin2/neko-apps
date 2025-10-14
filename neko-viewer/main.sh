#!/bin/bash

PYTHON="/home/jebin/.pyenv/versions/neko-viewer_env/bin/python"
SCRIPT="/home/jebin/git/neko-apps/neko-viewer/main.py"
PORT=8731

# Glyphs
ICON_RUNNING="󰄛  "
ICON_STOPPED="󰄛💤 "

# Find running main.py process using this Python
PID=$(pgrep -f "$PYTHON.*$SCRIPT")

# Check if port is in use (listening)
PORT_ACTIVE=$(ss -tuln | grep -q ":$PORT " && echo 1 || echo 0)

MODE="$1"

case "$MODE" in
    1)
        # Only check status
        if [ -n "$PID" ] || [ "$PORT_ACTIVE" -eq 1 ]; then
            echo "$ICON_RUNNING"
        else
            echo "$ICON_STOPPED"
        fi
        ;;
    2)
        # Kill if running; if not running, start
        if [ -n "$PID" ] || [ "$PORT_ACTIVE" -eq 1 ]; then
            echo "$ICON_STOPPED"
            [ -n "$PID" ] && kill $PID
            sleep 1
            notify-send "Neko Viewer Stopped"
        else
            echo "$ICON_RUNNING"
            "$PYTHON" "$SCRIPT" >> /dev/null 2>&1 &
            notify-send "Neko Viewer Started"
        fi
        ;;
    *)
        echo "Usage: $0 [1|2]"
        echo "1 = Check status only"
        echo "2 = Kill if running; start if not running"
        ;;
esac
