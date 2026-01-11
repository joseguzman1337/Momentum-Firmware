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
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
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
    info "pyserial not found (optional, install: pip3 install pyserial)"
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

# Summary
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Test Summary                                            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
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
