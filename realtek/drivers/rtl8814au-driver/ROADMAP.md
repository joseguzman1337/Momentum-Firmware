# Roadmap

High-level plan for an open-source RTL8814AU DriverKit driver for macOS Sequoia.

## 1. Repository & license
- Keep this project as a standalone public repository (MIT license).
- Include DriverKit sources, shim tools, build scripts, and a Homebrew formula.

## 2. DriverKit implementation
- Implement a DriverKit USB/network driver that binds to RTL8814AU USB IDs.
- Use DriverKit / NetworkDriverKit APIs (no legacy kernel kext APIs).
- Place hardware-specific logic (register programming, firmware, PHY/MAC) in a separate module.

## 3. Apple Developer steps
- Enroll in Apple Developer Program.
- Request DriverKit / System Extension entitlements for the host app and extension.
- Configure Xcode project with correct bundle IDs and Team.

## 4. Signing & notarization
- Sign the app and system extension with Developer ID.
- Build a pkg/dmg installer that places the app and registers the extension.
- Notarize the installer and staple the ticket.

## 5. Homebrew formula
- Host signed, notarized pkgs as GitHub Releases.
- Provide a Homebrew formula that:
  - Downloads the pkg.
  - Invokes `/usr/sbin/installer` to install.
  - Prints caveats explaining System Settings → Extensions approval steps.

## 6. Testing & CI
- Use GitHub Actions macOS runners to build the driver and shim.
- Run codesign verification in CI.
- Optionally, add basic functional tests that exercise the shim on test hardware.

This roadmap is intentionally high-level and should be refined as the driver matures.
