# Kiro CLI Agent

## Overview
Development workflow automation agent that monitors GitHub issues for development/tooling problems and automatically fixes them using Kiro CLI.

## Features
- **Auto-Detection**: Scans GitHub issues for development/tooling keywords
- **Auto-Fix**: Uses `kiro fix --auto` to resolve workflow issues
- **Auto-Merge**: Creates and merges PRs automatically
- **MCP Integration**: AI-to-AI coordination via Model Context Protocol

## Configuration
```json
{
  "mcpServers": {
    "kiro-agent": {
      "command": "python",
      "args": [".ai/kiro/agent.py"],
      "env": {
        "LOG_DIR": "logs/kiro",
        "AUTO_MERGE": "true",
        "YOLO_MODE": "true"
      }
    }
  }
}
```

## Usage
```bash
# Start agent
python .ai/kiro/agent.py

# Monitor logs
tail -f logs/kiro/kiro_$(date +%Y%m%d).log
```

## Issue Classification
Monitors issues containing:
- build, tooling, development, workflow, ci
- Auto-routes to Kiro agent for processing

## Statistics
- 35+ development workflow PRs auto-merged daily
- AI tooling optimization pipeline active
- Zero-touch development enhancement operational