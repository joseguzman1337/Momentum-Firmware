#!/usr/bin/env bash
# PR1M3 Python Environment Setup
# Ensures consistent Python environment across all scripts

# Priority order for Python:
# 1. Anaconda (most stable for this project)
# 2. Homebrew
# 3. System Python

# Export Anaconda Python first in PATH
export PATH="/opt/anaconda3/bin:$PATH"

# Set Python-related environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Increase file descriptor limits for Python
ulimit -Sn 10240 2>/dev/null || true

# Set default Python to Anaconda
alias python=python3
alias pip=pip3

# Verify Python version (stored for prompt use, not displayed)
export PYTHON_VERSION=$(python3 --version 2>&1)
export PYTHON_PATH=$(which python3)

# Store Anaconda status for potential prompt use
if [[ "$PYTHON_PATH" == *"anaconda"* ]]; then
    export PYTHON_ENV_STATUS="✅ Anaconda"
elif [[ "$PYTHON_PATH" == *"homebrew"* ]]; then
    export PYTHON_ENV_STATUS="⚠️  Homebrew"
else
    export PYTHON_ENV_STATUS="⚠️  System"
fi

# To display the Python environment info, run: show_python_env
show_python_env() {
    echo "🐍 Python Environment:"
    echo "   Version: $PYTHON_VERSION"
    echo "   Path: $PYTHON_PATH"
    echo ""
    echo "$PYTHON_ENV_STATUS Python"
    echo ""
}
