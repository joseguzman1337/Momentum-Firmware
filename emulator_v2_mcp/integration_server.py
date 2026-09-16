#!/usr/bin/env python3
"""MCP bridge for both Emulator v2 backends.

The process never opens physical hardware.  Protocol output is written only to
stdout; diagnostics belong on stderr.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import select
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("MOMENTUM_FIRMWARE_ROOT", HERE.parent)).expanduser().resolve()
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

try:  # Repository checkout: avoid collision with the root ``tools`` namespace.
    from emulator_v2_mcp.tools.flipper_emulator.emulator import FlipperZeroEmulator  # noqa: E402
except ModuleNotFoundError:  # Installed wheel exposes this package as ``tools``.
    from tools.flipper_emulator.emulator import FlipperZeroEmulator  # noqa: E402

RUNNER = REPO / "tools/flipper_emulator/runner.py"
CAPABILITIES = REPO / "tools/flipper_emulator/capabilities.json"
SCHEMA = REPO / "tools/flipper_emulator/spec.schema.json"
DEFAULT_ENGINE = REPO / ".tools/flipper-fap-studio/runtime/stm32/source/target/release/stm32-emulator"
DEFAULT_SVD = REPO / ".ai/logs/qemu-fw/fap-studio-profile/STM32WB55_CM4.svd"


def _json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _schema_errors(value: Any, schema: dict[str, Any]) -> list[str]:
    """Validate the object subset used by MCP input schemas and run specs."""
    if not isinstance(value, dict):
        return ["value must be an object"]
    errors: list[str] = []
    properties = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        errors.extend(f"unexpected property: {key}" for key in value.keys() - properties.keys())
    errors.extend(f"missing required property: {key}" for key in schema.get("required", []) if key not in value)
    python_types = {"string": str, "integer": int, "boolean": bool, "array": list, "object": dict}
    for key, item in value.items():
        rule = properties.get(key)
        if not rule:
            continue
        expected = python_types.get(rule.get("type"))
        if expected and (not isinstance(item, expected) or expected is int and isinstance(item, bool)):
            errors.append(f"{key} must be {rule['type']}")
            continue
        if "enum" in rule and item not in rule["enum"]:
            errors.append(f"{key} is not an allowed value")
        if isinstance(item, int) and not isinstance(item, bool):
            if "minimum" in rule and item < rule["minimum"]: errors.append(f"{key} is below minimum")
            if "maximum" in rule and item > rule["maximum"]: errors.append(f"{key} is above maximum")
    return errors


class EmulatorV2MCPServer:
    protocol_version = "2024-11-05"

    def __init__(self) -> None:
        self.emu = FlipperZeroEmulator(sd_card_path=str(HERE / "sd_card"))
        self._runs: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.tools = self._tools()

    @staticmethod
    def _tools() -> list[dict[str, Any]]:
        obj = {"type": "object", "additionalProperties": False}
        return [
            {"name": "emulator_capabilities", "description": "Return modeled, replayed, and explicitly unmodeled Emulator v2 surfaces.", "inputSchema": {**obj, "properties": {}}},
            {"name": "emulator_validate_spec", "description": "Validate an Emulator v2 run specification and all referenced artifacts without running it.", "inputSchema": {**obj, "properties": {"spec_path": {"type": "string"}}, "required": ["spec_path"]}},
            {"name": "emulator_validate_artifact", "description": "Inspect a local regular file (size and SHA-256) without changing it.", "inputSchema": {**obj, "properties": {"path": {"type": "string"}}, "required": ["path"]}},
            {"name": "emulator_run", "description": "Start the native STM32WB55 Emulator v2 runner in the background.", "inputSchema": {**obj, "properties": {"spec_path": {"type": "string"}}, "required": ["spec_path"]}},
            {"name": "emulator_run_status", "description": "Return authoritative process state for a run id.", "inputSchema": {**obj, "properties": {"run_id": {"type": "string"}}, "required": ["run_id"]}},
            {"name": "emulator_events", "description": "Read deterministic events.jsonl for a run, with offset and limit.", "inputSchema": {**obj, "properties": {"run_id": {"type": "string"}, "offset": {"type": "integer", "minimum": 0, "default": 0}, "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100}}, "required": ["run_id"]}},
            {"name": "emulator_report", "description": "Read the runner report.json for a completed or active run.", "inputSchema": {**obj, "properties": {"run_id": {"type": "string"}}, "required": ["run_id"]}},
            {"name": "emulator_snapshot_metadata", "description": "Validate and summarize a sanitized oracle snapshot; never opens hardware.", "inputSchema": {**obj, "properties": {"path": {"type": "string"}}, "required": ["path"]}},
            {"name": "emulator_screen", "description": "Read the latest canonical native FLIPPER_FRAME for run_id.", "inputSchema": {**obj, "properties": {"run_id": {"type": "string"}, "format": {"type": "string", "enum": ["ascii", "raw_hex", "base64_pbm"], "default": "ascii"}}, "required": ["run_id"]}},
            {"name": "emulator_input", "description": "Send BUTTON input through the canonical native run control FIFO. The run spec must set live_control=true.", "inputSchema": {**obj, "properties": {"run_id": {"type": "string"}, "button": {"type": "string", "enum": ["UP", "DOWN", "LEFT", "RIGHT", "OK", "BACK"]}, "action": {"type": "string", "enum": ["PRESS", "RELEASE"]}}, "required": ["run_id", "button", "action"]}},
            {"name": "emulator_storage_list", "description": "List staged native SD fixture storage for run_id.", "inputSchema": {**obj, "properties": {"run_id": {"type": "string"}, "path": {"type": "string", "default": "/ext"}}, "required": ["run_id"]}},
            {"name": "emulator_storage_read", "description": "Read a staged native SD fixture file for run_id.", "inputSchema": {**obj, "properties": {"run_id": {"type": "string"}, "path": {"type": "string"}}, "required": ["run_id", "path"]}},
            {"name": "model_storage_list", "description": "List the explicitly process-local Python model storage (not a native firmware run).", "inputSchema": {**obj, "properties": {"path": {"type": "string", "default": "/ext"}}}},
            {"name": "model_storage_read", "description": "Read the explicitly process-local Python model storage (not a native firmware run).", "inputSchema": {**obj, "properties": {"path": {"type": "string"}}, "required": ["path"]}},
            {"name": "emulator_usb_rpc", "description": "Invoke the canonical run's PTY-backed virtual USB protobuf RPC. The run spec must set virtual_usb=true.", "inputSchema": {**obj, "properties": {"run_id": {"type": "string"}, "operation": {"type": "string", "enum": ["ping", "device_info", "screen", "storage_list", "storage_read"]}, "path": {"type": "string", "default": "/int"}}, "required": ["run_id", "operation"]}},
        ]

    @staticmethod
    def _resolve(path: str) -> Path:
        return Path(path).expanduser().resolve()

    def _load_spec(self, raw: str) -> tuple[Path, dict[str, Any]]:
        path = self._resolve(raw)
        if not path.is_file():
            raise ValueError(f"spec not found: {path}")
        spec = json.loads(path.read_text())
        missing = {"firmware", "output"} - set(spec)
        if missing:
            raise ValueError("missing required keys: " + ", ".join(sorted(missing)))
        if not isinstance(spec.get("max_instructions", 20_000_000), int):
            raise ValueError("max_instructions must be an integer")
        inputs = spec.get("inputs", [])
        if not isinstance(inputs, list) or any(e.get("action") not in {"PRESS", "RELEASE"} or not e.get("button") for e in inputs):
            raise ValueError("each input needs button and PRESS or RELEASE action")
        return path, spec

    def _validate_spec(self, raw: str) -> dict[str, Any]:
        path = self._resolve(raw)
        if not path.is_file():
            return {"valid": False, "errors": [f"spec not found: {path}"], "spec": str(path), "schema": str(SCHEMA)}
        try:
            spec = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            return {"valid": False, "errors": [str(exc)], "spec": str(path), "schema": str(SCHEMA)}
        published_schema = json.loads(SCHEMA.read_text())
        errors = _schema_errors(spec, published_schema)
        artifacts: dict[str, Any] = {}
        spec = dict(spec)
        spec.setdefault("engine", str(DEFAULT_ENGINE))
        spec.setdefault("svd", str(DEFAULT_SVD))
        for key in ("firmware", "engine", "svd", "sd_image", "internal_flash_image", "c2_firmware", "device_info_model"):
            if spec.get(key):
                if not isinstance(spec[key], str):
                    continue
                item = self._resolve(spec[key])
                artifacts[key] = {"path": str(item), "exists": item.is_file()}
                if item.is_file():
                    artifacts[key].update(size=item.stat().st_size, sha256=_sha256(item))
        required = ("firmware", "engine", "svd")
        errors.extend(f"{key} is not a regular file" for key in required if not artifacts.get(key, {}).get("exists", False))
        for key in ("sd_image", "c2_firmware", "device_info_model"):
            if spec.get(key) and not artifacts.get(key, {}).get("exists", False): errors.append(f"{key} is not a regular file")
        for key in ("oracle_snapshot", "sd_tree"):
            if spec.get(key):
                item = self._resolve(spec[key]) if isinstance(spec[key], str) else Path("/")
                valid_directory = item.is_dir() and (item / "manifest.json").is_file()
                artifacts[key] = {"path": str(item), "exists": valid_directory}
                if not valid_directory: errors.append(f"{key} is not a directory with manifest.json")
        valid = not errors
        output = str(self._resolve(spec["output"])) if isinstance(spec.get("output"), str) else None
        return {"valid": valid, "errors": errors, "spec": str(path), "schema": str(SCHEMA), "output": output, "artifacts": artifacts, "virtual_usb": bool(spec.get("virtual_usb")), "inputs": len(spec.get("inputs", [])) if isinstance(spec.get("inputs", []), list) else 0}

    def _run_worker(self, run_id: str, spec: Path) -> None:
        state = self._runs[run_id]
        state["phase"] = "running"
        state["started_at"] = time.time()
        try:
            proc = subprocess.Popen([sys.executable, "-m", "tools.flipper_emulator.runner", str(spec)], cwd=str(REPO), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            state["pid"] = proc.pid
            stdout, stderr = proc.communicate()
            state.update(returncode=proc.returncode, stdout=stdout, stderr=stderr, phase="succeeded" if proc.returncode == 0 else "failed")
        except Exception as exc:
            state.update(returncode=None, stderr=str(exc), phase="failed")
        finally:
            state["finished_at"] = time.time()

    def _state(self, run_id: str) -> dict[str, Any]:
        try:
            state = self._runs[run_id]
        except KeyError as exc:
            raise ValueError(f"unknown run_id: {run_id}") from exc
        result = {k: v for k, v in state.items() if k not in {"stdout", "stderr"}} | {"stdout_tail": state.get("stdout", "")[-4000:], "stderr_tail": state.get("stderr", "")[-4000:]}
        runtime = Path(state["output"]) / "runtime-status.json"
        if runtime.is_file():
            try: result["native_runtime"] = json.loads(runtime.read_text())
            except (OSError, json.JSONDecodeError): pass
        return result

    def _run(self, run_id: str) -> dict[str, Any]:
        if run_id not in self._runs: raise ValueError(f"unknown run_id: {run_id}")
        return self._runs[run_id]

    def _native_frame(self, run_id: str) -> bytes:
        state = self._run(run_id)
        path = Path(state["output"]) / "events.jsonl"
        if not path.is_file(): raise ValueError("native events are not available yet")
        frames = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        frames = [event for event in frames if event.get("kind") == "frame"]
        if not frames: raise ValueError("native run emitted no FLIPPER_FRAME event")
        try: data = bytes.fromhex(frames[-1]["payload"])
        except (KeyError, ValueError) as exc: raise ValueError("latest native frame is malformed") from exc
        if len(data) != 1024: raise ValueError(f"native frame has {len(data)} bytes, expected 1024")
        return data

    @staticmethod
    def _render_frame(data: bytes) -> str:
        rows = []
        for y in range(64):
            rows.append("".join("#" if data[(y // 8) * 128 + x] & (1 << (y % 8)) else " " for x in range(128)))
        return "\n".join(rows)

    @staticmethod
    def _varint(value: int) -> bytes:
        out = bytearray()
        while True:
            byte = value & 0x7f; value >>= 7
            out.append(byte | (0x80 if value else 0))
            if not value: return bytes(out)

    @classmethod
    def _field(cls, number: int, value: bytes) -> bytes:
        return cls._varint(number << 3 | 2) + cls._varint(len(value)) + value

    @classmethod
    def _rpc_request(cls, command_id: int, tag: int, payload: bytes = b"") -> bytes:
        body = cls._varint(1 << 3) + cls._varint(command_id) + cls._field(tag, payload)
        return cls._varint(len(body)) + body

    @staticmethod
    def _read_varint(data: bytes, offset: int = 0) -> tuple[int, int]:
        value = 0
        for shift in range(0, 70, 7):
            if offset >= len(data): raise EOFError("incomplete varint")
            byte = data[offset]; offset += 1; value |= (byte & 0x7f) << shift
            if not byte & 0x80: return value, offset
        raise ValueError("oversized varint")

    @classmethod
    def _protobuf_fields(cls, data: bytes) -> list[tuple[int, int, int | bytes]]:
        result, offset = [], 0
        while offset < len(data):
            tag, offset = cls._read_varint(data, offset); number, wire = tag >> 3, tag & 7
            if wire == 0: value, offset = cls._read_varint(data, offset)
            elif wire == 2:
                size, offset = cls._read_varint(data, offset); value = data[offset:offset + size]
                if len(value) != size: raise EOFError("incomplete length-delimited field")
                offset += size
            else: raise ValueError(f"unsupported protobuf wire type {wire}")
            result.append((number, wire, value))
        return result

    @classmethod
    def _decode_rpc_messages(cls, stream: bytes, operation: str) -> list[dict[str, Any]]:
        messages, offset = [], 0
        while offset < len(stream):
            size, body_offset = cls._read_varint(stream, offset)
            body = stream[body_offset:body_offset + size]
            if len(body) != size: break
            offset = body_offset + size
            fields = cls._protobuf_fields(body)
            command_id = int(next((v for n, w, v in fields if n == 1 and w == 0), 0))
            status = int(next((v for n, w, v in fields if n == 2 and w == 0), 0))
            has_next = bool(next((v for n, w, v in fields if n == 3 and w == 0), 0))
            content = next(((n, v) for n, w, v in fields if w == 2 and n not in {1, 2, 3}), None)
            content_tag, payload = (content if content else (None, b""))
            assert isinstance(payload, bytes)
            decoded: dict[str, Any] = {}
            if operation == "device_info" and content_tag == 33:
                nested = cls._protobuf_fields(payload)
                key = next((v for n, w, v in nested if n == 1 and w == 2), b"")
                value = next((v for n, w, v in nested if n == 2 and w == 2), b"")
                decoded = {"key": bytes(key).decode("utf-8", "replace"), "value": bytes(value).decode("utf-8", "replace")}
            elif operation == "screen" and content_tag == 22:
                frame = next((v for n, w, v in cls._protobuf_fields(payload) if n == 1 and w == 2), b"")
                decoded = {"framebuffer_bytes": len(frame), "framebuffer_base64": base64.b64encode(bytes(frame)).decode()}
            elif operation == "storage_read" and content_tag == 10:
                decoded = {"content_base64": base64.b64encode(payload).decode()}
            elif operation == "storage_list" and content_tag == 8:
                decoded = {"entry_payload_bytes": len(payload)}
            messages.append({"command_id": command_id, "status": status, "has_next": has_next, "content_tag": content_tag, "payload_bytes": len(payload), "success": status == 0, "decoded": decoded})
        return messages

    def _native_rpc(self, run_id: str, operation: str, path: str) -> dict[str, Any]:
        state = self._run(run_id)
        runtime_path = Path(state["output"]) / "runtime-status.json"
        if not runtime_path.is_file(): raise ValueError("native runtime status is not available")
        runtime = json.loads(runtime_path.read_text())
        endpoint = runtime.get("virtual_usb_endpoint")
        if not endpoint: raise ValueError("native run was not started with virtual_usb=true")
        if runtime.get("phase") != "running": raise ValueError("native virtual USB endpoint is no longer live")
        tags = {"ping": 5, "device_info": 32, "screen": 20, "storage_list": 7, "storage_read": 9}
        nested = self._field(1, path.encode()) if operation.startswith("storage_") else b""
        fd = os.open(endpoint, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        try:
            if not state.get("rpc_started"):
                os.write(fd, b"start_rpc_session\r")
                deadline = time.time() + 1
                handshake = b""
                while time.time() < deadline:
                    ready, _, _ = select.select([fd], [], [], .05)
                    if ready: handshake += os.read(fd, 4096)
                    if b"start_rpc_session" in handshake: break
                if b"start_rpc_session" not in handshake: raise ValueError("virtual USB RPC handshake timed out")
                state["rpc_started"] = True
            os.write(fd, self._rpc_request(1, tags[operation], nested))
            deadline = time.time() + 1
            response = bytearray()
            while time.time() < deadline:
                ready, _, _ = select.select([fd], [], [], .05)
                if ready:
                    response.extend(os.read(fd, 65536))
                    if response: time.sleep(.02)
                elif response: break
            if not response: raise ValueError("virtual USB RPC response timed out")
            messages = self._decode_rpc_messages(bytes(response), operation)
            if not messages: raise ValueError("virtual USB RPC response contained no complete PB.Main message")
            return {"run_id": run_id, "operation": operation, "endpoint": endpoint, "response_bytes": len(response), "response_base64": base64.b64encode(response).decode(), "messages": messages, "success": all(item["success"] for item in messages), "canonical_native_transport": True}
        finally:
            os.close(fd)

    def _native_storage_path(self, run_id: str, virtual_path: str) -> Path:
        state = self._run(run_id)
        if not virtual_path.startswith("/ext") or (len(virtual_path) > 4 and virtual_path[4] != "/"):
            raise ValueError("native staged storage exposes /ext only")
        root = (Path(state["output"]) / "stage" / "sd-root").resolve()
        if not root.is_dir(): raise ValueError("run has no safely inspectable staged SD fixture tree")
        relative = virtual_path[4:].lstrip("/")
        if ".." in Path(relative).parts: raise ValueError("path traversal rejected")
        target = (root / relative).resolve()
        if target != root and root not in target.parents: raise ValueError("path escapes staged SD fixture")
        if target.is_symlink(): raise ValueError("symlink storage entries are not exposed")
        return target

    def call_tool(self, name: str, args: dict[str, Any]) -> Any:
        if name == "emulator_capabilities":
            data = json.loads(CAPABILITIES.read_text())
            data["mcp"] = {"tools": [tool["name"] for tool in self.tools], "hardware_access": False, "backends": ["native-runner", "interactive-v2"]}
            data["mcp"]["disclosure"] = "CPU2/radio and electrical behavior are not executed; no RF transmission tools are exposed."
            return data
        if name == "emulator_validate_spec":
            return self._validate_spec(args["spec_path"])
        if name == "emulator_validate_artifact":
            path = self._resolve(args["path"])
            if not path.is_file() or path.is_symlink():
                raise ValueError("artifact must be a non-symlink regular file")
            return {"path": str(path), "size": path.stat().st_size, "sha256": _sha256(path)}
        if name == "emulator_run":
            spec_path, spec = self._load_spec(args["spec_path"])
            validation = self._validate_spec(str(spec_path))
            if not validation["valid"]:
                raise ValueError("invalid spec: " + "; ".join(validation["errors"]))
            run_id = uuid.uuid4().hex
            self._runs[run_id] = {"run_id": run_id, "phase": "starting", "spec": str(spec_path), "output": str(self._resolve(spec["output"])), "created_at": time.time()}
            threading.Thread(target=self._run_worker, args=(run_id, spec_path), daemon=True).start()
            return self._state(run_id)
        if name == "emulator_run_status":
            return self._state(args["run_id"])
        if name in {"emulator_events", "emulator_report"}:
            state = self._runs.get(args["run_id"])
            if not state:
                raise ValueError(f"unknown run_id: {args['run_id']}")
            filename = "events.jsonl" if name == "emulator_events" else "report.json"
            path = Path(state["output"]) / filename
            if not path.is_file():
                return {"available": False, "phase": state["phase"], "path": str(path)}
            if name == "emulator_report":
                return json.loads(path.read_text())
            lines = path.read_text().splitlines()
            offset, limit = int(args.get("offset", 0)), int(args.get("limit", 100))
            return {"available": True, "offset": offset, "next_offset": min(len(lines), offset + limit), "total": len(lines), "events": [json.loads(x) for x in lines[offset:offset + limit]]}
        if name == "emulator_snapshot_metadata":
            path = self._resolve(args["path"])
            code = (
                "import json; from pathlib import Path; "
                "from tools.flipper_emulator.runner import validate_oracle_snapshot; "
                f"print(json.dumps(validate_oracle_snapshot(Path({str(path)!r}))))"
            )
            completed = subprocess.run([sys.executable, "-c", code], cwd=REPO, text=True, capture_output=True, check=True)
            return json.loads(completed.stdout)
        if name == "emulator_screen":
            fmt = args.get("format", "ascii")
            if not args.get("run_id"): raise ValueError("run_id is required for canonical native screen access")
            data = self._native_frame(args["run_id"])
            if fmt == "raw_hex": return data.hex()
            if fmt == "base64_pbm":
                packed = bytearray()
                for y in range(64):
                    for start in range(0, 128, 8):
                        value = 0
                        for bit in range(8):
                            if data[(y // 8) * 128 + start + bit] & (1 << (y % 8)): value |= 1 << (7 - bit)
                        packed.append(value)
                return base64.b64encode(b"P4\n128 64\n" + packed).decode()
            return self._render_frame(data)
        if name == "emulator_input":
            run_id, button, action = args.get("run_id"), args.get("button"), args.get("action")
            if not run_id or not button or action not in {"PRESS", "RELEASE"}: raise ValueError("run_id, button, and PRESS or RELEASE action are required")
            state = self._run(run_id)
            _, spec = self._load_spec(state["spec"])
            if not spec.get("live_control"): raise ValueError("native run was not started with live_control=true")
            fifo = Path(state["output"]) / "control.fifo"
            if state.get("phase") not in {"starting", "running"} or not fifo.exists(): raise ValueError("native run is not accepting live input")
            deadline = time.time() + 1
            while True:
                try:
                    fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
                    try: os.write(fd, f"BUTTON {button} {action}\n".encode())
                    finally: os.close(fd)
                    break
                except OSError as exc:
                    if time.time() >= deadline: raise ValueError(f"native control channel unavailable: {exc}") from exc
                    time.sleep(.02)
            return {"run_id": run_id, "accepted": True, "button": button, "action": action, "transport": "control.fifo"}
        if name == "emulator_storage_list":
            path = args.get("path", "/ext")
            if not args.get("run_id"): raise ValueError("run_id is required for canonical native storage access")
            target = self._native_storage_path(args["run_id"], path)
            if not target.is_dir(): raise ValueError(f"not a directory: {path}")
            return [{"name": item.name, "directory": item.is_dir(), "size": item.stat().st_size if item.is_file() else None} for item in sorted(target.iterdir()) if not item.is_symlink()]
        if name == "emulator_storage_read":
            path = args["path"]
            if not args.get("run_id"): raise ValueError("run_id is required for canonical native storage access")
            target = self._native_storage_path(args["run_id"], path)
            if not target.is_file(): raise ValueError(f"file not found: {path}")
            data = target.read_bytes()
            return {"path": path, "size": len(data), "utf8": data.decode("utf-8", "replace"), "base64": base64.b64encode(data).decode()}
        if name == "model_storage_list":
            return self.emu.rpc.handle_storage_list(args.get("path", "/ext"))
        if name == "model_storage_read":
            path = args["path"]
            data = self.emu.rpc.handle_storage_read(path)
            if data is None: raise ValueError(f"file not found: {path}")
            return {"path": path, "size": len(data), "utf8": data.decode("utf-8", "replace"), "base64": base64.b64encode(data).decode()}
        if name == "emulator_usb_rpc":
            return self._native_rpc(args["run_id"], args["operation"], args.get("path", "/int"))
        raise ValueError(f"unknown tool: {name}")

    def handle_request(self, request: Any) -> dict[str, Any] | None:
        if not isinstance(request, dict): return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}}
        method, msg_id = request.get("method"), request.get("id")
        if method == "notifications/initialized" or (method and method.startswith("notifications/")): return None
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"protocolVersion": self.protocol_version, "capabilities": {"tools": {"listChanged": False}, "resources": {"subscribe": False, "listChanged": False}}, "serverInfo": {"name": "momentum-emulator-v2", "version": "2.1.0"}}}
        if method == "ping": return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
        if method == "tools/list": return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": self.tools}}
        if method == "resources/list": return {"jsonrpc": "2.0", "id": msg_id, "result": {"resources": [{"uri": "flipper://capabilities", "name": "Emulator capabilities", "mimeType": "application/json"}, {"uri": "flipper://state", "name": "Interactive emulator state", "mimeType": "application/json"}]}}
        if method == "resources/read":
            uri = request.get("params", {}).get("uri")
            if uri == "flipper://capabilities":
                data = self.call_tool("emulator_capabilities", {})
            elif uri == "flipper://state":
                data = self.emu.get_state_summary()
                data["profile"]["name"] = "emulator-v2"
            else:
                data = None
            if data is None: return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32602, "message": "unknown resource"}}
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"contents": [{"uri": uri, "mimeType": "application/json", "text": _json(data)}]}}
        if method == "tools/call":
            params = request.get("params", {})
            try:
                name, arguments = params.get("name", ""), params.get("arguments") or {}
                definition = next((tool for tool in self.tools if tool["name"] == name), None)
                if definition is None: raise ValueError(f"unknown tool: {name}")
                errors = _schema_errors(arguments, definition["inputSchema"])
                if errors: raise ValueError("invalid arguments: " + "; ".join(errors))
                result = self.call_tool(name, arguments)
                return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": result if isinstance(result, str) else _json(result)}]}}
            except Exception as exc:
                return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": str(exc)}], "isError": True}}
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

    def run_stdio(self) -> None:
        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = self.handle_request(request)
            except json.JSONDecodeError as exc:
                response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error", "data": str(exc)}}
            except Exception as exc:
                response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(exc)}}
            if response is not None:
                sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
                sys.stdout.flush()


def main() -> None:
    EmulatorV2MCPServer().run_stdio()


if __name__ == "__main__":
    main()
