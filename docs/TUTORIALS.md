# Momentum Firmware Development Tutorials

## Quick Start Guides

### 1. Initial Setup
```bash
# Trust the project folder
./scripts/trust-manager.sh setup

# Configure Gemini CLI for firmware development
gemini /configure
```

### 2. Development Workflow
```bash
# Start development session
./scripts/quick-resume.sh

# Build and test
gemini /build

# Review changes
./scripts/automation/review-changes.sh

# Generate commit message
./scripts/automation/generate-commit.sh --auto
```

### 3. MCP Server Integration
```bash
# Setup GitHub integration
export GITHUB_PERSONAL_ACCESS_TOKEN="your_token"
./scripts/mcp-setup.sh github

# Test MCP connection
./scripts/mcp-setup.sh test
```

## Advanced Features

### Session Management
- Resume previous work: `gemini --resume`
- Session analysis: `./scripts/session-manager.sh list`
- Development summaries: `gemini /dev:summary`

### Observability
- Monitor development: `./scripts/telemetry-dashboard.sh`
- Analyze patterns: `./scripts/telemetry-analyzer.sh summary`
- Export reports: `./scripts/telemetry-analyzer.sh export`

### Automation
- Pre-commit checks: `./scripts/automation/run-all.sh pre-commit`
- Build analysis: `./scripts/automation/analyze-build.sh`
- Documentation: `./scripts/automation/generate-docs.sh applications/`

## Custom Commands

### Firmware-Specific
- `/build` - Build and flash firmware
- `/package` - Generate TGZ package
- `/app:launch <name>` - Launch specific app
- `/review <code>` - Code review for firmware

### Project Management
- `/status` - Git status and workflow suggestions
- `/telemetry` - Development metrics overview
- `/trust` - Check folder trust status
- `/mcp` - Manage MCP servers

## Security & Trust

### Folder Trust Setup
1. Enable in settings: `"folderTrust": {"enabled": true}`
2. Trust project: Select "Trust folder" when prompted
3. Verify: `./scripts/trust-manager.sh status`

### MCP Security
- Use fine-grained GitHub tokens
- Limit repository access scope
- Store tokens in environment variables
- Regular token rotation

## Troubleshooting

### Common Issues
- **Build failures**: Run `./scripts/automation/analyze-build.sh`
- **Trust issues**: Check `./scripts/trust-manager.sh status`
- **MCP connection**: Verify Docker and tokens with `./scripts/mcp-setup.sh test`

### Getting Help
- In CLI: `/help`
- Settings: `/settings`
- Permissions: `/permissions`
- Documentation: Check `docs/` directory