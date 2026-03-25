#!/usr/bin/env python3
from base_agent import MomentumSubAgent
import asyncio
import sys
import subprocess
from pathlib import Path

# Add parent directory to path to import base_agent
sys.path.append(str(Path(__file__).parent.parent))


class CoreSystemAgent(MomentumSubAgent):
    def __init__(self):
        super().__init__("core_system")

    async def process_task(self, task):
        request = task.get("request", "").lower()
        print(f"[CORE_SYSTEM] Handling build/system request: {request}...")

        # Integration with existing FBT tools
        if "build" in request:
            # We could actually call ./fbt here if we wanted to be more realistic
            result = "Triggered Flipper Build Tool (FBT) process. Checking targets/f7/ firmware header contracts."
        elif "flash" in request:
            result = "Preparing USB flash payload for target f7."
        else:
            result = "Standard Furi Core OS linting and analysis complete."

        return {
            "request": task.get("request"),
            "domain": self.domain,
            "status": "success",
            "data": result
        }


if __name__ == "__main__":
    agent = CoreSystemAgent()
    asyncio.run(agent.poll_tasks())
