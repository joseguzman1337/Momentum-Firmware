#!/usr/bin/env python3

import argparse
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "flipper"))

from storage import FlipperStorage, StorageErrorCode  # noqa: E402


def find_flipper_port():
    import glob

    patterns = [
        "/dev/ttyACM*",
        "/dev/serial/by-id/*Flipper*",
        "/dev/cu.usbmodem*",
    ]
    for pattern in patterns:
        ports = glob.glob(pattern)
        if ports:
            return ports[0]
    return None


def wait_for_port(timeout: int):
    deadline = time.time() + max(0, timeout)
    while True:
        port = find_flipper_port()
        if port:
            return port
        if time.time() >= deadline:
            return None
        time.sleep(1)


def stat_ext(storage: FlipperStorage) -> StorageErrorCode:
    storage.send_and_wait_eol('storage stat "/ext"\r')
    response = storage.read.until(storage.CLI_EOL)
    storage.read.until(storage.CLI_PROMPT)
    if storage.has_error(response):
        return storage.get_error(response)
    return StorageErrorCode.OK


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default="auto", help="Flipper serial port")
    parser.add_argument("--wait", action="store_true", help="Wait for Flipper port")
    parser.add_argument("--timeout", type=int, default=30, help="Wait timeout (sec)")
    parser.add_argument(
        "--format-if-missing",
        action="store_true",
        help="Format /ext if missing or not ready (destructive)",
    )
    args = parser.parse_args()

    if args.port == "auto":
        port = wait_for_port(args.timeout) if args.wait else find_flipper_port()
    else:
        port = args.port

    if not port:
        print("ERROR: Flipper serial port not found", file=sys.stderr)
        return 1

    with FlipperStorage(port) as storage:
        status = stat_ext(storage)
        if status == StorageErrorCode.OK:
            print("OK: /ext is available")
            return 0

        if args.format_if_missing:
            print(f"INFO: /ext status is '{status.value}', formatting /ext...")
            storage.format_ext()
            status = stat_ext(storage)
            if status == StorageErrorCode.OK:
                print("OK: /ext formatted and available")
                return 0

        print(f"ERROR: /ext not available ({status.value})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
