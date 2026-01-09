#!/usr/bin/env python3
"""Codex MCP Agent for Momentum Firmware"""

import asyncio
import os
import json
from datetime import datetime
from pathlib import Path

from agents import Agent, Runner, set_default_openai_api
from agents.mcp import MCPServerStdio

# Setup logging
log_dir = Path("logs/codex")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"codex_{datetime.now().strftime('%Y%m%d')}.log"

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

async def main():
    # Load API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        log("ERROR: OPENAI_API_KEY not found")
        return
    
    set_default_openai_api(api_key)
    
    async with MCPServerStdio(
        name="Codex CLI",
        params={
            "command": "npx",
            "args": ["-y", "codex", "mcp-server"],
        },
        client_session_timeout_seconds=360000,
    ) as codex_mcp_server:
        
        # Firmware Developer Agent
        firmware_agent = Agent(
            name="Firmware Developer",
            instructions=(
                "You are an expert C/C++ firmware developer for Flipper Zero. "
                "Focus on embedded systems, hardware interfaces, and firmware optimization. "
                "Always use approval-policy: never and sandbox: workspace-write when calling codex. "
                "Work within the Momentum Firmware codebase structure."
            ),
            mcp_servers=[codex_mcp_server],
        )
        
        # Issue Processor Agent  
        issue_agent = Agent(
            name="Issue Processor",
            instructions=(
                "You process GitHub issues for Momentum Firmware. "
                "Analyze issue content, classify by type (bug/feature/enhancement), "
                "and hand off to appropriate developer agents. "
                "Create fixes that maintain firmware stability and compatibility."
            ),
            handoffs=[firmware_agent],
        )
        
        log("Codex MCP agents initialized")
        
        # Monitor for issues (simplified for minimal implementation)
        sample_task = "Fix memory leak in SubGHz frequency scanner module"
        result = await Runner.run(issue_agent, sample_task)
        
        log(f"Task completed: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())