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

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class MarauderIaC:
    def __init__(self, port):
        self.port = port
        self.storage = FlipperStorage(port)
        self.temp_js = "/ext/marauder_auto_iac.js"
        self.state = {"aps": [], "stations": [], "selected": [], "gps": {}}

    def _exec(self, cmd, wait_ms=1000):
        """Internal low-level execution via JS Bridge"""
        js = f"""
let s=require("serial");
s.setup("usart", 115200);
s.write("{cmd}\\r\\n");
for(let i=0; i<{(wait_ms//200)+2}; i++){{
    let d=s.readAny(200);
    if(d) print(d);
}}
s.end();
"""
        with open("iac_payload.js", "w") as f: f.write(js)
        self.storage.start()
        try: self.storage.remove(self.temp_js)
        except: pass
        self.storage.send_file("iac_payload.js", self.temp_js)
        os.remove("iac_payload.js")
        self.storage.send(f"js {self.temp_js}\r\n")
        res = self.storage.read.until(self.storage.CLI_PROMPT).decode('ascii', 'ignore')
        self.storage.remove(self.temp_js)
        return res

    # --- 1. CORE SYSTEM FUNCTIONS ---
    def info(self): return self._exec("info")
    def reboot(self): return self._exec("reboot")
    def stop(self): return self._exec("stopscan")
    def list(self, target="a"): return self._exec(f"list -{target}") # a=ap, s=station, c=client
    
    # --- 2. SCANNING FUNCTIONS ---
    def scan_aps(self, t=10): return self._exec("scanap", t*1000)
    def scan_stations(self, t=10): return self._exec("scansta", t*1000)
    def scan_all(self, t=10): return self._exec("scanall", t*1000)
    
    # --- 3. SNIFFING FUNCTIONS ---
    def sniff_beacon(self): return self._exec("sniffbeacon")
    def sniff_pmkid(self, ch=1): return self._exec(f"sniffpmkid -c {ch}")
    def sniff_pwn(self): return self._exec("sniffpwn")
    def sniff_esp(self): return self._exec("sniffesp")
    def sniff_raw(self): return self._exec("sniffraw")

    # --- 4. ATTACK FUNCTIONS ---
    def attack_deauth(self): return self._exec("attack -t deauth")
    def attack_beacon_list(self): return self._exec("attack -t beacon -l")
    def attack_beacon_spam(self): return self._exec("attack -t beacon -a")
    def attack_rickroll(self): return self._exec("attack -t rickroll")

    # --- 5. GPS & TRACKING ---
    def gps_info(self): return self._exec("gpsdata")
    def gps_start(self): return self._exec("gpstracker -c start")
    def wardrive(self, start=True): return self._exec(f"wardrive -{'s' if start else 'f'}")

    # --- 6. EVIL PORTAL & KARMA ---
    def portal_start(self, html="index.html"): return self._exec(f"evilportal -c start -w {html}")
    def karma(self, index=0): return self._exec(f"karma -p {index}")

    # --- 7. UTILITIES ---
    def set_channel(self, ch): return self._exec(f"channel -s {ch}")
    def set_led(self, hex_color): return self._exec(f"led -s {hex_color}")
    def select(self, indexes): return self._exec(f"select -a {indexes}") # e.g. "0,1,2"

def run_workflow(iac, workflow_file):
    with open(workflow_file, 'r') as f:
        steps = json.load(f)
    
    logger.info(f"[*] Running Workflow: {workflow_file}")
    for step in steps:
        method = getattr(iac, step['action'])
        params = step.get('params', {})
        logger.info(f"[>] Action: {step['action']} {params}")
        print(method(**params))
        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", help="JSON workflow file")
    args = parser.parse_args()
    
    port = resolve_port(logger)
    if not port: sys.exit(1)
    
    iac = MarauderIaC(port)
    if args.workflow:
        run_workflow(iac, args.workflow)
    else:
        # Automated Recon Example
        iac.info()
        iac.scan_aps(t=5)
        print(iac.list("a"))
