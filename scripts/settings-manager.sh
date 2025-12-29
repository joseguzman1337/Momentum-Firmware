#!/bin/bash
# Gemini CLI settings management for Momentum Firmware

case "$1" in
    "backup")
        mkdir -p backups/settings
        cp .gemini/settings.json "backups/settings/settings_$(date +%Y%m%d_%H%M%S).json"
        echo "✅ Settings backed up"
        ;;
    "restore")
        if [ -z "$2" ]; then
            echo "Available backups:"
            ls -1 backups/settings/ 2>/dev/null || echo "No backups found"
            exit 1
        fi
        cp "backups/settings/$2" .gemini/settings.json
        echo "✅ Settings restored from $2"
        ;;
    "reset")
        rm -f .gemini/settings.json
        echo "✅ Settings reset to defaults"
        ;;
    "show")
        echo "Current Gemini CLI settings:"
        cat .gemini/settings.json | jq '.' 2>/dev/null || cat .gemini/settings.json
        ;;
    *)
        echo "Settings Manager for Momentum Firmware"
        echo "Usage: $0 {backup|restore <file>|reset|show}"
        ;;
esac