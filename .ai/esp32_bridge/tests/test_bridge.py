"""Hardware-free tests for the packaged ESP32 WebSocket MCP bridge."""
from __future__ import annotations

import asyncio
import json

import mcp_server


class FakeWebSocket:
    def __init__(self) -> None:
        self.messages: list[str] = []

    async def send(self, message: str) -> None:
        self.messages.append(message)


def exchange(request: object) -> dict:
    socket = FakeWebSocket()
    asyncio.run(
        mcp_server.VirtualLoRaAgent().handle_mcp_message(
            socket, json.dumps(request)
        )
    )
    assert len(socket.messages) == 1
    return json.loads(socket.messages[0])


def test_declared_environment_imports_runtime_dependency() -> None:
    assert mcp_server.websockets.__version__ == "17.1"


def test_initialize_and_list_all_tools() -> None:
    initialized = exchange(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
        }
    )
    assert initialized["result"]["protocolVersion"] == "2024-11-05"

    listed = exchange(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    )
    assert {tool["name"] for tool in listed["result"]["tools"]} == {
        "cc1101_configure",
        "a2a_transmit",
    }


def test_legacy_rag_method_remains_available() -> None:
    response = exchange(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "rag_query",
            "params": {"region": "eu868", "frequency": 868100000},
        }
    )
    assert response["result"]["method"] == "rag_config"


def test_notifications_do_not_emit_responses() -> None:
    socket = FakeWebSocket()
    asyncio.run(
        mcp_server.VirtualLoRaAgent().handle_mcp_message(
            socket,
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        )
    )
    assert socket.messages == []


def test_oversized_and_invalid_utf8_messages_are_rejected() -> None:
    for message, code in (
        (b"x" * (mcp_server.MAX_MESSAGE_BYTES + 1), -32600),
        (b"\xff", -32700),
        ("x" * (mcp_server.MAX_MESSAGE_BYTES + 1), -32600),
    ):
        socket = FakeWebSocket()
        asyncio.run(mcp_server.VirtualLoRaAgent().handle_mcp_message(socket, message))
        assert json.loads(socket.messages[0])["error"]["code"] == code


def test_transmit_payload_limit_is_utf8_bytes() -> None:
    accepted = exchange(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "a2a_transmit", "arguments": {"payload": "é" * 2048}},
        }
    )
    assert "error" not in accepted
    rejected = exchange(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "a2a_transmit", "arguments": {"payload": "é" * 2049}},
        }
    )
    assert rejected["result"]["isError"] is True


def test_packaged_entrypoint_starts_serve_coroutine(monkeypatch) -> None:
    observed: dict[str, object] = {}

    async def fake_serve() -> None:
        observed["served"] = True

    monkeypatch.setattr(mcp_server, "serve", fake_serve)
    # Exercise the entrypoint without opening a socket.
    real_run = asyncio.runners.run
    monkeypatch.setattr(mcp_server.asyncio, "run", real_run)

    mcp_server.main()
    assert observed == {"served": True}
