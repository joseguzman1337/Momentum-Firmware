#!/usr/bin/env python3

import os
import subprocess
import sys


def reset_flipper() -> int:
    try:
        import usb.core
        import usb.util
    except Exception as exc:
        print(f"[usbreset] pyusb unavailable: {exc}")
        toolchain_py = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "toolchain",
            "x86_64-linux",
            "bin",
            "python3",
        )
        if os.path.exists(toolchain_py):
            try:
                subprocess.run(
                    [toolchain_py, "-m", "pip", "install", "pyusb"],
                    check=True,
                )
            except Exception as install_exc:
                print(f"[usbreset] pyusb install failed: {install_exc}")
                return 1
            if os.environ.get("USBRESET_TOOLCHAIN") != "1":
                os.environ["USBRESET_TOOLCHAIN"] = "1"
                os.execv(toolchain_py, [toolchain_py, __file__])
            try:
                import usb.core
                import usb.util
            except Exception as exc2:
                print(f"[usbreset] pyusb import failed after install: {exc2}")
                return 1
        else:
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
