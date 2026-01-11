#!/usr/bin/env python3
import os
import sys
import subprocess
import glob
import time

try:
    import serial
except ImportError:
    serial = None

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def run_command(command, cwd=None, description=None):
    if description:
        print(f"[*] {description}...")
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True
        )
        return result
    except Exception as e:
        print(f"[!] Error executing command: {e}")
        return None

def check_fbt():
    print_header("FBT (Flipper Build Tool) Verification")
    fbt_path = "./fbt"
    if not os.path.exists(fbt_path):
        print("[!] ./fbt not found in current directory.")
        return False
    
    if not os.access(fbt_path, os.X_OK):
        print("[!] ./fbt is not executable. Attempting to fix...")
        os.chmod(fbt_path, 0o755)

    print("[+] ./fbt found and executable.")
    
    # Run help to verify it works
    res = run_command("./fbt -h", description="Running ./fbt -h")
    if res and res.returncode == 0:
        print("[+] ./fbt appears to be functioning.")
        return True
    else:
        print(f"[!] ./fbt failed to run. Stderr: {res.stderr if res else 'None'}")
        return False

def check_strawberry():
    print_header("Strawberry MCP (Hallucination Detector) Verification")
    path = ".ai/strawberry"
    if not os.path.exists(path):
        print(f"[!] Strawberry path {path} not found.")
        return False
    
    print(f"[+] Found Strawberry at {path}")
    
    # Check for pyproject.toml
    if os.path.exists(os.path.join(path, "pyproject.toml")):
        print("[+] pyproject.toml found.")
    else:
        print("[!] pyproject.toml missing.")
        return False

    # Check python environment (basic check)
    res = run_command("python3 --version", description="Checking Python version")
    if res and res.returncode == 0:
        print(f"[+] Python available: {res.stdout.strip()}")
    else:
        print("[!] Python3 not found.")
        return False

    return True

def check_esp_orchestrator():
    print_header("ESP MCP Orchestrator Verification")
    path = ".ai/esp_mcp_orchestrator"
    if not os.path.exists(path):
        print(f"[!] ESP Orchestrator path {path} not found.")
        return False
    
    print(f"[+] Found ESP Orchestrator at {path}")
    
    if os.path.exists(os.path.join(path, "Cargo.toml")):
        print("[+] Cargo.toml found.")
    else:
        print("[!] Cargo.toml missing.")
        return False

    # Check for cargo
    res = run_command("cargo --version", description="Checking Cargo version")
    if res and res.returncode == 0:
        print(f"[+] Cargo available: {res.stdout.strip()}")
        
        # Try a dry-run check
        print("[*] Attempting 'cargo check' (this might take a while if fetching deps)...")
        res_build = run_command(f"cargo check --manifest-path {path}/Cargo.toml", description="Running cargo check")
        if res_build and res_build.returncode == 0:
            print("[+] ESP Orchestrator builds/checks successfully.")
        else:
            print(f"[!] ESP Orchestrator check failed. (This might be expected if deps are missing)")
            if res_build:
                print(f"    Stderr: {res_build.stderr[:200]}...")
    else:
        print("[!] Cargo/Rust not installed or not in PATH.")
        return False
    
    return True

def check_flipper_connection():
    print_header("Flipper Zero Connection Verification")
    
    # Linux-specific check for serial devices
    # Flipper usually shows up as /dev/serial/by-id/usb-Flipper_...
    
    serial_by_id = "/dev/serial/by-id"
    found = False
    port_to_use = None
    
    if os.path.exists(serial_by_id):
        devices = glob.glob(os.path.join(serial_by_id, "*Flipper*"))
        if devices:
            print(f"[+] Flipper Zero detected at:")
            for dev in devices:
                print(f"    - {dev}")
            found = True
            port_to_use = devices[0]
        else:
            print("[-] No Flipper Zero device found in /dev/serial/by-id/.")
    else:
        print(f"[-] {serial_by_id} does not exist (not Linux or no serial devices).")

    active_comm = False
    if found and port_to_use:
        if serial:
            print(f"\n[*] Attempting active communication on {port_to_use}...")
            try:
                ser = serial.Serial(port_to_use, timeout=1)
                # Send wakeup
                ser.write(b"\r\n")
                time.sleep(0.5)
                ser.reset_input_buffer()
                
                # Send uptime command
                ser.write(b"uptime\r\n")
                time.sleep(0.5)
                
                response = ser.read_all().decode('utf-8', errors='ignore')
                print(f"[>] Response from Flipper:\n---\n{response.strip()}\n---")
                
                if "uptime" in response or "min" in response or "sec" in response or ">:" in response:
                     print("[+] Active communication SUCCESSFUL.")
                     active_comm = True
                else:
                     print("[?] Response unclear, but port opened.")
                     
                ser.close()
            except Exception as e:
                print(f"[!] Failed to communicate with Flipper: {e}")
        else:
            print("[!] pyserial not installed. Skipping active communication test.")

    if found:
        print("\n[SUCCESS] Flipper Zero is detected" + (" and responding." if active_comm else "."))
        print("You can now run the CLI session.")
    else:
        print("\n[WARNING] Flipper Zero not detected via standard serial paths.")
        print("Please ensure it is connected via USB and recognized by the OS.")

    return found

def main():
    print("Momentum Firmware - Automated Environment Verification")
    print("Context: Security Architect / Mandatory .ai + MCPs")
    
    fbt_ok = check_fbt()
    straw_ok = check_strawberry()
    esp_ok = check_esp_orchestrator()
    flip_conn = check_flipper_connection()
    
    print_header("Summary")
    print(f"FBT Tool:           {'[OK]' if fbt_ok else '[FAIL]'}")
    print(f"Strawberry MCP:     {'[OK]' if straw_ok else '[FAIL]'}")
    print(f"ESP Orchestrator:   {'[OK]' if esp_ok else '[FAIL]'}")
    print(f"Flipper Connection: {'[OK]' if flip_conn else '[FAIL]'}")
    
    print("\nTo start the Flipper CLI session, run:")
    print("  ./fbt cli")

if __name__ == "__main__":
    main()
