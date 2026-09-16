#!/usr/bin/env python3
"""Inventory repository MCP registries and safely probe stdio handshakes.

The health probe sends only ``initialize`` and ``tools/list``. It never invokes
``tools/call`` and defaults to repository-local subprocess registrations.
"""

from __future__ import annotations

import argparse
import json
import os
import select
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    tomllib = None


DEFAULT_ROOT = Path(__file__).resolve().parents[3]
SKIP_PARTS = {".git", ".venv", "venv", "build", "dist", "node_modules", "target", "__pycache__"}
CONFIG_SUFFIXES = {".json", ".toml"}
PATH_SUFFIXES = {".py", ".js", ".cjs", ".mjs", ".ts", ".sh"}


@dataclass(frozen=True)
class Registration:
    source: str
    name: str
    transport: str
    command: str | None
    args: list[str]
    cwd: str | None
    enabled: bool
    env: dict[str, str] = field(repr=False, compare=False)


def _walk_configs(root: Path) -> list[Path]:
    configs: list[Path] = []
    for path in (root / ".ai").rglob("*"):
        if not path.is_file() or path.suffix not in CONFIG_SUFFIXES:
            continue
        if any(part in SKIP_PARTS for part in path.relative_to(root).parts):
            continue
        try:
            preview = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "mcpServers" in preview or "mcp_servers" in preview or '"mcp_server"' in preview:
            configs.append(path)
    return sorted(configs)


def _load(path: Path) -> dict[str, Any] | None:
    try:
        if path.suffix == ".json":
            value = json.loads(path.read_text(encoding="utf-8"))
        elif tomllib is not None:
            value = tomllib.loads(path.read_text(encoding="utf-8"))
        else:
            return None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def discover(root: Path) -> tuple[list[Registration], list[str]]:
    root = root.resolve()
    registrations: list[Registration] = []
    invalid_configs: list[str] = []
    for path in _walk_configs(root):
        data = _load(path)
        if data is None:
            invalid_configs.append(str(path.relative_to(root)))
            continue
        servers = data.get("mcpServers")
        if servers is None:
            servers = data.get("mcp_servers")
        if not isinstance(servers, dict):
            continue
        for name, spec in sorted(servers.items()):
            if not isinstance(spec, dict):
                continue
            command = spec.get("command")
            url = spec.get("url")
            args = spec.get("args", [])
            registrations.append(
                Registration(
                    source=str(path.relative_to(root)),
                    name=str(name),
                    transport="http" if isinstance(url, str) else "stdio",
                    command=command if isinstance(command, str) else None,
                    args=[str(item) for item in args] if isinstance(args, list) else [],
                    cwd=spec.get("cwd") if isinstance(spec.get("cwd"), str) else None,
                    enabled=spec.get("enabled", True) is not False,
                    env={
                        str(key): str(value)
                        for key, value in spec.get("env", {}).items()
                    }
                    if isinstance(spec.get("env"), dict)
                    else {},
                )
            )
    return registrations, invalid_configs


def discover_registry_references(root: Path) -> list[dict[str, Any]]:
    """Find secondary JSON pointers to MCP registry documents."""
    root = root.resolve()
    references: list[dict[str, Any]] = []
    for path in _walk_configs(root):
        data = _load(path)
        if data is None:
            continue

        def visit(value: object, key_path: str = "") -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    child_path = f"{key_path}.{key}" if key_path else key
                    if key == "mcp_server" and isinstance(item, str):
                        candidate = Path(os.path.expandvars(os.path.expanduser(item)))
                        resolved = candidate if candidate.is_absolute() else root / candidate
                        references.append(
                            {
                                "source": str(path.relative_to(root)),
                                "key": child_path,
                                "target": item,
                                "resolved": str(resolved.resolve()),
                                "exists": resolved.is_file(),
                            }
                        )
                    visit(item, child_path)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    visit(item, f"{key_path}[{index}]")

        visit(data)
    return references


