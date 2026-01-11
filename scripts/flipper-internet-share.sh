#!/bin/bash
# Flipper Zero Auto Internet Sharing Script
# Automatically enables NAT and internet sharing when Flipper USB Ethernet is detected

set -e

FLIPPER_IFACE="$1"
ACTION="${2:-start}"
LOG_FILE="/var/log/flipper-ethernet.log"
STATE_FILE="/var/run/flipper-ethernet-${FLIPPER_IFACE}.state"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

get_wan_interface() {
    # Try to find active internet connection
    ip route get 8.8.8.8 2>/dev/null | grep -Po '(?<=dev\s)\w+' | head -1
}

setup_nat() {
    local WAN_IFACE="$1"
    local LAN_IFACE="$2"

    log "Setting up NAT: $WAN_IFACE -> $LAN_IFACE"

    # Enable IP forwarding
    echo 1 > /proc/sys/net/ipv4/ip_forward

    # Configure Flipper interface
    ip addr add 10.42.0.1/24 dev "$LAN_IFACE" 2>/dev/null || true
    ip link set "$LAN_IFACE" up

    # Setup NAT (iptables)
    iptables -t nat -A POSTROUTING -o "$WAN_IFACE" -j MASQUERADE
    iptables -A FORWARD -i "$LAN_IFACE" -o "$WAN_IFACE" -j ACCEPT
    iptables -A FORWARD -i "$WAN_IFACE" -o "$LAN_IFACE" -m state --state RELATED,ESTABLISHED -j ACCEPT

    # Setup DNS forwarding (dnsmasq if available)
    if command -v dnsmasq &> /dev/null; then
        dnsmasq --interface="$LAN_IFACE" --bind-interfaces \
                --dhcp-range=10.42.0.10,10.42.0.50,12h \
                --dhcp-option=option:router,10.42.0.1 \
                --dhcp-option=option:dns-server,8.8.8.8,8.8.4.4 \
                --pid-file="/var/run/dnsmasq-flipper-${LAN_IFACE}.pid" \
                2>/dev/null || log "dnsmasq failed, Flipper will need manual IP config"
    fi

    log "NAT enabled for $LAN_IFACE via $WAN_IFACE"
    echo "$WAN_IFACE" > "$STATE_FILE"
}

teardown_nat() {
    local LAN_IFACE="$1"

    if [ ! -f "$STATE_FILE" ]; then
        log "No state file found for $LAN_IFACE"
        return 0
    fi

    local WAN_IFACE=$(cat "$STATE_FILE")

    log "Tearing down NAT: $WAN_IFACE -> $LAN_IFACE"

    # Stop dnsmasq if running
    if [ -f "/var/run/dnsmasq-flipper-${LAN_IFACE}.pid" ]; then
        kill $(cat "/var/run/dnsmasq-flipper-${LAN_IFACE}.pid") 2>/dev/null || true
        rm -f "/var/run/dnsmasq-flipper-${LAN_IFACE}.pid"
    fi

    # Remove iptables rules
    iptables -t nat -D POSTROUTING -o "$WAN_IFACE" -j MASQUERADE 2>/dev/null || true
    iptables -D FORWARD -i "$LAN_IFACE" -o "$WAN_IFACE" -j ACCEPT 2>/dev/null || true
    iptables -D FORWARD -i "$WAN_IFACE" -o "$LAN_IFACE" -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || true

    # Remove IP address
    ip addr del 10.42.0.1/24 dev "$LAN_IFACE" 2>/dev/null || true

    rm -f "$STATE_FILE"
    log "NAT disabled for $LAN_IFACE"
}

case "$ACTION" in
    start)
        if [ -z "$FLIPPER_IFACE" ]; then
            log "ERROR: No interface specified"
            exit 1
        fi

        log "Flipper USB Ethernet detected: $FLIPPER_IFACE"

        # Wait for interface to be ready
        sleep 2

        WAN_IFACE=$(get_wan_interface)
        if [ -z "$WAN_IFACE" ]; then
            log "ERROR: Could not detect WAN interface"
            exit 1
        fi

        setup_nat "$WAN_IFACE" "$FLIPPER_IFACE"
        ;;

    stop)
        if [ -z "$FLIPPER_IFACE" ]; then
            log "ERROR: No interface specified"
            exit 1
        fi

        log "Flipper USB Ethernet disconnected: $FLIPPER_IFACE"
        teardown_nat "$FLIPPER_IFACE"
        ;;

    status)
        if [ -f "$STATE_FILE" ]; then
            WAN_IFACE=$(cat "$STATE_FILE")
            log "Active: $FLIPPER_IFACE via $WAN_IFACE"
            ip addr show "$FLIPPER_IFACE" 2>/dev/null || true
        else
            log "Not active"
        fi
        ;;

    *)
        echo "Usage: $0 <interface> {start|stop|status}"
        exit 1
        ;;
esac

exit 0
