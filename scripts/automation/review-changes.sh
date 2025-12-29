#!/bin/bash
# Automated code review for Momentum Firmware

set -e

echo "Running automated code review..."

# Get staged changes
diff_output=$(git diff --cached)

if [ -z "$diff_output" ]; then
    echo "No staged changes found"
    exit 0
fi

# Review changes with Gemini CLI
result=$(echo "$diff_output" | gemini -p "Review these Flipper Zero firmware changes for:
- Memory safety and buffer overflows
- Real-time constraints compliance
- Hardware compatibility issues
- Security vulnerabilities
- Code style consistency
Provide specific line-by-line feedback." --output-format json)

# Extract response and save
echo "$result" | jq -r '.response' > review-output.md
echo "Review saved to review-output.md"

# Check for critical issues
critical_count=$(echo "$result" | jq -r '.response' | grep -i "critical\|security\|buffer overflow\|memory leak" | wc -l)

if [ "$critical_count" -gt 0 ]; then
    echo "⚠️  Critical issues found: $critical_count"
    exit 1
else
    echo "✅ No critical issues detected"
fi