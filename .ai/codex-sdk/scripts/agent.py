#!/usr/bin/env python3
"""
Codex SDK Agent for Momentum Firmware
Integrates OpenAI Codex SDK for advanced code generation and issue resolution
"""

import os
import json
import subprocess
import asyncio
from datetime import datetime

class CodexSDKAgent:
    def __init__(self):
        self.log_dir = os.environ.get('LOG_DIR', 'logs/codex-sdk')
        self.auto_merge = os.environ.get('AUTO_MERGE', 'true').lower() == 'true'
        self.yolo_mode = os.environ.get('YOLO_MODE', 'true').lower() == 'true'
        
        os.makedirs(self.log_dir, exist_ok=True)
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file = f"{self.log_dir}/codex_sdk_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
        if not self.yolo_mode:
            print(f"[{timestamp}] {message}")

    async def process_issue(self, issue_data):
        """Process GitHub issue using Codex SDK"""
        issue_number = issue_data.get('number')
        title = issue_data.get('title', '')
        body = issue_data.get('body', '')
        
        self.log(f"Processing issue #{issue_number}: {title}")
        
        # Use Codex CLI exec for non-interactive processing
        task = f"Analyze and fix issue #{issue_number}: {title}\n{body}"
        
        try:
            # Run codex exec with full auto permissions
            result = subprocess.run([
                'codex', 'exec', '--full-auto', '--json',
                task
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log(f"Codex SDK successfully processed issue #{issue_number}")
                
                if self.auto_merge:
                    await self.create_and_merge_pr(issue_number, result.stdout)
                    
            else:
                self.log(f"Codex SDK failed for issue #{issue_number}: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.log(f"Codex SDK timeout for issue #{issue_number}")
        except Exception as e:
            self.log(f"Codex SDK error for issue #{issue_number}: {str(e)}")

    async def create_and_merge_pr(self, issue_number, codex_output):
        """Create and auto-merge PR from Codex output"""
        try:
            # Create PR using GitHub CLI
            pr_result = subprocess.run([
                'gh', 'pr', 'create',
                '--title', f'AI Fix: Resolve issue #{issue_number}',
                '--body', f'Auto-generated fix using Codex SDK\n\nCloses #{issue_number}',
                '--head', f'codex-sdk-fix-{issue_number}'
            ], capture_output=True, text=True)
            
            if pr_result.returncode == 0 and self.auto_merge:
                # Auto-merge the PR
                subprocess.run(['gh', 'pr', 'merge', '--auto', '--squash'])
                self.log(f"Auto-merged PR for issue #{issue_number}")
                
        except Exception as e:
            self.log(f"PR creation failed for issue #{issue_number}: {str(e)}")

if __name__ == "__main__":
    agent = CodexSDKAgent()
    agent.log("Codex SDK Agent started in YOLO mode")
    
    # Monitor GitHub issues (simplified for minimal implementation)
    asyncio.run(agent.process_issue({
        'number': 1,
        'title': 'Sample issue for Codex SDK processing',
        'body': 'This is a test issue for the Codex SDK agent'
    }))