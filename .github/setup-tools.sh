#!/bin/bash
# Auto-install all required development and CI tools silently
# This script installs: gh CLI, Python dependencies, Node dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output (only if terminal supports it)
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    NC='\033[0m'
else
    GREEN=''
    YELLOW=''
    RED=''
    NC=''
fi

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Install GitHub CLI if not present
install_gh_cli() {
    if command -v gh &> /dev/null; then
        log_info "gh CLI already installed: $(gh --version | head -1)"
        return 0
    fi

    log_info "Installing GitHub CLI..."

    # Try apt first (Debian/Ubuntu)
    if command -v apt-get &> /dev/null; then
        if sudo apt-get update -qq && sudo apt-get install -qq -y gh 2>/dev/null; then
            log_info "gh CLI installed via apt"
            return 0
        fi
    fi

    # Fallback to direct binary download
    GH_VERSION="${GH_VERSION:-2.63.0}"
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64) ARCH="amd64" ;;
        aarch64) ARCH="arm64" ;;
        armv7l) ARCH="armv6" ;;
    esac

    log_info "Installing gh CLI v${GH_VERSION} via direct download..."
    curl -sL "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_${ARCH}.tar.gz" | tar xz -C /tmp
    sudo mv "/tmp/gh_${GH_VERSION}_linux_${ARCH}/bin/gh" /usr/local/bin/
    rm -rf "/tmp/gh_${GH_VERSION}_linux_${ARCH}"

    if command -v gh &> /dev/null; then
        log_info "gh CLI installed: $(gh --version | head -1)"
    else
        log_error "Failed to install gh CLI"
        return 1
    fi
}

# Install Python dependencies
install_python_deps() {
    local requirements_file="$REPO_ROOT/.ai/requirements.txt"

    if [ ! -f "$requirements_file" ]; then
        log_warn "No Python requirements file found at $requirements_file"
        return 0
    fi

    if ! command -v pip3 &> /dev/null; then
        log_warn "pip3 not found, skipping Python dependencies"
        return 0
    fi

    log_info "Installing Python dependencies from $requirements_file..."
    pip3 install -q --user -r "$requirements_file" 2>/dev/null || \
        pip3 install -q -r "$requirements_file" 2>/dev/null || \
        log_warn "Some Python dependencies may have failed to install"

    log_info "Python dependencies installed"
}

# Install Node dependencies
install_node_deps() {
    local package_dir="$REPO_ROOT/.ai/codex-sdk"

    if [ ! -f "$package_dir/package.json" ]; then
        log_warn "No package.json found at $package_dir"
        return 0
    fi

    if ! command -v npm &> /dev/null; then
        log_warn "npm not found, skipping Node dependencies"
        return 0
    fi

    log_info "Installing Node dependencies from $package_dir..."
    cd "$package_dir"
    npm install --silent 2>/dev/null || log_warn "Some Node dependencies may have failed to install"
    cd - > /dev/null

    log_info "Node dependencies installed"
}

# Install additional useful tools
install_extra_tools() {
    # jq for JSON parsing
    if ! command -v jq &> /dev/null; then
        log_info "Installing jq..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -qq -y jq 2>/dev/null || true
        fi
    fi
}

# Main
main() {
    log_info "Setting up development tools for Momentum Firmware..."
    echo ""

    install_gh_cli
    install_python_deps
    install_node_deps
    install_extra_tools

    echo ""
    log_info "Setup complete! Installed tools:"
    echo "  - gh:      $(command -v gh 2>/dev/null && gh --version | head -1 || echo 'not installed')"
    echo "  - python3: $(command -v python3 2>/dev/null && python3 --version || echo 'not installed')"
    echo "  - pip3:    $(command -v pip3 2>/dev/null && pip3 --version | cut -d' ' -f1-2 || echo 'not installed')"
    echo "  - node:    $(command -v node 2>/dev/null && node --version || echo 'not installed')"
    echo "  - npm:     $(command -v npm 2>/dev/null && npm --version || echo 'not installed')"
    echo "  - jq:      $(command -v jq 2>/dev/null && jq --version || echo 'not installed')"
}

# Run if executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
