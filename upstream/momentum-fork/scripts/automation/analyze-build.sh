#!/bin/bash
# Analyze build errors and suggest fixes

set -e

echo "Building firmware and analyzing errors..."

# Capture build output
build_log=$(./fbt flash_usb_full 2>&1 || true)

# Check if build succeeded
if echo "$build_log" | grep -q "SUCCESS"; then
    echo "✅ Build successful"
    exit 0
fi

echo "❌ Build failed, analyzing errors..."

# Analyze errors with Gemini CLI
result=$(echo "$build_log" | gemini -p "Analyze these Flipper Zero firmware build errors and provide specific fixes:
- Identify root cause
- Suggest exact code changes
- Check for missing dependencies
- Verify toolchain issues" --output-format json)

# Save analysis
echo "$result" | jq -r '.response' > build-analysis.md
echo "Build error analysis saved to build-analysis.md"

# Extract quick fixes
echo "Quick fixes:"
echo "$result" | jq -r '.response' | grep -E "^[0-9]+\.|^\*|^-" | head -5