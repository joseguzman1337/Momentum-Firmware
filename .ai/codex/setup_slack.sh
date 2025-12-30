#!/bin/bash
# Codex Slack Integration Setup for Momentum Firmware

echo "🚀 Setting up Codex Slack Integration..."

# Create necessary directories
mkdir -p .ai/codex
mkdir -p logs/codex

# Set permissions
chmod +x .ai/codex/slack_integration.py

# Install dependencies if needed
if command -v pip3 &> /dev/null; then
    pip3 install requests slack-sdk --quiet
fi

echo "✅ Codex Slack integration setup complete!"
echo ""
echo "Next steps:"
echo "1. Go to https://chatgpt.com/codex/settings/connectors"
echo "2. Install the Codex Slack app in your workspace"
echo "3. Add @Codex to your Slack channels"
echo "4. Mention @Codex with your firmware development requests"
echo ""
echo "Example usage:"
echo "  @Codex fix the SubGHz frequency issue in applications/main/subghz/"
echo "  @Codex review the NFC implementation changes"
echo "  @Codex optimize the BadUSB keyboard layout"