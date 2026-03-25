#include "cli_vcp.h"
#include <furi_hal_usb_cdc.h>
#include <furi_hal_usb_eth.h>
#include <furi_hal.h>
#include <furi.h>
#include <stdint.h>
#include <stdlib.h>
#include <toolbox/pipe.h>
#include <toolbox/cli/shell/cli_shell.h>
#include <toolbox/api_lock.h>
#include "cli_main_shell.h"
#include "cli_main_commands.h"

#define TAG "CliVcp"

#define USB_CDC_PKT_LEN   CDC_DATA_SZ
#define VCP_BUF_SIZE      (USB_CDC_PKT_LEN * 3)
#define VCP_IF_NUM        0
#define VCP_MESSAGE_Q_LEN 8

typedef struct {
    enum {
        CliVcpMessageTypeEnable,
        CliVcpMessageTypeDisable,
    } type;
    FuriApiLock api_lock;
    union {};
} CliVcpMessage;

typedef enum {
    CliVcpInternalEventConnected,
    CliVcpInternalEventDisconnected,
    CliVcpInternalEventTxDone,
    CliVcpInternalEventRx,
} CliVcpInternalEvent;

struct CliVcp {
    FuriEventLoop* event_loop;
    FuriMessageQueue* message_queue; // <! external messages
    FuriMessageQueue* internal_evt_queue;

    bool is_enabled, is_connected;
    FuriHalUsbInterface* previous_interface;

    PipeSide* own_pipe;
    PipeSide* shell_pipe;
    volatile bool is_currently_transmitting;
    size_t previous_tx_length;

    CliRegistry* main_registry;
    CliShell* shell;
};

/**
 * Processes messages arriving from other threads
 */
static void cli_vcp_message_received(FuriEventLoopObject* object, void* context) {
    UNUSED(object);
    CliVcp* cli_vcp = context;
    CliVcpMessage message;
    furi_check(furi_message_queue_get(cli_vcp->message_queue, &message, 0) == FuriStatusOk);

    switch(message.type) {
    case CliVcpMessageTypeEnable:
        if(cli_vcp->is_enabled) break;
        FURI_LOG_I(TAG, "### ENABLING USB ETHERNET ###");
        cli_vcp->is_enabled = true;

        // switch usb mode
        cli_vcp->previous_interface = furi_hal_usb_get_config();
        furi_hal_usb_unlock();
        furi_hal_usb_set_config(&usb_eth, NULL);
        furi_hal_usb_enable();
        furi_hal_usb_lock();
        break;

    case CliVcpMessageTypeDisable:
        if(!cli_vcp->is_enabled) break;
        FURI_LOG_D(TAG, "Disabling");
        cli_vcp->is_enabled = false;

        // restore usb mode
        furi_hal_usb_set_config(cli_vcp->previous_interface, NULL);
        break;
    }

    api_lock_unlock(message.api_lock);
}

/**
 * Processes messages arriving from CDC event callbacks
 */
static void cli_vcp_internal_event_happened(FuriEventLoopObject* object, void* context) {
    UNUSED(object);
    CliVcp* cli_vcp = context;
    CliVcpInternalEvent event;
    furi_check(furi_message_queue_get(cli_vcp->internal_evt_queue, &event, 0) == FuriStatusOk);
    UNUSED(cli_vcp);
    UNUSED(event);
}

// ============
// Thread stuff
// ============

static CliVcp* cli_vcp_alloc(void) {
    CliVcp* cli_vcp = malloc(sizeof(CliVcp));
    memset(cli_vcp, 0, sizeof(CliVcp));

    cli_vcp->event_loop = furi_event_loop_alloc();

    cli_vcp->message_queue = furi_message_queue_alloc(VCP_MESSAGE_Q_LEN, sizeof(CliVcpMessage));
    furi_event_loop_subscribe_message_queue(
        cli_vcp->event_loop,
        cli_vcp->message_queue,
        FuriEventLoopEventIn,
        cli_vcp_message_received,
        cli_vcp);

    cli_vcp->internal_evt_queue =
        furi_message_queue_alloc(VCP_MESSAGE_Q_LEN, sizeof(CliVcpInternalEvent));
    furi_event_loop_subscribe_message_queue(
        cli_vcp->event_loop,
        cli_vcp->internal_evt_queue,
        FuriEventLoopEventIn,
        cli_vcp_internal_event_happened,
        cli_vcp);

    cli_vcp->main_registry = furi_record_open(RECORD_CLI);

    return cli_vcp;
}

int32_t cli_vcp_srv(void* p) {
    UNUSED(p);

    if(!furi_hal_is_normal_boot()) {
        FURI_LOG_W(TAG, "Skipping start in special boot mode");
        furi_thread_suspend(furi_thread_get_current_id());
        return 0;
    }

    CliVcp* cli_vcp = cli_vcp_alloc();
    furi_record_create(RECORD_CLI_VCP, cli_vcp);
    furi_event_loop_run(cli_vcp->event_loop);

    return 0;
}

// ==========
// Public API
// ==========

static void cli_vcp_synchronous_request(CliVcp* cli_vcp, CliVcpMessage* message) {
    message->api_lock = api_lock_alloc_locked();
    furi_message_queue_put(cli_vcp->message_queue, message, FuriWaitForever);
    api_lock_wait_unlock_and_free(message->api_lock);
}

void cli_vcp_enable(CliVcp* cli_vcp) {
    furi_check(cli_vcp);
    CliVcpMessage message = {
        .type = CliVcpMessageTypeEnable,
    };
    cli_vcp_synchronous_request(cli_vcp, &message);
}

void cli_vcp_disable(CliVcp* cli_vcp) {
    furi_check(cli_vcp);
    CliVcpMessage message = {
        .type = CliVcpMessageTypeDisable,
    };
    cli_vcp_synchronous_request(cli_vcp, &message);
}
