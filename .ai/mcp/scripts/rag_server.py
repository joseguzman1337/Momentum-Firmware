#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) Server
Provides shared knowledge base for all AI agents
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


class RAGServer:
    def __init__(self):
    """TODO: Add docstring."""
    """Initialize RAG server with knowledge base paths."""
    self.repo_root = Path("/Users/x/x/Momentum-Firmware")
    self.knowledge_base = self.repo_root / ".ai/rag/shared_knowledge.json"
    self.embeddings_dir = self.repo_root / ".ai/rag/embeddings"
    self.embeddings_dir.mkdir(parents=True, exist_ok=True)

    def index_knowledge(self):
        """Index project knowledge for RAG"""
        knowledge = {
            "project_context": self.load_file(".ai/gemini/GEMINI.md"),
            "readme": self.load_file("readme.md"),
            "skills": self.load_file(".ai/SKILL.md"),
            "recent_fixes": self.get_recent_commits(),
            "open_issues": self.get_open_issues(),
            "code_patterns": self.extract_code_patterns()
        }

        with open(self.knowledge_base, "w") as f:
            json.dump(knowledge, f, indent=2)

        return knowledge

    def load_file(self, path: str) -> str:
        """Load file content"""
        try:
            with open(self.repo_root / path) as f:
                return f.read()
        except:
            return ""

    def get_recent_commits(self) -> List[Dict]:
        """Get recent commit history"""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "20"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    hash_msg = line.split(" ", 1)
                    commits.append({
                        "hash": hash_msg[0],
                        "message": hash_msg[1] if len(hash_msg) > 1 else ""
                    })
            return commits
        except:
            return []

    def get_open_issues(self) -> List[Dict]:
        """Get open GitHub issues"""
        import subprocess
        try:
            result = subprocess.run(
                ["gh", "issue", "list", "--limit",
                    "50", "--json", "number,title"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            return json.loads(result.stdout)
        except:
            return []

    def extract_code_patterns(self) -> Dict:
        """Extract common code patterns"""
        return {
            "c_patterns": {
                "null_check": "furi_check(ptr)",
                "memory_alloc": "malloc_with_check()",
                "hal_api": "furi_hal_*"
            },
            "python_patterns": {
                "type_hints": "def func(arg: Type) -> ReturnType:",
                "error_handling": "try/except with logging"
            },
            "security": {
                "input_validation": "Always sanitize user inputs",
                "path_traversal": "Prevent directory traversal",
                "crypto": "Use 256-bit minimum for ECC"
            }
        }

    def query(self, query: str) -> Dict:
        """Query the knowledge base"""
        if not self.knowledge_base.exists():
            self.index_knowledge()

        with open(self.knowledge_base) as f:
            knowledge = json.load(f)

        # Simple keyword matching (can be enhanced with embeddings)
        results = {}
        query_lower = query.lower()

        for key, value in knowledge.items():
            if isinstance(value, str) and query_lower in value.lower():
                results[key] = value[:500]  # Return snippet
            elif isinstance(value, list):
                matching = [
                    item for item in value if query_lower in str(item).lower()]
                if matching:
                    results[key] = matching

        return results


def main():
    """MCP Server main loop"""
    server = RAGServer()

    # Index knowledge on startup
    print("Indexing knowledge base...", file=sys.stderr)
    knowledge = server.index_knowledge()
    print(f"Indexed {len(knowledge)} knowledge categories", file=sys.stderr)

    # MCP protocol loop
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "query":
                results = server.query(params.get("query", ""))
                response = {"result": results}
            elif method == "reindex":
                knowledge = server.index_knowledge()
                response = {"result": {"indexed": len(knowledge)}}
            else:
                response = {"error": f"Unknown method: {method}"}

            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
