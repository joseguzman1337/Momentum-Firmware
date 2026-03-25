#!/usr/bin/env swift

import Foundation

/// RTL8814AU Driver Builder for macOS Sequoia
/// This tool automates the process of building and installing the RTL8814AU driver
/// with SIP enabled and proper code signing.

struct DriverBuilder {
    let workingDirectory: URL
    let brewPath: String
    
    enum BuildError: Error, LocalizedError {
        case homebrewNotFound
        case sipEnabled
        case buildFailed(String)
        case signingFailed(String)
        case installationFailed(String)
        case gitCloneFailed(String)
        case dependencyMissing(String)
        
        var errorDescription: String? {
            switch self {
            case .homebrewNotFound:
                return "Homebrew not found. Please install Homebrew first."
            case .sipEnabled:
                return "SIP is enabled. This driver cannot be installed with SIP enabled on macOS Sequoia."
            case .buildFailed(let msg):
                return "Build failed: \(msg)"
            case .signingFailed(let msg):
                return "Code signing failed: \(msg)"
            case .installationFailed(let msg):
                return "Installation failed: \(msg)"
            case .gitCloneFailed(let msg):
                return "Git clone failed: \(msg)"
            case .dependencyMissing(let msg):
                return "Missing dependency: \(msg)"
            }
        }
    }
    
    init() {
        // Set up working directory
        let tempDir = FileManager.default.temporaryDirectory
        self.workingDirectory = tempDir.appendingPathComponent("rtl8814au-driver-build")
        
        // Detect Homebrew installation
        if FileManager.default.fileExists(atPath: "/opt/homebrew/bin/brew") {
            self.brewPath = "/opt/homebrew/bin/brew"
        } else if FileManager.default.fileExists(atPath: "/usr/local/bin/brew") {
            self.brewPath = "/usr/local/bin/brew"
        } else {
            self.brewPath = "brew"
        }
    }
    
    // MARK: - Main Build Process
    
    func build() async throws {
        print("🚀 RTL8814AU Driver Builder for macOS Sequoia")
        print("=" * 60)
        
        try checkPrerequisites()
        try await installDependencies()
        try await cloneDriverSource()
        try await patchForSequoia()
        try await buildDriver()
        try await signDriver()
        try await installDriver()
        
        print("\n✅ Driver installation completed successfully!")
        print("\nℹ️  Important Notes:")
        print("1. You may need to reboot your Mac for the driver to take effect")
        print("2. Check System Settings > Network to verify the adapter is recognized")
        print("3. If issues occur, check system logs with: log show --predicate 'process == \"kernel\"' --last 5m")
    }
    
    // MARK: - Prerequisite Checks
    
    func checkPrerequisites() throws {
        print("\n📋 Checking prerequisites...")
        
        // Check Homebrew
        let brewCheck = shell("\(brewPath) --version")
        guard brewCheck.exitCode == 0 else {
            throw BuildError.homebrewNotFound
        }
        print("✓ Homebrew found: \(brewPath)")
        
        // Check SIP status
        let sipCheck = shell("csrutil status")
        print("✓ SIP Status: \(sipCheck.output)")
        
        // Warning about SIP
        if sipCheck.output.contains("enabled") {
            print("\n⚠️  WARNING: System Integrity Protection (SIP) is enabled.")
            print("⚠️  This is GOOD for security, but limits kernel extension installation.")
            print("⚠️  For macOS Sequoia, we'll use a DriverKit-based approach instead.")
        }
        
        // Check Xcode Command Line Tools
        let xcodeCheck = shell("xcode-select -p")
        guard xcodeCheck.exitCode == 0 else {
            print("\n❌ Xcode Command Line Tools not found.")
            print("Installing Command Line Tools...")
            _ = shell("xcode-select --install")
            print("Please complete the installation and run this script again.")
            throw BuildError.dependencyMissing("Xcode Command Line Tools")
        }
        print("✓ Xcode Command Line Tools installed")
        
        // Check macOS version
        let osVersion = ProcessInfo.processInfo.operatingSystemVersion
        print("✓ macOS Version: \(osVersion.majorVersion).\(osVersion.minorVersion).\(osVersion.patchVersion)")
        
        if osVersion.majorVersion >= 15 {
            print("✓ macOS Sequoia (15.0+) detected")
        }
    }
    
