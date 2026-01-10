# Technical Feasibility and Implementation Strategy: Native USB Ethernet and Automated Internet Connection Sharing for Flipper Zero

## 1. Introduction to Native Ethernet on Embedded Frameworks

The Flipper Zero architecture has been modified to support native USB Ethernet functionality, creating a standardized network interface directly over the USB-C port. This implementation utilizes the CDC-ECM (Ethernet Control Model) protocol, ensuring compatibility with modern operating systems like macOS, Linux, and Windows (via drivers). This document outlines the engineering implementation, firmware modifications, and system behavior.

## 2. Implementation Technical Details

### 2.1 Protocol Selection: CDC-ECM vs. RNDIS

While RNDIS is the standard for Windows, CDC-ECM was chosen for its broad compatibility with UNIX-like systems and its status as a USB-IF standard.

- **CDC-ECM (Ethernet Control Model)**: Selected as the primary protocol.
- **Descriptors**: Custom USB descriptors were implemented in `furi_hal_usb_eth.c` to define the MAC address, interface associations, and endpoints.

### 2.2 USB Product ID (PID) Strategy

To ensure the host operating system correctly identifies the new functionality and loads the appropriate drivers, the USB Product ID was strategically managed:

- **Standard PID**: `0x5740` (Default Flipper Zero PID).
- **Modified PID**: `0x5741` was adopted for the Ethernet configuration. This slight modification prevents the host OS (specifically macOS) from caching previous driver associations (e.g., purely CDC-ACM or HID) and forces a fresh enumeration of the device as a new USB Ethernet adapter.

### 2.3 Firmware Integration

The implementation required deep integration into the Furi HAL (Hardware Abstraction Layer) and the TinyUSB stack.

#### **Key File Modifications:**

1.  **`targets/f7/furi_hal/furi_hal_usb_eth.c`**:
    *   **Descriptor Definition**: Defined `eth_device_desc` with `idProduct = 0x5741`.
    *   **MAC Address**: Implemented `eth_mac_desc` string descriptor.
    *   **CDC-ECM Structure**: Corrected struct entries (e.g., `bLength` vs `bFunctionLength`) to align with the TinyUSB stack requirements.
    *   **Endpoint Management**: Configured Notification and Data endpoints for network traffic.

2.  **`targets/f7/furi_hal/furi_hal_usb.c`**:
    *   **Default Interface**: Modified `furi_hal_usb_init` to set the default interface pointer `usb.interface` to `&usb_eth`. This ensures Ethernet mode is active immediately upon boot, overriding the previous Serial/CDC default.
    *   **Debug Facilities**: Integrated LED feedback (Red for Ethernet, Green for others) during the development phase to visually verify mode switching.

3.  **`applications/services/cli/cli_vcp.c`**:
    *   **Mode Switching Logic**: Updated the CLI initialization sequence. Instead of defaulting to `usb_cdc`, the system now requests the `usb_eth` configuration.
    *   **USB Enforce**: Added calls to `furi_hal_usb_enable()` after configuration changes to ensure the hardware is properly reset and ready for enumeration.

### 3. Comparison with Previous Methods

| Feature | Legacy CDC/Serial | New Native Ethernet |
| :--- | :--- | :--- |
| **Protocol** | CDC-ACM (Virtual Serial) | CDC-ECM (Ethernet) |
| **Host View** | COM Port / TTY | Network Adapter (enx/eth0) |
| **Throughput** | Limited (~1 Mbps) | Higher (Full Speed USB 12 Mbps) |
| **IP Stack** | None (Raw Stream) | LwIP (TCP/IP, DHCP, UDP) |
| **Use Case** | CLI, Logging | Networking, Web Server, Proxies |

### 4. System Behavior and Verification

Upon connecting the Flipper Zero to a host:
1.  **Enumeration**: The device presents itself with VIP `0x0483` and PID `0x5741`.
2.  **Driver Loading**: macOS/Linux loads `cdc_ether` or `AppleUSBNetworking`. Windows may require an INF driver or RNDIS compatibility shim.
3.  **Network Interface**: A new network interface (e.g., `enx...`) appears on the host.
4.  **IP Assignment**: The internal LwIP stack runs a DHCP client/server or uses static IP configuration to establish connectivity.

