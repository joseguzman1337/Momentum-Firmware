#!/usr/bin/env python3
"""
Codex Slack Integration for Momentum Firmware
Handles @Codex mentions and routes tasks to appropriate environments
"""

import os
import json
import logging
from datetime import datetime

# Setup logging
log_dir = "logs/codex"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=f"{log_dir}/slack_{datetime.now().strftime('%Y%m%d')}.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CodexSlackHandler:
    def __init__(self):
        self.environments = {
            "momentum-firmware": {
                "repo": "joseguzman1337/Momentum-Firmware",
                "branch": "dev",
                "keywords": ["firmware", "flipper", "momentum", "embedded"]
            }
        }
    
    def process_mention(self, message, thread_context=None):
        """Process @Codex mention and route to appropriate environment"""
        environment = self.select_environment(message, thread_context)
        
        logging.info(f"Processing Codex mention: {message[:100]}...")
        logging.info(f"Selected environment: {environment}")
        
        return {
            "environment": environment,
            "task_url": f"https://chatgpt.com/codex/tasks/{self.generate_task_id()}",
            "status": "acknowledged"
        }
    
    def select_environment(self, message, context=None):
        """Select best environment based on message content"""
        message_lower = message.lower()
        
        # Check for explicit environment mention
        if "momentum" in message_lower or "firmware" in message_lower:
            return "momentum-firmware"
        
        # Default to momentum-firmware for this project
        return "momentum-firmware"
    
    def generate_task_id(self):
        """Generate unique task ID"""
        return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if __name__ == "__main__":
    handler = CodexSlackHandler()
    print("Codex Slack integration ready")