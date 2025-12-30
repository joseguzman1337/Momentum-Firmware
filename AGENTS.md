# Momentum Firmware Agent Ecosystem

## Project Management & Automation
Momentum Firmware uses a multi-agent AI system for 24/7 development, security, and operations. All agents run in **YOLO Mode** with absolute authority to modify code and merge Pull Requests.

## Command Reference
```bash
# Build System
./fbt               # Default firmware build
./fbt updater_package # Create update bundle
./fbt flash_usb_full  # Flash over USB

# Code Quality
./fbt lint          # Check code style
./fbt format        # Auto-format code
./fbt test          # Run unit tests
```

## AI Agent Roster
| Agent | Role | Automation Path |
|-------|------|-----------------|
| **Codex** | Features & Bug Fixes | `.ai/orchestrator.py` |
| **Claude** | Security & CVE Fixes | `.ai/security_agent.py` |
| **Gemini** | Architecture Decisions | `.ai/gemini_agent.py` |
| **Jules** | Async Cloud Tasks | `.ai/jules/` |
| **DeepSeek** | Performance Optimization | `.ai/optimizer/` |
| **Warp** | Code Quality Analysis | `.ai/warp/` |
| **Amazon Q** | Cloud & AWS Infrastructure | `.ai/amazonq/` |
| **Kiro** | Build & Dev Workflow | `.ai/kiro/` |
| **Claude Slack** | Team Collaboration | `.ai/claude-slack/` |

## Automation Statistics (Live)
- **PR Auto-Merge:** 1,260+ daily
- **Issue Auto-Resolution:** 575+ daily
- **Response Time:** <12 seconds (AI-to-AI)
- **Uptime:** 24/7 (Zero-touch)

## Communication Protocol (MCP)
Agents coordinate via Model Context Protocol servers located in `.ai/*/mcp_server.json`. The shared knowledge base is maintained in `.ai/rag/`.