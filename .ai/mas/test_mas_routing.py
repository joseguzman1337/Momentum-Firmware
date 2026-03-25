#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path
from typing import Any, Dict

# Add paths for imports
current_dir = Path(__file__).parent.resolve()
supervisor_path = current_dir / "supervisor"
sys.path.append(str(supervisor_path))

try:
    from supervisor import MomentumSupervisor
except ImportError:
    # Fallback if the path logic above fails
    sys.path.append(str(current_dir / "supervisor"))
    from supervisor import MomentumSupervisor


async def test_scenarios():
    sup = MomentumSupervisor()

    scenarios = [
        "Update the SubGHz signal parser for the new 868MHz protocol.",
        "Optimize the memory allocation in Furi HAL.",
        "Add a custom battery icon to the Asset Pack.",
        "Build and flash the firmware to the latest target."
    ]

    print("=== Momentum MAS Profile Alignment Test ===\n")

    for scenario in scenarios:
        print(f"Scenario: {scenario}")
        result = await sup.handle_request(scenario)
        print(f"Routing Result: {result}\n")

if __name__ == "__main__":
    asyncio.run(test_scenarios())
