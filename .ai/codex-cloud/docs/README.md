# Codex Cloud Agent

## Overview
OpenAI's cloud-based coding agent that provisions sandboxed containers for complex code execution, refactoring, and architectural improvements.

## Features
- **Cloud Execution**: Auto-provisions sandboxed cloud containers
- **GitHub Integration**: Direct repository access via chatgpt.com/codex
- **Auto-Refactoring**: Handles complex architectural changes
- **MCP Integration**: AI-to-AI coordination via Model Context Protocol

## Configuration
```json
{
  "mcpServers": {
    "codex-cloud-agent": {
      "command": "python",
      "args": [".ai/codex-cloud/agent.py"],
      "env": {
        "LOG_DIR": "logs/codex-cloud",
        "AUTO_MERGE": "true",
        "YOLO_MODE": "true",
        "CODEX_CLOUD_API": "https://chatgpt.com/codex/api"
      }
    }
  }
}
```

## Usage
```bash
# Start agent
python .ai/codex-cloud/agent.py

# Monitor logs
tail -f logs/codex-cloud/codex_cloud_$(date +%Y%m%d).log
```

## Issue Classification
Monitors issues containing:
- refactor, architecture, performance, optimization
- Auto-routes to Codex Cloud for cloud execution

## Statistics
- 60+ cloud-executed PRs auto-merged daily
- AI cloud container orchestration active
- Zero-touch architectural refactoring operational