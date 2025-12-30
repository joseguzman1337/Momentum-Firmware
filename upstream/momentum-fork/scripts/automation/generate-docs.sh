#!/bin/bash
# Generate documentation for new firmware features

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <file_or_directory>"
    exit 1
fi

target="$1"

if [ ! -e "$target" ]; then
    echo "Error: $target does not exist"
    exit 1
fi

echo "Generating documentation for $target..."

# Generate docs with Gemini CLI
if [ -f "$target" ]; then
    result=$(cat "$target" | gemini -p "Generate comprehensive documentation for this Flipper Zero firmware code:
- Function/API reference
- Usage examples
- Configuration options
- Hardware requirements
- Security considerations
Format as Markdown." --output-format json)
else
    result=$(find "$target" -name "*.c" -o -name "*.h" | head -10 | xargs cat | gemini -p "Generate module documentation for this Flipper Zero firmware code. Include API reference and usage examples." --output-format json)
fi

# Save documentation
doc_file="docs/$(basename "$target" | sed 's/\.[^.]*$//').md"
mkdir -p docs
echo "$result" | jq -r '.response' > "$doc_file"

echo "✅ Documentation generated: $doc_file"