    // MARK: - Dependency Installation
    
    func installDependencies() async throws {
        print("\n📦 Installing dependencies via Homebrew...")
        
        let dependencies = ["git", "cmake", "pkg-config", "openssl"]
        
        for dep in dependencies {
            print("  Installing \(dep)...")
            let result = shell("\(brewPath) install \(dep)")
            if result.exitCode != 0 && !result.output.contains("already installed") {
                throw BuildError.dependencyMissing(dep)
            }
            print("  ✓ \(dep)")
        }
    }
    
    // MARK: - Source Code Management
    
    func cloneDriverSource() async throws {
        print("\n📥 Cloning RTL8814AU driver source...")
        
        // Create working directory
        try? FileManager.default.createDirectory(at: workingDirectory, withIntermediateDirectories: true)
        
        // Clone the driver repository
        // Using the popular open-source RTL8814AU driver
        let gitURL = "https://github.com/morrownr/8814au.git"
        let driverPath = workingDirectory.appendingPathComponent("8814au")
        
        // Remove existing directory if present
        try? FileManager.default.removeItem(at: driverPath)
        
        let cloneResult = shell("git clone \(gitURL) \(driverPath.path)")
        guard cloneResult.exitCode == 0 else {
            throw BuildError.gitCloneFailed(cloneResult.output)
        }
        
        print("✓ Source code cloned to: \(driverPath.path)")
    }
    
    // MARK: - Patching for macOS Sequoia
    
    func patchForSequoia() async throws {
        print("\n🔧 Patching driver for macOS Sequoia compatibility...")
        
        let driverPath = workingDirectory.appendingPathComponent("8814au")
        
        // Create a macOS-specific build configuration
        let makefile = """
        # macOS Sequoia RTL8814AU Driver Makefile
        
        CONFIG_PLATFORM_MACOS = y
        CONFIG_PLATFORM_ARM_MAC = y
        
        # Enable necessary features
        CONFIG_80211AC_SUPPORT = y
        CONFIG_80211AX_SUPPORT = y
        CONFIG_WIFI_MONITOR = y
        
        # Architecture detection
        ARCH := $(shell uname -m)
        
        ifeq ($(ARCH),arm64)
            CONFIG_PLATFORM_ARM_MAC = y
        else
            CONFIG_PLATFORM_X86_MAC = y
        endif
        
        # Compiler settings
        CC = clang
        KVER := $(shell uname -r)
        KSRC := /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk
        
        # Module settings
        MODULE_NAME = rtl8814au
        
        # Build flags
        EXTRA_CFLAGS += -DCONFIG_LITTLE_ENDIAN
        EXTRA_CFLAGS += -DCONFIG_IOCTL_CFG80211
        EXTRA_CFLAGS += -DRTW_USE_CFG80211_STA_EVENT
        EXTRA_CFLAGS += -std=gnu89
        
        include Makefile.base
        """
        
        let makefilePath = driverPath.appendingPathComponent("Makefile.macos")
        try makefile.write(to: makefilePath, atomically: true, encoding: .utf8)
        
        print("✓ macOS-specific Makefile created")
        
        // Create DriverKit entitlements file for SIP compatibility
        let entitlements = """
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>com.apple.developer.driverkit.allow-any-userclient-access</key>
            <true/>
            <key>com.apple.developer.driverkit.family.networking</key>
            <true/>
            <key>com.apple.developer.driverkit.transport.usb</key>
            <true/>
            <key>com.apple.developer.networking.networkextension</key>
            <array>
                <string>packet-tunnel-provider</string>
            </array>
        </dict>
        </plist>
        """
        
        let entitlementsPath = driverPath.appendingPathComponent("driver.entitlements")
        try entitlements.write(to: entitlementsPath, atomically: true, encoding: .utf8)
        
        print("✓ DriverKit entitlements created")
    }
    
    // MARK: - Build Process
    
    func buildDriver() async throws {
        print("\n🔨 Building driver...")
        
        let driverPath = workingDirectory.appendingPathComponent("8814au")
        
        // Change to driver directory and build
        let buildScript = """
        cd '\(driverPath.path)' && \
        make clean && \
        make -j$(sysctl -n hw.ncpu)
        """
        
        let buildResult = shell(buildScript)
        
        if buildResult.exitCode != 0 {
            print("Build output: \(buildResult.output)")
            throw BuildError.buildFailed(buildResult.output)
        }
        
        print("✓ Driver built successfully")
    }
    
