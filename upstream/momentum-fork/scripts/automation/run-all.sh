#!/bin/bash
# Master automation script for Momentum Firmware development

set -e

echo "🚀 Momentum Firmware Automation Suite"
echo "======================================"

# Function to run with error handling
run_check() {
    local name="$1"
    local script="$2"
    echo "Running $name..."
    if "$script"; then
        echo "✅ $name completed"
    else
        echo "❌ $name failed"
        return 1
    fi
    echo ""
}

# Pre-commit checks
if [ "$1" = "pre-commit" ]; then
    echo "Running pre-commit checks..."
    run_check "Code Review" "./scripts/automation/review-changes.sh"
    run_check "Build Test" "./scripts/automation/analyze-build.sh"
    echo "🎉 Pre-commit checks completed"
    exit 0
fi

# Full automation suite
echo "Running full automation suite..."

# Check if there are staged changes
if git diff --cached --quiet; then
    echo "No staged changes found"
else
    run_check "Code Review" "./scripts/automation/review-changes.sh"
    run_check "Generate Commit Message" "./scripts/automation/generate-commit.sh"
fi

run_check "Build Analysis" "./scripts/automation/analyze-build.sh"

echo "🎉 All automation checks completed"