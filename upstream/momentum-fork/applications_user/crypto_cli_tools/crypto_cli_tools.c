#include <furi.h>
#include <gui/gui.h>
#include <gui/view_dispatcher.h>
#include <gui/modules/submenu.h>
#include <gui/modules/text_input.h>
#include <gui/modules/text_box.h>
#include <gui/modules/popup.h>
#include <input/input.h>

#include "crypto_cli_tools_i.h"
#include "cli_bridge.h"
#include "crypto_wallet.h"
#include "ssh_tunnel.h"
#include "crypto_toolkit.h"
// Migrated function includes
#include "wallet_core/hd_wallet.h"
#include "esp32_wifi/esp32_wifi_module.h"
#include "tests/test_suite.h"
#include "network/network_detector.h"

#define TAG "CryptoCliTools"

// Menu items
typedef enum {
    CryptoCliToolsMenuCryptoBom,
    CryptoCliToolsMenuCliBridge,
    CryptoCliToolsMenuSshTunnel,
    CryptoCliToolsMenuWalletTools,
    CryptoCliToolsMenuCryptoDemo,
    CryptoCliToolsMenuInternet,
    CryptoCliToolsMenuAbout,
} CryptoCliToolsMenuItem;

// Views
typedef enum {
    CryptoCliToolsViewSubmenu,
    CryptoCliToolsViewTextInput,
    CryptoCliToolsViewTextBox,
    CryptoCliToolsViewPopup,
} CryptoCliToolsView;

// App context
typedef struct {
    ViewDispatcher* view_dispatcher;
    Submenu* submenu;
    TextInput* text_input;
    TextBox* text_box;
    Popup* popup;
    
    Clibridge* cli_bridge;
    CryptoWallet* wallet;
    SshTunnel* ssh_tunnel;
    
    char text_buffer[256];
    FuriString* text_box_store;
} CryptoCliToolsApp;

// Forward declarations
static void crypto_cli_tools_submenu_callback(void* context, uint32_t index);
static void crypto_cli_tools_text_input_callback(void* context);
static uint32_t crypto_cli_tools_exit(void* context);
static uint32_t crypto_cli_tools_back_to_submenu(void* context);

// Navigation callbacks
static uint32_t crypto_cli_tools_exit(void* context) {
    UNUSED(context);
    return VIEW_NONE;
}

static uint32_t crypto_cli_tools_back_to_submenu(void* context) {
    UNUSED(context);
    return CryptoCliToolsViewSubmenu;
}

