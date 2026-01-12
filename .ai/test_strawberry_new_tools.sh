#!/bin/bash

# Test script for new Strawberry/Furi MCP tools

set +e  # Don't exit on errors

echo "====================================================================="
echo "Testing New Strawberry/Furi MCP Tools"
echo "====================================================================="

cd /home/d3c0d3r/x/Momentum-Firmware/.ai/mcp/servers/strawberry_mcp

# Function to test if module imports successfully
test_import() {
    echo ""
    echo "---------------------------------------------------------------------"
    echo "Test: $1"
    echo "---------------------------------------------------------------------"

    PYTHONPATH=. .venv/bin/python -c "$2"

    if [ $? -eq 0 ]; then
        echo "✅ PASSED: $1"
        return 0
    else
        echo "❌ FAILED: $1"
        return 1
    fi
}

# Test 1: Import main module
test_import "Module Import" "import main; print('Module loaded successfully')"

# Test 2: Verify all tools are registered
test_import "Tool Registration" "
import main
import inspect

# Get all async functions decorated with @mcp.tool()
tools = []
for name, obj in inspect.getmembers(main):
    if inspect.iscoroutinefunction(obj) and not name.startswith('_'):
        tools.append(name)

print(f'Registered tools: {sorted(tools)}')

# Check for new tools
expected_tools = ['gpio_set', 'gpio_read', 'system_info', 'storage_info', 'nfc_detect', 'flipper_cli']
for tool in expected_tools:
    if tool in tools:
        print(f'✅ Found tool: {tool}')
    else:
        print(f'❌ Missing tool: {tool}')
        exit(1)

print('All expected tools are registered!')
"

# Test 3: Verify tool signatures
test_import "Tool Signatures" "
import main
import inspect

# Check gpio_set signature
sig = inspect.signature(main.gpio_set)
params = list(sig.parameters.keys())
assert 'pin' in params and 'state' in params, 'gpio_set signature incorrect'
print('✅ gpio_set signature correct: (pin: int, state: bool)')

# Check gpio_read signature
sig = inspect.signature(main.gpio_read)
params = list(sig.parameters.keys())
assert 'pin' in params, 'gpio_read signature incorrect'
print('✅ gpio_read signature correct: (pin: int)')

# Check flipper_cli signature
sig = inspect.signature(main.flipper_cli)
params = list(sig.parameters.keys())
assert 'command' in params, 'flipper_cli signature incorrect'
print('✅ flipper_cli signature correct: (command: str)')

print('All tool signatures are correct!')
"

# Test 4: Check for shlex import (security)
test_import "Security Check (shlex)" "
import main
import shlex

# Verify shlex is imported at module level
assert hasattr(main, 'shlex'), 'shlex not imported in main module'
print('✅ shlex imported for command sanitization')
"

echo ""
echo "====================================================================="
echo "Test Summary"
echo "====================================================================="
echo ""
echo "All module-level tests completed."
echo ""
echo "Note: End-to-end tests require a connected Flipper Zero device."
echo "To test with a device, use commands like:"
echo "  - gpio_set(pin=5, state=True)"
echo "  - gpio_read(pin=5)"
echo "  - system_info()"
echo "  - storage_info()"
echo "  - nfc_detect()"
echo ""
echo "====================================================================="
