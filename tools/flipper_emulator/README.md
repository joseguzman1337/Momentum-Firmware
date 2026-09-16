# Flipper firmware emulator wrapper

This module runs the separately built GPL STM32 engine in its own process and
staging directory. It never discovers, opens, resets, reads, or writes USB/SWD
hardware. The supplied firmware, SVD, optional SD image, engine binary, and run
limit are explicit inputs.

Create a JSON spec (see `spec.schema.json`) and run:

```sh
python3 -m tools.flipper_emulator.runner run.json
```

The output directory receives the exact generated profile, raw engine log,
deterministic instruction-clocked `events.jsonl`, and `report.json` containing
artifact hashes and the modeled/unmodeled peripheral boundary. Button hooks use
the engine's stdin protocol. Display frames and speaker changes are captured as
structured events. An optional SD image is copied into the isolated stage so
firmware writes cannot modify the source image.

This is a firmware-behavior simulator, not an exact physical twin. CPU2 radio,
NFC, infrared output, raw internal storage persistence, electrical behavior and
cycle-exact timing remain unmodeled and are always disclosed in the report.

`flipper_emulator.py` remains the small backend-selection front-end for native
and Renode comparison. `runner.py` is the stricter native backend interface for
isolated runs, virtual-device hooks, hashes, and machine-readable traces. The
two interfaces share the capability boundary in `capabilities.json`; neither
uses the hardware-oracle backend unless a separate hardware session is invoked
explicitly.

An `oracle_snapshot` input validates the sanitized manifest, capture safety
counters, fixture hashes, and redaction before execution. Snapshot metadata is
reported alongside the run but is never presented as an SD filesystem. A real
`sd_image` is required to exercise block reads and resource contents.

Alternatively, `sd_tree` accepts the validated content-addressed fixture root.
The runner verifies every manifest path, byte count and SHA-256, materializes
hard links as ordinary files, and creates an isolated FAT image. CPU2/FUS/radio
facts from `oracle_snapshot` are limited to sanitized versions and alive/mode
status; reports label these as replay stubs, never as CPU2 or RF emulation.

Set `virtual_usb: true` to start a process-local PTY that implements the Flipper
CDC CLI-to-RPC handshake and delimited `PB.Main` framing. Ping, sanitized device
info, protobuf version, ScreenStream, and read-only `/int` list/read calls are
available. `internal_flash_image` optionally selects the atomic persistent,
sanitized `/int` image; otherwise it is stored in the run output. This transport
does not impersonate physical USB hardware or alter production firmware.

The wire implementation uses the protocol declarations in `assets/protobuf`
and the qFlipper/flipperzero-firmware projects as interoperability references;
it does not copy qFlipper implementation code or link it into the emulator.
