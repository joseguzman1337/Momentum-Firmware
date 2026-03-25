#!/usr/bin/env python3
"""
Internet Access Security Validator
Monitors and validates internet requests from AI agents
"""

import json
import logging
import re
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional

class InternetAccessValidator:
    def __init__(self, config_path: str = ".ai/configs/internet_access.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
    def _load_config(self) -> Dict:
        """Load internet access configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load config: {e}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for security monitoring"""
        logger = logging.getLogger('internet_access_validator')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        handler = logging.FileHandler(log_dir / "internet_access_security.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def validate_domain(self, url: str, agent_name: str) -> bool:
        """Validate if domain is allowed for the agent"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check blocked domains first
            blocked = self.config.get("domain_allowlist", {}).get("blocked_domains", [])
            if any(blocked_domain in domain for blocked_domain in blocked):
                self.logger.warning(f"Blocked domain access: {domain} by {agent_name}")
                return False
            
            # Check common dependencies preset
            common_deps = self._get_common_dependencies()
            if domain in common_deps:
                return True
            
            # Check additional domains
            additional = self.config.get("domain_allowlist", {}).get("additional_domains", [])
            if domain in additional:
                return True
            
            # Check agent-specific domains
            agent_config = self.config.get("agent_specific_config", {}).get(agent_name, {})
            agent_domains = agent_config.get("additional_domains", [])
            if domain in agent_domains:
                return True
            
            self.logger.warning(f"Domain not in allowlist: {domain} by {agent_name}")
            return False
            
        except Exception as e:
            self.logger.error(f"Domain validation error: {e}")
            return False
    
    def validate_http_method(self, method: str) -> bool:
        """Validate if HTTP method is allowed"""
        allowed_methods = self.config.get("http_methods", {}).get("allowed", ["GET", "HEAD", "OPTIONS"])
        return method.upper() in allowed_methods
    
    def check_prompt_injection(self, content: str) -> bool:
        """Basic prompt injection detection"""
        suspicious_patterns = [
            r"ignore\s+previous\s+instructions",
            r"system\s*:\s*you\s+are",
            r"curl\s+.*\|\s*sh",
            r"wget\s+.*\|\s*sh",
            r"rm\s+-rf",
            r"sudo\s+",
            r"exec\s*\(",
            r"eval\s*\(",
            r"__import__\s*\(",
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, content_lower):
                self.logger.critical(f"Potential prompt injection detected: {pattern}")
                return True
        
        return False
    
    def _get_common_dependencies(self) -> Set[str]:
        """Get common dependency domains"""
        return {
            "alpinelinux.org", "anaconda.com", "apache.org", "apt.llvm.org",
            "archlinux.org", "azure.com", "bitbucket.org", "bower.io",
            "centos.org", "cocoapods.org", "continuum.io", "cpan.org",
            "crates.io", "debian.org", "docker.com", "docker.io",
            "dot.net", "dotnet.microsoft.com", "eclipse.org", "fedoraproject.org",
            "gcr.io", "ghcr.io", "github.com", "githubusercontent.com",
            "gitlab.com", "golang.org", "google.com", "goproxy.io",
            "gradle.org", "hashicorp.com", "haskell.org", "hex.pm",
            "java.com", "java.net", "jcenter.bintray.com", "json-schema.org",
            "json.schemastore.org", "k8s.io", "launchpad.net", "maven.org",
            "mcr.microsoft.com", "metacpan.org", "microsoft.com", "nodejs.org",
            "npmjs.com", "npmjs.org", "nuget.org", "oracle.com",
            "packagecloud.io", "packages.microsoft.com", "packagist.org",
            "pkg.go.dev", "ppa.launchpad.net", "pub.dev", "pypa.io",
            "pypi.org", "pypi.python.org", "pythonhosted.org", "quay.io",
            "ruby-lang.org", "rubyforge.org", "rubygems.org", "rubyonrails.org",
            "rustup.rs", "rvm.io", "sourceforge.net", "spring.io",
            "swift.org", "ubuntu.com", "visualstudio.com", "yarnpkg.com"
        }
    
    def log_request(self, agent_name: str, url: str, method: str, allowed: bool):
        """Log internet access request"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "url": url,
            "method": method,
            "allowed": allowed,
            "domain": urllib.parse.urlparse(url).netloc
        }
        
        if allowed:
            self.logger.info(f"Internet access granted: {json.dumps(log_entry)}")
        else:
            self.logger.warning(f"Internet access denied: {json.dumps(log_entry)}")

def main():
    """Main function for testing"""
    validator = InternetAccessValidator()
    
    # Test cases
    test_cases = [
        ("codex", "https://github.com/joseguzman1337/Momentum-Firmware", "GET"),
        ("claude", "https://malware-site.com/evil", "GET"),
        ("amazonq", "https://docs.aws.amazon.com/cli/", "GET"),
        ("gemini", "https://googleapis.com/api/v1", "POST"),
    ]
    
    for agent, url, method in test_cases:
        domain_ok = validator.validate_domain(url, agent)
        method_ok = validator.validate_http_method(method)
        allowed = domain_ok and method_ok
        
        validator.log_request(agent, url, method, allowed)
        print(f"{agent}: {url} [{method}] -> {'ALLOWED' if allowed else 'DENIED'}")

if __name__ == "__main__":
    main()