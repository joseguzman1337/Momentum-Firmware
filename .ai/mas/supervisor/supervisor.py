#!/usr/bin/env python3
import json
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List


class MomentumSupervisor:
    def __init__(self):
        self.agents = {
            "protocol": {
                "description": "Handles SubGHz, NFC, RFID, and Signal Processing logic.",
                "keywords": ["subghz", "nfc", "rfid", "protocol", "signal", "parser", "ir", "infrared"]
            },
            "ui_asset": {
                "description": "Manages Asset Packs, icons, and Furi GUI layout.",
                "keywords": ["asset", "icon", "gui", "ui", "view", "canvas", "layout", "graphics"]
            },
            "core_system": {
                "description": "Handles FBT (Flipper Build Tool), compilation, linting, and OS core.",
                "keywords": ["fbt", "build", "compile", "flash", "furi", "kernel", "hal", "system", "lint"]
            }
        }
        self.state_dir = Path(".ai/mas/state")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.policy_file = Path(".ai/mas/policies.json")
        self.policies = self._load_policies()

    def _load_policies(self) -> Dict[str, Any]:
        if self.policy_file.exists():
            return json.loads(self.policy_file.read_text())
        return {}

    def is_request_safe(self, request: str, domain: str) -> bool:
        """Check if the request violates any safety policies."""
        req_lower = request.lower()

        # Check forbidden commands
        for cmd in self.policies.get("forbidden_commands", []):
            if cmd in req_lower:
                return False

        # Check domain-specific restrictions
        restrictions = self.policies.get("roles", {}).get(domain, {})
        for path in restrictions.get("restricted_paths", []):
            if path in req_lower:
                # If a protocol agent tries to touch 'targets/', it might be a violation
                # unless it's just mentioning it. This is a simplified check.
                print(
                    f"Policy Warning: {domain} agent restricted from path: {path}")

        return True

    def classify_task(self, task_description: str) -> str:
        """Classify the task based on keywords."""
        task_lower = task_description.lower()

        # Check for explicit domain mentions using word matching
        words = set(task_lower.replace(".", " ").replace("/", " ").split())
        for domain, info in self.agents.items():
            if any(keyword in words for keyword in info["keywords"]):
                return domain

        # Default to core_system if unsure
        return "core_system"

    async def delegate_task(self, domain: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate task to a specific sub-agent."""
        print(f"Delegating task to {domain} agent...")

        # In a real implementation, this would call another script or an API
        # For now, we'll simulate the delegation by writing to a task file
        agent_task_file = Path(f".ai/mas/{domain}/pending_tasks.json")

        tasks = []
        if agent_task_file.exists():
            try:
                tasks = json.loads(agent_task_file.read_text())
            except json.JSONDecodeError:
                tasks = []

        tasks.append(task_data)
        agent_task_file.write_text(json.dumps(tasks, indent=2))

        return {"status": "assigned", "agent": domain}

    async def handle_request(self, request: str):
        domain = self.classify_task(request)

        if not self.is_request_safe(request, domain):
            print(f"Denied: Request violated safety policy for {domain}.")
            return {"status": "denied", "reason": "policy_violation"}

        task_data = {
            "request": request,
            "timestamp": asyncio.get_event_loop().time(),
            "status": "pending"
        }
        result = await self.delegate_task(domain, task_data)
        print(f"Supervisor: Task assigned to {domain}")
        return result


async def main():
    supervisor = MomentumSupervisor()
    if len(os.sys.argv) > 1:
        request = " ".join(os.sys.argv[1:])
        await supervisor.handle_request(request)
    else:
        print("Momentum Supervisor active. Pass a request as an argument.")

if __name__ == "__main__":
    asyncio.run(main())
