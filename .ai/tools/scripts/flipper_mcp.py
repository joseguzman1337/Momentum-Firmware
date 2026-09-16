#!/usr/bin/env python3
"""Flipper Tools MCP Server for Claude VS Code"""

import json
import os
import subprocess
import sys
from pathlib import Path

MCP_SCRIPTS = Path(__file__).resolve().parents[2] / "mcp" / "scripts"
sys.path.insert(0, str(MCP_SCRIPTS))
from mcp_stdio import MCPStdioServer

CONFIRM = "FLASH_VERIFIED_IMAGE"
LAUNCH_CONFIRM = "LAUNCH_VERIFIED_APP"

class FlipperToolsMCP:
    def __init__(self):
        self.workspace_root = Path(os.environ.get("WORKSPACE_ROOT", Path(__file__).resolve().parents[3])).resolve()
        self.fbt_path = Path(os.environ.get("FBT_PATH", self.workspace_root / "fbt"))
        if not self.fbt_path.is_absolute():
            self.fbt_path = self.workspace_root / self.fbt_path

    def _run(self, command, timeout=1800):
        result = subprocess.run(
            [str(item) for item in command],
            capture_output=True,
            text=True,
            cwd=self.workspace_root,
            timeout=timeout,
            check=False,
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[-12000:],
            "stderr": result.stderr[-12000:],
        }
    
    def build_firmware(self, target="f7"):
        """Build firmware using fbt"""
        if target not in {"f7", "f18"}:
            raise ValueError("target must be f7 or f18")
        cmd = [str(self.fbt_path), "updater_package", f"TARGET={target}"]
        return self._run(cmd)
    
    def flash_firmware(self, confirm="", dry_run=True):
        """Flash firmware only after explicit confirmation; defaults to dry-run."""
        if confirm != CONFIRM:
            raise PermissionError(f"refusing flash: confirm must equal {CONFIRM}")
        cmd = [str(self.fbt_path), "flash_usb_full"]
        if dry_run:
            return {"success": True, "dry_run": True, "command": cmd}
        return self._run(cmd, timeout=600)
    
    def launch_app(self, app_id, confirm="", dry_run=True):
        """Prepare an app launch, accessing a device only after exact confirmation."""
        if not app_id or Path(app_id).is_absolute() or ".." in Path(app_id).parts:
            raise ValueError("app_id must be a non-empty repository-relative path")
        cmd = [str(self.fbt_path), "launch", f"APPSRC={app_id}"]
        if dry_run:
            return {"success": True, "dry_run": True, "command": cmd}
        if confirm != LAUNCH_CONFIRM:
            raise PermissionError(f"refusing device launch: confirm must equal {LAUNCH_CONFIRM}")
        return self._run(cmd, timeout=600)
    
    def get_available_tools(self):
        """Get list of available fbt tools"""
        return [
            "build_firmware",
            "flash_firmware", 
            "launch_app",
            "updater_package",
            "flash_usb_full"
        ]

if __name__ == "__main__":
    tools = FlipperToolsMCP()
    mcp = MCPStdioServer("flipper-tools")
    mcp.tool(
        "build_firmware",
        "Build a firmware updater package without accessing a device.",
        {"type": "object", "properties": {"target": {"type": "string", "enum": ["f7", "f18"]},}, "additionalProperties": False},
        tools.build_firmware,
    )
    mcp.tool(
        "flash_firmware",
        "Destructive USB flash; requires FLASH_VERIFIED_IMAGE and defaults to dry-run.",
        {
            "type": "object",
            "properties": {"confirm": {"type": "string"}, "dry_run": {"type": "boolean", "default": True}},
            "required": ["confirm"],
            "additionalProperties": False,
        },
        tools.flash_firmware,
    )
    mcp.tool(
        "launch_app",
        "Prepare an app launch; defaults to dry-run and requires LAUNCH_VERIFIED_APP before device access.",
        {
            "type": "object",
            "properties": {
                "app_id": {"type": "string", "minLength": 1},
                "confirm": {"type": "string"},
                "dry_run": {"type": "boolean", "default": True},
            },
            "required": ["app_id"],
            "additionalProperties": False,
        },
        tools.launch_app,
    )
    mcp.tool(
        "get_available_tools",
        "List the helper capabilities without running them.",
        {"type": "object", "properties": {}, "additionalProperties": False},
        tools.get_available_tools,
    )
    mcp.run()
