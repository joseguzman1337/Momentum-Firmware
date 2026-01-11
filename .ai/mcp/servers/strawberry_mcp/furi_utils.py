"""
Utility functions for Furi OS (Flipper Zero) tools
"""
import os
import asyncio
from typing import Optional, Tuple

async def run_command_async(command: str) -> Tuple[int, str, str]:
    """Run a command asynchronously and capture output

    Args:
        command: The command to run

    Returns:
        Tuple[int, str, str]: Return code, stdout, stderr
    """
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout.decode(), stderr.decode()
    except Exception as e:
        return 1, "", f"Error executing command: {str(e)}"

async def run_command_async_stream(command: str, log_path: str) -> Tuple[int, str, str]:
    """Run a command asynchronously, streaming stdout/stderr to a log file.

    Args:
        command: The command to run
        log_path: Path to log file for real-time output

    Returns:
        Tuple[int, str, str]: Return code, stdout, stderr
    """
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_chunks = []
        stderr_chunks = []

        async def _read_stream(stream, prefix, chunks):
            while True:
                line = await stream.readline()
                if not line:
                    break
                text = line.decode(errors="replace")
                chunks.append(text)
                with open(log_path, "a") as handle:
                    handle.write(f"{prefix}{text}")
                    handle.flush()

        await asyncio.gather(
            _read_stream(process.stdout, "[stdout] ", stdout_chunks),
            _read_stream(process.stderr, "[stderr] ", stderr_chunks),
        )

        returncode = await process.wait()
        return returncode, "".join(stdout_chunks), "".join(stderr_chunks)
    except Exception as e:
        return 1, "", f"Error executing command: {str(e)}"
