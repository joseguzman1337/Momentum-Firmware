# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository purpose and big-picture architecture

This repository contains a macOS kernel extension (kext) framework and installer tooling for Realtek RTL88xxAU USB Wi‑Fi adapters (including Alfa AWUS1900). It is structured around three main pieces:
- A skeleton IOKit network driver (`RTL88xxAU.kext`) in `src/`
- A Makefile-based build system that produces the kext and simple installer packages
- Installer tooling (CLI + GUI) and distribution packaging scripts, plus an extracted vendor installer under `alfa_pkg/`

### Kernel extension skeleton (`src/`)

- Core driver class lives in `src/RTL88xxAU.h` and `src/RTL88xxAU.cpp`.
  - `RTL88xxAU` subclasses `IOEthernetController` and uses `IOUSBInterface`/`IOUSBDevice` as its provider.
  - The implementation is primarily a structure/framework: it wires up init/start/stop, simple USB configuration (`USB_CONFIG_VALUE`), a work loop, and stubbed pipe open/close functions.
  - Device support is constrained to Realtek vendor ID `0x0BDA` and a set of product IDs for RTL8812AU/RTL8821AU (and Alfa variants) via `isDeviceSupported`.
- The on-disk kext bundle layout that the build expects lives under `src/kext/RTL88xxAU.kext/Contents/` (particularly `Info.plist`).
- Per `PROJECT_SUMMARY.md`, this is an educational/framework implementation: the low-level USB/HW logic is intentionally incomplete and real deployment would require Apple private headers and proper signing. Do not assume the current driver is production‑ready.

### Build system (`Makefile`)

- The Makefile is the canonical way to build and install the kext:
  - Uses `clang++` with dual-arch flags (`-arch x86_64 -arch arm64`), the active macOS SDK (`xcrun --show-sdk-path`), and `-mmacosx-version-min=12.0`.
  - Compiles `src/RTL88xxAU.cpp` to an object with kext-specific flags (`-fno-builtin`, `-fno-stack-protector`, etc.).
  - Links a kext-style binary into `build/RTL88xxAU.kext/Contents/MacOS/RTL88xxAU` using `-Xlinker -kext -nostdlib -lkmod -lcc_kext` and copies `Info.plist` from `src/kext/RTL88xxAU.kext/Contents/`.
- The build target layout is:
  - `build/RTL88xxAU.kext/` – assembled kext bundle
  - Additional package artifacts under `build/` created by `package`/helper scripts.
- There is no separate linter/formatter target defined here; code style enforcement is not automated in this repo.

### Installer CLI scripts (`scripts/`)

- `scripts/install.sh` is the primary, fully featured installer:
  - Enforces root execution and checks macOS version (Big Sur and later), Xcode CLTs, and System Integrity Protection (SIP) status.
  - Chooses an install directory (`/Library/Extensions` on modern macOS when possible, otherwise `/System/Library/Extensions`).
  - Detects attached Realtek USB devices via `system_profiler SPUSBDataType` for user feedback.
  - Unloads and warns about existing Realtek kexts, removes any prior `RTL88xxAU.kext`, then runs a full rebuild via `make clean && make build`.
  - Installs the kext into the chosen extensions directory with correct ownership/permissions, updates kext caches, loads the kext, and verifies load state with `kextstat` and `networksetup`.
- `scripts/simple_install.sh` is a streamlined alternative designed to cope better with modern macOS security:
  - Requires root, chooses `/Library/Extensions` when available, optionally builds the driver if no `build/RTL88xxAU.kext` exists.
  - Unloads/removes any previous installation, copies the built kext, sets permissions, attempts `kextcache` and `kextload`, and guides the user to reboot if automatic loading fails.
- Both installers directly touch system paths (`/System/Library/Extensions`, `/Library/Extensions`) and invoke `kextcache`/`kextload`. Agents must not run them without explicit user intent, as they modify the host system.

### GUI installer (`installer_gui.py` + `requirements.txt`)

- `installer_gui.py` is a PyQt5‑based GUI wrapper around the shell installers:
  - Presents supported devices and status, can probe `system_profiler SPUSBDataType` to detect Realtek hardware.
  - "Install Driver (Simple)" opens a Terminal window and runs `scripts/simple_install.sh` with `sudo` using AppleScript.
  - "Advanced Install" uses an `InstallWorker` that runs AppleScript to open Terminal and execute `scripts/install.sh` with `sudo`, while streaming high‑level status back to the GUI.
  - "Open Terminal" opens a Terminal session pre‑populated with the full `sudo bash scripts/install.sh` command.
- `requirements.txt` currently lists `PyQt5>=5.15.7` as the only dependency.
- The GUI assumes it is run from the project root (checks for `scripts/install.sh` relative to CWD) and requires macOS (`sys.platform == "darwin"`).

### Packaging scripts and distribution artifacts

- `create_installer.sh` builds a single‑pkg installer using placeholder driver content:
  - Creates a clean `build/` tree with `pkg_root` and `pkg_scripts` subdirectories.
  - Assembles a demo `RTL88xxAU.kext` bundle under `pkg_root/System/Library/Extensions/` by copying `Info.plist` from `src/kext/RTL88xxAU.kext/Contents/` and writing a simple placeholder binary.
  - Writes `preinstall` and `postinstall` scripts that:
    - Enforce a minimum macOS version (Monterey+), unload/remove existing Realtek drivers, warn about conflicting kexts.
    - Fix up permissions, run `kextcache`, attempt `kextload`, and print post‑install guidance and diagnostics commands.
  - Uses `pkgbuild` to create `build/RTL88xxAU-1.0.0.pkg`, then generates a minimal `Distribution.xml` and wraps it into `build/RTL88xxAU-Installer-1.0.0.pkg` via `productbuild`.
