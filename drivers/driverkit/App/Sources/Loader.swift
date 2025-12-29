import Cocoa
import SystemExtensions

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Submit the request immediately on launch
        let request = OSSystemExtensionRequest.activationRequest(
            forExtensionWithIdentifier: "com.realtek.driver",
            queue: .main
        )
        request.delegate = self
        OSSystemExtensionManager.shared.submitRequest(request)
        
        // Optional: Show an initial popup explaining what is happening
        // (Blocking here might delay the request submission if not careful, but Submit is async)
        // Let's rely on the delegate callbacks for specific state prompts to be less annoying,
        // unless the user explicitly wants a "guide" popup first. 
        // The Prompt in 'requestNeedsUserApproval' is the critical one.
    }
}

extension AppDelegate: OSSystemExtensionRequestDelegate {
    
    // Successful installation/activation
    func request(_ request: OSSystemExtensionRequest, didFinishWithResult result: OSSystemExtensionRequest.Result) {
        let title = "Driver Installed"
        let msg = "The RTL88xxAU DriverKit extension was successfully installed and activated."
        runAlert(title: title, message: msg)
        NSApp.terminate(nil)
    }

    // Failed installation
    func request(_ request: OSSystemExtensionRequest, didFailWithError error: Error) {
        // If we are approved but fail for another reason
        let title = "Installation Failed"
        let msg = "Error: \(error.localizedDescription)\n\nPlease ensure you have a valid Provisioning Profile if SIP is enabled."
        runAlert(title: title, message: msg)
        NSApp.terminate(nil)
    }

    // macOS requires user approval (SIP enabled)
    func requestNeedsUserApproval(_ request: OSSystemExtensionRequest) {
        // User requested to avoid the extra "allow" step popup.
        // We directly open the Settings pane where they need to click Allow.
        // URL for macOS Sequoia / Ventura+
        if let url = URL(string: "x-apple.systempreferences:com.apple.LoginItems-Settings.extension") {
            NSWorkspace.shared.open(url)
        } else if let url = URL(string: "x-apple.systempreferences:com.apple.preference.security?General") {
            NSWorkspace.shared.open(url)
        }
        // We do typically need to keep the app running until approval logic completes.
    }

    // Replacing an existing version
    func request(_ request: OSSystemExtensionRequest, actionForReplacingExtension existing: OSSystemExtensionProperties, withExtension ext: OSSystemExtensionProperties) -> OSSystemExtensionRequest.ReplacementAction {
        let title = "Update Driver"
        let msg = "A previous version of the driver is installed. Would you like to replace it?"
        let alert = NSAlert()
        alert.messageText = title
        alert.informativeText = msg
        alert.addButton(withTitle: "Replace")
        alert.addButton(withTitle: "Cancel")
        
        let response = alert.runModal()
        return (response == .alertFirstButtonReturn) ? .replace : .cancel
    }
    
    // Helper for simple alerts
    func runAlert(title: String, message: String) {
        let alert = NSAlert()
        alert.messageText = title
        alert.informativeText = message
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
