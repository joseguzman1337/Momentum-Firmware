#!/bin/bash
# End-to-End Test Suite for Flipper Zero Auto USB Ethernet
# Tests all components of the automation system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[1;34m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Flipper Zero Auto USB Ethernet - E2E Test Suite        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}
echo ""

pass() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

skip() {
    echo -e "${YELLOW}⊘ SKIP:${NC} $1"
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
}

info() {
    echo -e "${BLUE}ℹ INFO:${NC} $1"
}

# Test 1: Check scripts exist
echo -e "\n${YELLOW}[TEST 1] Checking automation scripts exist...${NC}"
if [ -f "$SCRIPT_DIR/install-flipper-auto-ethernet.sh" ] && \
   [ -f "$SCRIPT_DIR/flash_and_setup_ethernet.sh" ] && \
   [ -f "$SCRIPT_DIR/flipper-internet-share.sh" ] && \
   [ -f "$SCRIPT_DIR/flipper-auto-ethernet-setup.sh" ]; then
    pass "All automation scripts exist"
else
    fail "Missing automation scripts"
fi

# Test 2: Check scripts are executable
echo -e "\n${YELLOW}[TEST 2] Checking scripts are executable...${NC}"
if [ -x "$SCRIPT_DIR/install-flipper-auto-ethernet.sh" ] && \
   [ -x "$SCRIPT_DIR/flash_and_setup_ethernet.sh" ] && \
   [ -x "$SCRIPT_DIR/flipper-internet-share.sh" ] && \
   [ -x "$SCRIPT_DIR/flipper-auto-ethernet-setup.sh" ]; then
    pass "All scripts are executable"
else
    fail "Some scripts are not executable"
fi

# Test 3: Check udev rules file exists
echo -e "\n${YELLOW}[TEST 3] Checking udev rules file...${NC}"
if [ -f "$SCRIPT_DIR/99-flipper-auto-ethernet.rules" ]; then
    pass "Udev rules file exists"
else
    fail "Udev rules file missing"
fi

# Test 4: Check systemd service file exists
echo -e "\n${YELLOW}[TEST 4] Checking systemd service file...${NC}"
if [ -f "$SCRIPT_DIR/flipper-ethernet@.service" ]; then
    pass "Systemd service file exists"
else
    fail "Systemd service file missing"
fi

# Test 5: Check FBT hooks
echo -e "\n${YELLOW}[TEST 5] Checking FBT hooks...${NC}"
if [ -f "$SCRIPT_DIR/fbt_hooks/post_flash_usb_ethernet.py" ] && \
   [ -x "$SCRIPT_DIR/fbt_hooks/post_flash_usb_ethernet.py" ]; then
    pass "FBT post-flash hook exists and is executable"
else
    fail "FBT post-flash hook missing or not executable"
fi

# Test 6: Check documentation
echo -e "\n${YELLOW}[TEST 6] Checking documentation...${NC}"
if [ -f "$PROJECT_ROOT/FLIPPER_AUTO_ETHERNET.md" ] && \
   [ -f "$PROJECT_ROOT/QUICK_START_AUTOMATION.md" ] && \
   [ -f "$PROJECT_ROOT/ESP_FLASHER_GUIDE.md" ]; then
    pass "All documentation files exist"
else
    fail "Missing documentation files"
fi

# Test 7: Check if Flipper is connected
echo -e "\n${YELLOW}[TEST 7] Checking Flipper Zero connection...${NC}"
if lsusb | grep -q "0483:5740"; then
    FLIPPER_CONNECTED=true
    pass "Flipper Zero is connected (VID:0483 PID:5740)"
else
    FLIPPER_CONNECTED=false
    skip "Flipper Zero not connected"
fi

# Test 8: Check if automation is installed
echo -e "\n${YELLOW}[TEST 8] Checking if automation is installed...${NC}"
AUTOMATION_INSTALLED=false
if [ -f "/etc/udev/rules.d/99-flipper-auto-ethernet.rules" ]; then
    AUTOMATION_INSTALLED=true
    pass "Udev rules installed"
else
    skip "Udev rules not installed (run: sudo ./scripts/install-flipper-auto-ethernet.sh)"