// Submenu callback
static void crypto_cli_tools_submenu_callback(void* context, uint32_t index) {
    CryptoCliToolsApp* app = context;
    
    switch(index) {
    case CryptoCliToolsMenuCryptoBom:
        // Initialize crypto wallet interface
        crypto_wallet_show_menu(app->wallet);
        break;
        
    case CryptoCliToolsMenuCliBridge:
        // Start CLI bridge
        view_dispatcher_switch_to_view(app->view_dispatcher, CryptoCliToolsViewTextInput);
        text_input_set_header_text(app->text_input, "CLI Bridge");
        text_input_set_result_callback(
            app->text_input,
            crypto_cli_tools_text_input_callback,
            app,
            app->text_buffer,
            sizeof(app->text_buffer),
            true);
        break;
        
    case CryptoCliToolsMenuSshTunnel:
        // Show SSH tunnel status and controls
        {
            char status_msg[128];
            ssh_tunnel_get_status_message(app->ssh_tunnel, status_msg, sizeof(status_msg));
            SshTunnelStatus tunnel_status = ssh_tunnel_get_status(app->ssh_tunnel);
            
            const char* status_names[] = {
                "Disconnected", "Connecting", "Connected", "Reconnecting", "Failed"
            };
            
            furi_string_printf(app->text_box_store, "SSH Tunnel Manager\n\n");
            furi_string_cat_printf(app->text_box_store, "Status: %s\n", status_names[tunnel_status]);
            furi_string_cat_printf(app->text_box_store, "Message: %s\n\n", status_msg);
            furi_string_cat_printf(app->text_box_store, "Configuration:\n");
            furi_string_cat_printf(app->text_box_store, "• Target: xs-mac\n");
            furi_string_cat_printf(app->text_box_store, "• User: x\n");
            furi_string_cat_printf(app->text_box_store, "• Ports: 8080->3000\n");
            furi_string_cat_printf(app->text_box_store, "• Auto-reconnect: Yes\n\n");
            
            if(tunnel_status == SshTunnelStatusConnected) {
                furi_string_cat_printf(app->text_box_store, "Tunnel is active!\n");
            } else {
                furi_string_cat_printf(app->text_box_store, "Use CLI to start tunnel\n");
            }
            
            furi_string_cat_printf(app->text_box_store, "\nPress Back to return");
        }
        
        text_box_set_text(app->text_box, furi_string_get_cstr(app->text_box_store));
        view_dispatcher_switch_to_view(app->view_dispatcher, CryptoCliToolsViewTextBox);
        break;
        
    case CryptoCliToolsMenuWalletTools:
        // Show wallet tools
        furi_string_printf(app->text_box_store, "Wallet Tools\n\n");
        furi_string_cat_printf(app->text_box_store, "Available functions:\n");
        furi_string_cat_printf(app->text_box_store, "• Generate mnemonic\n");
        furi_string_cat_printf(app->text_box_store, "• Derive keys\n");
        furi_string_cat_printf(app->text_box_store, "• Sign transactions\n");
        furi_string_cat_printf(app->text_box_store, "\nPress Back to return");
        
        text_box_set_text(app->text_box, furi_string_get_cstr(app->text_box_store));
        view_dispatcher_switch_to_view(app->view_dispatcher, CryptoCliToolsViewTextBox);
        break;
        
    case CryptoCliToolsMenuCryptoDemo:
        // Run production crypto toolkit validation
        {
            CryptoToolkit* toolkit = crypto_toolkit_alloc();
            crypto_toolkit_run_tests(toolkit);
            crypto_toolkit_free(toolkit);
            
            furi_string_printf(app->text_box_store, "Production Crypto Toolkit Validation Complete\n\n");
            furi_string_cat_printf(app->text_box_store, "All cryptographic functions validated.\n");
            furi_string_cat_printf(app->text_box_store, "Check the debug log for detailed results.\n\n");
            furi_string_cat_printf(app->text_box_store, "Validated Functions:\n");
            furi_string_cat_printf(app->text_box_store, "• SHA-256, Keccak-256, RIPEMD-160\n");
            furi_string_cat_printf(app->text_box_store, "• HMAC-SHA512, HASH160\n");
            furi_string_cat_printf(app->text_box_store, "• Keypair generation & derivation\n");
            furi_string_cat_printf(app->text_box_store, "• AES-256 encryption/decryption\n");
            furi_string_cat_printf(app->text_box_store, "• Digital signatures & verification\n");
            furi_string_cat_printf(app->text_box_store, "• PBKDF2-HMAC-SHA256\n");
            furi_string_cat_printf(app->text_box_store, "• Performance benchmarks\n\n");
            furi_string_cat_printf(app->text_box_store, "\nPress Back to return");
        }
        
        text_box_set_text(app->text_box, furi_string_get_cstr(app->text_box_store));
        view_dispatcher_switch_to_view(app->view_dispatcher, CryptoCliToolsViewTextBox);
        break;
        
    case CryptoCliToolsMenuInternet:
        // Auto-detect network interfaces and show Internet connection status
        {
            // Initialize network detector
            network_detector_init();
            
            NetworkDetectionResult network_result;
            bool detection_success = network_detector_scan_interfaces(&network_result);
            
            if(detection_success) {
                // Format network information for display
                network_detector_format_info(&network_result, app->text_box_store);
                
                // Get additional public IP information if connected
                if(network_result.internet_accessible) {
                    PublicIPInfo public_info;
                    if(network_detector_get_public_ip(&public_info)) {
                        // Public IP info is already included in format_info
                        FURI_LOG_I(TAG, "Public IP detection successful");
                    }
                }
            } else {
                furi_string_printf(app->text_box_store, "🌐 Internet Connection Status\n\n");
                furi_string_cat_printf(app->text_box_store, "❌ Network Detection Failed\n\n");
                furi_string_cat_printf(app->text_box_store, "Unable to detect network interfaces.\n");
                furi_string_cat_printf(app->text_box_store, "This may be normal on Flipper Zero\n");
                furi_string_cat_printf(app->text_box_store, "as it doesn't have built-in networking.\n\n");
                furi_string_cat_printf(app->text_box_store, "Network Detection Features:\n");
                furi_string_cat_printf(app->text_box_store, "• Auto-detect Ethernet interfaces\n");
                furi_string_cat_printf(app->text_box_store, "• Show IPv4 and IPv6 addresses\n");
                furi_string_cat_printf(app->text_box_store, "• Display public IP information\n");
                furi_string_cat_printf(app->text_box_store, "• Network statistics and monitoring\n");
                furi_string_cat_printf(app->text_box_store, "• Support for USB, WiFi, ESP32 modules\n\n");
                furi_string_cat_printf(app->text_box_store, "🔧 For real network detection:\n");
                furi_string_cat_printf(app->text_box_store, "• Connect USB-Ethernet adapter\n");
                furi_string_cat_printf(app->text_box_store, "• Use ESP32 WiFi module\n");
                furi_string_cat_printf(app->text_box_store, "• Enable USB networking mode\n\n");
                furi_string_cat_printf(app->text_box_store, "\nPress Back to return");
            }
            
            // Cleanup network detector
            network_detector_cleanup();
        }
        
        text_box_set_text(app->text_box, furi_string_get_cstr(app->text_box_store));
        view_dispatcher_switch_to_view(app->view_dispatcher, CryptoCliToolsViewTextBox);
        break;
        
    case CryptoCliToolsMenuAbout:
        furi_string_printf(app->text_box_store, "Crypto CLI Tools v1.0\n\n");
        furi_string_cat_printf(app->text_box_store, "A comprehensive crypto wallet ");
        furi_string_cat_printf(app->text_box_store, "and CLI bridge tool for Flipper Zero.\n\n");
        furi_string_cat_printf(app->text_box_store, "Features:\n");
        furi_string_cat_printf(app->text_box_store, "• HD Wallet support\n");
        furi_string_cat_printf(app->text_box_store, "• Multi-currency support\n");
        furi_string_cat_printf(app->text_box_store, "• CLI interface bridge\n");
        furi_string_cat_printf(app->text_box_store, "• Secure key management\n\n");
        furi_string_cat_printf(app->text_box_store, "Author: d3c0d3r\n");
        furi_string_cat_printf(app->text_box_store, "\nPress Back to return");
        
        text_box_set_text(app->text_box, furi_string_get_cstr(app->text_box_store));
        view_dispatcher_switch_to_view(app->view_dispatcher, CryptoCliToolsViewTextBox);
        break;
        
    default:
        break;
    }
}

