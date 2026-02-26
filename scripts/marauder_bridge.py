#!/usr/bin/env python3
import sys
import os
import time
import argparse
import logging
import re
import json
import cmd

# Add scripts directory to path for flipper imports
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
from flipper.utils.cdc import resolve_port
from flipper.storage import FlipperStorage

# ANSI Colors for a "Cyberpunk" aesthetic
CLR = {
    "R": "\033[0;31m",
    "G": "\033[0;32m",
    "Y": "\033[0;33m",
    "B": "\033[0;34m",
    "M": "\033[0;35m",
    "C": "\033[0;36m",
    "W": "\033[0;37m",
    "BOLD": "\033[1m",
    "RESET": "\033[0m",
    "BG": "\033[44m",
    "BR_G": "\033[1;32m",
    "ORNG": "\033[38;5;208m",
    "PURP": "\033[38;5;141m",
    "CYAN": "\033[38;5;51m",
    "GRAY": "\033[38;5;245m",
    "UL": "\033[4m"
}

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class MarauderTable:
    @staticmethod
    def get_rssi_color(rssi):
        try:
            r = int(rssi)
            if r >= -50: return CLR["BR_G"]
            if r >= -60: return CLR["G"]
            if r >= -70: return CLR["Y"]
            if r >= -80: return CLR["ORNG"]
            return CLR["R"]
        except: return CLR["W"]

    @staticmethod
    def format(data, headers, sort_by=None, reverse=True, title=None):
        if not data:
            return f"{CLR['Y']}[!] No data available.{CLR['RESET']}"
        
        # Determine sorting
        if sort_by and sort_by.lower() in [h.lower() for h in headers]:
            actual_key = next((h for h in headers if h.lower() == sort_by.lower()), None)
            if actual_key:
                try:
                    data = sorted(data, key=lambda x: x.get(actual_key, 0) if isinstance(x.get(actual_key), (int, float)) else str(x.get(actual_key, "")), reverse=reverse)
                except:
                    pass
        
        # Auto-calculate dynamic widths
        widths = {h: len(h) for h in headers}
        for row in data:
            for h in headers:
                val = str(row.get(h, ""))
                widths[h] = max(widths[h], len(val))
        
        # Build Table Components
        total_content_width = sum(widths.values()) + (len(headers) * 3) - 1
        
        output = []
        if title:
            output.append(f" {CLR['BOLD']}{CLR['PURP']}» {title.upper()} «{CLR['RESET']}")
            
        top = " " + CLR["CYAN"] + "╔" + "═" * (total_content_width + 2) + "╗" + CLR["RESET"]
        header_cells = [f"{CLR['BOLD']}{CLR['C']}{h.upper().center(widths[h])}{CLR['RESET']}" for h in headers]
        head = " " + CLR["CYAN"] + "║ " + f" {CLR['GRAY']}│{CLR['CYAN']} ".join(header_cells) + " ║" + CLR["RESET"]
        mid = " " + CLR["CYAN"] + "╟" + "─" * (total_content_width + 2) + "╢" + CLR["RESET"]
        bot = " " + CLR["CYAN"] + "╚" + "═" * (total_content_width + 2) + "╝" + CLR["RESET"]
        
        output.extend([top, head, mid])
        for row in data:
            cells = []
            for h in headers:
                val = str(row.get(h, ""))
                h_low = h.lower()
                if h_low == "rssi":
                    cells.append(f"{MarauderTable.get_rssi_color(val)}{val.rjust(widths[h])}{CLR['RESET']}")
                elif h_low == "ssid":
                    cells.append(f"{CLR['BOLD']}{val.ljust(widths[h])}{CLR['RESET']}")
                elif h_low in ["bssid", "mac"]:
                    cells.append(f"{CLR['PURP']}{val.ljust(widths[h])}{CLR['RESET']}")
                elif h_low in ["ch", "channel"]:
                    cells.append(f"{CLR['Y']}{val.center(widths[h])}{CLR['RESET']}")
                elif h_low == "status":
                    color = CLR["BR_G"] if "ON" in val.upper() or "ENABLED" in val.upper() else CLR["R"]
                    cells.append(f"{color}{val.center(widths[h])}{CLR['RESET']}")
                else:
                    cells.append(val.ljust(widths[h]))
            output.append(" " + CLR["CYAN"] + "║ " + f" {CLR['GRAY']}│{CLR['CYAN']} ".join(cells) + " ║" + CLR["RESET"])
        
        output.append(bot)
        return "\n".join(output)

