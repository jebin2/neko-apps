#!/bin/bash

PYTHON="/home/jebin/.pyenv/versions/neko-viewer_env/bin/python"
SCRIPT="/home/jebin/git/neko-apps/neko-viewer/main.py"

# Find running main.py process using this Python
PID=$(pgrep -f "$PYTHON.*$SCRIPT")

MODE="$1"

case "$MODE" in
    1)
        # Only check status
        if [ -n "$PID" ]; then
            echo "🔗 NekoViewer  "
        else
            echo "❌ NekoViewer  "
        fi
        ;;
    2)
        # Kill if running; if not running, start
        if [ -n "$PID" ]; then
            echo "❌ NekoViewer  "
            kill $PID
            sleep 1
        else
            echo "🔗 NekoViewer  "
            "$PYTHON" "$SCRIPT" >> /dev/null 2>&1 &
        fi
        ;;
    *)
        echo "Usage: $0 [1|2]"
        echo "1 = Check status only"
        echo "2 = Kill if running; start if not running"
        ;;
esac
