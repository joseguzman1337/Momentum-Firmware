---
description: Run the full PR1M3 logic (API Orchestrator, RAG Agents, and Recon Pipeline)
---

# PR1M3 Logic Workflow
This workflow defines the startup and verification logic for the PR1M3 system.

## 1. Startup
1. **Kill existing processes** to ensure a clean state:
   ```bash
   pkill -f nuclei_h1_scanner.py; pkill -f nuclei; echo "Stopped previous instances."
   ```

2. **Start the API Orchestrator**:
   This launches the `nuclei_h1_scanner.py`, which includes:
   - **Recon Pipeline**: `subfinder` -> `dnsx` -> `naabu` -> `httpx` -> `katana`
   - **RAG Agents**: `rag_super_agents.py` for template error fixing.
   - **Nuclei Scan**: Core vulnerability scanning.
   - **CVE Enrichment**: `cvemap` integration.
   - **Database**: `reports.db` persistence.

   ```bash
   python3 nuclei_h1_scanner.py > orchestrator_api.log 2>&1 &
   echo "PR1M3 API Orchestrator started in background."
   ```

## 2. Verification
1. **Wait for boot** (give it a few seconds).

2. **Check Status API**:
   Query the orchestrator to confirm it's running and see RAG stats.
   ```bash
   curl -s http://localhost:8080/api/status | json_pp
   ```

3. **Monitor Logs**:
   Tail the logs to see real-time progress of Recon and Scanning.
   ```bash
   tail -f orchestrator_api.log
   ```

## 3. Operations (Manual Control)
- **Stop Scan**:
  ```bash
  curl -X POST http://localhost:8080/api/scan/stop
  ```
- **Start Scan**:
  ```bash
  curl -X POST http://localhost:8080/api/scan/start
  ```
- **Get Findings Summary**:
  ```bash
  curl http://localhost:8080/api/findings
  ```

## 4. Maintenance
- **Review Database**:
  Check `reports.db` for recorded findings.
  ```bash
  sqlite3 reports.db "SELECT count(*) FROM nuclei_findings;"
  ```
