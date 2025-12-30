#!/bin/bash
# Real-time telemetry dashboard for firmware development

TELEMETRY_FILE=".ai/.gemini/telemetry.jsonl"

if [ ! -f "$TELEMETRY_FILE" ]; then
    echo "No telemetry data found"
    exit 1
fi

echo "🔍 Momentum Firmware Development Dashboard"
echo "=========================================="

while true; do
    clear
    echo "📊 Live Telemetry ($(date))"
    echo "=============================="

    # Recent activity (last 10 entries)
    echo "Recent Activity:"
    tail -10 "$TELEMETRY_FILE" | jq -r '
        select(.name == "gemini_cli.tool_call" or .name == "gemini_cli.api_request") |
        "\(.timestamp | strftime("%H:%M:%S")) - \(.name): \(.attributes.function_name // .attributes.model)"
    ' 2>/dev/null | tail -5

    echo ""
    echo "Session Stats:"
    echo "- Sessions: $(grep -c "gemini_cli.config" "$TELEMETRY_FILE")"
    echo "- Tool calls: $(grep -c "gemini_cli.tool_call" "$TELEMETRY_FILE")"
    echo "- API requests: $(grep -c "gemini_cli.api_request" "$TELEMETRY_FILE")"
    echo "- Errors: $(grep -c "error" "$TELEMETRY_FILE")"

    echo ""
    echo "Press Ctrl+C to exit"
    sleep 5
done