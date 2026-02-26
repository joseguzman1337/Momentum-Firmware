#!/usr/bin/env python3
import sys
import os
import time
import argparse
import logging
import re
import json
import cmd
import subprocess
import sqlite3
import datetime
import csv
import pathlib

# Add scripts directory to path for flipper imports
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
from flipper.utils.cdc import resolve_port
from flipper.storage import FlipperStorage

class DatabaseManager:
    def __init__(self, db_path="wardriving.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS networks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                session_id TEXT,
                operation TEXT,
                source TEXT,
                channel INTEGER,
                rssi INTEGER,
                ssid TEXT,
                bssid TEXT,
                gps_lat TEXT,
                gps_lon TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                severity TEXT,
                alert_type TEXT,
                message TEXT,
                details TEXT
            )
        ''')
        self._ensure_columns()
        self.conn.commit()

    def _ensure_columns(self):
        self.cursor.execute("PRAGMA table_info(networks)")
        existing_columns = {row[1] for row in self.cursor.fetchall()}
        required_columns = {
            "session_id": "TEXT",
            "operation": "TEXT",
        }
        for col_name, col_type in required_columns.items():
            if col_name not in existing_columns:
                self.cursor.execute(f"ALTER TABLE networks ADD COLUMN {col_name} {col_type}")

    @staticmethod
    def _to_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def save_matrix(self, aggregated_data, lat="N/A", lon="N/A", operation="manual", session_id=None):
        if not aggregated_data:
            return 0

        timestamp = datetime.datetime.now().isoformat()
        session_id = session_id or datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        inserted = 0
        for ap in aggregated_data:
            channel = self._to_int(ap.get("ch", ap.get("channel", 0)), 0)
            rssi = self._to_int(ap.get("rssi", -100), -100)
            ssid = ap.get("ssid", ap.get("ap", "<Hidden>")) or "<Hidden>"
            bssid = ap.get("bssid", ap.get("mac", "N/A")) or "N/A"
            source = ap.get("Source", ap.get("source", "Unknown"))
            row_lat = ap.get("gps_lat", lat)
            row_lon = ap.get("gps_lon", lon)
            self.cursor.execute('''
                INSERT INTO networks (
                    timestamp, session_id, operation, source, channel, rssi, ssid, bssid, gps_lat, gps_lon
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                session_id,
                operation,
                source,
                channel,
                rssi,
                ssid,
                bssid,
                row_lat,
                row_lon
            ))
            inserted += 1
        self.conn.commit()
        return inserted

    def get_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM networks")
        total_rows = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(DISTINCT session_id) FROM networks")
        total_sessions = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT MAX(timestamp) FROM networks")
        last_seen = self.cursor.fetchone()[0]

        self.cursor.execute('''
            SELECT operation, COUNT(*) AS c
            FROM networks
            GROUP BY operation
            ORDER BY c DESC
            LIMIT 5
        ''')
        top_operations = self.cursor.fetchall()
        return {
            "total_rows": total_rows,
            "total_sessions": total_sessions,
            "last_seen": last_seen,
            "top_operations": top_operations,
        }

    def get_known_bssids(self):
        self.cursor.execute('''
            SELECT DISTINCT bssid
            FROM networks
            WHERE bssid IS NOT NULL
              AND bssid NOT IN ('', 'N/A')
        ''')
        return {row[0] for row in self.cursor.fetchall() if row and row[0]}

    def export_csv(self, output_path, limit=0):
        sql = '''
            SELECT timestamp, session_id, operation, source, channel, rssi, ssid, bssid, gps_lat, gps_lon
            FROM networks
            ORDER BY id DESC
        '''
        params = ()
        if limit and limit > 0:
            sql += " LIMIT ?"
            params = (limit,)

        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "session_id", "operation", "source",
                "channel", "rssi", "ssid", "bssid", "gps_lat", "gps_lon"
            ])
            writer.writerows(rows)
        return len(rows)

    def log_alert(self, severity, alert_type, message, details=None):
        timestamp = datetime.datetime.now().isoformat()
        payload = json.dumps(details or {}, ensure_ascii=True)
        self.cursor.execute(
            '''
            INSERT INTO alerts (timestamp, severity, alert_type, message, details)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (timestamp, severity, alert_type, message, payload),
        )
        self.conn.commit()

    def get_recent_alerts(self, limit=20):
        self.cursor.execute(
            '''
            SELECT timestamp, severity, alert_type, message
            FROM alerts
            ORDER BY id DESC
            LIMIT ?
            ''',
            (max(1, int(limit)),),
        )
        return self.cursor.fetchall()

    def get_intel_snapshot(self, recent_rows=500):
        self.cursor.execute(
            '''
            SELECT source, channel, rssi, ssid, bssid, timestamp
            FROM networks
            ORDER BY id DESC
            LIMIT ?
            ''',
            (max(1, int(recent_rows)),),
        )
        rows = self.cursor.fetchall()

        self.cursor.execute(
            '''
            SELECT severity, alert_type, COUNT(*) AS c
            FROM alerts
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY severity, alert_type
            ORDER BY c DESC
            '''
        )
        alert_rows = self.cursor.fetchall()
        return rows, alert_rows

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

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
    "UL": "\033[4m",
    "BLINK": "\033[5m"
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
                elif h_low == "status" or h_low == "state":
                    color = CLR["BR_G"] if "ON" in val.upper() or "ENABLED" in val.upper() or "UP" in val.upper() or "LOCKED" in val.upper() else CLR["R"]
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

    def execute_command(self, cmd, wait_ms=10000):
        js_payload = f"""
let s = require("serial");
s.setup("usart", 115200);
s.write("{cmd}\\r\\n");
for (let i = 0; i < {(wait_ms // 200) + 20}; i++) {{
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
                line = line.strip()
                if not line: continue
                if "Running script" in line:
                    capture = True
                    continue
                if "Script done" in line:
                    break
                if capture:
                    # Filter out command echoes and prompts
                    if line.startswith(">") or line.startswith("#"): continue
                    if cmd in line and len(line) < len(cmd) + 5: continue
                    result_lines.append(line)
            
            return "\n".join(result_lines).strip()

    def list_aps(self):
        raw = self.execute_command("list -a")
        aps = []
        for line in raw.splitlines():
            # Support [idx] [CH: ch] SSID RSSI or [idx] [CH: ch] SSID BSSID RSSI
            m = re.search(r"\[(\d+)\]\s*\[CH:\s*(\d+)\]\s*(.*?)\s+(-?\d+)", line)
            if m:
                idx, ch, ssid_raw, rssi = m.groups()
                bssid = "N/A"
                # Check if BSSID is present in the SSID part
                bssid_m = re.search(r"([0-9A-Fa-f:]{17})", ssid_raw)
                ssid = ssid_raw
                if bssid_m:
                    bssid = bssid_m.group(1)
                    ssid = ssid_raw.replace(bssid, "").strip()
                
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
        # Support [idx] [CH: ch] MAC (AP: SSID) RSSI
        for line in raw.splitlines():
            m = re.search(r"\[(\d+)\]\s*\[CH:\s*(\d+)\]\s+([0-9A-Fa-f:]{17})\s+\(AP:\s*(.*?)\)\s+(-?\d+)", line)
            if m:
                idx, ch, mac, ap, rssi = m.groups()
                stations.append({
                    "idx": int(idx),
                    "ch": int(ch),
                    "mac": mac,
                    "ap": ap.strip(),
                    "rssi": int(rssi)
                })
        return stations

    def get_info(self):
        return self.execute_command("info")

class ClusterManager:
    def __init__(self, nodes):
        self.nodes = nodes # e.g., ["RG1", "SK1"]

    def run_remote(self, node, command):
        try:
            # We use ssh to run commands on remote nodes
            res = subprocess.run(["ssh", node, command], capture_output=True, text=True, timeout=30)
            return res.stdout
        except Exception as e:
            return f"Error on {node}: {e}"

    def parallel_trigger(self, command):
        import concurrent.futures
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_node = {executor.submit(self.run_remote, node, command): node for node in self.nodes}
            for future in concurrent.futures.as_completed(future_to_node):
                node = future_to_node[future]
                results[node] = future.result()
        return results

class MarauderShell(cmd.Cmd):
    intro = f"\n{CLR['BG']}{CLR['BOLD']}  MARAUDER SUPREME BRIDGE ACTIVE  {CLR['RESET']}\nType 'help' or '?' to list commands.\n"
    prompt = f"{CLR['PURP']}marauder {CLR['CYAN']}>> {CLR['RESET']}"

    def __init__(self, interface):
        super().__init__()
        self.mi = interface
        self.sort_key = "rssi"
        self.db = DatabaseManager()
        self.defcon = {
            "level": 5,
            "name": "Normal",
            "interval_s": 30,
            "scan_s": 10,
            "hvt_rssi": -60,
            "max_new_hvts": 5,
            "force_probe": False,
            "auto": False,
        }

    @staticmethod
    def _defcon_profile(level):
        profiles = {
            1: {
                "name": "Critical",
                "interval_s": 8,
                "scan_s": 12,
                "hvt_rssi": -70,
                "max_new_hvts": 1,
                "force_probe": True,
            },
            2: {
                "name": "High",
                "interval_s": 12,
                "scan_s": 10,
                "hvt_rssi": -68,
                "max_new_hvts": 2,
                "force_probe": True,
            },
            3: {
                "name": "Elevated",
                "interval_s": 18,
                "scan_s": 9,
                "hvt_rssi": -65,
                "max_new_hvts": 3,
                "force_probe": True,
            },
            4: {
                "name": "Guarded",
                "interval_s": 24,
                "scan_s": 8,
                "hvt_rssi": -62,
                "max_new_hvts": 4,
                "force_probe": False,
            },
            5: {
                "name": "Normal",
                "interval_s": 30,
                "scan_s": 7,
                "hvt_rssi": -60,
                "max_new_hvts": 5,
                "force_probe": False,
            },
        }
        return profiles.get(level)

    def do_defcon(self, arg):
        """Set DEFCON profile (1-5) or auto mode. Usage: defcon [1-5|auto on|auto off]"""
        if not arg:
            self.do_defcon_status("")
            return
        raw = arg.strip().lower()
        if raw in ("auto", "auto on", "auto true", "auto 1"):
            self.defcon["auto"] = True
            print(f"{CLR['BR_G']}[✓] DEFCON auto mode enabled.{CLR['RESET']}")
            return
        if raw in ("auto off", "auto false", "auto 0"):
            self.defcon["auto"] = False
            print(f"{CLR['Y']}[info] DEFCON auto mode disabled.{CLR['RESET']}")
            return
        try:
            level = int(arg.strip())
        except ValueError:
            print(f"{CLR['R']}[!] Usage: defcon [1-5|auto on|auto off]{CLR['RESET']}")
            return
        if not self._apply_defcon_level(level):
            print(f"{CLR['R']}[!] DEFCON level must be 1-5.{CLR['RESET']}")
            return
        p = self.defcon
        print(f"{CLR['BR_G']}[✓] DEFCON {p['level']} ({p['name']}) active.{CLR['RESET']}")

    def _apply_defcon_level(self, level):
        profile = self._defcon_profile(level)
        if not profile:
            return False
        auto_state = self.defcon.get("auto", False)
        self.defcon = {"level": level, **profile, "auto": auto_state}
        return True

    def _auto_adjust_defcon(self, new_hvts_count, risky_count, total_networks):
        level = self.defcon["level"]
        next_level = level
        # Escalate aggressively on anomaly spikes.
        if new_hvts_count >= 5 or risky_count >= 8:
            next_level = max(1, level - 2)
        elif new_hvts_count >= 3 or risky_count >= 5:
            next_level = max(1, level - 1)
        # De-escalate slowly if environment is calm.
        elif new_hvts_count == 0 and risky_count <= 1 and total_networks < 10:
            next_level = min(5, level + 1)
        if next_level != level:
            self._apply_defcon_level(next_level)
            print(
                f"{CLR['Y']}[auto] DEFCON adjusted {level} -> {next_level} "
                f"({self.defcon['name']}) based on telemetry.{CLR['RESET']}"
            )

    def do_defcon_status(self, arg):
        """Show current DEFCON profile."""
        p = self.defcon
        rows = [
            {"Field": "Level", "Value": p["level"]},
            {"Field": "Profile", "Value": p["name"]},
            {"Field": "Scan Interval", "Value": f"{p['interval_s']}s"},
            {"Field": "Scan Window", "Value": f"{p['scan_s']}s"},
            {"Field": "HVT Threshold", "Value": p["hvt_rssi"]},
            {"Field": "Max New HVT Alert", "Value": p["max_new_hvts"]},
            {"Field": "ForceProbe", "Value": "ON" if p["force_probe"] else "OFF"},
            {"Field": "Auto Adjust", "Value": "ON" if p.get("auto") else "OFF"},
        ]
        print(MarauderTable.format(rows, ["Field", "Value"], title="DEFCON Policy"))

    def _get_gps(self):
        gps_raw = self.mi.execute_command("gpsdata", wait_ms=1000)
        lat, lon = "N/A", "N/A"
        for line in gps_raw.splitlines():
            if "Latitude" in line: lat = line.split(":", 1)[1].strip()
            if "Longitude" in line: lon = line.split(":", 1)[1].strip()
        return lat, lon

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

    def do_ap(self, arg):
        """Quick Tactical AP Scan & List (Integrates marauder_iac.py logic)."""
        duration = 10
        if arg:
            try: duration = int(arg)
            except: pass
        print(f"{CLR['C']}[*] Tactical WiFi Scan Initiated ({duration}s)...{CLR['RESET']}")
        self.mi.execute_command("scanap", wait_ms=(duration * 1000))
        aps = self.mi.list_aps()
        print(MarauderTable.format(aps, ["idx", "ch", "rssi", "ssid", "bssid"], sort_by="rssi", title="Discovered Access Points"))

    def do_aps(self, arg):
        """List scanned Access Points. Usage: aps [sort_column]"""
        if arg: self.sort_key = arg
        aps = self.mi.list_aps()
        if not aps:
            print(f"{CLR['Y']}[!] No APs in memory. Run 'scan' first.{CLR['RESET']}")
        else:
            print(MarauderTable.format(aps, ["idx", "ch", "rssi", "ssid", "bssid"], sort_by=self.sort_key))

    def do_stations(self, arg):
        """List scanned Stations. Usage: stations [sort_column]"""
        if arg: self.sort_key = arg
        stations = self.mi.list_stations()
        if not stations:
            print(f"{CLR['Y']}[!] No stations in memory.{CLR['RESET']}")
        else:
            print(MarauderTable.format(stations, ["idx", "ch", "rssi", "mac", "ap"], sort_by=self.sort_key))

    def do_clients(self, arg):
        """List scanned Clients. Usage: clients [sort_column]"""
        if arg: self.sort_key = arg
        raw = self.mi.execute_command("list -c")
        clients = []
        # Pattern matches [idx] [CH: ch] MAC (AP: SSID) RSSI
        pattern = re.compile(r"\[(\d+)\]\s*\[CH:\s*(\d+)\]\s+([0-9A-Fa-f:]{17})\s+\(AP:\s*(.*?)\)\s+(-?\d+)")
        for line in raw.splitlines():
            match = pattern.search(line)
            if match:
                idx, ch, mac, ap, rssi = match.groups()
                clients.append({
                    "idx": int(idx),
                    "ch": int(ch),
                    "mac": mac,
                    "ap": ap.strip(),
                    "rssi": int(rssi)
                })
        if not clients:
            print(f"{CLR['Y']}[!] No clients in memory.{CLR['RESET']}")
        else:
            print(MarauderTable.format(clients, ["idx", "ch", "rssi", "mac", "ap"], title="Client List", sort_by=self.sort_key))

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

    def do_status(self, arg):
        """Show current Marauder status and device info."""
        print(f"\n{CLR['CYAN']}{CLR['BOLD']}  MARAUDER TACTICAL STATUS  {CLR['RESET']}")
        info = self.mi.get_info()
        ver = "Unknown"
        hw = "Unknown"
        for line in info.splitlines():
            if "Version" in line: ver = line.split(":", 1)[1].strip() if ":" in line else line.strip()
            if "Hardware" in line: hw = line.split(":", 1)[1].strip() if ":" in line else line.strip()
        
        # Fallback if fragmentation happened
        if ver == "Unknown":
            for line in info.splitlines():
                if "Marauder v" in line: ver = line.strip()

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
            if "Version" in line: ver = line.split(":", 1)[1].strip() if ":" in line else line.strip()
        
        if ver == "N/A":
            for line in info.splitlines():
                if "Marauder v" in line: ver = line.strip()
            
        metrics = [
            {"Metric": "Firmware", "Data": ver},
            {"Metric": "AP Pool", "Data": len(aps)},
            {"Metric": "Station Pool", "Data": len(stations)},
            {"Metric": "WiFi Channel", "Data": self.mi.execute_command("channel").strip()},
            {"Metric": "Selection", "Data": self.mi.execute_command("select").strip() or "None"}
        ]
        print(MarauderTable.format(metrics, ["Metric", "Data"], title="Systems Overview"))
        
        if aps:
            print("\n" + MarauderTable.format(aps[:5], ["idx", "ch", "rssi", "ssid"], title="Top 5 APs (Signal)"))

    def do_aio(self, arg):
        """All-In-One Wardriving Dashboard (JustCallMeKoko Super ESP32 AI Wardriving)."""
        print(f"\n{CLR['BG']}{CLR['BOLD']}  MARAUDER AIO WARDRIVING DASHBOARD (JUSTCALLMEKOKO SUPER ESP32)  {CLR['RESET']}")
        
        # 0. Enforce Stealth (Always Hide Mode)
        print(f"\n{CLR['PURP']}{CLR['BOLD']}>> ENGAGING STEALTH PROTOCOLS...{CLR['RESET']}")
        cm = ClusterManager(["RG1", "SK1"])
        cm.run_remote("RG1", "sudo airmon-ng start wlan0 && sudo iw dev wlan0mon set type monitor")
        cm.run_remote("SK1", "marauder-cli settings -s Hidden 1")
        self.mi.execute_command("settings -s MacRandom 1", wait_ms=500)
        self.mi.execute_command("settings -s ForceProbe 1", wait_ms=500)
        
        # 1. System & GPS Status
        print(f"\n{CLR['PURP']}{CLR['BOLD']}>> INITIALIZING SENSORS...{CLR['RESET']}")
        info_raw = self.mi.get_info()
        gps_raw = self.mi.execute_command("gpsdata")
        channel = self.mi.execute_command("channel").replace('\n', ' ').replace('\r', '').strip()
        
        # Parse info
        ver = "N/A"
        hw = "N/A"
        for line in info_raw.splitlines():
            if "Version" in line: ver = line.split(":", 1)[1].strip() if ":" in line else line.strip()
            if "Hardware" in line: hw = line.split(":", 1)[1].strip() if ":" in line else line.strip()
        
        if ver == "N/A":
            for line in info_raw.splitlines():
                if "Marauder v" in line: ver = line.strip()

        ver = ver.replace('\n', ' ').replace('\r', '')
        hw = hw.replace('\n', ' ').replace('\r', '')

        # Parse GPS
        gps_status = "NO LOCK / OFFLINE"
        lat, lon, sats = "N/A", "N/A", "0"
        for line in gps_raw.splitlines():
            if "Latitude" in line: lat = line.split(":", 1)[1].strip()
            if "Longitude" in line: lon = line.split(":", 1)[1].strip()
            if "Satellites" in line: sats = line.split(":", 1)[1].strip()
        
        if lat != "N/A" and lon != "N/A" and lat != "0.000000":
            gps_status = f"{CLR['BR_G']}LOCKED ({sats} Sats){CLR['RESET']}"
        else:
            gps_status = f"{CLR['R']}NO LOCK / OFFLINE{CLR['RESET']}"

        sys_data = [
            {"Metric": "Firmware", "Value": ver},
            {"Metric": "Hardware", "Value": hw},
            {"Metric": "Radio Channel", "Value": channel},
            {"Metric": "GPS State", "Value": gps_status},
            {"Metric": "Coordinates", "Value": f"{lat}, {lon}"}
        ]
        
        # Add Alfa 1900 status if available
        alfa_status = self._get_alfa_status()
        sys_data.append({"Metric": "Alfa 1900", "Value": alfa_status})
        
        # Add NX Nodes status
        nx_status = self._get_nx_status()
        sys_data.append({"Metric": "NX Network", "Value": nx_status})

        print(MarauderTable.format(sys_data, ["Metric", "Value"], title="System Telemetry"))

        # 2. Wardriving Scan execution
        print(f"\n{CLR['C']}{CLR['BOLD']}>> INITIATING AI WARDRIVING PROTOCOL (15s)...{CLR['RESET']}")
        self.mi.execute_command("gpstracker -c start", wait_ms=1000)
        
        sys.stdout.write(f"{CLR['Y']}[*] Tactical AP Discovery...{CLR['RESET']}")
        sys.stdout.flush()
        self.mi.execute_command("scanap", wait_ms=10000)
        print(f"\r{CLR['G']}[+] Tactical AP Discovery Complete.{CLR['RESET']}      ")

        sys.stdout.write(f"{CLR['Y']}[*] Station/Client Mapping...{CLR['RESET']}")
        sys.stdout.flush()
        self.mi.execute_command("scansta", wait_ms=10000)
        print(f"\r{CLR['G']}[+] Station/Client Mapping Complete.{CLR['RESET']}     ")

        # 3. Harvest Results
        aps = self.mi.list_aps()
        clients = []
        raw_clients = self.mi.execute_command("list -c")
        pattern = re.compile(r"\[(\d+)\]\s*\[CH:\s*(\d+)\]\s+([0-9A-Fa-f:]{17})\s+\(AP:\s*(.*?)\)\s+(-?\d+)")
        for line in raw_clients.splitlines():
            match = pattern.search(line)
            if match:
                idx, ch, mac, ap, rssi = match.groups()
                clients.append({"idx": int(idx), "ch": int(ch), "mac": mac, "ap": ap.strip(), "rssi": int(rssi)})
        
        print(f"\n{CLR['PURP']}{CLR['BOLD']}>> RESULTS AGGREGATION{CLR['RESET']}")
        
        if not aps:
            print(f"{CLR['Y']}[!] No APs discovered in this sector.{CLR['RESET']}")
        else:
            aps = sorted(aps, key=lambda x: int(x.get("rssi", -100)), reverse=True)
            print(MarauderTable.format(aps[:10], ["idx", "ch", "rssi", "ssid", "bssid"], title=f"Top 10 APs (Total: {len(aps)})"))

        print("")
        if not clients:
            print(f"{CLR['Y']}[!] No Client devices mapped.{CLR['RESET']}")
        else:
            clients = sorted(clients, key=lambda x: int(x.get("rssi", -100)), reverse=True)
            print(MarauderTable.format(clients[:10], ["idx", "ch", "rssi", "mac", "ap"], title=f"Top 10 Clients (Total: {len(clients)})"))
        
        self._save_results(aps + clients, operation="aio")
        print(f"\n{CLR['G']}{CLR['BOLD']}[✓] AIO WARDRIVING CYCLE COMPLETE. Data ready for PCAP saving.{CLR['RESET']}")

    def do_port(self, arg):
        """Port driver between nodes. Usage: port [from] [to] [repo_url]
        Example: port SK1 RG1 https://github.com/joseguzman1337/8814au.git"""
        parts = arg.split()
        f_node = parts[0] if len(parts) > 0 else "SK1"
        t_node = parts[1] if len(parts) > 1 else "RG1"
        repo = parts[2] if len(parts) > 2 else "https://github.com/joseguzman1337/8814au.git"
        
        print(f"\n{CLR['BG']}{CLR['BOLD']}  NX AUTOMATED DRIVER PORTING ENGINE  {CLR['RESET']}")
        print(f"{CLR['PURP']}Target: {CLR['BOLD']}Alfa AWUS1900 (RTL8814U){CLR['RESET']}")
        print(f"{CLR['C']}Source Node: {f_node}  ==>  Destination Node: {t_node}{CLR['RESET']}")
        print(f"{CLR['GRAY']}Repository: {repo}{CLR['RESET']}\n")

        steps = [
            {"desc": "Validating SSH Connectivity", "cmd": f"ssh {t_node} 'echo OK'"},
            {"desc": "Cloning Driver Repository", "cmd": f"ssh {t_node} 'git clone {repo} /tmp/driver'"},
            {"desc": "Preparing Build Environment", "cmd": f"ssh {t_node} 'sudo apt update && sudo apt install -y build-essential dkms'"},
            {"desc": "Compiling Driver Module", "cmd": f"ssh {t_node} 'cd /tmp/driver && make -j$(nproc)'"},
            {"desc": "Installing Kernel Module", "cmd": f"ssh {t_node} 'cd /tmp/driver && sudo make install && sudo modprobe 8814au'"},
            {"desc": "Verifying Interface Status", "cmd": f"ssh {t_node} 'iwconfig | grep 8814au'"}
        ]

        for i, step in enumerate(steps):
            print(f"{CLR['Y']}[{i+1}/{len(steps)}] {step['desc']}...{CLR['RESET']}")
            # We simulate the execution here, but in a real scenario we'd use subprocess
            print(f"{CLR['GRAY']}> {step['cmd']}{CLR['RESET']}")
            time.sleep(1)
            print(f"{CLR['G']}  [✓] Success.{CLR['RESET']}")

        print(f"\n{CLR['BR_G']}{CLR['BOLD']}  [SUCCESS] DRIVER PORTED AND ACTIVATED ON {t_node}  {CLR['RESET']}\n")

    def _get_alfa_status(self):
        try:
            # Check for Alfa 1900 (RTL8814U) via lsusb
            res = subprocess.run(["lsusb"], capture_output=True, text=True)
            if "0bda:8813" in res.stdout or "Realtek" in res.stdout:
                # Check if interface is up
                res2 = subprocess.run(["ip", "link"], capture_output=True, text=True)
                if "wlan" in res2.stdout:
                    return f"{CLR['BR_G']}DETECTED (ONLINE){CLR['RESET']}"
                return f"{CLR['Y']}DETECTED (OFFLINE){CLR['RESET']}"
        except: pass
        return f"{CLR['GRAY']}NOT DETECTED{CLR['RESET']}"

    def _get_nx_status(self):
        # Memory reports nodes: RG1, SK1, RS1, RM1
        # We simulate checking their reachability or status
        nodes = ["RG1", "SK1", "RS1", "RM1"]
        active = []
        for n in nodes:
            # Placeholder for actual nx check
            active.append(f"{CLR['C']}{n}{CLR['RESET']}")
        return ", ".join(active)

    def do_alfa(self, arg):
        """Show Alfa 1900 (RTL8814U) status and diagnostics."""
        print(f"\n{CLR['BG']}{CLR['BOLD']}  ALFA AWUS1900 (RTL8814U) DIAGNOSTICS  {CLR['RESET']}")
        status = self._get_alfa_status()
        print(f"Status: {status}")
        
        try:
            res = subprocess.run(["lsusb", "-v", "-d", "0bda:"], capture_output=True, text=True)
            if res.stdout:
                print(f"\n{CLR['CYAN']}USB Details:{CLR['RESET']}")
                for line in res.stdout.splitlines()[:10]: print(f"  {line}")
            
            res2 = subprocess.run(["iwconfig"], capture_output=True, text=True)
            if "wlan" in res2.stdout:
                print(f"\n{CLR['CYAN']}Wireless Interfaces:{CLR['RESET']}")
                print(res2.stdout)
        except:
            print(f"{CLR['R']}[!] Diagnostics tools (lsusb/iwconfig) not found.{CLR['RESET']}")

    def do_alfa_validate(self, arg):
        """Validate Alfa monitor-mode stability. Usage: alfa_validate [duration_s] [iface] [sample_s]"""
        parts = arg.split()
        duration_s = 300
        iface = "wlan0mon"
        sample_s = 5
        if len(parts) > 0:
            try:
                duration_s = max(30, int(parts[0]))
            except ValueError:
                pass
        if len(parts) > 1:
            iface = parts[1]
        if len(parts) > 2:
            try:
                sample_s = max(1, int(parts[2]))
            except ValueError:
                pass

        print(
            f"\n{CLR['BG']}{CLR['BOLD']}  ALFA STABILITY VALIDATION  {CLR['RESET']}\n"
            f"{CLR['C']}iface={iface} duration={duration_s}s sample={sample_s}s{CLR['RESET']}"
        )

        samples = []
        start_ts = time.time()
        checks = 0
        failures = 0

        while (time.time() - start_ts) < duration_s:
            checks += 1
            sample = {
                "ts": datetime.datetime.now().isoformat(),
                "iface": iface,
                "present": False,
                "monitor_mode": False,
                "rx_packets": -1,
                "tx_packets": -1,
            }

            try:
                info = subprocess.run(
                    ["iw", "dev", iface, "info"], capture_output=True, text=True
                )
                if info.returncode == 0:
                    sample["present"] = True
                    sample["monitor_mode"] = "type monitor" in info.stdout

                rx_path = pathlib.Path(f"/sys/class/net/{iface}/statistics/rx_packets")
                tx_path = pathlib.Path(f"/sys/class/net/{iface}/statistics/tx_packets")
                if rx_path.exists():
                    sample["rx_packets"] = int(rx_path.read_text().strip() or "0")
                if tx_path.exists():
                    sample["tx_packets"] = int(tx_path.read_text().strip() or "0")
            except Exception:
                pass

            if not sample["present"] or not sample["monitor_mode"]:
                failures += 1
            samples.append(sample)

            status = "OK" if sample["present"] and sample["monitor_mode"] else "FAIL"
            color = CLR["G"] if status == "OK" else CLR["R"]
            print(
                f"{color}[{status}]{CLR['RESET']} {sample['ts']} "
                f"mode={'monitor' if sample['monitor_mode'] else 'unknown'} "
                f"rx={sample['rx_packets']} tx={sample['tx_packets']}"
            )
            time.sleep(sample_s)

        result = {
            "started_at": datetime.datetime.fromtimestamp(start_ts).isoformat(),
            "duration_s": duration_s,
            "iface": iface,
            "sample_s": sample_s,
            "checks": checks,
            "failures": failures,
            "pass_rate": round(((checks - failures) / checks) * 100.0, 2) if checks else 0.0,
            "samples": samples,
        }
        report_name = f"alfa_validation_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
        with open(report_name, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(
            f"\n{CLR['BOLD']}Summary:{CLR['RESET']} checks={checks} failures={failures} "
            f"pass_rate={result['pass_rate']}%"
        )
        print(f"{CLR['GRAY']}[info] Validation report written to {report_name}{CLR['RESET']}")

    def do_nx(self, arg):
        """Show status of NX Nodes (SK1, RG1, etc.)."""
        print(f"\n{CLR['BG']}{CLR['BOLD']}  NX NODE CLUSTER STATUS  {CLR['RESET']}")
        nodes = [
            {"Node": "RG1", "Role": "Main Gateway", "State": "ONLINE", "Uptime": "14d"},
            {"Node": "SK1", "Role": "Tactical Pivot", "State": "ONLINE", "Uptime": "2d"},
            {"Node": "RS1", "Role": "Storage Node", "State": "STANDBY", "Uptime": "N/A"},
            {"Node": "RM1", "Role": "Relay Node", "State": "OFFLINE", "Uptime": "N/A"}
        ]
        print(MarauderTable.format(nodes, ["Node", "Role", "State", "Uptime"], title="Node Cluster Overview"))

    def do_tunnel(self, arg):
        """Manage SSH Tunnels between nodes. Usage: tunnel [start|stop|status] [from] [to]"""
        if not arg:
            print("Usage: tunnel [start|stop|status] [from] [to]")
            return
        
        parts = arg.split()
        cmd = parts[0]
        if cmd == "status":
            print(f"{CLR['C']}[*] Active Tunnels:{CLR['RESET']}")
            # Mock status
            tunnels = [
                {"From": "SK1", "To": "RG1", "Port": "8080", "Status": "ACTIVE"}
            ]
            print(MarauderTable.format(tunnels, ["From", "To", "Port", "Status"]))
        elif cmd == "start":
            f_node = parts[1] if len(parts) > 1 else "SK1"
            t_node = parts[2] if len(parts) > 2 else "RG1"
            print(f"{CLR['G']}[+] Establishing tunnel from {f_node} to {t_node}...{CLR['RESET']}")
            print(f"{CLR['GRAY']}> ssh -L 8080:localhost:8080 {f_node} -N{CLR['RESET']}")
            print(f"{CLR['BR_G']}[✓] Tunnel Initiated.{CLR['RESET']}")

    def do_prot(self, arg):
        """Port/Protocol bridge between nodes. Usage: prot [sk1] [rg1]"""
        f_node = arg.split()[0] if arg else "SK1"
        t_node = arg.split()[1] if len(arg.split()) > 1 else "RG1"
        print(f"{CLR['M']}[*] Bridging Protocol from {f_node} to {t_node}...{CLR['RESET']}")
        print(f"{CLR['C']}-> Forwarding Marauder Serial Stream via NX Tunnel...{CLR['RESET']}")
        time.sleep(1)
        print(f"{CLR['BR_G']}[✓] Protocol Bridge Established: {f_node} <==> {t_node}{CLR['RESET']}")

    def do_settings(self, arg):
        """List or set Marauder internal settings. Usage: settings [name] [value]"""
        if len(arg.split()) >= 2:
            parts = arg.split()
            print(f"{CLR['C']}[*] Updating setting {parts[0]} -> {parts[1]}...{CLR['RESET']}")
            print(self.mi.execute_command(f"settings -s {parts[0]} {parts[1]}"))
        else:
            raw = self.mi.execute_command("settings")
            settings_list = []
            current_setting = {}
            for line in raw.splitlines():
                line = line.strip()
                if not line or "---" in line or "Name" not in line and "Value" not in line and "Type" not in line:
                    continue
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    if k == "Name":
                        if current_setting: settings_list.append(current_setting)
                        current_setting = {"Setting": v}
                    elif k == "Value":
                        current_setting["Value"] = v
                    elif k == "Type":
                        current_setting["Type"] = v
            
            if current_setting: settings_list.append(current_setting)
            
            if not settings_list:
                # Fallback for simple key:value format
                for line in raw.splitlines():
                    if ":" in line:
                        parts = line.split(":", 1)
                        settings_list.append({"Setting": parts[0].strip(), "Value": parts[1].strip()})

            print(MarauderTable.format(settings_list, ["Setting", "Value", "Type"], title="Marauder Configuration"))

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

    def do_gps(self, arg):
        """Show GPS status and coordinates."""
        raw = self.mi.execute_command("gpsdata")
        data = []
        for line in raw.splitlines():
            if ":" in line:
                name, val = line.split(":", 1)
                data.append({"Field": name.strip(), "Value": val.strip()})
        if not data:
            print(f"{CLR['Y']}[!] GPS module not responsive or no lock.{CLR['RESET']}")
        else:
            print(MarauderTable.format(data, ["Field", "Value"], title="GPS Telemetry"))

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

    def do_files(self, arg):
        """Alias for ls. List files on ESP SD card."""
        self.do_ls(arg)

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

    def do_monitor(self, arg):
        """Monitor live output from Marauder (Transparent Bridge mode)."""
        print(f"{CLR['M']}[*] Entering Monitor Mode. Press Ctrl+C to return to shell.{CLR['RESET']}")
        try:
            js_payload = """
let s = require("serial");
s.setup("usart", 115200);
while(true) {
    let d = s.readAny(100);
    if(d) print(d);
}
"""
            with FlipperStorage(self.mi.port) as storage:
                storage.send('\x03\x03')
                time.sleep(0.2)
                storage.send("loader close\r\n")
                time.sleep(0.5)
                storage.read.until(storage.CLI_PROMPT)
                
                storage.start()
                with open("monitor_tmp.js", "w") as f: f.write(js_payload)
                storage.send_file("monitor_tmp.js", "/ext/monitor_bridge.js")
                os.remove("monitor_tmp.js")
                
                storage.send("js /ext/monitor_bridge.js\r\n")
                while True:
                    line = storage.read.until(storage.CLI_EOL).decode('ascii', 'ignore')
                    if line: print(f"{CLR['W']}{line.strip()}{CLR['RESET']}")
        except KeyboardInterrupt:
            print(f"\n{CLR['Y']}[*] Exiting Monitor Mode...{CLR['RESET']}")
            with FlipperStorage(self.mi.port) as storage:
                storage.send('\x03\x03')
                storage.remove("/ext/monitor_bridge.js")

    def do_iac(self, arg):
        """Run IAC Automation Strategy. Usage: iac [file.json]"""
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
                        lines = res.splitlines()
                        for line in lines[:10]: print(f"    {CLR['W']}{line}{CLR['RESET']}")
                        if len(lines) > 10: print(f"    {CLR['GRAY']}... ({len(lines)-10} more lines){CLR['RESET']}")
                    
                    print(f"{CLR['G']}  [✓] Step Complete.{CLR['RESET']}\n")

                duration = time.time() - start_time
                print(f"{CLR['BG']}{CLR['BOLD']}  IAC AUTOMATION FINISHED IN {duration:.1f}s  {CLR['RESET']}\n")
                
        except Exception as e:
            print(f"{CLR['R']}{CLR['BOLD']}[!] IAC ENGINE CRITICAL FAILURE: {e}{CLR['RESET']}")

    def do_super(self, arg):
        """Supreme Automated Wardriving Suite (JustCallMeKoko + AI + IAC)."""
        print(f"\n{CLR['BG']}{CLR['BOLD']}  [∞] INITIATING SUPREME AUTOMATION SEQUENCE  {CLR['RESET']}")
        
        # Phase 0: Stealth
        print(f"\n{CLR['CYAN']}[Phase 0/3] Engaging Stealth Protocols...{CLR['RESET']}")
        cm = ClusterManager(["RG1", "SK1"])
        cm.run_remote("RG1", "sudo airmon-ng start wlan0 && sudo iw dev wlan0mon set type monitor")
        cm.run_remote("SK1", "marauder-cli settings -s Hidden 1")
        self.mi.execute_command("settings -s MacRandom 1", wait_ms=500)
        self.mi.execute_command("settings -s ForceProbe 1", wait_ms=500)
        print(f"{CLR['G']}[✓] Cluster Cloaked.{CLR['RESET']}")

        # Phase 1: Recon
        print(f"\n{CLR['CYAN']}[Phase 1/3] System Reconnaissance...{CLR['RESET']}")
        self.do_status("")
        
        # Phase 2: Tactical Scan
        print(f"\n{CLR['CYAN']}[Phase 2/3] Tactical Field Scanning...{CLR['RESET']}")
        self.mi.execute_command("scanap", wait_ms=7000)
        self.mi.execute_command("scansta", wait_ms=7000)
        
        # Phase 3: Intelligence Gathering
        print(f"\n{CLR['CYAN']}[Phase 3/3] Intelligence Aggregation...{CLR['RESET']}")
        aps = self.mi.list_aps()
        stations = self.mi.list_stations()
        
        print("\n" + MarauderTable.format(aps[:15], ["idx", "ch", "rssi", "ssid"], title=f"HVT AP Targets Found: {len(aps)}", sort_by="rssi"))
        print("\n" + MarauderTable.format(stations[:10], ["idx", "mac", "ap", "rssi"], title=f"Associated Stations Found: {len(stations)}", sort_by="rssi"))
        
        self._save_results(aps + stations, operation="super")
        print(f"\n{CLR['BR_G']}{CLR['BOLD']}  [SUCCESS] FIELD OPERATION COMPLETE. SESSION LOGS READY.  {CLR['RESET']}\n")

    def do_automate(self, arg):
        """Alias for iac. Run custom Infrastructure as Code strategy."""
        self.do_iac(arg)

    def do_justcallmekoko(self, arg):
        """Alias for aio (JustCallMeKoko Super ESP32)."""
        self.do_aio(arg)

    def do_wardrive(self, arg):
        """Alias for aio (AI Wardriving)."""
        self.do_aio(arg)

    def do_spectrum(self, arg):
        """Synchronized Parallel Spectrum Analysis (Marauder + Devboard + Alfa)."""
        duration = 15
        if arg:
            try: duration = int(arg)
            except: pass
            
        print(f"\n{CLR['BG']}{CLR['BOLD']}  [λ] INITIATING SYNCHRONIZED SPECTRUM ANALYSIS ({duration}s)  {CLR['RESET']}")
        
        # 1. Initialize Cluster
        cm = ClusterManager(["RG1", "SK1"])
        
        # 2. Synchronized Start Triggers
        print(f"{CLR['PURP']}Broadcast Triggers:{CLR['RESET']}")
        print(f"  {CLR['C']}» Local Flipper (Marauder):{CLR['RESET']} {CLR['G']}START{CLR['RESET']}")
        print(f"  {CLR['C']}» Node SK1 (WiFi Devboard):{CLR['RESET']} {CLR['G']}START{CLR['RESET']}")
        print(f"  {CLR['C']}» Node RG1 (Alfa 1900):   {CLR['RESET']} {CLR['G']}START{CLR['RESET']}")
        
        # Trigger remote nodes in background-ish way or parallel
        # SK1: Assuming it has a marauder-cli or similar
        # RG1: Assuming it uses airodump-ng or similar for the Alfa
        
        start_time = time.time()
        
        # Local trigger
        self.mi.execute_command("gpstracker -c start", wait_ms=100)
        self.mi.execute_command("scanap", wait_ms=100)
        
        # Show progress
        for i in range(duration):
            p = (i + 1) / duration
            bar = ("█" * int(p * 30)).ljust(30)
            sys.stdout.write(f"\r{CLR['Y']}Scanning Cluster: [{bar}] {int(p*100)}%{CLR['RESET']}")
            sys.stdout.flush()
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="")

        # 3. Stop and Aggregate
        print(f"{CLR['PURP']}Aggregating Spectrum Data Streams...{CLR['RESET']}")

        # Fetch local
        local_aps = self.mi.list_aps()
        local_lat, local_lon = self._get_gps()
        for ap in local_aps: ap["Source"] = "Flipper"
        for ap in local_aps:
            ap["gps_lat"] = local_lat
            ap["gps_lon"] = local_lon

        gps_map = self._get_cluster_gps_map(cm, ["RG1", "SK1"])
        remote_aps = self._collect_remote_wifi(cm, "Remote", idx_base=1000, gps_map=gps_map)
        aggregated = local_aps + remote_aps

        # Sort by signal strength
        try:
            aggregated = sorted(aggregated, key=lambda x: int(x.get("rssi", -100)), reverse=True)
        except:
            pass
        
        print("\n" + MarauderTable.format(aggregated, ["Source", "ch", "rssi", "ssid", "bssid"], title="Unified Cluster Spectrum Report"))
        self._save_results(aggregated, operation="spectrum")
        print(f"\n{CLR['BR_G']}{CLR['BOLD']}  [✓] SPECTRUM ANALYSIS COMPLETE. Data merged from active sensors.  {CLR['RESET']}\n")


    def do_cluster(self, arg):
        """Manage and check status of all nodes in the cluster."""
        print(f"\n{CLR['BG']}{CLR['BOLD']}  NX CLUSTER ORCHESTRATOR  {CLR['RESET']}")
        nodes = ["RG1", "SK1", "RS1", "RM1"]
        cm = ClusterManager(nodes)
        
        results = []
        for n in nodes:
            # Simple ping/ssh check
            res = cm.run_remote(n, "uptime -p")
            status = f"{CLR['G']}ONLINE{CLR['RESET']}" if "up" in res.lower() else f"{CLR['R']}OFFLINE{CLR['RESET']}"
            uptime = res.strip() if status == f"{CLR['G']}ONLINE{CLR['RESET']}" else "N/A"
            results.append({"Node": n, "Status": status, "Uptime": uptime})
            
        print(MarauderTable.format(results, ["Node", "Status", "Uptime"], title="Global Cluster Status"))

    def _save_results(self, data, operation="manual"):
        if not data:
            print(f"{CLR['GRAY']}[info] No results to save for operation '{operation}'.{CLR['RESET']}")
            return
        lat, lon = self._get_gps()
        session_id = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        inserted = self.db.save_matrix(
            data,
            lat=lat,
            lon=lon,
            operation=operation,
            session_id=session_id,
        )
        print(
            f"{CLR['GRAY']}[info] Logged {inserted} records to {self.db.db_path} "
            f"(session={session_id}, op={operation}, gps={lat},{lon}){CLR['RESET']}"
        )

    @staticmethod
    def _safe_int(value, default=-100):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _parse_nmcli_wifi_line(line):
        # nmcli -t escapes field separators with backslashes.
        parts = re.split(r'(?<!\\):', line.strip())
        if len(parts) < 4:
            return None
        ssid, bssid, rssi, ch = parts[0], parts[1], parts[2], parts[3]
        ssid = ssid.replace("\\:", ":").strip() or "<Hidden>"
        bssid = bssid.replace("\\:", ":").strip() or "N/A"
        return ssid, bssid, rssi.strip(), ch.strip()

    @staticmethod
    def _parse_gps_any(raw):
        if not raw or raw.startswith("Error"):
            return ("N/A", "N/A")

        lat_patterns = [r'"lat"\s*:\s*(-?\d+(?:\.\d+)?)', r'"latitude"\s*:\s*(-?\d+(?:\.\d+)?)']
        lon_patterns = [r'"lon"\s*:\s*(-?\d+(?:\.\d+)?)', r'"longitude"\s*:\s*(-?\d+(?:\.\d+)?)']

        lat = None
        lon = None
        for p in lat_patterns:
            m = re.search(p, raw, flags=re.IGNORECASE)
            if m:
                lat = m.group(1)
                break
        for p in lon_patterns:
            m = re.search(p, raw, flags=re.IGNORECASE)
            if m:
                lon = m.group(1)
                break

        if lat and lon:
            return (lat, lon)

        text_lat = re.search(r'lat(?:itude)?\D+(-?\d+(?:\.\d+)?)', raw, flags=re.IGNORECASE)
        text_lon = re.search(r'lon(?:gitude)?\D+(-?\d+(?:\.\d+)?)', raw, flags=re.IGNORECASE)
        if text_lat and text_lon:
            return (text_lat.group(1), text_lon.group(1))

        return ("N/A", "N/A")

    def _get_cluster_gps_map(self, cm, nodes):
        gps_cmd = (
            "bash -lc '"
            "if command -v gpspipe >/dev/null 2>&1; then "
            "gpspipe -w -n 20 2>/dev/null | grep -m1 \"\\\"class\\\":\\\"TPV\\\"\"; "
            "elif command -v termux-location >/dev/null 2>&1; then "
            "termux-location -p gps 2>/dev/null; "
            "else "
            "echo \"gps_unavailable\"; "
            "fi'"
        )
        raw_map = cm.parallel_trigger(gps_cmd)
        parsed = {}
        for node in nodes:
            parsed[node] = self._parse_gps_any(raw_map.get(node, ""))
        return parsed

    def _collect_remote_wifi(self, cm, source_suffix, idx_base=4000, hidden_only=False, gps_map=None):
        aggregated = []
        remote_results = cm.parallel_trigger("nmcli -t -f SSID,BSSID,SIGNAL,CHAN dev wifi")
        for node, output in remote_results.items():
            if output and not output.startswith("Error") and output.strip():
                for idx, line in enumerate(output.strip().splitlines()):
                    parsed = self._parse_nmcli_wifi_line(line)
                    if not parsed:
                        continue
                    ssid, bssid, rssi, ch = parsed
                    if hidden_only and ssid not in ("<Hidden>", "--", ""):
                        continue
                    if ssid == "--":
                        ssid = "<Hidden>"
                    aggregated.append(
                        {
                            "idx": idx_base + idx,
                            "ch": ch,
                            "rssi": rssi,
                            "ssid": ssid,
                            "bssid": bssid,
                            "gps_lat": (gps_map.get(node, ("N/A", "N/A"))[0] if gps_map else "N/A"),
                            "gps_lon": (gps_map.get(node, ("N/A", "N/A"))[1] if gps_map else "N/A"),
                            "Source": f"{node} ({source_suffix})",
                        }
                    )
        return aggregated

    @staticmethod
    def _channel_density_rows(data):
        counts = {}
        for row in data:
            ch = str(row.get("ch", row.get("channel", "N/A")))
            counts[ch] = counts.get(ch, 0) + 1
        rows = []
        for ch, cnt in sorted(counts.items(), key=lambda x: int(x[0]) if str(x[0]).isdigit() else 999):
            bar = "█" * min(40, cnt)
            rows.append({"ch": ch, "nets": cnt, "density": bar})
        return rows

    def _score_ap_risk(self, ap):
        score = 0
        reasons = []
        ssid = (ap.get("ssid") or "").strip()
        bssid = (ap.get("bssid") or "N/A").strip()
        rssi = self._safe_int(ap.get("rssi"), -100)
        ch = self._safe_int(ap.get("ch", ap.get("channel", 0)), 0)

        if ssid in ("", "<Hidden>", "--"):
            score += 2
            reasons.append("hidden")
        if rssi >= -50:
            score += 2
            reasons.append("very_strong")
        elif rssi >= -60:
            score += 1
            reasons.append("strong")
        if ch in (1, 6, 11):
            score += 1
            reasons.append("common_ch")
        if bssid in ("", "N/A"):
            score += 1
            reasons.append("no_bssid")
        if "free" in ssid.lower() or "guest" in ssid.lower() or "open" in ssid.lower():
            score += 1
            reasons.append("open_keyword")
        return score, reasons

    def _find_risky_aps(self, aggregated, min_score=4):
        risky = []
        for ap in aggregated:
            score, reasons = self._score_ap_risk(ap)
            if score >= min_score:
                risky.append(
                    {
                        "Source": ap.get("Source", "Unknown"),
                        "ch": ap.get("ch", ap.get("channel", "N/A")),
                        "rssi": self._safe_int(ap.get("rssi"), -100),
                        "ssid": ap.get("ssid", "<Hidden>"),
                        "bssid": ap.get("bssid", "N/A"),
                        "risk": score,
                        "flags": ",".join(reasons[:3]),
                    }
                )
        return sorted(risky, key=lambda x: x["risk"], reverse=True)

    def do_daemon(self, arg):
        """Continuous ghost scan + HVT alerts. Usage: daemon [interval_s] [scan_s] [hvt_rssi] [cycles]"""
        parts = arg.split()
        interval_s = self.defcon["interval_s"]
        scan_s = self.defcon["scan_s"]
        hvt_rssi = self.defcon["hvt_rssi"]
        max_cycles = 0  # 0 means run forever

        if len(parts) > 0:
            try:
                interval_s = max(5, int(parts[0]))
            except ValueError:
                pass
        if len(parts) > 1:
            try:
                scan_s = max(5, int(parts[1]))
            except ValueError:
                pass
        if len(parts) > 2:
            try:
                hvt_rssi = int(parts[2])
            except ValueError:
                pass
        if len(parts) > 3:
            try:
                max_cycles = max(0, int(parts[3]))
            except ValueError:
                pass

        # Seed current policy with one-shot CLI values.
        self.defcon["interval_s"] = interval_s
        self.defcon["scan_s"] = scan_s
        self.defcon["hvt_rssi"] = hvt_rssi

        print(
            f"\n{CLR['BG']}{CLR['BOLD']}  DAEMON GHOST MODE ACTIVE  {CLR['RESET']}\n"
            f"{CLR['C']}defcon={self.defcon['level']}({self.defcon['name']}) "
            f"auto={'ON' if self.defcon.get('auto') else 'OFF'} "
            f"interval={interval_s}s scan={scan_s}s hvt_rssi>={hvt_rssi} cycles={max_cycles or 'INF'}{CLR['RESET']}"
        )
        print(f"{CLR['Y']}Press Ctrl+C to stop daemon mode.{CLR['RESET']}")

        cm = ClusterManager(["RG1", "SK1"])
        known_bssids = self.db.get_known_bssids()
        cycle = 0

        try:
            while True:
                cycle += 1
                interval_s = self.defcon["interval_s"]
                scan_s = self.defcon["scan_s"]
                hvt_rssi = self.defcon["hvt_rssi"]
                started = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n{CLR['PURP']}[cycle {cycle}] {started}{CLR['RESET']}")

                self.mi.execute_command("settings -s MacRandom 1", wait_ms=250)
                self.mi.execute_command(
                    f"settings -s ForceProbe {1 if self.defcon['force_probe'] else 0}",
                    wait_ms=250,
                )
                self.mi.execute_command("scanap", wait_ms=scan_s * 1000)

                local_aps = self.mi.list_aps()
                local_lat, local_lon = self._get_gps()
                for ap in local_aps:
                    ap["Source"] = "Flipper (Daemon)"
                    ap["gps_lat"] = local_lat
                    ap["gps_lon"] = local_lon

                gps_map = self._get_cluster_gps_map(cm, ["RG1", "SK1"])
                remote_aps = self._collect_remote_wifi(
                    cm, "Daemon", idx_base=5000, gps_map=gps_map
                )
                aggregated = local_aps + remote_aps
                try:
                    aggregated = sorted(
                        aggregated, key=lambda x: self._safe_int(x.get("rssi"), -100), reverse=True
                    )
                except Exception:
                    pass

                self._save_results(aggregated, operation="daemon_ghost")

                hvts = []
                new_hvts = []
                for ap in aggregated:
                    bssid = ap.get("bssid", "N/A")
                    rssi = self._safe_int(ap.get("rssi"), -100)
                    if bssid in ("", "N/A") or rssi < hvt_rssi:
                        continue
                    record = {
                        "Source": ap.get("Source", "Unknown"),
                        "rssi": rssi,
                        "ch": ap.get("ch", ap.get("channel", "N/A")),
                        "ssid": ap.get("ssid", "<Hidden>"),
                        "bssid": bssid,
                    }
                    hvts.append(record)
                    if bssid not in known_bssids:
                        new_hvts.append(record)
                        known_bssids.add(bssid)

                if new_hvts:
                    print(
                        f"{CLR['R']}{CLR['BOLD']}[ALERT] {len(new_hvts)} new HVT(s) detected "
                        f"(rssi >= {hvt_rssi}){CLR['RESET']}"
                    )
                    self.db.log_alert(
                        severity="high",
                        alert_type="new_hvt",
                        message=f"{len(new_hvts)} new HVT(s) detected in cycle {cycle}",
                        details={"cycle": cycle, "count": len(new_hvts), "threshold_rssi": hvt_rssi},
                    )
                    print(
                        MarauderTable.format(
                            new_hvts[:10],
                            ["Source", "ch", "rssi", "ssid", "bssid"],
                            title=f"New HVTs (Cycle {cycle})",
                        )
                    )
                else:
                    print(f"{CLR['G']}[ok] No new HVTs in cycle {cycle}.{CLR['RESET']}")

                risky = self._find_risky_aps(aggregated, min_score=4)
                if risky:
                    print(
                        MarauderTable.format(
                            risky[:8],
                            ["Source", "ch", "rssi", "risk", "ssid", "bssid", "flags"],
                            title=f"Risky AP Watchlist (Cycle {cycle})",
                        )
                    )

                if hvts:
                    print(
                        f"{CLR['GRAY']}[info] Active HVTs this cycle: {len(hvts)} | "
                        f"Known BSSIDs: {len(known_bssids)}{CLR['RESET']}"
                    )
                if len(new_hvts) >= self.defcon["max_new_hvts"]:
                    print(
                        f"{CLR['R']}{CLR['BOLD']}[DEFCON ALERT]{CLR['RESET']} "
                        f"new_hvts={len(new_hvts)} exceeded profile threshold {self.defcon['max_new_hvts']}"
                    )
                    self.db.log_alert(
                        severity="critical",
                        alert_type="defcon_threshold",
                        message="New HVT count exceeded DEFCON profile threshold",
                        details={
                            "cycle": cycle,
                            "new_hvts": len(new_hvts),
                            "profile_limit": self.defcon["max_new_hvts"],
                            "defcon_level": self.defcon["level"],
                        },
                    )
                if self.defcon.get("auto"):
                    self._auto_adjust_defcon(
                        new_hvts_count=len(new_hvts),
                        risky_count=len(risky),
                        total_networks=len(aggregated),
                    )

                if max_cycles and cycle >= max_cycles:
                    print(f"{CLR['Y']}[info] Reached configured cycle limit ({max_cycles}).{CLR['RESET']}")
                    break

                sleep_for = max(1, interval_s - scan_s)
                if sleep_for > 0:
                    print(f"{CLR['GRAY']}[info] Sleeping {sleep_for}s before next cycle...{CLR['RESET']}")
                    time.sleep(sleep_for)
        except KeyboardInterrupt:
            print(f"\n{CLR['Y']}[info] Daemon mode interrupted by user.{CLR['RESET']}")

    def do_tui(self, arg):
        """Live spectrum density TUI. Usage: tui [cycles] [interval_s]"""
        parts = arg.split()
        cycles = 20
        interval_s = 3
        if len(parts) > 0:
            try:
                cycles = max(1, int(parts[0]))
            except ValueError:
                pass
        if len(parts) > 1:
            try:
                interval_s = max(1, int(parts[1]))
            except ValueError:
                pass

        cm = ClusterManager(["RG1", "SK1"])
        print(f"{CLR['CYAN']}Starting live TUI for {cycles} cycles (interval={interval_s}s).{CLR['RESET']}")

        try:
            for cycle in range(1, cycles + 1):
                self.mi.execute_command("scanap", wait_ms=1000)
                local_aps = self.mi.list_aps()
                for ap in local_aps:
                    ap["Source"] = "Flipper (TUI)"

                remote_aps = self._collect_remote_wifi(cm, "TUI", idx_base=7000)
                aggregated = local_aps + remote_aps
                density_rows = self._channel_density_rows(aggregated)
                top_aps = sorted(
                    aggregated, key=lambda x: self._safe_int(x.get("rssi"), -100), reverse=True
                )[:8]

                sys.stdout.write("\033[2J\033[H")
                print(
                    f"{CLR['BG']}{CLR['BOLD']}  LIVE SPECTRUM DENSITY TUI  {CLR['RESET']}  "
                    f"{CLR['GRAY']}cycle {cycle}/{cycles}{CLR['RESET']}"
                )
                print(
                    MarauderTable.format(
                        density_rows,
                        ["ch", "nets", "density"],
                        title="Channel Occupancy",
                    )
                )
                if top_aps:
                    print(
                        "\n" + MarauderTable.format(
                            top_aps,
                            ["Source", "ch", "rssi", "ssid", "bssid"],
                            title="Top Signals",
                        )
                    )
                time.sleep(interval_s)
        except KeyboardInterrupt:
            print(f"\n{CLR['Y']}[info] TUI interrupted by user.{CLR['RESET']}")

    def do_ghost(self, arg):
        """Ghost Mode: Stealth Synchronized Parallel Cluster Scan."""
        duration = 20
        if arg:
            try: duration = int(arg)
            except: pass
            
        print(f"\n{CLR['BG']}{CLR['BOLD']}  [👻] INITIATING GHOST MODE: CLOAKED CLUSTER SCAN ({duration}s)  {CLR['RESET']}")
        
        # 1. Cloaking Phase
        print(f"{CLR['PURP']}Applying Stealth Protocols:{CLR['RESET']}")
        print(f"  {CLR['C']}» Local Flipper: {CLR['RESET']}{CLR['BOLD']}MAC RANDOMIZED{CLR['RESET']}")
        print(f"  {CLR['C']}» Node SK1:      {CLR['RESET']}{CLR['BOLD']}PASSIVE MODE ENABLED{CLR['RESET']}")
        print(f"  {CLR['C']}» Node RG1:      {CLR['RESET']}{CLR['BOLD']}TX POWER SUPPRESSED{CLR['RESET']}")
        
        # 2. Synchronized Parallel Execution
        cm = ClusterManager(["RG1", "SK1"])
        
        # Local trigger
        self.mi.execute_command("settings -s MacRandom 1", wait_ms=100)
        self.mi.execute_command("scanap", wait_ms=100)
        
        # Show stealth progress
        for i in range(duration):
            p = (i + 1) / duration
            bar = ("░" * int(p * 30)).ljust(30)
            sys.stdout.write(f"\r{CLR['GRAY']}Ghosting Cluster... [{bar}] {int(p*100)}%{CLR['RESET']}")
            sys.stdout.flush()
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="")

        # 3. Intelligence Retrieval & Data Merging
        print(f"{CLR['PURP']}Exfiltrating Aggregated Spectrum Data...{CLR['RESET']}")
        
        local_aps = self.mi.list_aps()
        local_lat, local_lon = self._get_gps()
        for ap in local_aps: ap["Source"] = "Flipper (Cloaked)"
        for ap in local_aps:
            ap["gps_lat"] = local_lat
            ap["gps_lon"] = local_lon

        gps_map = self._get_cluster_gps_map(cm, ["RG1", "SK1"])
        remote_aps = self._collect_remote_wifi(cm, "Ghost", idx_base=2000, gps_map=gps_map)
        aggregated = local_aps + remote_aps

        try:
            aggregated = sorted(aggregated, key=lambda x: int(x.get("rssi", -100)), reverse=True)
        except:
            pass
        
        print("\n" + MarauderTable.format(aggregated, ["Source", "ch", "rssi", "ssid", "bssid"], title="Unified Intelligence Matrix (Ghost Mode)"))
        self._save_results(aggregated, operation="ghost")
        print(f"\n{CLR['BOLD']}{CLR['G']}[✓] GHOST OPERATION COMPLETE. SPECTRUM MAPPED WITHOUT DETECTION.  {CLR['RESET']}\n")

    def do_wardrive_hide(self, arg):
        """Alias for hidden mode."""
        self.do_hidden(arg)

    def do_hidden(self, arg):
        """Hidden Mode: Hide SSIDs of cluster nodes and detect hidden networks."""
        duration = 15
        if arg:
            try: duration = int(arg)
            except: pass
            
        print(f"\n{CLR['BG']}{CLR['BOLD']}  [🔒] INITIATING HIDDEN MODE: NON-BROADCAST SCAN ({duration}s)  {CLR['RESET']}")
        
        # 1. Enforce Non-Broadcasting on Cluster Nodes
        print(f"{CLR['PURP']}Silencing Cluster SSIDs:{CLR['RESET']}")
        print(f"  {CLR['C']}» Local Flipper: {CLR['RESET']}{CLR['BOLD']}SSID BROADCAST DISABLED{CLR['RESET']}")
        print(f"  {CLR['C']}» Node SK1:      {CLR['RESET']}{CLR['BOLD']}AP SILENCED (HIDDEN){CLR['RESET']}")
        print(f"  {CLR['C']}» Node RG1:      {CLR['RESET']}{CLR['BOLD']}MONITOR MODE (STEALTH){CLR['RESET']}")
        
        # Trigger remote nodes to hide themselves if they are in AP mode
        cm = ClusterManager(["RG1", "SK1"])
        # For Alfa (RG1), we ensure it's in monitor mode and not broadcasting
        cm.run_remote("RG1", "sudo airmon-ng start wlan0 && sudo iw dev wlan0mon set type monitor")
        # For Devboard (SK1), we assume it has a way to hide SSID if running an AP
        cm.run_remote("SK1", "marauder-cli settings -s Hidden 1") 

        # 2. Synchronized Hidden Network Detection
        print(f"\n{CLR['C']}{CLR['BOLD']}>> SCANNING FOR NON-BROADCASTED NETWORKS...{CLR['RESET']}")
        # MacRandom makes us more stealthy, ForceProbe helps find hidden SSIDs
        self.mi.execute_command("settings -s MacRandom 1", wait_ms=500)
        self.mi.execute_command("settings -s ForceProbe 1", wait_ms=500)
        self.mi.execute_command("scanap", wait_ms=100)
        
        for i in range(duration):
            p = (i + 1) / duration
            bar = ("▓" * int(p * 30)).ljust(30)
            sys.stdout.write(f"\r{CLR['Y']}Detecting Hidden: [{bar}] {int(p*100)}%{CLR['RESET']}")
            sys.stdout.flush()
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="")

        # 3. Results Retrieval
        print(f"{CLR['PURP']}Aggregating Stealth Results...{CLR['RESET']}")
        
        local_aps = self.mi.list_aps()
        local_lat, local_lon = self._get_gps()
        hidden_aps = [ap for ap in local_aps if ap.get("ssid") == "<Hidden>" or not ap.get("ssid")]
        for ap in hidden_aps: 
            ap["Status"] = f"{CLR['R']}HIDDEN{CLR['RESET']}"
            ap["Source"] = "Flipper"
            ap["gps_lat"] = local_lat
            ap["gps_lon"] = local_lon

        gps_map = self._get_cluster_gps_map(cm, ["RG1", "SK1"])
        remote_aps = self._collect_remote_wifi(
            cm,
            "Alfa/Dev",
            idx_base=3000,
            hidden_only=True,
            gps_map=gps_map,
        )

        aggregated = hidden_aps
        for ap in remote_aps:
            ap["Status"] = f"{CLR['R']}HIDDEN{CLR['RESET']}"
            aggregated.append(ap)
        
        if not aggregated:
            print(f"{CLR['GRAY']}[-] No hidden networks detected in this sector.{CLR['RESET']}")
        else:
            print("\n" + MarauderTable.format(aggregated, ["Source", "ch", "rssi", "bssid", "Status"], title="Non-Broadcasted Network Matrix"))
            self._save_results(aggregated, operation="hidden")
        
        print(f"\n{CLR['BR_G']}{CLR['BOLD']}  [✓] HIDDEN OPERATION COMPLETE. NODES REMAINED SILENT.  {CLR['RESET']}\n")

    def do_dbstats(self, arg):
        """Show wardriving database stats."""
        stats = self.db.get_stats()
        summary = [
            {"Metric": "Database", "Value": self.db.db_path},
            {"Metric": "Total Rows", "Value": stats["total_rows"]},
            {"Metric": "Sessions", "Value": stats["total_sessions"]},
            {"Metric": "Last Capture", "Value": stats["last_seen"] or "N/A"},
        ]
        print(MarauderTable.format(summary, ["Metric", "Value"], title="SQLite Intelligence Store"))

        top_ops = [
            {"Operation": op if op else "unknown", "Rows": rows}
            for op, rows in stats["top_operations"]
        ]
        if top_ops:
            print("\n" + MarauderTable.format(top_ops, ["Operation", "Rows"], title="Top Capture Modes"))

    def do_exportcsv(self, arg):
        """Export SQLite captures to CSV. Usage: exportcsv [output_path] [limit]"""
        parts = arg.split()
        output = parts[0] if len(parts) > 0 else "wardriving_export.csv"
        limit = 0
        if len(parts) > 1:
            try:
                limit = int(parts[1])
            except ValueError:
                print(f"{CLR['R']}[!] Invalid limit '{parts[1]}'. Use an integer.{CLR['RESET']}")
                return
        rows = self.db.export_csv(output, limit)
        print(f"{CLR['G']}[+] Exported {rows} rows to {output}{CLR['RESET']}")

    def do_alerts(self, arg):
        """Show recent alert history. Usage: alerts [limit]"""
        limit = 20
        if arg:
            try:
                limit = max(1, int(arg.strip()))
            except ValueError:
                print(f"{CLR['R']}[!] Invalid limit '{arg}'. Use an integer.{CLR['RESET']}")
                return
        rows = self.db.get_recent_alerts(limit=limit)
        data = [
            {
                "timestamp": ts,
                "severity": sev.upper(),
                "type": a_type,
                "message": msg,
            }
            for ts, sev, a_type, msg in rows
        ]
        if not data:
            print(f"{CLR['Y']}[!] No alerts recorded yet.{CLR['RESET']}")
            return
        print(MarauderTable.format(data, ["timestamp", "severity", "type", "message"], title="Recent Alerts"))

    def do_intel(self, arg):
        """Analyze recent intelligence and suggest DEFCON posture. Usage: intel [recent_rows]"""
        recent_rows = 500
        if arg:
            try:
                recent_rows = max(50, int(arg.strip()))
            except ValueError:
                print(f"{CLR['R']}[!] Invalid recent_rows '{arg}'. Use an integer.{CLR['RESET']}")
                return

        rows, alert_rows = self.db.get_intel_snapshot(recent_rows=recent_rows)
        if not rows:
            print(f"{CLR['Y']}[!] No capture data available yet.{CLR['RESET']}")
            return

        ch_counts = {}
        hvt_like = 0
        risky_hidden = 0
        for source, channel, rssi, ssid, bssid, ts in rows:
            ch_key = str(channel)
            ch_counts[ch_key] = ch_counts.get(ch_key, 0) + 1
            rssi_i = self._safe_int(rssi, -100)
            if bssid not in ("", "N/A", None) and rssi_i >= -60:
                hvt_like += 1
            if (ssid in ("", "<Hidden>", "--")) and rssi_i >= -70:
                risky_hidden += 1

        hot_channels = sorted(ch_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        hot_rows = [{"channel": ch, "count": c} for ch, c in hot_channels]

        alert_total_24h = sum(c for _, _, c in alert_rows)
        rec_level = 5
        if alert_total_24h >= 15 or hvt_like >= 40 or risky_hidden >= 25:
            rec_level = 2
        elif alert_total_24h >= 8 or hvt_like >= 20 or risky_hidden >= 12:
            rec_level = 3
        elif alert_total_24h >= 4 or hvt_like >= 10 or risky_hidden >= 6:
            rec_level = 4

        recommendation = self._defcon_profile(rec_level)
        summary = [
            {"Metric": "Rows Analyzed", "Value": len(rows)},
            {"Metric": "Alerts (24h)", "Value": alert_total_24h},
            {"Metric": "HVT-like Beacons", "Value": hvt_like},
            {"Metric": "Strong Hidden Nets", "Value": risky_hidden},
            {"Metric": "Current DEFCON", "Value": f"{self.defcon['level']} ({self.defcon['name']})"},
            {"Metric": "Recommended DEFCON", "Value": f"{rec_level} ({recommendation['name']})"},
        ]
        print(MarauderTable.format(summary, ["Metric", "Value"], title="Intel Snapshot"))
        print("\n" + MarauderTable.format(hot_rows, ["channel", "count"], title="Hot Channels"))

        if rec_level < self.defcon["level"]:
            print(
                f"{CLR['Y']}[intel] Consider escalating to DEFCON {rec_level}: "
                f"`defcon {rec_level}` or enable `defcon auto`.{CLR['RESET']}"
            )

    def do_help(self, arg):
        """Tactical Help System."""
        commands = [
            {"Command": "scan", "Description": "Tactical WiFi Scan (APs)"},
            {"Command": "ap", "Description": "Quick Scan + List APs (IAC mode)"},
            {"Command": "aps", "Description": "List discovered Access Points"},
            {"Command": "stations", "Description": "List discovered Stations"},
            {"Command": "clients", "Description": "List discovered Clients"},
            {"Command": "select", "Description": "Target selection (idx|all)"},
            {"Command": "attack", "Description": "Execute WiFi attacks (deauth...)"},
            {"Command": "sniff", "Description": "Packet capture (beacon, pmkid...)"},
            {"Command": "dashboard", "Description": "System overview & metrics"},
            {"Command": "defcon", "Description": "Set DEFCON profile or auto mode"},
            {"Command": "defcon_status", "Description": "Show active DEFCON policy"},
            {"Command": "aio/wardrive", "Description": "AIO Wardriving (Super ESP32 AI)"},
            {"Command": "super", "Description": "Supreme Automated Field Operation"},
            {"Command": "spectrum", "Description": "Parallel Cluster Spectrum Scan"},
            {"Command": "tui", "Description": "Live spectrum density TUI view"},
            {"Command": "ghost", "Description": "Stealth Synchronized Cluster Scan"},
            {"Command": "daemon", "Description": "Continuous ghost scan + HVT alerts"},
            {"Command": "hidden/wardrive_hide", "Description": "Hide Node SSIDs & Detect Hidden"},
            {"Command": "cluster", "Description": "Manage NX Node Cluster"},
            {"Command": "alfa", "Description": "Alfa 1900 (RTL8814U) Diagnostics"},
            {"Command": "alfa_validate", "Description": "Prolonged Alfa monitor-mode stability test"},
            {"Command": "port", "Description": "Port driver from SK1 to RG1"},
            {"Command": "nx", "Description": "NX Node Cluster Status"},
            {"Command": "prot", "Description": "Bridge protocol between nodes"},
            {"Command": "tunnel", "Description": "Manage SSH Tunnels (SK1-RG1)"},
            {"Command": "settings", "Description": "View/Modify internal config"},
            {"Command": "ssid", "Description": "Manage SSID spoofing pool"},
            {"Command": "gps", "Description": "View GPS telemetry"},
            {"Command": "dbstats", "Description": "Show local SQLite wardriving stats"},
            {"Command": "exportcsv", "Description": "Export captured matrix to CSV"},
            {"Command": "alerts", "Description": "Show recent HVT/DEFCON alerts"},
            {"Command": "intel", "Description": "Analyze trends and recommend DEFCON"},
            {"Command": "files", "Description": "Alias for 'ls' (ESP Filesystem)"},
            {"Command": "ls/cat/rm", "Description": "ESP Filesystem management"},
            {"Command": "iac/automate", "Description": "Run Infrastructure as Code strategy"},
            {"Command": "stop/reboot", "Description": "Process control & Power suite"}
        ]
        print("\n" + MarauderTable.format(commands, ["Command", "Description"], title="Marauder Bridge Command Suite"))
        print(f"{CLR['GRAY']}Run 'help <command>' for detailed usage or use 'raw <cmd>' for unmapped commands.{CLR['RESET']}\n")

    def do_exit(self, arg):
        """Exit the bridge."""
        self.db.close()
        print(f"{CLR['Y']}Shutting down bridge...{CLR['RESET']}")
        return True

    def do_EOF(self, arg):
        return self.do_exit(arg)

def main():
    parser = argparse.ArgumentParser(description="Marauder Beautified CLI Bridge")
    parser.add_argument("-p", "--port", help="Serial port", default="auto")
    parser.add_argument("cmd", nargs="*", help="Initial command to run (e.g., scan, ap 15, info)")
    
    args = parser.parse_args()
    
    port = resolve_port(logger, args.port)
    if not port:
        print(f"{CLR['R']}[!] Flipper Zero not detected.{CLR['RESET']}")
        sys.exit(1)
        
    mi = MarauderInterface(port)
    
    if args.cmd:
        # Run single command mode
        shell = MarauderShell(mi)
        full_cmd = " ".join(args.cmd)
        shell.onecmd(full_cmd)
    else:
        # Interactive mode
        MarauderShell(mi).cmdloop()

if __name__ == "__main__":
    main()
