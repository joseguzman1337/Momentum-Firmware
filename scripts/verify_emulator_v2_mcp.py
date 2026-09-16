#!/usr/bin/env python3
"""Black-box MCP health gate for the canonical Emulator v2 integration."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "emulator_v2_mcp" / "flipper_mcp_server.py"
FULL_SPEC_FIELDS = {"firmware", "output", "max_instructions", "live_control", "sd_tree", "oracle_snapshot", "internal_flash_image", "virtual_usb"}


def audit_full_spec(spec_path: Path) -> tuple[dict, list[str]]:
    spec = json.loads(spec_path.read_text())
    errors = [f"missing full-spec field: {key}" for key in sorted(FULL_SPEC_FIELDS - set(spec))]
    if spec.get("max_instructions") != 250_000_000:
        errors.append("max_instructions must be exactly 250000000")
    for flag in ("live_control", "virtual_usb"):
        if spec.get(flag) is not True: errors.append(f"{flag} must be true")
    for key in ("firmware", "sd_tree", "oracle_snapshot"):
        if spec.get(key) and not Path(spec[key]).expanduser().resolve().exists(): errors.append(f"{key} does not exist")
    if spec.get("internal_flash_image") and not Path(spec["internal_flash_image"]).expanduser().resolve().parent.exists():
        errors.append("internal_flash_image parent does not exist")
    return spec, errors


def verify_internal_flash_persistence(path: Path) -> dict:
    """Prove the sanitized atomic image can be reopened without data drift."""
    first_bytes = path.read_bytes()
    first = json.loads(first_bytes)
    errors = []
    if first.get("schema") != 1: errors.append("unsupported internal flash schema")
    if first.get("sanitized") is not True: errors.append("internal flash is not declared sanitized")
    decoded = {}
    for name, value in first.get("files", {}).items():
        if not name.startswith("/int/") or ".." in Path(name).parts: errors.append(f"unsafe internal path: {name}")
        try: decoded[name] = base64.b64decode(value, validate=True)
        except Exception: errors.append(f"invalid base64 for {name}")
    second = json.loads(path.read_bytes())
    if first != second: errors.append("internal flash changed while reopening")
    return {"valid": not errors, "errors": errors, "schema": first.get("schema"), "sanitized": first.get("sanitized"), "files": len(decoded), "bytes": sum(map(len, decoded.values())), "sha256": hashlib.sha256(first_bytes).hexdigest(), "reopen_equal": first == second}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / ".ai/logs/qemu-fw/mcp-stdio-health.json",
    )
    args = parser.parse_args()
    spec, spec_errors = audit_full_spec(args.spec.resolve())
    spec_data = json.loads(args.spec.read_text())
    process = subprocess.Popen(
        [sys.executable, str(SERVER)],
        cwd=SERVER.parent,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    assert process.stdin and process.stdout
    request_id = 0

    def request(method: str, params: dict | None = None) -> dict:
        nonlocal request_id
        request_id += 1
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            payload["params"] = params
        process.stdin.write(json.dumps(payload) + "\n")
        process.stdin.flush()
        line = process.stdout.readline()
        if not line:
            raise RuntimeError("MCP server closed stdout")
        return json.loads(line)

    result: dict = {"schema": 2, "server": str(SERVER), "spec": str(args.spec.resolve()), "full_spec_errors": spec_errors}
    try:
        initialized = request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "momentum-health", "version": "1"}})
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        process.stdin.flush()
        tools = request("tools/list")["result"]["tools"]
        names = {tool["name"] for tool in tools}
        capabilities = request("tools/call", {"name": "emulator_capabilities", "arguments": {}})
        validated = request("tools/call", {"name": "emulator_validate_spec", "arguments": {"spec_path": str(args.spec.resolve())}})
        validated_data = json.loads(validated["result"]["content"][0]["text"])
        snapshot = request("tools/call", {"name": "emulator_snapshot_metadata", "arguments": {"path": str(Path(spec["oracle_snapshot"]).expanduser().resolve())}}) if not spec_errors else None
        snapshot_data = json.loads(snapshot["result"]["content"][0]["text"]) if snapshot and not snapshot["result"].get("isError") else None
        if spec_errors:
            raise RuntimeError("full spec rejected: " + "; ".join(spec_errors))
        started = request("tools/call", {"name": "emulator_run", "arguments": {"spec_path": str(args.spec.resolve())}})
        run = json.loads(started["result"]["content"][0]["text"])
        run_id = run["run_id"]
        input_result = None
        screen_result = None
        usb_result = None
        storage_result = None
        storage_read_result = None
        fixture_manifest = json.loads((Path(spec["sd_tree"]).expanduser().resolve() / "manifest.json").read_text())
        fixture_entry = next((entry for entry in fixture_manifest.get("files", []) if entry.get("path")), None)
        fixture_virtual_path = "/ext/" + fixture_entry["path"].lstrip("/") if fixture_entry else None
        deadline = time.time() + 60
        while time.time() < deadline:
            state_response = request("tools/call", {"name": "emulator_run_status", "arguments": {"run_id": run_id}})
            state = json.loads(state_response["result"]["content"][0]["text"])
            if input_result is None and state["phase"] == "running":
                candidate = request("tools/call", {"name": "emulator_input", "arguments": {"run_id": run_id, "button": "OK", "action": "PRESS"}})
                if not candidate["result"].get("isError"):
                    input_result = candidate
            if screen_result is None and state["phase"] == "running":
                candidate = request("tools/call", {"name": "emulator_screen", "arguments": {"run_id": run_id, "format": "raw_hex"}})
                if not candidate["result"].get("isError"):
                    screen_result = candidate
            if usb_result is None and state["phase"] == "running":
                candidate = request("tools/call", {"name": "emulator_usb_rpc", "arguments": {"run_id": run_id, "operation": "ping"}})
                if not candidate["result"].get("isError"):
                    usb_result = json.loads(candidate["result"]["content"][0]["text"])
            if storage_result is None and state["phase"] == "running":
                candidate = request("tools/call", {"name": "emulator_storage_list", "arguments": {"run_id": run_id, "path": "/ext"}})
                if not candidate["result"].get("isError"): storage_result = json.loads(candidate["result"]["content"][0]["text"])
            if storage_read_result is None and fixture_virtual_path and state["phase"] == "running":
                candidate = request("tools/call", {"name": "emulator_storage_read", "arguments": {"run_id": run_id, "path": fixture_virtual_path}})
                if not candidate["result"].get("isError"): storage_read_result = json.loads(candidate["result"]["content"][0]["text"])
            if state["phase"] in {"succeeded", "failed"}:
                break
            time.sleep(0.05)
        report_response = request("tools/call", {"name": "emulator_report", "arguments": {"run_id": run_id}})
        report = json.loads(report_response["result"]["content"][0]["text"])
        events_response = request("tools/call", {"name": "emulator_events", "arguments": {"run_id": run_id, "limit": 1000}})
        events = json.loads(events_response["result"]["content"][0]["text"])
        internal_flash = Path(spec["internal_flash_image"]).expanduser().resolve()
        internal_persistence = verify_internal_flash_persistence(internal_flash) if internal_flash.is_file() else {"valid": False, "errors": ["image missing"]}
        storage_sha_ok = bool(storage_read_result and fixture_entry and storage_read_result.get("size") == fixture_entry.get("size"))
        report_contract = {
            "oracle_valid": bool(report.get("oracle_snapshot", {}).get("valid")),
            "sd_fixture_valid": bool(report.get("sd_fixture", {}).get("valid")),
            "virtual_usb_enabled": bool(report.get("virtual_usb", {}).get("enabled")),
            "internal_flash_path_matches": Path(report.get("virtual_usb", {}).get("persistent_internal_flash", "")).resolve() == internal_flash,
            "internal_flash_exists": internal_flash.is_file(),
            "internal_flash_reopens": internal_persistence["valid"] and internal_persistence["reopen_equal"],
        }
        result.update(
            passed=(
                not spec_errors
                and initialized["result"]["protocolVersion"] == "2024-11-05"
                and len(names) == 15
                and not capabilities["result"].get("isError", False)
                and validated_data["valid"]
                and bool(snapshot_data and snapshot_data["valid"])
                and state["phase"] == "succeeded"
                and report["returncode"] == 0
                and any(
                    report["command"][index:index + 2] == ["--max-instructions", "250000000"]
                    for index in range(len(report["command"]) - 1)
                )
                and bool(input_result)
                and bool(screen_result)
                and bool(usb_result and usb_result.get("canonical_native_transport") and usb_result.get("success") and usb_result.get("messages"))
                and bool(storage_result)
                and storage_sha_ok
                and events["total"] > 0
                and all(report_contract.values())
            ),
            protocol_version=initialized["result"]["protocolVersion"],
            tool_count=len(names),
            tools=sorted(names),
            run_id=run_id,
            run_state=state,
            native_report=str(Path(state["output"]) / "report.json"),
            native_returncode=report["returncode"],
            firmware=report["firmware"],
            engine=report["engine"],
            event_count=events["total"],
            live_input_verified=bool(input_result),
            native_screen_verified=bool(screen_result),
            native_usb_rpc_verified=bool(usb_result),
            native_storage_verified=bool(storage_result),
            native_storage_read_verified=storage_sha_ok,
            snapshot_metadata=snapshot_data,
            report_contract=report_contract,
            internal_flash_image=str(internal_flash),
            internal_flash_persistence=internal_persistence,
        )
    finally:
        process.terminate()
        _, stderr = process.communicate(timeout=5)
        result["server_stderr"] = stderr[-4000:]
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