### 5. Future Considerations

- **Composite Support**: Future iterations may re-integrate HID support alongside CDC-ECM to allow "BadUSB" style script injection for automated Internet Connection Sharing setup.
- **Windows RNDIS Fallback**: Implementing an automatic switch to RNDIS detection for better out-of-box Windows support without manual driver installation.

### 6. Current Status and Practical Usage

#### 6.1 Implementation Status

The current Momentum Firmware tree already includes a working native USB Ethernet implementation:

- `targets/f7/furi_hal/furi_hal_usb_eth.c`
  - Implements a CDC-ECM USB device with:
    - Vendor ID `0x0483`.
    - Product ID `0x5741` (distinct from the stock `0x5740` so the host treats it as a new network adapter).
  - Defines communication and data interfaces and endpoints for Ethernet traffic.
  - Integrates with lwIP:
    - Initializes the TCP/IP stack (`tcpip_init`).
    - Creates and registers `eth_netif` with name `"ue"`, MTU 1500, and flags `NETIF_FLAG_BROADCAST | NETIF_FLAG_ETHARP | NETIF_FLAG_LINK_UP`.
    - Sets `linkoutput` to `eth_low_level_output`, which writes Ethernet frames via `usbd_ep_write` on the TX bulk endpoint.
    - Starts DHCP on this interface with `dhcp_start(&eth_netif)`.
  - Handles RX via `eth_rx_callback`, which reads from the RX bulk endpoint, wraps data in a `pbuf`, and forwards it to `eth_netif.input` (ultimately `tcpip_input`).

- `targets/furi_hal_include/furi_hal_usb_eth.h`
  - Declares `extern FuriHalUsbInterface usb_eth;`, exposing the Ethernet USB interface to the rest of the firmware.

- `targets/f7/furi_hal/furi_hal_usb.c`
  - In `furi_hal_usb_init`, USB is brought up and the **default** interface is set to Ethernet:
    - `usb.enabled = false;`
    - `usb.interface = &usb_eth;`
  - As a result, on boot the Flipper enumerates as a USB Ethernet device unless another component overrides the configuration.

- `applications/services/cli/cli_vcp.c`
  - The CLI VCP service explicitly switches to Ethernet when enabled:
    - Logs a marker when enabling (e.g., `ENABLING USB ETHERNET`).
    - Saves the previous USB interface with `furi_hal_usb_get_config()`.
    - Unlocks USB mode, calls `furi_hal_usb_set_config(&usb_eth, NULL)` and `furi_hal_usb_enable()`, then locks again to enforce the new mode.
    - Disabling restores the previous interface.

In summary, native USB Ethernet over USB-C is wired in at the HAL level and is the default USB mode for this firmware build.

#### 6.2 What "Auto-Connect to Internet" Means

On-device behavior (Flipper side):

- Selects `usb_eth` as the active USB interface.
- Initializes lwIP and brings up the Ethernet netif.
- Immediately starts DHCP on that interface.

Once the host provides a functional network on the USB Ethernet link (for example, through Internet Connection Sharing or a bridge), the Flipper will automatically request and obtain an IP address. No additional on-device configuration is required for basic connectivity.

However, the Flipper is always a **USB device**, not a USB host, so it cannot independently create or backhaul its own internet connection. The host computer must:

- Recognize and configure the Flipper's USB Ethernet adapter.
- Attach this adapter to an upstream internet connection (Wi‑Fi, Ethernet, etc.).
- Provide IP configuration (typically via DHCP) and route/NAT packets to the wider network.

In practice, "auto-connect Flipper to internet over USB‑C" therefore has two sides:

1. **Device side (Flipper)** – already implemented:
   - Enumerate as a CDC‑ECM USB Ethernet device.
   - Run DHCP over that link.