def discover_implementations(root: Path, registrations: list[Registration]) -> list[dict[str, Any]]:
    """Inventory MCP server entrypoints, including packaged standalone servers."""
    root = root.resolve()
    registered_targets: set[Path] = set()
    for registration in registrations:
        cwd = _working_directory(root, registration)
        registered_targets.update(_local_targets(registration, cwd))
    implementations: list[dict[str, Any]] = []
    for path in (root / ".ai").rglob("*.py"):
        relative = path.relative_to(root)
        if any(part in SKIP_PARTS for part in relative.parts) or path.name.startswith("test_"):
            continue
        if path.name in {"mcp_stdio.py", "mcp_health_audit.py"}:
            continue
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        is_server = (
            ("MCPStdioServer(" in source and ".run()" in source)
            or ("FastMCP(" in source and ".run(" in source)
            or ("FastMCPCompat(" in source and ".run(" in source)
            or ("MCPServer(" in source and ".run(" in source)
            or "handle_mcp_message" in source
        )
        if not is_server:
            continue
        registered = path.resolve() in registered_targets
        project_dir = next(
            (
                parent
                for parent in (path.parent, *path.parents)
                if parent != root
                and parent.is_relative_to(root)
                and (parent / "pyproject.toml").is_file()
            ),
            None,
        )
        implementations.append(
            {
                "path": str(relative),
                "transport": "websocket" if "websockets.serve" in source else "stdio",
                "registered": registered,
                "packaged": project_dir is not None,
                "project": str(project_dir.relative_to(root)) if project_dir else None,
            }
        )
    return sorted(implementations, key=lambda item: item["path"])


def _working_directory(root: Path, registration: Registration) -> Path:
    if registration.cwd:
        candidate = Path(os.path.expandvars(os.path.expanduser(registration.cwd)))
        return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    return root


def _command_path(command: str | None, cwd: Path) -> str | None:
    if not command:
        return None
    expanded = Path(os.path.expandvars(os.path.expanduser(command)))
    if expanded.is_absolute() or "/" in command:
        candidate = expanded if expanded.is_absolute() else cwd / expanded
        return str(candidate.resolve()) if candidate.exists() else None
    return shutil.which(command)


def _local_targets(registration: Registration, cwd: Path) -> list[Path]:
    targets: list[Path] = []
    for arg in registration.args:
        expanded_text = os.path.expandvars(os.path.expanduser(arg))
        candidate = Path(expanded_text)
        is_path = (
            candidate.is_absolute()
            or arg.startswith((".", ".ai/"))
            or candidate.suffix.lower() in PATH_SUFFIXES
        )
        if is_path:
            targets.append((candidate if candidate.is_absolute() else cwd / candidate).resolve())
    return targets


def validate_registration(root: Path, registration: Registration) -> dict[str, Any]:
    root = root.resolve()
    cwd = _working_directory(root, registration)
    command_path = _command_path(registration.command, cwd)
    targets = _local_targets(registration, cwd)
    missing_targets = [str(path) for path in targets if not path.exists()]
    issues: list[str] = []
    if registration.transport == "stdio" and command_path is None:
        issues.append("command_not_found")
    if not cwd.is_dir():
        issues.append("cwd_not_found")
    if missing_targets:
        issues.append("local_target_not_found")
    return {
        "command_path": command_path,
        "cwd_path": str(cwd),
        "local_targets": [str(path) for path in targets],
        "missing_targets": missing_targets,
        "issues": issues,
        "path_valid": not issues,
    }


def _read_response(process: subprocess.Popen[str], request_id: int, deadline: float) -> dict[str, Any]:
    assert process.stdout is not None
    while time.monotonic() < deadline:
        remaining = max(0.0, deadline - time.monotonic())
        readable, _, _ = select.select([process.stdout], [], [], remaining)
        if not readable:
            break
        line = process.stdout.readline()
        if line == "":
            break
        try:
            response = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(response, dict) and response.get("id") == request_id:
            return response
    raise TimeoutError(f"no JSON-RPC response for request id {request_id}")


def _validate_tools(tools: object) -> tuple[list[str] | None, str | None]:
    """Validate the observable MCP tools/list contract for local tool servers."""
    if not isinstance(tools, list):
        return None, "tools must be an array"
    if not tools:
        return None, "tools must not be empty"
    names: list[str] = []
    for index, tool in enumerate(tools):
        if not isinstance(tool, dict):
            return None, f"tool {index} must be an object"
        name = tool.get("name")
        if not isinstance(name, str) or not name.strip():
            return None, f"tool {index} must have a non-empty string name"
        schema = tool.get("inputSchema")
        if not isinstance(schema, dict) or schema.get("type") != "object":
            return None, f"tool {name!r} must have an object inputSchema"
        if name in names:
            return None, f"duplicate tool name: {name}"
        names.append(name)
    return names, None


