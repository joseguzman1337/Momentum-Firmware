#!/usr/bin/env python3
import json
import time
import subprocess
import os
import uuid
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION ---
BASE_DIR = Path(".ai/workflows")
LEDGER_FILE = BASE_DIR / "task_ledger.json"
CONTEXT_FILE = BASE_DIR / "compressed_context.json"

AGENT_POOL = [
    "Claude", "Codex", "Jules", "Warp", "Gemini", "OpenClaw",
    "DeepSeek", "Ollama", "Kiro", "AmazonQ", "Llama", "HuggingFace", "NVIDIA"
]

# --- UTILS ---
def log_console(agent, action, detail):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{agent.upper()}] → {action}: {detail}")

def orchestrator_log(action, detail):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] [ORCHESTRATOR] → {action}: {detail}")

def compress_context():
    if not LEDGER_FILE.exists(): return
    with open(LEDGER_FILE, "r") as f:
        ledger = json.load(f)
    
    active_tasks = [t["type"] + ":" + t["target"] for t in ledger if t["status"] == "active"]
    summary = f"Active: {len(active_tasks)} | Completed: {len([t for t in ledger if t['status'] == 'completed'])}"
    
    ctx = {
        "ts": datetime.now().isoformat(),
        "summary": summary,
        "active_tasks": active_tasks
    }
    with open(CONTEXT_FILE, "w") as f:
        json.dump(ctx, f)
    orchestrator_log("Context Updated (compressed)", summary)

def validate_task(task, ledger):
    # Rule 2: Strict task uniqueness
    for entry in ledger:
        if entry["status"] == "active" and entry["target"] == task["target"] and entry["type"] == task["type"]:
            return False, "rejected"
    return True, "unique"

def assign_task(agent, task_type, target, description):
    if not LEDGER_FILE.exists():
        ledger = []
    else:
        with open(LEDGER_FILE, "r") as f:
            ledger = json.load(f)
    
    new_task = {
        "id": str(uuid.uuid4()),
        "agent": agent,
        "type": task_type,
        "target": target,
        "description": description,
        "status": "active",
        "start_time": datetime.now().isoformat()
    }
    
    valid, status = validate_task(new_task, ledger)
    orchestrator_log("Task Validated", f"{status.upper()} / {agent} -> {target}")
    
    if valid:
        ledger.append(new_task)
        with open(LEDGER_FILE, "w") as f:
            json.dump(ledger, f, indent=4)
        log_console(agent, "Assigned Task", description)
        return True
    return False

def complete_task(agent, result):
    with open(LEDGER_FILE, "r") as f:
        ledger = json.load(f)
    
    for t in ledger:
        if t["agent"] == agent and t["status"] == "active":
            t["status"] = "completed"
            t["result"] = result
            t["end_time"] = datetime.now().isoformat()
            log_console(agent, "Output", result)
            break
            
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=4)
    
    compress_context()

def generate_new_task(agent):
    # Rule 3: Auto-generate new tasks based on gaps
    # For now, seeding with firmware hardening targets
    targets = [
        ("Audit", "furi/core", "Scan Furi Core for memory leaks and NULL dereferences"),
        ("Harden", "lib/lwip", "Secure network stack against buffer overflows"),
        ("Analyze", "applications/main/nfc", "Verify NFC protocol parsers for bounds safety"),
        ("Secure", "lib/crypto", "Audit SECP256R1 implementation"),
        ("Verify", "targets/f7", "Validate power management hardware abstraction"),
        ("Refactor", "applications/services", "Optimize inter-process communication")
    ]
    
    with open(LEDGER_FILE, "r") as f:
        ledger = json.load(f)
    
    assigned_targets = [t["target"] for t in ledger if t["status"] == "active"]
    
    for task_type, target, desc in targets:
        if target not in assigned_targets:
            if assign_task(agent, task_type, target, desc):
                orchestrator_log("New Task Generated", f"{agent} -> {target}")
                return True
    return False

# --- MAIN LOOP ---
def orchestrate():
    orchestrator_log("Master Control Active", "Continuous Multi-Agent Orchestration loop initiated.")
    
    # Initial seeding
    active_agents = AGENT_POOL[:5] # Start with first 5 agents
    for agent in active_agents:
        generate_new_task(agent)

    while True:
        with open(LEDGER_FILE, "r") as f:
            ledger = json.load(f)
        
        active_entries = [t for t in ledger if t["status"] == "active"]
        
        for t in active_entries:
            agent = t["agent"]
            log_console(agent, "Working", f"Processing {t['target']}...")
            
            # Simulated completion for loop demonstration
            # In real execution, we would call the agent's specific tool/CLI
            time.sleep(1)
            complete_task(agent, f"Successfully audited {t['target']}")
            
            # Replace completed task
            generate_new_task(agent)
            
        time.sleep(2)

if __name__ == "__main__":
    orchestrate()