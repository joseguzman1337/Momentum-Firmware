#!/bin/bash
# Analyze Gemini CLI telemetry for Momentum Firmware development

set -e

TELEMETRY_FILE=".gemini/telemetry.jsonl"

if [ ! -f "$TELEMETRY_FILE" ]; then
    echo "No telemetry data found. Enable telemetry in settings first."
    exit 1
fi

case "$1" in
    "summary")
        echo "📊 Firmware Development Telemetry Summary"
        echo "========================================"
        
        # Session count
        sessions=$(grep "gemini_cli.config" "$TELEMETRY_FILE" | wc -l)
        echo "Sessions: $sessions"
        
        # Tool usage
        echo "Top tools used:"
        grep "gemini_cli.tool_call" "$TELEMETRY_FILE" | \
        jq -r '.attributes.function_name' | sort | uniq -c | sort -nr | head -5
        
        # Build-related activity
        builds=$(grep -E "(fbt|build)" "$TELEMETRY_FILE" | wc -l)
        echo "Build-related operations: $builds"
        
        # Token usage
        tokens=$(grep "gen_ai.client.token.usage" "$TELEMETRY_FILE" | \
        jq -r '.attributes."gen_ai.usage.input_tokens" + .attributes."gen_ai.usage.output_tokens"' | \
        awk '{sum+=$1} END {print sum}')
        echo "Total tokens used: ${tokens:-0}"
        ;;
        
    "errors")
        echo "🚨 Error Analysis"
        echo "================"
        grep "gemini_cli.api_error\|error" "$TELEMETRY_FILE" | \
        jq -r '.attributes.error_type // .attributes.error' | sort | uniq -c
        ;;
        
    "performance")
        echo "⚡ Performance Metrics"
        echo "===================="
        
        # API latency
        echo "Average API response time:"
        grep "gemini_cli.api_response" "$TELEMETRY_FILE" | \
        jq -r '.attributes.duration_ms' | awk '{sum+=$1; count++} END {print sum/count "ms"}'
        
        # Tool latency
        echo "Average tool execution time:"
        grep "gemini_cli.tool_call" "$TELEMETRY_FILE" | \
        jq -r '.attributes.duration_ms' | awk '{sum+=$1; count++} END {print sum/count "ms"}'
        ;;
        
    "export")
        output_file="telemetry_report_$(date +%Y%m%d_%H%M%S).json"
        echo "Exporting telemetry analysis to $output_file..."
        
        {
            echo "{"
            echo "  \"summary\": {"
            echo "    \"sessions\": $(grep "gemini_cli.config" "$TELEMETRY_FILE" | wc -l),"
            echo "    \"tool_calls\": $(grep "gemini_cli.tool_call" "$TELEMETRY_FILE" | wc -l),"
            echo "    \"api_requests\": $(grep "gemini_cli.api_request" "$TELEMETRY_FILE" | wc -l),"
            echo "    \"errors\": $(grep "error" "$TELEMETRY_FILE" | wc -l)"
            echo "  },"
            echo "  \"generated_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
            echo "}"
        } > "$output_file"
        echo "✅ Report exported to $output_file"
        ;;
        
    *)
        echo "Momentum Firmware Telemetry Analyzer"
        echo "Usage: $0 {summary|errors|performance|export}"
        echo ""
        echo "Commands:"
        echo "  summary     - Show development activity summary"
        echo "  errors      - Analyze error patterns"
        echo "  performance - Show performance metrics"
        echo "  export      - Export analysis to JSON"
        ;;
esac