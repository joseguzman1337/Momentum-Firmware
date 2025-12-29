# Apple Signing and Notarization Checklist

This document outlines the concrete steps required to ship the RTL8814AU DriverKit driver on macOS with SIP enabled.

## 1. Apple Developer Setup

1. Enroll in the Apple Developer Program (paid account).
2. In Certificates, Identifiers & Profiles:
   - Create bundle IDs:
     - Host app: `com.yourorg.RTL8814AUHost`
     - System extension: `com.yourorg.RTL8814AUDriverKit`
   - Request entitlements:
     - `com.apple.developer.system-extension.install`
     - `com.apple.developer.driverkit`
     - `com.apple.developer.driverkit.transport.usb`
     - `com.apple.developer.driverkit.family.networking`
3. Create certificates:
   - Developer ID Application
   - Developer ID Installer

## 2. Xcode Project Configuration

1. Create an Xcode project `RTL8814AUDriver.xcodeproj`.
2. Add two targets:
   - macOS app target `RTL8814AUHost` using `RTL8814AUHost/Info.plist` and `RTL8814AUHost.entitlements`.
   - DriverKit system extension target `RTL8814AUDriverKit` using `RTL8814AUDriverKit/Info.plist` and `RTL8814AUDriverKit.entitlements`.
3. Set the Team to your Apple Developer team for both targets.
4. Enable the requested entitlements in Signing & Capabilities.

## 3. Building and Archiving

1. In Xcode, select `RTL8814AUHost` scheme (Release configuration).
2. Product → Archive.
3. Verify that the archive contains the host app and embedded system extension.

## 4. Creating the Installer Package

Use the provided script as a template:

```bash
./drivers/rtl8814au-driver-xcode/Scripts/build_pkg.sh build/Release
```

This script:
- Copies `RTL8814AU Driver Manager.app` into `pkgroot/Applications`.
- Uses `productbuild` to create `RTL8814AUDriver-unsigned.pkg`.
- Uses `productsign` with your `Developer ID Installer` cert to create `RTL8814AUDriver-signed.pkg`.

## 5. Notarization

Using `xcrun notarytool` (recommended):

```bash
xcrun notarytool submit RTL8814AUDriver-signed.pkg \
  --keychain-profile YOUR_NOTARY_PROFILE \
  --wait
```

After a successful submission, staple the ticket:

```bash
xcrun stapler staple RTL8814AUDriver-signed.pkg
```

Verify:

```bash
spctl --assess --type install RTL8814AUDriver-signed.pkg
pkgutil --check-signature RTL8814AUDriver-signed.pkg
```

## 6. Publishing and Homebrew

1. Upload `RTL8814AUDriver-signed.pkg` (now notarized and stapled) to a GitHub Release.
2. Update `drivers/rtl8814au-driver-xcode/brew/rtl8814au-driver.rb`:
   - Set the correct `url` to the release asset.
   - Replace `REPLACE_WITH_REAL_SHA256` with the pkg's SHA256.
3. Users can then install via:

```bash
brew install yourorg/yourtap/rtl8814au-driver
```

They must still:
- Approve the system extension in System Settings → Privacy & Security.
- Reboot if prompted.

This flow keeps SIP enabled and complies with Apple’s current driver model.
