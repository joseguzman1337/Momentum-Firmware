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

    # 1. DataIngestor: Global Security Scan
    add_task("DataIngestor", "security_scan", {
        "targets": ["furi/core", "applications/main", "applications/services"],
        "skill": "furi_audit"
    })

    # 2. ModelTrainer: Remediation of NULL Dereferences (Issue #395 context)
    add_task("ModelTrainer", "harden_allocations", {
        "focus": "furi_check addition to all malloc/alloc calls in targets",
        "strategy": "atomic_patch"
    })

    # 3. APIBuilder: Furi Record Safety
    add_task("APIBuilder", "harden_records", {
        "focus": "Validate furi_record_open returns in all applications",
        "strategy": "null_guard_insertion"
    })

    # 4. TestRunner: Continuous Verification
    add_task("TestRunner", "verify_hardening", {
        "command": "./run_unit_tests.py",
        "scope": "core_security"
    })

    # 5. Deployer: Real-time Deployment
    add_task("Deployer", "push_hardened_firmware", {
        "branch": "next",
        "strategy": "force-with-lease"
    })

if __name__ == "__main__":
    seed_firmware_hardening_sprint()