---
description: Run the H1 API Orchestrator
---
# Run H1 API Orchestrator

This workflow starts the new API-driven H1 Orchestrator.

1. Navigate to the project root
2. Run the orchestrator script

```bash
cd /Users/x/x/pr1m3
python3 python/nuclei_h1_scanner.py
```

## API Usage

Once running, you can interact with the orchestrator via HTTP:

- **Status**: `GET http://localhost:8080/status`
- **Start Scan**: `POST http://localhost:8080/scan/start` - JSON: `{"target": "https://example.com"}` or `{"program_handle": "security"}`
- **Stop Scan**: `POST http://localhost:8080/scan/stop`
- **Get Results**: `GET http://localhost:8080/results`
