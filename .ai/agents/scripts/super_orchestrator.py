#!/usr/bin/env python3
"""
AI Super Agent Orchestrator
Manages all AI agents with YOLO mode, A2A communication, RAG, and MCP integration
"""

import json
import subprocess
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class AIOrchestrator:
    def __init__(self, config_path: str = ".ai/configs/master.json"):
        self.repo_root = Path("/Users/x/x/Momentum-Firmware")
        self.config_path = self.repo_root / config_path
        self.config = self.load_config()
        self.message_bus = []
        self.shared_context = {}
        
    def load_config(self) -> Dict:
        """Load master configuration"""
        with open(self.config_path) as f:
            return json.load(f)
    
    def log(self, agent: str, message: str, level: str = "INFO"):
        """Centralized logging"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "agent": agent,
            "level": level,
            "message": message
        }
        
        # Write to agent-specific log
        log_dir = self.repo_root / self.config["agents"][agent]["log_dir"]
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        print(f"[{timestamp}] [{agent.upper()}] {message}")
    
    def get_pending_issues(self) -> List[Dict]:
        """Fetch open GitHub issues"""
        try:
            result = subprocess.run(
                ["gh", "issue", "list", "--limit", "100", "--json", "number,title,labels"],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Error fetching issues: {e}")
            return []
    
    def route_task(self, issue: Dict) -> str:
        """Intelligent task routing to appropriate agent"""
        title = issue["title"].lower()
        labels = [l.get("name", "").lower() for l in issue.get("labels", [])]
        
        # Security-related -> Claude
        if any(k in title for k in ["security", "vulnerability", "cve", "exploit"]):
            return "claude"
        
        # Architecture/complex -> Gemini
        if any(k in title for k in ["architecture", "refactor", "optimize", "performance", "design"]):
            return "gemini"
        
        # Feature/bug -> Codex
        if any(k in labels for k in ["enhancement", "bug", "feature"]):
            return "codex"
        
        # Default to Codex
        return "codex"
    
    def start_codex(self, issue: Dict):
        """Start Codex agent in YOLO mode"""
        agent_config = self.config["agents"]["codex"]
        if not agent_config["enabled"]:
            return
        
        issue_num = issue["number"]
        issue_title = issue["title"]
        log_file = self.repo_root / agent_config["log_dir"] / f"issue_{issue_num}.log"
        
        self.log("codex", f"Starting task: Issue #{issue_num}: {issue_title}")
        
        cmd = [
            "codex",
            "--full-auto",
            "--search",
            "exec",
            f"Fix and resolve Issue #{issue_num}: {issue_title}. "
            f"Make sure to generate a Pull Request (or commit) message that includes 'Closes #{issue_num}' to auto-close the issue on merge."
        ]
        
        subprocess.Popen(
            cmd,
            stdout=open(log_file, "w"),
            stderr=subprocess.STDOUT,
            cwd=self.repo_root
        )
    
    def start_gemini(self, issue: Dict):
        """Start Gemini agent in YOLO mode"""
        agent_config = self.config["agents"]["gemini"]
        if not agent_config["enabled"]:
            return
        
        issue_num = issue["number"]
        issue_title = issue["title"]
        log_file = self.repo_root / agent_config["log_dir"] / f"issue_{issue_num}.log"
        
        self.log("gemini", f"Starting task: Issue #{issue_num}: {issue_title}")
        
        prompt = f"""Fix and resolve Issue #{issue_num}: {issue_title}

