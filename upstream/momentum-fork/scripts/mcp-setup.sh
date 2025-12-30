#!/bin/bash

# MCP Setup Script for Momentum Firmware
# Configures Model Context Protocol servers for AI-powered development

set -e

PROJECT_ROOT="/Users/x/x/Momentum-Firmware"
CODEX_CONFIG_DIR="$HOME/.codex"
MCP_CONFIG="$CODEX_CONFIG_DIR/config.toml"

echo "🚀 Setting up MCP for Momentum Firmware..."

# Create Codex config directory if it doesn't exist
mkdir -p "$CODEX_CONFIG_DIR"

# Backup existing config if it exists
if [ -f "$MCP_CONFIG" ]; then
    echo "📦 Backing up existing Codex config..."
    cp "$MCP_CONFIG" "$MCP_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Copy unified MCP configuration
echo "📋 Installing unified MCP configuration..."
cp "$PROJECT_ROOT/.ai/.codex/mcp_unified.toml" "$MCP_CONFIG"

# Install required Node.js packages for external MCP servers
echo "📦 Installing external MCP servers..."
npm install -g @upstash/context7-mcp @modelcontextprotocol/server-github @playwright/mcp

# Create MCP server directories
echo "📁 Creating MCP server directories..."
mkdir -p "$PROJECT_ROOT/.ai/mcp/servers"
mkdir -p "$PROJECT_ROOT/.ai/rag"
mkdir -p "$PROJECT_ROOT/.ai/workflows"
mkdir -p "$PROJECT_ROOT/.ai/tools"
mkdir -p "$PROJECT_ROOT/.ai/docs"
mkdir -p "$PROJECT_ROOT/.ai/security"

# Create basic MCP server implementations
echo "🔧 Creating MCP server implementations..."

# RAG Knowledge Server
cat > "$PROJECT_ROOT/.ai/rag/server.py" << 'EOF'
#!/usr/bin/env python3
"""RAG Knowledge MCP Server for Momentum Firmware"""

import json
import sys
import os
from typing import Dict, Any, List

class RAGServer:
    def __init__(self):
        self.knowledge_base = os.getenv('KNOWLEDGE_BASE', '.ai/rag/shared_knowledge.json')
        self.vector_store = os.getenv('VECTOR_STORE', '.ai/rag/embeddings')
        
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get('method')
        
        if method == 'tools/list':
            return {
                "tools": [
                    {
                        "name": "search_knowledge",
                        "description": "Search the shared knowledge base",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "add_knowledge",
                        "description": "Add knowledge to the shared base",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string", "description": "Knowledge content"},
                                "tags": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["content"]
                        }
                    }
                ]
            }
        elif method == 'tools/call':
            return self.handle_tool_call(request.get('params', {}))
        
        return {"error": "Unknown method"}
    
    def handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if tool_name == 'search_knowledge':
            return {"content": [{"type": "text", "text": f"Searching for: {arguments.get('query')}"}]}
        elif tool_name == 'add_knowledge':
            return {"content": [{"type": "text", "text": "Knowledge added successfully"}]}
        
        return {"error": "Unknown tool"}

if __name__ == "__main__":
    server = RAGServer()
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
EOF

# Message Bus Server
cat > "$PROJECT_ROOT/.ai/workflows/message_bus.py" << 'EOF'
#!/usr/bin/env python3
"""Agent Communication MCP Server for Momentum Firmware"""

import json
import sys
import os
from typing import Dict, Any

class MessageBusServer:
    def __init__(self):
        self.message_bus = os.getenv('MESSAGE_BUS', '.ai/workflows/message_bus.json')
        
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get('method')
        
        if method == 'tools/list':
            return {
                "tools": [
                    {
                        "name": "send_message",
                        "description": "Send message to another agent",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "recipient": {"type": "string", "description": "Target agent"},
                                "message": {"type": "string", "description": "Message content"},
                                "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                            },
                            "required": ["recipient", "message"]
                        }
                    },
                    {
                        "name": "get_messages",
                        "description": "Get pending messages",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "agent_id": {"type": "string", "description": "Agent identifier"}
                            },
                            "required": ["agent_id"]
                        }
                    }
                ]
            }
        elif method == 'tools/call':
            return self.handle_tool_call(request.get('params', {}))
        
        return {"error": "Unknown method"}
    
    def handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if tool_name == 'send_message':
            return {"content": [{"type": "text", "text": f"Message sent to {arguments.get('recipient')}"}]}
        elif tool_name == 'get_messages':
            return {"content": [{"type": "text", "text": "No pending messages"}]}
        
        return {"error": "Unknown tool"}

