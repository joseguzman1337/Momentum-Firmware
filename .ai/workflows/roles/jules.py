#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

AGENT_NAME = "Jules"
CLI_CMD = ["jules"]

class AgentRole:
    def __init__(self):
        self.queue_path = Path(".ai/workflows/task_queue.json")
        self.role = AGENT_NAME

    def process(self):
        if not self.queue_path.exists(): return
        
        with open(self.queue_path, "r") as f:
            tasks = json.load(f)
        
        updated = False
        for task in tasks:
            if task["role"].lower() == self.role.lower() and task["status"] == "pending":
                print(f"🤖 [{self.role}] Processing: {task['type']}")
                instruction = task.get("payload", {}).get("instruction", "")
                
                try:
                    cmd = CLI_CMD + [instruction]
                    print(f"   >>> Executing: {' '.join(cmd)}")
                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    print(f"   <<< Output: {proc.stdout[:200]}...")
                    task["status"] = "completed"
                    task["result"] = proc.stdout
                except Exception as e:
                    print(f"   !!! Error: {e}")
                    task["status"] = "failed"
                    task["error"] = str(e)
                
                updated = True
                break
        
        if updated:
            with open(self.queue_path, "w") as f:
                json.dump(tasks, f, indent=4)

if __name__ == "__main__":
    AgentRole().process()
