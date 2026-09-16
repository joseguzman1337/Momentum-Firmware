"""Small dependency-free MCP stdio runtime for repository-local tools."""

from __future__ import annotations

import asyncio
import inspect
import json
import re
import sys
from collections.abc import Callable
from typing import Any, Optional, Union, get_args, get_origin, get_type_hints


MAX_REQUEST_BYTES = 1024 * 1024
_DRAIN_CHUNK_BYTES = 64 * 1024


def _read_bounded_line(stream) -> tuple[bytes, bool]:
    """Read one newline-delimited request without ever buffering an oversized line.

    ``BufferedReader.readline()`` without a size limit can allocate until an
    attacker eventually sends a newline.  Read one byte beyond the protocol
    limit, then drain the remainder in fixed-size chunks so the following
    request stays aligned.
    """
    raw_line = stream.readline(MAX_REQUEST_BYTES + 1)
    oversized = len(raw_line) > MAX_REQUEST_BYTES
    if oversized and not raw_line.endswith(b"\n"):
        while True:
            chunk = stream.readline(_DRAIN_CHUNK_BYTES)
            if not chunk or chunk.endswith(b"\n"):
                break
    return raw_line, oversized


def _validate_schema(value: object, schema: dict, path: str = "arguments") -> None:
    """Validate the small JSON Schema subset used by repository MCP tools."""
    if "anyOf" in schema:
        failures = []
        for alternative in schema["anyOf"]:
            try:
                _validate_schema(value, alternative, path)
                return
            except ValueError as error:
                failures.append(str(error))
        raise ValueError(f"{path} does not match any allowed schema: {'; '.join(failures)}")
    expected = schema.get("type")
    type_matches = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    if expected in type_matches and not type_matches[expected](value):
        raise ValueError(f"{path} must be {expected}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path} must be one of {schema['enum']!r}")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        missing = [name for name in schema.get("required", []) if name not in value]
        if missing:
            raise ValueError(f"{path} missing required field(s): {', '.join(missing)}")
        if schema.get("additionalProperties") is False:
            extras = sorted(set(value) - set(properties))
            if extras:
                raise ValueError(f"{path} has unknown field(s): {', '.join(extras)}")
        for name, item in value.items():
            if name in properties:
                _validate_schema(item, properties[name], f"{path}.{name}")
    elif isinstance(value, list) and isinstance(schema.get("items"), dict):
        for index, item in enumerate(value):
            _validate_schema(item, schema["items"], f"{path}[{index}]")
    elif isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ValueError(f"{path} is shorter than minLength")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise ValueError(f"{path} is longer than maxLength")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            raise ValueError(f"{path} does not match required pattern")
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise ValueError(f"{path} is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise ValueError(f"{path} is above maximum")


class MCPStdioServer:
    def __init__(self, name: str, version: str = "1.0.0") -> None:
        self.name = name
        self.version = version
        self._tools: dict[str, tuple[dict, Callable]] = {}

    def tool(self, name: str, description: str, input_schema: dict, handler: Callable) -> None:
        if name in self._tools:
            raise ValueError(f"duplicate MCP tool: {name}")
        self._tools[name] = (
            {"name": name, "description": description, "inputSchema": input_schema},
            handler,
        )

    def _result(self, request_id: object, result: object) -> dict:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _error(self, request_id: object, code: int, message: str) -> dict:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    def dispatch(self, request: object) -> Optional[dict]:
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            return self._error(request.get("id") if isinstance(request, dict) else None, -32600, "Invalid Request")
        request_id = request.get("id")
        method = request.get("method")
        if "id" not in request:  # notifications never receive responses
            return None
        if method == "initialize":
            return self._result(
                request_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": self.name, "version": self.version},
                },
            )
        if method == "ping":
            return self._result(request_id, {})
        if method == "tools/list":
            return self._result(request_id, {"tools": [item[0] for item in self._tools.values()]})
        if method != "tools/call":
            return self._error(request_id, -32601, "Method not found")

        params = request.get("params")
        if not isinstance(params, dict) or not isinstance(params.get("name"), str):
            return self._error(request_id, -32602, "Invalid tools/call parameters")
        entry = self._tools.get(params["name"])
        if entry is None:
            return self._error(request_id, -32602, f"Unknown tool: {params['name']}")
        arguments = params.get("arguments", {})
        if not isinstance(arguments, dict):
            return self._error(request_id, -32602, "Tool arguments must be an object")
        try:
            _validate_schema(arguments, entry[0]["inputSchema"])
            value = entry[1](**arguments)
            if inspect.isawaitable(value):
                value = asyncio.run(value)
            text = json.dumps(value, sort_keys=True, default=str)
            return self._result(request_id, {"content": [{"type": "text", "text": text}], "isError": False})
        except (TypeError, ValueError) as error:
            return self._error(request_id, -32602, str(error))
        except Exception as error:
            return self._result(
                request_id,
                {"content": [{"type": "text", "text": f"{type(error).__name__}: {error}"}], "isError": True},
            )

    def run(self) -> None:
        while True:
            raw_line, oversized = _read_bounded_line(sys.stdin.buffer)
            if not raw_line:
                break
            if oversized:
                response = self._error(None, -32600, "Request too large")
            else:
                try:
                    response = self.dispatch(json.loads(raw_line))
                except json.JSONDecodeError:
                    response = self._error(None, -32700, "Parse error")
            if response is not None:
                sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
                sys.stdout.flush()


class FastMCPCompat:
    """Minimal decorator-compatible fallback for local FastMCP servers."""

    def __init__(self, name: str) -> None:
        self.server = MCPStdioServer(name)

    def tool(self):
        def register(handler: Callable) -> Callable:
            signature = inspect.signature(handler)
            try:
                hints = get_type_hints(handler)
            except (NameError, TypeError):
                hints = {}
            properties = {}
            required = []
            for name, parameter in signature.parameters.items():
                annotation = hints.get(name, parameter.annotation)
                properties[name] = self._annotation_schema(annotation)
                if parameter.default is inspect.Parameter.empty:
                    required.append(name)
            self.server.tool(
                handler.__name__,
                inspect.getdoc(handler) or handler.__name__,
                {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False,
                },
                handler,
            )
            return handler

        return register

    @staticmethod
    def _annotation_schema(annotation: object) -> dict:
        """Translate common Python annotations into honest MCP input schemas."""
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Union or str(origin) == "<class 'types.UnionType'>":
            alternatives = [
                {"type": "null"} if item is type(None) else FastMCPCompat._annotation_schema(item)
                for item in args
            ]
            return {"anyOf": alternatives}
        if annotation is bool:
            return {"type": "boolean"}
        if annotation is int:
            return {"type": "integer"}
        if annotation is float:
            return {"type": "number"}
        if annotation in (dict, Any) or origin is dict:
            return {"type": "object"}
        if annotation is list or origin is list:
            schema = {"type": "array"}
            if args:
                schema["items"] = FastMCPCompat._annotation_schema(args[0])
            return schema
        return {"type": "string"}

    def run(self, **_kwargs) -> None:
        self.server.run()
