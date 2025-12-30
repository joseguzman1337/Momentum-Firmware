#!/usr/bin/env python3
import subprocess
import json
import time
from pathlib import Path

def process_issues():
    """Process up to 38 issues from the repository"""
    
    print("🚀 Fetching up to 38 issues from joseguzman1337/Momentum-Firmware...")
    
    # Fetch issues
    cmd = "gh issue list --repo joseguzman1337/Momentum-Firmware --limit 38 --json number,title,body"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Failed to fetch issues")
        return
        
    issues = json.loads(result.stdout)
    print(f"🎯 Successfully fetched {len(issues)} issues")
    
    for i, issue in enumerate(issues, 1):
        num = issue['number']
        title = issue['title']
        print(f"\n[{i}/{len(issues)}] Tackling Issue #{num}: {title}...")
        
        # Invoke DeepSeek Agent
        # We assume the agent will handle file detection or default to CHANGELOG.md for general fixes
        wrapper_cmd = f'./deepseek "Fix Issue #{num}: {title}" --individual-pr'
        
        # Capture output
        log_file = Path(f"logs/deepseek/issue_{num}.log")
        with open(log_file, "w") as f:
            proc = subprocess.run(wrapper_cmd, shell=True, stdout=f, stderr=f)
            
        if proc.returncode == 0:
            print(f"✅ Issue #{num} tackled successfully. Check logs/deepseek/issue_{num}.log")
        else:
            print(f"❌ Failed to tackle Issue #{num}")
            
        time.sleep(2) # Stagger requests

if __name__ == "__main__":
    process_issues()
