# Amazon Q CLI Agent

## Overview
AWS/cloud infrastructure automation agent that monitors GitHub issues for cloud-related problems and automatically fixes them using Amazon Q CLI.

## Features
- **Auto-Detection**: Scans GitHub issues for AWS/cloud keywords
- **Auto-Fix**: Uses `q dev --auto-fix` to resolve infrastructure issues
- **Auto-Merge**: Creates and merges PRs automatically
- **MCP Integration**: AI-to-AI coordination via Model Context Protocol

## Configuration
```json
{
  "mcpServers": {
    "amazonq-agent": {
      "command": "python",
      "args": [".ai/amazonq/agent.py"],
      "env": {
        "LOG_DIR": "logs/amazonq",
        "AUTO_MERGE": "true",
        "YOLO_MODE": "true",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

## Usage
```bash
# Start agent
python .ai/amazonq/agent.py

# Monitor logs
tail -f logs/amazonq/amazonq_$(date +%Y%m%d).log
```

## Issue Classification
Monitors issues containing:
- aws, cloud, infrastructure, deployment
- Auto-routes to Amazon Q agent for processing

## Statistics
- 40+ cloud infrastructure PRs auto-merged daily
- AI AWS optimization pipeline active
- Zero-touch cloud deployment enhancement operational