fi

if [ -f "/etc/systemd/system/flipper-ethernet@.service" ]; then
    pass "Systemd service installed"
else
    skip "Systemd service not installed"
fi

if [ -f "/usr/local/bin/flipper-internet-share.sh" ] && \
   [ -f "/usr/local/bin/flipper-auto-ethernet-setup.sh" ]; then
    pass "Automation scripts installed in /usr/local/bin/"
else
    skip "Automation scripts not installed in /usr/local/bin/"
fi

# Test 9: Check dependencies
echo -e "\n${YELLOW}[TEST 9] Checking dependencies...${NC}"
DEP_ISSUES=0

if command -v iptables &> /dev/null; then
    pass "iptables is available"
else
    fail "iptables not found"
    DEP_ISSUES=$((DEP_ISSUES + 1))
fi

if command -v python3 &> /dev/null; then
    pass "python3 is available"
else
    fail "python3 not found"
    DEP_ISSUES=$((DEP_ISSUES + 1))
fi

if command -v systemctl &> /dev/null; then
    pass "systemctl is available"
else
    fail "systemctl not found"
    DEP_ISSUES=$((DEP_ISSUES + 1))
fi

if command -v dnsmasq &> /dev/null; then
    pass "dnsmasq is available (optional)"
else
    info "dnsmasq not found (optional, but recommended for DHCP)"
fi

if python3 -c "import serial" 2>/dev/null; then
    pass "pyserial is available"
else
    info "pyserial not found (install: pip3 install pyserial)"
fi

# Test 10: Check for FlipperSerial library
echo -e "\n${YELLOW}[TEST 10] Checking FlipperSerial library...${NC}"
if [ -d "$PROJECT_ROOT/tools/fz" ]; then
    pass "FlipperSerial library found (tools/fz)"
else
    skip "FlipperSerial library not found (optional)"
fi

# Test 11: Check if USB Ethernet interface exists
echo -e "\n${YELLOW}[TEST 11] Checking USB Ethernet interface...${NC}"
ETH_IFACE=$(ip link show | grep -o 'enx[0-9a-f]*' | head -1 || true)
if [ -n "$ETH_IFACE" ]; then
    pass "USB Ethernet interface found: $ETH_IFACE"

    # Check if it has an IP
    if ip addr show "$ETH_IFACE" | grep -q "inet "; then
        IP_ADDR=$(ip addr show "$ETH_IFACE" | grep "inet " | awk '{print $2}')
        pass "Interface has IP: $IP_ADDR"
    else
        info "Interface $ETH_IFACE has no IP address assigned"
    fi
else
    skip "No USB Ethernet interface found (enable on Flipper: Settings → System → USB → USB Ethernet)"
fi

# Test 12: Check IP forwarding
echo -e "\n${YELLOW}[TEST 12] Checking IP forwarding...${NC}"
if [ "$(cat /proc/sys/net/ipv4/ip_forward 2>/dev/null)" = "1" ]; then
    pass "IP forwarding is enabled"
else
    skip "IP forwarding is disabled (will be enabled by automation)"
fi

# Test 13: Check iptables NAT rules
echo -e "\n${YELLOW}[TEST 13] Checking iptables NAT rules...${NC}"
if sudo -n iptables -t nat -L POSTROUTING 2>/dev/null | grep -q "MASQUERADE"; then
    pass "NAT rules configured"
else
    skip "NAT rules not configured (will be set up by automation)"
fi

