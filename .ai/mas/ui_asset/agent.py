#!/usr/bin/env python3
from base_agent import MomentumSubAgent
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import base_agent
sys.path.append(str(Path(__file__).parent.parent))


class UIAssetAgent(MomentumSubAgent):
    def __init__(self):
        super().__init__("ui_asset")

    async def process_task(self, task):
        request = task.get("request", "").lower()
        print(f"[UI_ASSET] Managing assets for {request}...")

        # Simulated logic for UI/Asset management
        if "icon" in request or "asset" in request:
            result = "Mapping icons from assets/icons/ for Furi GUI layout."
        else:
            result = "UI layout optimization suggested for applications/main/gui."

        return {
            "request": task.get("request"),
            "domain": self.domain,
            "status": "success",
            "data": result
        }


if __name__ == "__main__":
    agent = UIAssetAgent()
    asyncio.run(agent.poll_tasks())
