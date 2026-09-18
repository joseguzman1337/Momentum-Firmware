#!/usr/bin/env python3
"""Create an atomic updater resource tree containing verified Marketplace apps."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

try:
    from fbt_tools.fbt_resources import _fim_text, _normalize_png
except ModuleNotFoundError:  # imported as scripts.bundle_marketplace_resources in tests/tools
    from scripts.fbt_tools.fbt_resources import _fim_text, _normalize_png


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
    if (
        not report.get("complete")
        or report.get("verified_apps") != report.get("catalog_apps")
        or len(report.get("apps", ())) != report.get("verified_apps")
    ):
        raise RuntimeError("refusing to bundle an incomplete Marketplace synchronization")

    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
    try:
        shutil.copytree(base, stage, dirs_exist_ok=True)
        shutil.rmtree(stage / "apps", ignore_errors=True)
        shutil.copytree(apps, stage / "apps")
        manifests = stage / "apps_manifests"
        shutil.rmtree(manifests, ignore_errors=True)
        manifests.mkdir()
        aliases: set[str] = set()
        application_ids: set[str] = set()
        version_ids: set[str] = set()
        for app in report["apps"]:
            alias = app["alias"]
            application_id = app["application_id"]
            version_id = app["version_id"]
            name = app["name"]
            if not re.fullmatch(r"[a-z0-9_]+", alias):
                raise RuntimeError(f"invalid Marketplace manifest alias: {alias}")
            if alias in aliases:
                raise RuntimeError(f"duplicate Marketplace manifest alias: {alias}")
            if not re.fullmatch(r"[0-9a-f]{24}", application_id):
                raise RuntimeError(f"invalid Marketplace application ID for {alias}")
            if not re.fullmatch(r"[0-9a-f]{24}", version_id):
                raise RuntimeError(f"invalid Marketplace version ID for {alias}")
            if application_id in application_ids or version_id in version_ids:
                raise RuntimeError(f"duplicate Marketplace identity for {alias}")
            if not name or "\n" in name or "\r" in name:
                raise RuntimeError(f"invalid Marketplace application name for {alias}")
            aliases.add(alias)
            application_ids.add(application_id)
            version_ids.add(version_id)
            fap = stage / "apps" / Path(app["path"])
            if not fap.is_file() or not fap.resolve().is_relative_to((stage / "apps").resolve()):
                raise RuntimeError(f"Marketplace manifest has no staged FAP for {alias}")
            icon = _normalize_png(base64.b64decode(app["icon"], validate=True))
            manifest = _fim_text(
                name=name,
                icon=icon,
                api=report["api"],
                uid=application_id,
                version_uid=version_id,
                path=f"/ext/apps/{app['path']}",
            )
            (manifests / f"{alias}.fim").write_text(manifest, encoding="utf-8", newline="\n")
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
