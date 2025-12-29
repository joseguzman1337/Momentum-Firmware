#!/usr/bin/env python3
# ==============================================================================
# AWUS1900 Automated Driver Injector (Concept Implementation)
# Target OS: macOS "Tahoe"-style environment (kmutil / AuxKC)
# Hardware: Alfa AWUS1900 (RTL8814AU Chipset)
# Repository: x31337/realtek2 (Primary)
#
# WARNING:
# - This script assumes you understand the risks of loading unsigned kexts.
# - You must typically disable SIP and set Reduced Security for 3rd-party kexts.
# - Run only on a test/development machine you are prepared to recover.
# ==============================================================================

import os
import sys
import subprocess
import shutil
import time
import re

# --- Configuration ------------------------------------------------------------

REPO_URL = "https://github.com/x31337/realtek2.git"

# Where we want the kexts to end up
TARGET_EXTENSION_DIR = "/Library/Extensions"

# Temporary staging directory for cloning and preparation
STAGING_DIR = "/tmp/awus1900_stage"

# The specific kexts typically used for RTL8814AU
REQUIRED_KEXTS = [
    "RtWlanU.kext",
    "RtWlanU1827.kext",
]

# Device IDs for AWUS1900 (Realtek 8814AU)
TARGET_VID = "0x0bda"
TARGET_PID_CANDIDATES = {"0x8813", "0x8814"}


# --- Logging ------------------------------------------------------------------


class SystemLogger:
    """Handles formatted output for the installation process."""

    HEADER = "\033[95m"
    INFO = "\033[94m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"

    @staticmethod
    def info(msg: str) -> None:
        print(f"{SystemLogger.INFO}[INFO]{SystemLogger.ENDC} {msg}")

    @staticmethod
    def success(msg: str) -> None:
        print(f"{SystemLogger.GREEN}[OK]{SystemLogger.ENDC}   {msg}")

    @staticmethod
    def warn(msg: str) -> None:
        print(f"{SystemLogger.WARNING}[WARN]{SystemLogger.ENDC}  {msg}")

    @staticmethod
    def error(msg: str) -> None:
        print(f"{SystemLogger.FAIL}[ERR]{SystemLogger.ENDC}   {msg}")


# --- Helpers ------------------------------------------------------------------


def run_shell(command: str, ignore_errors: bool = False) -> str:
    """Execute a shell command and return stdout.

    Raises on failure unless ignore_errors=True.
    """
    SystemLogger.info(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            check=not ignore_errors,
            text=True,
        )
        if result.stderr and not ignore_errors:
            # kmutil and friends often emit useful diagnostics on stderr
            SystemLogger.info(f"Stderr: {result.stderr.strip()}")
        return (result.stdout or "").strip()
    except subprocess.CalledProcessError as e:
        if not ignore_errors:
            SystemLogger.error(f"Command failed: {command}")
            if e.stderr:
                SystemLogger.error(e.stderr.strip())
        return (e.stdout or "").strip()


# --- Environment / Security Checks -------------------------------------------


def check_requirements() -> None:
    """Validate root privileges and (soft) SIP status."""

    # Root check
    if os.geteuid() != 0:
        SystemLogger.error("This script must be run as root. Use `sudo`.")
        sys.exit(1)

    # SIP check (best-effort; may fail on some systems)
    try:
        sip_status = run_shell("csrutil status", ignore_errors=True)
        if "enabled" in (sip_status or "").lower():
            SystemLogger.warn("System Integrity Protection (SIP) appears ENABLED.")
            SystemLogger.warn(
                "Unsigned/3rd-party kexts typically will NOT load with SIP enabled."
            )
            SystemLogger.warn(
                "Disable SIP in Recovery and set Reduced Security before proceeding."
            )
            input(
                "Press Enter to continue anyway (installation will likely fail), "
                "or Ctrl+C to abort..."
            )
        else:
            if sip_status:
                SystemLogger.success(f"SIP status: {sip_status}")
            else:
                SystemLogger.warn("SIP status unknown (no output from csrutil).")
    except Exception as e:
        SystemLogger.warn(f"Could not determine SIP status: {e}")
        SystemLogger.warn("Proceeding with caution.")