class MarauderInterface:
    def __init__(self, port):
        self.port = port
        self.temp_js = "/ext/marauder_bridge_tmp.js"

    def execute_command(self, cmd, wait_ms=5000):
        js_payload = f"""
let s = require("serial");
s.setup("usart", 115200);
s.write("{cmd}\\r\\n");
for (let i = 0; i < {(wait_ms // 200) + 10}; i++) {{
    let data = s.readAny(200);
    if (data) print(data);
}}
s.end();
"""
        with FlipperStorage(self.port) as storage:
            storage.send('\x03\x03')
            time.sleep(0.2)
            storage.send("loader close\r\n")
            time.sleep(0.5)
            storage.read.until(storage.CLI_PROMPT)
            
            storage.start()
            with open("marauder_tmp.js", "w") as f:
                f.write(js_payload)
            storage.send_file("marauder_tmp.js", self.temp_js)
            os.remove("marauder_tmp.js")
            
            storage.send(f"js {self.temp_js}\r\n")
            output = storage.read.until(storage.CLI_PROMPT).decode('ascii', 'ignore')
            
            storage.remove(self.temp_js)
            
            capture = False
            result_lines = []
            for line in output.splitlines():
                if "Running script" in line:
                    capture = True
                    continue
                if "Script done" in line:
                    break
                if capture:
                    result_lines.append(line)
            
            return "\n".join(result_lines).strip()

    def list_aps(self):
        raw = self.execute_command("list -a")
        aps = []
        # pattern matches [idx] [CH: ch] SSID BSSID RSSI
        pattern = re.compile(r"\[(\d+)\]\s*\[CH:\s*(\d+)\]\s*(.*?)\s+([0-9A-F:]{17})\s+(-?\d+)")
        for line in raw.splitlines():
            match = pattern.search(line)
            if match:
                idx, ch, ssid, bssid, rssi = match.groups()
                aps.append({
                    "idx": int(idx),
                    "ch": int(ch),
                    "ssid": ssid.strip() or "<Hidden>",
                    "bssid": bssid,
                    "rssi": int(rssi)
                })
        return aps

    def list_stations(self):
        raw = self.execute_command("list -s")
        stations = []
        pattern = re.compile(r"\[(\d+)\]\s*\[CH:\s*(\d+)\]\s+([0-9A-F:]{17})\s+\(AP:\s*(.*?)\)\s+(-?\d+)")
        for line in raw.splitlines():
            match = pattern.search(line)
            if match:
                idx, ch, mac, ap, rssi = match.groups()
                stations.append({
                    "idx": int(idx),
                    "ch": int(ch),
                    "mac": mac,
                    "ap": ap.strip(),
                    "rssi": int(rssi)
                })
        return stations

