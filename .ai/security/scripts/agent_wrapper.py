#!/usr/bin/env python3
"""
Agent Internet Access Wrapper
Wraps agent internet requests with security validation
"""

import json
import sys
import subprocess
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from internet_validator import InternetAccessValidator

class AgentInternetWrapper:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.validator = InternetAccessValidator()
        
    def make_request(self, url: str, method: str = "GET", **kwargs):
        """Make validated internet request"""
        # Validate domain and method
        domain_ok = self.validator.validate_domain(url, self.agent_name)
        method_ok = self.validator.validate_http_method(method)
        
        if not (domain_ok and method_ok):
            self.validator.log_request(self.agent_name, url, method, False)
            raise PermissionError(f"Internet access denied for {url}")
        
        # Log successful request
        self.validator.log_request(self.agent_name, url, method, True)
        
        # Make actual request using curl (safer than requests library)
        if method.upper() == "GET":
            cmd = ["curl", "-s", "-L", "--max-time", "30", url]
        elif method.upper() == "HEAD":
            cmd = ["curl", "-s", "-I", "--max-time", "30", url]
        else:
            raise ValueError(f"HTTP method {method} not allowed")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Request to {url} timed out")
        except Exception as e:
            raise RuntimeError(f"Request failed: {e}")

def create_agent_wrapper(agent_name: str):
    """Factory function to create agent-specific wrapper"""
    return AgentInternetWrapper(agent_name)

# Agent-specific wrappers
codex_internet = create_agent_wrapper("codex")
claude_internet = create_agent_wrapper("claude")
gemini_internet = create_agent_wrapper("gemini")
amazonq_internet = create_agent_wrapper("amazonq")
warp_internet = create_agent_wrapper("warp")
kiro_internet = create_agent_wrapper("kiro")
deepseek_internet = create_agent_wrapper("deepseek")
jules_internet = create_agent_wrapper("jules")