# Momentum Firmware Security Configuration

## Trusted Folders Setup

This project uses Gemini CLI Trusted Folders for secure development:

### Features Enabled When Trusted:
- ✅ Workspace settings (.gemini/settings.json)
- ✅ Custom commands (.gemini/commands/)
- ✅ Environment variables (.env files)
- ✅ Tool auto-acceptance
- ✅ MCP server connections
- ✅ Extension management
- ✅ Automatic memory loading
- ✅ Telemetry collection

### Security Benefits:
- 🛡️ Prevents malicious code execution
- 🔒 Protects against untrusted project configurations
- 🚫 Blocks unauthorized tool execution
- 📝 Maintains audit trail of trusted projects

### Setup Instructions:

1. **Enable folder trust** (already configured):
   ```json
   {"security": {"folderTrust": {"enabled": true}}}
   ```

2. **Trust this project**:
   ```bash
   # Run Gemini CLI and select "Trust folder" when prompted
   gemini
   
   # Or use trust manager
   ./scripts/trust-manager.sh setup
   ```

3. **Verify trust status**:
   ```bash
   ./scripts/trust-manager.sh status
   # Or in Gemini CLI: /permissions
   ```

### Management Commands:
- `/trust` - Check trust status
- `/permissions` - Modify trust settings
- `trust-manager.sh` - Command-line trust management

### Trust File Location:
`~/.gemini/trustedFolders.json`