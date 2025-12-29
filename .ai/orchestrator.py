#!/usr/bin/env python3
"""AI Agent Orchestrator for Momentum Firmware"""

import asyncio
import subprocess
import sys
from pathlib import Path
import os

def start_agent(agent_path):
    """Start an AI agent process"""
    try:
        # Sanitize path to prevent traversal attacks
        safe_path = Path(agent_path).resolve()
        if not safe_path.is_relative_to(Path.cwd()):
            raise ValueError(f"Path outside project directory: {agent_path}")
        if not safe_path.exists():
            raise FileNotFoundError(f"Agent script not found: {safe_path}")
        return subprocess.Popen([sys.executable, str(safe_path)], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
    except (FileNotFoundError, PermissionError, OSError, ValueError) as e:
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
    agents_list = ["codex", "codex-cloud", "claude", "jules", "gemini", "deepseek", "warp", "amazonq", "kiro"]
    for agent in agents_list:
        log_dir = Path("logs") / agent
        log_dir.mkdir(parents=True, exist_ok=True)
    
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
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Force killing process {process.pid}")
                try:
                    process.kill()
                    process.wait(timeout=2)
                except (ProcessLookupError, OSError) as e:
                    print(f"Process {process.pid} already terminated: {e}")
            except (ProcessLookupError, OSError) as e:
                print(f"Process {process.pid} not found: {e}")
            except Exception as e:
                print(f"Error shutting down process {process.pid}: {e}")

if __name__ == "__main__":
    asyncio.run(main())