def probe(root: Path, registration: Registration, timeout: float) -> dict[str, Any]:
    root = root.resolve()
    validation = validate_registration(root, registration)
    if not registration.enabled:
        return {"status": "disabled", "tool_count": None}
    if registration.transport != "stdio":
        return {"status": "remote_not_probed", "tool_count": None}
    if not validation["path_valid"]:
        return {"status": "invalid_path", "tool_count": None}
    # Avoid package downloaders, containers and arbitrary system binaries. The
    # auditor's default contract is repository-local stdio processes only.
    local_targets = validation["local_targets"]
    if not local_targets or not all(Path(path).is_relative_to(root) for path in local_targets):
        return {"status": "external_not_probed", "tool_count": None}

    cwd = Path(validation["cwd_path"])
    env = os.environ.copy()
    env.update({key: os.path.expandvars(value) for key, value in registration.env.items()})
    process = subprocess.Popen(
        [registration.command or "", *registration.args],
        cwd=cwd,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        # Health never consumes server diagnostics. Discard them so a noisy
        # local server cannot fill a pipe and deadlock before tools/list.
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )
    try:
        assert process.stdin is not None
        deadline = time.monotonic() + timeout
        initialize = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        process.stdin.write(json.dumps(initialize) + "\n")
        process.stdin.flush()
        initialized = _read_response(process, 1, deadline)
        if "error" in initialized or "result" not in initialized:
            return {"status": "initialize_failed", "tool_count": None, "response": initialized}
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}) + "\n")
        process.stdin.flush()
        listed = _read_response(process, 2, deadline)
        tools = listed.get("result", {}).get("tools") if isinstance(listed.get("result"), dict) else None
        if "error" in listed:
            return {"status": "tools_list_failed", "tool_count": None, "response": listed}
        tool_names, validation_error = _validate_tools(tools)
        if validation_error is not None:
            return {"status": "tools_list_invalid", "tool_count": None, "error": validation_error}
        assert tool_names is not None
        return {"status": "healthy", "tool_count": len(tool_names), "tools": tool_names}
    except (OSError, TimeoutError, ValueError) as error:
        return {"status": "probe_failed", "tool_count": None, "error": f"{type(error).__name__}: {error}"}
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=1)
        for stream in (process.stdin, process.stdout):
            if stream is not None:
                stream.close()


def audit(root: Path, health: bool = False, timeout: float = 5.0) -> dict[str, Any]:
    root = root.resolve()
    registrations, invalid_configs = discover(root)
    registry_references = discover_registry_references(root)
    implementations = discover_implementations(root, registrations)
    rows = []
    for registration in registrations:
        row = {
            "source": registration.source,
            "name": registration.name,
            "transport": registration.transport,
            "command": registration.command,
            "args": registration.args,
            "cwd": registration.cwd,
            "enabled": registration.enabled,
            "env_keys": sorted(registration.env),
        }
        row["validation"] = validate_registration(root, registration)
        if health:
            row["health"] = probe(root, registration, timeout)
        rows.append(row)
    return {
        "root": str(root),
        "registry_count": len({row.source for row in registrations}),
        "registration_count": len(registrations),
        "invalid_configs": invalid_configs,
        "registry_references": registry_references,
        "implementation_inventory": implementations,
        "registrations": rows,
    }


def report_has_failures(report: dict[str, Any], health: bool = False) -> bool:
    if report.get("invalid_configs"):
        return True
    if any(not item.get("exists", False) for item in report.get("registry_references", [])):
        return True
    for item in report.get("registrations", []):
        if item.get("validation", {}).get("issues"):
            return True
        if health and item.get("health", {}).get("status") not in {
            "healthy",
            "disabled",
            "external_not_probed",
            "remote_not_probed",
        }:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--health", action="store_true", help="perform initialize + tools/list for local stdio entries")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.root.resolve(), health=args.health, timeout=max(0.1, args.timeout))
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 1 if report_has_failures(report, health=args.health) else 0


if __name__ == "__main__":
    raise SystemExit(main())
