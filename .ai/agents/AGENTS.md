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

### ESP/Embedded MCP Servers

- **esp_mcp** (vendored from `horw/esp-mcp`):
  - Location: `.ai/mcp/servers/esp_mcp`
  - Registered in: `.ai/mcp/codex_server.json` under the `esp_mcp` key.
  - Responsibilities:
    - Install and manage ESP-IDF toolchains (`run_esp_idf_install`).
    - Create and configure ESP-IDF projects (`create_esp_project`, `setup_project_esp_target`).
    - Build and flash ESP firmware (`build_esp_project`, `flash_esp_project`).
    - Discover ESP serial ports (`list_esp_serial_ports`).
    - Run pytest / pytest-embedded test flows on ESP targets (`run_pytest`).
  - Usage notes:
    - Prefer these tools over raw `idf.py` shell commands when automating ESP32 workflows.
    - `IDF_PATH` is configured via MCP env; agents can override per-call with the `idf_path` parameter when different ESP-IDF versions are needed.

## Core AI Technologies and Focus Areas

**1. Generative AI and Large Language Models (LLMs)**

- **LLMs/Generative AI:** Extensive knowledge and experience with Large Language Models (LLMs) such as Llama 3 and GPT-4.
- **GenAI Infrastructure:** Building a proxy-first "AI Gateway" intermediary layer and a unified API endpoint to abstract LLM complexities for centralized control and security.
- **Multi-Agent Systems:** Deep experience with multi-agent systems, agent-to-agent (A2A) communication, and orchestration frameworks.

**2. AI/ML Security and Validation**

- **AI Security:** Securing AI and Machine Learning (ML) pipelines from development to runtime.
- **ML Security Solutions:** Deploying and operationalizing solutions like **Prisma AIRS**, which includes **AI Model Scanning** and **AI Red Teaming**.
- **Adversarial ML:** Direct experience in AI security, including adversarial ML techniques.

**3. Machine Learning and Data Science**

- **MLOps:** Hands-on experience with the ML operational lifecycle.
- **Frameworks:** Proficiency in frameworks like **TensorFlow** and **PyTorch**.
- **Data Research:** Performing data-driven research on big data platforms.

**4. Foundation Model and Research (e.g., xAI)**

- **Foundation Models:** Working on world models, multimodal understanding (visual/audio), and pre-training infrastructure.
- **Reinforcement Learning (RL):** Focus on RL for coding agents, computer control, and RL training frameworks.
- **Synthetic Data:** Expertise in synthetic data & epistemics, sometimes referred to as Grokipedia.
- **Reasoning:** Roles focusing on reasoning efficiency and alignment.

**5. AI Technologies**

- **Natural Language Processing (NLP):** Used in roles such as patent agent and for designing and developing AI solutions.
- **GenAI Observability:** Experience building and maintaining highly observable GenAI systems, including proficiency with tracing and evaluation tools like **LangSmith**, **Arize**, and **HoneyHive**.