- `create_all_installers.sh` orchestrates a richer "release" set:
  - Rebuilds a demo kext structure in `build/RTL88xxAU.kext` with a shell script placeholder binary.
  - Creates installer payload and scripts (preinstall/postinstall) similar to `create_installer.sh`, then runs `pkgbuild` to produce `build/RTL88xxAU-1.0.0.pkg`.
  - Optionally builds a more advanced "Professional" installer via `productbuild` if `build/distribution.xml` and `build/installer_resources` are present.
  - Assembles a DMG `build/RTL88xxAU-macOS-Driver-1.0.0.dmg` containing the installer pkg(s), README, and optionally a GUI app.
  - Generates SHA‑256 checksums for `.pkg` and `.dmg` files into `build/RTL88xxAU-1.0.0-checksums.txt`.

### Extracted vendor installer (`alfa_pkg/expanded/`)

- `alfa_pkg/expanded/` contains the expanded contents of a third‑party macOS installer for Alfa/Realtek/Mediatek adapters.
- That directory has its own `WARP.md` describing the `Distribution` XML, component `*.pkg` payloads, and extensive shell scripts for install/uninstall and EFI/Clover cleanup.
- When working under `alfa_pkg/expanded/`, use the guidance in that `WARP.md` in addition to this file. Treat its scripts as production installer logic: they are complex, heavily side‑effectful, and operate directly on `/System/Library/Extensions`, `/Library/Extensions`, `/Library/Application Support`, Clover ESP volumes, and SystemConfiguration plists.

## Common commands for agents

The commands below are the primary entry points an agent should use when building, testing, and packaging this project. All shell commands are intended to be run from the repository root unless noted.

### Build, clean, and basic validation

- Build the kext (default target):
  - `make build`
- Clean all build artifacts:
  - `make clean`
- Quick structural validation of the built kext (no hardware I/O):
  - `make test` (invokes `kextutil -t build/RTL88xxAU.kext`)

### Install, uninstall, load, unload (kext lifecycle)

These targets all ultimately manipulate `/System/Library/Extensions` and/or `/Library/Extensions` and must be run with `sudo`.

- Install (builds if needed, copies kext to system extensions, updates caches):
  - `sudo make install`
- Uninstall:
  - `sudo make uninstall`
- Load the installed kext:
  - `sudo make load`
- Unload the installed kext:
  - `sudo make unload`

For investigating a single "test" of whether the kext loads correctly on the current system, prefer:
- `make build`
- `make test` (non‑destructive, does not install system‑wide)
- If needed, `sudo make install && sudo make load` followed by diagnostic commands below.

### Installer scripts (CLI flows)

Use these when you specifically want to exercise the scripted installation flows rather than just the Makefile targets.

- Full interactive installer with environment checks and verification:
  - `sudo ./scripts/install.sh`
- Simplified installer tuned for modern macOS security behavior:
  - `sudo ./scripts/simple_install.sh`

Both scripts will attempt to unload existing Realtek kexts, delete any previous `RTL88xxAU.kext` from extensions directories, copy the newly built kext, update caches, and load the driver.

### GUI installer

- Install GUI dependencies (PyQt5) and prepare the GUI app helper:
  - `make gui-deps`
- Run the GUI installer application directly:
  - `python3 installer_gui.py`

From within the GUI you can:
- Detect devices (uses `system_profiler SPUSBDataType`).
- Launch the simplified installer in Terminal.
- Launch the advanced installer in Terminal.

### Packaging and distribution artifacts

- Create a basic pkg and distribution pkg using the standalone packager script:
  - `./create_installer.sh`
- Build the full set of installers (kext structure, basic pkg, optional professional pkg, DMG, checksums):
  - `./create_all_installers.sh`

These scripts overwrite the `build/` directory. Do not run them if you need to preserve previous build artifacts in `build/`.

### Diagnostics and manual checks

Useful commands drawn from `README.md` and the installer scripts for verifying behavior:

- Check whether the driver is loaded:
  - `kextstat | grep RTL88xxAU`
- Inspect USB Realtek devices:
  - `system_profiler SPUSBDataType | grep -A5 -B5 -i realtek`
- View driver logs (on recent macOS versions):
  - `log show --predicate 'senderImagePath contains "RTL88xxAU"' --info`
  - `log stream --predicate 'senderImagePath contains "RTL88xxAU"' --info`

## Notes and constraints for agents

- Many scripts and installer components in this repo perform privileged operations on macOS system directories, kernel extension caches, and EFI/Clover volumes.
  - Do not invoke `sudo`ed installer scripts (`scripts/install.sh`, `scripts/simple_install.sh`, vendor scripts under `alfa_pkg/expanded/`) unless the user explicitly asks for that action and understands the impact.
- The kext and installer packages produced here are intended as a framework/demo:
  - `PROJECT_SUMMARY.md` calls out that real hardware functionality is incomplete without private kernel headers and proper code signing.
  - When making changes, preserve this educational/demo character unless the user is explicitly moving toward a production‑ready driver.
- There is no automated unit test suite; `make test` is a structural validation using `kextutil`. When asked to "run tests" in this repo, that is usually the closest built‑in mechanism.
- When working inside `alfa_pkg/expanded/`, follow its local `WARP.md` for detailed guidance on the vendor installer scripts and `Distribution` XML, and keep in mind that those scripts are tightly coupled to specific macOS versions and SystemConfiguration layouts.
