#!/usr/bin/env python3
"""
Linear-Codex Integration for Momentum Firmware
Auto-assigns GitHub issues to Codex via Linear
"""

import os
import json
import requests
from datetime import datetime

class LinearCodexBridge:
    def __init__(self):
        self.linear_api_key = os.getenv('LINEAR_API_KEY')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.team_id = os.getenv('LINEAR_TEAM_ID', 'momentum-firmware')
        
    def sync_github_to_linear(self, github_issue):
        """Convert GitHub issue to Linear and auto-assign to Codex"""
        mutation = f'''
        mutation {{
            issueCreate(input: {{
                title: "{github_issue['title']}"
                description: "GitHub #{github_issue['number']}\\n\\n{github_issue['body']}"
                teamId: "{self.team_id}"
                assigneeId: "codex"
            }}) {{
                issue {{ id url }}
            }}
        }}
        '''
        
        response = requests.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": f"Bearer {self.linear_api_key}"},
            json={"query": mutation}
        )
        
        return response.json()

if __name__ == "__main__":
    bridge = LinearCodexBridge()
    print("Linear-Codex bridge active")