#!/bin/bash
# Generate commit messages for Momentum Firmware

set -e

# Get staged changes
diff_output=$(git diff --cached)

if [ -z "$diff_output" ]; then
    echo "No staged changes to commit"
    exit 1
fi

# Generate commit message
result=$(echo "$diff_output" | gemini -p "Generate a conventional commit message for these Flipper Zero firmware changes. Format: type(scope): description. Types: feat, fix, docs, style, refactor, test, chore. Keep under 50 chars." --output-format json)

commit_msg=$(echo "$result" | jq -r '.response' | head -1)

echo "Generated commit message: $commit_msg"

# Optionally commit automatically
if [ "$1" = "--auto" ]; then
    git commit -m "$commit_msg"
    echo "✅ Changes committed"
else
    echo "Run: git commit -m \"$commit_msg\""
fi