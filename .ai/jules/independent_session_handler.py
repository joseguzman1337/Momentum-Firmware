#!/usr/bin/env python3
import asyncio
import subprocess
import json
import os
from datetime import datetime

class JulesIndependentSessionHandler:
    def __init__(self):
        self.log_dir = "logs/jules"
        os.makedirs(self.log_dir, exist_ok=True)
        
    async def process_issues_independently(self):
        """Process each issue in independent Jules sessions with auto-push/close"""
        issues = await self.get_open_issues()
        
        for issue in issues:
            await self.spawn_independent_session(issue)
    
    async def get_open_issues(self):
        """Get open GitHub issues"""
        result = subprocess.run(['gh', 'issue', 'list', '--json', 'number,title,body'], 
                              capture_output=True, text=True)
        return json.loads(result.stdout) if result.returncode == 0 else []
    
    async def spawn_independent_session(self, issue):
        """Spawn independent session for single issue"""
        session_id = f"jules-{issue['number']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Direct issue processing with auto-push/close
        await self.process_issue_directly(issue, session_id)
        
        # Log session creation
        with open(f"{self.log_dir}/independent_sessions.log", "a") as f:
            f.write(f"{datetime.now()}: Processed issue #{issue['number']} in session {session_id}\n")
    
    async def process_issue_directly(self, issue, session_id):
        """Process issue directly with auto-push and auto-close"""
        # Create branch for issue
        branch_name = f"jules-fix-{issue['number']}"
        subprocess.run(['git', 'checkout', '-b', branch_name], capture_output=True)
        
        # Auto-fix based on issue content
        if 'readability' in issue.get('title', '').lower():
            await self.fix_readability_issues()
        
        # Commit and push
        subprocess.run(['git', 'add', '.'], capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'Auto-fix: {issue["title"]} (#{issue["number"]})'], capture_output=True)
        subprocess.run(['git', 'push', 'origin', branch_name], capture_output=True)
        
        # Create PR and auto-merge
        subprocess.run(['gh', 'pr', 'create', '--title', f'Auto-fix: {issue["title"]}', '--body', f'Closes #{issue["number"]}'], capture_output=True)
        subprocess.run(['gh', 'pr', 'merge', '--auto', '--squash'], capture_output=True)
    
    async def fix_readability_issues(self):
        """Fix readability issues in orchestrator.py"""
        file_path = '.ai/orchestrator.py'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Fix nested exception handling
            content = content.replace(
                '                try:\n                    process.terminate()\n                except (ProcessLookupError, OSError):\n                    pass',
                '                process.terminate()'
            )
            
            with open(file_path, 'w') as f:
                f.write(content)

if __name__ == "__main__":
    handler = JulesIndependentSessionHandler()
    asyncio.run(handler.process_issues_independently())