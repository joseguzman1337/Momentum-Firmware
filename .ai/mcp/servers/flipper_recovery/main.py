#!/usr/bin/env python3
"""FastMCP adapter for the repository-local safe Flipper recovery engine."""

import importlib.util
import sys
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP as MCPServer
except ModuleNotFoundError:  # MCP SDK 2.x rename
    try:
        from mcp.server.mcpserver import MCPServer
    except ModuleNotFoundError:
        SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
        sys.path.insert(0, str(SCRIPTS))
        from mcp_stdio import FastMCPCompat as MCPServer

ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location("flipper_recovery", ROOT / "scripts/flipper_recovery.py")
recovery = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(recovery)

mcp = MCPServer("flipper-recovery")

@mcp.tool()
def get_recovery_status() -> dict:
    """Read device inventory and monitor state; never builds or flashes."""
    return {"workspace": str(ROOT), **recovery.devices(), "monitor": recovery.monitor_status(ROOT)}

@mcp.tool()
def analyze_firmware_image(image: str) -> dict:
    """Read and validate an ELF against the immutable CPU2 flash boundary."""
    return recovery.validate_image(Path(image))

@mcp.tool()
def get_verified_good_state() -> dict:
    """The verify_good_state readonly surface: prove Flipper CDC 0483:5740; never writes or flashes."""
    return recovery.verify_good_state()

@mcp.tool()
def run_safe_build(dry_run: bool = False) -> dict:
    """Build firmware and reject the result if its flash payload crosses CPU2."""
    return recovery.build(root=ROOT, dry_run=dry_run)

@mcp.tool()
def flash_firmware_usb(image: str, confirm: str = "", dry_run: bool = False) -> dict:
    """IRREVERSIBLE/DESTRUCTIVE: USB-flash a verified ELF; requires FLASH_VERIFIED_IMAGE."""
    return recovery.flash_usb(Path(image), root=ROOT, confirm=confirm, dry_run=dry_run)

@mcp.tool()
def flash_firmware_swd(image: str, port: str = "/dev/cu.usbmodem1101", confirm: str = "", dry_run: bool = False) -> dict:
    """IRREVERSIBLE/DESTRUCTIVE: SWD-flash a verified ELF; requires FLASH_VERIFIED_IMAGE."""
    return recovery.flash_swd(Path(image), root=ROOT, port=port, confirm=confirm, dry_run=dry_run)

@mcp.tool()
def recover_to_good_state(image: str, port: str = "/dev/cu.usbmodem1101", confirm: str = "", build_first: bool = True, dry_run: bool = False) -> dict:
    """IRREVERSIBLE/DESTRUCTIVE recovery orchestration; requires FLASH_VERIFIED_IMAGE and never claims completion without Flipper CDC proof."""
    return recovery.recover_to_good_state(Path(image), root=ROOT, port=port, confirm=confirm, build_first=build_first, dry_run=dry_run)

@mcp.tool()
def arm_autoflash(image: str, port: str = "/dev/cu.usbmodem1101", confirm: str = "") -> dict:
    """Arm exactly one verified SWD recovery; requires FLASH_VERIFIED_IMAGE and pins image hash."""
    return recovery.arm_monitor(Path(image), root=ROOT, port=port, confirm=confirm)

@mcp.tool()
def get_monitor_observation() -> dict:
    """Read devices and monitor state once; never writes, arms, builds, or flashes."""
    return recovery.monitor_observation(ROOT)

@mcp.tool()
def run_monitor_once() -> dict:
    """Run one active monitor cycle; may consume a prior explicit one-shot autoflash arm."""
    return recovery.monitor_once(ROOT)

@mcp.tool()
def start_recovery_monitor(interval: float = 3.0) -> dict:
    """Start the single-instance background observer; starting it never arms a flash."""
    return recovery.monitor_start(ROOT, interval=interval)

@mcp.tool()
def stop_recovery_monitor() -> dict:
    """Stop only the recovery monitor instance recorded by this repository."""
    return recovery.monitor_stop(ROOT)

@mcp.tool()
def get_monitor_status() -> dict:
    """Read persistent monitor, arm, PID, and log state without mutation or flash."""
    return recovery.monitor_status(ROOT)

@mcp.tool()
def get_monitor_history(limit: int = 100, since: float | None = None, state: str | None = None) -> list[dict]:
    """Read bounded persistent transition/heartbeat history; never writes or flashes."""
    return recovery.get_monitor_history(ROOT, limit=limit, since=since, state=state)

@mcp.tool()
def get_monitor_debug_summary() -> dict:
    """Read current monitor diagnostics and recent transitions; never writes or flashes."""
    return recovery.get_monitor_debug_summary(ROOT)

if __name__ == "__main__":
    mcp.run()
