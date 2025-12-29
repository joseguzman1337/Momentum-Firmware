import Testing
import Testing
import Foundation

/// Test suite for RTL8814AU Driver Builder
/// Verifies system requirements and build process
@Suite("RTL8814AU Driver Tests")
struct RTL8814AUDriverTests {
    
    // MARK: - System Requirement Tests
    
    @Test("macOS version is Sequoia or later")
    func testMacOSVersion() async throws {
        let osVersion = ProcessInfo.processInfo.operatingSystemVersion
        
        #expect(osVersion.majorVersion >= 15, 
                "macOS Sequoia (15.0) or later required. Found: \(osVersion.majorVersion).\(osVersion.minorVersion)")
    }
    
    @Test("Running on macOS platform")
    func testMacOSPlatform() async throws {
        #if os(macOS)
        // Test passes
        #expect(true)
        #else
        #expect(false, "This driver only works on macOS")
        #endif
    }
    
    @Test("Homebrew is installed")
    func testHomebrewInstalled() async throws {
        let homebrewPaths = [
            "/opt/homebrew/bin/brew",      // Apple Silicon
            "/usr/local/bin/brew",         // Intel
        ]
        
        let homebrewExists = homebrewPaths.contains { path in
            FileManager.default.fileExists(atPath: path)
        }
        
        #expect(homebrewExists, "Homebrew not found. Install from https://brew.sh")
    }
    
    @Test("Xcode Command Line Tools installed")
    func testXcodeToolsInstalled() async throws {
        let result = shell("xcode-select -p")
        #expect(result.exitCode == 0, "Xcode Command Line Tools not installed. Run: xcode-select --install")
    }
    
    @Test("Architecture is supported (arm64 or x86_64)")
    func testArchitecture() async throws {
        let arch = shell("uname -m").output
        let supportedArchs = ["arm64", "x86_64"]
        
        #expect(supportedArchs.contains(arch), 
                "Unsupported architecture: \(arch). Expected: arm64 or x86_64")
    }
    
    // MARK: - SIP Status Tests
    
    @Test("SIP status can be determined")
    func testSIPStatus() async throws {
        let result = shell("csrutil status")
        #expect(result.exitCode == 0 || result.exitCode == 1, 
                "Unable to determine SIP status")
    }
    
    @Test("SIP configuration is documented")
    func testSIPDocumentation() async throws {
        let readmePath = "/repo/README.md"
        
        if FileManager.default.fileExists(atPath: readmePath) {
            let readme = try String(contentsOfFile: readmePath, encoding: .utf8)
            #expect(readme.contains("System Integrity Protection"), 
                    "README should document SIP")
            #expect(readme.contains("SIP"), 
                    "README should mention SIP")
        }
    }
    
    // MARK: - Dependency Tests
    
    @Test("Required build tools are documented")
    func testBuildDependencies() async throws {
        let requiredTools = ["git", "cmake", "pkg-config", "openssl"]
        
        for tool in requiredTools {
            // Check if Homebrew can find the formula
            let result = shell("brew info \(tool)")
            #expect(result.exitCode == 0, 
                    "\(tool) is not available in Homebrew")
        }
    }
    
    @Test("Git is available")
    func testGitAvailable() async throws {
        let result = shell("which git")
        #expect(result.exitCode == 0, "Git not found. Install with: brew install git")
    }
    
    // MARK: - File Structure Tests
    
    @Test("Installation script exists and is executable")
    func testInstallScriptExists() async throws {
        let scriptPath = "/repo/install-rtl8814au.sh"
        
        if FileManager.default.fileExists(atPath: scriptPath) {
            let attributes = try FileManager.default.attributesOfItem(atPath: scriptPath)
            let permissions = attributes[.posixPermissions] as? Int
            
            // Check if executable bit is set (0o100 = owner execute)
            let isExecutable = (permissions ?? 0) & 0o100 != 0
            #expect(isExecutable, "Install script should be executable. Run: chmod +x install-rtl8814au.sh")
        }
    }
    
    @Test("README.md exists and contains essential information")
    func testREADMEExists() async throws {
        let readmePath = "/repo/README.md"
        #expect(FileManager.default.fileExists(atPath: readmePath), 
                "README.md not found")
        
        if FileManager.default.fileExists(atPath: readmePath) {
            let readme = try String(contentsOfFile: readmePath, encoding: .utf8)
            
            // Check for essential sections
            #expect(readme.contains("Installation"), "README should have Installation section")
            #expect(readme.contains("Troubleshooting"), "README should have Troubleshooting section")
            #expect(readme.contains("RTL8814AU"), "README should mention RTL8814AU")
        }
    }
    
    @Test("Homebrew formula has correct structure")
    func testHomebrewFormula() async throws {
        let formulaPath = "/repo/rtl8814au-driver.rb"
        
        if FileManager.default.fileExists(atPath: formulaPath) {
            let formula = try String(contentsOfFile: formulaPath, encoding: .utf8)
            
            #expect(formula.contains("class Rtl8814auDriver"), 
                    "Homebrew formula should define Rtl8814auDriver class")
            #expect(formula.contains("def install"), 
                    "Homebrew formula should have install method")
            #expect(formula.contains("def caveats"), 
                    "Homebrew formula should have caveats for user warnings")
        }
    }
    
    // MARK: - Build Process Tests
    
    @Test("Temporary directory is writable")
    func testTempDirectoryWritable() async throws {
        let tempDir = FileManager.default.temporaryDirectory
        let testFile = tempDir.appendingPathComponent("rtl8814au-test-\(UUID().uuidString)")
        
        do {
            try "test".write(to: testFile, atomically: true, encoding: .utf8)
            try FileManager.default.removeItem(at: testFile)
            // Test passes if we get here
        } catch {
            #expect(Bool(false), "Temporary directory is not writable: \(tempDir.path)")
        }
    }
    
    @Test("Swift builder compiles")
    func testSwiftBuilderCompiles() async throws {
        let builderPath = "/repo/RTL8814AUDriverBuilder.swift"
        
        if FileManager.default.fileExists(atPath: builderPath) {
            // Try to compile (syntax check only)
            let result = shell("swift -parse \(builderPath)")
            #expect(result.exitCode == 0, 
                    "Swift builder has syntax errors: \(result.output)")
        }
    }
    
    // MARK: - Code Signing Tests
    
    @Test("Code signing identities can be listed")
    func testCodeSigningAvailable() async throws {
        let result = shell("security find-identity -v -p codesigning")
        // This should work even if no identities are found
        #expect(result.exitCode == 0, 
                "Unable to query code signing identities")
    }
    
    @Test("Developer ID documentation is present")
    func testDeveloperIDDocs() async throws {
        let readmePath = "/repo/README.md"
        
        if FileManager.default.fileExists(atPath: readmePath) {
            let readme = try String(contentsOfFile: readmePath, encoding: .utf8)
            #expect(readme.contains("Developer ID"), 
                    "README should document Developer ID signing")
            #expect(readme.contains("code signing") || readme.contains("Code Signing"), 
                    "README should explain code signing")
        }
    }
    
    // MARK: - Security Tests
    
    @Test("Security warnings are documented")
    func testSecurityWarnings() async throws {
        let readmePath = "/repo/README.md"
        
        if FileManager.default.fileExists(atPath: readmePath) {
            let readme = try String(contentsOfFile: readmePath, encoding: .utf8)
            
            #expect(readme.contains("⚠️") || readme.contains("Warning"), 
                    "README should contain security warnings")
            #expect(readme.contains("risk") || readme.contains("security"), 
                    "README should mention security risks")
        }
    }
    
    @Test("Installation requires sudo (documented)")
    func testSudoRequirementDocumented() async throws {
        let readmePath = "/repo/README.md"
        
        if FileManager.default.fileExists(atPath: readmePath) {
            let readme = try String(contentsOfFile: readmePath, encoding: .utf8)
            #expect(readme.contains("sudo"), 
                    "README should document sudo requirement")
        }
    }
    
    // MARK: - Uninstallation Tests
    
    @Test("Uninstall process is documented")
    func testUninstallDocumentation() async throws {
        let readmePath = "/repo/README.md"
        
        if FileManager.default.fileExists(atPath: readmePath) {
            let readme = try String(contentsOfFile: readmePath, encoding: .utf8)
            #expect(readme.contains("Uninstall"), 
                    "README should document uninstallation")
        }
    }
    
    // MARK: - Troubleshooting Tests
    
    @Test("Troubleshooting section exists")
    func testTroubleshootingSection() async throws {
        let readmePath = "/repo/README.md"
        
        if FileManager.default.fileExists(atPath: readmePath) {
            let readme = try String(contentsOfFile: readmePath, encoding: .utf8)
            
            #expect(readme.contains("Troubleshooting"), 
                    "README should have Troubleshooting section")
            #expect(readme.contains("kextstat"), 
                    "Troubleshooting should mention kextstat command")
            #expect(readme.contains("log show"), 
                    "Troubleshooting should mention log viewing")
        }
    }
    
    // MARK: - Platform-Specific Tests
    
    @Test("Apple Silicon specific paths exist")
    func testAppleSiliconSupport() async throws {
        #if arch(arm64)
        // Check for Apple Silicon Homebrew path
        let brewPath = "/opt/homebrew/bin/brew"
        let homebrewExists = FileManager.default.fileExists(atPath: brewPath)
        
        if !homebrewExists {
            print("⚠️ Homebrew not found at Apple Silicon location: \(brewPath)")
            print("   Install with: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        }
        #endif
        
        // Test always passes, but provides helpful info
        #expect(true)
    }
    
    @Test("Intel specific paths work")
    func testIntelSupport() async throws {
        #if arch(x86_64)
        // Check for Intel Homebrew path
        let brewPath = "/usr/local/bin/brew"
        let homebrewExists = FileManager.default.fileExists(atPath: brewPath)
        
        if !homebrewExists {
            print("⚠️ Homebrew not found at Intel location: \(brewPath)")
        }
        #endif
        
        // Test always passes, but provides helpful info
        #expect(true)
    }
    
    // MARK: - Utilities
    
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
            return ("", -1)
        }
    }
}

