#!/usr/bin/env python3
"""
Agent-to-Agent (A2A) Communication Server
Enables AI agents to communicate and coordinate tasks
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class A2AServer:
    def __init__(self):
        self.repo_root = Path("/Users/x/x/Momentum-Firmware")
        self.message_bus_file = self.repo_root / ".ai/workflows/message_bus.json"
        self.message_bus_file.parent.mkdir(parents=True, exist_ok=True)
        self.messages = self.load_messages()
    
    def load_messages(self) -> List[Dict]:
        """Load message history"""
        if self.message_bus_file.exists():
            with open(self.message_bus_file) as f:
                return json.load(f)
        return []
    
    def save_messages(self):
        """Save message history"""
        with open(self.message_bus_file, "w") as f:
            json.dump(self.messages, f, indent=2)
    
    def send_message(self, from_agent: str, to_agent: str, message_type: str, payload: Dict) -> Dict:
        """Send message from one agent to another"""
        message = {
            "id": len(self.messages) + 1,
            "timestamp": datetime.now().isoformat(),
            "from": from_agent,
            "to": to_agent,
            "type": message_type,
            "payload": payload,
            "status": "sent"
        }
        
        self.messages.append(message)
        self.save_messages()
        
        return message
    
    def get_messages(self, agent: str, status: str = None) -> List[Dict]:
        """Get messages for an agent"""
        messages = [m for m in self.messages if m["to"] == agent]
        if status:
            messages = [m for m in messages if m["status"] == status]
        return messages
    
    def mark_read(self, message_id: int) -> bool:
        """Mark message as read"""
        for msg in self.messages:
            if msg["id"] == message_id:
                msg["status"] = "read"
                self.save_messages()
                return True
        return False
    
    def broadcast(self, from_agent: str, message_type: str, payload: Dict) -> List[Dict]:
        """Broadcast message to all agents"""
        agents = ["codex", "claude", "gemini", "jules", "warp"]
        sent_messages = []
        
        for agent in agents:
            if agent != from_agent:
                msg = self.send_message(from_agent, agent, message_type, payload)
                sent_messages.append(msg)
        
        return sent_messages
    
    def coordinate_task(self, task: Dict) -> Dict:
        """Coordinate a task across multiple agents"""
        coordination = {
            "task_id": task.get("id"),
            "primary_agent": task.get("assigned_to"),
            "supporting_agents": [],
            "status": "coordinating"
        }
        
        # Determine which agents should support
        task_type = task.get("type", "")
        
        if "security" in task_type.lower():
            coordination["supporting_agents"].append("claude")
        if "architecture" in task_type.lower():
            coordination["supporting_agents"].append("gemini")
        if "implementation" in task_type.lower():
            coordination["supporting_agents"].append("codex")
        
        # Broadcast coordination request
        self.broadcast(
            "orchestrator",
            "task_coordination",
            coordination
        )
        
        return coordination

def main():
    """MCP Server main loop"""
    server = A2AServer()
    
    print("A2A Communication Server started", file=sys.stderr)
    
    # MCP protocol loop
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "send":
                result = server.send_message(
                    params["from"],
                    params["to"],
                    params["type"],
                    params["payload"]
                )
            elif method == "get_messages":
                result = server.get_messages(
                    params["agent"],
                    params.get("status")
                )
            elif method == "broadcast":
                result = server.broadcast(
                    params["from"],
                    params["type"],
                    params["payload"]
                )
            elif method == "coordinate":
                result = server.coordinate_task(params["task"])
            elif method == "mark_read":
                result = server.mark_read(params["message_id"])
            else:
                result = {"error": f"Unknown method: {method}"}
            
            print(json.dumps({"result": result}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
