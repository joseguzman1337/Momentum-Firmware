#!/bin/bash
# Web fetch automation for Momentum Firmware research

set -e

case "$1" in
    "docs")
        echo "📚 Fetching Flipper Zero documentation..."
        gemini --prompt "web_fetch(prompt='Summarize key points from https://docs.flipper.net/ for firmware developers')" --output-format json | jq -r '.response' > research/flipper-docs.md
        echo "✅ Documentation saved to research/flipper-docs.md"
        ;;
        
    "security")
        echo "🔒 Researching firmware security practices..."
        gemini --prompt "web_fetch(prompt='Extract security best practices from https://owasp.org/www-project-embedded-application-security/ for embedded firmware')" --output-format json | jq -r '.response' > research/security-practices.md
        echo "✅ Security research saved to research/security-practices.md"
        ;;
        
    "api")
        if [ -z "$2" ]; then
            echo "Usage: $0 api <url>"
            exit 1
        fi
        echo "🔌 Analyzing API documentation..."
        gemini --prompt "web_fetch(prompt='Analyze API documentation at $2 and provide implementation examples for C firmware')" --output-format json | jq -r '.response' > "research/api-$(basename "$2").md"
        echo "✅ API analysis saved to research/api-$(basename "$2").md"
        ;;
        
    "compare")
        if [ $# -lt 3 ]; then
            echo "Usage: $0 compare <url1> <url2>"
            exit 1
        fi
        echo "⚖️  Comparing firmware approaches..."
        gemini --prompt "web_fetch(prompt='Compare firmware development approaches from $2 and $3, highlighting differences relevant to Flipper Zero')" --output-format json | jq -r '.response' > research/comparison.md
        echo "✅ Comparison saved to research/comparison.md"
        ;;
        
    "community")
        echo "👥 Gathering community insights..."
        urls=(
            "https://github.com/flipperdevices/flipperzero-firmware/discussions"
            "https://forum.flipper.net/"
        )
        
        for url in "${urls[@]}"; do
            echo "Fetching from $url..."
            gemini --prompt "web_fetch(prompt='Summarize recent firmware development discussions from $url')" --output-format json | jq -r '.response' >> research/community-insights.md
            echo "---" >> research/community-insights.md
        done
        echo "✅ Community insights saved to research/community-insights.md"
        ;;
        
    *)
        echo "Web Fetch Research for Momentum Firmware"
        echo "Usage: $0 {docs|security|api <url>|compare <url1> <url2>|community}"
        echo ""
        echo "Commands:"
        echo "  docs      - Fetch Flipper Zero documentation"
        echo "  security  - Research security best practices"
        echo "  api       - Analyze API documentation"
        echo "  compare   - Compare two firmware resources"
        echo "  community - Gather community discussions"
        echo ""
        echo "Examples:"
        echo "  $0 api https://developer.flipper.net/flipperzero/doxygen/"
        echo "  $0 compare https://site1.com https://site2.com"
        ;;
esac