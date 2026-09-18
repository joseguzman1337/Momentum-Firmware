#!/usr/bin/env python3
"""Create an atomic updater resource tree containing verified Marketplace apps."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def _base_timestamp(base: Path) -> int:
    for line in (base / "Manifest").read_text(encoding="utf-8").splitlines():
        if line.startswith("T:"):
            return int(line[2:])
    raise RuntimeError("base resource Manifest has no timestamp")


def bundle(
    base: Path,
    apps: Path,
    destination: Path,
    assets_tool: Path,
    timestamp: int | None = None,
) -> None:
    lock = apps / "marketplace-lock.json"
    report = json.loads(lock.read_text(encoding="utf-8"))
    if not report.get("complete") or report.get("verified_apps") != report.get("catalog_apps"):
        raise RuntimeError("refusing to bundle an incomplete Marketplace synchronization")

    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
    try:
        shutil.copytree(base, stage, dirs_exist_ok=True)
        shutil.rmtree(stage / "apps", ignore_errors=True)
        shutil.copytree(apps, stage / "apps")
        subprocess.run(
            [
                str(assets_tool),
                "manifest",
                str(stage),
                f"--timestamp={timestamp if timestamp is not None else _base_timestamp(base)}",
            ],
            check=True,
        )
        previous = destination.with_name(f".{destination.name}.previous")
        shutil.rmtree(previous, ignore_errors=True)
        if destination.exists():
            os.replace(destination, previous)
        try:
            os.replace(stage, destination)
        except Exception:
            if previous.exists() and not destination.exists():
                os.replace(previous, destination)
            raise
        shutil.rmtree(previous, ignore_errors=True)
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--apps", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--assets-tool", type=Path, required=True)
    parser.add_argument("--timestamp", type=int)
    args = parser.parse_args()
    bundle(
        args.base.resolve(),
        args.apps.resolve(),
        args.destination.resolve(),
        args.assets_tool.resolve(),
        args.timestamp,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
