# Self-Hosted GitHub Actions Runner Setup

## Installation

### 1. Download and Configure Runner

```bash
# Create runner directory
mkdir -p ~/actions-runner && cd ~/actions-runner

# Download latest runner
curl -o actions-runner-osx-arm64-2.321.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-osx-arm64-2.321.0.tar.gz

# Extract
tar xzf ./actions-runner-osx-arm64-2.321.0.tar.gz

# Configure
./config.sh --url https://github.com/joseguzman1337/Momentum-Firmware --token <YOUR_TOKEN>
```

### 2. Get Registration Token

```bash
# Generate a new runner token
gh api -X POST /repos/joseguzman1337/Momentum-Firmware/actions/runners/registration-token --jq .token
```

### 3. Install as Service (macOS)

```bash
# Install service
sudo ./svc.sh install

# Start service
sudo ./svc.sh start

# Check status
sudo ./svc.sh status
```

### 4. Configure Environment Variables

Create `~/actions-runner/.env`:

```bash
ANTHROPIC_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_pat_here
```

### 5. Install Python Dependencies

```bash
pip3 install anthropic openai requests
```

## Usage

### Manual Trigger

```bash
# Trigger workflow manually
gh workflow run security-auto-fix.yml
```

### Automatic Trigger

The workflow automatically runs when:
1. An issue is labeled with `auto-fix`
2. Every 6 hours (scheduled)
3. Manual dispatch via GitHub UI

## Monitoring

```bash
# View runner logs
tail -f ~/actions-runner/_diag/Runner_*.log

# Check runner status
gh api /repos/joseguzman1337/Momentum-Firmware/actions/runners
```

## Troubleshooting

### Runner Not Appearing

```bash
# Re-register runner
cd ~/actions-runner
./config.sh remove
./config.sh --url https://github.com/joseguzman1337/Momentum-Firmware --token <NEW_TOKEN>
```

### Workflow Not Triggering

```bash
# Check workflow status
gh workflow view security-auto-fix.yml

# List recent runs
gh run list --workflow=security-auto-fix.yml
```

## Security Notes

1. **API Keys**: Store in GitHub Secrets or local `.env` file
2. **Runner Isolation**: Run in dedicated user account
3. **Network Access**: Ensure runner can access GitHub and AI APIs
4. **Permissions**: Runner needs write access to create PRs

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Security Scanning (CodeQL)                            │ │
│  │  ↓                                                      │ │
│  │  24 Vulnerabilities Detected                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Auto-Fix Script (auto_fix_vulns.py)            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • Fetch alerts via GitHub API                         │ │
│  │  • Assign to Claude (security) or Codex (quality)      │ │
│  │  • Create GitHub issues for tracking                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│         Self-Hosted Runner (security-auto-fix.yml)          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Triggered by: Issue labeled "auto-fix"                │ │
│  │  ↓                                                      │ │
│  │  1. Extract vulnerability details from issue           │ │
│  │  2. Read vulnerable code + context                     │ │
│  │  3. Call AI agent (Claude/Codex)                       │ │
│  │  4. Generate secure fix                                │ │
│  │  5. Create PR with fix                                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    AI Agents (Local)                         │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │  Claude (Anthropic)  │  │  Codex (OpenAI GPT-4)        │ │
│  │  • Security fixes    │  │  • Code quality fixes        │ │
│  │  • Crypto issues     │  │  • Logic improvements        │ │
│  │  • 9 alerts          │  │  • 15 alerts                 │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Pull Requests Created                       │
│  • Auto-reviewed and tested                                  │
│  • Merged to dev → master                                    │
│  • Closes security issues                                    │
└─────────────────────────────────────────────────────────────┘
```
