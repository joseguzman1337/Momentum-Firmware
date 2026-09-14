#!/usr/bin/env python3
"""Idempotent, explicit registration for the Momentum Flipper recovery MCP."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

try:
    import yaml
except ImportError:  # Registration must be run with the configured Sensei venv.
    yaml = None

NAME = "momentum-flipper-recovery"
PYTHON = "/Users/x/.hermes/sensei/.venv/bin/python"
ROOT = Path(__file__).resolve().parents[4]
MAIN = Path(__file__).resolve().with_name("main.py")
TARGETS = [Path("/Users/x/.hermes/config.yaml"), Path("/Users/x/.claude.json"), Path("/Users/x/.codex/config.toml")]


def desired(path: Path, original: str) -> str:
    if path.suffix == ".json":
        data = json.loads(original or "{}")
        servers = data.setdefault("mcpServers", {})
        if not isinstance(servers, dict):
            raise ValueError("top-level mcpServers must be a JSON object")
        if NAME in servers:
            return original
        servers[NAME] = {"command": PYTHON, "args": [str(MAIN)], "env": {"FLIPPER_RECOVERY_WORKSPACE": str(ROOT)}}
        # Correctness and top-level targeting take precedence over byte formatting.
        # dict insertion order still preserves unrelated key ordering.
        return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if path.suffix == ".toml":
        marker = f"[mcp_servers.{NAME}]"
        if marker in original:
            return original
        block = f'\n{marker}\ncommand = "{PYTHON}"\nargs = ["{MAIN}"]\n\n[mcp_servers.{NAME}.env]\nFLIPPER_RECOVERY_WORKSPACE = "{ROOT}"\n'
        return original.rstrip() + "\n" + block
    if yaml is None:
        raise RuntimeError(f"PyYAML is required; run this script with {PYTHON}")
    data = yaml.safe_load(original) if original.strip() else {}
    if not isinstance(data, dict):
        raise ValueError("Hermes YAML root must be a mapping")
    servers = data.setdefault("mcp_servers", {})
    if not isinstance(servers, dict):
        raise ValueError("top-level mcp_servers must be a YAML mapping")
    if NAME in servers:
        return original
    servers[NAME] = {"command": PYTHON, "args": [str(MAIN)], "env": {"FLIPPER_RECOVERY_WORKSPACE": str(ROOT)}}
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def plan(apply: bool) -> dict:
    results = []
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for path in TARGETS:
        original = path.read_text(encoding="utf-8") if path.exists() else ""
        updated = desired(path, original)
        changed = updated != original
        backup = None
        if apply and changed:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                backup = path.with_name(f"{path.name}.bak.{stamp}")
                shutil.copy2(path, backup)
            path.write_text(updated, encoding="utf-8")
        results.append({"path": str(path), "changed": changed, "applied": apply and changed, "backup": str(backup) if backup else None})
    return {"name": NAME, "apply": apply, "python": PYTHON, "main": str(MAIN), "workspace": str(ROOT), "targets": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(json.dumps(plan(args.apply), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
