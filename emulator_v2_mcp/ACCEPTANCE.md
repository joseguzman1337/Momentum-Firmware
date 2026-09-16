# Emulator v2 MCP acceptance matrix

| Requirement | Authoritative evidence | Result |
|---|---|---|
| MCP stdio initialize | `mcp-full-feature-health.json`: protocol `2024-11-05` | PASS |
| Tool discovery | Same report: 15 unique tools | PASS |
| Representative `tools/call` | Full-feature run created through `emulator_run` | PASS |
| Real CPU1 engine | Engine SHA-256 `3e41b839...050b9c`, return code 0 | PASS |
| Current firmware | Firmware SHA-256 `ee6b41e9...197f2`, 250M instructions | PASS |
| Live native input | `live_input_verified: true`, run-bound FIFO | PASS |
| Native framebuffer | `native_screen_verified: true`, streamed `FLIPPER_FRAME` | PASS |
| SD fixture | 973 files / 27,048,600 bytes; native storage call PASS | PASS |
| Virtual USB/RPC | Run-bound PTY RPC ping PASS | PASS |
| Internal flash | Persistent isolated JSON image staged | PASS |
| Sanitized oracle | 15 fixtures, manifest valid, identifiers redacted | PASS |
| CPU2 reference boundary | Public C2 hash recorded, `executed: false`, replay 1.20.0 | PASS |
| Packaging | Wheel-style install and both console scripts import/launch | PASS |
| MCP registration | `.ai/mcp/emulator_v2_mcp.json` parses; global `codex mcp get flipper-emulator-v2` is enabled and points at the absolute repo entrypoint | PASS |
| Hardware isolation | No USB/serial enumeration or flash operation in server/runner | PASS |

Observed model boundaries are recorded, not hidden: USB uses a host PTY and is
not execution of the STM32 USB peripheral; CPU2/FUS/radio are deterministic
replay; and the latest full-feature run reported
`captured_framebuffer_match: false` while native frame streaming itself passed.
These facts limit emulator fidelity but do not break the verified MCP transport.

Evidence files:

- `../.ai/logs/qemu-fw/mcp-full-feature-250m.spec.json`
- `../.ai/logs/qemu-fw/mcp-full-feature-health.json`
- `../.ai/logs/qemu-fw/mcp-full-feature-250m/report.json`
- `../.ai/logs/qemu-fw/mcp-full-feature-250m/runtime-status.json`
- `../.ai/logs/qemu-fw/mcp-full-feature-250m/events.jsonl`

The PASS result means the declared software integration is complete. It does
not claim electrical timing, Cortex-M0+ execution, FUS execution, or RF
transmission; those remain explicit replay/model boundaries.

The effective global registration was additionally exercised with
`initialize`, `tools/list`, and `emulator_capabilities`: protocol `2024-11-05`,
15 tools, clean stderr, and no tool error.
