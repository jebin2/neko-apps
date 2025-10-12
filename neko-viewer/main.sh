#!/bin/bash

PYTHON="/home/jebin/.pyenv/versions/neko-viewer_env/bin/python"
SCRIPT="main.py"

# Find running main.py process using this Python
PID=$(pgrep -f "$PYTHON.*$SCRIPT")

if [ -n "$PID" ]; then
    echo "Found running process $PID, killing it..."
    kill $PID
    sleep 1
else
    echo "No process running. Starting $PWD//$SCRIPT..."
    "$PYTHON" "$PWD/$SCRIPT" >> /dev/null 2>&1 &
    NEW_PID=$!
    echo "Started $PWD//$SCRIPT with PID $NEW_PID"
fi
