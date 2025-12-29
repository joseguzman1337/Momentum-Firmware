#!/usr/bin/env python3
"""
Simple user-space Wi-Fi / USB diagnostic helper for macOS.

This tool does NOT implement a driver. It only queries existing
system information via standard macOS CLI tools so it can be
run without special entitlements or kext loading.
"""

import subprocess
import sys
import re
from typing import Dict, List, Tuple


def run(cmd: str) -> str:
    """Run a shell command and return stdout as text (stderr merged)."""
    proc = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if proc.returncode != 0 and not proc.stdout:
        return proc.stderr.strip()
    return proc.stdout.strip()


def print_header(title: str) -> None:
    print("\n" + "=" * 8 + f" {title} " + "=" * 8)


def show_realtek_usb_devices() -> None:
    """Show Realtek USB devices (vendor 0x0BDA) if present."""
    print_header("Realtek USB devices (vendor 0x0BDA)")
    # Prefer IORegistry for robustness, then fall back to system_profiler.
    ioreg = run("ioreg -p IOUSB -w0 -l 2>/dev/null | egrep -i 'realtek|802.11ac NIC' || true")
    if ioreg:
        print("[IOUSB] Matching Realtek entries:")
        print(ioreg)
        return

    out = run("system_profiler SPUSBDataType 2>/dev/null | grep -i -A5 -B2 realtek || true")
    if not out:
        print("No Realtek USB devices detected (by name).")
    else:
        print(out)


def parse_hardware_ports(raw: str) -> List[Tuple[str, str, str]]:
    """Parse `networksetup -listallhardwareports` output.

    Returns list of (port_name, device, macaddr).
    """
    blocks = re.split(r"\n\s*\n", raw.strip())
    result: List[Tuple[str, str, str]] = []
    for blk in blocks:
        name = dev = mac = ""
        for line in blk.splitlines():
            line = line.strip()
            if line.startswith("Hardware Port:"):
                name = line.split(":", 1)[1].strip()
            elif line.startswith("Device:"):
                dev = line.split(":", 1)[1].strip()
            elif line.startswith("Ethernet Address:"):
                mac = line.split(":", 1)[1].strip()
        if name and dev:
            result.append((name, dev, mac))
    return result


def get_ifconfig_info(dev: str) -> Dict[str, str]:
    """Return basic info from ifconfig for a given device."""
    txt = run(f"ifconfig {dev} 2>/dev/null")
    info: Dict[str, str] = {}
    if not txt:
        return info

    # Status line
    m = re.search(r"status: (\S+)", txt)
    if m:
        info["status"] = m.group(1)

    # IPv4 address
    m = re.search(r"\sinet (\d+\.\d+\.\d+\.\d+)", txt)
    if m:
        info["ipv4"] = m.group(1)

    # Netmask
    m = re.search(r"\snetmask (0x[0-9a-fA-F]+)", txt)
    if m:
        info["netmask"] = m.group(1)

    return info


def show_network_services() -> None:
    """List all network services, their devices, MACs, and basic link/IP status."""
    print_header("Network services (networksetup + ifconfig)")
    raw = run("networksetup -listallhardwareports 2>/dev/null")
    if not raw:
        print("networksetup output is empty or command failed.")
        return

    ports = parse_hardware_ports(raw)
    if not ports:
        print("No hardware ports parsed from networksetup output.")
        return

    for name, dev, mac in ports:
        info = get_ifconfig_info(dev)
        status = info.get("status", "unknown")
        ipv4 = info.get("ipv4", "-")
        print(f"- {name}: {dev}")
        print(f"    MAC: {mac or '-'}")
        print(f"    Status: {status}")
        print(f"    IPv4: {ipv4}")


def show_rtl88xx_kext_status() -> None:
    """Show whether any RTL88xxAU-related kext appears to be loaded.

    This remains purely observational: it never attempts to load
    or unload anything.
    """
    print_header("RTL88xxAU kext load status")
    # Prefer kmutil on modern macOS; fall back to kextstat if needed.
    out = run("kmutil showloaded 2>/dev/null | grep -i RTL88xxAU || true")
    if not out:
        out = run("kextstat 2>/dev/null | grep -i RTL88xxAU || true")

    if not out:
        print("No loaded kexts matching 'RTL88xxAU' were found.")
    else:
        print(out)


def detect_awus1900() -> None:
    """Detect Alfa AWUS1900 / RTL8814AU (Realtek 802.11ac NIC) on USB.

    Uses IOUSB IORegistry and known VID/PID pairs.
    """
    print_header("Alfa AWUS1900 / RTL8814AU detection")
    # Realtek vendor 0x0BDA (3034), AWUS1900 commonly PID 0x8813 / 0x8814
    txt = run("ioreg -p IOUSB -w0 -l 2>/dev/null")
    if not txt:
        print("IOUSB registry not available.")
        return

    found = False
    # Look for nodes that mention both Realtek + 802.11ac NIC, or VID/PID values.
    blocks = re.split(r"\\+-o ", txt)
    for blk in blocks:
        if "Realtek" in blk and "802.11ac NIC" in blk:
            print("Found candidate AWUS1900 node:")
            print("+-o " + "\\n".join(blk.strip().splitlines()[:20]))
            found = True
            break
        if "idVendor" in blk and "idProduct" in blk and "Realtek" in blk:
            if "3034" in blk and ("34835" in blk or "0x8813" in blk or "0x8814" in blk):
                print("Found Realtek 802.11ac NIC with RTL8814AU IDs:")
                print("+-o " + "\\n".join(blk.strip().splitlines()[:20]))
                found = True
                break

    if not found:
        print("No AWUS1900 / RTL8814AU device detected in IOUSB tree.")


def detect_flipper_zero() -> None:
    """Detect Flipper Zero devices on USB.

    Matches vendor name "Flipper Devices Inc." or serials like "flip_*".
    """
    print_header("Flipper Zero detection")
    txt = run("ioreg -p IOUSB -w0 -l 2>/dev/null")
    if not txt:
        print("IOUSB registry not available.")
        return

    found = False
    blocks = re.split(r"\\+-o ", txt)
    for blk in blocks:
        if "Flipper Devices Inc." in blk or "flip_" in blk:
            print("Found Flipper device:")
            print("+-o " + "\\n".join(blk.strip().splitlines()[:20]))
            found = True
    if not found:
        print("No Flipper Zero device detected in IOUSB tree.")


def main(argv: list[str]) -> int:
    show_realtek_usb_devices()
    detect_awus1900()
    detect_flipper_zero()
    show_network_services()
    show_rtl88xx_kext_status()
    print("\\nDone. This tool only inspects system state; it does not load or install any drivers.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
