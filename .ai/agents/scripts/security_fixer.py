#!/usr/bin/env python3
"""
Real-time Security Vulnerability Fixer
Assigns all open security alerts to Claude in parallel
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def get_security_alerts():
    """Fetch all open code scanning alerts"""
    try:
        result = subprocess.run(
            ["gh", "api", "/repos/joseguzman1337/Momentum-Firmware/code-scanning/alerts"],
            capture_output=True,
            text=True,
            check=True
        )
        alerts = json.loads(result.stdout)
        return [a for a in alerts if a.get("state") == "open"]
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        return []

def start_claude_fix(alert):
    """Start Claude to fix a specific security alert"""
    alert_num = alert["number"]
    rule_id = alert["rule"]["id"]
    severity = alert["rule"]["severity"]
    location = alert["most_recent_instance"]["location"]["path"]
    
    log_dir = Path("/Users/x/x/Momentum-Firmware/logs/claude")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"security_alert_{alert_num}.log"
    
    prompt = f"""Fix security vulnerability in {location}

Alert #{alert_num}:
- Rule: {rule_id}
- Severity: {severity}
- File: {location}

Requirements:
1. Analyze the vulnerability thoroughly
2. Apply secure fix with proper validation
3. Add comments explaining the security improvement
4. Ensure no functionality is broken
5. Include 'Security fix: Alert #{alert_num}' in commit message

Use YOLO mode - auto-approve all changes."""
    
    print(f"🛡️  Starting Claude on Alert #{alert_num}: {rule_id} ({severity}) in {location}")
    
    cmd = [
        "claude",
        "-p", prompt,
        "--dangerously-skip-permissions"
    ]
    
    subprocess.Popen(
        cmd,
        stdout=open(log_file, "w"),
        stderr=subprocess.STDOUT,
        cwd="/Users/x/x/Momentum-Firmware"
    )
    
    return alert_num

def main():
    print("🛡️  REAL-TIME SECURITY VULNERABILITY FIXER")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Fetch alerts
    print("📋 Fetching security alerts...")
    alerts = get_security_alerts()
    print(f"Found {len(alerts)} open security vulnerabilities")
    print()
    
    if not alerts:
        print("No open alerts to fix")
        return
    
    # Group by severity
    errors = [a for a in alerts if a["rule"]["severity"] == "error"]
    warnings = [a for a in alerts if a["rule"]["severity"] == "warning"]
    notes = [a for a in alerts if a["rule"]["severity"] == "note"]
    
    print(f"📊 Breakdown:")
    print(f"  🔴 Errors: {len(errors)}")
    print(f"  🟡 Warnings: {len(warnings)}")
    print(f"  🔵 Notes: {len(notes)}")
    print()
    
    # Start Claude on all alerts in parallel
    print("🚀 Launching Claude agents in parallel...")
    print()
    
    fixed_count = 0
    
    # Process errors first (highest priority)
    for alert in errors:
        start_claude_fix(alert)
        fixed_count += 1
    
    # Then warnings
    for alert in warnings:
        start_claude_fix(alert)
        fixed_count += 1
    
    # Finally notes
    for alert in notes:
        start_claude_fix(alert)
        fixed_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ Launched {fixed_count} Claude agents")
    print(f"📊 Monitor progress: tail -f logs/claude/security_alert_*.log")
    print(f"⏱️  Estimated completion: 10-15 minutes")
    print("=" * 60)

if __name__ == "__main__":
    main()
