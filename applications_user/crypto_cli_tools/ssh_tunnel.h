#pragma once

#include <furi.h>

typedef struct SshTunnel SshTunnel;

// Tunnel status
typedef enum {
    SshTunnelStatusDisconnected,
    SshTunnelStatusConnecting,
    SshTunnelStatusConnected,
    SshTunnelStatusReconnecting,
    SshTunnelStatusFailed,
} SshTunnelStatus;

// Tunnel configuration
typedef struct {
    char target_host[64];
    char ssh_user[32];
    uint16_t local_port;
    uint16_t remote_port;
    uint32_t keep_alive_interval;
    uint32_t connection_timeout;
    bool auto_reconnect;
} SshTunnelConfig;

/**
 * @brief Allocate SSH tunnel instance
 * @return SshTunnel* Pointer to allocated instance
 */
SshTunnel* ssh_tunnel_alloc(void);

/**
 * @brief Free SSH tunnel instance
 * @param tunnel Pointer to SSH tunnel instance
 */
void ssh_tunnel_free(SshTunnel* tunnel);

/**
 * @brief Configure SSH tunnel parameters
 * @param tunnel Pointer to SSH tunnel instance
 * @param config Tunnel configuration
 * @return bool True if configuration successful
 */
bool ssh_tunnel_configure(SshTunnel* tunnel, const SshTunnelConfig* config);

/**
 * @brief Start SSH tunnel
 * @param tunnel Pointer to SSH tunnel instance
 * @return bool True if tunnel started successfully
 */
bool ssh_tunnel_start(SshTunnel* tunnel);

/**
 * @brief Stop SSH tunnel
 * @param tunnel Pointer to SSH tunnel instance
 * @return bool True if tunnel stopped successfully
 */
bool ssh_tunnel_stop(SshTunnel* tunnel);

/**
 * @brief Get tunnel status
 * @param tunnel Pointer to SSH tunnel instance
 * @return SshTunnelStatus Current tunnel status
 */
SshTunnelStatus ssh_tunnel_get_status(SshTunnel* tunnel);

/**
 * @brief Get tunnel status message
 * @param tunnel Pointer to SSH tunnel instance
 * @param message Buffer to store status message
 * @param message_size Size of message buffer
 * @return bool True if message retrieved successfully
 */
bool ssh_tunnel_get_status_message(SshTunnel* tunnel, char* message, size_t message_size);

/**
 * @brief Check if tunnel is active
 * @param tunnel Pointer to SSH tunnel instance
 * @return bool True if tunnel is active
 */
bool ssh_tunnel_is_active(SshTunnel* tunnel);

/**
 * @brief Restart SSH tunnel
 * @param tunnel Pointer to SSH tunnel instance
 * @return bool True if tunnel restarted successfully
 */
bool ssh_tunnel_restart(SshTunnel* tunnel);

/**
 * @brief Test connectivity to target host
 * @param tunnel Pointer to SSH tunnel instance
 * @return bool True if target host is reachable
 */
bool ssh_tunnel_test_connectivity(SshTunnel* tunnel);