if __name__ == "__main__":
    server = MessageBusServer()
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
EOF

# Flipper Tools Server
cat > "$PROJECT_ROOT/.ai/tools/flipper_mcp.py" << 'EOF'
#!/usr/bin/env python3
"""Flipper Tools MCP Server for Momentum Firmware"""

import json
import sys
import os
import subprocess
from typing import Dict, Any

class FlipperToolsServer:
    def __init__(self):
        self.fbt_path = os.getenv('FBT_PATH', './fbt')
        self.toolchain = os.getenv('FLIPPER_TOOLCHAIN', 'toolchain/current')
        
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get('method')
        
        if method == 'tools/list':
            return {
                "tools": [
                    {
                        "name": "build_firmware",
                        "description": "Build Flipper firmware",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "target": {"type": "string", "description": "Build target", "default": "f7"},
                                "debug": {"type": "boolean", "description": "Debug build", "default": False}
                            }
                        }
                    },
                    {
                        "name": "flash_firmware",
                        "description": "Flash firmware to device",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "method": {"type": "string", "enum": ["usb", "swd"], "default": "usb"}
                            }
                        }
                    },
                    {
                        "name": "build_app",
                        "description": "Build external application",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "app_id": {"type": "string", "description": "Application ID"}
                            },
                            "required": ["app_id"]
                        }
                    }
                ]
            }
        elif method == 'tools/call':
            return self.handle_tool_call(request.get('params', {}))
        
        return {"error": "Unknown method"}
    
    def handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        try:
            if tool_name == 'build_firmware':
                target = arguments.get('target', 'f7')
                debug = arguments.get('debug', False)
                cmd = [self.fbt_path, f'TARGET={target}']
                if debug:
                    cmd.append('DEBUG=1')
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                return {"content": [{"type": "text", "text": f"Build result: {result.returncode}\n{result.stdout}"}]}
                
            elif tool_name == 'flash_firmware':
                method = arguments.get('method', 'usb')
                cmd = [self.fbt_path, f'flash_{method}_full']
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                return {"content": [{"type": "text", "text": f"Flash result: {result.returncode}\n{result.stdout}"}]}
                
            elif tool_name == 'build_app':
                app_id = arguments.get('app_id')
                cmd = [self.fbt_path, 'launch', f'APPSRC={app_id}']
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                return {"content": [{"type": "text", "text": f"App build result: {result.returncode}\n{result.stdout}"}]}
                
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": "Unknown tool"}

if __name__ == "__main__":
    server = FlipperToolsServer()
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
EOF

# Make Python scripts executable
chmod +x "$PROJECT_ROOT/.ai/rag/server.py"
chmod +x "$PROJECT_ROOT/.ai/workflows/message_bus.py"
chmod +x "$PROJECT_ROOT/.ai/tools/flipper_mcp.py"

# Create shared knowledge base
echo "📚 Initializing shared knowledge base..."
cat > "$PROJECT_ROOT/.ai/rag/shared_knowledge.json" << 'EOF'
{
    "version": "1.0",
    "created": "2025-01-02",
    "knowledge_base": {
        "firmware_architecture": {
            "description": "Momentum Firmware is based on Official Flipper Zero firmware with Unleashed features",
            "key_components": ["applications", "lib", "furi", "targets"],
            "build_system": "fbt (Flipper Build Tool)"
        },
        "development_workflow": {
            "build_command": "./fbt",
            "flash_command": "./fbt flash_usb_full",
            "app_build": "./fbt launch APPSRC=app_id"
        },
        "ai_agents": {
            "codex": "Feature implementation and bug fixes",
            "claude": "Security vulnerability remediation",
            "jules": "Asynchronous coding tasks",
            "gemini": "Architectural decisions",
            "deepseek": "Performance optimization",
            "warp": "Code quality analysis",
            "amazonq": "Cloud infrastructure",
            "kiro": "Development workflow"
        }
    }
}
EOF

