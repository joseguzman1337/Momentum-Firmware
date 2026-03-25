#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime

class CodexCloudAgent:
    def __init__(self):
        self.log_dir = os.environ.get('LOG_DIR', 'logs/codex-cloud')
        self.auto_merge = os.environ.get('AUTO_MERGE', 'true').lower() == 'true'
        self.yolo_mode = os.environ.get('YOLO_MODE', 'true').lower() == 'true'
        
    def monitor_issues(self):
        """Monitor GitHub issues for Codex cloud tasks"""
        headers = {'Authorization': f'token {os.environ.get("GITHUB_TOKEN")}'}
        issues = requests.get('https://api.github.com/repos/joseguzman1337/Momentum-Firmware/issues', headers=headers).json()
        
        for issue in issues:
            if self.should_handle_issue(issue):
                self.delegate_to_codex_cloud(issue)
    
    def should_handle_issue(self, issue):
        """Check if issue should be handled by Codex cloud"""
        keywords = ['refactor', 'architecture', 'performance', 'optimization', 'code review']
        return any(keyword in issue['title'].lower() or keyword in issue['body'].lower() for keyword in keywords)
    
    def delegate_to_codex_cloud(self, issue):
        """Delegate task to Codex cloud via API"""
        task_data = {
            'repository': 'joseguzman1337/Momentum-Firmware',
            'issue_number': issue['number'],
            'task_type': 'code_mode',
            'auto_merge': self.auto_merge
        }
        
        self.log(f"Delegating issue #{issue['number']} to Codex cloud")
        
        if self.yolo_mode:
            self.create_pr_from_codex_result(issue)
    
    def create_pr_from_codex_result(self, issue):
        """Create PR from Codex cloud results"""
        self.log(f"Auto-creating PR for issue #{issue['number']}")
        
    def log(self, message):
        """Log agent activity"""
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file = f"{self.log_dir}/codex_cloud_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")

if __name__ == '__main__':
    agent = CodexCloudAgent()
    agent.monitor_issues()