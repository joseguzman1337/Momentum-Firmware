// Network Detection Module Implementation for Crypto CLI Tools
// Auto-detect ethernet connections and retrieve network information

#include "network_detector.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <furi.h>

#define TAG "NetworkDetector"

// Mock network interfaces for Flipper Zero demonstration
static NetworkInterface mock_interfaces[] = {
    {
        .interface_name = "eth0",
        .mac_address = "02:42:ac:11:00:02",
        .type = NETWORK_TYPE_ETHERNET,
        .status = NETWORK_STATUS_CONNECTED,
        .addresses = {
            .ipv4_address = "192.168.1.100",
            .ipv4_netmask = "255.255.255.0",
            .ipv4_gateway = "192.168.1.1",
            .ipv6_address = "2001:db8::100",
            .ipv6_prefix = "/64",
            .dns_primary = "8.8.8.8",
            .dns_secondary = "8.8.4.4",
            .has_ipv4 = true,
            .has_ipv6 = true,
            .has_dns = true
        },
        .speed_mbps = 1000,
        .signal_strength = 0,
        .bytes_sent = 1048576,
        .bytes_received = 2097152,
        .packets_sent = 1024,
        .packets_received = 2048,
        .is_default_route = true
    },
    {
        .interface_name = "wlan0",
        .mac_address = "aa:bb:cc:dd:ee:ff",
        .type = NETWORK_TYPE_WIFI,
        .status = NETWORK_STATUS_DISCONNECTED,
        .addresses = {
            .has_ipv4 = false,
            .has_ipv6 = false,
            .has_dns = false
        },
        .speed_mbps = 0,
        .signal_strength = -70,
        .bytes_sent = 0,
        .bytes_received = 0,
        .packets_sent = 0,
        .packets_received = 0,
        .is_default_route = false
    },
    {
        .interface_name = "usb0",
        .mac_address = "12:34:56:78:9a:bc",
        .type = NETWORK_TYPE_USB,
        .status = NETWORK_STATUS_CONNECTED,
        .addresses = {
            .ipv4_address = "10.0.0.2",
            .ipv4_netmask = "255.255.255.0",
            .ipv4_gateway = "10.0.0.1",
            .dns_primary = "10.0.0.1",
            .has_ipv4 = true,
            .has_ipv6 = false,
            .has_dns = true
        },
        .speed_mbps = 100,
        .signal_strength = 0,
        .bytes_sent = 524288,
        .bytes_received = 1048576,
        .packets_sent = 512,
        .packets_received = 1024,
        .is_default_route = false
    }
};

static bool is_initialized = false;
static uint32_t last_scan_time = 0;

// --- Public Functions ---

bool network_detector_init(void) {
    FURI_LOG_I(TAG, "Initializing network detector");
    is_initialized = true;
    last_scan_time = 0;
    return true;
}

void network_detector_cleanup(void) {
    FURI_LOG_I(TAG, "Cleaning up network detector");
    is_initialized = false;
}

bool network_detector_scan_interfaces(NetworkDetectionResult* result) {
    if (!is_initialized || !result) {
        FURI_LOG_E(TAG, "Network detector not initialized or invalid result pointer");
        return false;
    }
    
    FURI_LOG_I(TAG, "Scanning network interfaces");
    
    // Clear result structure
    memset(result, 0, sizeof(NetworkDetectionResult));
    
    // Copy mock interfaces for demonstration
    result->interface_count = sizeof(mock_interfaces) / sizeof(mock_interfaces[0]);
    if (result->interface_count > 8) result->interface_count = 8;
    
    for (uint8_t i = 0; i < result->interface_count; i++) {
        memcpy(&result->interfaces[i], &mock_interfaces[i], sizeof(NetworkInterface));
    }
    
    // Set hostname
    strncpy(result->hostname, "flipper-zero", sizeof(result->hostname) - 1);
    result->hostname[sizeof(result->hostname) - 1] = '\0';
    
    // Check internet accessibility
    result->internet_accessible = network_detector_test_connectivity(5000);
    
    // Set timestamp
    result->detection_timestamp = furi_get_tick();
    last_scan_time = result->detection_timestamp;
    
    FURI_LOG_I(TAG, "Found %d network interfaces", result->interface_count);
    return true;
}

bool network_detector_get_interface_info(const char* interface_name, NetworkInterface* interface) {
    if (!is_initialized || !interface_name || !interface) {
        return false;
    }
    
    // Search for interface in mock data
    for (size_t i = 0; i < sizeof(mock_interfaces) / sizeof(mock_interfaces[0]); i++) {
        if (strcmp(mock_interfaces[i].interface_name, interface_name) == 0) {
            memcpy(interface, &mock_interfaces[i], sizeof(NetworkInterface));
            
            // Update statistics with simulated data
            if (interface->status == NETWORK_STATUS_CONNECTED) {
                interface->bytes_sent += (furi_get_tick() / 1000) * 100;  // Simulate traffic
                interface->bytes_received += (furi_get_tick() / 1000) * 200;
                interface->packets_sent += (furi_get_tick() / 1000) / 10;
                interface->packets_received += (furi_get_tick() / 1000) / 5;
            }
            
            FURI_LOG_D(TAG, "Retrieved info for interface %s", interface_name);
            return true;
        }
    }
    
    FURI_LOG_W(TAG, "Interface %s not found", interface_name);
    return false;
}

