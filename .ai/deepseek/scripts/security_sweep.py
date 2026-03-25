#!/usr/bin/env python3
import subprocess
import json
import time
import requests
from pathlib import Path

class DeepSeekSecurityAgent:
    def __init__(self):
        self.repo = "joseguzman1337/Momentum-Firmware"
        self.log_dir = Path("logs/deepseek")
        self.log_dir.mkdir(exist_ok=True)
        
    def fetch_vulnerabilities(self):
        cmd = f"gh api repos/{self.repo}/code-scanning/alerts --jq '.[] | select(.state == \"open\")'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            alerts = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    alerts.append(json.loads(line))
            return alerts
        return []
    
    def process_vulnerability(self, alert):
        alert_id = alert['number']
        rule_id = alert['rule']['id']
        file_path = alert['most_recent_instance']['location']['path']
        
        print(f"🔍 DeepSeek processing vulnerability #{alert_id}: {rule_id}")
        
        # Create individual PR for this vulnerability
        cmd = f'deepseek --individual-pr "Fix security vulnerability #{alert_id}: {rule_id} in {file_path}"'
        
        with open(self.log_dir / f"vuln_{alert_id}.log", "w") as log:
            process = subprocess.Popen(cmd, shell=True, stdout=log, stderr=log)
            print(f"✅ DeepSeek started fixing vulnerability #{alert_id} (PID: {process.pid})")
            return process
    
    def run_security_sweep(self):
        print("🚀 DeepSeek Security Agent - Processing 24 vulnerabilities...")
        vulnerabilities = self.fetch_vulnerabilities()
        
        print(f"📊 Found {len(vulnerabilities)} open vulnerabilities")
        
        processes = []
        for vuln in vulnerabilities:
            process = self.process_vulnerability(vuln)
            processes.append(process)
            time.sleep(2)  # Stagger starts
        
        # Monitor progress
        while processes:
            active = [p for p in processes if p.poll() is None]
            completed = len(processes) - len(active)
            print(f"⚡ Progress: {completed}/{len(processes)} vulnerabilities processed")
            
            if not active:
                break
            time.sleep(10)
        
        print("🎉 All vulnerabilities assigned to DeepSeek!")

if __name__ == "__main__":
    agent = DeepSeekSecurityAgent()
    agent.run_security_sweep()