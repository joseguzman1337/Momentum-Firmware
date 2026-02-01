#!/usr/bin/env python3
import json
import uuid
import os
from pathlib import Path

QUEUE_FILE = Path(".ai/workflows/task_queue.json")

def add_task(role, task_type, payload, granularity="atomic"):
    if not QUEUE_FILE.exists():
        QUEUE_FILE.write_text("[]")
    with open(QUEUE_FILE, "r") as f:
        tasks = json.load(f)
    
    task = {
        "id": str(uuid.uuid4()),
        "role": role,
        "type": task_type,
        "payload": payload,
        "granularity": granularity,
        "status": "pending"
    }
    tasks.append(task)
    with open(QUEUE_FILE, "w") as f:
        json.dump(tasks, f, indent=4)
    print(f"Added {granularity} task for {role}: {task_type}")

def seed_firmware_hardening_sprint():
    # Clear queue to ensure OpenClaw takes fresh control
    with open(QUEUE_FILE, "w") as f:
        json.dump([], f)

    # 1. Claude: Security Analysis
    add_task("Claude", "security_audit", {
        "instruction": "Analyze SECURITY.md and suggest 3 key improvements for 2026."
    })

    # 2. Codex: Code Implementation
    add_task("Codex", "feature_impl", {
        "instruction": "Write a python script scripts/hello_codex.py that prints 'Hello from Codex'."
    })

    # 3. Jules: PR/Branch Management
    add_task("Jules", "pr_check", {
        "instruction": "Check for any stale branches starting with 'jules-' and list them."
    })

    # 4. Warp: Optimization
    add_task("Warp", "code_opt", {
        "instruction": "Suggest optimizations for the main build script SConstruct."
    })

    # 5. Gemini: Orchestration/Summary
    add_task("Gemini", "status_report", {
        "instruction": "Generate a brief status report of the .ai directory structure."
    })

if __name__ == "__main__":
    seed_firmware_hardening_sprint()