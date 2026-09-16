#!/usr/bin/env python3
"""Read-only recovery observer for Flipper Zero and Blackmagic dev board."""

from __future__ import annotations

import argparse
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
OUTPUT = ROOT / ".ai" / "logs" / "flash-session"
SERIAL_PATTERNS = ("/dev/cu.usb*", "/dev/tty.usb*")
TAIL_FILES = (
    "devboard-parallel.log",
    "devboard-swd-preflight.log",
    "flash-live.log",
    "direct-dfu-preflight.log",
)
MAX_IOREG = 512 * 1024
MAX_TAIL = 64 * 1024


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def snapshot_usb() -> str:
    try:
        result = subprocess.run(
            ["ioreg", "-r", "-c", "IOUSBHostDevice", "-l", "-w0"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=8,
            check=False,
        )
        return result.stdout[:MAX_IOREG].decode("utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError) as error:
        return f"ioreg unavailable: {type(error).__name__}: {error}\n"


def tail(path: Path) -> str:
    try:
        with path.open("rb") as stream:
            stream.seek(0, os.SEEK_END)
            stream.seek(max(0, stream.tell() - MAX_TAIL))
            return stream.read(MAX_TAIL).decode("utf-8", errors="replace")
    except OSError as error:
        return f"unavailable: {type(error).__name__}: {error}\n"


def render(state: dict[str, object]) -> str:
    nodes = state["serial_nodes"] or ["none"]
    transitions = state["transitions"] or ["none"]
    return "\n".join(
        [
            "# Recovery progress",
            "",
            "| Signal | Live state |",
            "|---|---|",
            f"| Observer | running, read-only, PID `{state['pid']}` |",
            f"| Updated UTC | `{state['timestamp']}` |",
            f"| Samples | `{state['samples']}` at 2 s interval |",
            f"| Flipper normal USB | `{'present' if state['flipper_normal'] else 'absent'}` |",
            f"| Flipper DFU | `{'present' if state['flipper_dfu'] else 'absent'}` |",
            f"| Dev board USB | `{'present' if state['devboard_present'] else 'absent'}` |",
            f"| Dev board 1101 | `{'present' if state['devboard_1101'] else 'absent'}` |",
            f"| Dev board 1103 | `{'present' if state['devboard_1103'] else 'absent'}` |",
            f"| Serial nodes | {'<br>'.join(f'`{node}`' for node in nodes)} |",
            f"| Last transitions | {'<br>'.join(f'`{item}`' for item in transitions)} |",
            "| SWD/debug action | none; log tails only |",
            "| Flash/reset action | none |",
            "",
        ]
    )


def run(interval: float) -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    tails = OUTPUT / "recovery-tails"
    tails.mkdir(exist_ok=True)
    atomic_write(OUTPUT / "recovery-monitor.pid", f"{os.getpid()}\n")
    stopping = False

    def stop(_signum: int, _frame: object) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    previous: dict[str, bool] = {}
    samples = 0
    while not stopping:
        samples += 1
        usb = snapshot_usb()
        low = usb.lower()
        nodes = sorted({node for pattern in SERIAL_PATTERNS for node in glob.glob(pattern)})
        node_text = " ".join(nodes).lower()
        flags = {
            # The Blackmagic dev board also reports vendor "Flipper Devices Inc.".
            # Match this unit's FZ product/serial identity, never the vendor label.
            "flipper_normal": "flipper asch1rp" in low or "flip_asch1rp" in low,
            "flipper_dfu": "stm32 bootloader" in low or ("dfu" in low and "stm32" in low),
            "devboard_present": "blackmagic esp32" in low or "303a" in low and "4001" in low,
            "devboard_1101": "usbmodem1101" in node_text,
            "devboard_1103": "usbmodem1103" in node_text,
        }
        transitions = [
            f"{key}:{'connected' if value else 'disconnected'}"
            for key, value in flags.items()
            if key in previous and previous[key] != value
        ]
        previous = flags.copy()
        for name in TAIL_FILES:
            source = OUTPUT / name
            atomic_write(tails / name, tail(source))
        state: dict[str, object] = {
            "pid": os.getpid(),
            "timestamp": now(),
            "samples": samples,
            "serial_nodes": nodes,
            "transitions": transitions,
            "read_only": True,
            **flags,
        }
        atomic_write(OUTPUT / "recovery-state.json", json.dumps(state, indent=2, sort_keys=True) + "\n")
        atomic_write(OUTPUT / "recovery-progress.md", render(state))
        with (OUTPUT / "recovery-events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(state, sort_keys=True) + "\n")
            stream.flush()
        time.sleep(interval)
    atomic_write(OUTPUT / "recovery-monitor.stopped", f"{now()} pid={os.getpid()}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    if not 0.5 <= args.interval <= 60:
        parser.error("--interval must be between 0.5 and 60 seconds")
    return run(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
