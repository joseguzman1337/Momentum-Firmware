#!/bin/bash
# Generate release notes from git commits

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <from_tag> [to_tag]"
    echo "Example: $0 v1.0.0 v1.1.0"
    exit 1
fi

from_tag="$1"
to_tag="${2:-HEAD}"

echo "Generating release notes from $from_tag to $to_tag..."

# Get commit range
commits=$(git log --oneline "$from_tag..$to_tag")

if [ -z "$commits" ]; then
    echo "No commits found in range"
    exit 1
fi

# Generate release notes
result=$(echo "$commits" | gemini -p "Generate release notes for Momentum Firmware from these commits:
- Group by: Features, Bug Fixes, Improvements, Breaking Changes
- Use conventional commit format
- Highlight Flipper Zero specific changes
- Include upgrade instructions if needed
- Format as Markdown" --output-format json)

# Save release notes
release_file="RELEASE_NOTES_$(date +%Y%m%d).md"
echo "$result" | jq -r '.response' > "$release_file"

echo "✅ Release notes generated: $release_file"

# Show summary
echo "Summary:"
echo "$result" | jq -r '.response' | head -20