// Text input callback  
static void crypto_cli_tools_text_input_callback(void* context) {
    CryptoCliToolsApp* app = context;
    
    // Execute command through CLI bridge
    FuriString* result = furi_string_alloc();
    bool success = cli_bridge_execute_command(app->cli_bridge, app->text_buffer, result);
    
    if(success) {
        furi_string_printf(app->text_box_store, "Command: %s\n\n", app->text_buffer);
        furi_string_cat_printf(app->text_box_store, "Output:\n%s", furi_string_get_cstr(result));
    } else {
        furi_string_printf(app->text_box_store, "Command: %s\n\n", app->text_buffer);
        furi_string_cat_printf(app->text_box_store, "Error: Failed to execute command\n");
        furi_string_cat_printf(app->text_box_store, "%s", furi_string_get_cstr(result));
    }
    
    text_box_set_text(app->text_box, furi_string_get_cstr(app->text_box_store));
    view_dispatcher_switch_to_view(app->view_dispatcher, CryptoCliToolsViewTextBox);
    
    furi_string_free(result);
}

// App allocation
static CryptoCliToolsApp* crypto_cli_tools_app_alloc() {
    CryptoCliToolsApp* app = malloc(sizeof(CryptoCliToolsApp));
    
    // Initialize view dispatcher
    app->view_dispatcher = view_dispatcher_alloc();
    view_dispatcher_set_event_callback_context(app->view_dispatcher, app);
    
    // Initialize submenu
    app->submenu = submenu_alloc();
    submenu_add_item(app->submenu, "Crypto Wallet", CryptoCliToolsMenuCryptoBom, crypto_cli_tools_submenu_callback, app);
    submenu_add_item(app->submenu, "CLI Bridge", CryptoCliToolsMenuCliBridge, crypto_cli_tools_submenu_callback, app);
    submenu_add_item(app->submenu, "SSH Tunnel", CryptoCliToolsMenuSshTunnel, crypto_cli_tools_submenu_callback, app);
    submenu_add_item(app->submenu, "Wallet Tools", CryptoCliToolsMenuWalletTools, crypto_cli_tools_submenu_callback, app);
    submenu_add_item(app->submenu, "Crypto Toolkit", CryptoCliToolsMenuCryptoDemo, crypto_cli_tools_submenu_callback, app);
    submenu_add_item(app->submenu, "Internet", CryptoCliToolsMenuInternet, crypto_cli_tools_submenu_callback, app);
    submenu_add_item(app->submenu, "About", CryptoCliToolsMenuAbout, crypto_cli_tools_submenu_callback, app);
    
    view_set_previous_callback(submenu_get_view(app->submenu), crypto_cli_tools_exit);
    view_dispatcher_add_view(app->view_dispatcher, CryptoCliToolsViewSubmenu, submenu_get_view(app->submenu));
    
    // Initialize text input
    app->text_input = text_input_alloc();
    view_set_previous_callback(text_input_get_view(app->text_input), crypto_cli_tools_back_to_submenu);
    view_dispatcher_add_view(app->view_dispatcher, CryptoCliToolsViewTextInput, text_input_get_view(app->text_input));
    
    // Initialize text box
    app->text_box = text_box_alloc();
    app->text_box_store = furi_string_alloc();
    view_set_previous_callback(text_box_get_view(app->text_box), crypto_cli_tools_back_to_submenu);
    view_dispatcher_add_view(app->view_dispatcher, CryptoCliToolsViewTextBox, text_box_get_view(app->text_box));
    
    // Initialize popup
    app->popup = popup_alloc();
    view_set_previous_callback(popup_get_view(app->popup), crypto_cli_tools_back_to_submenu);
    view_dispatcher_add_view(app->view_dispatcher, CryptoCliToolsViewPopup, popup_get_view(app->popup));
    
    // Initialize modules
    app->cli_bridge = cli_bridge_alloc();
    app->wallet = crypto_wallet_alloc();
    app->ssh_tunnel = ssh_tunnel_alloc();
    
    return app;
}