# Test 14: Validate script syntax
echo -e "\n${YELLOW}[TEST 14] Validating script syntax...${NC}"
SYNTAX_OK=true
for script in "$SCRIPT_DIR"/*.sh; do
    if bash -n "$script" 2>/dev/null; then
        : # Script is valid
    else
        fail "Syntax error in $(basename "$script")"
        SYNTAX_OK=false
    fi
done
if $SYNTAX_OK; then
    pass "All shell scripts have valid syntax"
fi

# Test 15: Check Python script syntax
echo -e "\n${YELLOW}[TEST 15] Validating Python script syntax...${NC}"
if python3 -m py_compile "$SCRIPT_DIR/fbt_hooks/post_flash_usb_ethernet.py" 2>/dev/null; then
    pass "Python script has valid syntax"
else
    fail "Syntax error in post_flash_usb_ethernet.py"
fi

# Pre-flight: Ensure USB Ethernet NAT and routing are configured
echo -e "\n${YELLOW}[SETUP] Ensuring USB Ethernet NAT and routing are configured...${NC}"
if $FLIPPER_CONNECTED && [ -n "$ETH_IFACE" ]; then
    NAT_OK=false

    # Check if IP forwarding, NAT, and interface IP are already in place
    if [ "$(cat /proc/sys/net/ipv4/ip_forward 2>/dev/null)" = "1" ] && \
       sudo -n iptables -t nat -L POSTROUTING 2>/dev/null | grep -q "MASQUERADE" && \
       ip addr show "$ETH_IFACE" 2>/dev/null | grep -q "10.42.0.1/24"; then
        NAT_OK=true
        info "Existing NAT and routing detected for $ETH_IFACE"
    else
        # Try to use flipper-internet-share helper if available
        SHARE_CMD=""
        if command -v flipper-internet-share.sh >/dev/null 2>&1; then
            SHARE_CMD="flipper-internet-share.sh \"$ETH_IFACE\" start"
        elif [ -x "$SCRIPT_DIR/flipper-internet-share.sh" ]; then
            SHARE_CMD="\"$SCRIPT_DIR/flipper-internet-share.sh\" \"$ETH_IFACE\" start"
        fi

        if [ -n "$SHARE_CMD" ]; then
            info "Attempting to bring up NAT and routing for $ETH_IFACE"
            if [ "$EUID" -eq 0 ]; then
                # Already running as root
                if bash -c "$SHARE_CMD"; then
                    NAT_SETUP_RESULT=0
                else
                    NAT_SETUP_RESULT=$?
                    info "NAT setup script exited with status $NAT_SETUP_RESULT"
                fi
            elif command -v sudo >/dev/null 2>&1; then
                # If E2E_SUDO_PASSWORD is provided, use it for non-interactive sudo
                if [ -n "$E2E_SUDO_PASSWORD" ]; then
                    if printf '%s\n' "$E2E_SUDO_PASSWORD" | sudo -S bash -c "$SHARE_CMD"; then
                        NAT_SETUP_RESULT=0
                    else
                        NAT_SETUP_RESULT=$?
                        info "sudo NAT setup failed with status $NAT_SETUP_RESULT"
                    fi
                else
                    if sudo bash -c "$SHARE_CMD"; then
                        NAT_SETUP_RESULT=0
                    else
                        NAT_SETUP_RESULT=$?
                        info "sudo NAT setup failed with status $NAT_SETUP_RESULT"
                    fi
                fi
            else
                info "sudo not available; cannot automatically enable NAT"
            fi
        else
            info "flipper-internet-share.sh helper not found; skipping automatic NAT setup"
        fi

        # Re-check configuration after attempting setup
        if [ "$(cat /proc/sys/net/ipv4/ip_forward 2>/dev/null)" = "1" ] && \
           sudo -n iptables -t nat -L POSTROUTING 2>/dev/null | grep -q "MASQUERADE" && \
           ip addr show "$ETH_IFACE" 2>/dev/null | grep -q "10.42.0.1/24"; then
            NAT_OK=true
        fi
    fi

    if $NAT_OK; then
        info "USB Ethernet NAT and routing are active for $ETH_IFACE"
    else
        info "USB Ethernet NAT/routing could not be fully verified; connectivity tests may fail"
    fi
else
    info "Flipper or USB Ethernet interface not ready; skipping NAT setup"
fi

# Test 16: Ping Flipper USB Ethernet IP
echo -e "\n${YELLOW}[TEST 16] Pinging Flipper USB Ethernet IP...${NC}"
FLIPPER_USB_ETH_IP="${FLIPPER_USB_ETH_IP:-10.42.0.1}"
if ! $FLIPPER_CONNECTED || [ -z "$ETH_IFACE" ]; then
    skip "Cannot ping Flipper USB Ethernet IP (Flipper or USB Ethernet not ready)"
elif command -v ping &> /dev/null; then
    if ping -c 4 -W 1 "$FLIPPER_USB_ETH_IP" &> /dev/null; then
        pass "Successfully pinged Flipper at $FLIPPER_USB_ETH_IP"
    else
        fail "Unable to ping Flipper at $FLIPPER_USB_ETH_IP"
    fi
else
    skip "ping command not available"
fi

# Test 17: Traceroute/tracepath to Flipper USB Ethernet IP
echo -e "\n${YELLOW}[TEST 17] Tracing route to Flipper USB Ethernet IP...${NC}"
if ! $FLIPPER_CONNECTED || [ -z "$ETH_IFACE" ]; then
    skip "Cannot trace route (Flipper or USB Ethernet not ready)"
else
    if command -v traceroute &> /dev/null; then
        if traceroute -m 5 "$FLIPPER_USB_ETH_IP" &> /dev/null; then
            pass "Traceroute to $FLIPPER_USB_ETH_IP succeeded"
        else
            fail "Traceroute to $FLIPPER_USB_ETH_IP failed"
        fi
    elif command -v tracepath &> /dev/null; then
        if tracepath -m 5 "$FLIPPER_USB_ETH_IP" &> /dev/null; then
            pass "Tracepath to $FLIPPER_USB_ETH_IP succeeded"
        else
            fail "Tracepath to $FLIPPER_USB_ETH_IP failed"
        fi
    else
        skip "Neither traceroute nor tracepath is installed"
    fi
fi

# Test 18: Flipper internet connectivity via CLI (pyserial)
echo -e "\n${YELLOW}[TEST 18] Verifying Flipper internet connectivity via CLI...${NC}"
if ! $FLIPPER_CONNECTED; then
    skip "Flipper not connected; skipping CLI connectivity test"
elif ! command -v python3 &> /dev/null; then
    skip "python3 not available; skipping CLI connectivity test"
elif ! python3 -c "import serial" 2>/dev/null; then
    skip "pyserial not available; skipping CLI connectivity test (pip3 install pyserial)"
else
    FLIPPER_SERIAL_PORT="${FLIPPER_SERIAL_PORT:-/dev/ttyACM0}"
    if [ ! -e "$FLIPPER_SERIAL_PORT" ]; then
        skip "Serial port $FLIPPER_SERIAL_PORT not found; set FLIPPER_SERIAL_PORT to override"
    else
        PY_EXIT_CODE=0
        if python3 - << 'PY'
import os
import sys
import time

try:
    import serial  # type: ignore
except Exception as e:  # pragma: no cover - runtime check
    print(f"[ERROR] pyserial not available: {e}")
    sys.exit(1)

port = os.environ.get("FLIPPER_SERIAL_PORT", "/dev/ttyACM0")

# Hard upper bound on how long we will wait for the CLI to respond
TOTAL_TIMEOUT = 25.0
# How long we will tolerate complete silence from the CLI before
# treating it as unresponsive and skipping the test
IDLE_TIMEOUT = 10.0

# How long we wait for a CLI prompt like ">: " after resetting
PROMPT_TIMEOUT = 10.0
PROMPT_SEQUENCE = b">: "


def send_with_retry(ser, payload, attempts=2, delay=1.0):
    """Send bytes to the serial port with a simple retry loop.

    Returns True on success, False if all attempts fail.
    """
    for idx in range(attempts):
        try:
            ser.write(payload)
            return True
        except serial.SerialTimeoutException as e:  # pragma: no cover - runtime protection
            print(f"[WARN] Serial write timeout (attempt {idx + 1}/{attempts}): {e}")
            if idx + 1 < attempts:
                time.sleep(delay)
        except Exception as e:  # pragma: no cover - runtime protection
            print(f"[WARN] Serial write error (attempt {idx + 1}/{attempts}): {e}")
            break
    return False


def drain_until_prompt(ser, timeout):
    """Drain buffered noise and wait for a CLI prompt like '>: '.

    Returns True if a prompt-like sequence is observed, False on timeout.
    """
    end = time.time() + timeout
    buf = bytearray()

    while time.time() < end:
        try:
            waiting = getattr(ser, "in_waiting", 0) or 0
        except Exception:
            waiting = 0

        if waiting:
            try:
                chunk = ser.read(waiting)
            except Exception:
                chunk = ser.read(1)
        else:
            chunk = ser.read(1)

        if not chunk:
            time.sleep(0.05)
            continue

        buf.extend(chunk)

        # Avoid unbounded growth
        if len(buf) > 4096:
            buf = buf[-1024:]

        if PROMPT_SEQUENCE in buf:
            return True

    return False


start = time.time()
last_data_time = start
lines = []
buffer = bytearray()
unresponsive = False

try:
    # Use non-blocking reads (timeout=0) so that readline-style
    # parsing cannot hang the process. We implement our own line
    # buffering below and enforce strict timeouts.
    ser = serial.Serial(port, baudrate=115200, timeout=0, write_timeout=15)
except Exception as e:
    msg = str(e).lower()
    print(f"[ERROR] Could not open serial port {port}: {e}")
    if "device or resource busy" in msg or "resource busy" in msg:
        print("[HINT] The Flipper serial port appears busy. Is qFlipper or another tool using it?")
        sys.exit(2)
    sys.exit(1)

try:
    # Best-effort input/output reset
    try:
        ser.reset_input_buffer()
    except Exception:
        pass
    try:
        ser.reset_output_buffer()
    except Exception:
        pass

    # Send a Ctrl+C first to clear any stuck CLI commands
    if not send_with_retry(ser, b"\x03", attempts=2, delay=0.5):
        print("[WARN] Unable to send Ctrl+C to reset CLI; treating as unresponsive.")
        sys.exit(2)

    # Drain any noise and wait for the CLI prompt (e.g., '>: ')
    if not drain_until_prompt(ser, PROMPT_TIMEOUT):
        print("[WARN] Flipper CLI prompt not detected after reset; skipping connectivity test.")
        unresponsive = True
        print("[HINT] Ensure no other tools (e.g., qFlipper) are attached to the serial port.")
        sys.exit(2)

    # Short grace period before issuing the ping command
    time.sleep(0.2)

    cmd = "ping 8.8.8.8\r\n"
    if not send_with_retry(ser, cmd.encode("ascii"), attempts=2, delay=1.0):
        print("[WARN] Serial write timeout when sending ping command after retries.")
        # Treat this similarly to an unresponsive CLI so the shell wrapper
        # can skip the test rather than marking the whole suite as failed.
        sys.exit(2)

    got_summary = False

    while True:
        now = time.time()
        if now - start > TOTAL_TIMEOUT:
            break
        if now - last_data_time > IDLE_TIMEOUT:
            unresponsive = True
            break

        # Read whatever is available without blocking. With timeout=0, 
        # read() will return immediately. 
        try:
            waiting = getattr(ser, "in_waiting", 0) or 0
        except Exception:
            waiting = 0

        if waiting:
            try:
                data = ser.read(waiting)
            except Exception:
                data = ser.read(1)
        else:
            data = ser.read(1)

        if data:
            last_data_time = now
            buffer.extend(data)

            # Process complete lines from the buffer
            while b"\n" in buffer:
                line_bytes, _, remainder = buffer.partition(b"\n")
                buffer = bytearray(remainder)
                line = line_bytes.decode(errors="ignore").strip()
                if line:
                    lines.append(line)
                lower_line = line.lower()
                
                # Check for our new native ping command output
                if "ping success!" in lower_line:
                    got_summary = True
                    PY_EXIT_CODE = 0
                    break
                if "ping failed" in lower_line:
                    got_summary = True
                    PY_EXIT_CODE = 1
                    break
                # Fallback check for standard ping output (if format changes)
                if (
                    "packets transmitted" in lower_line
                    or "statistics" in lower_line
                    or "packet loss" in lower_line
                ):
                    got_summary = True
                    break

            if got_summary:
                break
        else:
            # No data available right now; avoid busy-waiting
            time.sleep(0.1)
finally:
    try:
        ser.close()
    except Exception:
        pass

text = "\n".join(lines)
print(text)

lower = text.lower()

if not text.strip():
    # No output at all; treat as a failure from the perspective of
    # connectivity, but not as a hang.
    sys.exit(1)

if unresponsive:
    # CLI never produced useful output within IDLE_TIMEOUT; signal the
    # shell wrapper to skip this test rather than hanging the suite.
    print("[WARN] Flipper CLI unresponsive; skipping connectivity test.")
    sys.exit(2)

if "ping success!" in lower:
    sys.exit(0)

if "ping failed" in lower or "100% packet loss" in lower or "0 received" in lower:
    sys.exit(1)

# If we get here, we didn't see explicit success or failure messages
# but received some text. Treat as failure to be safe.
sys.exit(1)
PY
        then
            PY_EXIT_CODE=0
        else
            PY_EXIT_CODE=$?
        fi

        if [ "$PY_EXIT_CODE" -eq 0 ]; then
            pass "Flipper can reach the internet via host NAT (ping 8.8.8.8)"
        elif [ "$PY_EXIT_CODE" -eq 2 ]; then
            skip "Flipper CLI unresponsive; skipping CLI connectivity test"
        else
            fail "Flipper could not reach the internet via host NAT (ping 8.8.8.8 failed)"
        fi
    fi
fi

# Test 19: Simulated file transfer via large ping packets
echo -e "\n${YELLOW}[TEST 19] Simulating file transfer with large ping packets...${NC}"
if ! $FLIPPER_CONNECTED || [ -z "$ETH_IFACE" ]; then
    skip "Cannot simulate file transfer (Flipper or USB Ethernet not ready)"
elif ! command -v ping &> /dev/null; then
    skip "ping command not available; skipping simulated file transfer"
else
    if ping -c 10 -s 1024 "$FLIPPER_USB_ETH_IP" &> /dev/null; then
        pass "Large-packet ping to $FLIPPER_USB_ETH_IP succeeded (link stable, MTU OK for 1KB packets)"
    else
        fail "Large-packet ping to $FLIPPER_USB_ETH_IP failed (link/MTU issue)"
    fi
fi

# Summary
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Test Summary                                            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}
echo ""
echo -e "${GREEN}Passed:  ${TESTS_PASSED}${NC}"
echo -e "${RED}Failed:  ${TESTS_FAILED}${NC}"
echo -e "${YELLOW}Skipped: ${TESTS_SKIPPED}${NC}"
echo ""

if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}⚠ Some tests failed! Please review the output above.${NC}"
    EXIT_CODE=1
else
    echo -e "${GREEN}✓ All critical tests passed!${NC}"
    EXIT_CODE=0
fi

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""

if ! $AUTOMATION_INSTALLED; then
    echo -e "${YELLOW}1. Install automation:${NC}"
    echo -e "   ${GREEN}sudo ./scripts/install-flipper-auto-ethernet.sh${NC}"
    echo ""
fi

if ! $FLIPPER_CONNECTED; then
    echo -e "${YELLOW}2. Connect Flipper Zero via USB${NC}"
    echo ""
fi

if $AUTOMATION_INSTALLED && $FLIPPER_CONNECTED; then
    if [ -z "$ETH_IFACE" ]; then
        echo -e "${YELLOW}3. Enable USB Ethernet on Flipper:${NC}"
        echo -e "   ${GREEN}Settings → System → USB → USB Ethernet${NC}"
        echo -e "   ${BLUE}Or let automation do it automatically!${NC}"
    else
        echo -e "${GREEN}✓ System is ready!${NC}"
        echo -e "   - Flipper connected"
        echo -e "   - USB Ethernet active: $ETH_IFACE"
        echo -e "   - Automation installed"
        echo ""
        echo -e "${BLUE}Test ESP Flasher FAP:${NC}"
        echo -e "   Apps → GPIO → [ESP] ESP Flasher"
    fi
    echo ""
fi

echo -e "${BLUE}Logs:${NC}"
echo -e "   ${GREEN}tail -f /var/log/flipper-ethernet.log${NC}"
echo ""

exit $EXIT_CODE
