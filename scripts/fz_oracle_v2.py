#!/usr/bin/env python3
"""Build a sanitized, read-only hardware oracle for the Flipper emulator.

Only public USB descriptors and explicitly allow-listed CLI/RPC reads are used.
Stable identifiers, storage payloads and protected MCU data are never acquired.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "scripts" / "fz_emulator_snapshot.py"
_spec = importlib.util.spec_from_file_location("fz_snapshot", SNAPSHOT_PATH)
snapshot = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(snapshot)

FORBIDDEN = re.compile(r"(?i)(uid|serial|mac|pair|bond|key|token|secret|otp|option.?byte)")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def usb_topology() -> dict[str, object]:
    """Read numeric descriptors only; deliberately never requests USB strings."""
    try:
        import usb.core
    except ImportError:
        return {"available": False, "reason": "pyusb unavailable"}
    device = usb.core.find(idVendor=0x0483, idProduct=0x5740)
    if device is None:
        return {"available": False, "reason": "runtime USB device absent"}
    configurations = []
    for config in device:
        interfaces = []
        for interface in config:
            interfaces.append({
                "number": interface.bInterfaceNumber,
                "alternate": interface.bAlternateSetting,
                "class": interface.bInterfaceClass,
                "subclass": interface.bInterfaceSubClass,
                "protocol": interface.bInterfaceProtocol,
                "endpoints": [{
                    "address": endpoint.bEndpointAddress,
                    "attributes": endpoint.bmAttributes,
                    "max_packet_size": endpoint.wMaxPacketSize,
                    "interval": endpoint.bInterval,
                } for endpoint in interface],
            })
        configurations.append({
            "value": config.bConfigurationValue,
            "attributes": config.bmAttributes,
            "max_power_ma": config.bMaxPower * 2,
            "interfaces": interfaces,
        })
    return {
        "available": True,
        "vendor_id": device.idVendor,
        "product_id": device.idProduct,
        "usb_bcd": device.bcdUSB,
        "device_bcd": device.bcdDevice,
        "class": device.bDeviceClass,
        "subclass": device.bDeviceSubClass,
        "protocol": device.bDeviceProtocol,
        "ep0_max_packet_size": device.bMaxPacketSize0,
        "configurations": configurations,
        "strings_requested": False,
    }


def source_contracts() -> dict[str, object]:
    """Derive public timing and settings layouts from the checked-out firmware."""
    input_c = (ROOT / "applications/services/input/input.c").read_text(errors="replace")
    defines = dict(re.findall(r"^#define\s+(INPUT_[A-Z0-9_]+)\s+([^/\n]+)", input_c, re.M))
    files = {
        "desktop": "applications/services/desktop/desktop_settings.h",
        "expansion": "applications/services/expansion/expansion_settings.h",
        "notification": "applications/services/notification/notification_settings.h",
    }
    settings = {}
    for name, relative in files.items():
        path = ROOT / relative
        text = path.read_text(errors="replace") if path.exists() else ""
        fields = []
        for ctype, field in re.findall(r"^\s*([A-Za-z_][\w\s\*]*?)\s+([A-Za-z_]\w*)(?:\[[^]]+\])?;", text, re.M):
            if not FORBIDDEN.search(field):
                fields.append({"type": " ".join(ctype.split()), "name": field})
        settings[name] = {"source": relative, "fields": fields, "payload_extracted": False}
    return {
        "input": {"source": "applications/services/input/input.c", "defines": {k: v.strip() for k, v in defines.items()}},
        "settings": settings,
    }


def capture(port: str, output: Path, frame_count: int = 3) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    cli_dir = output / "cli"
    cli_dir.mkdir(exist_ok=True)
    transport = snapshot.SerialTransport(port)
    commands = []
    try:
        for command in snapshot.READ_ONLY_COMMANDS:
            started = time.monotonic_ns()
            clean = snapshot.sanitize(transport.command(command))
            elapsed = (time.monotonic_ns() - started) / 1_000_000
            # Sensitive field names are retained as part of the public schema,
            # but every corresponding value must have been replaced.
            for line in clean.splitlines():
                key = line.split(":", 1)[0]
                if snapshot.SECRET_KEYS.search(key) and ":" in line and "<redacted>" not in line:
                    raise RuntimeError(f"sanitizer invariant failed for {command}")
            filename = command.replace(" ", "_").replace("/", "root_") + ".txt"
            payload = clean.encode()
            (cli_dir / filename).write_bytes(payload)
            commands.append({"command": command, "latency_ms": round(elapsed, 3), "sha256": _sha(payload)})
    finally:
        transport.close()

    frames = []
    for index in range(frame_count):
        started = time.monotonic_ns()
        metadata = snapshot.capture_screen_frame(port, output)
        latency = (time.monotonic_ns() - started) / 1_000_000
        raw = output / metadata["file"]
        destination = output / "screen" / f"frame-{index:02d}.bin"
        destination.write_bytes(raw.read_bytes())
        frames.append({"index": index, "latency_ms": round(latency, 3), "bytes": destination.stat().st_size,
                       "sha256": _sha(destination.read_bytes()), "orientation": metadata["orientation"]})

    manifest = {
        "schema": 2,
        "safety": {"device_writes": 0, "device_resets": 0, "device_flashes": 0,
                   "protected_reads": 0, "storage_payloads_read": 0, "usb_strings_requested": 0},
        "rpc": {"screen_stream": {"request_count": frame_count, "frames": frames},
                "persistent_state_changed": False},
        "cli": commands,
        "usb": usb_topology(),
        "contracts": source_contracts(),
    }
    path = output / "oracle-v2.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    parser.add_argument("--output", type=Path, default=Path(".ai/fz-emulator/oracle-v2"))
    parser.add_argument("--frames", type=int, default=3)
    args = parser.parse_args()
    print(capture(args.port, args.output, args.frames))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
