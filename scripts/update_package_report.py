#!/usr/bin/env python3
"""Produce a deterministic, machine-readable updater release audit."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from update import Main as UpdateMain  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest(path: Path) -> dict[str, str]:
    fields = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and ": " in line:
            key, value = line.split(": ", 1)
            fields[key] = value
    return fields


def little_endian_hex(value: str) -> int:
    return int.from_bytes(bytes.fromhex(value), "little")


def audit(package: Path) -> dict:
    fields = manifest(package / UpdateMain.UPDATE_MANIFEST_NAME)
    required = ("Loader", "Firmware", "Radio", "Resources")
    missing = [name for name in required if not fields.get(name)]
    if missing:
        raise ValueError(f"manifest missing package members: {', '.join(missing)}")
    members = sorted(
        {fields[name] for name in required} | {UpdateMain.UPDATE_MANIFEST_NAME}
    )
    absent = [name for name in members if not (package / name).is_file()]
    if absent:
        raise ValueError(f"package members not found: {', '.join(absent)}")

    fw_start, fw_end = UpdateMain.dfu_flash_range(package / fields["Firmware"])
    radio_address = little_endian_hex(fields["Radio address"])
    headroom = radio_address - fw_end
    minimum = UpdateMain.MIN_GAP_PAGES * UpdateMain.FLASH_PAGE_SIZE
    files = {
        name: {
            "bytes": (package / name).stat().st_size,
            "sha256": sha256(package / name),
        }
        for name in members
    }
    return {
        "schema": 1,
        "package": package.name,
        "version": fields.get("Info", ""),
        "target": fields.get("Target", ""),
        "firmware": {
            "start": f"0x{fw_start:08X}",
            "end_exclusive": f"0x{fw_end:08X}",
            "radio_address": f"0x{radio_address:08X}",
            "headroom_bytes": headroom,
            "required_headroom_bytes": minimum,
            "layout_ready": headroom >= minimum,
        },
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    report = audit(args.package.resolve())
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return int(args.require_ready and not report["firmware"]["layout_ready"])


if __name__ == "__main__":
    raise SystemExit(main())
