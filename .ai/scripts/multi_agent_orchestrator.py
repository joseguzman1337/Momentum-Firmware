#!/usr/bin/env python3
import json
import time
import subprocess
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BASE_DIR = Path(".ai/workflows")
QUEUE_FILE = BASE_DIR / "task_queue.json"
CONTEXT_FILE = BASE_DIR / "compressed_context.json"
ROLES_DIR = BASE_DIR / "roles"
LOG_DIR = BASE_DIR / "logs"

AGENTS = ["Claude", "Codex", "Jules", "Warp", "Gemini", "OpenClaw"]

def log_console(agent, action, detail):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{agent.upper()}] → {action}: {detail}")

def compress_context(state):
    # Logic to summarize and remove redundancy
    compressed = {
        "timestamp": datetime.now().isoformat(),
        "active_goal": state.get("active_goal", "Firmware Hardening"),
        "recent_findings": state.get("findings", [])[-5:], # Keep only last 5
        "completed_tasks": state.get("completed", [])[-3:],
        "status": "COMPRESSED"
    }
    with open(CONTEXT_FILE, "w") as f:
        json.dump(compressed, f, indent=4)
    log_console("ORCHESTRATOR", "Context Updated", "Summary generated and broadcasted")

def get_next_task(agent):
    if not QUEUE_FILE.exists(): return None
    try:
        with open(QUEUE_FILE, "r") as f:
            tasks = json.load(f)
        for task in tasks:
            if task.get("status") == "pending" and (task.get("agent") == agent or task.get("agent") == "ANY"):
                return task
    except (json.JSONDecodeError, KeyError):
        pass
    return None

def update_task_status(task_id, status, output=None):
    with open(QUEUE_FILE, "r+") as f:
        tasks = json.load(f)
        for t in tasks:
            if t["id"] == task_id:
                t["status"] = status
                if output: t["output"] = output
        f.seek(0); json.dump(tasks, f, indent=4); f.truncate()

def execute_agent_task(agent, task):
    log_console(agent, "Assigned Task", task["description"])
    log_console(agent, "Working", "Analyzing firmware modules...")
    
    # Simulate execution via CLI or internal logic
    # In a real run, this would call 'claude -p ...' or similar
    time.sleep(1) 
    
    result = f"Completed {task['type']} for {task['target']}"
    update_task_status(task["id"], "completed", result)
    log_console(agent, "Output", result)

def auto_generate_tasks():
    # Proactive task generation if queue is low
    new_tasks = [
        {"id": str(uuid.uuid4()), "agent": "Claude", "type": "Audit", "target": "furi/core", "description": "Scan for memory leaks", "status": "pending"},
        {"id": str(uuid.uuid4()), "agent": "Codex", "type": "Harden", "target": "applications/main", "description": "Add NULL guards to record access", "status": "pending"},
        {"id": str(uuid.uuid4()), "agent": "Warp", "type": "Analyze", "target": "lib/nfc", "description": "Check buffer bounds in EMV", "status": "pending"},
        {"id": str(uuid.uuid4()), "agent": "Gemini", "type": "Refactor", "target": "targets/f7", "description": "Optimize power management calls", "status": "pending"},
        {"id": str(uuid.uuid4()), "agent": "Jules", "type": "Verify", "target": "unit_tests", "description": "Validate security patches", "status": "pending"}
    ]
    with open(QUEUE_FILE, "w") as f:
        json.dump(new_tasks, f, indent=4)
    log_console("ORCHESTRATOR", "New Task Generated", f"Batch of {len(new_tasks)} tasks added to queue")

def main_loop():
    if not QUEUE_FILE.exists() or os.path.getsize(QUEUE_FILE) == 0:
        auto_generate_tasks()

    while True:
        progress_made = False
        for agent in AGENTS:
            task = get_next_task(agent)
            if task:
                execute_agent_task(agent, task)
                compress_context({"findings": [task["description"]], "completed": [task["id"]]})
                progress_made = True
            
        if not progress_made:
            auto_generate_tasks()
        
        time.sleep(2)

if __name__ == "__main__":
    main_loop()
