#!/usr/bin/env python3
import subprocess
import json
import time
from pathlib import Path

def reprocess_vulnerabilities():
    """Reprocess all 24 vulnerabilities with working DeepSeek CLI"""
    
    # Get vulnerabilities
    cmd = "gh api repos/joseguzman1337/Momentum-Firmware/code-scanning/alerts --jq '.[] | select(.state == \"open\")'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Failed to fetch vulnerabilities")
        return
    
    vulnerabilities = []
    for line in result.stdout.strip().split('\n'):
        if line:
            vulnerabilities.append(json.loads(line))
    
    print(f"🎯 Processing {len(vulnerabilities)} vulnerabilities with working DeepSeek CLI")
    
    # Clear old logs
    subprocess.run("rm -f logs/deepseek/vuln_*.log", shell=True)
    
    # Process each vulnerability
    for i, vuln in enumerate(vulnerabilities, 1):
        alert_id = vuln['number']
        rule_id = vuln['rule']['id']
        file_path = vuln['most_recent_instance']['location']['path']
        
        print(f"🔧 [{i}/24] Processing vulnerability #{alert_id}: {rule_id}")
        
        # Use working DeepSeek CLI
        cmd = f'PATH="$PWD:$PATH" ./deepseek "Fix vulnerability #{alert_id}: {rule_id} in {file_path}"'
        
        with open(f"logs/deepseek/vuln_{alert_id}.log", "w") as log:
            result = subprocess.run(cmd, shell=True, stdout=log, stderr=log)
            
        if result.returncode == 0:
            print(f"✅ Vulnerability #{alert_id} processed successfully")
        else:
            print(f"❌ Vulnerability #{alert_id} failed")
        
        time.sleep(1)
    
    print("🎉 All 24 vulnerabilities reprocessed!")

if __name__ == "__main__":
    reprocess_vulnerabilities()