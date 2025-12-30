# Policy Engine for Momentum Firmware

## Overview
The policy engine provides fine-grained control over tool execution in the Momentum Firmware development environment. It uses TOML configuration files to define rules that determine whether operations should be allowed, denied, or require user confirmation.

## Policy Files
- `default.toml` - Basic development policies
- `ai-agents.toml` - Policies for AI automation agents
- `security.toml` - Security-focused restrictions
- `development.toml` - Development workflow policies

## Rule Structure
```toml
[[rule]]
toolName = "tool_name"           # Tool to match
commandPrefix = "git "           # Command prefix for shell commands
argsPattern = '"pattern"'        # Regex for tool arguments
mcpName = "server_name"          # MCP server name
decision = "allow"               # allow, deny, or ask_user
priority = 100                   # Higher numbers win
modes = ["yolo"]                 # Active in specific modes
```

## Priority System
- **900-999**: Critical security rules
- **800-899**: AI agent automation
- **700-799**: Project-specific rules
- **600-699**: Git operations
- **500-599**: Hardware operations
- **400-499**: Network/installation
- **300-399**: Development tools
- **200-299**: Documentation/formatting
- **100-199**: Basic file operations

## Usage Examples

### Allow all git status commands
```toml
[[rule]]
toolName = "run_shell_command"
commandPrefix = "git status"
decision = "allow"
priority = 200
```

### Require confirmation for file writes
```toml
[[rule]]
toolName = ["write_file", "replace"]
decision = "ask_user"
priority = 150
```

### Block dangerous operations
```toml
[[rule]]
toolName = "run_shell_command"
commandPrefix = "rm -rf"
decision = "deny"
priority = 900
```

## Modes
- **Default**: Standard development mode with confirmations
- **YOLO**: Automated mode for AI agents (allows most operations)
- **autoEdit**: Allows certain write operations without prompting

## Security Features
- Blocks access to sensitive files (SSH keys, credentials)
- Requires confirmation for network operations
- Denies system-level modifications
- Allows security scanning tools

## AI Agent Integration
The policy engine is integrated with the AI automation pipeline:
- MCP servers have dedicated policies
- AI agents can operate in YOLO mode
- Automated git operations are allowed
- Log writing is permitted for all agents