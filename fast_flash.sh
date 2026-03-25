#!/bin/bash
# High-speed polling for WiFi Board

PYTHON_CMD="/home/d3c0d3r/.local/bin/python3"
if ! command -v "$PYTHON_CMD" &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "🚀 polling for ESP32-S2 (ID 303a:*) every 0.1s..."

start_time=$(date +%s)
timeout=120

while true; do
    current_time=$(date +%s)
    if [ $((current_time - start_time)) -ge $timeout ]; then
        echo "⏰ Timeout waiting for device."
        exit 1
    fi

    if lsusb -d 303a: > /dev/null; then
        echo "✅ DEVICE DETECTED! Starting flash..."
        # Wait a split second for enumeration to stabilize?
        # sleep 0.5 
        # Actually, let's just go.
        $PYTHON_CMD -m ufbt devboard_flash
        exit_code=$?
        if [ $exit_code -eq 0 ]; then
            echo "🎉 SUCCESS: Flash complete."
            exit 0
        else
            echo "❌ ERROR: Flash failed with code $exit_code."
            # Don't exit, maybe try again?
            # exit 1
            echo "Retrying detection..."
            sleep 2
        fi
    fi
    sleep 0.1
done
