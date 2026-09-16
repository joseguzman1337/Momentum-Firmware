#!/usr/bin/env python3
"""Run every repository MCP test/health gate without accessing hardware."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(argv: list[str], *, cwd: Path = ROOT) -> None:
    print("+", " ".join(argv), flush=True)
    subprocess.run(argv, cwd=cwd, check=True)


def main() -> int:
    run(
        [
            sys.executable,
            "-m",
            "unittest",
            "-q",
            "tests.test_mcp_stdio",
            "tests.test_mcp_health_audit",
            "tests.test_esp_install_gate",
            "tests.test_flipper_recovery",
            "tests.test_official_marketplace_sync",
        ]
    )
    run(
        [sys.executable, "-m", "unittest", "-q", "test.test_hardening"],
        cwd=ROOT / ".ai/mcp/servers/esp_mcp",
    )
    run([sys.executable, ".ai/mcp/servers/strawberry_mcp/test_strawberry_mcp.py", "-q"])
    run(
        [
            "uv",
            "run",
            "--no-project",
            "--with",
            "pytest",
            "--with",
            "websockets",
            "pytest",
            "-q",
            "tests/test_mcp_bridges.py",
            "tests/test_strawberry_mcp.py",
        ]
    )
    run(["uv", "run", "--directory", ".ai/esp32_bridge", "pytest", "-q"])
    run(["cargo", "test", "--quiet", "--manifest-path", ".ai/esp_mcp_orchestrator/Cargo.toml"])
    run(
        [
            "cargo",
            "clippy",
            "--quiet",
            "--manifest-path",
            ".ai/esp_mcp_orchestrator/Cargo.toml",
            "--all-targets",
            "--",
            "-D",
            "warnings",
        ]
    )
    run(
        [
            sys.executable,
            ".ai/mcp/scripts/mcp_health_audit.py",
            "--health",
            "--timeout",
            "10",
            "--output",
            "/tmp/momentum-mcp-health.json",
        ]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
