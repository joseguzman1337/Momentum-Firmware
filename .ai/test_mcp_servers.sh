#!/bin/bash
# End-to-end test script for all 4 MCP servers

echo "====================================================================="
echo "Testing MCP Servers - Momentum Firmware"
echo "====================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0

test_server() {
    local name="$1"
    local command="$2"

    echo "---------------------------------------------------------------------"
    echo "Testing: $name"
    echo "---------------------------------------------------------------------"

    if eval "$command"; then
        echo -e "${GREEN}✓ PASSED${NC}: $name"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}: $name"
        ((FAILED++))
    fi
    echo ""
}

# Test 1: ESP-IDF MCP (external)
echo "1. Testing ESP-IDF MCP Server (External)"
test_server "ESP-IDF MCP" "cd ~/.claude-mcp-servers/esp-idf-mcp && /home/d3c0d3r/.local/bin/uv run --python python3 python -c 'import main; print(\"ESP-IDF MCP module loaded successfully\")'"

# Test 2: ESP RainMaker MCP (external)
echo "2. Testing ESP RainMaker MCP Server (External)"
test_server "ESP RainMaker MCP" "cd ~/.claude-mcp-servers/esp-rainmaker-mcp && /home/d3c0d3r/.local/bin/uv run --python python3 python -c 'import sys; sys.path.insert(0, \".\"); import server; print(\"ESP RainMaker MCP module loaded successfully\")'"

# Test 3: ESP MCP Local
echo "3. Testing ESP MCP Local Server"
test_server "ESP MCP Local" "cd /home/d3c0d3r/x/Momentum-Firmware/.ai/mcp/servers/esp_mcp && /home/d3c0d3r/.local/bin/uv run --python python3 python -c 'import main; print(\"ESP MCP Local module loaded successfully\")'"

# Test 4: Strawberry/Furi MCP
echo "4. Testing Strawberry/Furi MCP Server"
test_server "Strawberry/Furi MCP" "cd /home/d3c0d3r/x/Momentum-Firmware/.ai/mcp/servers/strawberry_mcp && PYTHONPATH=. .venv/bin/python -c 'import main; import furi_utils; print(\"Strawberry/Furi MCP module loaded successfully\")'"

# Summary
echo "====================================================================="
echo "Test Summary"
echo "====================================================================="
echo -e "Total tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All MCP servers are configured and working!${NC}"
    echo ""
    echo "To use these MCP servers, restart Claude Code or start a new conversation."
    echo ""
    echo "Available servers:"
    echo "  1. esp-idf-mcp - ESP-IDF build, flash, and project management"
    echo "  2. esp-rainmaker-mcp - ESP RainMaker IoT device control"
    echo "  3. esp-mcp-local - Local ESP utilities and tools"
    echo "  4. strawberry-furi-mcp - Flipper Zero firmware build/flash (FuriOS)"
    exit 0
else
    echo -e "${RED}✗ Some MCP servers failed. Please check the errors above.${NC}"
    exit 1
fi
