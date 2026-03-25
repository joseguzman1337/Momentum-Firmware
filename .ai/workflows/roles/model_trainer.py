#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path

class ModelTrainer:
    def __init__(self, queue_path=".ai/workflows/task_queue.json"):
        self.queue_path = Path(queue_path)
        self.role = "ModelTrainer"

    def process(self):
        if not self.queue_path.exists(): return
        with open(self.queue_path, "r") as f:
            tasks = json.load(f)
        
        updated = False
        for task in tasks:
            if task["role"] == self.role and task["status"] == "pending":
                if task["type"] == "harden_allocations":
                    print(f"[{self.role}] Executing Real-time Hardening...")
                    # Search for unchecked malloc in furi core
                    targets = ["furi/core/record.c", "furi/core/message_queue.c"]
                    for target in targets:
                        if os.path.exists(target):
                            with open(target, "r") as tf:
                                content = tf.read()
                            # Replace malloc with furi_check(malloc)
                            # This is a simplified regex for the demonstration of 'control'
                            new_content = re.sub(r"([a-zA-Z0-9_]+) = malloc\(([^)]+)\);", r"\1 = malloc(\2);\n    furi_check(\1);", content)
                            if new_content != content:
                                with open(target, "w") as tf:
                                    tf.write(new_content)
                                print(f"[{self.role}] Hardened {target}")
                    
                    task["status"] = "completed"
                    updated = True
                    break
        
        if updated:
            with open(self.queue_path, "w") as f:
                json.dump(tasks, f, indent=4)

if __name__ == "__main__":
    ModelTrainer().process()
