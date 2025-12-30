#!/usr/bin/env python3
"""
MCP Validation Script for Momentum Firmware
Tests MCP server functionality and configuration
"""

import json
import subprocess
import sys
import os
from pathlib import Path
import time

class MCPValidator:
    def __init__(self):
        self.project_root = Path("/Users/x/x/Momentum-Firmware")
        self.config_path = Path.home() / ".codex" / "config.toml"
        self.results = []
        
    def log(self, message, status="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        self.results.append({"timestamp": timestamp, "status": status, "message": message})
    
    def check_dependencies(self):
        """Check required dependencies"""
        self.log("Checking dependencies...", "INFO")
        
        # Check Python
        try:
            result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"Python: {result.stdout.strip()}", "PASS")
            else:
                self.log("Python not found", "FAIL")
        except Exception as e:
            self.log(f"Python check failed: {e}", "FAIL")
        
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"Node.js: {result.stdout.strip()}", "PASS")
            else:
                self.log("Node.js not found", "FAIL")
        except Exception as e:
            self.log(f"Node.js check failed: {e}", "FAIL")
        
        # Check Codex CLI
        try:
            result = subprocess.run(["codex", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"Codex CLI: {result.stdout.strip()}", "PASS")
            else:
                self.log("Codex CLI not found", "WARN")
        except Exception as e:
            self.log(f"Codex CLI not installed: {e}", "WARN")
    
    def check_configuration(self):
        """Check MCP configuration files"""
        self.log("Checking configuration files...", "INFO")
        
        # Check unified config
        unified_config = self.project_root / ".codex" / "mcp_unified.toml"
        if unified_config.exists():
            self.log(f"Unified MCP config found: {unified_config}", "PASS")
        else:
            self.log(f"Unified MCP config missing: {unified_config}", "FAIL")
        
        # Check Codex config
        if self.config_path.exists():
            self.log(f"Codex config found: {self.config_path}", "PASS")
        else:
            self.log(f"Codex config missing: {self.config_path}", "WARN")
        
        # Check agent directories
        ai_dir = self.project_root / ".ai"
        if ai_dir.exists():
            self.log(f"AI directory found: {ai_dir}", "PASS")
            
            # Check individual agent directories
            agents = ["codex", "claude", "jules", "gemini", "deepseek", "warp", "amazonq", "kiro"]
            for agent in agents:
                agent_dir = ai_dir / agent
                if agent_dir.exists():
                    self.log(f"Agent directory found: {agent}", "PASS")
                else:
                    self.log(f"Agent directory missing: {agent}", "WARN")
        else:
            self.log(f"AI directory missing: {ai_dir}", "FAIL")
    
    def check_mcp_servers(self):
        """Check MCP server implementations"""
        self.log("Checking MCP server implementations...", "INFO")
        
        # Check internal MCP servers
        servers = [
            ".ai/rag/server.py",
            ".ai/workflows/message_bus.py", 
            ".ai/tools/flipper_mcp.py"
        ]
        
        for server in servers:
            server_path = self.project_root / server
            if server_path.exists():
                # Check if executable
                if os.access(server_path, os.X_OK):
                    self.log(f"MCP server ready: {server}", "PASS")
                else:
                    self.log(f"MCP server not executable: {server}", "WARN")
            else:
                self.log(f"MCP server missing: {server}", "FAIL")
    
    def test_mcp_server(self, server_path):
        """Test individual MCP server"""
        try:
            # Send tools/list request
            test_request = {"method": "tools/list", "params": {}}
            
            process = subprocess.Popen(
                [sys.executable, str(server_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(
                input=json.dumps(test_request) + "\n",
                timeout=10
            )
            
            if process.returncode == 0:
                try:
                    response = json.loads(stdout.strip())
                    if "tools" in response:
                        self.log(f"Server test passed: {server_path.name}", "PASS")
                        return True
                    else:
                        self.log(f"Server test failed - no tools: {server_path.name}", "FAIL")
                        return False
                except json.JSONDecodeError:
                    self.log(f"Server test failed - invalid JSON: {server_path.name}", "FAIL")
                    return False
            else:
                self.log(f"Server test failed - exit code {process.returncode}: {server_path.name}", "FAIL")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"Server test timeout: {server_path.name}", "FAIL")
            return False
        except Exception as e:
            self.log(f"Server test error: {server_path.name} - {e}", "FAIL")
            return False
    
    def check_external_packages(self):
        """Check external MCP packages"""
        self.log("Checking external MCP packages...", "INFO")
        
        packages = [
            "@upstash/context7-mcp",
            "@modelcontextprotocol/server-github",
            "@playwright/mcp"
        ]
        
        for package in packages:
            try:
                result = subprocess.run(
                    ["npm", "list", "-g", package],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.log(f"Package installed: {package}", "PASS")
                else:
                    self.log(f"Package missing: {package}", "WARN")
            except Exception as e:
                self.log(f"Package check failed: {package} - {e}", "FAIL")
    
    def check_environment_variables(self):
        """Check required environment variables"""
        self.log("Checking environment variables...", "INFO")
        
        env_vars = [
            "GITHUB_TOKEN",
            "OPENAI_API_KEY", 
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY"
        ]
        
        for var in env_vars:
            if os.getenv(var):
                self.log(f"Environment variable set: {var}", "PASS")
            else:
                self.log(f"Environment variable missing: {var}", "WARN")
    
    def check_log_directories(self):
        """Check log directories exist"""
        self.log("Checking log directories...", "INFO")
        
        log_dirs = [
            "logs/codex",
            "logs/claude", 
            "logs/jules",
            "logs/gemini",
            "logs/deepseek",
            "logs/warp",
            "logs/amazonq",
            "logs/kiro"
        ]
        
        for log_dir in log_dirs:
            log_path = self.project_root / log_dir
            if log_path.exists():
                self.log(f"Log directory exists: {log_dir}", "PASS")
            else:
                self.log(f"Log directory missing: {log_dir}", "WARN")
                # Create directory
                try:
                    log_path.mkdir(parents=True, exist_ok=True)
                    self.log(f"Created log directory: {log_dir}", "INFO")
                except Exception as e:
                    self.log(f"Failed to create log directory: {log_dir} - {e}", "FAIL")
    
    def run_validation(self):
        """Run complete validation"""
        self.log("Starting MCP validation for Momentum Firmware", "INFO")
        self.log("=" * 60, "INFO")
        
        # Run all checks
        self.check_dependencies()
        self.check_configuration()
        self.check_mcp_servers()
        self.check_external_packages()
        self.check_environment_variables()
        self.check_log_directories()
        
        # Test MCP servers
        self.log("Testing MCP servers...", "INFO")
        servers_to_test = [
            self.project_root / ".ai/rag/server.py",
            self.project_root / ".ai/workflows/message_bus.py",
            self.project_root / ".ai/tools/flipper_mcp.py"
        ]
        
        for server in servers_to_test:
            if server.exists():
                self.test_mcp_server(server)
        
        # Summary
        self.log("=" * 60, "INFO")
        self.log("Validation Summary", "INFO")
        
        pass_count = len([r for r in self.results if r["status"] == "PASS"])
        warn_count = len([r for r in self.results if r["status"] == "WARN"])
        fail_count = len([r for r in self.results if r["status"] == "FAIL"])
        
        self.log(f"PASS: {pass_count}, WARN: {warn_count}, FAIL: {fail_count}", "INFO")
        
        if fail_count == 0:
            self.log("✅ MCP setup validation completed successfully!", "PASS")
            return True
        else:
            self.log("❌ MCP setup has issues that need attention", "FAIL")
            return False
    
    def save_report(self):
        """Save validation report"""
        report_path = self.project_root / "logs" / "mcp_validation.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": self.results
            }, f, indent=2)
        
        self.log(f"Validation report saved: {report_path}", "INFO")

def main():
    validator = MCPValidator()
    success = validator.run_validation()
    validator.save_report()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()