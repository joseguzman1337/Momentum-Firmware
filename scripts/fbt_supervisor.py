#!/usr/bin/env python3
"""Timestamp, classify, and safely retry FBT subprocesses."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Sequence


class FailureKind(Enum):
    USB_TRANSIENT = "usb_transient"
    NETWORK_TRANSIENT = "network_transient"
    BUILD = "build"
    UNKNOWN = "unknown"


def classify_line(line: str) -> FailureKind | None:
    lower = line.lower()
    if any(
        marker in lower
        for marker in (
            "timed out waiting for",
            "serialexception",
            "could not configure port",
            "device disconnected",
            "input/output error",
            "no such device",
            "storage error: file/dir not exist",
        )
    ):
        return FailureKind.USB_TRANSIENT
    if any(
        marker in lower
        for marker in (
            "urlerror",
            "connection timed out",
            "temporary failure in name resolution",
            "remote end closed connection",
        )
    ):
        return FailureKind.NETWORK_TRANSIENT
    if (
        " fbt errors " in lower
        or "scons: ***" in lower
        or ("error:" in lower and (".c:" in lower or ".cpp:" in lower or ".h:" in lower))
    ):
        return FailureKind.BUILD
    return None


def select_failure(kinds: set[FailureKind | None]) -> FailureKind:
    """Prefer a specific recoverable cause over generic SCons wrappers."""
    if FailureKind.USB_TRANSIENT in kinds:
        return FailureKind.USB_TRANSIENT
    if FailureKind.NETWORK_TRANSIENT in kinds:
        return FailureKind.NETWORK_TRANSIENT
    if FailureKind.BUILD in kinds:
        return FailureKind.BUILD
    return FailureKind.UNKNOWN


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def next_usb_chunk_size(current: int) -> int:
    return max(1024, current // 2)


def extract_selfupdate_manifest(line: str) -> Path | None:
    match = re.search(r"Local manifest:\s+(.+\.fuf)\s*$", line)
    return Path(match.group(1)) if match else None


def selfupdate_retry_command(manifest: Path, *, port: str) -> list[str]:
    script = Path(__file__).resolve().parents[1] / "scripts" / "selfupdate.py"
    return [sys.executable, str(script), "-p", port, str(manifest)]


def _default_remediation(kind: FailureKind, attempt: int) -> bool:
    if kind is FailureKind.NETWORK_TRANSIENT:
        return True
    if kind is not FailureKind.USB_TRANSIENT:
        return False
    current_chunk = int(os.environ.get("FBT_STORAGE_CHUNK_SIZE", "4096"))
    os.environ["FBT_STORAGE_CHUNK_SIZE"] = str(next_usb_chunk_size(current_chunk))
    repository = Path(__file__).resolve().parents[1]
    reset_script = repository / "scripts" / "usbreset_flipper.py"
    result = subprocess.run([sys.executable, str(reset_script)], check=False)
    if result.returncode == 0:
        time.sleep(float(os.environ.get("FBT_USB_RESET_DELAY", "8")))
        return True
    return False


def supervise(
    command: Sequence[str],
    *,
    phase: str,
    log_dir: Path,
    max_attempts: int,
    remediation: Callable[[FailureKind, int], bool] = _default_remediation,
    retry_delay: float = 3,
) -> int:
    log_dir.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = log_dir / f"{run_id}-{phase}.log"
    events_path = log_dir / f"{run_id}-{phase}.jsonl"
    attempt = 0
    active_command = list(command)
    manifest: Path | None = None
    while max_attempts == 0 or attempt < max_attempts:
        attempt += 1
        kinds: set[FailureKind] = set()
        with log_path.open("a", encoding="utf-8") as log, events_path.open(
            "a", encoding="utf-8"
        ) as events:
            start = f"{_timestamp()} [{phase}][attempt={attempt}] START {' '.join(active_command)}"
            print(start, flush=True)
            log.write(start + "\n")
            process = subprocess.Popen(
                active_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert process.stdout is not None
            try:
                for raw_line in process.stdout:
                    line = raw_line.rstrip("\r\n")
                    discovered_manifest = extract_selfupdate_manifest(line)
                    if discovered_manifest is not None:
                        manifest = discovered_manifest
                    stamped = f"{_timestamp()} [{phase}][attempt={attempt}] {line}"
                    print(stamped, flush=True)
                    log.write(stamped + "\n")
                    log.flush()
                    kind = classify_line(line)
                    if kind is not None:
                        kinds.add(kind)
                        event = {
                            "timestamp": _timestamp(),
                            "phase": phase,
                            "attempt": attempt,
                            "kind": kind.value,
                            "line": line,
                        }
                        events.write(json.dumps(event, sort_keys=True) + "\n")
                        events.flush()
            except KeyboardInterrupt:
                process.terminate()
                process.wait()
                raise
            return_code = process.wait()
            end = f"{_timestamp()} [{phase}][attempt={attempt}] EXIT code={return_code}"
            print(end, flush=True)
            log.write(end + "\n")
        if return_code == 0:
            return 0
        failure = select_failure(kinds)
        if (max_attempts and attempt >= max_attempts) or not remediation(failure, attempt):
            return return_code
        if failure is FailureKind.USB_TRANSIENT and manifest and manifest.is_file():
            active_command = selfupdate_retry_command(
                manifest, port=os.environ.get("FLIPPER_PATH", "auto")
            )
        message = (
            f"{_timestamp()} [{phase}][attempt={attempt}] "
            f"AUTOREMEDIATE kind={failure.value}"
            f" chunk_size={os.environ.get('FBT_STORAGE_CHUNK_SIZE', 'unchanged')}; retrying"
        )
        print(message, flush=True)
        with log_path.open("a", encoding="utf-8") as log:
            log.write(message + "\n")
        time.sleep(retry_delay)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    parser.add_argument("--max-attempts", type=int, default=1)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command is required after --")
    return supervise(
        command,
        phase=args.phase,
        log_dir=args.log_dir,
        max_attempts=args.max_attempts,
    )


if __name__ == "__main__":
    raise SystemExit(main())
