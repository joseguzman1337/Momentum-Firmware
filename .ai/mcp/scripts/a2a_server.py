#!/usr/bin/env python3
"""
Agent-to-Agent (A2A) Communication Server
Enables AI agents to communicate and coordinate tasks
"""

import json
import os
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List
from mcp_stdio import MCPStdioServer

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None

MAX_BUS_BYTES = 10 * 1024 * 1024
MAX_PAYLOAD_BYTES = 256 * 1024

class A2AServer:
    def __init__(self):
        self.repo_root = Path(os.environ.get("REPO_ROOT", Path(__file__).resolve().parents[3])).resolve()
        self.message_bus_file = Path(
            os.environ.get("MESSAGE_BUS", self.repo_root / ".ai/workflows/message_bus.json")
        ).resolve()
        self._thread_lock = threading.RLock()
        self._enveloped_format = False
        self.messages = self.load_messages()

    @contextmanager
    def locked_bus(self):
        """Serialize cross-thread and cross-process message-bus updates."""
        self.message_bus_file.parent.mkdir(parents=True, exist_ok=True)
        lock_path = self.message_bus_file.with_suffix(self.message_bus_file.suffix + ".lock")
        with self._thread_lock, open(lock_path, "a+b") as lock:
            if fcntl is not None:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                if fcntl is not None:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    
    def load_messages(self) -> List[Dict]:
        """Load message history"""
        if self.message_bus_file.exists():
            if self.message_bus_file.stat().st_size > MAX_BUS_BYTES:
                raise ValueError("message bus exceeds 10 MiB safety limit")
            with open(self.message_bus_file, encoding="utf-8") as f:
                messages = json.load(f)
            if isinstance(messages, dict) and isinstance(messages.get("messages"), list):
                self._enveloped_format = True
                messages = messages["messages"]
            if not isinstance(messages, list) or any(not isinstance(item, dict) for item in messages):
                raise ValueError("message bus root must be an array of objects")
            return messages
        return []
    
    def save_messages(self):
        """Atomically save message history."""
        self.message_bus_file.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".message-bus.", dir=self.message_bus_file.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                document = (
                    {"messages": self.messages, "last_updated": datetime.now(timezone.utc).isoformat()}
                    if self._enveloped_format
                    else self.messages
                )
                json.dump(document, stream, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.message_bus_file)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    
    def send_message(self, from_agent: str, to_agent: str, message_type: str, payload: Dict) -> Dict:
        """Send message from one agent to another"""
        return self._append_messages(from_agent, [to_agent], message_type, payload)[0]

    def _append_messages(
        self, from_agent: str, recipients: List[str], message_type: str, payload: Dict
    ) -> List[Dict]:
        """Append a complete recipient batch in one locked atomic transaction."""
        if len(json.dumps(payload, separators=(",", ":")).encode("utf-8")) > MAX_PAYLOAD_BYTES:
            raise ValueError("payload exceeds 256 KiB safety limit")
        if not recipients:
            return []
        with self.locked_bus():
            self.messages = self.load_messages()
            numeric_ids = [item.get("id") for item in self.messages if isinstance(item.get("id"), int)]
            next_id = max(numeric_ids, default=0) + 1
            messages = [
                {
                    "id": next_id + offset,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "from": from_agent,
                    "to": recipient,
                    "type": message_type,
                    "payload": payload,
                    "status": "sent",
                }
                for offset, recipient in enumerate(recipients)
            ]
            self.messages.extend(messages)
            self.save_messages()
            return messages
    
    def get_messages(self, agent: str, status: str = None) -> List[Dict]:
        """Get messages for an agent"""
        with self.locked_bus():
            self.messages = self.load_messages()
        messages = [m for m in self.messages if m.get("to") == agent]
        if status:
            messages = [m for m in messages if m.get("status") == status]
        return messages
    
    def mark_read(self, message_id: int) -> bool:
        """Mark message as read"""
        with self.locked_bus():
            self.messages = self.load_messages()
            for msg in self.messages:
                if msg.get("id") == message_id:
                    msg["status"] = "read"
                    self.save_messages()
                    return True
        return False
    
    def broadcast(self, from_agent: str, message_type: str, payload: Dict) -> List[Dict]:
        """Broadcast message to all agents"""
        agents = ["codex", "claude", "gemini", "jules", "warp"]
        recipients = [agent for agent in agents if agent != from_agent]
        return self._append_messages(from_agent, recipients, message_type, payload)
    
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

def create_mcp_server(server: A2AServer = None) -> MCPStdioServer:
    """Create the MCP server, including additive legacy tool aliases."""
    server = server or A2AServer()
    mcp = MCPStdioServer("momentum-a2a")
    identity = {"type": "string", "minLength": 1, "maxLength": 64, "pattern": "^[a-zA-Z0-9_.-]+$"}
    mcp.tool(
        "get_messages",
        "Read messages addressed to an agent.",
        {
            "type": "object",
            "properties": {"agent": identity, "status": {"type": "string", "enum": ["sent", "read"]}},
            "required": ["agent"],
            "additionalProperties": False,
        },
        server.get_messages,
    )
    send_schema = {
        "type": "object",
        "properties": {
            "from_agent": identity,
            "to_agent": identity,
            "message_type": identity,
            "payload": {"type": "object"},
        },
        "required": ["from_agent", "to_agent", "message_type", "payload"],
        "additionalProperties": False,
    }
    send_handler = server.send_message
    mcp.tool(
        "send_message",
        "Append one agent message to the repository-local bus (mutating).",
        send_schema,
        send_handler,
    )
    mcp.tool(
        "send",
        "Legacy alias for send_message; appends one agent message to the repository-local bus (mutating).",
        send_schema,
        send_handler,
    )
    mcp.tool(
        "mark_read",
        "Mark one message as read (mutating).",
        {
            "type": "object",
            "properties": {"message_id": {"type": "integer", "minimum": 1}},
            "required": ["message_id"],
            "additionalProperties": False,
        },
        server.mark_read,
    )
    mcp.tool(
        "broadcast",
        "Append a message for each configured peer agent (mutating).",
        {
            "type": "object",
            "properties": {"from_agent": identity, "message_type": identity, "payload": {"type": "object"}},
            "required": ["from_agent", "message_type", "payload"],
            "additionalProperties": False,
        },
        server.broadcast,
    )
    coordinate_schema = {
        "type": "object",
        "properties": {"task": {"type": "object"}},
        "required": ["task"],
        "additionalProperties": False,
    }
    coordinate_handler = server.coordinate_task
    mcp.tool(
        "coordinate_task",
        "Create and broadcast an agent coordination record (mutating).",
        coordinate_schema,
        coordinate_handler,
    )
    mcp.tool(
        "coordinate",
        "Legacy alias for coordinate_task; creates and broadcasts an agent coordination record (mutating).",
        coordinate_schema,
        coordinate_handler,
    )
    return mcp


def main():
    """Run a standards-compliant MCP stdio server."""
    mcp = create_mcp_server()
    mcp.run()

if __name__ == "__main__":
    main()
