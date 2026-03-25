#!/usr/bin/env python3
import subprocess
import time
import sys
import os
from pathlib import Path


def start_process(name, path):
    print(f"Starting {name} agent...")
    return subprocess.Popen([sys.executable, path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True)


def main():
    base_path = Path(".ai/mas")
    agents = {
        "Protocol": base_path / "protocol" / "agent.py",
        "UI_Asset": base_path / "ui_asset" / "agent.py",
        "Core_System": base_path / "core_system" / "agent.py",
    }

    processes = {}

    try:
        # Start sub-agents
        for name, path in agents.items():
            if path.exists():
                processes[name] = start_process(name, str(path))
            else:
                print(f"Warning: {name} agent script not found at {path}")

        print("\nAll MAS agents are running.")
        print(
            "To send a task, use: python3 .ai/mas/supervisor/supervisor.py 'YOUR REQUEST'")

        while True:
            # Monitor processes
            for name, proc in processes.items():
                if proc.poll() is not None:
                    print(f"Error: {name} agent crashed. Restarting...")
                    processes[name] = start_process(name, str(agents[name]))
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nShutting down MAS...")
        for name, proc in processes.items():
            print(f"Terminating {name}...")
            proc.terminate()
        print("Done.")


if __name__ == "__main__":
    main()