2. **Host side (PC/Mac/Linux/Windows)** – requires per-OS automation:
   - Enable Internet Connection Sharing (ICS) or bridging from the primary network interface to the Flipper USB NIC.
   - Optionally script that behavior using platform-specific tooling (shell scripts, PowerShell, `networksetup`, `nmcli`, etc.) or BadUSB payloads.

#### 6.3 How to Use Native Ethernet Today

With the current Momentum Firmware build:

1. Build and flash this firmware to the Flipper Zero.
2. Connect the Flipper to a host via USB‑C.
3. On the host, verify that a new USB network interface appears, identified as:
   - VID `0x0483`, PID `0x5741`, CDC‑ECM class.
4. Configure the host to share or bridge internet to that interface:
   - **Windows**: Enable Internet Connection Sharing on the primary adapter, selecting the Flipper USB adapter as the shared interface.
   - **macOS**: Enable Internet Sharing from Wi‑Fi or Ethernet to the Flipper USB Ethernet adapter.
   - **Linux**: Bridge or NAT from the main interface to the Flipper interface using tools such as `nmcli`, `ip`, and `iptables`/`nftables`, and provide DHCP (for example via `dnsmasq`).

Once ICS or bridging is active, `dhcp_start(&eth_netif)` on the Flipper will obtain an IP address, and the device will be reachable over IP.

#### 6.4 Next-Step Integration Options

Given the working USB Ethernet and lwIP stack, there are two main directions for further automation:

1. **Host-side zero-click automation**
   - Implement OS-specific scripts or BadUSB payloads that:
     - Detect the Flipper USB NIC.
     - Automatically enable ICS or configure a bridge from the host's primary network interface to the Flipper adapter.
   - This corresponds to the automation concepts originally described in `ethernet.md`.

2. **On-device HTTP download service over Ethernet**
   - Implement a small firmware service (not a FAP) on top of lwIP that can:
     - Perform HTTP GET requests over `eth_netif`.
     - Save downloaded files to locations such as `apps_data/esp_flasher/...`.
   - Integrate this service with ESP Flasher so it can automatically download, store, and then flash updated firmware (for example, ESP32 Marauder images) whenever the USB Ethernet link is online.


Here’s where you stand right now with “native Ethernet over USB‑C” and “auto‑connect to internet” in ~/x/x/Momentum-Firmware:



1. Native USB Ethernet (CDC‑ECM) is already implemented

You do have a working CDC‑ECM USB Ethernet device implementation in this tree.

Key pieces:

•  targets/f7/furi_hal/furi_hal_usb_eth.c
◦  Defines a CDC‑ECM USB device with:
▪  VID 0x0483
▪  PID 0x5741 (different from the stock 0x5740 so the host sees it as a new device)
◦  Sets up descriptors for:
▪  Communication interface (ECM control)
▪  Data interface (RX/TX bulk endpoints)
◦  Hooks into lwIP:
▪  Initializes TCP/IP stack once (tcpip_init)
▪  Creates a netif eth_netif:
▪  name "ue" (so likely interface name ue0-style if exposed)
▪  mtu = 1500
▪  flags BROADCAST | ETHARP | LINK_UP
▪  linkoutput = eth_low_level_output which sends frames by usbd_ep_write on ETH_RNDIS_TX_EP
▪  Starts DHCP immediately:
▪  netif_add(..., eth_netif_init, tcpip_input)
▪  netif_set_default(&eth_netif);
▪  netif_set_up(&eth_netif);
▪  dhcp_start(&eth_netif);
◦  RX side:
▪  eth_rx_callback reads USB RX endpoint into a buffer, wraps in a pbuf, and passes into eth_netif.input (which is tcpip_input), so inbound packets go into lwIP.
•  targets/furi_hal_include/furi_hal_usb_eth.h
◦  Declares extern FuriHalUsbInterface usb_eth;
◦  So usb_eth is a standard FuriHalUsbInterface that other code can select.
•  targets/f7/furi_hal/furi_hal_usb.c
◦  In furi_hal_usb_init:
▪  USB core is brought up, and default interface is set to Ethernet:
      usb.enabled = false;
      usb.interface = &usb_eth;
