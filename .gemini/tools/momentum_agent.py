#!/usr/bin/env python3
"""
Custom Gemini CLI Tool for Momentum Firmware AI Agent Coordination
"""

import json
import subprocess
import sys
from pathlib import Path

class MomentumAgentTool:
    def __init__(self):
        self.name = "momentum_agent"
        self.description = "Coordinate AI agents for Momentum Firmware development"
        
    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["status", "trigger", "logs"],
                        "description": "Action to perform"
                    },
                    "agent": {
                        "type": "string", 
                        "enum": ["codex", "claude", "amazonq", "all"],
                        "description": "Target agent"
                    }
                },
                "required": ["action"]
            }
        }
    
    def execute(self, params):
        action = params.get("action")
        agent = params.get("agent", "all")
        
        if action == "status":
            return self._get_status(agent)
        elif action == "logs":
            return self._get_logs(agent)
            
    def _get_status(self, agent):
        log_dir = Path("logs")
        status = {}
        agents = ["codex", "claude", "amazonq"] if agent == "all" else [agent]
        
        for a in agents:
            agent_logs = log_dir / a
            status[a] = {"active": agent_logs.exists()}
        
        return {"status": status}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--discover":
        tool = MomentumAgentTool()
        print(json.dumps([tool.get_schema()]))
    else:
        params = json.loads(sys.stdin.read())
        tool = MomentumAgentTool()
        result = tool.execute(params)
        print(json.dumps(result))