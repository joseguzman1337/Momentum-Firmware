#!/bin/bash
set -e

# Configuration
INTERFACE_WAN=$(ip route | grep default | awk '{print $5}' | head -n 1)
INTERFACE_USB="enx*" # Adjust if needed, often enx... or usb0

echo "[*] Detected WAN interface: $INTERFACE_WAN"
echo "[*] Setting up NAT for Flipper Zero..."

# Enable IP forwarding
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward > /dev/null

# Clear existing rules (optional, be careful)
# sudo iptables -F
# sudo iptables -t nat -F

# Set up NAT
sudo iptables -t nat -A POSTROUTING -o $INTERFACE_WAN -j MASQUERADE
sudo iptables -A FORWARD -i $INTERFACE_WAN -o $INTERFACE_USB -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i $INTERFACE_USB -o $INTERFACE_WAN -j ACCEPT

echo "[+] NAT enabled."
echo "[*] Assigning IP to USB interface (if not already done via NetworkManager)..."
# This part depends on the OS. On many systems NetworkManager handles it.
# If manual:
# sudo ip addr add 192.168.2.1/24 dev $INTERFACE_USB
# sudo ip link set $INTERFACE_USB up

echo "[+] Internet Connection Sharing setup complete."