Analyze thoroughly, design optimal solution, implement with proper error handling.
Include 'Closes #{issue_num}' in commit message."""
        
        cmd = [
            "gemini",
            "-p", prompt,
            "--approval-mode", "yolo",
            "-o", "json"
        ]
        
        subprocess.Popen(
            cmd,
            stdout=open(log_file, "w"),
            stderr=subprocess.STDOUT,
            cwd=self.repo_root
        )
    
    def start_claude(self, alert: Dict):
        """Start Claude agent in YOLO mode for security"""
        agent_config = self.config["agents"]["claude"]
        if not agent_config["enabled"]:
            return
        
        alert_num = alert["number"]
        log_file = self.repo_root / agent_config["log_dir"] / f"alert_{alert_num}.log"
        
        self.log("claude", f"Starting security fix: Alert #{alert_num}")
        
        prompt = f"Fix security alert #{alert_num}. Apply secure patches with validation."
        
        cmd = [
            "claude",
            "-p", prompt,
            "--dangerously-skip-permissions",
            "-o", "json"
        ]
        
        subprocess.Popen(
            cmd,
            stdout=open(log_file, "w"),
            stderr=subprocess.STDOUT,
            cwd=self.repo_root
        )
    
    def start_jules(self, issue: Dict):
        """Start Jules async session"""
        agent_config = self.config["agents"]["jules"]
        if not agent_config["enabled"]:
            return
        
        issue_num = issue["number"]
        issue_title = issue["title"]
        
        self.log("jules", f"Creating async session: Issue #{issue_num}")
        
        cmd = [
            f"{os.environ.get('PNPM_HOME', '$HOME/.pnpm-global')}/jules",
            "new",
            "--repo", "joseguzman1337/Momentum-Firmware",
            f"Fix issue #{issue_num}: {issue_title}"
        ]
        
        subprocess.run(cmd, cwd=self.repo_root)
    
    def start_warp(self):
        """Start Warp automation in batch mode"""
        agent_config = self.config["agents"]["warp"]
        if not agent_config["enabled"]:
            return
        
        self.log("warp", "Starting batch automation")
        
        # Run Warp automation script
        cmd = ["python3", ".ai/agents/warp_automation.py"]
        
        log_file = self.repo_root / agent_config["log_dir"] / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        subprocess.Popen(
            cmd,
            stdout=open(log_file, "w"),
            stderr=subprocess.STDOUT,
            cwd=self.repo_root
        )
    
    def check_and_merge_prs(self):
        """Auto-merge ready PRs"""
        try:
            result = subprocess.run(
                ["gh", "pr", "list", "--json", "number,title,mergeable"],
                capture_output=True,
                text=True,
                check=True
            )
            prs = json.loads(result.stdout)
            
            for pr in prs:
                if pr.get("mergeable") == "MERGEABLE":
                    pr_num = pr["number"]
                    self.log("orchestrator", f"Auto-merging PR #{pr_num}")
                    subprocess.run(["gh", "pr", "merge", str(pr_num), "--merge"])
        except Exception as e:
            print(f"Error checking PRs: {e}")
    
    def run_super_agent(self):
        """Main orchestration loop"""
        print("🤖 AI Super Agent Orchestrator")
        print("=" * 60)
        print(f"Mode: YOLO (Auto-approve all actions)")
        print(f"A2A Communication: {self.config['a2a_communication']['enabled']}")
        print(f"RAG: {self.config['rag']['enabled']}")
        print(f"Continuous: {self.config['automation']['continuous_mode']}")
        print("=" * 60)
        print()
        
        iteration = 0
        while True:
            iteration += 1
            print(f"\n🔄 Iteration {iteration} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Fetch pending issues
            issues = self.get_pending_issues()
            print(f"📋 Found {len(issues)} open issues")
            
            # Route and assign tasks
            for issue in issues[:5]:  # Process top 5
                agent = self.route_task(issue)
                print(f"   #{issue['number']}: {issue['title'][:50]}... -> {agent.upper()}")
                
                if agent == "codex":
                    self.start_codex(issue)
                elif agent == "gemini":
                    self.start_gemini(issue)
                elif agent == "jules":
                    self.start_jules(issue)
            
            # Run Warp batch automation every iteration
            if iteration % 2 == 0:  # Every 2nd iteration to avoid overload
                print("   Running Warp batch automation...")
                self.start_warp()
            
            # Check and merge ready PRs
            self.check_and_merge_prs()
            
            # Health check interval
            if not self.config["automation"]["continuous_mode"]:
                break
            
            sleep_time = self.config["automation"]["health_check_interval"]
            print(f"\n⏸️  Sleeping for {sleep_time}s...")
            time.sleep(sleep_time)

def main():
    orchestrator = AIOrchestrator()
    orchestrator.run_super_agent()

if __name__ == "__main__":
    main()
