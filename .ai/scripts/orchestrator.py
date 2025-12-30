#!/usr/bin/env python3
"""AI Agent Orchestrator for Momentum Firmware"""

import asyncio
import subprocess
import sys
from pathlib import Path

def start_agent(agent_path):
    """Start an AI agent process"""
    try:
        if not Path(agent_path).exists():
            raise FileNotFoundError(f"Agent script not found: {agent_path}")
        return subprocess.Popen([sys.executable, agent_path], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"Failed to start {agent_path}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error starting {agent_path}: {e}")
        return None

async def main():
    if "--yolo-mode" not in sys.argv:
        print("Use --yolo-mode to activate all agents")
        return
    
    # Ensure log directories exist
    for agent in ["codex", "codex-cloud", "claude", "jules", "gemini", "deepseek", "warp", "amazonq", "kiro"]:
        Path(f"logs/{agent}").mkdir(parents=True, exist_ok=True)
    
    # Start all agents
    agents = []
    agent_paths = [
        ".ai/codex/agent.py",
        # Add other agent paths as they're implemented
    ]
    
    for path in agent_paths:
        if Path(path).exists():
            process = start_agent(path)
            if process:
                agents.append(process)
                print(f"Started agent: {path}")
    
    print(f"YOLO Mode: {len(agents)} agents running")
    
    # Keep orchestrator running
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down agents...")
        for process in agents:
            process.terminate()

if __name__ == "__main__":
    asyncio.run(main())