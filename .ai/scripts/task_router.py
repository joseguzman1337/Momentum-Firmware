#!/usr/bin/env python3
import json
import requests
from pathlib import Path

class TaskRouter:
    def __init__(self):
        self.routing_rules = {
            'security': 'claude',
            'performance': 'deepseek', 
            'feature': 'codex',
            'architecture': 'gemini',
            'refactoring': 'codex-cloud',
            'quality': 'warp',
            'async': 'jules',
            'cloud': 'amazonq',
            'development': 'kiro'
        }
    
    def route_issue(self, issue_data):
        issue_type = self.classify_issue(issue_data)
        agent = self.routing_rules.get(issue_type, 'codex')
        return self.assign_to_agent(agent, issue_data)
    
    def classify_issue(self, issue_data):
        title = issue_data.get('title', '').lower()
        body = issue_data.get('body', '').lower()
        
        if any(word in title + body for word in ['security', 'vulnerability', 'cve']):
            return 'security'
        elif any(word in title + body for word in ['performance', 'optimize', 'speed']):
            return 'performance'
        elif any(word in title + body for word in ['architecture', 'design']):
            return 'architecture'
        elif any(word in title + body for word in ['refactor', 'restructure', 'reorganize']):
            return 'refactoring'
        elif any(word in title + body for word in ['quality', 'lint', 'documentation']):
            return 'quality'
        elif any(word in title + body for word in ['aws', 'cloud', 'infrastructure', 'deployment']):
            return 'cloud'
        elif any(word in title + body for word in ['build', 'tooling', 'development', 'workflow', 'ci']):
            return 'development'
        else:
            return 'feature'
    
    def assign_to_agent(self, agent, issue_data):
        agent_file = Path(f'.ai/{agent}/tasks.json')
        tasks = []
        if agent_file.exists():
            tasks = json.loads(agent_file.read_text())
        tasks.append(issue_data)
        agent_file.write_text(json.dumps(tasks, indent=2))
        return agent