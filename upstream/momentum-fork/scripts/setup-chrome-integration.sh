#!/bin/bash

# Setup Chrome integration for Claude Code in Momentum Firmware project
set -e

echo "Setting up Chrome integration for Momentum Firmware development..."

# Check if Claude Code is installed
if ! command -v claude &> /dev/null; then
    echo "Error: Claude Code CLI not found. Please install it first."
    exit 1
fi

# Update Claude Code
echo "Updating Claude Code..."
claude update

# Check Chrome extension
echo "Checking Chrome extension..."
if ! pgrep -x "Google Chrome" > /dev/null; then
    echo "Starting Chrome..."
    open -a "Google Chrome"
    sleep 3
fi

# Create Chrome integration config
mkdir -p .ai/chrome
cat > .ai/chrome/config.json << 'EOF'
{
  "enabled": true,
  "autoStart": true,
  "permissions": {
    "localhost": true,
    "github.com": true,
    "momentum-fw.dev": true
  },
  "workflows": {
    "testLocalBuild": "localhost:8080",
    "checkDocs": "momentum-fw.dev",
    "reviewPRs": "github.com/joseguzman1337/Momentum-Firmware"
  }
}
EOF

echo "Chrome integration setup complete!"
echo "Start Claude Code with: claude --chrome"
echo "Or enable by default with: /chrome -> 'Enabled by default'"