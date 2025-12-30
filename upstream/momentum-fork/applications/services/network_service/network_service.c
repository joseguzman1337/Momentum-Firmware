#include <furi.h>
#include <furi_hal.h>
#include <lwip/tcpip.h>
#include <lwip/netif.h>
#include <lwip/dhcp.h>
#include <lwip/init.h>
#include <lwip/apps/http_client.h>

// Prototype for the LwIP Interface Init (callbacks provided by furi_lwip_netif.c)
err_t ethernetif_init(struct netif* netif);

#define TAG "NetworkService"

static struct netif furi_netif;

static int32_t network_service_thread(void* ctx) {
    UNUSED(ctx);

    // Allow system to stabilize
    furi_delay_ms(1000);

    FURI_LOG_I(TAG, "Initializing LwIP Stack...");

    // Initialize TCP/IP stack
    tcpip_init(NULL, NULL);

    ip4_addr_t ipaddr, netmask, gw;
    IP4_ADDR(&ipaddr, 0, 0, 0, 0);
    IP4_ADDR(&netmask, 0, 0, 0, 0);
    IP4_ADDR(&gw, 0, 0, 0, 0);

    // Add the network interface
    // ethernetif_init is defined in lib/lwip/port/furi_lwip_netif.c
    if(netif_add(&furi_netif, &ipaddr, &netmask, &gw, NULL, ethernetif_init, tcpip_input) ==
       NULL) {
        FURI_LOG_E(TAG, "netif_add failed");
        return -1;
    }

    // Set as default
    netif_set_default(&furi_netif);

    // Bring it up
    netif_set_up(&furi_netif);

    // Start DHCP
    FURI_LOG_I(TAG, "Starting DHCP...");
    err_t dhcp_err = dhcp_start(&furi_netif);
    if(dhcp_err != ERR_OK) {
        FURI_LOG_E(TAG, "DHCP Start failed: %d", dhcp_err);
    } else {
        FURI_LOG_I(TAG, "DHCP Started");
    }

    // We stay alive to keep network tasks happy?
    // LwIP runs in its own thread `tcpip_thread`.
    // We can exit this thread if we allocate variables on heap or static.
    // furi_netif is static.

    // Monitor IP assignment loop (optional debug)
    while(1) {
        if(furi_netif.ip_addr.addr != 0) {
            // FURI_LOG_I(TAG, "IP Assigned: %s", ip4addr_ntoa(&furi_netif.ip_addr));
            // break?
        }
        furi_delay_ms(5000);
    }
    return 0;
}

int32_t network_service_app(void* p) {
    UNUSED(p);
    FURI_LOG_I(TAG, "Starting Network Service");

    FuriThread* thread = furi_thread_alloc();
    furi_thread_set_name(thread, "NetworkSrv");
    furi_thread_set_stack_size(thread, 4096);
    furi_thread_set_callback(thread, network_service_thread);
    furi_thread_start(thread);

    // We don't join, we let it run as a daemon thread?
    // But this app entry point returns.
    // Ideally we should block or return differently.
    // Services usually run their own event loop or spawn a thread and exit if allowed?
    // Looking at `power` or `bt`, they often run an event loop in the main thread.

    // Since we just want to init LwIP, spawning a thread and returning 0 is risky if the robust systems kills child threads?
    // But LwIP creates `tcpip_thread`.
    // Let's assume for now we keep this thread running.

    furi_thread_join(thread);
    furi_thread_free(thread);
    return 0;
}
