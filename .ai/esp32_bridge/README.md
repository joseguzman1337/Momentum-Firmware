# ESP32 MCP bridge

This directory has an isolated, locked Python environment for the WebSocket
bridge. It does not contact or flash hardware.

Create or refresh the environment and run its protocol tests:

```sh
uv sync --project .ai/esp32_bridge --locked
uv run --directory .ai/esp32_bridge pytest
```

Start the bridge on loopback (the default):

```sh
uv run --directory .ai/esp32_bridge esp32-mcp-bridge
```

`MCP_WEBSOCKET_HOST` and `MCP_WEBSOCKET_PORT` may override the default
`127.0.0.1:8765` listener. Runtime and test versions are pinned in
`pyproject.toml` and resolved exactly in `uv.lock`.
