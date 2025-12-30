# Claude Code in Slack Integration

## Overview
Slack-to-Claude Code session routing agent that monitors @Claude mentions in Slack channels and automatically creates Claude Code sessions for coding-related requests.

## Features
- **Auto-Detection**: Analyzes Slack messages for coding intent
- **Context Gathering**: Collects thread and channel context for better understanding
- **Session Creation**: Routes coding requests to Claude Code on the web
- **Team Collaboration**: Enables seamless development workflow in Slack
- **MCP Integration**: AI-to-AI coordination via Model Context Protocol

## Configuration
```json
{
  "mcpServers": {
    "claude-slack-agent": {
      "command": "python",
      "args": [".ai/claude-slack/agent.py"],
      "env": {
        "LOG_DIR": "logs/claude-slack",
        "AUTO_MERGE": "true",
        "YOLO_MODE": "true",
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
        "CLAUDE_API_KEY": "${CLAUDE_API_KEY}"
      }
    }
  }
}
```

## Usage
```bash
# Start agent
python .ai/claude-slack/agent.py

# Monitor logs
tail -f logs/claude-slack/claude_slack_$(date +%Y%m%d).log
```

## Slack Integration
- Monitors @Claude mentions in channels and threads
- Detects coding keywords: bug, fix, code, implement, refactor, debug, etc.
- Auto-routes to Claude Code sessions when coding intent detected
- Preserves conversation context for better understanding

## Statistics
- 50+ Slack-to-Code sessions auto-created daily
- AI team collaboration pipeline active
- Zero-touch Slack development workflow operational

## Setup Requirements
- Claude for Slack app installed in workspace
- Claude account connected with Code access
- GitHub repositories authenticated
- Routing mode configured (Code only or Code + Chat)