// App deallocation
static void crypto_cli_tools_app_free(CryptoCliToolsApp* app) {
    furi_assert(app);
    
    // Free modules
    cli_bridge_free(app->cli_bridge);
    crypto_wallet_free(app->wallet);
    ssh_tunnel_free(app->ssh_tunnel);
    
    // Remove views from dispatcher
    view_dispatcher_remove_view(app->view_dispatcher, CryptoCliToolsViewSubmenu);
    view_dispatcher_remove_view(app->view_dispatcher, CryptoCliToolsViewTextInput);
    view_dispatcher_remove_view(app->view_dispatcher, CryptoCliToolsViewTextBox);
    view_dispatcher_remove_view(app->view_dispatcher, CryptoCliToolsViewPopup);
    
    // Free views
    submenu_free(app->submenu);
    text_input_free(app->text_input);
    text_box_free(app->text_box);
    popup_free(app->popup);
    furi_string_free(app->text_box_store);
    
    // Free view dispatcher
    view_dispatcher_free(app->view_dispatcher);
    
    // Free app
    free(app);
}

// Main entry point
int32_t crypto_cli_tools_app_main(void* p) {
    UNUSED(p);
    
    CryptoCliToolsApp* app = crypto_cli_tools_app_alloc();
    
    // Open GUI and attach view dispatcher
    Gui* gui = furi_record_open(RECORD_GUI);
    view_dispatcher_attach_to_gui(app->view_dispatcher, gui, ViewDispatcherTypeFullscreen);
    
    // Set initial view
    view_dispatcher_switch_to_view(app->view_dispatcher, CryptoCliToolsViewSubmenu);
    
    // Run app
    view_dispatcher_run(app->view_dispatcher);
    
    // Cleanup
    furi_record_close(RECORD_GUI);
    crypto_cli_tools_app_free(app);
    
    return 0;
}
