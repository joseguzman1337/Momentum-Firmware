import logging
import shlex
import time
from typing import Optional, Tuple

from mcp.server.fastmcp import FastMCP
import os
from furi_utils import run_command_async, run_command_async_stream

mcp = FastMCP("strawberry-mcp")

LOG_DIR = os.getenv("STRAWBERRY_MCP_LOG_DIR", os.path.join(os.getcwd(), ".ai", "logs", "strawberry_mcp"))

def _ensure_log_dir() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)

def _write_log(filename: str, content: str) -> None:
    _ensure_log_dir()
    log_path = os.path.join(LOG_DIR, filename)
    with open(log_path, "w+") as handle:
        handle.write(content)

def _timestamped(name: str) -> str:
    return f"{name}-{time.strftime('%Y%m%d-%H%M%S')}.log"

def _log_path(filename: str) -> str:
    _ensure_log_dir()
    return os.path.join(LOG_DIR, filename)

@mcp.tool()
async def build_firmware(target: str = "f7", app_id: str = None) -> Tuple[str, str]:
    """Build Flipper Zero firmware using fbt.

    Args:
        target: Target architecture (default: f7).
        app_id: Optional application ID to build specific app (e.g. "applications/main/subghz").

    Returns:
        tuple: (stdout, stderr) - Build logs and error messages.
    """
    start_time = time.time()

    # Assuming fbt is in the repo root
    repo_root = os.getcwd()
    fbt_cmd = "./fbt"

    cmd_args = []
    if app_id:
        cmd_args.append(f"fap_{app_id}")

    full_cmd = f"{fbt_cmd} {' '.join(cmd_args)}"

    build_log = _log_path("mcp-build-live.log")
    returncode, stdout, stderr = await run_command_async_stream(full_cmd, build_log)

    elapsed_time = time.time() - start_time
    timing_info = f"\n\n[Build completed in {elapsed_time:.2f} seconds]\n"
    stdout_with_timing = stdout + timing_info

    _write_log("mcp-build.log", str((stdout, stderr)))
    _write_log(_timestamped("mcp-build"), str((stdout, stderr)))
    logging.warning(f"build result - elapsed: {elapsed_time:.2f}s, return code: {returncode}")
    return stdout_with_timing, stderr

@mcp.tool()
async def flash_firmware() -> Tuple[str, str]:
    """Flash Flipper Zero firmware via USB.

    Returns:
        tuple: (stdout, stderr) - Flash logs and error messages.
    """
    start_time = time.time()
    fbt_cmd = "./fbt flash_usb_full"

    flash_log = _log_path("mcp-flash-live.log")
    returncode, stdout, stderr = await run_command_async_stream(fbt_cmd, flash_log)

    elapsed_time = time.time() - start_time
    timing_info = f"\n\n[Flash completed in {elapsed_time:.2f} seconds]\n"
    stdout_with_timing = stdout + timing_info

    _write_log("mcp-flash.log", str((stdout, stderr)))
    _write_log(_timestamped("mcp-flash"), str((stdout, stderr)))
    return stdout_with_timing, stderr

@mcp.tool()
async def clean_firmware() -> Tuple[str, str]:
    """Clean Flipper Zero build artifacts.

    Returns:
        tuple: (stdout, stderr)
    """
    fbt_cmd = "./fbt -c"

    clean_log = _log_path("mcp-clean-live.log")
    returncode, stdout, stderr = await run_command_async_stream(fbt_cmd, clean_log)

    _write_log("mcp-clean.log", str((stdout, stderr)))
    return stdout, stderr

@mcp.tool()
async def deploy_wifi_devboard_config() -> Tuple[str, str]:
    """Applies the mandatory configuration to always use SD card for WiFi Devboard.

    (Note: This tool is mainly a placeholder to signify the deployment action,
    as the changes are applied to the source code directly).

    Returns:
        tuple: (stdout, stderr)
    """
    return "WiFi Devboard V1 configuration (Always Use SD Card) applied to source code.", ""

