# AI Automation System

Complete AI-powered development automation with YOLO mode, A2A communication, RAG, and MCP integration.

## 🤖 Architecture

```
.ai/
├── agents/              # AI agent implementations
│   └── super_orchestrator.py  # Main orchestrator
├── configs/             # Configuration files
│   └── master.json      # Master configuration
├── mcp/                 # Model Context Protocol servers
│   ├── codex_server.json
│   ├── claude_server.json
│   ├── gemini_server.json
│   ├── jules_server.json
│   ├── claude_slack_server.json
│   └── servers/
│       ├── rag_server.py      # RAG knowledge base
│       └── a2a_server.py      # Agent-to-agent communication
├── rag/                 # Retrieval-Augmented Generation
│   ├── embeddings/      # Vector store
│   └── shared_knowledge.json  # Indexed knowledge
└── workflows/           # Workflow definitions
    └── message_bus.json # A2A message bus
```

## 🚀 Features

### 1. YOLO Mode (Auto-Approve)
All agents run in YOLO mode with automatic approval of all actions:
- **Codex**: `--full-auto` mode
- **Claude**: `--dangerously-skip-permissions`
- **Gemini**: `--approval-mode yolo`
- **Jules**: Async with auto-approval

### 2. Agent-to-Agent (A2A) Communication
Agents can communicate and coordinate:
- Message bus for inter-agent communication
- Task coordination across multiple agents
- Broadcast capabilities
- Status synchronization

### 3. RAG (Retrieval-Augmented Generation)
Shared knowledge base for all agents:
- Indexes project documentation
- Recent commits and fixes
- Open issues
- Code patterns and best practices

### 4. Super Agent Orchestrator
Intelligent task routing and management:
- Routes tasks to appropriate agents
- Monitors agent health
- Auto-merges ready PRs
- Continuous operation mode

### 5. MCP Integration
Model Context Protocol servers for each agent:
- GitHub integration
- RAG knowledge access
- A2A communication
- Custom tools per agent

## 📋 Usage

### Start Super Orchestrator (Continuous Mode)
```bash
python3 .ai/agents/super_orchestrator.py
```

### One-Time Run
Edit `.ai/configs/master.json` and set:
```json
"automation": {
  "continuous_mode": false
}
```

### Monitor Logs
```bash
# All agents
tail -f logs/*/*.log

# Specific agent
tail -f logs/codex/*.log
```

## ⚙️ Configuration

### Master Config (`.ai/configs/master.json`)

**Agent Settings:**
- `enabled`: Enable/disable agent
- `mode`: "yolo" for auto-approve
- `auto_approve`: Auto-approve all actions
- `log_dir`: Log directory path
- `tasks`: Task types handled by agent

**Super Agent:**
- `decision_model`: Model for routing decisions
- `rag_enabled`: Enable RAG integration

**A2A Communication:**
- `protocol`: "mcp" for Model Context Protocol
- `message_bus`: Path to message bus file

**RAG:**
- `vector_store`: Embeddings directory
- `knowledge_base`: Files to index
- `embedding_model`: Model for embeddings

**Automation:**
- `auto_pr_creation`: Auto-create PRs
- `auto_merge`: Auto-merge ready PRs
- `continuous_mode`: Run continuously
- `health_check_interval`: Seconds between iterations

## 🔧 Agent Capabilities

### Codex
- Feature implementation
- Bug fixes
- Code generation
- **Mode**: YOLO (`--full-auto`)

### Claude
- Security fixes
- Code review
- Vulnerability remediation
- **Mode**: YOLO (`--dangerously-skip-permissions`)

### Gemini
- Architecture decisions
- Complex refactoring
- Performance optimization
- **Mode**: YOLO (`--approval-mode yolo`)

### Jules
- Async coding tasks
- PR generation
- Multi-step workflows
- **Mode**: Async with auto-approval

### Warp
- Code quality analysis
- Documentation
- Manual review tasks
- **Mode**: Manual (task list)

### Claude Slack
- Slack message monitoring
- Coding intent detection
- Automated session routing
- **Mode**: YOLO (`--auto-route`)

### Amazon Q
- AWS/cloud infrastructure fixes
- Deployment optimization
- Cloud resource management
- **Mode**: YOLO (`q dev --auto-fix`)

### Kiro
- Development workflow automation
- Tooling optimization
- Build system fixes
- **Mode**: YOLO (`kiro fix --auto`)

## 📊 Task Routing

The super orchestrator intelligently routes tasks:

| Keywords | Agent |
|----------|-------|
| security, vulnerability, CVE | Claude |
| architecture, refactor, optimize | Gemini |
| feature, bug, enhancement | Codex |
| async, complex, multi-step | Jules |
| aws, cloud, infrastructure, deployment | Amazon Q |
| build, tooling, development, workflow, ci | Kiro |
| slack, mention, @claude, message | Claude Slack |

## 🔐 Security

- All logs in `/logs/` (gitignored)
- MCP servers run with trust mode
- RAG knowledge base is local
- A2A messages stored locally

## 📈 Monitoring

### Check Agent Status
```bash
ps aux | grep -E "codex|claude|gemini" | grep -v grep
```

### View Message Bus
```bash
cat .ai/workflows/message_bus.json | jq
```

### Check RAG Knowledge
```bash
cat .ai/rag/shared_knowledge.json | jq
```

## 🎯 Workflow

1. **Orchestrator** fetches open issues
2. **Routes** each issue to appropriate agent
3. **Agents** work in YOLO mode (auto-approve)
4. **A2A** coordinates complex tasks
5. **RAG** provides shared context
6. **Auto-merge** ready PRs
7. **Repeat** continuously

## 🛠️ Maintenance

### Reindex RAG Knowledge
```python
from .ai.mcp.servers.rag_server import RAGServer
server = RAGServer()
server.index_knowledge()
```

### Clear Message Bus
```bash
echo '[]' > .ai/workflows/message_bus.json
```

### Reset Logs
```bash
rm -rf logs/*/*.log
```

## 📝 License

Part of Momentum Firmware project.