bool network_detector_get_public_ip(PublicIPInfo* public_info) {
    if (!is_initialized || !public_info) {
        return false;
    }
    
    FURI_LOG_I(TAG, "Detecting public IP address");
    
    // Clear structure
    memset(public_info, 0, sizeof(PublicIPInfo));
    
    // Simulate public IP detection (in real implementation would use HTTP requests)
    strncpy(public_info->public_ipv4, "203.0.113.42", sizeof(public_info->public_ipv4) - 1);
    strncpy(public_info->public_ipv6, "2001:db8::42", sizeof(public_info->public_ipv6) - 1);
    strncpy(public_info->country, "United States", sizeof(public_info->country) - 1);
    strncpy(public_info->region, "California", sizeof(public_info->region) - 1);
    strncpy(public_info->city, "San Francisco", sizeof(public_info->city) - 1);
    strncpy(public_info->isp, "Example ISP Corp", sizeof(public_info->isp) - 1);
    strncpy(public_info->timezone, "America/Los_Angeles", sizeof(public_info->timezone) - 1);
    
    public_info->has_public_ipv4 = true;
    public_info->has_public_ipv6 = true;
    public_info->location_available = true;
    
    FURI_LOG_I(TAG, "Public IP: %s", public_info->public_ipv4);
    return true;
}

bool network_detector_test_connectivity(uint32_t timeout_ms) {
    if (!is_initialized) {
        return false;
    }
    
    UNUSED(timeout_ms);
    FURI_LOG_I(TAG, "Testing internet connectivity");
    
    // Simulate connectivity test (check if any interface has default route)
    for (size_t i = 0; i < sizeof(mock_interfaces) / sizeof(mock_interfaces[0]); i++) {
        if (mock_interfaces[i].status == NETWORK_STATUS_CONNECTED && 
            mock_interfaces[i].is_default_route &&
            mock_interfaces[i].addresses.has_ipv4) {
            FURI_LOG_I(TAG, "Internet connectivity available via %s", mock_interfaces[i].interface_name);
            return true;
        }
    }
    
    FURI_LOG_W(TAG, "No internet connectivity detected");
    return false;
}

bool network_detector_get_statistics(const char* interface_name, NetworkInterface* interface) {
    if (!interface_name || !interface) {
        return false;
    }
    
    // Get current interface info (which includes updated statistics)
    return network_detector_get_interface_info(interface_name, interface);
}

void network_detector_format_info(const NetworkDetectionResult* result, FuriString* output) {
    if (!result || !output) {
        return;
    }
    
    furi_string_printf(output, "🌐 Internet Connection Status\n\n");
    
    // Overall status
    furi_string_cat_printf(output, "Hostname: %s\n", result->hostname);
    furi_string_cat_printf(output, "Internet: %s\n", 
                          result->internet_accessible ? "✅ Connected" : "❌ Offline");
    furi_string_cat_printf(output, "Interfaces: %d found\n\n", result->interface_count);
    
    // Interface details
    for (uint8_t i = 0; i < result->interface_count; i++) {
        const NetworkInterface* iface = &result->interfaces[i];
        
        furi_string_cat_printf(output, "📶 %s (%s)\n", 
                              iface->interface_name, network_type_to_string(iface->type));
        furi_string_cat_printf(output, "Status: %s%s\n", 
                              network_status_to_string(iface->status),
                              iface->is_default_route ? " [DEFAULT]" : "");
        furi_string_cat_printf(output, "MAC: %s\n", iface->mac_address);
        
        if (iface->addresses.has_ipv4) {
            furi_string_cat_printf(output, "IPv4: %s/%s\n", 
                                  iface->addresses.ipv4_address, 
                                  iface->addresses.ipv4_netmask);
            furi_string_cat_printf(output, "Gateway: %s\n", iface->addresses.ipv4_gateway);
        } else {
            furi_string_cat_printf(output, "IPv4: Not configured\n");
        }
        
        if (iface->addresses.has_ipv6) {
            furi_string_cat_printf(output, "IPv6: %s%s\n", 
                                  iface->addresses.ipv6_address,
                                  iface->addresses.ipv6_prefix);
        } else {
            furi_string_cat_printf(output, "IPv6: Not configured\n");
        }
        
        if (iface->addresses.has_dns) {
            furi_string_cat_printf(output, "DNS: %s", iface->addresses.dns_primary);
            if (strlen(iface->addresses.dns_secondary) > 0) {
                furi_string_cat_printf(output, ", %s", iface->addresses.dns_secondary);
            }
            furi_string_cat_printf(output, "\n");
        }
        
        if (iface->speed_mbps > 0) {
            furi_string_cat_printf(output, "Speed: %lu Mbps\n", (unsigned long)iface->speed_mbps);
        }
        
        if (iface->type == NETWORK_TYPE_WIFI && iface->signal_strength != 0) {
            furi_string_cat_printf(output, "Signal: %d dBm\n", iface->signal_strength);
        }
        
        if (iface->status == NETWORK_STATUS_CONNECTED) {
            furi_string_cat_printf(output, "TX: %llu bytes (%lu pkts)\n", 
                                  (unsigned long long)iface->bytes_sent,
                                  (unsigned long)iface->packets_sent);
            furi_string_cat_printf(output, "RX: %llu bytes (%lu pkts)\n", 
                                  (unsigned long long)iface->bytes_received,
                                  (unsigned long)iface->packets_received);
        }
        
        furi_string_cat_printf(output, "\n");
    }
    
    // Public IP information
    if (result->internet_accessible) {
        furi_string_cat_printf(output, "🌍 Public IP Information\n");
        furi_string_cat_printf(output, "IPv4: 203.0.113.42\n");
        furi_string_cat_printf(output, "IPv6: 2001:db8::42\n");
        furi_string_cat_printf(output, "Location: San Francisco, CA, US\n");
        furi_string_cat_printf(output, "ISP: Example ISP Corp\n");
        furi_string_cat_printf(output, "Timezone: America/Los_Angeles\n\n");
    }
    
    furi_string_cat_printf(output, "🔄 Last updated: %lu ms ago\n", 
                          (unsigned long)(furi_get_tick() - result->detection_timestamp));
    furi_string_cat_printf(output, "\nPress Back to return");
}

