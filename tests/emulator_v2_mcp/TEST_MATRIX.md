# Emulator v2 MCP completion matrix

“100% connected” means every row below passes against the checked-in stdio
entrypoint.  It does not mean the emulator models 100% of physical Flipper Zero
hardware; modeled and replay-only surfaces remain declared by
`tools/flipper_emulator/capabilities.json`.

| Layer | Required evidence | Automated test |
| --- | --- | --- |
| MCP lifecycle | `initialize`, negotiated version, server identity | `test_initialize_notification_list_and_representative_call` |
| Notifications | `notifications/initialized` produces no response and does not block the next request | same lifecycle test |
| Discovery | all tools have unique names and object JSON Schemas | same lifecycle test |
| Invocation | representative `tools/call` returns structured Emulator v2 capabilities | same lifecycle test |
| Errors | unknown method uses JSON-RPC `-32601`; unknown tool and bad arguments use MCP tool errors | `test_unknown_method_and_tool_have_standard_distinct_errors`, `test_invalid_arguments_are_reported_as_tool_errors` |
| Resources | every advertised resource can be read | `test_resources_are_readable` |
| Backend bridge | both `native-runner` and `interactive-v2` are advertised and hardware access is false | `test_diagnostics_cover_every_declared_emulator_subsystem` |
| Long-run plumbing | MCP background run carries `250000000` to a hermetic fake engine and exposes status, report, and events | `test_native_background_run_honors_250m_instruction_spec` |
| Canonical native run | compiled engine SHA `3e41b8...` executes current firmware SHA `ee6b41...` for 250M, reaches stable UI, and emits frame/input events | `test_real_compiled_engine_runs_current_firmware_for_250m` |
| Run-bound control | screen and input require a native `run_id`; they never silently target the duplicate process-local model | `test_screen_and_input_are_bound_to_a_native_run` |
| Interactive smoke | process-local CPU advances 250M cycles without halting | `test_sensible_long_run_is_deterministic_and_does_not_halt` |
| Virtual storage | MCP reads from an isolated temporary `/ext` tree | `test_storage_round_trip_stays_inside_temporary_virtual_card` |
| Path safety | traversal cannot read a host sentinel through storage or virtual USB RPC | `test_path_traversal_is_rejected_without_touching_host_files` |
| Hardware isolation | capabilities assert `hardware_access=false`; tests use only a fake engine, temporary files, and virtual PTY | lifecycle, backend, long-run, and storage tests |
| Documentation truth | no private unit identity or physical RF/key-transmission claim; no-hardware and replay limitations are explicit | `DocumentationAccuracyTests` |

Run with:

```sh
python3 -m unittest -v tests.emulator_v2_mcp.test_mcp_integration
```
