#!/usr/bin/env python3
import json
import time
import subprocess
import os
from pathlib import Path

# Paths
ROLES_DIR = Path(".ai/workflows/roles")
QUEUE_FILE = Path(".ai/workflows/task_queue.json")
PUSHER_SCRIPT = Path(".ai/scripts/real_time_pusher.sh")
TASK_GENERATOR = Path(".ai/scripts/shared_task_queue.py")

def log_claw(msg):
    print(f"🦞 [OpenClaw Orchestrator] {msg}")

def run_role(role_script):
    log_claw(f"Executing Agent: {role_script.name}")
    result = subprocess.run(["python3", str(role_script)], capture_output=True, text=True)
    if result.stdout: print(result.stdout)
    if result.stderr: print(result.stderr)

def main_loop():
    log_claw("Master Control Active. Ensuring continuous operation...")
    
    while True:
        # 1. Ensure tasks exist
        with open(QUEUE_FILE, "r") as f:
            tasks = json.load(f)
        
        pending_tasks = [t for t in tasks if t["status"] == "pending"]
        
        if not pending_tasks:
            log_claw("Queue empty. Proactively generating new hardening tasks...")
            subprocess.run(["python3", str(TASK_GENERATOR)])
            continue # Re-check queue

        # 2. Execute roles in sequence for the first pending task
        task = pending_tasks[0]
        role_script = ROLES_DIR / f"{task['role'].lower().replace('agent', '')}.py"
        
        if role_script.exists():
            run_role(role_script)
            
            # 3. Real-time Push
            log_claw("Task processed. Synchronizing to remote...")
            commit_msg = f"OpenClaw: Processed {task['type']} for {task['role']}"
            subprocess.run([str(PUSHER_SCRIPT), commit_msg])
        else:
            log_claw(f"Warning: No script found for role {task['role']}")
            # Mark as skipped/completed to avoid loop
            with open(QUEUE_FILE, "r+") as f:
                tasks = json.load(f)
                for t in tasks:
                    if t["id"] == task["id"]: t["status"] = "skipped"
                f.seek(0); json.dump(tasks, f, indent=4); f.truncate()

        time.sleep(2) # Throttle to prevent CPU exhaustion

if __name__ == "__main__":
    main_loop()
