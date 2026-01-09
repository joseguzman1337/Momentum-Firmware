#!/usr/bin/env python3
"""Flipper Tools MCP Server for Claude VS Code"""

import subprocess
import json
from pathlib import Path

class FlipperToolsMCP:
    def __init__(self):
        self.workspace_root = Path("/Users/x/x/Momentum-Firmware")
        self.fbt_path = self.workspace_root / "fbt"
    
    def build_firmware(self, target="f7"):
        """Build firmware using fbt"""
        cmd = [str(self.fbt_path), "updater_package", f"TARGET={target}"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.workspace_root)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def flash_firmware(self):
        """Flash firmware to device"""
        cmd = [str(self.fbt_path), "flash_usb_full"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.workspace_root)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def launch_app(self, app_id):
        """Launch specific app"""
        cmd = [str(self.fbt_path), "launch", f"APPSRC={app_id}"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.workspace_root)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
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
    print(json.dumps(tools.get_available_tools(), indent=2))