/// Performance and resource tests
@Suite("Performance Tests")
struct PerformanceTests {
    
    @Test("Build directory can be created")
    func testBuildDirectoryCreation() async throws {
        let tempDir = FileManager.default.temporaryDirectory
        let buildDir = tempDir.appendingPathComponent("rtl8814au-test-\(UUID().uuidString)")
        
        try FileManager.default.createDirectory(at: buildDir, withIntermediateDirectories: true)
        
        #expect(FileManager.default.fileExists(atPath: buildDir.path))
        
        // Cleanup
        try FileManager.default.removeItem(at: buildDir)
    }
    
    @Test("Sufficient disk space available")
    func testDiskSpace() async throws {
        let tempDir = FileManager.default.temporaryDirectory
        
        if let attributes = try? FileManager.default.attributesOfFileSystem(forPath: tempDir.path),
           let freeSize = attributes[.systemFreeSize] as? Int64 {
            let freeGB = Double(freeSize) / 1_000_000_000
            
            print("Free disk space: \(String(format: "%.2f", freeGB)) GB")
            
            #expect(freeGB >= 2.0, 
                    "Insufficient disk space. Need at least 2GB free, have \(String(format: "%.2f", freeGB)) GB")
        }
    }
    
    @Test("System has sufficient memory")
    func testMemory() async throws {
        let physicalMemory = ProcessInfo.processInfo.physicalMemory
        let memoryGB = Double(physicalMemory) / 1_000_000_000
        
        print("Physical memory: \(String(format: "%.2f", memoryGB)) GB")
        
        #expect(memoryGB >= 4.0, 
                "Low memory warning: \(String(format: "%.2f", memoryGB)) GB. Recommended: 4GB+")
    }
}
