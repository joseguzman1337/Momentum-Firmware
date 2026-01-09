---
trigger: always_on
description: "PR1M3 Architecture Guardrails - Enforces the API-first, Recon-driven, RAG-powered architecture."
---

# Architecture Rules

When modifying `*.py` you MUST adhere to the following principles:

1.  **API-First Design**:
    *   The `APIOrchestrator` class is the entry point. Do not revert to a simple `main()` loop.
    *   All control actions (Start, Stop, Status) must be exposed via `aiohttp` endpoints.

2. **File & Directory Structure Guardrails**:
    *   **Python Scripts**: ALL Python logic files (`*.py`) MUST reside in the `python/` directory. Do not create Python scripts in the project root.
    *   **JSON Data**: Static or generated JSON files (e.g., schemas, debug dumps) MUST reside in the `json/` directory.
    *   **Reports**: Scan output files and logs MUST reside in the `reports/` directory or its subdirectories.
    *   **Project Root Exclusions**: The project root is reserved ONLY for:
        *   Configuration files (`.env`, `.secrets`, `.config`, `pyrefly.toml`)
        *   Database files (`reports.db`)
        *   Documentation (`README.md`, `LICENSE`, `AUTHORS`)
        *   Entry point shell scripts (if absolutely necessary, e.g., (binary/script)
    *   **Path Resolution**:
        *   Scripts in `python/` MUST resolve paths relative to the **Project Root**.
        *   Use `Path(__file__).resolve().parent.parent` to locate the root directory reliably.
        *   Do not assume the Current Working Directory (CWD) is the script's directory.
    *   **Cleanliness**: Do not clutter the root directory with temporary scan files or debug artifacts.