# --- Hardware Detection -------------------------------------------------------


def detect_hardware() -> bool:
    """Check if AWUS1900/RTL8814AU is present on the USB bus."""
    SystemLogger.info("Scanning USB bus for AWUS1900 / RTL8814AU...")
    try:
        usb_tree = run_shell("ioreg -p IOUSB -w0 -l", ignore_errors=True).lower()
        if not usb_tree:
            SystemLogger.warn("No IOUSB tree returned; ioreg may not be available.")
            return False

        if TARGET_VID in usb_tree:
            for pid in TARGET_PID_CANDIDATES:
                if pid.lower() in usb_tree:
                    SystemLogger.success(
                        f"Detected Realtek device VID={TARGET_VID}, PID={pid}."
                    )
                    return True

            SystemLogger.warn(
                "Realtek USB device detected (VID match), but PID not in expected set."
            )
            return True

        SystemLogger.warn("No Realtek RTL8814AU device detected on USB bus.")
        SystemLogger.warn(
            "Ensure the AWUS1900 is plugged in directly (avoid unpowered hubs if possible)."
        )
        return False

    except Exception as e:
        SystemLogger.error(f"Hardware detection failed: {e}")
        return False


# --- Environment Sanitization -------------------------------------------------


def clean_environment() -> None:
    """Remove previous driver installs and clear kernel staging."""
    SystemLogger.info("Sanitizing existing driver environment...")

    for kext_name in REQUIRED_KEXTS:
        paths = [
            os.path.join("/Library/Extensions", kext_name),
            os.path.join("/System/Library/Extensions", kext_name),
        ]
        for path in paths:
            if os.path.exists(path):
                SystemLogger.info(
                    f"Found legacy driver at {path}; attempting unload + removal."
                )

                run_shell(f"kmutil unload -p '{path}'", ignore_errors=True)
                run_shell(f"kextunload '{path}'", ignore_errors=True)

                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    SystemLogger.success(f"Removed {path}.")
                except Exception as e:
                    SystemLogger.warn(f"Failed to remove {path}: {e}")

    SystemLogger.info("Clearing Kernel Management staging area (kmutil clear-staging)...")
    run_shell("kmutil clear-staging", ignore_errors=True)


# --- Fetch & Install ----------------------------------------------------------


def fetch_and_install() -> list[str]:
    """Clone the repo and install required kexts into /Library/Extensions.

    Returns a list of installed kext paths.
    """
    if os.path.exists(STAGING_DIR):
        SystemLogger.info(f"Removing existing staging dir {STAGING_DIR}...")
        shutil.rmtree(STAGING_DIR)

    os.makedirs(STAGING_DIR, exist_ok=True)

    SystemLogger.info(f"Cloning repository: {REPO_URL}")
    run_shell(f"git clone '{REPO_URL}' '{STAGING_DIR}'")

    found_kexts: list[tuple[str, str]] = []

    for root, dirs, _files in os.walk(STAGING_DIR):
        for d in dirs:
            if d in REQUIRED_KEXTS:
                src = os.path.join(root, d)
                dst = os.path.join(TARGET_EXTENSION_DIR, d)
                found_kexts.append((src, dst))

    if not found_kexts:
        SystemLogger.error(
            f"Could not locate any of {REQUIRED_KEXTS} in the cloned repository."
        )
        sys.exit(1)

    installed_paths: list[str] = []

    for src, dst in found_kexts:
        kext_name = os.path.basename(dst)
        SystemLogger.info(f"Installing {kext_name} to {TARGET_EXTENSION_DIR}...")

        if os.path.exists(dst):
            SystemLogger.info(f"Removing existing {dst} before copy...")
            shutil.rmtree(dst)

        shutil.copytree(src, dst)

        SystemLogger.info(f"Setting ownership and permissions on {dst}...")
        run_shell(f"chown -R root:wheel '{dst}'")
        run_shell(f"chmod -R 755 '{dst}'")

        info_plist = os.path.join(dst, "Contents", "Info.plist")
        if os.path.exists(info_plist):
            run_shell(f"chmod 644 '{info_plist}'", ignore_errors=True)

        SystemLogger.info(f"Clearing com.apple.quarantine on {dst}...")
        run_shell(f"xattr -dr com.apple.quarantine '{dst}'", ignore_errors=True)

        installed_paths.append(dst)
        SystemLogger.success(f"Installed {kext_name} to {dst}.")

    return installed_paths


