#!/usr/bin/env python3
"""
Warp Terminal Automation Wrapper
Executes Warp AI tasks automatically in batch mode
"""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

class WarpAutomation:
    def __init__(self):
        self.repo_root = Path("/Users/x/x/Momentum-Firmware")
        self.task_file = self.repo_root / "warp_agent_tasks.md"
        self.log_dir = self.repo_root / "logs/warp"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def log(self, message: str):
        """Log to file and console"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        log_file = self.log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(log_entry)
        
        print(log_entry.strip())
    
    def parse_tasks(self) -> list:
        """Parse tasks from warp_agent_tasks.md"""
        if not self.task_file.exists():
            return []
        
        with open(self.task_file) as f:
            content = f.read()
        
        tasks = []
        in_task = False
        current_task = {"title": "", "prompt": ""}
        
        for line in content.split("\n"):
            # Task headers
            if line.startswith("### Task"):
                if current_task["prompt"]:
                    tasks.append(current_task)
                current_task = {"title": line.replace("###", "").strip(), "prompt": ""}
                in_task = True
            # Code blocks with prompts
            elif in_task and line.startswith("```") and not current_task["prompt"]:
                in_task = "prompt"
            elif in_task == "prompt" and line.startswith("```"):
                in_task = True
            elif in_task == "prompt":
                current_task["prompt"] += line + " "
        
        if current_task["prompt"]:
            tasks.append(current_task)
        
        return tasks
    
    def execute_task(self, task: dict) -> bool:
        """Execute a single Warp task via Gemini CLI (Warp's AI backend)"""
        self.log(f"Executing: {task['title']}")
        
        prompt = task["prompt"].strip()
        if not prompt:
            self.log("  Skipped: Empty prompt")
            return False
        
        # Use Gemini CLI as Warp's backend (Warp uses Gemini internally)
        log_file = self.log_dir / f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        try:
            result = subprocess.run(
                ["gemini", "-p", prompt, "--approval-mode", "yolo", "-o", "json"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            with open(log_file, "w") as f:
                f.write(f"Task: {task['title']}\n")
                f.write(f"Prompt: {prompt}\n")
                f.write(f"\n--- Output ---\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\n--- Errors ---\n")
                    f.write(result.stderr)
            
            self.log(f"  Completed: {task['title']}")
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.log(f"  Timeout: {task['title']}")
            return False
        except Exception as e:
            self.log(f"  Error: {e}")
            return False
    
    def run_batch(self):
        """Run all tasks in batch mode"""
        self.log("🤖 Warp Automation - Batch Mode")
        self.log("=" * 60)
        
        tasks = self.parse_tasks()
        self.log(f"Found {len(tasks)} tasks")
        
        if not tasks:
            self.log("No tasks to execute")
            return
        
        successful = 0
        failed = 0
        
        for i, task in enumerate(tasks, 1):
            self.log(f"\n[{i}/{len(tasks)}] Processing...")
            if self.execute_task(task):
                successful += 1
            else:
                failed += 1
            
            # Small delay between tasks
            time.sleep(2)
        
        self.log("\n" + "=" * 60)
        self.log(f"📊 Summary: {successful} successful, {failed} failed")
        self.log("=" * 60)

def main():
    automation = WarpAutomation()
    automation.run_batch()

if __name__ == "__main__":
    main()
