#!/usr/bin/env python3
import asyncio
import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

class AmazonQAgent:
    def __init__(self):
        self.log_dir = Path(os.getenv('LOG_DIR', 'logs/amazonq'))
        self.auto_merge = os.getenv('AUTO_MERGE', 'true').lower() == 'true'
        self.yolo_mode = os.getenv('YOLO_MODE', 'true').lower() == 'true'
        self.log_dir.mkdir(exist_ok=True)
    
    async def run_yolo_mode(self):
        """Amazon Q CLI agent in YOLO mode - auto-executing AWS/cloud tasks"""
        while True:
            try:
                # Monitor for AWS/cloud-related issues
                issues = await self.get_cloud_issues()
                for issue in issues:
                    await self.process_cloud_issue(issue)
                await asyncio.sleep(30)
            except Exception as e:
                self.log(f"Error in YOLO mode: {e}")
                await asyncio.sleep(60)
    
    async def get_cloud_issues(self):
        """Get AWS/cloud-related issues from GitHub"""
        try:
            result = subprocess.run([
                'gh', 'issue', 'list', '--json', 'number,title,body,labels',
                '--search', 'aws OR cloud OR infrastructure OR deployment'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return []
        except Exception as e:
            self.log(f"Error fetching cloud issues: {e}")
            return []
    
    async def process_cloud_issue(self, issue):
        """Process cloud/AWS issue with Amazon Q CLI"""
        issue_num = issue['number']
        title = issue['title']
        
        self.log(f"Processing cloud issue #{issue_num}: {title}")
        
        try:
            # Use Amazon Q CLI to analyze and fix cloud issues
            q_result = subprocess.run([
                'q', 'dev', '--auto-fix', '--issue', str(issue_num),
                '--context', 'aws-infrastructure', '--merge'
            ], capture_output=True, text=True)
            
            if q_result.returncode == 0:
                # Auto-create and merge PR
                await self.create_pr(issue_num, title, q_result.stdout)
                self.log(f"✅ Auto-fixed cloud issue #{issue_num}")
            else:
                self.log(f"❌ Failed to fix issue #{issue_num}: {q_result.stderr}")
                
        except Exception as e:
            self.log(f"Error processing issue #{issue_num}: {e}")
    
    async def create_pr(self, issue_num, title, changes):
        """Create and auto-merge PR"""
        if not self.auto_merge:
            return
            
        branch_name = f"amazonq-fix-{issue_num}"
        
        try:
            # Create branch and commit changes
            subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', f'Amazon Q: Fix cloud issue #{issue_num}'], check=True)
            subprocess.run(['git', 'push', 'origin', branch_name], check=True)
            
            # Create PR with auto-merge
            subprocess.run([
                'gh', 'pr', 'create', '--title', f'Amazon Q: {title}',
                '--body', f'Auto-generated fix for issue #{issue_num}\n\nCloses #{issue_num}',
                '--auto-merge'
            ], check=True)
            
            self.log(f"✅ Created and auto-merged PR for issue #{issue_num}")
            
        except Exception as e:
            self.log(f"Error creating PR for issue #{issue_num}: {e}")
    
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        log_file = self.log_dir / f"amazonq_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a') as f:
            f.write(log_message + '\n')

if __name__ == "__main__":
    agent = AmazonQAgent()
    asyncio.run(agent.run_yolo_mode())