#!/usr/bin/env python3
import subprocess
import time
import json
from pathlib import Path

def monitor_deepseek_progress():
    log_dir = Path("logs/deepseek")
    
    print("🔍 Real-time DeepSeek Vulnerability Fix Monitor")
    print("=" * 50)
    
    while True:
        # Check active processes
        result = subprocess.run("ps aux | grep deepseek | grep -v grep | wc -l", 
                              shell=True, capture_output=True, text=True)
        active_processes = int(result.stdout.strip())
        
        # Check completed logs
        completed_logs = len(list(log_dir.glob("vuln_*.log")))
        
        # Check for new PRs
        pr_result = subprocess.run("gh pr list --state open --author @me | wc -l", 
                                 shell=True, capture_output=True, text=True)
        open_prs = int(pr_result.stdout.strip())
        
        print(f"⚡ Active DeepSeek processes: {active_processes}")
        print(f"📝 Vulnerability logs created: {completed_logs}/24")
        print(f"🔄 Open PRs generated: {open_prs}")
        
        if active_processes == 0 and completed_logs >= 24:
            print("✅ All vulnerabilities processed by DeepSeek!")
            break
            
        time.sleep(5)
        print("-" * 30)

if __name__ == "__main__":
    monitor_deepseek_progress()