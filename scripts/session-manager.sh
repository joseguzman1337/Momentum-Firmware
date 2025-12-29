#!/bin/bash
# Session management for Momentum Firmware development

set -e

case "$1" in
    "list")
        echo "📋 Recent Momentum Firmware sessions:"
        gemini --list-sessions
        ;;
    "resume")
        if [ -n "$2" ]; then
            echo "🔄 Resuming session $2..."
            gemini --resume "$2"
        else
            echo "🔄 Resuming latest session..."
            gemini --resume
        fi
        ;;
    "clean")
        echo "🧹 Cleaning old sessions..."
        # List sessions older than 7 days
        echo "Sessions to be cleaned:"
        gemini --list-sessions | grep -E "\([0-9]+ (day|week|month)s? ago\)"
        read -p "Continue? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            # Note: Actual cleanup happens automatically via settings.json
            echo "✅ Cleanup configured in settings.json"
        fi
        ;;
    "backup")
        backup_dir="backups/sessions/$(date +%Y%m%d)"
        mkdir -p "$backup_dir"
        cp -r ~/.gemini/tmp/*/chats/ "$backup_dir/" 2>/dev/null || true
        echo "💾 Sessions backed up to $backup_dir"
        ;;
    "search")
        if [ -z "$2" ]; then
            echo "Usage: $0 search <keyword>"
            exit 1
        fi
        echo "🔍 Searching sessions for: $2"
        find ~/.gemini/tmp/*/chats/ -name "*.json" -exec grep -l "$2" {} \; 2>/dev/null | head -5
        ;;
    *)
        echo "Momentum Firmware Session Manager"
        echo "Usage: $0 {list|resume [id]|clean|backup|search <keyword>}"
        echo ""
        echo "Commands:"
        echo "  list     - Show recent sessions"
        echo "  resume   - Resume latest or specific session"
        echo "  clean    - Clean old sessions"
        echo "  backup   - Backup session history"
        echo "  search   - Search sessions by keyword"
        ;;
esac