#!/bin/bash
# Verification script for Go development tools
# Checks that all tools are installed and functioning

set -e

echo "🔍 Verifying Go Development Tools Setup..."
echo ""

GOBIN=$(go env GOPATH)/bin
ERRORS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
check_tool() {
    local tool=$1
    local version_cmd=$2
    local path="${GOBIN}/${tool}"

    if [ -f "$path" ]; then
        echo -e "${GREEN}✅ ${tool}${NC}"
        if [ -n "$version_cmd" ]; then
            echo "   Version: $("$path" $version_cmd 2>&1 | head -1)"
        fi
        echo "   Path: $path"
        echo ""
    else
        echo -e "${RED}❌ ${tool}${NC} - NOT FOUND"
        echo "   Expected at: $path"
        echo ""
        ERRORS=$((ERRORS + 1))
    fi
}

echo "📍 Go Environment:"
echo "   GOPATH: $(go env GOPATH)"
echo "   GOBIN: ${GOBIN}"
echo "   Go version: $(go version)"
echo ""

echo "🔧 Checking Tools:"
echo "---"

# Check each tool
check_tool "gopls" "version"
check_tool "goimports" ""
check_tool "golangci-lint" "version --format short"
check_tool "godoc" ""
check_tool "dlv" "version"

# Check VS Code settings
echo "📝 VS Code Configuration:"
if [ -f ".vscode/settings.json" ]; then
    if grep -q "gopls" ".vscode/settings.json"; then
        echo -e "${GREEN}✅ VS Code settings configured${NC}"
        echo "   gopls path in settings.json: $(grep -A1 'alternateTools' .vscode/settings.json | grep gopls | cut -d'"' -f4)"
    else
        echo -e "${YELLOW}⚠️  gopls not found in VS Code settings${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  .vscode/settings.json not found${NC}"
fi
echo ""

# Check PATH
echo "🛤️  PATH Configuration:"
if echo "$PATH" | grep -q "${GOBIN}"; then
    echo -e "${GREEN}✅ GOBIN is in PATH${NC}"
else
    echo -e "${YELLOW}⚠️  GOBIN not in PATH${NC}"
    echo "   Tools will work in VS Code but not in terminal"
    echo "   Add to ~/.zshrc or ~/.bashrc:"
    echo "   export PATH=\"\$PATH:${GOBIN}\""
fi
echo ""

# Final summary
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Reload VS Code: Cmd+Shift+P → 'Reload Window'"
    echo "2. Open a .go file to test gopls"
    echo "3. See .vscode/GO_SETUP_COMPLETE.md for details"
else
    echo -e "${RED}❌ Found $ERRORS issue(s)${NC}"
    echo ""
    echo "To fix issues, run:"
    echo "  ./scripts/setup-go-tools.sh"
fi
echo "=========================================="
