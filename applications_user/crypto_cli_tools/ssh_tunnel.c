#include "ssh_tunnel.h"
#include <furi.h>
#include <furi_hal_random.h>
#include <storage/storage.h>

#define TAG "SshTunnel"
#define SSH_TUNNEL_FILE_PATH APP_DATA_PATH("ssh_tunnel.conf")
#define DEFAULT_KEEP_ALIVE 60
#define DEFAULT_TIMEOUT 10
#define MAX_RECONNECT_ATTEMPTS 5

struct SshTunnel {
    SshTunnelConfig config;
    SshTunnelStatus status;
    char status_message[128];
    uint32_t process_id;
    FuriThread* monitor_thread;
    FuriMutex* mutex;
    Storage* storage;
    File* config_file;
    bool stop_requested;
    uint32_t reconnect_attempts;
    uint32_t last_connection_time;
};

static const char* status_names[] = {
    "Disconnected",
    "Connecting", 
    "Connected",
    "Reconnecting",
    "Failed"
};

// Forward declarations
static int32_t ssh_tunnel_monitor_thread(void* context);
static bool ssh_tunnel_load_config(SshTunnel* tunnel);
static bool ssh_tunnel_save_config(SshTunnel* tunnel);
static void ssh_tunnel_set_status(SshTunnel* tunnel, SshTunnelStatus status, const char* message);

SshTunnel* ssh_tunnel_alloc() {
    SshTunnel* tunnel = malloc(sizeof(SshTunnel));
    
    // Initialize default configuration
    memset(&tunnel->config, 0, sizeof(SshTunnelConfig));
    strcpy(tunnel->config.target_host, "xs-mac");
    strcpy(tunnel->config.ssh_user, "x");
    tunnel->config.local_port = 8080;
    tunnel->config.remote_port = 3000;
    tunnel->config.keep_alive_interval = DEFAULT_KEEP_ALIVE;
    tunnel->config.connection_timeout = DEFAULT_TIMEOUT;
    tunnel->config.auto_reconnect = true;
    
    tunnel->status = SshTunnelStatusDisconnected;
    memset(tunnel->status_message, 0, sizeof(tunnel->status_message));
    strcpy(tunnel->status_message, "Ready to connect");
    
    tunnel->process_id = 0;
    tunnel->monitor_thread = NULL;
    tunnel->mutex = furi_mutex_alloc(FuriMutexTypeNormal);
    tunnel->stop_requested = false;
    tunnel->reconnect_attempts = 0;
    tunnel->last_connection_time = 0;
    
    tunnel->storage = furi_record_open(RECORD_STORAGE);
    tunnel->config_file = storage_file_alloc(tunnel->storage);
    
    // Try to load saved configuration
    ssh_tunnel_load_config(tunnel);
    
    FURI_LOG_I(TAG, "SSH tunnel allocated");
    return tunnel;
}

void ssh_tunnel_free(SshTunnel* tunnel) {
    furi_assert(tunnel);
    
    // Stop tunnel if running
    if(tunnel->status != SshTunnelStatusDisconnected) {
        ssh_tunnel_stop(tunnel);
    }
    
    // Cleanup
    if(tunnel->config_file) {
        storage_file_free(tunnel->config_file);
    }
    
    if(tunnel->storage) {
        furi_record_close(RECORD_STORAGE);
    }
    
    if(tunnel->mutex) {
        furi_mutex_free(tunnel->mutex);
    }
    
    free(tunnel);
    FURI_LOG_I(TAG, "SSH tunnel freed");
}

bool ssh_tunnel_configure(SshTunnel* tunnel, const SshTunnelConfig* config) {
    furi_assert(tunnel);
    furi_assert(config);
    
    furi_mutex_acquire(tunnel->mutex, FuriWaitForever);
    
    // Copy configuration
    memcpy(&tunnel->config, config, sizeof(SshTunnelConfig));
    
    // Save configuration
    bool result = ssh_tunnel_save_config(tunnel);
    
    furi_mutex_release(tunnel->mutex);
    
    FURI_LOG_I(TAG, "SSH tunnel configured: host=%s, user=%s, ports=%d->%d", 
               config->target_host, config->ssh_user, config->local_port, config->remote_port);
    
    return result;
}

