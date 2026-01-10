# AI Documentation

Central documentation for the AI agent ecosystem.

See individual agent directories for detailed documentation.

## ESP/Embedded Tooling

### esp_mcp (ESP-IDF MCP server)

This repository vendors the `horw/esp-mcp` MCP server under `.ai/mcp/servers/esp_mcp`. It exposes ESP-IDF workflows (install, build, flash, pytest) as MCP tools that agents can call without manual shell interaction.

Key tools:
- `run_esp_idf_install(idf_path?)` – install ESP-IDF toolchain via `install.sh`.
- `create_esp_project(project_path, project_name)` – scaffold a new ESP-IDF project.
- `setup_project_esp_target(project_path, target, idf_path?)` – set the target chip (e.g. `esp32`, `esp32c3`, `esp32s3`).
- `build_esp_project(project_path, idf_path?, sdkconfig_defaults?)` – incremental or full builds.
- `list_esp_serial_ports()` – discover available ESP serial ports.
- `flash_esp_project(project_path, port?)` – flash firmware to a connected ESP.
- `run_pytest(project_path, test_path, pytest_args, idf_path?)` – run pytest/pytest-embedded test suites for ESP projects.

The `esp_mcp` server is registered in `.ai/mcp/codex_server.json` and runs via `python3 main.py` with `cwd` set to `.ai/mcp/servers/esp_mcp`. Agents should prefer these tools for ESP32 automation instead of invoking `idf.py` directly.

### Core AI Technologies and Focus Areas

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
