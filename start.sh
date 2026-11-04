#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────
# start.sh  –  uruchamia bota i restartuje go jeśli crashnie
# Uruchom: bash start.sh
# ──────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[start.sh] Uruchamiam Minecraft AFK Bot w trybie watchdog..."

while true; do
    python3 bot.py
    EXIT_CODE=$?
    echo "[start.sh] Bot zakończył pracę (kod: $EXIT_CODE). Restart za 5s..."
    sleep 5
done
