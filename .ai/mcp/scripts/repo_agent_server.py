#!/usr/bin/env python3
"""Portable read-only MCP backend for repository agent registrations."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from mcp_stdio import MCPStdioServer


ROOT = Path(os.environ.get("PROJECT_ROOT", Path(__file__).resolve().parents[3])).resolve()
ROLE = os.environ.get("MCP_AGENT_ROLE", "repository-agent")


def _run(argv: list[str], timeout: int = 30) -> dict:
    result = subprocess.run(
        argv,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-12000:],
    }


def get_repository_summary() -> dict:
    """Return branch, HEAD and scoped worktree status without modifying files."""
    branch = _run(["git", "branch", "--show-current"])
    head = _run(["git", "rev-parse", "HEAD"])
    status = _run(["git", "status", "--short"])
    return {
        "role": ROLE,
        "workspace": str(ROOT),
        "branch": branch["stdout"].strip(),
        "head": head["stdout"].strip(),
        "status": status["stdout"].splitlines(),
        "ok": branch["ok"] and head["ok"] and status["ok"],
    }


def validate_workspace() -> dict:
    """Run non-mutating repository validation checks."""
    diff = _run(["git", "diff", "--check"])
    return {"role": ROLE, "checks": {"git_diff_check": diff}, "ok": diff["ok"]}


def list_capabilities() -> dict:
    """Describe this conservative repository MCP surface."""
    return {
        "role": ROLE,
        "adapter_mode": "readonly_repository_status",
        "safety": "readonly",
        "configured_role_is_identity_only": True,
        "not_implemented": [
            "background monitoring",
            "code generation",
            "cloud-provider calls",
            "GitHub issue or pull-request mutation",
            "automatic merge",
        ],
        "capabilities": ["get_repository_summary", "validate_workspace", "list_capabilities"],
    }


def main() -> None:
    mcp = MCPStdioServer(f"momentum-{ROLE}")
    empty = {"type": "object", "properties": {}, "additionalProperties": False}
    mcp.tool("get_repository_summary", get_repository_summary.__doc__ or "", empty, get_repository_summary)
    mcp.tool("validate_workspace", validate_workspace.__doc__ or "", empty, validate_workspace)
    mcp.tool("list_capabilities", list_capabilities.__doc__ or "", empty, list_capabilities)
    mcp.run()


if __name__ == "__main__":
    main()
