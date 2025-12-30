#!/usr/bin/env python3
"""Claude Code in Slack integration for Momentum Firmware"""

import json
import os
from datetime import datetime

class ClaudeSlackAgent:
    def __init__(self):
        self.log_dir = os.environ.get('LOG_DIR', 'logs/claude-slack')
        self.auto_merge = os.environ.get('AUTO_MERGE', 'true').lower() == 'true'
        self.yolo_mode = os.environ.get('YOLO_MODE', 'true').lower() == 'true'
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file = f"{self.log_dir}/claude_slack_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def detect_coding_intent(self, message):
        """Detect if Slack message contains coding request"""
        coding_keywords = [
            'bug', 'fix', 'code', 'implement', 'refactor', 'debug',
            'feature', 'function', 'class', 'method', 'variable',
            'error', 'exception', 'compile', 'build', 'test'
        ]
        return any(keyword in message.lower() for keyword in coding_keywords)
    
    def route_to_claude_code(self, slack_context):
        """Route Slack request to Claude Code session"""
        if self.yolo_mode:
            self.log(f"YOLO: Auto-routing Slack request to Claude Code")
            return self.create_code_session(slack_context)
        return False
    
    def create_code_session(self, context):
        """Create Claude Code session from Slack context"""
        session_data = {
            'source': 'slack',
            'context': context,
            'repository': 'joseguzman1337/Momentum-Firmware',
            'auto_merge': self.auto_merge
        }
        
        self.log(f"Creating Claude Code session: {json.dumps(session_data)}")
        return True

if __name__ == "__main__":
    agent = ClaudeSlackAgent()
    agent.log("Claude Slack Agent started in YOLO mode")