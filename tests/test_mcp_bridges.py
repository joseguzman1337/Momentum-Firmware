"""Hardware-free protocol tests for repository MCP bridge implementations."""
from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeWebSocket:
    def __init__(self) -> None:
        self.messages: list[str] = []

    async def send(self, message: str) -> None:
        self.messages.append(message)


@pytest.fixture(scope="module")
def lora_module():
    return _load(REPO_ROOT / ".ai/esp32_bridge/mcp_server.py", "lora_mcp_bridge")


def _exchange(module, request: object) -> dict:
    socket = FakeWebSocket()
    asyncio.run(module.VirtualLoRaAgent().handle_mcp_message(socket, json.dumps(request)))
    assert len(socket.messages) == 1
    return json.loads(socket.messages[0])


def test_lora_bridge_standard_mcp_handshake_and_tool_list(lora_module) -> None:
    initialized = _exchange(lora_module, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "clientInfo": {"name": "test"}}})
    assert initialized["result"]["protocolVersion"] == "2024-11-05"
    assert initialized["result"]["capabilities"] == {"tools": {"listChanged": False}}
    listed = _exchange(lora_module, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    assert {tool["name"] for tool in listed["result"]["tools"]} == {"cc1101_configure", "a2a_transmit"}


def test_lora_bridge_tools_call_is_structured_and_hardware_free(lora_module) -> None:
    response = _exchange(lora_module, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "cc1101_configure", "arguments": {"region": "eu868", "frequency": 868100000}}})
    content = json.loads(response["result"]["content"][0]["text"])
    assert content["frequency"] == 868100000
    assert set(content["cc1101_registers"]) >= {"FREQ2", "FREQ1", "FREQ0"}


def test_lora_bridge_returns_protocol_errors(lora_module) -> None:
    assert _exchange(lora_module, {"jsonrpc": "2.0", "id": 4, "method": "missing"})["error"]["code"] == -32601
    socket = FakeWebSocket()
    asyncio.run(lora_module.VirtualLoRaAgent().handle_mcp_message(socket, "not json"))
    assert json.loads(socket.messages[0])["error"]["code"] == -32700


def test_vscode_bridge_stdio_tools_list_and_flash_plan() -> None:
    script = REPO_ROOT / ".ai/claude-vscode/scripts/mcp_bridge.py"
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "flash_firmware", "arguments": {"target": "f7"}}},
    ]
    process = subprocess.run(
        [sys.executable, str(script)],
        input="".join(json.dumps(item) + "\n" for item in requests),
        text=True,
        capture_output=True,
        timeout=10,
        check=True,
        cwd=REPO_ROOT,
    )
    responses = [json.loads(line) for line in process.stdout.splitlines()]
    assert {tool["name"] for tool in responses[1]["result"]["tools"]} == {"build_firmware", "flash_firmware", "coordinate_with_agents"}
    plan = json.loads(responses[2]["result"]["content"][0]["text"])
    assert plan["executed"] is False
    assert plan["confirmation_valid"] is False
    assert process.stderr == ""


def test_vscode_bridge_remains_planning_only_with_valid_confirmation() -> None:
    module = _load(
        REPO_ROOT / ".ai/claude-vscode/scripts/mcp_bridge.py",
        "claude_vscode_planning_gate",
    )
    plan = asyncio.run(
        module.ClaudeVSCodeMCPBridge().flash_firmware(
            {"target": "f7", "confirmation": module.FLASH_CONFIRMATION}
        )
    )
    assert plan["confirmation_valid"] is True
    assert plan["executed"] is False


@pytest.mark.parametrize("target", ["", "f0", 7])
def test_vscode_bridge_rejects_invalid_targets(target) -> None:
    module = _load(
        REPO_ROOT / ".ai/claude-vscode/scripts/mcp_bridge.py",
        f"claude_vscode_invalid_{target!s}",
    )
    with pytest.raises(ValueError, match="target must be"):
        asyncio.run(module.ClaudeVSCodeMCPBridge().build_firmware({"target": target}))


@pytest.mark.parametrize(
    ("agent", "message"),
    [("", "work"), ("a" * 129, "work"), ("agent", ""), ("agent", "m" * 16_385)],
)
def test_vscode_bridge_enforces_coordination_bounds(agent: str, message: str) -> None:
    module = _load(
        REPO_ROOT / ".ai/claude-vscode/scripts/mcp_bridge.py",
        f"claude_vscode_bounds_{len(agent)}_{len(message)}",
    )
    with pytest.raises(ValueError):
        asyncio.run(
            module.ClaudeVSCodeMCPBridge().coordinate_with_agents(
                {"agent": agent, "message": message}
            )
        )
