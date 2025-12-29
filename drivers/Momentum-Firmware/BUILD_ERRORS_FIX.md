# Xcode Build Errors - Resolution Guide

This document explains and fixes the build errors in your RTL8814AU DriverKit project.

## Issues Fixed

### 1. ❌ On-Demand Resources Error
**Error:** `On-Demand Resources is enabled (ENABLE_ON_DEMAND_RESOURCES = YES), but is not supported for kernel extension targets`

**Fix:** Created `DriverKit.xcconfig` with `ENABLE_ON_DEMAND_RESOURCES = NO`

**How to apply:**
1. In Xcode, select your DriverKit extension target
2. Go to Build Settings tab
3. Search for "On-Demand Resources"
4. Set `ENABLE_ON_DEMAND_RESOURCES` to `NO`
5. Alternatively, apply the `DriverKit.xcconfig` file to your target

### 2. ❌ Module Dependency Errors (Foundation, SystemExtensions, USBDriverKit, Testing)

These errors indicate incorrect target configuration and imports.

#### Foundation and Clang Scanner Errors
**Cause:** Using wrong SDK or improper target configuration

**Fix:**
- Ensure your DriverKit target uses the DriverKit SDK (`SDKROOT = driverkit`)
- Your builder tool should use the macOS SDK
- Tests should be in a separate test bundle

#### SystemExtensions Import Error
**Error:** `Unable to find module dependency: 'SystemExtensions'`

**Fix:** Removed `import SystemExtensions` from `RTL8814AUDriverRTL8814AUDriver.swift`

**Why:** DriverKit extensions run in userspace and don't directly import SystemExtensions. SystemExtensions is only used by the host application that installs and activates the driver extension.

#### USBDriverKit Import Error  
**Error:** `Unable to find module dependency: 'USBDriverKit'`

**Fix:** This should work with proper SDK configuration. Ensure:
- Target SDK is set to DriverKit
- Xcode version is 14.0 or later
- Deployment target is macOS 10.15 or later

#### Testing Module Error
**Error:** `Unable to find module dependency: 'Testing'`

**Fix:** Added `import Testing` to `RTL8814AUDriverTests.swift`

**Additional steps:**
- Ensure test target has the Testing framework linked
- For Swift Testing, you need Xcode 16.0+ and macOS 15.0+
- Verify test target build settings include testing search paths

### 3. ❌ RTL8814AUDriver Module Error
**Error:** `Unable to find module dependency: 'RTL8814AUDriver'`

**Cause:** Test target can't see the DriverKit extension module

**Fix Options:**

**Option A:** Make tests test the builder tool instead
Since DriverKit extensions are hard to unit test directly, focus tests on:
- System requirements verification
- Build script functionality  
- Configuration validation

**Option B:** Keep driver tests but mark as integration tests
- These tests verify the development environment, not the driver code itself
- Remove imports of the driver module
- Focus on prerequisite checking

### 4. ❌ Hashbang Line Error
**Error:** `Hashbang line is allowed only in the main file`

**Status:** No hashbang found in current file. If this error persists:
- Ensure `RTL8814AUDriverBuilder.swift` doesn't start with `#!/usr/bin/swift` or similar
- If you want a standalone script, create a separate `.swift` file outside the Xcode project

## Project Structure Recommendations

Your project should have these separate targets:

### Target 1: DriverKit Extension (`RTL8814AUDriver`)
**Files:**
- `RTL8814AUDriver.swift` (main driver with @main)
- `RTL8814AUDriverDriver.swift` (USB driver implementation)  
- `RTL8814AUDriverFirmwareLoader.swift`
- Supporting Swift files

**SDK:** DriverKit
**Imports:** DriverKit, USBDriverKit, NetworkingDriverKit, os.log

**Build Settings:**
- `SDKROOT = driverkit`
- `ENABLE_ON_DEMAND_RESOURCES = NO`
- `DRIVERKIT_DEPLOYMENT_TARGET = 19.0`

### Target 2: Host Application (Optional - for installation UI)
**Purpose:** Provides UI to install and activate the driver extension

**SDK:** macOS
**Imports:** SystemExtensions, SwiftUI/AppKit

**Note:** This is separate from the driver and uses SystemExtensions API

### Target 3: Command Line Tool (`RTL8814AUDriverBuilder`)
**Files:**
- `RTL8814AUDriverBuilder.swift`

**SDK:** macOS  
**Imports:** Foundation

**Build Settings:**
- `SDKROOT = macosx`
- `PRODUCT_NAME = rtl8814au-builder`

### Target 4: Test Bundle (`RTL8814AUDriverTests`)
**Files:**
- `RTL8814AUDriverTests.swift`

**SDK:** macOS
**Imports:** Testing, Foundation
**Host:** Can be standalone or hosted by the builder tool

**Build Settings:**
- Enable testing search paths
- Link Testing framework (Xcode 16+) or XCTest

## Quick Fix Checklist

- [x] Remove `import SystemExtensions` from DriverKit extension files
- [x] Add `import Testing` to test files
- [x] Create `DriverKit.xcconfig` with proper settings
- [ ] Apply xcconfig to DriverKit target in Xcode
- [ ] Verify SDK settings for each target:
  - DriverKit target → DriverKit SDK
  - Builder target → macOS SDK
  - Test target → macOS SDK
- [ ] Ensure only ONE file has `@main` in the DriverKit target
- [ ] Remove or disable tests that try to import the DriverKit module directly
- [ ] Update test target to not reference DriverKit module

## Applying Fixes in Xcode

### Step 1: Fix DriverKit Target Settings

1. Select your project in Xcode
2. Select the DriverKit extension target
3. Go to Build Settings
4. Search for "On-Demand" and set `ENABLE_ON_DEMAND_RESOURCES` to `NO`
5. Search for "Base SDK" and ensure it's set to "DriverKit" (not macOS)
6. Search for "Deployment Target" and set appropriate version

### Step 2: Fix Test Target

1. Select the test target
2. Go to Build Settings  
3. Ensure Base SDK is macOS (not DriverKit)
4. Go to Build Phases → Link Binary With Libraries
5. Add Testing framework (or XCTest if using older testing approach)
6. Remove any references to the DriverKit target if tests can't compile

### Step 3: Verify File Target Membership

1. Select each Swift file in the project navigator
2. Open the File Inspector (right panel)
3. Check "Target Membership"
4. Ensure:
   - Driver files → DriverKit extension target only
   - Builder files → Builder tool target only
   - Test files → Test target only

### Step 4: Clean Build

```bash
# Clean build folder
rm -rf ~/Library/Developer/Xcode/DerivedData/RTL8814AU*

# Or in Xcode: Product → Clean Build Folder (Shift+Cmd+K)
```

## Additional Resources

- [DriverKit Documentation](https://developer.apple.com/documentation/driverkit)
- [SystemExtensions Documentation](https://developer.apple.com/documentation/systemextensions)  
- [Swift Testing Documentation](https://developer.apple.com/documentation/testing)

## Need More Help?

If errors persist after these fixes:

1. Share your `project.pbxproj` file (or screenshot of target settings)
2. Run `xcodebuild -list` and share the output
3. Check Console.app for additional error details
4. Verify Xcode version: `xcodebuild -version`

---

**Last Updated:** December 27, 2025
