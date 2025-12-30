#!/bin/bash
# Launch Claude Code (powered by DeepSeek)
# Reference: DeepSeek API Guides - Anthropic API

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed. Please install Node.js."
    exit 1
fi

# Check if claude-code is installed
if ! command -v claude &> /dev/null; then
    echo "📦 Installing @anthropic-ai/claude-code..."
    npm install -g @anthropic-ai/claude-code
fi

# Check for API Key
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ Error: DEEPSEEK_API_KEY is not set."
    exit 1
fi

echo "🚀 Configuring DeepSeek x Anthropic Environment..."

# Export Configuration
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_API_KEY=$DEEPSEEK_API_KEY
# Note: Claude Code uses ANTHROPIC_AUTH_TOKEN usually, but docs say:
# export ANTHROPIC_AUTH_TOKEN=${YOUR_API_KEY}
export ANTHROPIC_AUTH_TOKEN=$DEEPSEEK_API_KEY

export API_TIMEOUT_MS=600000
export ANTHROPIC_MODEL=deepseek-chat
export ANTHROPIC_SMALL_FAST_MODEL=deepseek-chat
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1

echo "🤖 Launching Claude Code (DeepSeek Edition)..."
echo "   Model: $ANTHROPIC_MODEL"
echo "   Base URL: $ANTHROPIC_BASE_URL"
echo "---------------------------------------------------"

# Execute Claude
claude
