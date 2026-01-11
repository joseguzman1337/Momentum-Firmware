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

if __name__ == '__main__':
    mcp.run(transport='stdio')
