#!/usr/bin/env python3
"""Read-only USB and flash-log observer.

The observer never opens a serial device and never invokes a flashing tool.  It
only enumerates device nodes/USB metadata and copies bounded tails of existing
logs into a timestamped history directory.
"""

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
DEFAULT_OUTPUT = ROOT / ".ai" / "logs" / "flash-session"
WATCH_ROOTS = (
    ROOT / ".ai" / "logs" / "esp_mcp",
    ROOT / ".ai" / "logs" / "strawberry_mcp",
    ROOT / ".ai" / "esp_projects",
)
SERIAL_PATTERNS = (
    "/dev/cu.usb*",
    "/dev/tty.usb*",
    "/dev/cu.wchusb*",
    "/dev/cu.SLAB_USBtoUART*",
)
MAX_USB_BYTES = 512 * 1024
MAX_LOG_TAIL = 128 * 1024


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def serial_nodes() -> list[str]:
    return sorted({node for pattern in SERIAL_PATTERNS for node in glob.glob(pattern)})


def usb_snapshot() -> str:
    try:
        result = subprocess.run(
            ["ioreg", "-r", "-c", "IOUSBHostDevice", "-l", "-w0"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=8,
            check=False,
        )
        data = result.stdout[:MAX_USB_BYTES]
        return data.decode("utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError) as error:
        return f"ioreg unavailable: {type(error).__name__}: {error}\n"


def watched_logs(output: Path) -> list[Path]:
    found: list[Path] = []
    for base in WATCH_ROOTS:
        if not base.exists():
            continue
        for path in base.rglob("*.log"):
            try:
                path.relative_to(output)
            except ValueError:
                found.append(path)
    return sorted(found)


def bounded_tail(path: Path) -> bytes:
    with path.open("rb") as stream:
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(max(0, size - MAX_LOG_TAIL))
        return stream.read(MAX_LOG_TAIL)


def markdown(state: dict[str, object]) -> str:
    devices = state["serial_nodes"] or ["none detected"]
    changed = state["changed_logs"]
    files = list(changed[:12]) if changed else ["none"]
    if len(changed) > 12:
        files.append(f"... and {len(changed) - 12} more (see state.json)")
    return "\n".join(
        [
            "# Flash session monitor",
            "",
            "| Item | Current state |",
            "|---|---|",
            f"| Observer | running (read-only), PID `{state['pid']}` |",
            f"| Last snapshot (UTC) | `{state['timestamp']}` |",
            f"| Samples | `{state['samples']}` |",
            f"| Serial device nodes | {'<br>'.join(f'`{item}`' for item in devices)} |",
            f"| USB snapshot | `{state['usb_file']}` |",
            f"| Logs changed in last sample | {'<br>'.join(f'`{item}`' for item in files)} |",
            "| Device access | never opened; enumeration only |",
            "| Flash/reset writes | none |",
            "",
            "The monitor reports observations only. Detection is not proof that flashing has started or succeeded.",
            "",
        ]
    )


def run(interval: float, output: Path, once: bool) -> int:
    output.mkdir(parents=True, exist_ok=True)
    history = output / "history"
    tails = output / "tails"
    history.mkdir(exist_ok=True)
    tails.mkdir(exist_ok=True)
    stop = False

    def request_stop(_signum: int, _frame: object) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    atomic_write(output / "monitor.pid", f"{os.getpid()}\n")
    known: dict[str, tuple[int, int]] = {}
    samples = 0
    try:
        while not stop:
            samples += 1
            stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            usb_text = usb_snapshot()
            usb_name = f"usb-{stamp}-{samples:06d}.txt"
            atomic_write(history / usb_name, usb_text)
            nodes = serial_nodes()
            changed: list[str] = []
            for path in watched_logs(output):
                try:
                    stat = path.stat()
                    marker = (stat.st_mtime_ns, stat.st_size)
                    key = str(path.relative_to(ROOT))
                    if known.get(key) != marker:
                        known[key] = marker
                        changed.append(key)
                        safe_name = key.replace("/", "__")
                        (tails / safe_name).write_bytes(bounded_tail(path))
                except OSError:
                    continue
            state: dict[str, object] = {
                "pid": os.getpid(),
                "timestamp": utc_now(),
                "samples": samples,
                "serial_nodes": nodes,
                "usb_file": f"history/{usb_name}",
                "changed_logs": changed,
                "read_only": True,
            }
            atomic_write(output / "state.json", json.dumps(state, indent=2, sort_keys=True) + "\n")
            atomic_write(output / "progress.md", markdown(state))
            with (output / "events.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(state, sort_keys=True) + "\n")
            if once:
                break
            time.sleep(interval)
    finally:
        atomic_write(output / "monitor.stopped", f"{utc_now()} pid={os.getpid()}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=float, default=3.0)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if not 0.5 <= args.interval <= 3600:
        parser.error("--interval must be between 0.5 and 3600 seconds")
    return run(args.interval, args.output.resolve(), args.once)


if __name__ == "__main__":
    raise SystemExit(main())
