#!/bin/bash
# High-speed polling for WiFi Board

PYTHON_CMD="${PYTHON_CMD:-python3}"

esp32_s2_present() {
    if command -v lsusb >/dev/null 2>&1; then
        lsusb -d 303a: >/dev/null 2>&1
    elif command -v system_profiler >/dev/null 2>&1; then
        system_profiler SPUSBDataType 2>/dev/null | grep -Eiq 'Vendor ID: 0x303a'
    elif command -v ioreg >/dev/null 2>&1; then
        ioreg -p IOUSB -l -w 0 2>/dev/null | grep -Eiq '"idVendor"[[:space:]]*=[[:space:]]*12346'
    else
        echo "No supported USB inventory command found (lsusb, system_profiler, or ioreg)." >&2
        return 2
    fi
}

echo "🚀 polling for ESP32-S2 (ID 303a:*) every 0.1s..."

start_time=$(date +%s)
timeout=120

while true; do
    current_time=$(date +%s)
    if [ $((current_time - start_time)) -ge $timeout ]; then
        echo "⏰ Timeout waiting for device."
        exit 1
    fi

    if esp32_s2_present; then
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
