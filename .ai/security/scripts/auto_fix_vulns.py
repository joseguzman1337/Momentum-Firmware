#!/usr/bin/env python3
"""
Security Vulnerability Auto-Fixer
Assigns and fixes GitHub Code Scanning alerts using Claude and Codex AI agents.
"""

import json
import subprocess
import sys
from datetime import datetime

def get_alerts():
    """Fetch all open code scanning alerts from GitHub."""
    cmd = [
        "gh", "api", "/repos/joseguzman1337/Momentum-Firmware/code-scanning/alerts",
        "--jq", '.[] | select(.state == "open") | {number, rule: .rule.id, severity: .rule.severity, file: .most_recent_instance.location.path, line: .most_recent_instance.location.start_line, message: .rule.description}'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/Users/x/x/Momentum-Firmware")
    
    alerts = []
    for line in result.stdout.strip().split('\n'):
        if line:
            alerts.append(json.loads(line))
    return alerts

def assign_to_agent(alert):
    """Determine which AI agent should handle this vulnerability."""
    severity = alert['severity']
    rule = alert['rule']
    
    # High-severity and crypto issues go to Claude (security expert)
    if severity == 'error' or 'crypto' in rule or 'security' in rule:
        return 'claude'
    # Code quality and logic issues go to Codex
    else:
        return 'codex'

def create_fix_issue(alert, agent):
    """Create a GitHub issue for the vulnerability fix."""
    title = f"[{agent.upper()}] Fix {alert['rule']}: {alert['file']}:{alert['line']}"
    body = f"""## Security Vulnerability Auto-Fix Request

**Alert**: #{alert['number']}
**Severity**: {alert['severity']}
**Rule**: `{alert['rule']}`
**File**: `{alert['file']}`
**Line**: {alert['line']}

**Description**: {alert.get('message', 'N/A')}

---

**Assigned to**: @{agent}

**Action Required**:
1. Analyze the vulnerability
2. Implement a secure fix
3. Create a PR with the fix
4. Reference this issue in the PR

**Auto-generated**: {datetime.now().isoformat()}
"""
    
    cmd = [
        "gh", "issue", "create",
        "--title", title,
        "--body", body,
        "--label", f"security,{agent},auto-fix",
        "--assignee", "@me"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/Users/x/x/Momentum-Firmware")
    return result.stdout.strip()

def main():
    print("🔍 Fetching security vulnerabilities...")
    alerts = get_alerts()
    
    print(f"📊 Found {len(alerts)} open security alerts")
    
    assignments = {'claude': [], 'codex': []}
    
    for alert in alerts:
        agent = assign_to_agent(alert)
        assignments[agent].append(alert)
        print(f"  [{agent.upper()}] Alert #{alert['number']}: {alert['rule']} ({alert['severity']})")
    
    print(f"\n📋 Assignment Summary:")
    print(f"  Claude (Security): {len(assignments['claude'])} alerts")
    print(f"  Codex (Code Quality): {len(assignments['codex'])} alerts")
    
    print(f"\n🚀 Creating fix issues...")
    
    created_issues = []
    for agent, agent_alerts in assignments.items():
        for alert in agent_alerts:
            issue_url = create_fix_issue(alert, agent)
            created_issues.append(issue_url)
            print(f"  ✅ Created: {issue_url}")
    
    print(f"\n✨ Complete! Created {len(created_issues)} fix issues")
    print(f"\nNext steps:")
    print(f"  1. AI agents will analyze and fix vulnerabilities")
    print(f"  2. PRs will be created automatically")
    print(f"  3. Review and merge the fixes")

if __name__ == "__main__":
    main()
