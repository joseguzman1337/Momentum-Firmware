#!/usr/bin/env python3
"""
Entrypoint for Flipper Zero Emulator Model Context Protocol (MCP) Server.
Communicates via JSON-RPC 2.0 over standard I/O (stdio).
"""

import sys
import os

# Add local path to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from integration_server import EmulatorV2MCPServer

def main():
    server = EmulatorV2MCPServer()
    server.run_stdio()

if __name__ == "__main__":
    main()
