#!/usr/bin/env python3
"""Passive USB and session-log observer for the dev-board control run."""

from __future__ import annotations

import datetime as dt
import glob
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".ai" / "logs" / "flash-session"
WATCHED_LOGS = (
    "swd-flash-live.log",
    "devboard-parallel.log",
    "flash-live.log",
    "direct-dfu-preflight.log",
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def atomic_write(path: Path, content: str) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def usb_snapshot() -> str:
    try:
        result = subprocess.run(
            ["ioreg", "-r", "-c", "IOUSBHostDevice", "-l", "-w0"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=8,
            check=False,
        )
        return result.stdout[: 512 * 1024].decode(errors="replace")
    except (OSError, subprocess.SubprocessError) as error:
        return f"ioreg error: {type(error).__name__}: {error}"


def render(state: dict[str, object]) -> str:
    transitions = state["recent_transitions"] or ["none"]
    changes = state["log_changes"] or ["none"]
    return "\n".join(
        (
            "# Full-control progress",
            "",
            "| Signal | Current state |",
            "|---|---|",
            f"| Observer | `running` PID `{state['pid']}`; passive/read-only |",
            f"| Updated UTC | `{state['timestamp']}` |",
            f"| Samples | `{state['samples']}` every 2 seconds |",
            f"| BMP USB | `{'present' if state['bmp_usb'] else 'absent'}` |",
            f"| BMP 1101 | `{'present' if state['bmp_1101'] else 'absent'}` |",
            f"| BMP 1103 | `{'present' if state['bmp_1103'] else 'absent'}` |",
            f"| FZ normal | `{'present' if state['fz_normal'] else 'absent'}` |",
            f"| FZ DFU | `{'present' if state['fz_dfu'] else 'absent'}` |",
            f"| Recent transitions | {'<br>'.join(f'`{x}`' for x in transitions)} |",
            f"| Changed logs | {'<br>'.join(f'`{x}`' for x in changes)} |",
            "| Serial/SWD access | `none` |",
            "",
        )
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    pid_path = OUT / "full-control-monitor.pid"
    state_path = OUT / "full-control-state.json"
    events_path = OUT / "full-control-events.jsonl"
    progress_path = OUT / "full-control-progress.md"
    atomic_write(pid_path, f"{os.getpid()}\n")
    stopping = False

    def stop(_signum: int, _frame: object) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    previous_flags: dict[str, bool] = {}
    previous_logs: dict[str, tuple[int, int]] = {}
    recent: list[str] = []
    samples = 0
    while not stopping:
        samples += 1
        usb = usb_snapshot().lower()
        nodes = sorted(glob.glob("/dev/cu.usbmodem*") + glob.glob("/dev/tty.usbmodem*"))
        node_text = " ".join(nodes).lower()
        flags = {
            "bmp_usb": "blackmagic esp32" in usb or ("303a" in usb and "4001" in usb),
            "bmp_1101": "usbmodem1101" in node_text,
            "bmp_1103": "usbmodem1103" in node_text,
            "fz_normal": "flipper asch1rp" in usb or "flip_asch1rp" in usb,
            "fz_dfu": "stm32 bootloader" in usb or ("stm32" in usb and "dfu" in usb),
        }
        timestamp = utc_now()
        transitions = [
            f"{timestamp} {key}={'present' if value else 'absent'}"
            for key, value in flags.items()
            if key in previous_flags and previous_flags[key] != value
        ]
        if transitions:
            recent = (transitions + recent)[:12]
        previous_flags = flags.copy()
        log_changes: list[str] = []
        log_status: dict[str, dict[str, int]] = {}
        for name in WATCHED_LOGS:
            path = OUT / name
            try:
                stat = path.stat()
                signature = (stat.st_size, stat.st_mtime_ns)
                log_status[name] = {"bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}
                if name in previous_logs and previous_logs[name] != signature:
                    log_changes.append(f"{name} ({previous_logs[name][0]}->{stat.st_size} bytes)")
                previous_logs[name] = signature
            except FileNotFoundError:
                log_status[name] = {"bytes": -1, "mtime_ns": -1}
        state: dict[str, object] = {
            "pid": os.getpid(),
            "timestamp": timestamp,
            "samples": samples,
            "read_only": True,
            "serial_or_swd_opened": False,
            "serial_nodes": nodes,
            "recent_transitions": recent,
            "transitions": transitions,
            "log_changes": log_changes,
            "logs": log_status,
            **flags,
        }
        atomic_write(state_path, json.dumps(state, indent=2, sort_keys=True) + "\n")
        atomic_write(progress_path, render(state))
        if samples == 1 or transitions or log_changes:
            with events_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(state, sort_keys=True) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        time.sleep(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