bool ssh_tunnel_start(SshTunnel* tunnel) {
    furi_assert(tunnel);
    
    furi_mutex_acquire(tunnel->mutex, FuriWaitForever);
    
    if(tunnel->status == SshTunnelStatusConnected) {
        furi_mutex_release(tunnel->mutex);
        return true;
    }
    
    ssh_tunnel_set_status(tunnel, SshTunnelStatusConnecting, "Starting SSH tunnel");
    tunnel->stop_requested = false;
    tunnel->reconnect_attempts = 0;
    
    // Start monitor thread
    if(!tunnel->monitor_thread) {
        tunnel->monitor_thread = furi_thread_alloc_ex("SshTunnelMonitor", 2048, ssh_tunnel_monitor_thread, tunnel);
        furi_thread_start(tunnel->monitor_thread);
    }
    
    furi_mutex_release(tunnel->mutex);
    
    FURI_LOG_I(TAG, "SSH tunnel start requested");
    return true;
}

bool ssh_tunnel_stop(SshTunnel* tunnel) {
    furi_assert(tunnel);
    
    furi_mutex_acquire(tunnel->mutex, FuriWaitForever);
    
    tunnel->stop_requested = true;
    
    // Stop monitor thread
    if(tunnel->monitor_thread) {
        furi_thread_join(tunnel->monitor_thread);
        furi_thread_free(tunnel->monitor_thread);
        tunnel->monitor_thread = NULL;
    }
    
    ssh_tunnel_set_status(tunnel, SshTunnelStatusDisconnected, "Tunnel stopped");
    tunnel->process_id = 0;
    
    furi_mutex_release(tunnel->mutex);
    
    FURI_LOG_I(TAG, "SSH tunnel stopped");
    return true;
}

SshTunnelStatus ssh_tunnel_get_status(SshTunnel* tunnel) {
    furi_assert(tunnel);
    
    furi_mutex_acquire(tunnel->mutex, FuriWaitForever);
    SshTunnelStatus status = tunnel->status;
    furi_mutex_release(tunnel->mutex);
    
    return status;
}

bool ssh_tunnel_get_status_message(SshTunnel* tunnel, char* message, size_t message_size) {
    furi_assert(tunnel);
    furi_assert(message);
    
    furi_mutex_acquire(tunnel->mutex, FuriWaitForever);
    strncpy(message, tunnel->status_message, message_size - 1);
    message[message_size - 1] = '\0';
    furi_mutex_release(tunnel->mutex);
    
    return true;
}

bool ssh_tunnel_is_active(SshTunnel* tunnel) {
    furi_assert(tunnel);
    return ssh_tunnel_get_status(tunnel) == SshTunnelStatusConnected;
}

bool ssh_tunnel_restart(SshTunnel* tunnel) {
    furi_assert(tunnel);
    
    FURI_LOG_I(TAG, "Restarting SSH tunnel");
    
    ssh_tunnel_stop(tunnel);
    furi_delay_ms(1000);
    return ssh_tunnel_start(tunnel);
}

bool ssh_tunnel_test_connectivity(SshTunnel* tunnel) {
    furi_assert(tunnel);
    
    // For demonstration purposes, simulate connectivity test
    // In a real implementation, this would test network connectivity
    // to the target host
    
    FURI_LOG_I(TAG, "Testing connectivity to %s", tunnel->config.target_host);
    
    // Simulate network test delay
    furi_delay_ms(100);
    
    // For now, return true to simulate successful connectivity
    // In reality, this would check if the host is reachable
    return true;
}

// Helper functions
static void ssh_tunnel_set_status(SshTunnel* tunnel, SshTunnelStatus status, const char* message) {
    tunnel->status = status;
    if(message) {
        strncpy(tunnel->status_message, message, sizeof(tunnel->status_message) - 1);
        tunnel->status_message[sizeof(tunnel->status_message) - 1] = '\0';
    }
    
    FURI_LOG_I(TAG, "Status: %s - %s", status_names[status], tunnel->status_message);
}

