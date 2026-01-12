#!/usr/bin/env python3

import sys


def reset_flipper() -> int:
    try:
        import usb.core
        import usb.util
    except Exception as exc:
        print(f"[usbreset] pyusb unavailable: {exc}")
        return 1

    dev = usb.core.find(idVendor=0x0483, idProduct=0x5740)
    if dev is None:
        print("[usbreset] Flipper USB device not found")
        return 1

    try:
        usb.util.dispose_resources(dev)
        dev.reset()
        print("[usbreset] Flipper USB device reset")
        return 0
    except Exception as exc:
        print(f"[usbreset] Reset failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(reset_flipper())
