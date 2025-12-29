# Agent Internet Access Configuration

## Overview
This configuration enables secure internet access for AI agents working on the Momentum Firmware project. It implements strict security controls to mitigate risks while allowing necessary functionality.

## Security Model

### Risk Mitigation
- **Prompt Injection Protection**: Content filtering and pattern detection
- **Domain Allowlist**: Restricted to trusted domains only
- **HTTP Method Restrictions**: Only GET, HEAD, OPTIONS allowed
- **Request Logging**: All requests logged for audit
- **Rate Limiting**: Prevents abuse and excessive usage
- **SSL Verification**: Ensures secure connections

### Configuration Files

#### `.ai/configs/internet_access.json`
Main configuration file defining:
- Domain allowlists (common dependencies + project-specific)
- HTTP method restrictions
- Agent-specific permissions
- Security policies
- Monitoring settings

#### `.ai/security/internet_validator.py`
Security validation engine that:
- Validates domains against allowlists
- Checks HTTP methods
- Detects prompt injection attempts
- Logs all requests for audit

#### `.ai/security/agent_wrapper.py`
Wrapper library providing secure internet access for agents:
- Pre-request validation
- Timeout enforcement
- Response size limits
- Error handling

## Domain Allowlists

### Common Dependencies (Preset)
Includes popular domains for development:
- Source control: github.com, gitlab.com, bitbucket.org
- Package managers: pypi.org, npmjs.com, maven.org
- Container registries: docker.com, gcr.io, ghcr.io
- Cloud providers: aws.amazon.com, google.com, azure.com

### Project-Specific Domains
- flipperzero.one (official Flipper Zero site)
- momentum-fw.dev (project website)
- discord.gg (community support)
- ko-fi.com, paypal.me (donations)

### Agent-Specific Domains
Each agent has additional allowed domains:
- **Codex**: openai.com, api.openai.com
- **Claude**: anthropic.com, api.anthropic.com
- **Gemini**: googleapis.com, cloud.google.com
- **Amazon Q**: aws.amazon.com, docs.aws.amazon.com

## HTTP Method Restrictions

### Allowed Methods
- `GET`: Read-only data retrieval
- `HEAD`: Metadata requests
- `OPTIONS`: CORS preflight requests

### Blocked Methods
- `POST`, `PUT`, `PATCH`: Data modification
- `DELETE`: Resource deletion
- `TRACE`, `CONNECT`: Security risks

## Security Policies

### Request Validation
1. Domain allowlist check
2. HTTP method validation
3. Prompt injection detection
4. Rate limit enforcement
5. SSL certificate verification

### Response Processing
1. Size limit enforcement (10MB max)
2. Content type validation
3. Security header checks
4. Malware scanning (basic)

### Logging and Monitoring
- All requests logged with timestamp, agent, URL, method
- Blocked requests generate security alerts
- Daily log rotation with 30-day retention
- Real-time monitoring dashboard

## Usage Examples

### Agent Implementation
```python
from .ai.security.agent_wrapper import amazonq_internet

# Safe internet request
try:
    response = amazonq_internet.make_request(
        "https://docs.aws.amazon.com/cli/latest/userguide/"
    )
    # Process response
except PermissionError:
    # Handle blocked request
    pass
```

### Configuration Updates
```bash
# Test configuration
python3 .ai/security/internet_validator.py

# Setup environment
.ai/security/setup_internet_access.sh

# Monitor logs
tail -f logs/internet_access_security.log
```

## Risk Assessment

### Low Risk Agents
- **Claude**: Security-focused, conservative requests
- **Gemini**: Architecture decisions, limited scope
- **Amazon Q**: AWS-specific, well-defined domains

### Medium Risk Agents
- **Codex**: Feature implementation, broader scope
- **Warp**: Code quality, analysis tasks
- **Kiro**: Development workflow automation
- **DeepSeek**: Optimization tasks

### High Risk Scenarios
- Dynamic URL construction from user input
- Processing untrusted content from web
- Executing downloaded scripts or code
- Accessing user-provided URLs

## Monitoring and Alerts

### Security Events
- Blocked domain access attempts
- Suspicious pattern detection
- Rate limit violations
- SSL certificate failures

### Audit Trail
- Complete request history
- Agent attribution
- Success/failure tracking
- Performance metrics

### Response Procedures
1. **Immediate**: Block suspicious requests
2. **Investigation**: Analyze logs and patterns
3. **Mitigation**: Update allowlists/policies
4. **Review**: Assess agent behavior

## Maintenance

### Regular Tasks
- Review and update domain allowlists
- Analyze security logs for patterns
- Update prompt injection patterns
- Performance optimization

### Emergency Procedures
- Disable internet access: Set `enabled: false`
- Block specific domains: Add to `blocked_domains`
- Agent isolation: Disable individual agents
- Full lockdown: Emergency stop all agents

## Compliance

### Data Privacy
- No PII in requests or logs
- Secure credential handling
- GDPR compliance for EU users
- Data retention policies

### Security Standards
- OWASP guidelines compliance
- Regular security assessments
- Vulnerability scanning
- Incident response procedures