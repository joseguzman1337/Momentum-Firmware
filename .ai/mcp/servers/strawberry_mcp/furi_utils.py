"""Safe asynchronous process helpers for Strawberry's Flipper tools."""
from __future__ import annotations
import asyncio
from collections import deque
from pathlib import Path
from typing import Sequence, Tuple

DEFAULT_TIMEOUT = 300.0
MAX_CAPTURE_BYTES = 1024 * 1024
MAX_LOG_BYTES = 8 * 1024 * 1024
PROCESS_STOP_TIMEOUT = 2.0
_TRUNCATION_MARKER = b"[... earlier output truncated ...]\n"


class _BoundedCapture:
    """Retain only the newest output bytes without bounding process drainage."""

    def __init__(self, limit: int = MAX_CAPTURE_BYTES) -> None:
        self.limit = max(1, limit)
        self.parts: deque[bytes] = deque()
        self.size = 0
        self.truncated = False

    def append(self, data: bytes) -> None:
        if not data:
            return
        if len(data) >= self.limit:
            self.parts.clear()
            self.parts.append(data[-self.limit :])
            self.size = self.limit
            self.truncated = True
            return
        self.parts.append(data)
        self.size += len(data)
        while self.size > self.limit and self.parts:
            excess = self.size - self.limit
            first = self.parts[0]
            if len(first) <= excess:
                self.parts.popleft()
                self.size -= len(first)
            else:
                self.parts[0] = first[excess:]
                self.size -= excess
            self.truncated = True

    def text(self) -> str:
        data = b"".join(self.parts).decode(errors="replace")
        if self.truncated:
            return _TRUNCATION_MARKER.decode() + data
        return data


