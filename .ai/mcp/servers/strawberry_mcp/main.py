"""Strawberry MCP tools for safe local Flipper firmware operations."""
from __future__ import annotations
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    MCP_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
    if str(MCP_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MCP_SCRIPTS))
    from mcp_stdio import FastMCPCompat as FastMCP
from furi_utils import run_command_async, run_command_async_stream

mcp = FastMCP("strawberry-mcp")
REPO_ROOT = Path(__file__).resolve().parents[4]
LOG_DIR = Path(os.getenv("STRAWBERRY_MCP_LOG_DIR", REPO_ROOT / ".ai" / "logs" / "strawberry_mcp"))
ALLOWED_TARGETS = {"f7": "7", "f18": "18"}
APP_ID_RE = re.compile(r"^[a-z0-9_]+$")
GPIO_STATE_RE = re.compile(
    r"(?i)(?:\bstate\s*[:=]\s*(HIGH|LOW|[01])\b|\b(HIGH|LOW)\b|[:=]\s*([01])\b)"
)
FLIPPER_CLI_CONFIRMATION = "EXECUTE_FLIPPER_CLI"
GPIO_SET_CONFIRMATION = "EXECUTE_GPIO_SET"
FLASH_FIRMWARE_CONFIRMATION = "FLASH_VERIFIED_FIRMWARE"
CLEAN_FIRMWARE_CONFIRMATION = "CLEAN_BUILD_ARTIFACTS"

def _write_log(filename: str, content: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / filename).write_text(content, encoding="utf-8")

def _timestamped(name: str) -> str:
    return f"{name}-{time.strftime('%Y%m%d-%H%M%S')}.log"

def _log_path(filename: str) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return LOG_DIR / filename

def _result(return_code: int, stdout: str = "", stderr: str = "", **extra: Any) -> dict[str, Any]:
    return {"success": return_code == 0, "return_code": return_code, "stdout": stdout, "stderr": stderr, **extra}

def _validation_error(message: str, **extra: Any) -> dict[str, Any]:
    return _result(2, stderr=message, error="validation_error", **extra)

def _validate_pin(pin: int) -> dict[str, Any] | None:
    if isinstance(pin, bool) or not isinstance(pin, int) or not 0 <= pin <= 13:
        return _validation_error("pin must be an integer from 0 through 13", pin=pin)
    return None

async def _cli(command: str, timeout: float = 30.0) -> dict[str, Any]:
    if not isinstance(command, str) or not command.strip():
        return _validation_error("command must be a non-empty string")
    if len(command) > 512 or any(ord(char) < 32 and char != "\t" for char in command):
        return _validation_error("command contains control characters or exceeds 512 characters")
    argv = [str(REPO_ROOT / "fbt"), "cli", "-c", command]
    returncode, stdout, stderr = await run_command_async(argv, cwd=REPO_ROOT, timeout=timeout)
    return _result(returncode, stdout, stderr)

@mcp.tool()
async def build_firmware(target: str = "f7", app_id: str | None = None) -> dict[str, Any]:
    """Build firmware or a named external app; never accesses or flashes a device."""
    if target not in ALLOWED_TARGETS:
        return _validation_error("target must be one of: f7, f18", target=target)
    if app_id is not None and not APP_ID_RE.fullmatch(app_id):
        return _validation_error("app_id must match ^[a-z0-9_]+$", app_id=app_id)
    argv = [str(REPO_ROOT / "fbt"), f"fap_{app_id}" if app_id else "firmware_all", f"TARGET_HW={ALLOWED_TARGETS[target]}"]
    started = time.monotonic()
    returncode, stdout, stderr = await run_command_async_stream(argv, _log_path("mcp-build-live.log"), cwd=REPO_ROOT, timeout=1800.0)
    elapsed = time.monotonic() - started
    result = _result(returncode, stdout, stderr, elapsed_seconds=round(elapsed, 3), target=target, app_id=app_id)
    serialized = repr(result)
    _write_log("mcp-build.log", serialized)
    _write_log(_timestamped("mcp-build"), serialized)
    logging.info("build completed in %.2fs with return code %d", elapsed, returncode)
    return result

@mcp.tool()
async def flash_firmware(confirm: str | None = None, dry_run: bool = True) -> dict[str, Any]:
    """Flash via USB only with the exact textual confirmation token."""
    argv = [str(REPO_ROOT / "fbt"), "flash_usb_full"]
    if dry_run:
        return _result(0, dry_run=True, executed=False, command=argv, required_confirmation=FLASH_FIRMWARE_CONFIRMATION)
    if not isinstance(confirm, str) or confirm != FLASH_FIRMWARE_CONFIRMATION:
        return _validation_error(
            f"flash requires confirm={FLASH_FIRMWARE_CONFIRMATION!r} when dry_run=false",
            dry_run=False,
            executed=False,
            required_confirmation=FLASH_FIRMWARE_CONFIRMATION,
        )
    started = time.monotonic()
    returncode, stdout, stderr = await run_command_async_stream(argv, _log_path("mcp-flash-live.log"), cwd=REPO_ROOT, timeout=600.0)
    result = _result(returncode, stdout, stderr, dry_run=False, executed=True, elapsed_seconds=round(time.monotonic() - started, 3))
    serialized = repr(result)
    _write_log("mcp-flash.log", serialized)
    _write_log(_timestamped("mcp-flash"), serialized)
    return result

