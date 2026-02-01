#!/usr/bin/env python3
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

class TaskRegistry:
    def __init__(self, registry_path=".ai/workflows/task_registry.json"):
        self.path = Path(registry_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"tasks": []}, indent=4))
    
    def register_task(self, agent, task_name, status="started"):
        data = json.loads(self.path.read_text())
        task_id = str(uuid.uuid4())[:8]
        task = {
            "id": task_id,
            "agent": agent,
            "name": task_name,
            "status": status,
            "started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        data["tasks"].append(task)
        self.path.write_text(json.dumps(data, indent=4))
        return task_id

    def update_task(self, task_id, status, result=None):
        data = json.loads(self.path.read_text())
        for task in data["tasks"]:
            if task["id"] == task_id:
                task["status"] = status
                task["updated_at"] = datetime.now().isoformat()
                if result:
                    task["result"] = result
                break
        self.path.write_text(json.dumps(data, indent=4))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        registry = TaskRegistry()
        action = sys.argv[1]
        if action == "register":
            agent = sys.argv[2]
            name = sys.argv[3]
            tid = registry.register_task(agent, name)
            print(tid)
        elif action == "update":
            tid = sys.argv[2]
            status = sys.argv[3]
            registry.update_task(tid, status)
