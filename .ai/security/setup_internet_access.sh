#!/bin/bash
# Agent Internet Access Environment Setup
# Configures secure internet access for AI agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🔧 Setting up agent internet access configuration..."

# Create necessary directories
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/.ai/security"
mkdir -p "$PROJECT_ROOT/.ai/configs"

# Set permissions
chmod +x "$PROJECT_ROOT/.ai/security/scripts/internet_validator.py"
chmod +x "$PROJECT_ROOT/.ai/security/scripts/agent_wrapper.py"

# Create environment variables file
cat > "$PROJECT_ROOT/.ai/configs/internet_env.sh" << 'EOF'
#!/bin/bash
# Internet Access Environment Variables

export AGENT_INTERNET_ACCESS=true
export AGENT_SECURITY_MODE=strict
export AGENT_LOG_REQUESTS=true
export AGENT_TIMEOUT=30
export AGENT_MAX_RESPONSE_SIZE=10485760  # 10MB

# Domain validation
export AGENT_VALIDATE_DOMAINS=true
export AGENT_BLOCK_SUSPICIOUS=true

# HTTP method restrictions
export AGENT_ALLOWED_METHODS="GET,HEAD,OPTIONS"

# Logging
export AGENT_LOG_DIR="logs"
export AGENT_LOG_LEVEL=INFO

# Security features
export AGENT_PROMPT_INJECTION_CHECK=true
export AGENT_SSL_VERIFY=true
export AGENT_RATE_LIMIT=true
EOF

# Make environment file executable
chmod +x "$PROJECT_ROOT/.ai/configs/internet_env.sh"

# Test the configuration
echo "🧪 Testing internet access configuration..."
cd "$PROJECT_ROOT"
python3 .ai/security/scripts/internet_validator.py

# Create systemd-style service file for monitoring
cat > "$PROJECT_ROOT/.ai/security/internet_monitor.service" << EOF
[Unit]
Description=AI Agent Internet Access Monitor
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_ROOT
ExecStart=/usr/bin/python3 $PROJECT_ROOT/.ai/security/scripts/internet_validator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Agent internet access configuration complete!"
echo ""
echo "📋 Configuration Summary:"
echo "  - Internet access: ENABLED (restricted mode)"
echo "  - Security level: HIGH"
echo "  - Domain allowlist: Common dependencies + project-specific"
echo "  - HTTP methods: GET, HEAD, OPTIONS only"
echo "  - Logging: All requests logged to logs/internet_access_security.log"
echo "  - Monitoring: Real-time validation and blocking"
echo ""
echo "🔒 Security Features:"
echo "  - Prompt injection detection"
echo "  - Domain allowlist validation"
echo "  - HTTP method restrictions"
echo "  - Request rate limiting"
echo "  - SSL certificate verification"
echo "  - Response size limits"
echo ""
echo "📁 Configuration Files:"
echo "  - .ai/configs/internet_access.json"
echo "  - .ai/security/scripts/internet_validator.py"
echo "  - .ai/security/scripts/agent_wrapper.py"
echo "  - .ai/configs/internet_env.sh"