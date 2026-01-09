import Foundation
import SystemExtensions
import os.log

@main
struct RTL8814AUApp {
    static let logger = Logger(subsystem: "com.rtl8814au.app", category: "main")
    
    static func main() {
        let arguments = CommandLine.arguments
        
        if arguments.count > 1 {
            switch arguments[1] {
            case "install":
                installExtension()
            case "uninstall":
                uninstallExtension()
            default:
                print("Usage: RTL8814AUApp [install|uninstall]")
                exit(1)
            }
        } else {
            // Default: show GUI for installation
            showInstallationInterface()
        }
    }
    
    static func installExtension() {
        logger.info("Installing RTL8814AU system extension...")
        
        let request = OSSystemExtensionRequest.activationRequest(
            forExtensionWithIdentifier: "com.rtl8814au.driver",
            queue: .main
        )
        
        let delegate = ExtensionDelegate()
        request.delegate = delegate
        OSSystemExtensionManager.shared.submitRequest(request)
        
        // Keep running until installation completes
        RunLoop.main.run()
    }
    
    static func uninstallExtension() {
        logger.info("Uninstalling RTL8814AU system extension...")
        
        let request = OSSystemExtensionRequest.deactivationRequest(
            forExtensionWithIdentifier: "com.rtl8814au.driver",
            queue: .main
        )
        
        let delegate = ExtensionDelegate()
        request.delegate = delegate
        OSSystemExtensionManager.shared.submitRequest(request)
        
        // Keep running until uninstallation completes
        RunLoop.main.run()
    }
    
    static func showInstallationInterface() {
        print("RTL8814AU Driver Installer")
        print("=========================")
        print()
        print("This will install the RTL8814AU WiFi driver for macOS.")
        print()
        print("Usage:")
        print("  sudo RTL8814AUApp install    - Install the driver")
        print("  sudo RTL8814AUApp uninstall  - Uninstall the driver")
        print()
        print("After installation, approve the system extension in:")
        print("System Settings > Privacy & Security")
    }
}

// MARK: - Extension Delegate

class ExtensionDelegate: NSObject, OSSystemExtensionRequestDelegate {
    let logger = Logger(subsystem: "com.rtl8814au.app", category: "extension")
    
    func request(_ request: OSSystemExtensionRequest,
                 actionForReplacingExtension existing: OSSystemExtensionProperties,
                 withExtension ext: OSSystemExtensionProperties) -> OSSystemExtensionRequest.ReplacementAction {
        logger.info("Replacing existing extension version \(existing.bundleShortVersion) with \(ext.bundleShortVersion)")
        return .replace
    }
    
    func requestNeedsUserApproval(_ request: OSSystemExtensionRequest) {
        logger.info("Extension requires user approval")
        print("⚠️  User approval required!")
        print("Please approve the system extension in System Settings > Privacy & Security")
    }
    
    func request(_ request: OSSystemExtensionRequest,
                 didFinishWithResult result: OSSystemExtensionRequest.Result) {
        logger.info("Extension request completed with result: \(result.rawValue)")
        
        switch result {
        case .completed:
            print("✅ Extension installed successfully!")
        case .willCompleteAfterReboot:
            print("✅ Extension will be activated after reboot")
            print("Please restart your Mac to complete installation")
        @unknown default:
            print("Extension request completed with unknown result")
        }
        
        exit(0)
    }
    
    func request(_ request: OSSystemExtensionRequest,
                 didFailWithError error: Error) {
        logger.error("Extension request failed: \(error.localizedDescription)")
        print("❌ Extension installation failed: \(error.localizedDescription)")
        exit(1)
    }
}
