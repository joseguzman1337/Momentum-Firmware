# Contributing

This project is an experimental DriverKit-based driver for RTL8814AU USB Wi-Fi on macOS Sequoia.

## Development workflow (high level)

1. **Clone & build locally**
   - Use the `shim/` to experiment with device enumeration and bring-up.
   - Use the `driver/` sources as the basis for an Xcode DriverKit system extension target.

2. **DriverKit implementation**
   - Implement a DriverKit USB/network driver that binds to RTL8814AU USB IDs.
   - Keep hardware-specific code (register programming, firmware loading, PHY/MAC config) in dedicated modules so it is easy to audit.
   - Use DriverKit / NetworkDriverKit APIs only; avoid legacy kernel APIs so the driver stays compatible with modern macOS.

3. **Apple Developer entitlements**
   - Enroll in the Apple Developer Program.
   - Request DriverKit / System Extension entitlements for the app + extension bundle IDs.
   - Configure Xcode with your Team and signing identities.

4. **Signing & notarization**
   - Sign the host app and DriverKit system extension with your Developer ID.
   - Notarize the installer (pkg or dmg) and staple the notarization ticket.
   - Verify with `spctl --assess --type exec` and `codesign --verify --deep --strict`.

5. **Distribution**
   - Publish signed, notarized installers as GitHub Releases.
   - Maintain a Homebrew formula that downloads the pkg, runs the installer, and prints caveats for approving the System Extension in System Settings.

6. **Testing & CI**
   - Use GitHub Actions macOS runners to build and run basic tests.
   - Keep any signing keys out of CI or use a secure secrets setup; never commit keys.

Please open issues and PRs for any substantial changes. This driver is experimental; test only on non-production systems.
