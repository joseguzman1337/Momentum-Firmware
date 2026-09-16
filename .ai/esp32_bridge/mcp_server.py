#!/usr/bin/env python3
"""MCP-compatible WebSocket bridge for the simulated LoRa cloud agent."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
import logging
import os
from typing import Any

import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MAX_MESSAGE_BYTES = 1024 * 1024
PROTOCOLS = ("2025-06-18", "2024-11-05")


class VirtualLoRaAgent:
    def __init__(self) -> None:
        self.connected_devices: dict[str, dict[str, Any]] = {}
        self.rag_database = {
            "eu868": {"frequencies": [868100000, 868300000, 868500000], "cc1101_config": {"FREQ2": 0x21, "FREQ1": 0x62, "FREQ0": 0x76, "MDMCFG4": 0x2D, "MDMCFG2": 0x30}},
            "us915": {"frequencies": list(range(902300000, 927500000, 200000)), "cc1101_config": {"FREQ2": 0x23, "FREQ1": 0x31, "FREQ0": 0x3B, "MDMCFG4": 0x2D, "MDMCFG2": 0x30}},
        }
        self.a2a_endpoints = {"ttn": "https://eu1.cloud.thethings.network/api/v3", "helium": "https://console.helium.com/api"}

    @staticmethod
    def tool_definitions() -> list[dict[str, Any]]:
        return [
            {"name": "cc1101_configure", "description": "Return validated CC1101 registers for a supported frequency.", "inputSchema": {"type": "object", "properties": {"region": {"type": "string", "enum": ["eu868", "us915"]}, "frequency": {"type": "integer", "minimum": 1}}, "required": ["frequency"], "additionalProperties": False}},
            {"name": "a2a_transmit", "description": "Simulate a bounded LoRaWAN A2A transmission without hardware I/O.", "inputSchema": {"type": "object", "properties": {"payload": {"type": "string", "maxLength": 4096}, "protocol": {"type": "string", "enum": ["lorawan"]}}, "required": ["payload"], "additionalProperties": False}},
        ]

    @staticmethod
    def _ok(request_id: Any, result: Any) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    async def handle_mcp_message(self, websocket: Any, message: str | bytes) -> None:
        if isinstance(message, bytes):
            if len(message) > MAX_MESSAGE_BYTES:
                await websocket.send(json.dumps(self._error(None, -32600, "Message too large")))
                return
            try:
                message = message.decode("utf-8")
            except UnicodeDecodeError:
                await websocket.send(json.dumps(self._error(None, -32700, "Parse error")))
                return
        if len(message.encode()) > MAX_MESSAGE_BYTES:
            await websocket.send(json.dumps(self._error(None, -32600, "Message too large")))
            return
        try:
            data = json.loads(message)
        except (json.JSONDecodeError, TypeError):
            await websocket.send(json.dumps(self._error(None, -32700, "Parse error")))
            return
        await self.handle_request(websocket, data)

    async def handle_request(self, websocket: Any, data: Any) -> None:
        if not isinstance(data, dict) or data.get("jsonrpc") != "2.0":
            await websocket.send(json.dumps(self._error(None, -32600, "Invalid Request")))
            return
        method, params, request_id = data.get("method"), data.get("params", {}), data.get("id")
        notification = "id" not in data
        if not isinstance(method, str) or not isinstance(params, dict):
            if not notification:
                await websocket.send(json.dumps(self._error(request_id, -32600, "Invalid Request")))
            return
        response = None
        if method == "initialize":
            info = params.get("clientInfo", {}) if isinstance(params.get("clientInfo", {}), dict) else {}
            self.connected_devices[f"{str(info.get('name', 'unknown'))[:128]}_{id(websocket)}"] = {"websocket": websocket, "client_info": info, "connected_at": datetime.now(timezone.utc)}
            requested = params.get("protocolVersion")
            response = self._ok(request_id, {"protocolVersion": requested if requested in PROTOCOLS else PROTOCOLS[0], "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "VirtualLoRa-CloudAgent", "version": "1.1.0"}})
        elif method == "ping":
            response = self._ok(request_id, {})
        elif method == "tools/list":
            response = self._ok(request_id, {"tools": self.tool_definitions()})
        elif method == "tools/call":
            response = await self._tools_call(params, request_id)
        elif method == "notifications/initialized":
            pass
        elif method == "rag_query":  # Legacy ESP32 method.
            try:
                response = self._ok(request_id, {"method": "rag_config", "params": self._configuration(params)})
            except ValueError as exc:
                response = self._error(request_id, -32602, str(exc))
        elif method == "a2a_transmit":  # Legacy ESP32 method.
            try:
                result = await self._a2a_transmit(params)
                response = None if notification else self._ok(request_id, result)
            except ValueError as exc:
                response = None if notification else self._error(request_id, -32602, str(exc))
        elif method == "lora_detected":
            logger.info("LoRa detected: %r", params)
            response = None if notification else self._ok(request_id, {})
        else:
            response = self._error(request_id, -32601, "Method not found")
        if response is not None and not notification:
            await websocket.send(json.dumps(response, separators=(",", ":")))

    async def _tools_call(self, params: dict[str, Any], request_id: Any) -> dict[str, Any]:
        name, arguments = params.get("name"), params.get("arguments", {})
        if not isinstance(name, str) or not isinstance(arguments, dict):
            return self._error(request_id, -32602, "Invalid tools/call parameters")
        try:
            if name == "cc1101_configure":
                result = self._configuration(arguments)
            elif name == "a2a_transmit":
                result = await self._a2a_transmit(arguments)
            else:
                return self._error(request_id, -32602, f"Unknown tool: {name}")
        except ValueError as exc:
            return self._ok(request_id, {"content": [{"type": "text", "text": str(exc)}], "isError": True})
        return self._ok(request_id, {"content": [{"type": "text", "text": json.dumps(result, separators=(",", ":"))}]})

    def _configuration(self, params: dict[str, Any]) -> dict[str, Any]:
        region, frequency = params.get("region", "eu868"), params.get("frequency")
        if isinstance(frequency, bool) or not isinstance(frequency, int):
            raise ValueError("frequency must be an integer")
        config = self.rag_database.get(region)
        if config is None or frequency not in config["frequencies"]:
            raise ValueError(f"Unsupported frequency {frequency} for region {region}")
        registers = config["cc1101_config"].copy()
        word = int((frequency * 65536) / 26000000)
        registers.update({"FREQ2": (word >> 16) & 0xFF, "FREQ1": (word >> 8) & 0xFF, "FREQ0": word & 0xFF})
        return {"cc1101_registers": registers, "frequency": frequency, "region": region}

    @staticmethod
    async def _a2a_transmit(params: dict[str, Any]) -> dict[str, Any]:
        payload, protocol = params.get("payload"), params.get("protocol", "lorawan")
        if not isinstance(payload, str) or len(payload.encode()) > 4096:
            raise ValueError("payload must be a UTF-8 string no larger than 4096 bytes")
        if protocol != "lorawan":
            raise ValueError("protocol must be lorawan")
        await asyncio.sleep(0)
        return {"status": "success", "payload": payload, "timestamp": datetime.now(timezone.utc).isoformat(), "simulated": True}


async def handle_client(websocket: Any, _path: Any = None) -> None:
    agent = VirtualLoRaAgent()
    try:
        async for message in websocket:
            await agent.handle_mcp_message(websocket, message)
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")


async def serve() -> None:
    host, port = os.environ.get("MCP_WEBSOCKET_HOST", "127.0.0.1"), int(os.environ.get("MCP_WEBSOCKET_PORT", "8765"))
    if not 1 <= port <= 65535:
        raise ValueError("MCP_WEBSOCKET_PORT must be between 1 and 65535")
    async with websockets.serve(handle_client, host, port, max_size=MAX_MESSAGE_BYTES):
        await asyncio.Future()


def main() -> None:
    asyncio.run(serve())


if __name__ == "__main__":
    main()
