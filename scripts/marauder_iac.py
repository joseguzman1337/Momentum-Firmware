#!/usr/bin/env python3
import sys
import os
import time
import argparse
import logging
import json
import re

sys.path.append(os.path.join(os.getcwd(), 'scripts'))
from flipper.utils.cdc import resolve_port
from flipper.storage import FlipperStorage

# ANSI Colors
CLR = {
    "R": "\033[0;31m", "G": "\033[0;32m", "Y": "\033[0;33m", 
    "B": "\033[0;34m", "M": "\033[0;35m", "C": "\033[0;36m",
    "W": "\033[0;37m", "BOLD": "\033[1m", "RESET": "\033[0m",
    "BG": "\033[44m", "BR_G": "\033[1;32m", "ORNG": "\033[38;5;208m"
}

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class SupremeTable:
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
    def format(data, headers, sort_by=None, reverse=True):
        if not data: return f"{CLR['Y']}[!] No data available.{CLR['RESET']}"
        if sort_by: data = sorted(data, key=lambda x: x.get(sort_by, 0), reverse=reverse)
        
        # Auto-calculate dynamic widths
        widths = {h: len(h) for h in headers}
        for row in data:
            for h in headers:
                widths[h] = max(widths[h], len(str(row.get(h, ""))))
        
        # Build Table Components
        top = " ╔" + "═" * (sum(widths.values()) + (len(headers) * 3) - 1) + "╗"
        head = " ║ " + " | ".join(f"{CLR['BOLD']}{CLR['C']}{h.upper().ljust(widths[h])}{CLR['RESET']}" for h in headers) + " ║"
        mid = " ╟" + "─" * (sum(widths.values()) + (len(headers) * 3) - 1) + "╢"
        bot = " ╚" + "═" * (sum(widths.values()) + (len(headers) * 3) - 1) + "╝"
        
        lines = [top, head, mid]
        for row in data:
            cells = []
            for h in headers:
                val = str(row.get(h, ""))
                # Special case: Colorize RSSI
                if h == "rssi":
                    color = SupremeTable.get_rssi_color(val)
                    cells.append(f"{color}{val.ljust(widths[h])}{CLR['RESET']}")
                elif h == "ssid":
                    cells.append(f"{CLR['BOLD']}{val.ljust(widths[h])}{CLR['RESET']}")
                else:
                    cells.append(val.ljust(widths[h]))
            lines.append(" ║ " + " | ".join(cells) + " ║")
        lines.append(bot)
        return "\n".join(lines)

class MarauderIaC:
    def __init__(self, port):
        self.port = port
        self.temp_js = "/ext/marauder_supreme_iac.js"

    def _exec(self, cmd, wait_ms=3000):
        js = f"""
let s=require("serial");
s.setup("usart", 115200);
s.write("{cmd}\\r\\n");
for(let i=0; i<{(wait_ms//200)+5}; i++){{
    let d=s.readAny(200);
    if(d) print(d);
}}
s.end();
"""
        with open("supreme_payload.js", "w") as f: f.write(js)
        with FlipperStorage(self.port) as storage:
            storage.send('\x03\x03')
            time.sleep(0.3)
            storage.send("loader close\r\n")
            time.sleep(0.5)
            storage.read.until(storage.CLI_PROMPT)
            storage.start()
            try: storage.remove(self.temp_js)
            except: pass
            storage.send_file("supreme_payload.js", self.temp_js)
            os.remove("supreme_payload.js")
            storage.send(f"js {self.temp_js}\r\n")
            res = storage.read.until(storage.CLI_PROMPT).decode('ascii', 'ignore')
            lines = res.splitlines()
            cleaned = []
            capture = False
            for line in lines:
                if "Running script" in line: capture = True; continue
                if "Script done" in line: break
                if capture: cleaned.append(line)
            storage.remove(self.temp_js)
        return "\n".join(cleaned).strip()

    def get_aps(self):
        raw = self._exec("list -a")
        aps = []
        for line in raw.splitlines():
            m = re.search(r"\[(\d+)\]\s*\[CH:\s*(\d+)\]\s*(.*?)\s+(-?\d+)", line)
            if m:
                idx, ch, ssid, rssi = m.groups()
                bssid = "N/A"
                bssid_m = re.search(r"([:0-9A-F]{17})", ssid)
                if bssid_m:
                    bssid = bssid_m.group(1)
                    ssid = ssid.replace(bssid, "").strip()
                aps.append({"idx": int(idx), "ch": int(ch), "rssi": int(rssi), "ssid": ssid.strip() or "<Hidden>", "bssid": bssid})
        return aps

    def get_ls(self, path="/"):
        raw = self._exec(f"ls {path}")
        files = []
        for line in raw.splitlines():
            if line.startswith(">") or "ls" in line: continue
            parts = line.split()
            if len(parts) >= 2:
                files.append({"name": parts[0], "size": parts[1]})
        return files

    def info(self): return self._exec("info")
    def scan_aps(self, t=15): return self._exec("scanap", t*1000)

def main():
    parser = argparse.ArgumentParser(description="Supreme Marauder IaC Dashboard")
    parser.add_argument("cmd", help="Action", nargs="?", default="aps")
    args = parser.parse_args()
    
    port = resolve_port(logger)
    if not port: sys.exit(1)
    iac = MarauderIaC(port)
    
    print(f"\n{CLR['BG']}{CLR['BOLD']}  MARAUDER SUPREME AUTOMATION BRIDGE  {CLR['RESET']}")
    
    if args.cmd == "aps":
        print(f"{CLR['C']}[*] Tactical WiFi Scan Initiated...{CLR['RESET']}")
        iac.scan_aps(t=10)
        aps = iac.get_aps()
        print(SupremeTable.format(aps, ["idx", "ch", "rssi", "ssid", "bssid"], sort_by="rssi"))
    elif args.cmd == "files":
        print(f"{CLR['C']}[*] Indexing ESP SD Card Storage...{CLR['RESET']}")
        files = iac.get_ls("/")
        print(SupremeTable.format(files, ["name", "size"]))
    elif args.cmd == "info":
        print(f"{CLR['C']}[*] Fetching Module Hardware Profile...{CLR['RESET']}")
        print(f"{CLR['W']}{iac.info()}{CLR['RESET']}")
    else:
        print(f"{CLR['R']}[!] Unknown command: {args.cmd}{CLR['RESET']}")

if __name__ == "__main__":
    main()
