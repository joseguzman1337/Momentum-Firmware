# Flipper emulator v2 coverage

| Surface | Model | Verification | Boundary |
|---|---|---|---|
| Cortex-M4/NVIC/SysTick | Native instruction engine | Headless instruction run | Timing is not cycle-exact |
| Display/buttons/audio | Native peripherals and event trace | Frame/input/audio events | Electrical behavior omitted |
| SD | FAT block image | Manifest SHA-256 and sector I/O | Host-isolated fixture only |
| Internal `/int` | Persistent flash image | Restart/readback and NOR semantics | Never copied from protected storage |
| USB CDC/RPC | Host transport model | Framing and RPC request tests | No physical USB device impersonation |
| InfoTable | Safe synthetic facts | Schema and rejection tests | No UID, keys, OTP or calibration secrets |
| Option bytes | Read-only safe defaults | Mutation rejection test | No RDP or boot configuration writes |
| HSEM | 32 ownership semaphores | Exclusion/release tests | Functional, not cycle-exact |
| IPCC | Six channels per direction | Busy/delivery/consume tests | Message-level model |
| CPU2/FUS/radio | Deterministic command/reply replay | State/version/BLE-bound tests | No M0+ or RF execution |
| Public C2 image | Hash/provenance reference | Size/hash and non-execution test | Never mapped or executed |

“Complete” means complete enough to exercise firmware service boundaries and
reproduce boot/application logic. It does not claim RF conformance, protected
STM32WB state extraction, or cycle-accurate dual-core silicon emulation.
