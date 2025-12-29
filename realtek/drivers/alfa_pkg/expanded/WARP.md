# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

This directory is the expanded contents of a macOS installer for Alfa USB Wi‑Fi adapters based on Realtek (and Mediatek) chipsets. It is not a conventional source tree: there is no build system or tests here, only prebuilt installer packages (`*.pkg`), their scripts, and localized resources.

The central entry point is the top-level `Distribution` XML, which defines the installer UI flow and ties together the component packages:
- `Realtek109110Driver.pkg` – kernel extension driver package.
- `RealtekUtility1014.pkg` – Realtek/ALFA status bar utility and helper infrastructure.
- `RealtekSerialsInstaller.pkg` – additional UI helper and status bar app variant.
- `Realtek_Uninstall.pkg` and `Uninstall.pkg` – uninstaller logic (including EFI/Clover cleanup).
- `MediatekSerialsInstaller.pkg` – package for Mediatek-based adapters.
- `Resources/` – localized readme, license, and welcome assets referenced by `Distribution`.

## High-level installer architecture

### Distribution XML

- `Distribution` is an Apple installer Distribution XML that:
  - Declares six choices (`installer_choice_1` … `installer_choice_6`) and their enable/selected logic.
  - References each component package via `<pkg-ref>` elements (e.g. `com.alfa-network-inc.Realtek109Driver` → `#Realtek109110Driver.pkg`).
  - Contains a `<script>` section that controls which choices are enabled/selected based on other choices.
- When repackaged into a `.pkg`, `Distribution` is what the macOS Installer application reads to drive the flow; the `*.pkg` directories here are the component payloads that Distribution expects.

### Realtek kernel driver package (`Realtek109110Driver.pkg`)

- Primary behavior is implemented in `Realtek109110Driver.pkg/Scripts/preinstall` and `.../postinstall` (POSIX shell scripts run by the installer as `root`).
- `preinstall` responsibilities:
  - Unloads existing Realtek-related kexts via `kextunload`.
  - Aggressively removes a wide range of Realtek/RTL* kexts from `/System/Library/Extensions` and `/Library/Extensions`.
  - Removes legacy installer receipts in `/Library/Receipts` for older Realtek/"Wireless Network Utility" installers.
  - Cleans up SystemConfiguration network service entries associated with Realtek interfaces by:
    - Using `/usr/libexec/PlistBuddy` on `preferences.plist` and `NetworkInterfaces.plist`.
    - Finding `RtWlanU`/`RTL*` interfaces and deleting corresponding `NetworkServices` entries and their service order entries.
  - Touches `/System/Library/Extensions` on newer macOS versions (10.11+) to trigger kext cache updates.
- `postinstall` responsibilities:
  - Normalizes permissions and ownership for installed kexts:
    - `/System/Library/Extensions/RtWlanU.kext`
    - `/System/Library/Extensions/RtWlanU1827.kext`
    - `/System/Library/Extensions/RtWlanDisk.kext`
  - On newer systems, ensures `_CodeSignature/CodeResources` and `Info.plist` files have correct modes.
  - Rebuilds kernel extension caches via `kextcache` (different arguments for 10.6 vs 10.7–10.10).
  - `touch`es `/System/Library/Extensions` and explicitly `kextload`s the Realtek kexts.

### Utility/StatusBar app package (`RealtekUtility1014.pkg`)

- Implements pre/post install behavior in `RealtekUtility1014.pkg/Scripts/preinstall` and `.../postinstall`.
- `preinstall` cleans out prior UI and helper artifacts:
  - Removes legacy LaunchAgents/LaunchDaemons for `Wlan*` identifiers.
  - Removes several existing Wi‑Fi utility apps (e.g. `Wireless Network Utility.app`, `Wireless-AC Network Utility.app`, `TP-LINK Wireless Configuration Utility.app`, `BearExtender.app`).
  - Removes `StatusBarApp.app` from `/System/Library/CoreServices` and various `WLAN`/`ALFA_RTWIFI` support directories and Realtek preference plists under `~/Library/Preferences`.
  - Kills processes such as `StatusBarApp`, `wpa_supplicant`, and `RtWlanHelper` if they are running.
  - Creates `/Library/Application Support/ALFA_RTWIFI` and `/Library/Application Support/ALFA_RTWIFI/com.realtek.utility.wifi` with `root:wheel` ownership.
- `postinstall` sets up the new UI stack:
  - Populates `/Library/Application Support/ALFA_RTWIFI/com.realtek.utility.wifi` with `StatusBarApp.app`, `RtWlanHelper`, and related assets (including `installerFiles.zip`).
  - Unpacks additional resources from `installerFiles.zip` when present and cleans up the archive.
  - Computes the macOS version and chooses LaunchAgent/LaunchDaemon paths accordingly (10.6 vs ≥10.7 path conventions).
  - Writes LaunchAgent and LaunchDaemon property lists at runtime for:
    - `Wlan.Software` (LaunchAgent) pointing to the `StatusBarApp` binary.
    - `Wlan.SoftwareDaemon` (LaunchDaemon) pointing to the `RtWlanHelper` binary.
  - Uses `launchctl` to unload/reload these plists and verifies they are loaded by grepping `launchctl list`.
  - Manages a status bar utility socket under `/var/tmp/com.realtek.utility.statusbar.socket`, adjusting permissions for broader access.
  - Opens the status bar app via `open -a "/Library/Application Support/ALFA_RTWIFI/StatusBarApp.app"` after installation.

### Additional UI helper package (`RealtekSerialsInstaller.pkg`)

