---
description: Execute all GitHub Actions workflows locally using act
---

# Execute All GitHub Actions Workflows Locally

This workflow executes each GitHub Actions workflow file locally using `act` (a tool that runs GitHub Actions locally).

## Prerequisites

1. **act** must be installed (already confirmed: `/opt/homebrew/bin/act`)
2. **Docker** must be running (act uses Docker to simulate GitHub runners)
3. **Environment variables** and secrets must be configured

## Execution Steps

// turbo-all
1. **Check Docker is running**
```bash
docker info
```


3. **List all workflow files**
```bash
find .github/workflows -name "*.yml" -type f | sort
```

4. **Execute snyk-infrastructure.yml workflow**
```bash
cd / && act pull_request \
  --workflows .github/workflows/snyk-infrastructure.yml \
  --secret-file
  --env-file .env \
  --verbose \
  --container-architecture linux/amd64
```

6. **Execute codeql.yml workflow**
```bash
cd / && act push \
  --workflows .github/workflows/codeql.yml \
  --secret-file
  --verbose \
  --container-architecture linux/amd64
```

7. **Execute semgrep.yml workflow**
```bash
cd / && act pull_request \
  --workflows .github/workflows/semgrep.yml \
  --secret-file
  --verbose \
  --container-architecture linux/amd64
```

8. **Execute checkov.yml workflow**
```bash
cd / && act pull_request \
  --workflows .github/workflows/checkov.yml \
  --secret-file
  --verbose \
  --container-architecture linux/amd64
```

9. **Execute dependency-review.yml workflow**
```bash
cd / && act pull_request \
  --workflows .github/workflows/dependency-review.yml \
  --secret-file
  --verbose \
  --container-architecture linux/amd64
```

10. **Execute scorecards.yml workflow**
```bash
cd / && act schedule \
  --workflows .github/workflows/scorecards.yml \
  --secret-file
  --verbose \
  --container-architecture linux/amd64
```

## Auto-Fix Strategy

For each workflow execution:
1. **Monitor output** for errors
2. **Identify error type**:
   - Missing dependencies → Install them
   - Configuration errors → Fix workflow YAML
   - Permission errors → Adjust permissions
   - Token/secret errors → Update .secrets file
3. **Apply fixes** immediately
4. **Re-run** the workflow
5. **Verify** success before moving to next workflow

## Notes

- Some workflows may require specific triggers (push, pull_request, schedule)
- Container scans require Docker images to be built first
- Some security scans may require external API access
- Workflows designed for cloud runners may need adaptation for local execution
