#!/bin/bash
# Codex setup script for Momentum Firmware

# Install build dependencies
apt-get update && apt-get install -y \
    gcc-arm-none-eabi \
    build-essential \
    git \
    python3 \
    python3-pip

# Install Python dependencies
pip3 install scons protobuf grpcio-tools

# Set environment variables
echo "export TOOLCHAIN_PATH=/usr/bin" >> ~/.bashrc
echo "export FBT_TOOLCHAIN_PATH=/usr/bin" >> ~/.bashrc