#!/bin/bash
# Setup script for Go development tools
# Ensures gopls and other Go tools are installed and accessible

set -e

echo "🔧 Setting up Go development tools..."

# Get GOPATH
GOPATH=$(go env GOPATH)
GOBIN="${GOPATH}/bin"

echo "📍 GOPATH: ${GOPATH}"
echo "📍 GOBIN: ${GOBIN}"

# Install/upgrade gopls (force latest)
echo "📦 Installing/upgrading gopls to latest version..."
go install -v golang.org/x/tools/gopls@latest

# Verify gopls installation
if [ -f "${GOBIN}/gopls" ]; then
    echo "✅ gopls installed at: ${GOBIN}/gopls"
    "${GOBIN}/gopls" version
else
    echo "❌ gopls installation failed"
    exit 1
fi

# Check if GOBIN is in PATH
if echo "$PATH" | grep -q "${GOBIN}"; then
    echo "✅ GOBIN is in PATH"
else
    echo "⚠️  GOBIN is not in PATH"
    echo "   Add this to your shell profile (~/.zshrc, ~/.bashrc, etc.):"
    echo "   export PATH=\"\$PATH:${GOBIN}\""
fi

# Install/upgrade other useful Go tools
echo ""
echo "📦 Installing/upgrading additional Go development tools to latest versions..."

# Go tooling - force latest versions with verbose output
echo "  → goimports..."
go install -v golang.org/x/tools/cmd/goimports@latest

echo "  → golangci-lint..."
go install -v github.com/golangci/golangci-lint/cmd/golangci-lint@latest

echo "  → godoc..."
go install -v golang.org/x/tools/cmd/godoc@latest

echo "  → delve debugger..."
go install -v github.com/go-delve/delve/cmd/dlv@latest

echo ""
echo "✅ Go development tools setup complete!"
echo ""
echo "Installed tools:"
ls -lh "${GOBIN}" | grep -E "gopls|goimports|golangci-lint|godoc|dlv" || echo "  (checking...)"

# Update VS Code settings if .vscode exists
if [ -d ".vscode" ]; then
    echo ""
    echo "✅ VS Code settings already configured for gopls"
    echo "   See: .vscode/settings.json"
fi

echo ""
echo "🎯 Next steps:"
echo "   1. Reload VS Code window (Cmd+Shift+P -> 'Reload Window')"
echo "   2. Open a .go file to verify gopls is working"
echo "   3. If needed, add GOBIN to PATH: export PATH=\"\$PATH:${GOBIN}\""
