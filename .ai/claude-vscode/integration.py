#!/usr/bin/env python3
"""Claude VS Code Extension Integration for Momentum Firmware AI Pipeline"""

import json
import subprocess
import os
from pathlib import Path

class ClaudeVSCodeIntegration:
    def __init__(self):
        self.workspace_root = Path("/Users/x/x/Momentum-Firmware")
        self.ai_dir = self.workspace_root / ".ai"
        self.logs_dir = self.workspace_root / "logs" / "claude-vscode"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
    def install_extension(self):
        """Install Claude Code extension"""
        try:
            subprocess.run(["code", "--install-extension", "anthropic.claude-code"], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def configure_extension(self):
        """Configure VS Code settings for Claude Code"""
        vscode_settings = {
            "claudeCode.selectedModel": "claude-3-5-sonnet-20241022",
            "claudeCode.useTerminal": False,
            "claudeCode.initialPermissionMode": "default",
            "claudeCode.autosave": True,
            "claudeCode.respectGitIgnore": True,
            "claudeCode.useCtrlEnterToSend": True
        }
        
        settings_path = self.workspace_root / ".vscode" / "settings.json"
        settings_path.parent.mkdir(exist_ok=True)
        
        if settings_path.exists():
            with open(settings_path) as f:
                existing = json.load(f)
            existing.update(vscode_settings)
        else:
            existing = vscode_settings
            
        with open(settings_path, 'w') as f:
            json.dump(existing, f, indent=2)
    
    def create_mcp_bridge(self):
        """Create MCP bridge for VS Code extension"""
        bridge_config = {
            "mcpServers": {
                "claude-vscode-bridge": {
                    "command": "python",
                    "args": [str(self.ai_dir / "claude-vscode" / "mcp_bridge.py")],
                    "env": {
                        "WORKSPACE_ROOT": str(self.workspace_root),
                        "LOG_DIR": str(self.logs_dir)
                    }
                }
            }
        }
        
        with open(self.ai_dir / "claude-vscode" / "mcp_server.json", 'w') as f:
            json.dump(bridge_config, f, indent=2)

if __name__ == "__main__":
    integration = ClaudeVSCodeIntegration()
    integration.install_extension()
    integration.configure_extension()
    integration.create_mcp_bridge()