#!/usr/bin/env python3
"""
Robust resource transfer to Flipper Zero.

Improvements over the default storage.py send:
  - Larger chunk size (64 KB) → 8× fewer FATFS open/close cycles, less
    chance of cluster-allocation errors corrupting the file mid-write.
  - Per-file retry with reconnect on any failure.
  - Size-based skip: files whose remote size already matches the local
    file are skipped without re-sending.
  - Errors from mid-write FATFS failures are detected and retried.
"""

import logging
import os
import sys
import time

# Allow running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from flipper.storage import FlipperStorage, FlipperStorageException, FlipperStorageOperations

PORT = os.environ.get("FBT_FLIPPER_PORT", "/dev/ttyACM0")
RESOURCES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "build", "f7-firmware-C", "resources"
)
CHUNK_SIZE = 65536   # 64 KB — 8× larger than default, far fewer open/close cycles
MAX_RETRIES = 5
RETRY_DELAY = 3      # seconds between retries

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("push_resources")


def make_storage():
    s = FlipperStorage(PORT, chunk_size=CHUNK_SIZE)
    s.start()
    return s


def send_one_file(storage, local_path, remote_path):
    """Send a single file; raises FlipperStorageException on failure."""
    local_size = os.path.getsize(local_path)

    # Skip if remote already has the correct size
    try:
        remote_size = storage.size(remote_path)
        if remote_size == local_size:
            return False  # skipped
    except FlipperStorageException:
        pass  # file doesn't exist or stat failed → send it

    storage.send_file(local_path, remote_path)
    return True  # sent


def ensure_remote_dir(storage, remote_dir):
    ops = FlipperStorageOperations(storage)
    try:
        ops.mkpath(remote_dir)
    except FlipperStorageException:
        pass


def run():
    resources_dir = os.path.normpath(RESOURCES_DIR)
    if not os.path.isdir(resources_dir):
        log.error(f"Resources directory not found: {resources_dir}")
        sys.exit(1)

    # Collect all files
    all_files = []
    for root, dirs, files in os.walk(resources_dir):
        dirs.sort()
        for fname in sorted(files):
            local_path = os.path.join(root, fname)
            rel = os.path.relpath(local_path, resources_dir).replace(os.sep, "/")
            remote_path = "/ext/" + rel
            all_files.append((local_path, remote_path))

    total = len(all_files)
    log.info(f"Found {total} resource files to sync")

    storage = make_storage()
    sent = skipped = failed_count = 0
    failed_files = []

    for idx, (local_path, remote_path) in enumerate(all_files, 1):
        rel = os.path.relpath(local_path, resources_dir).replace(os.sep, "/")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Ensure parent directory exists
                remote_dir = posixpath_dirname(remote_path)
                ensure_remote_dir(storage, remote_dir)

                transferred = send_one_file(storage, local_path, remote_path)
                if transferred:
                    log.info(f"[{idx}/{total}] OK  {rel}")
                    sent += 1
                else:
                    log.debug(f"[{idx}/{total}] SKIP (same size) {rel}")
                    skipped += 1
                break

            except (FlipperStorageException, TimeoutError, OSError, Exception) as exc:
                log.warning(f"[{idx}/{total}] Attempt {attempt}/{MAX_RETRIES} failed for {rel}: {exc}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    # Reconnect the serial session
                    try:
                        storage.stop()
                    except Exception:
                        pass
                    time.sleep(1)
                    try:
                        storage = make_storage()
                    except Exception as conn_err:
                        log.error(f"Reconnect failed: {conn_err}")
                        time.sleep(RETRY_DELAY)
                else:
                    log.error(f"[{idx}/{total}] FAILED {rel}")
                    failed_count += 1
                    failed_files.append(rel)

    try:
        storage.stop()
    except Exception:
        pass

    log.info(f"\nDone — sent: {sent}, skipped: {skipped}, failed: {failed_count}")
    if failed_files:
        log.error("Failed files:")
        for f in failed_files:
            log.error(f"  {f}")
        sys.exit(1)


def posixpath_dirname(path):
    """posixpath.dirname without importing posixpath at top level."""
    idx = path.rfind("/")
    return path[:idx] if idx > 0 else "/"


if __name__ == "__main__":
    run()
