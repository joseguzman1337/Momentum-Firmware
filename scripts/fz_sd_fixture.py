#!/usr/bin/env python3
"""Build a deduplicated, read-only SD fixture from public Flipper paths."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))


ALLOW_ROOTS = ("/ext/apps", "/ext/asset_packs")
DENY = re.compile(r"(?i)(apps_data|\.bt|pair|key|secret|token|uid|serial|dolphin)")
CONTENT_ID = re.compile(
    rb"(?im)^\s*(?:device[_ ]?uid|hardware[_ ]?uid|uid|ble[_ ]?mac|mac[_ ]?address|serial(?: number)?)\s*[:=]\s*(?:[0-9a-f]{2}[\s:-]*){3,}"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def allowed_path(path: str) -> bool:
    pure = PurePosixPath(path)
    return (
        path.startswith(tuple(root + "/" for root in ALLOW_ROOTS))
        and ".." not in pure.parts
        and not DENY.search(path)
    )


def store_blob(output: Path, relative: Path, data: bytes) -> dict[str, object]:
    sha = digest(data)
    blob = output / "blobs" / sha
    blob.parent.mkdir(parents=True, exist_ok=True)
    if not blob.exists():
        blob.write_bytes(data)
    target = output / "tree" / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    try:
        os.link(blob, target)
    except OSError:
        shutil.copyfile(blob, target)
    return {"path": relative.as_posix(), "size": len(data), "sha256": sha}


def snapshot_storage(
    storage,
    output: Path,
    max_file_size: int = 4 * 1024 * 1024,
    max_total_size: int = 64 * 1024 * 1024,
    max_files: int = 4096,
) -> list[dict[str, object]]:
    records = []
    total = 0
    for root in ALLOW_ROOTS:
        for directory, _dirs, files in storage.walk(root):
            for name in files:
                remote = f"{directory.rstrip('/')}/{name}"
                if not allowed_path(remote):
                    continue
                size = storage.size(remote)
                if size > max_file_size:
                    records.append({"path": remote.removeprefix("/ext/"), "size": size, "skipped": "file_cap"})
                    continue
                if len(records) >= max_files or total + size > max_total_size:
                    raise RuntimeError("SD fixture safety cap exceeded")
                data = bytes(storage.read_file(remote))
                if len(data) != size:
                    raise IOError(f"size mismatch for {remote}: expected {size}, got {len(data)}")
                records.append(store_blob(output, Path(remote.removeprefix("/ext/")), data))
                total += size
    return records


def add_update_resources(output: Path, archive: Path) -> list[dict[str, object]]:
    if not archive.is_file():
        return []
    records = [store_blob(output, Path("update_resources/resources.tar.gz"), archive.read_bytes())]
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            if not member.isfile():
                continue
            pure = PurePosixPath(member.name)
            if (
                pure.is_absolute()
                or ".." in pure.parts
                or DENY.search(member.name)
                or pure.name.casefold() == "manifest"
            ):
                continue
            if member.size > 4 * 1024 * 1024:
                continue
            stream = bundle.extractfile(member)
            if stream is None:
                continue
            data = stream.read()
            if CONTENT_ID.search(data):
                continue
            records.append(store_blob(output, Path("update_resources/extracted") / Path(*pure.parts), data))
    return records


def main() -> int:
    from flipper.storage import FlipperStorage

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    parser.add_argument("--output", type=Path, default=Path(".ai/fz-emulator/sd-fixture"))
    parser.add_argument("--resources", type=Path)
    parser.add_argument("--max-file-mib", type=int, default=4)
    parser.add_argument("--max-total-mib", type=int, default=64)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with FlipperStorage(args.port) as storage:
        records = snapshot_storage(
            storage,
            args.output,
            args.max_file_mib * 1024 * 1024,
            args.max_total_mib * 1024 * 1024,
        )
    if args.resources:
        records.extend(add_update_resources(args.output, args.resources))
    manifest = {
        "schema": 1,
        "source_roots": list(ALLOW_ROOTS),
        "excluded": ["/ext/apps_data", "user files", "keys", "pairing", "dolphin", "BT settings", "option bytes", "unique IDs"],
        "device_writes": 0,
        "files": sorted(records, key=lambda item: str(item["path"])),
    }
    manifest["total_bytes"] = sum(int(item["size"]) for item in records if "sha256" in item)
    manifest["unique_blobs"] = len({item["sha256"] for item in records if "sha256" in item})
    manifest_path = args.output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
