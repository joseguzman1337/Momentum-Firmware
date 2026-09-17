# Momentum Multi-Agent System (MAS) Architecture

## Overview

The Momentum Firmware project has evolved from a monolithic assistant model to a modular, hierarchical **Multi-Agent System**. This architecture decouples domain-specific knowledge and tool access, allowing for greater precision, safety, and scalability.

## Agent Hierarchy

### 1. Supervisor Agent (Orchestrator)
- **Role:** The "Brain" and Router.
- **Location:** `.ai/mas/supervisor/supervisor.py`
- **Functions:**
    - High-level intent classification.
    - Delegation to specialized sub-agents.
    - Multi-step planning for firmware modifications.

### 2. Protocol Agent (Domain Expert)
- **Role:** Handles signal processing and file parsing.
- **Location:** `.ai/mas/protocol/agent.py`
- **Focus:** SubGHz, NFC, RFID, IR, and custom protocol definitions (`.sub`, `.nfc`).

### 3. UI/Asset Agent (Utility Expert)
- **Role:** Manages visual elements and layouts.
- **Location:** `.ai/mas/ui_asset/agent.py`
- **Focus:** Icon encoding, Asset Packs, Furi GUI canvas layout, and animation scripting.

### 4. Core System Agent (Task Expert)
- **Role:** Bridges the gap between AI and the build environment.
- **Location:** `.ai/mas/core_system/agent.py`
- **Focus:** `fbt` operations, firmware compilation, flashing, linting, and Furi Core API contracts.

## Interface Protocol

All agents communicate via a standardized JSON interface. Tasks are queued in `pending_tasks.json` within each agent's directory, and results are published to `completed_tasks.json`.

## Governance & Safety

By separating concerns, we enforce policy-based access:
- **Core Agent** has access to `targets/` and build tools.
- **Protocol Agent** is restricted to application-level logic.
- **UI Agent** manages non-functional assets.

## Getting Started

To launch the Multi-Agent System:
```bash
python3 .ai/mas/mas_manager.py
```

To send a task to the Supervisor:
```bash
python3 .ai/mas/supervisor/supervisor.py "Create a new SubGHz protocol parser for XYZ"
```
