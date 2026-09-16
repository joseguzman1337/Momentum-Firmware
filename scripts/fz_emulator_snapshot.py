#!/usr/bin/env python3
"""Capture a sanitized, read-only Flipper Zero profile for emulation.

The command allow-list intentionally excludes every CLI operation capable of
writing storage, changing GPIO, resetting, updating, or starting an app.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol


READ_ONLY_COMMANDS = (
    "device_info",
    "storage info /int",
    "storage info /ext",
    "storage list /int",
    "storage list /ext",
    "storage tree /ext/apps",
    "storage tree /ext/asset_packs",
    "storage tree /ext/update",
    "storage md5 /int/.notification.settings",
    "storage md5 /int/.expansion.settings",
    "storage md5 /int/.desktop.settings",
    "storage md5 /int/.region_data",
    "storage md5 /int/.momentum_firstboot.flag",
    "uptime",
    "free",
)

SECRET_KEYS = re.compile(
    r"(?i)(uid|serial|\bsn\b|mac|name|label|timestamp|signature|pair|key|token|secret)"
)
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
DEVICE_PROMPT = re.compile(r"(?m)^>:\s*$")


class Transport(Protocol):
    def command(self, command: str) -> str: ...
    def close(self) -> None: ...


class SerialTransport:
    def __init__(self, port: str, baudrate: int = 115200) -> None:
        import serial

        self._serial = serial.Serial(port, baudrate, timeout=0.15)
        self._serial.reset_input_buffer()
        self._serial.write(b"\r")
        self._read_until_prompt(2.0)

    def _read_until_prompt(self, timeout: float) -> str:
        end = time.monotonic() + timeout
        data = bytearray()
        while time.monotonic() < end:
            data.extend(self._serial.read(65536))
            text = ANSI.sub("", data.decode("utf-8", errors="replace"))
            if DEVICE_PROMPT.search(text):
                return text
        raise TimeoutError("Flipper CLI prompt was not received")

    def command(self, command: str) -> str:
        if command not in READ_ONLY_COMMANDS:
            raise ValueError(f"command is not in the read-only allow-list: {command}")
        self._serial.reset_input_buffer()
        self._serial.write((command + "\r").encode("ascii"))
        return self._read_until_prompt(15.0)

    def close(self) -> None:
        self._serial.close()


def sanitize(text: str) -> str:
    """Remove stable identifiers while preserving hardware/emulator fields."""
    text = ANSI.sub("", text).replace("\r", "")
    result = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped in READ_ONLY_COMMANDS or stripped == ">:":
            continue
        if ":" in line:
            key, _value = line.split(":", 1)
            if SECRET_KEYS.search(key):
                line = f"{key}: <redacted>"
        # Device names can also occur in storage-info prose.
        line = re.sub(r"(?i)^(Label:\s*).+$", r"\1<redacted>", line)
        line = re.sub(r"(?i)^(SN:\s*).+$", r"\1<redacted>", line)
        result.append(line.rstrip())
    return "\n".join(result).strip() + "\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_artifact_name(path: Path) -> str:
    name = path.name
    if re.search(r"(?i)(backup|asch|serial|uid)", name):
        suffixes = "".join(path.suffixes)
        return f"<redacted>{suffixes}"
    return name


def parse_update_metadata(path: Path) -> dict[str, str]:
    allowed = {
        "Filetype",
        "Version",
        "Info",
        "Target",
        "Loader",
        "Firmware",
        "Radio",
        "Radio address",
        "Radio version",
        "Resources",
        "Splashscreen",
    }
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key in allowed:
            result[key] = value.strip()
    return result


def decode_varint(data: bytes | bytearray, offset: int = 0) -> tuple[int, int]:
    value = 0
    for shift in range(0, 70, 7):
        if offset >= len(data):
            raise ValueError("incomplete varint")
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
    raise ValueError("oversized varint")


def protobuf_fields(data: bytes) -> list[tuple[int, int, int | bytes]]:
    fields = []
    offset = 0
    while offset < len(data):
        tag, offset = decode_varint(data, offset)
        field, wire = tag >> 3, tag & 7
        if wire == 0:
            value, offset = decode_varint(data, offset)
        elif wire == 2:
            size, offset = decode_varint(data, offset)
            value = data[offset : offset + size]
            if len(value) != size:
                raise ValueError("truncated protobuf field")
            offset += size
        else:
            raise ValueError(f"unsupported protobuf wire type {wire}")
        fields.append((field, wire, value))
    return fields


def capture_screen_frame(port: str, output: Path) -> dict[str, object]:
    """Capture one GUI ScreenStream frame and cleanly stop the stream/session."""
    import serial

    stream = serial.Serial(port, 115200, timeout=0.1)
    buffer = bytearray()
    frame_data = None
    orientation = 0
    try:
        stream.reset_input_buffer()
        stream.write(b"\r")
        time.sleep(0.2)
        stream.read(65536)
        stream.write(b"start_rpc_session\r")
        time.sleep(0.2)
        stream.read(65536)  # command echo only; RPC now owns the channel

        # Delimited PB.Main(command_id=1, gui_start_screen_stream_request={}).
        stream.write(bytes.fromhex("05 08 01 A2 01 00"))
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline and frame_data is None:
            buffer.extend(stream.read(65536))
            while buffer:
                try:
                    size, header_end = decode_varint(buffer)
                except ValueError:
                    break
                if len(buffer) < header_end + size:
                    break
                message = bytes(buffer[header_end : header_end + size])
                del buffer[: header_end + size]
                for field, wire, value in protobuf_fields(message):
                    if field != 22 or wire != 2 or not isinstance(value, bytes):
                        continue
                    for nested_field, nested_wire, nested_value in protobuf_fields(value):
                        if nested_field == 1 and nested_wire == 2:
                            frame_data = bytes(nested_value)
                        elif nested_field == 2 and nested_wire == 0:
                            orientation = int(nested_value)
        if frame_data is None:
            raise TimeoutError("RPC ScreenStream did not return a framebuffer")

        fixture = output / "screen"
        fixture.mkdir(parents=True, exist_ok=True)
        raw_path = fixture / "framebuffer-128x64-1bpp.bin"
        raw_path.write_bytes(frame_data)
        metadata = {
            "captured": True,
            "transport": "RPC ScreenStream",
            "width": 128,
            "height": 64,
            "format": "Flipper canvas native 1bpp",
            "bytes": len(frame_data),
            "orientation": orientation,
            "sha256": sha256(raw_path),
            "file": str(raw_path.relative_to(output)),
        }
        (fixture / "framebuffer.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return metadata
    finally:
        # Delimited PB.Main(command_id=2, gui_stop_screen_stream_request={}).
        try:
            stream.write(bytes.fromhex("05 08 02 AA 01 00"))
            time.sleep(0.1)
            stream.read(65536)
        finally:
            stream.close()


def usb_descriptor_profile() -> dict[str, object]:
    output = subprocess.run(
        ["ioreg", "-p", "IOUSB", "-l", "-w0"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    block_match = re.search(r"Flipper .*?(?=\n\s*[+|]---o|\Z)", output, re.S)
    block = block_match.group(0) if block_match else ""
    def number(key: str) -> int | None:
        match = re.search(rf'"{re.escape(key)}"\s*=\s*(\d+)', block)
        return int(match.group(1)) if match else None
    return {
        "vendor_id": number("idVendor"),
        "product_id": number("idProduct"),
        "device_class": number("bDeviceClass"),
        "device_subclass": number("bDeviceSubClass"),
        "configurations": number("bNumConfigurations"),
        "link_speed_bps": number("UsbLinkSpeed"),
        "vendor": "Flipper Devices Inc." if "Flipper Devices Inc." in block else None,
        "serial": "<redacted>",
        "product_name": "Flipper <redacted>",
    }


def capture(
    transport: Transport,
    output: Path,
    artifact_paths: list[Path],
    screen: dict[str, object] | None = None,
) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    command_dir = output / "cli"
    command_dir.mkdir(exist_ok=True)
    ledger = []
    for command in READ_ONLY_COMMANDS:
        payload = sanitize(transport.command(command))
        filename = command.replace(" ", "_").replace("/", "root_") + ".txt"
        path = command_dir / filename
        path.write_text(payload, encoding="utf-8")
        ledger.append({"command": command, "mode": "read-only", "sha256": sha256(path)})

    artifacts = []
    update_metadata = None
    for path in artifact_paths:
        if path.is_file():
            artifacts.append(
                {"name": safe_artifact_name(path), "size": path.stat().st_size, "sha256": sha256(path)}
            )
            if path.name == "update.fuf":
                update_metadata = parse_update_metadata(path)

    manifest = {
        "schema": 1,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "safety": {
            "device_writes": 0,
            "device_resets": 0,
            "device_flashes": 0,
            "identifiers_redacted": True,
            "storage_contents_downloaded": False,
        },
        "commands": ledger,
        "usb": usb_descriptor_profile(),
        "local_firmware_artifacts": artifacts,
        "firmware_package": update_metadata,
        "screen": screen or {"captured": False, "reason": "screen capture skipped"},
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    parser.add_argument("--output", type=Path, default=Path(".ai/fz-emulator/snapshot"))
    parser.add_argument("--artifact", action="append", type=Path, default=[])
    parser.add_argument("--skip-screen", action="store_true")
    args = parser.parse_args()
    transport = SerialTransport(args.port)
    try:
        manifest = capture(transport, args.output, args.artifact)
    finally:
        transport.close()
    if not args.skip_screen:
        screen = capture_screen_frame(args.port, args.output)
        # Rewrite manifest with the already-captured CLI files and screen metadata.
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["screen"] = screen
        manifest.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
