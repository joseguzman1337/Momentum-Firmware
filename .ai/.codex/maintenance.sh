#!/bin/bash
# Codex maintenance script

# Update git submodules
git submodule update --init --recursive

# Update Python dependencies
pip3 install --upgrade scons protobuf grpcio-tools