static bool ssh_tunnel_load_config(SshTunnel* tunnel) {
    if(!storage_file_exists(tunnel->storage, SSH_TUNNEL_FILE_PATH)) {
        return false;
    }
    
    if(!storage_file_open(tunnel->config_file, SSH_TUNNEL_FILE_PATH, FSAM_READ, FSOM_OPEN_EXISTING)) {
        return false;
    }
    
    size_t bytes_read = storage_file_read(tunnel->config_file, &tunnel->config, sizeof(SshTunnelConfig));
    storage_file_close(tunnel->config_file);
    
    if(bytes_read == sizeof(SshTunnelConfig)) {
        FURI_LOG_I(TAG, "Configuration loaded from storage");
        return true;
    }
    
    return false;
}

static bool ssh_tunnel_save_config(SshTunnel* tunnel) {
    // Create storage directory if it doesn't exist
    storage_simply_mkdir(tunnel->storage, APP_DATA_PATH(""));
    
    if(!storage_file_open(tunnel->config_file, SSH_TUNNEL_FILE_PATH, FSAM_WRITE, FSOM_CREATE_ALWAYS)) {
        return false;
    }
    
    size_t bytes_written = storage_file_write(tunnel->config_file, &tunnel->config, sizeof(SshTunnelConfig));
    storage_file_close(tunnel->config_file);
    
    if(bytes_written == sizeof(SshTunnelConfig)) {
        FURI_LOG_I(TAG, "Configuration saved to storage");
        return true;
    }
    
    return false;
}

static int32_t ssh_tunnel_monitor_thread(void* context) {
    SshTunnel* tunnel = context;
    
    FURI_LOG_I(TAG, "SSH tunnel monitor thread started");
    
    while(!tunnel->stop_requested) {
        furi_mutex_acquire(tunnel->mutex, FuriWaitForever);
        
        SshTunnelStatus current_status = tunnel->status;
        
        switch(current_status) {
        case SshTunnelStatusConnecting:
        case SshTunnelStatusReconnecting:
            // Simulate connection attempt
            if(ssh_tunnel_test_connectivity(tunnel)) {
                ssh_tunnel_set_status(tunnel, SshTunnelStatusConnected, "SSH tunnel established");
                tunnel->reconnect_attempts = 0;
                tunnel->last_connection_time = furi_get_tick();
                tunnel->process_id = furi_hal_random_get(); // Simulate process ID
            } else {
                tunnel->reconnect_attempts++;
                if(tunnel->reconnect_attempts >= MAX_RECONNECT_ATTEMPTS) {
                    ssh_tunnel_set_status(tunnel, SshTunnelStatusFailed, "Maximum reconnection attempts reached");
                } else {
                    char msg[64];
                    snprintf(msg, sizeof(msg), "Connection failed, attempt %lu/%d", 
                             (unsigned long)tunnel->reconnect_attempts, MAX_RECONNECT_ATTEMPTS);
                    ssh_tunnel_set_status(tunnel, SshTunnelStatusReconnecting, msg);
                }
            }
            break;
            
        case SshTunnelStatusConnected:
            // Check if connection is still alive (simulate periodic check)
            if(!ssh_tunnel_test_connectivity(tunnel)) {
                if(tunnel->config.auto_reconnect) {
                    ssh_tunnel_set_status(tunnel, SshTunnelStatusReconnecting, "Connection lost, reconnecting");
                } else {
                    ssh_tunnel_set_status(tunnel, SshTunnelStatusFailed, "Connection lost");
                }
            }
            break;
            
        case SshTunnelStatusFailed:
            if(tunnel->config.auto_reconnect && tunnel->reconnect_attempts < MAX_RECONNECT_ATTEMPTS) {
                ssh_tunnel_set_status(tunnel, SshTunnelStatusReconnecting, "Auto-reconnect enabled");
            }
            break;
            
        default:
            break;
        }
        
        furi_mutex_release(tunnel->mutex);
        
        // Sleep for monitoring interval
        furi_delay_ms(5000);
    }
    
    FURI_LOG_I(TAG, "SSH tunnel monitor thread stopped");
    return 0;
}