- `RealtekSerialsInstaller.pkg/Scripts/Apps/preinstall`:
  - Performs a similar cleanup to the utility preinstall, but focused on older LaunchAgents/Daemons and apps under `/Applications` and `/Library/Application Support/WLAN`.
  - Removes prior Realtek UI preferences and temporary files under `/var/tmp/com.realtek.utility.*`.
  - Recreates `/Library/Application Support/WLAN/com.realtek.utility.wifi` with permissive permissions, then resets ownership to `root:wheel`.
- `RealtekSerialsInstaller.pkg/Scripts/Apps/postinstall`:
  - Copies `StatusBarApp.app` and `RtWlanHelper` into `/Library/Application Support/WLAN` and its `com.realtek.utility.wifi` subdirectory.
  - Sets `chmod 777` on the app and helper directories, then fixes ownership to `root:wheel`.
  - Detects the OS minor version and sets LaunchAgent/Daemon paths similarly to the utility package.
  - Writes LaunchAgent (`Wlan.Software`) and LaunchDaemon (`Wlan.SoftwareDaemon`) plists pointing to the status bar app and helper within `/Library/Application Support/WLAN`.
  - Unloads and reloads these plists via `launchctl`, and verifies they are properly loaded.
- `RealtekSerialsInstaller.pkg/Scripts/Driver/EFI/CLOVER/kexts/Other/` contains `RtWlanU.kext` and `RtWlanU1827.kext` used for EFI/Clover-based setups; payload layout is consumed by the uninstaller/installer scripts that mount and modify the ESP.

### Uninstall logic (`Realtek_Uninstall.pkg` and `Uninstall.pkg`)

- `Uninstall.pkg/Scripts/preinstall` (Bash script) is the main high-level uninstaller:
  - Prompts for the administrator password and clearly labels multiple phases (terminate utilities, remove utility-related files, remove install logs, system information, etc.).
  - Kills Wi‑Fi utility processes (StatusBarApp, Realtek utilities, TP-LINK utilities, `wpa_supplicant`).
  - Removes LaunchAgents/LaunchDaemons, applications, status bar helpers, support directories, preferences, and installer receipts under `/private/var/db/receipts` for a broad set of `com.realtek.*` and `com.Wlan.*` identifiers.
  - Uses `PlistBuddy` against `preferences.plist` and `NetworkInterfaces.plist` to:
    - Discover Realtek WLAN interfaces (e.g. `en6`, `en7`, etc.).
    - Remove corresponding `NetworkServices` entries and update the IPv4 `ServiceOrder` array.
  - Prints intermediate state such as `autoUuid`, `RtWlanArray`, and service UUIDs for debugging.
  - Ends with an "Uninstall Complete" phase message.
- `Uninstall.pkg/Scripts/postinstall` focuses on EFI/Clover cleanup:
  - Ensures `/Volumes/EFI` and `/Volumes/ESP` are unmounted if present.
  - Calls a local `MountESP` helper to mount the system's ESP at `/Volumes/ESP`.
  - Removes `RtWlanU.kext` and `RtWlanU1827.kext` from `/Volumes/ESP/EFI/CLOVER/kexts/Other`.
  - Deletes a volume-local `EFIROOTDIR` link.
- `Realtek_Uninstall.pkg` provides an additional package referenced by `Distribution` with its own uninstall behavior (not all scripts may be present or distinct; behavior largely mirrors `Uninstall.pkg`).

### MediatekSerialsInstaller and resources

- `MediatekSerialsInstaller.pkg` is referenced by `Distribution` but has no custom scripts; its behavior is defined purely by its payload.
- `Resources/` contains localized RTF readmes, welcome screens, and license text referenced in `Distribution` via `welcome`, `readme`, and `license` tags.

## Working with this repository

- There is no build, lint, or test harness in this directory. It is a snapshot of installer artifacts. Any rebuilding of a distributable `.pkg` must be done using macOS installer tooling (`pkgbuild`/`productbuild`) outside of what is defined here.
- When modifying behavior:
  - Prefer editing the shell scripts under `*.pkg/Scripts/` and the `Distribution` XML rather than attempting to patch binary payloads (`.app` bundles, `.kext` binaries).
  - Keep scripts POSIX‑compatible (`/bin/sh`) unless they explicitly use Bash (`#!/bin/bash`), as the installer environment may be constrained.
  - Be careful with `sudo` calls in scripts: they assume an installer context running as `root`. Do not execute these scripts directly on a development machine unless you fully understand their effects.
  - Many scripts hard-code paths under `/System/Library/Extensions`, `/Library/Extensions`, `/Library/Application Support`, `/Applications`, `~/Library/Preferences`, and `/private/var/db/receipts`; changes here have system-wide impact.
  - Network configuration cleanup logic is tightly coupled to SystemConfiguration plist structure; edits to `PlistBuddy` commands should be made with caution.

## Helpful inspection and validation commands

These commands are useful when exploring or validating changes in this repository (they do not perform installation themselves):

- List overall structure:
  - `ls -R` from the repo root to see all component packages and their internal scripts/resources.
- Inspect or diff shell scripts without executing them:
  - `sed -n '1,160p' Realtek109110Driver.pkg/Scripts/preinstall`
  - `sed -n '1,200p' RealtekUtility1014.pkg/Scripts/postinstall`
  - Use `diff` or `git diff --no-pager` to review changes across script files.
- Validate `Distribution` XML after edits:
  - `xmllint --noout Distribution` (if `xmllint` is installed) to catch syntax errors.
- View localized readme text from the RTF bundle (macOS only):
  - `textutil -convert txt -stdout Resources/en.lproj/readme.rtfd/TXT.rtf`

If you need to repackage the installer, rely on standard macOS documentation for `productbuild`/`pkgbuild`; this repository does not contain project-specific build scripts or metadata beyond the `Distribution` file and the component `*.pkg` directories.