@mcp.tool()
async def clean_firmware(confirm: str | None = None, dry_run: bool = True) -> dict[str, Any]:
    """Clean build artifacts only after explicit confirmation; dry-run by default."""
    argv = [str(REPO_ROOT / "fbt"), "-c"]
    if dry_run:
        return _result(0, dry_run=True, executed=False, command=argv, required_confirmation=CLEAN_FIRMWARE_CONFIRMATION)
    if not isinstance(confirm, str) or confirm != CLEAN_FIRMWARE_CONFIRMATION:
        return _validation_error(
            f"clean requires confirm={CLEAN_FIRMWARE_CONFIRMATION!r} when dry_run=false",
            dry_run=False,
            executed=False,
            required_confirmation=CLEAN_FIRMWARE_CONFIRMATION,
        )
    returncode, stdout, stderr = await run_command_async_stream(argv, _log_path("mcp-clean-live.log"), cwd=REPO_ROOT, timeout=600.0)
    result = _result(returncode, stdout, stderr, dry_run=False, executed=True)
    _write_log("mcp-clean.log", repr(result))
    return result

@mcp.tool()
async def deploy_wifi_devboard_config() -> dict[str, Any]:
    """Report configuration support without claiming an unimplemented deployment."""
    return _result(3, stderr="No deployable WiFi Devboard configuration artifact is defined in this repository", supported=False, executed=False, error="not_implemented")

@mcp.tool()
async def gpio_set(
    pin: int,
    state: bool,
    dry_run: bool = True,
    confirmation: str | None = None,
) -> dict[str, Any]:
    """Plan a GPIO mutation by default; execute only with the exact confirmation token."""
    if error := _validate_pin(pin):
        return error
    if not isinstance(state, bool):
        return _validation_error("state must be a boolean", pin=pin)
    command = f"gpio set {pin} {1 if state else 0}"
    plan = {
        "command": command,
        "pin": pin,
        "state": "HIGH" if state else "LOW",
        "dry_run": dry_run,
        "executed": False,
        "required_confirmation": GPIO_SET_CONFIRMATION,
    }
    if dry_run:
        return _result(0, **plan)
    if confirmation != GPIO_SET_CONFIRMATION:
        return _validation_error(
            f"gpio_set requires confirmation={GPIO_SET_CONFIRMATION!r} when dry_run=false",
            **plan,
        )
    result = await _cli(command)
    result.update(pin=pin, state="HIGH" if state else "LOW")
    result.update(dry_run=False, executed=True)
    return result

@mcp.tool()
async def gpio_read(pin: int) -> dict[str, Any]:
    """Read and strictly parse a GPIO pin state."""
    if error := _validate_pin(pin):
        return error
    result = await _cli(f"gpio read {pin}")
    result["pin"] = pin
    if not result["success"]:
        return result
    matches = [token for match in GPIO_STATE_RE.findall(result["stdout"]) for token in match if token]
    if not matches:
        return _result(65, result["stdout"], "Unable to parse GPIO state", pin=pin, error="parse_error")
    token = matches[-1].upper()
    result["state"] = "HIGH" if token in {"HIGH", "1"} else "LOW"
    return result

@mcp.tool()
async def system_info() -> dict[str, Any]:
    """Get device information through the Flipper CLI."""
    return await _cli("device_info")

@mcp.tool()
async def storage_info() -> dict[str, Any]:
    """Get SD-card information through the Flipper CLI."""
    return await _cli("storage info")

@mcp.tool()
async def nfc_detect() -> dict[str, Any]:
    """Request NFC detection and report evidence present in CLI output."""
    result = await _cli("nfc detect", timeout=60.0)
    result["tag_detected"] = bool(result["success"] and re.search(r"\b(?:tag\s+detected|uid\s*[:=])", result["stdout"], re.IGNORECASE))
    return result

@mcp.tool()
async def flipper_cli(
    command: str,
    dry_run: bool = True,
    confirmation: str | None = None,
) -> dict[str, Any]:
    """Plan an arbitrary CLI command by default; execute only with exact confirmation."""
    if not isinstance(command, str) or not command.strip():
        return _validation_error("command must be a non-empty string", dry_run=dry_run, executed=False)
    if len(command) > 512 or any(ord(char) < 32 and char != "\t" for char in command):
        return _validation_error(
            "command contains control characters or exceeds 512 characters",
            dry_run=dry_run,
            executed=False,
        )
    plan = {
        "command": command,
        "dry_run": dry_run,
        "executed": False,
        "required_confirmation": FLIPPER_CLI_CONFIRMATION,
    }
    if dry_run:
        return _result(0, **plan)
    if confirmation != FLIPPER_CLI_CONFIRMATION:
        return _validation_error(
            f"flipper_cli requires confirmation={FLIPPER_CLI_CONFIRMATION!r} when dry_run=false",
            **plan,
        )
    result = await _cli(command)
    result.update(dry_run=False, executed=True)
    return result

if __name__ == "__main__":
    mcp.run()
