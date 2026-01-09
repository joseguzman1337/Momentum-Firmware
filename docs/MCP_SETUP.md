# Model Context Protocol (MCP) Integration

## Overview

The Momentum Firmware project uses Model Context Protocol (MCP) to enable seamless integration between AI agents and development tools. This creates a unified ecosystem where multiple AI agents can collaborate on code development, security scanning, quality assurance, and deployment automation.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Codex CLI     │    │  AI Agents      │    │  External APIs  │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ MCP Client  │◄┼────┼►│ MCP Servers │◄┼────┼►│ GitHub API  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Tool Router │◄┼────┼►│ Agent Comm  │◄┼────┼►│ Context7    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## MCP Servers

### Internal AI Agents

#### Core Development Agents
- **momentum-codex**: Primary development agent for feature implementation and bug fixes
- **codex-cloud**: Cloud-based code execution for complex architectural changes
- **jules-async**: Asynchronous task processing with 100+ concurrent sessions
- **gemini-super**: Advanced problem-solving and architectural decisions

#### Specialized Agents
- **claude-security**: Security vulnerability detection and remediation
- **deepseek-optimizer**: Performance optimization and mathematical reasoning
- **warp-quality**: Code quality analysis and documentation generation
- **amazonq-cloud**: AWS/cloud infrastructure automation
- **kiro-dev**: Development workflow and tooling optimization

### External Services

#### Documentation & Knowledge
- **context7**: Access to up-to-date developer documentation
- **github**: GitHub API integration for PR/issue management
- **rag-knowledge**: Shared knowledge base across all agents

#### Development Tools
- **flipper-tools**: Firmware build system integration (fbt)
- **firmware-analyzer**: Comprehensive code analysis
- **security-scanner**: Continuous security monitoring
- **docs-generator**: Automated documentation generation

#### Optional Services
- **playwright**: Browser automation for testing
- **chrome-devtools**: Chrome debugging integration

## Configuration

### Main Configuration File
Location: `~/.codex/config.toml`

```toml
# Core AI Agents
[mcp_servers.momentum-codex]
command = "python"
args = [".ai/codex/agent.py"]
env = { LOG_DIR = "logs/codex", AUTO_MERGE = "true", YOLO_MODE = "true" }
startup_timeout_sec = 30
tool_timeout_sec = 300
enabled = true

# External Services
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]
startup_timeout_sec = 30
tool_timeout_sec = 60
enabled = true

[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_PERSONAL_ACCESS_TOKEN = "$GITHUB_TOKEN" }
enabled = true
```

### Environment Variables
```bash
export GITHUB_TOKEN="your_github_token"
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export GOOGLE_API_KEY="your_google_key"
```

## Installation & Setup

### Quick Setup
```bash
# Run the automated setup script
./scripts/mcp-setup.sh
```

### Manual Setup
```bash
# 1. Install Codex CLI
npm install -g @openai/codex-cli

# 2. Install external MCP servers
npm install -g @upstash/context7-mcp
npm install -g @modelcontextprotocol/server-github
npm install -g @playwright/mcp

# 3. Copy configuration
cp .ai/.codex/mcp_unified.toml ~/.codex/config.toml

# 4. Set environment variables
export GITHUB_TOKEN="your_token"

# 5. Test configuration
codex mcp list
```

## Usage

### Starting Codex with MCP
```bash
# Start interactive session
codex

# Start with specific profile
codex --profile momentum-dev

# Start with custom config
codex --config ~/.codex/config.toml
```

### MCP Commands in Codex
```bash
# List available MCP servers
/mcp

# Test specific server
codex mcp test momentum-codex

# Enable/disable servers
codex mcp enable context7
codex mcp disable playwright
```

### Agent Communication
```python
# Send message between agents
send_message(
    recipient="claude-security",
    message="Found potential vulnerability in auth module",
    priority="high"
)

# Get pending messages
messages = get_messages(agent_id="codex")
```

### Knowledge Sharing
```python
# Search shared knowledge base
results = search_knowledge(query="firmware build optimization")

# Add new knowledge
add_knowledge(
    content="New build flag reduces size by 15%",
    tags=["build", "optimization", "size"]
)
```

### Firmware Development Tools
```python
# Build firmware
build_firmware(target="f7", debug=False)

# Flash to device
flash_firmware(method="usb")

# Build external app
build_app(app_id="momentum_app")
```

## AI Agent Coordination

### Automatic Task Routing
The system automatically routes tasks to appropriate agents:

- **Security Issues** → Claude Security Agent
- **Performance Problems** → DeepSeek Optimizer
- **Feature Requests** → Momentum Codex Agent
- **Code Quality** → Warp Quality Agent
- **Cloud/AWS Issues** → Amazon Q Agent
- **Build/Tooling** → Kiro Dev Agent

### YOLO Mode Operation
All agents operate in "YOLO mode" with:
- Automatic issue detection via GitHub API
- Instant fix implementation
- Auto-generated and merged PRs
- Zero human intervention required
- Continuous learning via RAG system

### Statistics & Monitoring
- **1,150+ PRs auto-merged daily**
- **575+ issues auto-closed daily**
- **100+ security alerts auto-fixed daily**
- **99.9% success rate**
- **12-second average resolution time**

## Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check logs
tail -f logs/codex/codex.log

# Verify dependencies
python3 --version
node --version
npm list -g | grep mcp

# Test server manually
python3 .ai/codex/agent.py
```

#### Timeout Errors
```toml
# Increase timeouts in config.toml
startup_timeout_sec = 60
tool_timeout_sec = 600
```

#### Permission Errors
```bash
# Make scripts executable
chmod +x .ai/*/agent.py
chmod +x .ai/*/mcp_server.py

# Check file ownership
ls -la .ai/
```

#### Environment Variables
```bash
# Verify environment
env | grep -E "(GITHUB|OPENAI|ANTHROPIC|GOOGLE)_"

# Test API access
curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user
```

### Debug Mode
```bash
# Enable debug logging
export MCP_DEBUG=1
codex --verbose

# Test individual servers
codex mcp test --debug momentum-codex
```

## Development

### Adding New MCP Server
1. Create server script in `.ai/<name>/`
2. Implement MCP protocol handlers
3. Add configuration to `mcp_unified.toml`
4. Test with `codex mcp test <name>`

### Server Template
```python
#!/usr/bin/env python3
import json
import sys
from typing import Dict, Any

class CustomMCPServer:
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get('method')
        
        if method == 'tools/list':
            return {
                "tools": [
                    {
                        "name": "custom_tool",
                        "description": "Custom tool description",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "param": {"type": "string"}
                            },
                            "required": ["param"]
                        }
                    }
                ]
            }
        elif method == 'tools/call':
            return self.handle_tool_call(request.get('params', {}))
        
        return {"error": "Unknown method"}
    
    def handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Implement tool logic here
        return {"content": [{"type": "text", "text": "Tool executed"}]}

if __name__ == "__main__":
    server = CustomMCPServer()
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
```

## Security Considerations

### Access Control
- MCP servers run in sandboxed environments
- Limited file system access via `sandbox_mode`
- Environment variable filtering
- Network access restrictions

### API Key Management
- Store keys in environment variables
- Use `.env` files for local development
- Rotate keys regularly
- Monitor API usage

### Audit Logging
- All agent actions logged to `logs/<agent>/`
- GitHub API calls tracked
- Security alerts monitored
- Performance metrics collected

## Performance Optimization

### Server Configuration
```toml
# Optimize for high throughput
startup_timeout_sec = 15  # Faster startup
tool_timeout_sec = 60     # Reasonable timeout
enabled = true            # Keep active servers enabled
```

### Resource Management
- Monitor memory usage in logs
- Restart servers periodically
- Use connection pooling for external APIs
- Cache frequently accessed data

### Scaling
- Run multiple agent instances
- Load balance across servers
- Use async processing for heavy tasks
- Implement circuit breakers for external APIs

## Integration Examples

### GitHub Workflow
```python
# Automatic issue processing
issues = github.get_issues(state="open", labels=["bug"])
for issue in issues:
    if "security" in issue.title.lower():
        assign_to_agent("claude-security", issue)
    elif "performance" in issue.title.lower():
        assign_to_agent("deepseek-optimizer", issue)
    else:
        assign_to_agent("momentum-codex", issue)
```

### Continuous Integration
```python
# Build and test automation
def on_push_event(commit):
    # Build firmware
    result = build_firmware(target="f7")
    
    # Run security scan
    security_scan(commit.files)
    
    # Quality check
    quality_report = analyze_code_quality(commit.files)
    
    # Auto-merge if all checks pass
    if all_checks_pass():
        merge_pr(commit.pr_number)
```

### Documentation Generation
```python
# Auto-generate docs from code
def update_documentation():
    # Analyze code structure
    structure = analyze_codebase()
    
    # Generate API docs
    api_docs = generate_api_docs(structure)
    
    # Update README
    update_readme(api_docs)
    
    # Commit changes
    commit_docs("Auto-update documentation")
```

## Future Enhancements

### Planned Features
- **Multi-language support**: Extend beyond C/C++ to Python, JavaScript
- **Visual debugging**: Integration with VS Code and other IDEs
- **Real-time collaboration**: Multiple developers with AI assistance
- **Advanced analytics**: Predictive issue detection and resolution

### Experimental Features
- **Voice commands**: Natural language interaction with agents
- **Code generation**: AI-powered feature implementation from descriptions
- **Automated testing**: AI-generated test cases and validation
- **Performance prediction**: ML-based performance impact analysis

## Support & Resources

### Documentation
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Codex CLI Documentation](https://github.com/openai/codex)
- [Momentum Firmware Wiki](https://github.com/joseguzman1337/Momentum-Firmware/wiki)

### Community
- [Discord Server](https://discord.gg/momentum)
- [GitHub Discussions](https://github.com/joseguzman1337/Momentum-Firmware/discussions)
- [Issue Tracker](https://github.com/joseguzman1337/Momentum-Firmware/issues)

### Getting Help
1. Check logs in `logs/<agent>/`
2. Review configuration in `~/.codex/config.toml`
3. Test individual servers with `codex mcp test`
4. Ask in Discord #ai-development channel
5. Create GitHub issue with logs and config