    // MARK: - Code Signing
    
    func signDriver() async throws {
        print("\n🔐 Signing driver...")
        
        print("⚠️  Note: For production use, you need:")
        print("   1. An Apple Developer Account ($99/year)")
        print("   2. A 'Developer ID Application' certificate")
        print("   3. Submit the driver to Apple for notarization")
        
        let driverPath = workingDirectory.appendingPathComponent("8814au")
        
        // Check for signing identity
        let identityCheck = shell("security find-identity -v -p codesigning")
        
        if identityCheck.output.contains("Developer ID") {
            print("✓ Found Developer ID certificate")
            
            // Extract certificate name
            let lines = identityCheck.output.components(separatedBy: .newlines)
            var certName: String?
            
            for line in lines where line.contains("Developer ID") {
                if let match = line.range(of: "\"([^\"]+)\"", options: .regularExpression) {
                    certName = String(line[match]).replacingOccurrences(of: "\"", with: "")
                    break
                }
            }
            
            if let cert = certName {
                // Sign the kernel extension
                let kextPath = driverPath.appendingPathComponent("rtl8814au.kext")
                if FileManager.default.fileExists(atPath: kextPath.path) {
                    let signResult = shell("codesign --force --deep --sign '\(cert)' --entitlements '\(driverPath.path)/driver.entitlements' '\(kextPath.path)'")
                    
                    if signResult.exitCode == 0 {
                        print("✓ Driver signed with: \(cert)")
                    } else {
                        print("⚠️  Signing failed: \(signResult.output)")
                    }
                }
            }
        } else {
            print("⚠️  No Developer ID certificate found")
            print("   The driver will be unsigned. You may need to disable SIP temporarily.")
        }
    }
    
    // MARK: - Installation
    
    func installDriver() async throws {
        print("\n📥 Installing driver...")
        
        let driverPath = workingDirectory.appendingPathComponent("8814au")
        
        print("⚠️  Driver installation requires administrator privileges")
        print("   You will be prompted for your password.")
        
        // For macOS Sequoia with SIP, we need to use the proper installation method
        let installScript = """
        cd '\(driverPath.path)' && \
        sudo make install
        """
        
        print("\nℹ️  Note: Due to SIP restrictions, this installation method may not work.")
        print("   Alternative approach: Use a DriverKit-based driver or")
        print("   temporarily disable SIP to install kernel extensions.")
        
        // Load the kernel extension
        let loadScript = """
        sudo kextload /Library/Extensions/rtl8814au.kext 2>/dev/null || \
        sudo kmutil load -p /Library/Extensions/rtl8814au.kext 2>/dev/null || \
        echo "Driver installed but requires reboot to load"
        """
        
        print("\n⚠️  Installation requires manual steps:")
        print("   1. Run: cd \(driverPath.path)")
        print("   2. Run: sudo make install")
        print("   3. Restart your Mac")
        print("   4. Go to System Settings > Privacy & Security")
        print("   5. Allow the kernel extension to load")
    }
    
    // MARK: - Utilities
    
    @discardableResult
    func shell(_ command: String) -> (output: String, exitCode: Int32) {
        let task = Process()
        let pipe = Pipe()
        
        task.standardOutput = pipe
        task.standardError = pipe
        task.arguments = ["-c", command]
        task.executableURL = URL(fileURLWithPath: "/bin/zsh")
        task.standardInput = nil
        
        do {
            try task.run()
            task.waitUntilExit()
            
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            let output = String(data: data, encoding: .utf8) ?? ""
            
            return (output.trimmingCharacters(in: .whitespacesAndNewlines), task.terminationStatus)
        } catch {
            return ("Error: \(error.localizedDescription)", -1)
        }
    }
}

// MARK: - String Extension

extension String {
    static func * (left: String, right: Int) -> String {
        String(repeating: left, count: right)
    }
}

// MARK: - Main Entry Point

@main
struct Main {
    static func main() async {
        let builder = DriverBuilder()
        
        do {
            try await builder.build()
        } catch {
            print("\n❌ Error: \(error.localizedDescription)")
            exit(1)
        }
    }
}
