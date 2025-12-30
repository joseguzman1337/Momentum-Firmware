// Network Detection Module for Crypto CLI Tools
// Auto-detect ethernet connections and retrieve network information

#pragma once

#include <stdint.h>
#include <stdbool.h>
#include <furi.h>

// Network interface types
typedef enum {
    NETWORK_TYPE_UNKNOWN = 0,
    NETWORK_TYPE_ETHERNET = 1,
    NETWORK_TYPE_WIFI = 2,
    NETWORK_TYPE_USB = 3,
    NETWORK_TYPE_ESP32 = 4,
    NETWORK_TYPE_CELLULAR = 5
} NetworkType;

// Network connection status
typedef enum {
    NETWORK_STATUS_DISCONNECTED = 0,
    NETWORK_STATUS_CONNECTING = 1,
    NETWORK_STATUS_CONNECTED = 2,
    NETWORK_STATUS_ERROR = 3,
    NETWORK_STATUS_TIMEOUT = 4
} NetworkStatus;

// IP address information
typedef struct {
    char ipv4_address[16];      // xxx.xxx.xxx.xxx\0
    char ipv4_netmask[16];      // xxx.xxx.xxx.xxx\0
    char ipv4_gateway[16];      // xxx.xxx.xxx.xxx\0
    char ipv6_address[40];      // xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx\0
    char ipv6_prefix[8];        // /xx\0
    char dns_primary[16];       // Primary DNS server
    char dns_secondary[16];     // Secondary DNS server
    bool has_ipv4;
    bool has_ipv6;
    bool has_dns;
} NetworkAddresses;

// Network interface information
typedef struct {
    char interface_name[16];    // eth0, wlan0, etc.
    char mac_address[18];       // xx:xx:xx:xx:xx:xx\0
    NetworkType type;
    NetworkStatus status;
    NetworkAddresses addresses;
    uint32_t speed_mbps;        // Interface speed in Mbps
    int8_t signal_strength;     // WiFi signal strength (-100 to 0 dBm)
    uint64_t bytes_sent;
    uint64_t bytes_received;
    uint32_t packets_sent;
    uint32_t packets_received;
    bool is_default_route;      // Is this the default gateway interface
} NetworkInterface;

// Public IP information
typedef struct {
    char public_ipv4[16];       // Public IPv4 address
    char public_ipv6[40];       // Public IPv6 address
    char country[32];           // Country name
    char region[32];            // Region/state
    char city[32];              // City name
    char isp[64];               // Internet service provider
    char timezone[32];          // Timezone
    bool has_public_ipv4;
    bool has_public_ipv6;
    bool location_available;
} PublicIPInfo;

// Complete network information
typedef struct {
    NetworkInterface interfaces[8];  // Up to 8 network interfaces
    uint8_t interface_count;
    PublicIPInfo public_info;
    char hostname[64];
    bool internet_accessible;
    uint32_t detection_timestamp;
} NetworkDetectionResult;

// --- Network Detection Functions ---

/**
 * @brief Initialize network detection module
 * @return true on success, false on failure
 */
bool network_detector_init(void);

/**
 * @brief Cleanup network detection module
 */
void network_detector_cleanup(void);

/**
 * @brief Auto-detect all network interfaces
 * @param result Pointer to store detection results
 * @return true on success, false on failure
 */
bool network_detector_scan_interfaces(NetworkDetectionResult* result);

/**
 * @brief Get detailed information for a specific interface
 * @param interface_name Name of the interface (e.g., "eth0")
 * @param interface Pointer to store interface information
 * @return true on success, false on failure
 */
bool network_detector_get_interface_info(const char* interface_name, NetworkInterface* interface);

/**
 * @brief Detect public IP address and location information
 * @param public_info Pointer to store public IP information
 * @return true on success, false on failure
 */
bool network_detector_get_public_ip(PublicIPInfo* public_info);

/**
 * @brief Test internet connectivity
 * @param timeout_ms Timeout in milliseconds
 * @return true if internet is accessible, false otherwise
 */
bool network_detector_test_connectivity(uint32_t timeout_ms);

/**
 * @brief Get network statistics for an interface
 * @param interface_name Name of the interface
 * @param interface Pointer to update with statistics
 * @return true on success, false on failure
 */
bool network_detector_get_statistics(const char* interface_name, NetworkInterface* interface);

/**
 * @brief Format network information for display
 * @param result Network detection result
 * @param output FuriString to store formatted output
 */
void network_detector_format_info(const NetworkDetectionResult* result, FuriString* output);

// --- Helper Functions ---

/**
 * @brief Convert network type to string
 * @param type Network type
 * @return String representation
 */
const char* network_type_to_string(NetworkType type);

/**
 * @brief Convert network status to string
 * @param status Network status
 * @return String representation
 */
const char* network_status_to_string(NetworkStatus status);

/**
 * @brief Validate IPv4 address format
 * @param ip_address IPv4 address string
 * @return true if valid, false otherwise
 */
bool network_detector_validate_ipv4(const char* ip_address);

/**
 * @brief Validate IPv6 address format
 * @param ip_address IPv6 address string
 * @return true if valid, false otherwise
 */
bool network_detector_validate_ipv6(const char* ip_address);

/**
 * @brief Get interface name by type
 * @param type Network type
 * @param interface_name Buffer to store interface name
 * @param buffer_size Size of the buffer
 * @return true if found, false otherwise
 */
bool network_detector_get_interface_by_type(NetworkType type, char* interface_name, size_t buffer_size);

/**
 * @brief Check if interface has internet access
 * @param interface_name Name of the interface
 * @return true if has internet access, false otherwise
 */
bool network_detector_interface_has_internet(const char* interface_name);