// --- Helper Functions ---

const char* network_type_to_string(NetworkType type) {
    switch (type) {
        case NETWORK_TYPE_ETHERNET: return "Ethernet";
        case NETWORK_TYPE_WIFI: return "WiFi";
        case NETWORK_TYPE_USB: return "USB";
        case NETWORK_TYPE_ESP32: return "ESP32";
        case NETWORK_TYPE_CELLULAR: return "Cellular";
        case NETWORK_TYPE_UNKNOWN:
        default: return "Unknown";
    }
}

const char* network_status_to_string(NetworkStatus status) {
    switch (status) {
        case NETWORK_STATUS_CONNECTED: return "Connected";
        case NETWORK_STATUS_CONNECTING: return "Connecting";
        case NETWORK_STATUS_DISCONNECTED: return "Disconnected";
        case NETWORK_STATUS_ERROR: return "Error";
        case NETWORK_STATUS_TIMEOUT: return "Timeout";
        default: return "Unknown";
    }
}

bool network_detector_validate_ipv4(const char* ip_address) {
    if (!ip_address) return false;
    
    int a, b, c, d;
    int result = sscanf(ip_address, "%d.%d.%d.%d", &a, &b, &c, &d);
    
    if (result != 4) return false;
    if (a < 0 || a > 255) return false;
    if (b < 0 || b > 255) return false;
    if (c < 0 || c > 255) return false;
    if (d < 0 || d > 255) return false;
    
    return true;
}

bool network_detector_validate_ipv6(const char* ip_address) {
    if (!ip_address) return false;
    
    // Simplified IPv6 validation - check for colons and hex digits
    size_t len = strlen(ip_address);
    if (len == 0 || len > 39) return false;
    
    int colon_count = 0;
    bool has_double_colon = false;
    
    for (size_t i = 0; i < len; i++) {
        char c = ip_address[i];
        if (c == ':') {
            colon_count++;
            if (i > 0 && ip_address[i-1] == ':') {
                if (has_double_colon) return false; // Multiple ::
                has_double_colon = true;
            }
        } else if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F'))) {
            return false;
        }
    }
    
    // Basic validation: should have at least 2 colons, max 7
    return (colon_count >= 2 && colon_count <= 7);
}

bool network_detector_get_interface_by_type(NetworkType type, char* interface_name, size_t buffer_size) {
    if (!interface_name || buffer_size == 0) return false;
    
    for (size_t i = 0; i < sizeof(mock_interfaces) / sizeof(mock_interfaces[0]); i++) {
        if (mock_interfaces[i].type == type && mock_interfaces[i].status == NETWORK_STATUS_CONNECTED) {
            strncpy(interface_name, mock_interfaces[i].interface_name, buffer_size - 1);
            interface_name[buffer_size - 1] = '\0';
            return true;
        }
    }
    
    return false;
}

bool network_detector_interface_has_internet(const char* interface_name) {
    if (!interface_name) return false;
    
    for (size_t i = 0; i < sizeof(mock_interfaces) / sizeof(mock_interfaces[0]); i++) {
        if (strcmp(mock_interfaces[i].interface_name, interface_name) == 0) {
            return (mock_interfaces[i].status == NETWORK_STATUS_CONNECTED && 
                    mock_interfaces[i].is_default_route &&
                    mock_interfaces[i].addresses.has_ipv4);
        }
    }
    
    return false;
}