@mcp.tool()
async def gpio_set(pin: int, state: bool) -> str:
    """Set GPIO pin state on Flipper Zero.

    Args:
        pin: GPIO pin number (0-13)
        state: True for HIGH, False for LOW

    Returns:
        Status message
    """
    if not (0 <= pin <= 13):
        return f"Error: Invalid pin number {pin}. Must be 0-13."

    state_str = "1" if state else "0"
    cmd = f"./fbt cli -c 'gpio set {pin} {state_str}'"

    returncode, stdout, stderr = await run_command_async(cmd)

    if returncode == 0:
        return f"GPIO pin {pin} set to {'HIGH' if state else 'LOW'}"
    else:
        return f"Error setting GPIO pin {pin}: {stderr}"

@mcp.tool()
async def gpio_read(pin: int) -> dict:
    """Read GPIO pin state from Flipper Zero.

    Args:
        pin: GPIO pin number (0-13)

    Returns:
        Pin state and metadata
    """
    if not (0 <= pin <= 13):
        return {"error": f"Invalid pin number {pin}. Must be 0-13."}

    cmd = f"./fbt cli -c 'gpio read {pin}'"
    returncode, stdout, stderr = await run_command_async(cmd)

    if returncode == 0:
        # Parse output - looking for HIGH/LOW or 1/0
        state = "HIGH" if "1" in stdout or "HIGH" in stdout.upper() else "LOW"
        return {
            "pin": pin,
            "state": state,
            "raw_output": stdout.strip(),
            "success": True
        }
    else:
        return {
            "pin": pin,
            "error": stderr,
            "success": False
        }

@mcp.tool()
async def system_info() -> dict:
    """Get Flipper Zero system information.

    Returns:
        System information including firmware version, hardware info
    """
    cmd = "./fbt cli -c 'device_info'"
    returncode, stdout, stderr = await run_command_async(cmd)

    if returncode == 0:
        return {
            "success": True,
            "device_info": stdout.strip(),
            "raw_output": stdout
        }
    else:
        return {
            "success": False,
            "error": stderr
        }

@mcp.tool()
async def storage_info() -> dict:
    """Get Flipper Zero storage (SD card) information.

    Returns:
        Storage information including size, free space
    """
    cmd = "./fbt cli -c 'storage info'"
    returncode, stdout, stderr = await run_command_async(cmd)

    if returncode == 0:
        return {
            "success": True,
            "storage_info": stdout.strip(),
            "raw_output": stdout
        }
    else:
        return {
            "success": False,
            "error": stderr
        }

@mcp.tool()
async def nfc_detect() -> dict:
    """Detect NFC tag on Flipper Zero.

    Returns:
        NFC tag detection result
    """
    cmd = "./fbt cli -c 'nfc detect'"
    returncode, stdout, stderr = await run_command_async(cmd)

    if returncode == 0:
        # Check if tag was detected
        tag_detected = "detected" in stdout.lower() or "uid" in stdout.lower()
        return {
            "success": True,
            "tag_detected": tag_detected,
            "nfc_output": stdout.strip(),
            "raw_output": stdout
        }
    else:
        return {
            "success": False,
            "error": stderr
        }

@mcp.tool()
async def flipper_cli(command: str) -> dict:
    """Execute arbitrary Flipper CLI command.

    Args:
        command: CLI command (e.g., "gpio set 5 1", "storage info")

    Returns:
        Command output
    """
    # Sanitize command to prevent injection
    safe_command = shlex.quote(command)
    cmd = f"./fbt cli -c {safe_command}"

    returncode, stdout, stderr = await run_command_async(cmd)

    return {
        "success": returncode == 0,
        "stdout": stdout,
        "stderr": stderr,
        "return_code": returncode
    }

if __name__ == '__main__':
    mcp.run(transport='stdio')
