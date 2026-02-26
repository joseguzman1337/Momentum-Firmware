# Wardriving & Marauder Bridge TODOs

## Completed
- [x] Added `fbt aio` dashboard with Super ESP32 AI capabilities.
- [x] Added `fbt spectrum` for parallel synchronized spectrum analysis (Flipper, SK1, RG1).
- [x] Added `fbt ghost` for stealthy synchronized cluster scans with MAC cloaking.
- [x] Implemented `port` command for automated RTL8814U driver deployment to NX nodes.
- [x] Created `fbt hidden` to hide node SSIDs and detect non-broadcasted networks.
- [x] Enforced stealth mode (hide mode) by default on all AI wardriving functions (`aio`, `super`).

## Pending / Next Steps
- [x] Implement automated saving of unified intelligence matrix to SQLite database across `aio`, `super`, `spectrum`, `ghost`, and `hidden` modes.
- [x] Add local database observability/export commands (`dbstats`, `exportcsv`) for downstream analysis tooling.
- [x] Add real-time graphing or TUI visualization of spectrum density across nodes.
- [x] Integrate GPS location metadata from all nodes (if available) to the unified matrix.
- [x] Build a daemon mode to continuously run `ghost` scans and alert on new high-value targets (HVTs).
- [x] Validate Alfa 1900 (RG1/SK1 path) driver stability during prolonged monitor mode operations.
  - Run completed on February 26, 2026 (SK1, `wlan1`, 180s, 5s sampling): `checks=36`, `failures=0`, `pass_rate=100%`.
  - Report: `/tmp/alfa_validation_20260226T051246Z.json` on `SK1`.
