#!/usr/bin/env python3

import argparse
import time


def find_ports():
    import glob

    patterns = (
        "/dev/serial/by-id/*Flipper*",
        "/dev/ttyACM*",
        "/dev/cu.usbmodem*",
    )
    seen = set()
    for pattern in patterns:
        for port in glob.glob(pattern):
            if port not in seen:
                seen.add(port)
                yield port


def set_usb_mode(port: str, mode: str) -> int:
    try:
        from flipperzero import FlipperZero

        flipper = FlipperZero(port=port)
        flipper.connect()
        flipper.cli_send(f"storage write /int/.system/usb.mode {mode}")
        time.sleep(0.3)
        flipper.cli_send("power reboot")
        flipper.disconnect()
        return 0
    except Exception:
        pass

    try:
        import serial

        for baud in (115200, 230400):
            try:
                ser = serial.Serial(port, baud, timeout=2, write_timeout=2)
                time.sleep(0.5)
                ser.read(ser.in_waiting or 1024)
                ser.write(b"\r\n")
                time.sleep(0.2)
                ser.write(f"storage write /int/.system/usb.mode {mode}\r\n".encode("ascii"))
                time.sleep(0.3)
                ser.write(b"power reboot\r\n")
                time.sleep(0.3)
                ser.close()
                return 0
            except Exception:
                try:
                    ser.close()
                except Exception:
                    pass
        return 1
    except Exception:
        return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="usb_serial")
    parser.add_argument("-p", "--port", default="auto")
    args = parser.parse_args()

    ports = [args.port] if args.port != "auto" else list(find_ports())
    if not ports:
        return 1
    for port in ports:
        for _ in range(3):
            if set_usb_mode(port, args.mode) == 0:
                return 0
            time.sleep(0.5)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
