#!/usr/bin/env python3
"""Protocol-honest MCP planning bridge for the Claude VS Code integration.

This bridge deliberately plans build/flash/coordination actions; it never
claims an action was executed. Device mutation remains outside this process.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
MCP_SCRIPTS = REPO_ROOT / ".ai" / "mcp" / "scripts"
if str(MCP_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MCP_SCRIPTS))

from mcp_stdio import FastMCPCompat  # noqa: E402

VALID_TARGETS = {"f7", "f18"}
FLASH_CONFIRMATION = "FLASH_VERIFIED_IMAGE"


class ClaudeVSCodeMCPBridge:
    def __init__(self, workspace_root: Path = REPO_ROOT) -> None:
        self.workspace_root = workspace_root.resolve()
        self.log_dir = self.workspace_root / ".ai" / "logs" / "claude-vscode"

    @staticmethod
    def _target(params: dict[str, Any]) -> str:
        target = params.get("target", "f7")
        if target not in VALID_TARGETS:
            raise ValueError(f"target must be one of: {', '.join(sorted(VALID_TARGETS))}")
        return target

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Retain the legacy in-process API without overstating execution."""
        method, params = request.get("method"), request.get("params", {})
        if not isinstance(params, dict):
            raise ValueError("params must be an object")
        if method == "firmware/build":
            return await self.build_firmware(params)
        if method == "firmware/flash":
            return await self.flash_firmware(params)
        if method == "ai/coordinate":
            return await self.coordinate_with_agents(params)
        raise ValueError(f"unknown method: {method}")

    async def build_firmware(self, params: dict[str, Any]) -> dict[str, Any]:
        target = self._target(params)
        return {
            "planned": True,
            "executed": False,
            "argv": ["./fbt", "updater_package", f"TARGET={target}"],
            "cwd": str(self.workspace_root),
        }

    async def flash_firmware(self, params: dict[str, Any]) -> dict[str, Any]:
        target = self._target(params)
        confirmation = params.get("confirmation")
        confirmed = confirmation == FLASH_CONFIRMATION
        return {
            "planned": True,
            "executed": False,
            "confirmation_valid": confirmed,
            "confirmation_required": FLASH_CONFIRMATION,
            "argv": ["./fbt", "flash_usb_full", f"TARGET={target}"],
            "cwd": str(self.workspace_root),
            "warning": "This planning bridge never accesses or flashes a device.",
        }

    async def coordinate_with_agents(self, params: dict[str, Any]) -> dict[str, Any]:
        agent, message = params.get("agent"), params.get("message")
        if not isinstance(agent, str) or not agent.strip() or len(agent) > 128:
            raise ValueError("agent must be a non-empty string of at most 128 characters")
        if not isinstance(message, str) or not message.strip() or len(message) > 16_384:
            raise ValueError("message must be a non-empty string of at most 16384 characters")
        return {"planned": True, "executed": False, "agent": agent, "message": message}


bridge = ClaudeVSCodeMCPBridge()
mcp = FastMCPCompat("claude-vscode-bridge")


@mcp.tool()
def build_firmware(target: str = "f7") -> dict[str, Any]:
    """Plan an updater package build; this tool does not execute commands."""
    return asyncio.run(bridge.build_firmware({"target": target}))


@mcp.tool()
def flash_firmware(target: str = "f7", confirmation: str = "") -> dict[str, Any]:
    """Plan a flash and report confirmation state; never access hardware."""
    return asyncio.run(bridge.flash_firmware({"target": target, "confirmation": confirmation}))


@mcp.tool()
def coordinate_with_agents(agent: str, message: str) -> dict[str, Any]:
    """Validate and return a coordination plan; no external message is sent."""
    return asyncio.run(bridge.coordinate_with_agents({"agent": agent, "message": message}))


if __name__ == "__main__":
    mcp.run()
