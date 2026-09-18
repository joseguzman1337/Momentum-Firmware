#!/usr/bin/env python3
"""Fetch hash-verified FAPs directly from the official Flipper Apps Catalog.

This tool never communicates with a Flipper Zero.  It only creates an atomic,
verified staging tree which a separate deployment step may copy to the device.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path


CATALOG_ORIGIN = "https://catalog.flipperzero.one"
API_ROOT = f"{CATALOG_ORIGIN}/api/v0"
USER_AGENT = "Momentum-Firmware-Official-Marketplace-Sync/1.0"


def fetch(url: str, *, timeout: int = 30) -> bytes:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "catalog.flipperzero.one" or parsed.username or parsed.password or parsed.port:
        raise RuntimeError(f"refusing non-official catalog URL: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        final = urllib.parse.urlsplit(response.geturl())
        if final.scheme != "https" or final.hostname != "catalog.flipperzero.one" or final.username or final.password or final.port:
            raise RuntimeError(f"catalog redirected outside official origin: {response.geturl()}")
        return response.read()


def fetch_json(url: str) -> object:
    return json.loads(fetch(url).decode("utf-8"))


def catalog_apps(*, page_size: int = 500) -> list[dict]:
    result: list[dict] = []
    offset = 0
    while True:
        query = urllib.parse.urlencode(
            {
                "limit": page_size,
                "offset": offset,
                "is_latest_release_version": "true",
            }
        )
        page = fetch_json(f"{API_ROOT}/0/application?{query}")
        if not isinstance(page, list):
            raise RuntimeError("official catalog returned a non-list application response")
        result.extend(page)
        if len(page) < page_size:
            if not result:
                raise RuntimeError("official catalog returned no applications")
            ids = [app.get("_id") for app in result]
            if any(not item for item in ids) or len(ids) != len(set(ids)):
                raise RuntimeError("official catalog returned missing or duplicate application IDs")
            return sorted(result, key=lambda app: app.get("alias", ""))
        offset += len(page)


def category_map() -> dict[str, str]:
    categories = fetch_json(f"{API_ROOT}/category")
    if not isinstance(categories, list):
        raise RuntimeError("official catalog returned a non-list category response")
    return {item["_id"]: item["name"] for item in categories}


def compatible_fap(app: dict, *, target: str, api: str) -> tuple[bytes, dict]:
    alias = app["alias"]
    application_id = app.get("_id")
    version = app.get("current_version") or {}
    version_id = version.get("_id")
    name = version.get("name")
    build = version.get("current_build") or {}
    expected_hash = build.get("fap_hash")
    if not re.fullmatch(r"[0-9a-f]{24}", application_id or ""):
        raise RuntimeError(f"{alias}: catalog application ID is invalid")
    if not re.fullmatch(r"[0-9a-f]{24}", version_id or ""):
        raise RuntimeError(f"{alias}: catalog version ID is invalid")
    if not name:
        raise RuntimeError(f"{alias}: catalog version has no name")
    if not expected_hash:
        raise RuntimeError(f"{alias}: catalog has no ready release build")
    query = urllib.parse.urlencode({"target": target, "api": api})
    url = f"{API_ROOT}/application/version/{version_id}/build/compatible?{query}"
    payload = fetch(url)
    actual_hash = hashlib.sha256(payload).hexdigest()
    if actual_hash != expected_hash:
        raise RuntimeError(
            f"{alias}: SHA-256 mismatch: expected {expected_hash}, got {actual_hash}"
        )
    if not payload.startswith(b"\x7fELF"):
        raise RuntimeError(f"{alias}: compatible build is not an ELF/FAP")
    icon_uri = version.get("icon_uri")
    if not icon_uri:
        raise RuntimeError(f"{alias}: catalog version has no icon")
    icon = fetch(icon_uri)
    if not icon.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(f"{alias}: catalog icon is not a PNG")
    return payload, {
        "alias": alias,
        "application_id": application_id,
        "name": name,
        "version": version.get("version"),
        "version_id": version_id,
        "icon": base64.b64encode(icon).decode("ascii"),
        "sha256": actual_hash,
        "source": url,
    }


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def safe_relative_path(category: str, alias: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 +_.-]*", category):
        raise RuntimeError(f"unsafe catalog category: {category!r}")
    if not re.fullmatch(r"[a-z0-9_]+", alias):
        raise RuntimeError(f"unsafe catalog alias: {alias!r}")
    return Path(category) / f"{alias}.fap"


def sync(
    destination: Path,
    *,
    target: str,
    api: str,
    base: Path | None = None,
    limit: int | None = None,
) -> dict:
    apps = catalog_apps()
    confirmation = catalog_apps()
    inventory = tuple((app.get("_id"), app.get("current_version", {}).get("_id")) for app in apps)
    confirmed_inventory = tuple(
        (app.get("_id"), app.get("current_version", {}).get("_id")) for app in confirmation
    )
    if inventory != confirmed_inventory:
        raise RuntimeError("official catalog changed during inventory; retry synchronization")
    if limit is not None:
        apps = apps[:limit]
    categories = category_map()
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
    if base is not None:
        if not base.is_dir():
            shutil.rmtree(stage)
            raise RuntimeError(f"bundled app tree does not exist: {base}")
        shutil.copytree(base, stage, dirs_exist_ok=True)
    receipts: list[dict] = []
    failures: list[dict] = []
    output_paths: set[str] = set()
    for app in apps:
        alias = app.get("alias", "<unknown>")
        try:
            category = categories[app["category_id"]]
            payload, receipt = compatible_fap(app, target=target, api=api)
            relative = safe_relative_path(category, alias)
            normalized = relative.as_posix().casefold()
            if normalized in output_paths:
                raise RuntimeError(f"duplicate catalog output path: {relative}")
            output_paths.add(normalized)
            candidate = (stage / relative).resolve()
            if not candidate.is_relative_to(stage.resolve()):
                raise RuntimeError(f"catalog path escapes staging tree: {relative}")
            atomic_write(candidate, payload)
            receipt["path"] = relative.as_posix()
            receipts.append(receipt)
        except Exception as error:  # keep a complete fail-closed audit
            failures.append({"alias": alias, "error": str(error)})

    report = {
        "schema": 1,
        "official_origin": CATALOG_ORIGIN,
        "target": target,
        "api": api,
        "catalog_apps": len(apps),
        "verified_apps": len(receipts),
        "failed_apps": failures,
        "apps": receipts,
        "complete": len(receipts) == len(apps) and not failures,
    }
    if not report["complete"]:
        shutil.rmtree(stage)
        details = "; ".join(f"{item['alias']}: {item['error']}" for item in failures)
        raise RuntimeError(
            f"official marketplace sync incomplete: {len(failures)} app(s) failed: {details}"
        )
    atomic_write(stage / "marketplace-lock.json", (json.dumps(report, indent=2, sort_keys=True) + "\n").encode())
    backup = destination.with_name(f".{destination.name}.previous")
    if backup.exists():
        shutil.rmtree(backup)
    if destination.exists():
        os.replace(destination, backup)
    try:
        os.replace(stage, destination)
    except Exception:
        if backup.exists() and not destination.exists():
            os.replace(backup, destination)
        raise
    if backup.exists():
        shutil.rmtree(backup)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, default=Path("build/official-marketplace/apps"))
    parser.add_argument("--target", default="f7")
    parser.add_argument("--base", type=Path, help="bundled app tree to merge before official apps")
    api_group = parser.add_mutually_exclusive_group(required=True)
    api_group.add_argument("--api")
    api_group.add_argument("--api-file", type=Path)
    parser.add_argument("--limit", type=int, help="test only: process the first N catalog apps")
    args = parser.parse_args()
    api = args.api
    if args.api_file:
        first_data_line = args.api_file.read_text(encoding="utf-8").splitlines()[1]
        fields = first_data_line.split(",")
        if len(fields) < 3 or fields[0] != "Version":
            raise RuntimeError(f"cannot read API version from {args.api_file}")
        api = fields[2]
    report = sync(
        args.destination.resolve(),
        target=args.target,
        api=api,
        base=args.base.resolve() if args.base else None,
        limit=args.limit,
    )
    print(json.dumps({key: report[key] for key in ("complete", "catalog_apps", "verified_apps", "target", "api")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
