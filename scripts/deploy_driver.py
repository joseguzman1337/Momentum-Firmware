import os
import subprocess
import sys
import threading
import time
import re

def run_command(command, shell=False):
    print(f"Running: {' '.join(command) if isinstance(command, list) else command}")
    try:
        subprocess.check_call(command, shell=shell)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        # Build failures should stop us, but load failures might be expected if user needs to interact with UI
        if "xcodebuild" in str(command):
            sys.exit(1)

def get_signing_identity():
    try:
        output = subprocess.check_output(["security", "find-identity", "-v", "-p", "codesigning"], text=True)
        # Look for the first line with a hex ID
        for line in output.splitlines():
            if "valid identities found" in line:
                continue
            parts = line.strip().split()
            if len(parts) >= 2 and len(parts[1]) == 40: # crude check for SHA1
                return parts[1]
    except Exception as e:
        print(f"Could not find signing identity: {e}")
    return None

def resign_kext(path, identity):
    print(f"Resigning {path} with {identity}...")
    try:
        # We strip entitlements by NOT including --entitlements
        subprocess.check_call(["codesign", "--force", "--sign", identity, "--deep", path])
        print("Resign successful.")
    except subprocess.CalledProcessError as e:
        print(f"Resign failed: {e}")

def build_and_load_driverkit():
    cwd = os.path.dirname(os.path.abspath(__file__))
    # Point to the drivers directory where the DriverKit Makefile resides
    drivers_dir = os.path.join(cwd, "../drivers")
    
    print(f"--- [Deploy] Switching to DriverKit deployment in {drivers_dir} ---")
    
    # Check if Makefile exists
    if not os.path.exists(os.path.join(drivers_dir, "Makefile")):
        print(f"Error: Makefile not found in {drivers_dir}")
        return False

    # Get identity to pass to Make (overriding the hardcoded one if needed, though Make has it)
    identity = get_signing_identity()
    env = os.environ.copy()
    if identity:
        print(f"Wrapper: Using Signing Identity: {identity}")
        # We could pass this to make if we edited the Makefile to accept var, 
        # but the Makefile currently hardcodes it or we can rely on it being correct.
        # For now, we trust 'make install' to do the right thing as validated previously.

    cmd = ["make", "install"]
    
    try:
        # Run make install which builds the App/Dext and opens it
        subprocess.check_call(cmd, cwd=drivers_dir, env=env)
        print("--- [Deploy] DriverKit App Installed and Launched ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"DriverKit deployment failed: {e}")
        return False

class LogMonitor:
    def __init__(self):
        self.process = None
        self.stop_event = threading.Event()
        self.error_detected = False
        self.policy_blocked = False
        self.load_success = False

    def start(self):
        # Monitor logs for our driver, kernel extension manager, and system extension daemon
        cmd = [
            "log", "stream", 
            "--predicate", 
            'senderImagePath contains "realtek" OR eventMessage contains "realtek" OR process == "kernel" OR process == "sysextd"', 
            "--style", "syslog",
            "--timeout", "60" # Auto-stop after 60s to prevent hanging
        ]
        
        def run_monitor():
            print("--- [Real-Time Debug] Log Monitor Started ---")
            self.process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1
            )
            
            while not self.stop_event.is_set():
                line = self.process.stdout.readline()
                if not line:
                    break
                
                # Analyze line for key events
                if "Bad code signature" in line or "code signature validity" in line:
                    self.error_detected = True
                    print(f"!!! [DEBUG] Signature Error Detected: {line.strip()}")
                elif "System Policy: allowed" in line:
                    print(f"+++ [DEBUG] Policy Allowed: {line.strip()}")
                elif "blocked" in line and "extension" in line:
                    self.policy_blocked = True
                    print(f"!!! [DEBUG] System Policy Blocked Load: {line.strip()}")
                elif "successfully loaded" in line or "Load succeeded" in line:
                    self.load_success = True
                    print(f"+++ [DEBUG] Driver Loaded Successfully: {line.strip()}")
                
                # Print relevant lines to console
                if "realtek" in line.lower():
                    print(f"[LOG] {line.strip()}")

        self.thread = threading.Thread(target=run_monitor)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.process:
            self.process.terminate()
            print("--- [Real-Time Debug] Log Monitor Stopped ---")

def main():
    print("--- [Setup] Enabling System Extension Developer Mode (Required for SIP) ---")
    try:
        # Enable Developer Mode (requires admin privileges, prompted via osascript)
        script = 'do shell script "systemextensionsctl developer on" with administrator privileges'
        subprocess.check_call(["osascript", "-e", script])
        print("Developer Mode Enabled.")
    except subprocess.CalledProcessError:
        print("Warning: Failed to enable Developer Mode. User cancel or error. SIP might block the extension.")

    monitor = LogMonitor()
    monitor.start()
    
    try:
        # We now use the DriverKit workflow instead of the legacy kext workflow
        success = build_and_load_driverkit()
        
        if success:
            # Check for immediate errors from the monitor
            time.sleep(2) 
            
            if monitor.error_detected:
                print(">>> [AUTO-FIX] Checks detected an issue. Ensure SIP is configured or Identity is valid.")
            
            # The App (RTLLoader) now handles the UI/Settings logic internally.
            
            if monitor.policy_blocked:
                 print(">>> [STATUS] System Extension Blocked. Manual approval required in Settings.")
            
            print("App launched. Waiting for manual approval in System Settings...")
            time.sleep(5) 
        else:
            print("Deployment failed.")
            sys.exit(1)
            
    finally:
        monitor.stop()

if __name__ == "__main__":
    main()