c
•  So from power‑up, the Flipper will present itself as the Ethernet USB device unless something else changes the config.
•  applications/services/cli/cli_vcp.c
◦  The CLI VCP service explicitly switches to Ethernet when enabled:
▪  On CliVcpMessageTypeEnable:
▪  Logs: ### ENABLING USB ETHERNET ###
▪  Saves previous_interface = furi_hal_usb_get_config();
▪  Unlocks USB mode, sets config to &usb_eth, calls furi_hal_usb_enable(), then locks again.
◦  Disable restores the previous USB interface.

Conclusion:  
USB‑C native Ethernet is already wired in at the HAL level and is actually the default USB mode in this firmware. When you plug this firmware into a host, it should enumerate as a USB Ethernet adapter (CDC‑ECM) with PID 0x5741. On enumeration, Flipper brings up lwIP and starts DHCP.



2. What “auto‑connect to internet” really means here

On the Flipper side, your code already does:

•  Bring up usb_eth as the active USB interface.
•  Initialize lwIP and an Ethernet netif.
•  Start DHCP automatically.

That means:

•  As soon as the host provides a functional network on that USB Ethernet interface (e.g. via Internet Connection Sharing, bridge, etc.), the Flipper will automatically request and obtain an IP. No extra on‑device steps are needed for that part.

What cannot be done purely on the Flipper:

•  The Flipper is always a USB device, not a USB host.
•  It cannot create its own internet connection without the host:
◦  The host (your PC, Mac, etc.) must:
▪  Recognize the USB Ethernet adapter.
▪  Attach it to some upstream internet connection (Wi‑Fi, Ethernet, etc.).
▪  Hand out an IP (DHCP) and route/NAT traffic.

So in practice, “auto‑connect Flipper to internet over USB‑C” splits into:

1. Device side (Flipper) – already implemented:
◦  Enumerate as USB Ethernet CDC‑ECM.
◦  Start DHCP over that link.
2. Host side (PC/Mac/Linux/Windows) – still needs automation:
◦  Enable ICS/bridge from your real network interface to the Flipper’s USB NIC.
◦  Optionally script this via:
▪  BadUSB keyboard scripts that click through OS dialogs or run commands.
▪  PowerShell / netsh on Windows.
▪  networksetup or pfctl/ipfw/pf on macOS.
▪  nmcli, ip, and iptables/nftables on Linux.

Right now, your code base covers (1) fully, but (2) is still manual unless you add OS‑specific scripts/BadUSB payloads.



3. How to use this right now

With the current firmware in ~/x/x/Momentum-Firmware:

1. Build and flash the firmware to your Flipper.
2. Plug Flipper into a host via USB‑C.
3. On the host you should see a new USB network interface:
◦  VID 0x0483, PID 0x5741, class CDC‑ECM.
4. Configure the host to share internet to that interface:
◦  Windows: enable Internet Connection Sharing on your main network adapter, target the Flipper adapter.
◦  macOS: Internet Sharing from Wi‑Fi/Ethernet to the Flipper adapter.
◦  Linux: bridge or NAT from your main interface to the Flipper one, run a DHCP server or use dnsmasq.

If ICS/bridging is set up, the Flipper’s dhcp_start(&eth_netif) will get an IP and it is “online” from an IP‑layer perspective.



4. Next step options

You now have two main directions for “full automation”:

1. Host‑side “zero‑click” automation (recommended first):
◦  Implement platform‑specific scripts (or BadUSB payloads) that:
▪  Detect the Flipper USB NIC.
▪  Turn on ICS/bridge automatically.
◦  This is exactly what your ethernet.md was describing.
2. On‑device HTTP downloader using this Ethernet link:
◦  Build a small service on top of lwIP (inside firmware, not as a FAP) that:
▪  Does plain HTTP GET over eth_netif.
▪  Saves downloaded files to apps_data/esp_flasher/....
◦  Then adjust ESP Flasher to trigger that service (via a firmware API / record) to auto‑download Marauder before flashing.

Both are feasible; the HAL + lwIP side is already there.
