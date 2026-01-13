#!/usr/bin/env python3
import json
import asyncio
from pathlib import Path
from typing import Dict, Any


class MomentumSubAgent:
    def __init__(self, domain: str):
        self.domain = domain
        self.base_dir = Path(f".ai/mas/{domain}")
        self.task_file = self.base_dir / "pending_tasks.json"
        self.result_file = self.base_dir / "completed_tasks.json"

        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def poll_tasks(self):
        """Poll for new tasks in the pending_tasks.json file."""
        print(f"[{self.domain.upper()} Agent] Polling for tasks...")
        while True:
            if self.task_file.exists():
                try:
                    tasks = json.loads(self.task_file.read_text())
                except json.JSONDecodeError:
                    tasks = []

                if tasks:
                    # Process the first task
                    task = tasks.pop(0)
                    self.task_file.write_text(json.dumps(tasks, indent=2))

                    print(
                        f"[{self.domain.upper()} Agent] Processing task: {task.get('request')}")
                    result = await self.process_task(task)
                    self.save_result(result)

            await asyncio.sleep(2)

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method in sub-agents."""
        return {"status": "completed", "result": "Abstract agent processed task"}

    def save_result(self, result: Dict[str, Any]):
        """Save task result to completed_tasks.json."""
        results = []
        if self.result_file.exists():
            try:
                results = json.loads(self.result_file.read_text())
            except json.JSONDecodeError:
                results = []

        results.append(result)
        self.result_file.write_text(json.dumps(results, indent=2))
        print(f"[{self.domain.upper()} Agent] Task result saved.")


if __name__ == "__main__":
    # This is a base class, but we can run a test if needed
    pass
