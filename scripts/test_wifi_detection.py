import os
import serial.tools.list_ports as list_ports

def _grep_ports(regexp: str):
    return list(list_ports.grep(regexp))

def is_wifi_board_connected() -> bool:
    # Standard detection via serial ports
    if (len(_grep_ports("ESP32-S2")) > 0
            or len(_grep_ports("CMSIS-DAP")) > 0):
        print("Detected via serial grep (ESP32-S2 or CMSIS-DAP)")
        return True

    # Linux-specific "Ghost USB" detection
    if os.path.exists("/sys/bus/usb/devices"):
        try:
            for device in os.listdir("/sys/bus/usb/devices"):
                vid_path = f"/sys/bus/usb/devices/{device}/idVendor"
                pid_path = f"/sys/bus/usb/devices/{device}/idProduct"
                if os.path.exists(vid_path):
                    with open(vid_path, "r") as f:
                        vid = f.read().strip()
                    if vid == "303a":
                        print(f"Detected via Ghost USB: {device} (VID: {vid})")
                        if os.path.exists(pid_path):
                            with open(pid_path, "r") as f:
                                pid = f.read().strip()
                            print(f"  PID: {pid}")
                        return True
        except Exception as e:
            # print(f"Ghost USB check error: {e}")
            pass
    
    return False

if __name__ == "__main__":
    if is_wifi_board_connected():
        print("Result: WiFi Board IS CONNECTED")
    else:
        print("Result: WiFi Board NOT FOUND")

    print("\nAll serial ports:")
    for p in list_ports.comports():
        vid_val = p.vid if p.vid is not None else 0
        pid_val = p.pid if p.pid is not None else 0
        print(f"  {p.device} - {p.description} (VID: {vid_val:04x}, PID: {pid_val:04x})")
