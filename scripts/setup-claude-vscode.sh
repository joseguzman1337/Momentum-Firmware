#!/bin/bash
# Team Setup Script for Claude VS Code Extension - Momentum Firmware

set -e

echo "🚀 Setting up Claude VS Code Extension for Momentum Firmware Team"

# Install Claude Code extension
echo "📦 Installing Claude Code extension..."
code --install-extension anthropic.claude-code

# Setup workspace configuration
echo "⚙️ Configuring workspace settings..."
mkdir -p .vscode

# Create tasks.json for firmware development
cat > .vscode/tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build Firmware",
            "type": "shell",
            "command": "./fbt",
            "args": ["updater_package"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Flash Firmware",
            "type": "shell",
            "command": "./fbt",
            "args": ["flash_usb_full"],
            "group": "build"
        },
        {
            "label": "Launch App",
            "type": "shell",
            "command": "./fbt",
            "args": ["launch", "APPSRC=${input:appId}"],
            "group": "build"
        }
    ],
    "inputs": [
        {
            "id": "appId",
            "description": "App ID to launch",
            "default": "hello_world",
            "type": "promptString"
        }
    ]
}
EOF

# Create launch.json for debugging
cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Flipper App",
            "type": "cortex-debug",
            "request": "launch",
            "servertype": "openocd",
            "cwd": "${workspaceRoot}",
            "executable": "./build/latest/firmware.elf",
            "configFiles": [
                "debug/stm32wbx.cfg"
            ]
        }
    ]
}
EOF

# Setup Claude Code settings
echo "🤖 Configuring Claude Code settings..."
mkdir -p .ai/.claude

cat > .ai/.claude/settings.json << 'EOF'
{
  "allowedCommands": [
    "./fbt",
    "make",
    "cmake",
    "git",
    "grep",
    "find"
  ],
  "allowedDirectories": [
    "/Users/x/x/Momentum-Firmware"
  ],
  "mcpServers": {
    "flipper-tools": {
      "command": "python",
      "args": [".ai/tools/flipper_mcp.py"]
    },
    "firmware-analyzer": {
      "command": "python",
      "args": [".ai/tools/firmware_analyzer.py"]
    }
  }
}
EOF

# Create team documentation
cat > CLAUDE_SETUP.md << 'EOF'
# Claude VS Code Extension Setup - Momentum Firmware

## Quick Start
1. Extension auto-installed via setup script
2. Use `Cmd+Shift+Esc` to open new Claude conversation
3. Use `Alt+K` to @-mention files with line numbers

## Firmware Development Shortcuts
- **Build**: `Cmd+Shift+P` → "Tasks: Run Task" → "Build Firmware"
- **Flash**: `Cmd+Shift+P` → "Tasks: Run Task" → "Flash Firmware"
- **Debug**: `F5` to start debugging session

## Claude Code Commands
- `/model` - Switch AI model
- `/help` - Show available commands
- `/compact` - Toggle compact mode

## MCP Tools Available
- `build_firmware(target="f7")` - Build for specific target
- `flash_firmware()` - Flash to device
- `analyze_code_quality(file)` - Check code quality
- `check_flipper_compatibility(file)` - Verify Flipper compatibility

## Team Workflow
1. Open file in VS Code
2. Select code section
3. Press `Alt+K` to @-mention in Claude
4. Ask Claude to review/improve/debug
5. Accept/reject changes via diff interface
EOF

echo "✅ Claude VS Code Extension setup complete!"
echo "📖 See CLAUDE_SETUP.md for team usage instructions"