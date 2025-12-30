#!/bin/bash
set -e

# Install ARM toolchain for Flipper Zero
if [ "$CLAUDE_CODE_REMOTE" = "true" ]; then
    apt-get update -qq
    apt-get install -y gcc-arm-none-eabi
fi

# Install Python dependencies
pip install -r scripts/requirements.txt

# Setup git submodules
git submodule update --init --recursive

echo "Environment setup complete"