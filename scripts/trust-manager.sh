#!/bin/bash
# Trusted Folders management for Momentum Firmware

TRUST_FILE="$HOME/.gemini/trustedFolders.json"

case "$1" in
    "status")
        echo "🔒 Folder Trust Status"
        echo "====================="
        
        if [ -f "$TRUST_FILE" ]; then
            echo "Trust configuration found:"
            cat "$TRUST_FILE" | jq '.' 2>/dev/null || cat "$TRUST_FILE"
        else
            echo "No trust configuration found"
        fi
        
        echo ""
        echo "Current folder: $(pwd)"
        echo "Trust status: Run 'gemini /permissions' to check"
        ;;
        
    "trust")
        echo "🔓 Trusting current folder: $(pwd)"
        echo "Run 'gemini /permissions' and select 'Trust folder'"
        ;;
        
    "untrust")
        if [ -f "$TRUST_FILE" ]; then
            current_dir=$(pwd)
            echo "🔒 Removing trust for: $current_dir"
            # Note: Manual editing required as CLI manages this file
            echo "Edit $TRUST_FILE to remove entries for $current_dir"
        else
            echo "No trust file found"
        fi
        ;;
        
    "backup")
        if [ -f "$TRUST_FILE" ]; then
            backup_file="backups/trust_$(date +%Y%m%d_%H%M%S).json"
            mkdir -p backups
            cp "$TRUST_FILE" "$backup_file"
            echo "✅ Trust settings backed up to $backup_file"
        else
            echo "No trust file to backup"
        fi
        ;;
        
    "setup")
        echo "🛡️  Setting up Trusted Folders for Momentum Firmware"
        echo "=================================================="
        
        # Check if trust is enabled
        if grep -q '"enabled": true' .gemini/settings.json 2>/dev/null; then
            echo "✅ Folder trust is enabled"
        else
            echo "❌ Folder trust is not enabled"
            echo "Add to .gemini/settings.json:"
            echo '{"security": {"folderTrust": {"enabled": true}}}'
            exit 1
        fi
        
        echo ""
        echo "Next steps:"
        echo "1. Run 'gemini' in this directory"
        echo "2. When prompted, select 'Trust folder'"
        echo "3. This enables full Gemini CLI features for firmware development"
        ;;
        
    *)
        echo "Momentum Firmware Trust Manager"
        echo "Usage: $0 {status|trust|untrust|backup|setup}"
        echo ""
        echo "Commands:"
        echo "  status   - Show current trust status"
        echo "  trust    - Instructions to trust current folder"
        echo "  untrust  - Remove trust from current folder"
        echo "  backup   - Backup trust settings"
        echo "  setup    - Initial trust setup for firmware project"
        ;;
esac