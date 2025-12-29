# Xcode Project Setup for RTL8814AU DriverKit Extension

## Critical Issues to Address

### 1. SDK Cyclic Dependency Bug (macOS 26.2)

You're encountering a known bug in the macOS 26.2 SDK where IOKit has a cyclic dependency with CoreServices:
```
CoreServices -> DiskArbitration -> IOKit -> CoreServices
```

**Solutions:**
1. **Update Xcode**: Install the latest Xcode version
2. **Change Base SDK**: 
   - Select your target in Xcode
   - Go to Build Settings
   - Search for "Base SDK"
   - Select macOS 15.x or an earlier stable SDK
3. **Report to Apple**: File a feedback at https://feedbackassistant.apple.com

### 2. DriverKit Project Configuration

Your project needs to be properly configured as a DriverKit extension:

#### Step 1: Create DriverKit Extension Target

1. In Xcode, go to File → New → Target
2. Select "DriverKit → Driver Extension"
3. Name it "RTL8814AUDriver"
4. Make sure the language is set to Swift

#### Step 2: Configure Build Settings

1. Select the DriverKit target
2. Go to Build Settings
3. Set these values:
   - **Base SDK**: macOS 15.0 or later
   - **Deployment Target**: macOS 10.15 or later
   - **Swift Language Version**: Swift 5.9 or later
   - **Enable Hardened Runtime**: YES
   - **Code Signing Identity**: Developer ID Application

#### Step 3: Add Entitlements

Create or edit `RTL8814AUDriver.entitlements`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.developer.driverkit</key>
    <true/>
    <key>com.apple.developer.driverkit.family.networking</key>
    <true/>
    <key>com.apple.developer.driverkit.family.usb</key>
    <true/>
    <key>com.apple.developer.driverkit.transport.usb</key>
    <true/>
    <key>com.apple.developer.driverkit.allow-any-usb-device</key>
    <true/>
</dict>
</plist>
```

#### Step 4: Configure Info.plist

Your `Info.plist` needs IOKit matching information:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>$(DEVELOPMENT_LANGUAGE)</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundlePackageType</key>
    <string>$(PRODUCT_BUNDLE_PACKAGE_TYPE)</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>IOKitPersonalities</key>
    <dict>
        <key>RTL8814AUDriver</key>
        <dict>
            <key>CFBundleIdentifier</key>
            <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
            <key>IOClass</key>
            <string>IOUserUSBHostDevice</string>
            <key>IOMatchCategory</key>
            <string>IODefaultMatchCategory</string>
            <key>IOProviderClass</key>
            <string>IOUSBHostDevice</string>
            <key>IOUserClass</key>
            <string>RTL8814AUDriver</string>
            <key>IOUserServerName</key>
            <string>com.rtl8814au.driver</string>
            <key>idVendor</key>
            <integer>3034</integer>
            <key>idProduct</key>
            <integer>34835</integer>
        </dict>
    </dict>
    <key>OSBundleUsage</key>
    <string>RTL8814AU USB WiFi Driver</string>
</dict>
</plist>
```

#### Step 5: Project Structure

Organize your files:

```
RTL8814AUDriver/
├── Info.plist
├── RTL8814AUDriver.entitlements
├── RTL8814AUDriver.swift (main driver class)
├── NetworkInterface.swift
├── Driver.swift (USB driver implementation)
└── Supporting Files/
    └── Constants.swift
    
RTL8814AUDriverTests/
├── RTL8814AUDriverTests.swift
└── Info.plist

RTL8814AUDriverBuilder/
└── Builder.swift (separate command-line tool, not part of driver)
```

#### Step 6: Separate Builder Tool

The `RTL8814AUDriverBuilder.swift` file appears to be a standalone tool and should NOT be part of the DriverKit target. Create a separate "Command Line Tool" target for it:

1. File → New → Target
2. Select "macOS → Command Line Tool"
3. Name it "RTL8814AUDriverBuilder"
4. Move the builder file to this target
5. The builder can have a shebang line if it's a standalone script

### 3. Test Target Configuration

For the test target:

1. Create a Unit Test Bundle target
2. Link against the Swift Testing framework
3. Set the host application (if needed) or make it a standalone test
4. In Build Settings, ensure:
   - **Enable Testing Search Paths**: YES
   - **Swift Optimization Level**: No optimization for Debug

### 4. File Organization

Based on the errors, here's how files should be organized:

**DriverKit Extension Target:**
- `RTL8814AUDriver.swift` (main driver)
- `Driver.swift` (USB driver implementation)
- `NetworkInterface.swift`
- Remove or comment out any `@main` attribute if you have multiple files with it

**App Host Target** (if you need one for SystemExtensions activation):
- Files that use `import SystemExtensions`
- UI for installing/activating the driver extension
- Note: DriverKit extensions themselves don't use SystemExtensions directly

**Command Line Tool Target:**
- `RTL8814AUDriverBuilder.swift` (the builder/installer tool)

### 5. Common Pitfalls

1. **Multiple @main attributes**: Only one file in your driver extension can have `@main`
2. **SystemExtensions in DriverKit**: DriverKit extensions don't directly import SystemExtensions - that's for the host app that installs the extension
3. **Testing DriverKit**: You typically can't unit test DriverKit code directly because it requires kernel interaction

## Recommended Next Steps

1. **Fix SDK Issue First**: Try changing to macOS 15.x SDK
2. **Restructure Project**: Create proper targets (DriverKit Extension, Host App, Command Line Tool)
3. **Configure Entitlements**: Add proper DriverKit entitlements
4. **Sign with Developer ID**: DriverKit requires proper code signing

## Testing on macOS Sequoia

Note that on macOS Sequoia:
- SIP must be disabled for third-party kernel extensions/drivers
- Use `csrutil disable` in Recovery Mode
- Consider using DriverKit which works with SIP enabled (but still requires approval)

## Additional Resources

- [DriverKit Documentation](https://developer.apple.com/documentation/driverkit)
- [Creating a DriverKit Extension](https://developer.apple.com/documentation/driverkit/creating_a_driver_using_the_driverkit_sdk)
- [USB DriverKit](https://developer.apple.com/documentation/usbdriverkit)
- [Networking DriverKit](https://developer.apple.com/documentation/networkingdriverkit)