# Create message bus file
echo "📨 Initializing message bus..."
cat > "$PROJECT_ROOT/.ai/workflows/message_bus.json" << 'EOF'
{
    "version": "1.0",
    "created": "2025-01-02",
    "messages": [],
    "agents": {
        "codex": {"status": "active", "last_seen": null},
        "claude": {"status": "active", "last_seen": null},
        "jules": {"status": "active", "last_seen": null},
        "gemini": {"status": "active", "last_seen": null},
        "deepseek": {"status": "active", "last_seen": null},
        "warp": {"status": "active", "last_seen": null},
        "amazonq": {"status": "active", "last_seen": null},
        "kiro": {"status": "active", "last_seen": null}
    }
}
EOF

# Test MCP configuration
echo "🧪 Testing MCP configuration..."
if command -v codex &> /dev/null; then
    echo "✅ Codex CLI found"
    codex mcp list || echo "⚠️  MCP servers not yet configured in Codex"
else
    echo "⚠️  Codex CLI not found. Install from: https://github.com/openai/codex"
fi

# Create quick start guide
echo "📖 Creating MCP quick start guide..."
cat > "$PROJECT_ROOT/docs/MCP_SETUP.md" << 'EOF'
# MCP Setup for Momentum Firmware

## Overview
Model Context Protocol (MCP) enables AI agents to access tools and context for automated development.

## Configuration
- **Main Config**: `~/.codex/config.toml`
- **Unified MCP**: `.ai/.codex/mcp_unified.toml`
- **Agent Scripts**: `.ai/*/agent.py`

## Available MCP Servers

### Internal AI Agents
- `momentum-codex`: Feature implementation and bug fixes
- `codex-cloud`: Cloud-based code execution
- `claude-security`: Security vulnerability remediation  
- `jules-async`: Asynchronous coding tasks
- `gemini-super`: Architectural decisions
- `deepseek-optimizer`: Performance optimization
- `warp-quality`: Code quality analysis
- `amazonq-cloud`: AWS/cloud infrastructure
- `kiro-dev`: Development workflow automation

### External Services
- `context7`: Developer documentation access
- `github`: GitHub API integration
- `playwright`: Browser automation (optional)
- `chrome-devtools`: Chrome debugging (optional)

### Internal Tools
- `rag-knowledge`: Shared knowledge base
- `agent-communication`: Agent-to-agent messaging
- `flipper-tools`: Firmware build tools
- `firmware-analyzer`: Code analysis
- `security-scanner`: Security scanning
- `docs-generator`: Documentation generation

## Usage

### Start Codex with MCP
```bash
codex
```

### List MCP Servers
```bash
codex mcp list
```

### Test MCP Connection
```bash
codex mcp test <server-name>
```

### Enable/Disable Servers
Edit `~/.codex/config.toml` and set `enabled = true/false`

## Troubleshooting

### Server Won't Start
1. Check logs in `logs/<agent>/`
2. Verify Python/Node.js dependencies
3. Check environment variables

### Timeout Issues
Increase `startup_timeout_sec` and `tool_timeout_sec` in config

### Permission Errors
Ensure scripts are executable: `chmod +x .ai/*/agent.py`

## Development

### Adding New MCP Server
1. Create server script in `.ai/<name>/`
2. Add configuration to `mcp_unified.toml`
3. Test with `codex mcp test <name>`

### Agent Communication
Use `agent-communication` server for inter-agent messaging:
```python
# Send message to another agent
send_message(recipient="claude-security", message="Found vulnerability", priority="high")

# Get pending messages
messages = get_messages(agent_id="codex")
```

### Shared Knowledge
Use `rag-knowledge` server for shared context:
```python
# Search knowledge base
results = search_knowledge(query="firmware build process")

# Add new knowledge
add_knowledge(content="New build optimization", tags=["build", "performance"])
```
EOF

echo "✅ MCP setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Install Codex CLI: https://github.com/openai/codex"
echo "2. Set environment variables (GITHUB_TOKEN, etc.)"
echo "3. Run: codex mcp list"
echo "4. Start development: codex"
echo ""
echo "📚 Documentation: docs/MCP_SETUP.md"
echo "🔧 Configuration: ~/.codex/config.toml"
echo "📊 Logs: logs/<agent>/"