# --- Driver Load / Activation -------------------------------------------------


def load_drivers(installed_paths: list[str]) -> None:
    """Attempt to load the primary kext via kmutil."""
    SystemLogger.info("Injecting drivers into Auxiliary Kernel Collection via kmutil...")

    primary = os.path.join(TARGET_EXTENSION_DIR, "RtWlanU.kext")
    if primary not in installed_paths or not os.path.exists(primary):
        primary = installed_paths[0]

    SystemLogger.info(f"Invoking kmutil load for: {primary}")
    result = run_shell(f"kmutil load -p '{primary}'", ignore_errors=True)

    if result:
        SystemLogger.info(f"kmutil output:\n{result}")

    SystemLogger.warn(
        "If you see 'System Extension Blocked' in System Settings → Privacy & Security, "
        "you must ALLOW it and reboot."
    )


def activate_network_interface() -> None:
    """Attempt to find the new NIC and bring it up."""
    SystemLogger.info("Waiting for kernel to enumerate new network interface...")
    time.sleep(3)

    hw_ports = run_shell("networksetup -listallhardwareports", ignore_errors=True)
    if not hw_ports:
        SystemLogger.warn("Could not retrieve hardware ports via networksetup.")
        return

    matches = re.findall(
        r"Hardware Port: (.+?)\nDevice: (en\d+)",
        hw_ports,
        flags=re.MULTILINE,
    )

    if not matches:
        SystemLogger.warn("No matching Wi-Fi/USB WLAN hardware ports detected.")
        SystemLogger.warn("You may need to unplug and replug the adapter.")
        return

    port_name, device_id = matches[-1]
    SystemLogger.success(f"Detected wireless interface: {port_name} ({device_id})")

    SystemLogger.info(f"Attempting to enable power on {device_id}...")
    run_shell(f"networksetup -setairportpower {device_id} on", ignore_errors=True)

    airport_cmd = (
        "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/"
        "Resources/airport -s"
    )
    SystemLogger.info("Attempting Wi-Fi scan via airport (best-effort)...")
    scan = run_shell(airport_cmd, ignore_errors=True)
    if scan:
        SystemLogger.success("Wireless scan returned results – radio appears active.")
    else:
        SystemLogger.warn(
            "Wireless scan returned no results or airport is unavailable. "
            "Interface may still be working; verify in Network settings."
        )


# --- Main ---------------------------------------------------------------------


def main() -> None:
    print(
        f"{SystemLogger.HEADER}"
        "=== AWUS1900 / RTL8814AU macOS Driver Automator ==="
        f"{SystemLogger.ENDC}"
    )

    check_requirements()

    hardware_present = detect_hardware()

    clean_environment()

    installed_kexts = fetch_and_install()

    load_drivers(installed_kexts)

    if hardware_present:
        activate_network_interface()
    else:
        SystemLogger.warn(
            "Hardware was not detected at install time – interface activation "
            "may require plugging the device in after reboot."
        )

    print("\n" + "=" * 60)
    SystemLogger.success("Installation routine completed (script side).")
    print(f"{SystemLogger.WARNING}CRITICAL NEXT STEPS:{SystemLogger.ENDC}")
    print("1. Open System Settings → Privacy & Security.")
    print(
        "2. If you see 'System software from developer ... was blocked', click ALLOW."
    )
    print("3. Reboot to rebuild the Auxiliary Kernel Collection.")
    print(
        "4. After reboot, plug in the AWUS1900 (if not already) and check:"
    )
    print("   - `networksetup -listallhardwareports` for a new Wi-Fi/USB WLAN interface.")
    print("   - LED activity on the adapter.")
    print("=" * 60)


if __name__ == "__main__":
    main()
