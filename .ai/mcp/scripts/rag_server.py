#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) Server
Provides shared knowledge base for all AI agents
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List
from mcp_stdio import MCPStdioServer


class RAGServer:
    def __init__(self):
        """Initialize RAG server with workspace-relative knowledge paths."""
        self.repo_root = Path(os.environ.get("REPO_ROOT", Path(__file__).resolve().parents[3])).resolve()
        self.knowledge_base = Path(
            os.environ.get("KNOWLEDGE_BASE", self.repo_root / ".ai/rag/shared_knowledge.json")
        ).resolve()
        self.embeddings_dir = Path(
            os.environ.get("VECTOR_STORE", self.repo_root / ".ai/rag/embeddings")
        ).resolve()

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

        self.knowledge_base.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".knowledge.", dir=self.knowledge_base.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(knowledge, stream, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.knowledge_base)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

        return knowledge

    def load_file(self, path: str) -> str:
        """Load file content"""
        try:
            with open(self.repo_root / path) as f:
                return f.read()
        except (OSError, UnicodeError):
            return ""

    def get_recent_commits(self) -> List[Dict]:
        """Get recent commit history"""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "20"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=15,
                check=False,
            )
            if result.returncode != 0:
                return []
            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    hash_msg = line.split(" ", 1)
                    commits.append({
                        "hash": hash_msg[0],
                        "message": hash_msg[1] if len(hash_msg) > 1 else ""
                    })
            return commits
        except (OSError, subprocess.SubprocessError):
            return []

    def get_open_issues(self) -> List[Dict]:
        """Get open GitHub issues"""
        try:
            result = subprocess.run(
                ["gh", "issue", "list", "--limit",
                    "50", "--json", "number,title"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=20,
                check=False,
            )
            if result.returncode != 0 or len(result.stdout) > 1_000_000:
                return []
            return json.loads(result.stdout)
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
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
        if not isinstance(query, str) or not 1 <= len(query) <= 512:
            raise ValueError("query must contain 1..512 characters")
        if not self.knowledge_base.exists():
            raise FileNotFoundError("knowledge base is not indexed; call reindex_knowledge first")

        if self.knowledge_base.stat().st_size > 10 * 1024 * 1024:
            raise ValueError("knowledge base exceeds 10 MiB safety limit")
        with open(self.knowledge_base, encoding="utf-8") as f:
            knowledge = json.load(f)
        if not isinstance(knowledge, dict):
            raise ValueError("knowledge base root must be an object")

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


def create_mcp_server(server: RAGServer = None) -> MCPStdioServer:
    """Create the MCP server, including additive legacy tool aliases."""
    server = server or RAGServer()
    mcp = MCPStdioServer("momentum-rag")
    query_schema = {
        "type": "object",
        "properties": {"query": {"type": "string", "minLength": 1, "maxLength": 512}},
        "required": ["query"],
        "additionalProperties": False,
    }
    reindex_schema = {"type": "object", "properties": {}, "additionalProperties": False}
    query_handler = server.query
    reindex_handler = lambda: {"indexed": len(server.index_knowledge())}
    mcp.tool(
        "query_knowledge",
        "Search the repository-local knowledge base without modifying it.",
        query_schema,
        query_handler,
    )
    mcp.tool(
        "query",
        "Legacy alias for query_knowledge; searches without modifying the knowledge base.",
        query_schema,
        query_handler,
    )
    mcp.tool(
        "reindex_knowledge",
        "Rebuild the repository-local knowledge index (mutating).",
        reindex_schema,
        reindex_handler,
    )
    mcp.tool(
        "reindex",
        "Legacy alias for reindex_knowledge; rebuilds the repository-local knowledge index (mutating).",
        reindex_schema,
        reindex_handler,
    )
    return mcp


def main():
    """Run a standards-compliant MCP stdio server."""
    mcp = create_mcp_server()
    mcp.run()


if __name__ == "__main__":
    main()
