#include "cli_bridge.h"
#include <furi.h>

#define TAG "CliBridge"

struct Clibridge {
    FuriStreamBuffer* rx_stream;
    FuriStreamBuffer* tx_stream;
    bool active;
};

Clibridge* cli_bridge_alloc() {
    Clibridge* cli_bridge = malloc(sizeof(Clibridge));
    
    // Allocate stream buffers for communication
    cli_bridge->rx_stream = furi_stream_buffer_alloc(1024, 1);
    cli_bridge->tx_stream = furi_stream_buffer_alloc(1024, 1);
    
    cli_bridge->active = false;
    
    return cli_bridge;
}

void cli_bridge_free(Clibridge* cli_bridge) {
    furi_assert(cli_bridge);
    
    if(cli_bridge->active) {
        cli_bridge_stop(cli_bridge);
    }
    
    furi_stream_buffer_free(cli_bridge->rx_stream);
    furi_stream_buffer_free(cli_bridge->tx_stream);
    
    free(cli_bridge);
}

bool cli_bridge_start(Clibridge* cli_bridge) {
    furi_assert(cli_bridge);
    
    if(cli_bridge->active) {
        return true;
    }
    
    cli_bridge->active = true;
    
    FURI_LOG_I(TAG, "CLI bridge started");
    return true;
}

bool cli_bridge_stop(Clibridge* cli_bridge) {
    furi_assert(cli_bridge);
    
    if(!cli_bridge->active) {
        return true;
    }
    
    cli_bridge->active = false;
    
    FURI_LOG_I(TAG, "CLI bridge stopped");
    return true;
}

bool cli_bridge_execute_command(Clibridge* cli_bridge, const char* command, FuriString* result) {
    furi_assert(cli_bridge);
    furi_assert(command);
    furi_assert(result);
    
    furi_string_reset(result);
    
    if(!cli_bridge->active) {
        if(!cli_bridge_start(cli_bridge)) {
            furi_string_set(result, "Failed to start CLI bridge");
            return false;
        }
    }
    
    // Clear any existing data in streams
    furi_stream_buffer_reset(cli_bridge->rx_stream);
    furi_stream_buffer_reset(cli_bridge->tx_stream);
    
    // For demo purposes, simulate command execution
    furi_string_printf(result, "Simulated output for command: %s\n", command);
    furi_string_cat_printf(result, "CLI bridge is active: %s\n", cli_bridge->active ? "Yes" : "No");
    furi_string_cat_printf(result, "This is a demonstration CLI bridge.\n");
    
    // Simulate some processing time
    furi_delay_ms(100);
    
    FURI_LOG_D(TAG, "Command executed: %s", command);
    return true;
}

bool cli_bridge_is_active(Clibridge* cli_bridge) {
    furi_assert(cli_bridge);
    return cli_bridge->active;
}