class MarauderShell(cmd.Cmd):
    intro = f"\n{CLR['BG']}{CLR['BOLD']}  MARAUDER SUPREME BRIDGE ACTIVE  {CLR['RESET']}\nType 'help' or '?' to list commands.\n"
    prompt = f"{CLR['PURP']}marauder {CLR['CYAN']}>> {CLR['RESET']}"

    def __init__(self, interface):
        super().__init__()
        self.mi = interface
        self.sort_key = "rssi"

    def do_scan(self, arg):
        """Scan for access points. Usage: scan [duration_seconds]"""
        duration = 10
        if arg:
            try: duration = int(arg)
            except: print(f"{CLR['R']}Invalid duration. Using default 10s.{CLR['RESET']}")
        print(f"{CLR['C']}[*] Tactical WiFi Scan Initiated ({duration}s)...{CLR['RESET']}")
        # Show a simple progress indicator
        for i in range(duration):
            sys.stdout.write(f"\r{CLR['Y']}[{('=' * i).ljust(duration)}] Scanning... {i+1}/{duration}s{CLR['RESET']}")
            sys.stdout.flush()
            time.sleep(1)
        print("\r" + " " * 50 + "\r", end="")
        self.mi.execute_command("scanap", wait_ms=2000)
        print(f"{CLR['G']}[+] Scan Complete.{CLR['RESET']}")
        self.do_aps("")

    def do_status(self, arg):
        """Show current Marauder status and device info."""
        print(f"\n{CLR['CYAN']}{CLR['BOLD']}  MARAUDER TACTICAL STATUS  {CLR['RESET']}")
        info = self.mi.get_info()
        ver = "Unknown"
        hw = "Unknown"
        for line in info.splitlines():
            if "Marauder v" in line: ver = line.strip()
            if "Hardware" in line: hw = line.split(":", 1)[1].strip()
        
        status_data = [
            {"Property": "Version", "Value": ver},
            {"Property": "Hardware", "Value": hw},
            {"Property": "Connection", "Value": f"{CLR['G']}STABLE{CLR['RESET']}"},
            {"Property": "Interface", "Value": "USART (115200)"}
        ]
        print(MarauderTable.format(status_data, ["Property", "Value"]))

    def do_dashboard(self, arg):
        """High-level Tactical Dashboard overview."""
        print(f"\n{CLR['BG']}{CLR['BOLD']}  MARAUDER TACTICAL DASHBOARD  {CLR['RESET']}")
        
        # Gathering metrics
        aps = self.mi.list_aps()
        stations = self.mi.list_stations()
        info = self.mi.get_info()
        
        ver = "N/A"
        for line in info.splitlines():
            if "Marauder v" in line: ver = line.strip(); break
            
        metrics = [
            {"Metric": "Firmware", "Data": ver},
            {"Metric": "AP Pool", "Data": len(aps)},
            {"Metric": "Station Pool", "Data": len(stations)},
            {"Metric": "WiFi Channel", "Data": self.mi.execute_command("channel").strip()}
        ]
        print(MarauderTable.format(metrics, ["Metric", "Data"], title="Systems Overview"))
        
        if aps:
            print("\n" + MarauderTable.format(aps[:5], ["idx", "ch", "rssi", "ssid"], title="Top 5 APs (Signal)"))

    def do_settings(self, arg):
        """List or set Marauder internal settings. Usage: settings [name] [value]"""
        if len(arg.split()) >= 2:
            parts = arg.split()
            print(f"{CLR['C']}[*] Updating setting {parts[0]} -> {parts[1]}...{CLR['RESET']}")
            print(self.mi.execute_command(f"settings -s {parts[0]} {parts[1]}"))
        else:
            raw = self.mi.execute_command("settings")
            settings_list = []
            # Parse settings output, usually "Name: Value"
            for line in raw.splitlines():
                if ":" in line:
                    name, val = line.split(":", 1)
                    settings_list.append({"Setting": name.strip(), "Value": val.strip()})
            print(MarauderTable.format(settings_list, ["Setting", "Value"], title="Marauder Configuration"))

    def do_ssid(self, arg):
        """SSID Pool Orchestration. Usage: ssid [add|remove|list|clear] [name]"""
        sub = arg.split()[0] if arg else "list"
        if sub == "add":
            name = " ".join(arg.split()[1:])
            print(f"{CLR['C']}[*] Adding SSID to pool: {name}{CLR['RESET']}")
            print(self.mi.execute_command(f"ssid -a {name}"))
        elif sub == "remove":
            idx = arg.split()[1]
            print(f"{CLR['C']}[*] Removing SSID index {idx}{CLR['RESET']}")
            print(self.mi.execute_command(f"ssid -r {idx}"))
        elif sub == "clear":
            print(f"{CLR['Y']}[*] Clearing SSID pool...{CLR['RESET']}")
            print(self.mi.execute_command("ssid -c"))
        else:
            raw = self.mi.execute_command("ssid")
            pool = []
            for line in raw.splitlines():
                m = re.search(r"\[(\d+)\]\s+(.*)", line)
                if m:
                    idx, name = m.groups()
                    pool.append({"idx": idx, "SSID": name.strip()})
            print(MarauderTable.format(pool, ["idx", "SSID"], title="SSID Pool"))

    def do_stop(self, arg):
        """Stop all active attacks, scans, or sniffing processes."""
        print(f"{CLR['R']}{CLR['BOLD']}[!] EMERGENCY STOP INITIATED{CLR['RESET']}")
        print(self.mi.execute_command("stop"))

    def do_reboot(self, arg):
        """Reboot the Marauder module."""
        print(f"{CLR['Y']}[*] Rebooting ESP32...{CLR['RESET']}")
        self.mi.execute_command("reboot")

    def do_led(self, arg):
        """Control Module LED. Usage: led [on|off] or led [r] [g] [b]"""
        if not arg:
            print("Usage: led [on|off] or led [r] [g] [b]")
            return
        print(f"{CLR['C']}[*] Updating LED state: {arg}{CLR['RESET']}")
        print(self.mi.execute_command(f"led {arg}"))

    def do_cat(self, arg):
        """Display contents of a file on ESP SD card. Usage: cat [path]"""
        if not arg:
            print("Usage: cat [path]")
            return
        print(f"{CLR['GRAY']}Reading {arg}...{CLR['RESET']}")
        print(self.mi.execute_command(f"cat {arg}"))

    def do_rm(self, arg):
        """Delete a file on ESP SD card. Usage: rm [path]"""
        if not arg:
            print("Usage: rm [path]")
            return
        print(f"{CLR['R']}[*] Deleting {arg}...{CLR['RESET']}")
        print(self.mi.execute_command(f"rm {arg}"))

    def do_mkdir(self, arg):
        """Create a directory on ESP SD card. Usage: mkdir [path]"""
        if not arg:
            print("Usage: mkdir [path]")
            return
        print(f"{CLR['G']}[*] Creating directory {arg}...{CLR['RESET']}")
        print(self.mi.execute_command(f"mkdir {arg}"))

    def do_run(self, arg):
        """Run a Marauder script file stored on the ESP SD card. Usage: run [path]"""
        if not arg:
            print("Usage: run [path]")
            return
        print(f"{CLR['M']}[*] Executing ESP-local script: {arg}{CLR['RESET']}")
        print(self.mi.execute_command(f"run {arg}", wait_ms=10000))

    def do_aps(self, arg):
        """List scanned Access Points. Usage: aps [sort_column]"""
        if arg: self.sort_key = arg
        aps = self.mi.list_aps()
        if not aps:
            print(f"{CLR['Y']}[!] No APs in memory. Run 'scan' first.{CLR['RESET']}")
        else:
            print(MarauderTable.format(aps, ["idx", "ch", "rssi", "ssid", "bssid"], sort_by=self.sort_key))

    def do_select(self, arg):
        """Select targets by index. Usage: select [idx1,idx2,... or 'all']"""
        if not arg:
            print(f"{CLR['R']}Usage: select [indices|all]{CLR['RESET']}")
            return
        cmd = f"select -a {arg}" if arg != "all" else "select -a all"
        print(f"{CLR['C']}[*] Selecting targets: {arg}{CLR['RESET']}")
        print(self.mi.execute_command(cmd))

    def do_attack(self, arg):
        """Execute WiFi attacks. Usage: attack [deauth|beacon|probe|rickroll]"""
        if not arg:
            print(f"{CLR['R']}Usage: attack [deauth|beacon|probe|rickroll]{CLR['RESET']}")
            return
        print(f"{CLR['R']}{CLR['BOLD']}[!] INITIATING ATTACK: {arg.upper()}{CLR['RESET']}")
        print(self.mi.execute_command(f"attack -t {arg}"))

    def do_sniff(self, arg):
        """Start sniffing. Usage: sniff [raw|beacon|probe|pmkid]"""
        if not arg:
            print(f"{CLR['R']}Usage: sniff [raw|beacon|probe|pmkid]{CLR['RESET']}")
            return
        print(f"{CLR['C']}[*] Sniffing {arg}... (Ctrl+C on Flipper to stop){CLR['RESET']}")
        print(self.mi.execute_command(f"sniff{arg}", wait_ms=10000))

    def do_channel(self, arg):
        """Get or set WiFi channel. Usage: channel [ch_number]"""
        if arg:
            print(f"{CLR['C']}[*] Setting channel to {arg}...{CLR['RESET']}")
            print(self.mi.execute_command(f"channel -s {arg}"))
        else:
            print(f"{CLR['C']}[*] Current Channel: {CLR['RESET']}")
            print(self.mi.execute_command("channel"))

    def do_clear(self, arg):
        """Clear lists. Usage: clear [ap|st|all]"""
        target = arg if arg else "all"
        print(f"{CLR['Y']}[*] Clearing {target} list...{CLR['RESET']}")
        if target == "ap" or target == "all": print(self.mi.execute_command("clear -a"))
        if target == "st" or target == "all": print(self.mi.execute_command("clear -s"))

    def do_save(self, arg):
        """Save current session/PCAP. Usage: save [name]"""
        print(f"{CLR['G']}[*] Saving data...{CLR['RESET']}")
        print(self.mi.execute_command("save"))

    def do_iac(self, arg):
        """Run IAC Automation Script. Usage: iac [file.json]"""
        if not arg:
            print(f"{CLR['R']}Usage: iac [automation_script.json]{CLR['RESET']}")
            return
        
        path = arg if os.path.exists(arg) else os.path.join(os.getcwd(), arg)
        if not os.path.exists(path):
            print(f"{CLR['R']}[!] Script not found: {arg}{CLR['RESET']}")
            return

        print(f"\n{CLR['M']}{CLR['BOLD']}  [∞] INITIATING IAC AUTOMATION ENGINE  {CLR['RESET']}")
        start_time = time.time()
        
        try:
            with open(path, 'r') as f:
                script = json.load(f)
                name = script.get("name", "Unnamed Strategy")
                steps = script.get("steps", [])
                
                print(f"{CLR['PURP']}Strategy: {CLR['BOLD']}{name}{CLR['RESET']}")
                print(f"{CLR['GRAY']}Targeting {len(steps)} tactical steps...{CLR['RESET']}\n")

                for i, step in enumerate(steps):
                    cmd = step.get("cmd")
                    desc = step.get("desc", "Executing step")
                    wait = step.get("wait", 2)
                    
                    print(f"{CLR['C']}[{i+1}/{len(steps)}] {CLR['BOLD']}{desc}{CLR['RESET']}")
                    print(f"{CLR['GRAY']}  > {cmd}{CLR['RESET']}")
                    
                    res = self.mi.execute_command(cmd, wait_ms=wait*1000)
                    if res:
                        # Print first few lines of result to keep it clean
                        lines = res.splitlines()
                        for line in lines[:10]: print(f"    {CLR['W']}{line}{CLR['RESET']}")
                        if len(lines) > 10: print(f"    {CLR['GRAY']}... ({len(lines)-10} more lines){CLR['RESET']}")
                    
                    print(f"{CLR['G']}  [✓] Step Complete.{CLR['RESET']}\n")

                duration = time.time() - start_time
                print(f"{CLR['BG']}{CLR['BOLD']}  IAC AUTOMATION FINISHED IN {duration:.1f}s  {CLR['RESET']}\n")
                
        except Exception as e:
            print(f"{CLR['R']}{CLR['BOLD']}[!] IAC ENGINE CRITICAL FAILURE: {e}{CLR['RESET']}")

    def do_stations(self, arg):
        """List scanned Stations. Usage: stations [sort_column]"""
        if arg: self.sort_key = arg
        stations = self.mi.list_stations()
        if not stations:
            print(f"{CLR['Y']}[!] No stations in memory.{CLR['RESET']}")
        else:
            print(MarauderTable.format(stations, ["idx", "ch", "rssi", "mac", "ap"], sort_by=self.sort_key))

    def do_info(self, arg):
        """Show Marauder hardware/firmware info."""
        print(f"{CLR['C']}[*] Module Profile:{CLR['RESET']}")
        print(self.mi.execute_command("info"))

    def do_ls(self, arg):
        """List files on ESP SD card. Usage: ls [path]"""
        path = arg if arg else "/"
        raw = self.mi.execute_command(f"ls {path}")
        files = []
        for line in raw.splitlines():
            if line.startswith(">") or "ls" in line: continue
            parts = line.split()
            if len(parts) >= 2:
                files.append({"name": parts[0], "size": parts[1]})
        if files:
            print(MarauderTable.format(files, ["name", "size"]))
        else:
            print(raw)

    def do_raw(self, arg):
        """Send raw command to Marauder. Usage: raw [command]"""
        if not arg:
            print("Please provide a command.")
            return
        print(self.mi.execute_command(arg))

    def default(self, line):
        """Try running as raw command if not recognized."""
        print(f"{CLR['GRAY']}Executing raw: {line}{CLR['RESET']}")
        print(self.mi.execute_command(line))

    def do_exit(self, arg):
        """Exit the bridge."""
        print(f"{CLR['Y']}Shutting down bridge...{CLR['RESET']}")
        return True

    def do_EOF(self, arg):
        return True

def main():
    parser = argparse.ArgumentParser(description="Marauder Beautified CLI Bridge")
    parser.add_argument("cmd", nargs="?", help="Initial command to run (scan, aps, stations, info)")
    parser.add_argument("--port", help="Serial port", default="auto")
    
    args = parser.parse_args()
    
    port = resolve_port(logger, args.port)
    if not port:
        print(f"{CLR['R']}[!] Flipper Zero not detected.{CLR['RESET']}")
        sys.exit(1)
        
    mi = MarauderInterface(port)
    
    if args.cmd:
        # Run single command mode
        shell = MarauderShell(mi)
        shell.onecmd(" ".join(sys.argv[1:]))
    else:
        # Interactive mode
        MarauderShell(mi).cmdloop()

if __name__ == "__main__":
    main()
