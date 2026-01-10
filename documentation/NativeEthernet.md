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