class _BoundedLogWriter:
    """Append with hysteretic compaction, avoiding a full-log rewrite per chunk."""

    def __init__(self, path: Path, limit: int = MAX_LOG_BYTES) -> None:
        self.path = path
        self.limit = max(len(_TRUNCATION_MARKER) + 1, limit)
        # Dropping to half capacity means another half-log must arrive before
        # the next rotation. Total disk I/O therefore stays linear in output.
        self.low_watermark = max(len(_TRUNCATION_MARKER) + 1, self.limit // 2)
        self.handle = path.open("ab")
        self.size = self.handle.tell()
        self.rotations = 0

    def append(self, payload: bytes) -> None:
        if not payload:
            return
        if self.size + len(payload) <= self.limit:
            self.handle.write(payload)
            self.size += len(payload)
            return

        self.handle.flush()
        self.handle.close()
        tail_size = self.low_watermark - len(_TRUNCATION_MARKER)
        # Include the newest payload in the retained tail without ever reading
        # or writing more than one low-watermark per rotation.
        payload_tail = payload[-tail_size:] if tail_size else b""
        remaining = tail_size - len(payload_tail)
        previous_tail = b""
        if remaining > 0:
            with self.path.open("rb") as source:
                source.seek(max(0, self.size - remaining))
                previous_tail = source.read(remaining)
        with self.path.open("wb") as target:
            target.write(_TRUNCATION_MARKER)
            target.write(previous_tail)
            target.write(payload_tail)
        self.rotations += 1
        self.handle = self.path.open("ab")
        self.size = self.handle.tell()

    def close(self) -> None:
        if not self.handle.closed:
            self.handle.close()


def _append_bounded_log(path: Path, payload: bytes) -> None:
    """Compatibility helper for a single bounded append."""
    writer = _BoundedLogWriter(path)
    try:
        writer.append(payload)
    finally:
        writer.close()

async def _stop_process(process: asyncio.subprocess.Process) -> None:
    if process.returncode is not None:
        return
    try:
        process.terminate()
    except ProcessLookupError:
        pass
    try:
        await asyncio.wait_for(process.wait(), timeout=PROCESS_STOP_TIMEOUT)
    except asyncio.TimeoutError:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        try:
            await asyncio.wait_for(process.wait(), timeout=PROCESS_STOP_TIMEOUT)
        except asyncio.TimeoutError:
            # A broken platform transport must not make cancellation cleanup
            # unbounded after both terminate and kill have been attempted.
            return

async def run_command_async(argv: Sequence[str], *, cwd: str | Path | None = None, timeout: float = DEFAULT_TIMEOUT) -> Tuple[int, str, str]:
    """Run an argv vector without a shell and capture decoded output."""
    if not argv:
        return 2, "", "Command argv must not be empty"
    readers: list[asyncio.Task[None]] = []
    process: asyncio.subprocess.Process | None = None
    stdout_capture = _BoundedCapture(MAX_CAPTURE_BYTES)
    stderr_capture = _BoundedCapture(MAX_CAPTURE_BYTES)
    try:
        process = await asyncio.create_subprocess_exec(*(str(arg) for arg in argv), cwd=str(cwd) if cwd is not None else None, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        async def _read_stream(stream: asyncio.StreamReader, capture: _BoundedCapture) -> None:
            while chunk := await stream.read(8192):
                capture.append(chunk)

        readers = [
            asyncio.create_task(_read_stream(process.stdout, stdout_capture)),
            asyncio.create_task(_read_stream(process.stderr, stderr_capture)),
        ]
        try:
            await asyncio.wait_for(asyncio.gather(*readers, process.wait()), timeout=timeout)
        except asyncio.TimeoutError:
            await _stop_process(process)
            for reader in readers:
                if not reader.done():
                    reader.cancel()
            await asyncio.gather(*readers, return_exceptions=True)
            message = f"Command timed out after {timeout:g} seconds"
            stderr = stderr_capture.text()
            return 124, stdout_capture.text(), stderr + ("\n" if stderr else "") + message
        except asyncio.CancelledError:
            await _stop_process(process)
            for reader in readers:
                reader.cancel()
            await asyncio.gather(*readers, return_exceptions=True)
            raise
        return process.returncode or 0, stdout_capture.text(), stderr_capture.text()
    except Exception as error:
        if process is not None:
            await _stop_process(process)
        for reader in readers:
            reader.cancel()
        await asyncio.gather(*readers, return_exceptions=True)
        return 127, "", f"Unable to execute command: {error}"

async def run_command_async_stream(argv: Sequence[str], log_path: str | Path, *, cwd: str | Path | None = None, timeout: float = DEFAULT_TIMEOUT) -> Tuple[int, str, str]:
    """Run argv safely while mirroring stdout and stderr to a log file."""
    if not argv:
        return 2, "", "Command argv must not be empty"
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")
    log_writer = _BoundedLogWriter(path, MAX_LOG_BYTES)
    readers: list[asyncio.Task[None]] = []
    process: asyncio.subprocess.Process | None = None
    try:
        process = await asyncio.create_subprocess_exec(*(str(arg) for arg in argv), cwd=str(cwd) if cwd is not None else None, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout_capture = _BoundedCapture(MAX_CAPTURE_BYTES)
        stderr_capture = _BoundedCapture(MAX_CAPTURE_BYTES)

        async def _read_stream(stream: asyncio.StreamReader, prefix: bytes, capture: _BoundedCapture) -> None:
            while chunk := await stream.read(8192):
                capture.append(chunk)
                log_writer.append(prefix + chunk)

        readers = [
            asyncio.create_task(_read_stream(process.stdout, b"[stdout] ", stdout_capture)),
            asyncio.create_task(_read_stream(process.stderr, b"[stderr] ", stderr_capture)),
        ]
        try:
            await asyncio.wait_for(
                asyncio.gather(*readers, process.wait()), timeout=timeout
            )
        except asyncio.TimeoutError:
            await _stop_process(process)
            for reader in readers:
                if not reader.done():
                    reader.cancel()
            await asyncio.gather(*readers, return_exceptions=True)
            timeout_message = f"Command timed out after {timeout:g} seconds"
            stderr = stderr_capture.text()
            return 124, stdout_capture.text(), stderr + ("\n" if stderr else "") + timeout_message
        except asyncio.CancelledError:
            await _stop_process(process)
            for reader in readers:
                reader.cancel()
            await asyncio.gather(*readers, return_exceptions=True)
            raise
        return process.returncode or 0, stdout_capture.text(), stderr_capture.text()
    except asyncio.CancelledError:
        # This also covers failures before the inner wait block is entered.
        if process is not None:
            await _stop_process(process)
        for reader in readers:
            if not reader.done():
                reader.cancel()
        await asyncio.gather(*readers, return_exceptions=True)
        raise
    except Exception as error:
        # A reader/transport failure must never orphan the child. Keep the
        # helper's established structured failure contract after cleanup.
        if process is not None:
            await _stop_process(process)
        for reader in readers:
            if not reader.done():
                reader.cancel()
        await asyncio.gather(*readers, return_exceptions=True)
        return 127, "", f"Unable to execute command: {error}"
    finally:
        log_writer.close()
