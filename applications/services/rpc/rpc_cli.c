#include <toolbox/cli/cli_command.h>
#include <cli/cli_main_commands.h>
#include <cli/cli_vcp.h>
#include <furi.h>
#include "rpc_i.h"
#include <furi_hal.h>
#include <toolbox/pipe.h>
#include <toolbox/pipe_i.h>

#define TAG "RpcCli"

typedef struct {
    PipeSide* pipe;
    bool session_close_request;
    FuriSemaphore* terminate_semaphore;
} CliRpc;

#define CLI_READ_BUFFER_SIZE 64UL
// Storage reads carry up to 512 data bytes plus protobuf framing, paths, and status fields.
// Keep a conservative complete-response slot free while GUI frames are being streamed.
#define CLI_RPC_STORAGE_RESPONSE_MAX 768UL
#define CLI_RPC_CONTROL_RESERVE CLI_RPC_STORAGE_RESPONSE_MAX
// Screen frames are disposable and must never form a queue. Admit one only when the USB pipe is
// completely idle; a reliable reply that arrives immediately afterwards can then wait behind at
// most the single in-flight frame instead of an accumulated stream backlog.
#define CLI_RPC_BEST_EFFORT_BACKLOG_MAX 0UL

static void rpc_cli_send_bytes_callback(void* context, uint8_t* bytes, size_t bytes_len) {
    furi_assert(context);
    furi_assert(bytes);
    furi_assert(bytes_len > 0);
    CliRpc* cli_rpc = context;
    // Reliable replies retain the pipe's lossless backpressure semantics. Best-effort GUI
    // traffic is admitted separately and cannot consume the storage-response reserve below.
    pipe_send(cli_rpc->pipe, bytes, bytes_len);
}

static bool
    rpc_cli_send_bytes_best_effort_callback(void* context, uint8_t* bytes, size_t bytes_len) {
    furi_assert(context);
    furi_assert(bytes);
    furi_assert(bytes_len > 0);
    CliRpc* cli_rpc = context;
    const size_t spaces = pipe_spaces_available(cli_rpc->pipe);
    const size_t queued = CLI_VCP_TX_BUF_SIZE - spaces;
    // Screen frames are best-effort traffic. Preserve room for a small command response so a
    // saturated stream cannot make stop/get-info control traffic wait behind its own frames.
    if((queued > CLI_RPC_BEST_EFFORT_BACKLOG_MAX) || (spaces < bytes_len) ||
       ((spaces - bytes_len) < CLI_RPC_CONTROL_RESERVE)) {
        return false;
    }
    return pipe_try_send(cli_rpc->pipe, bytes, bytes_len) == bytes_len;
}

static void rpc_cli_session_close_callback(void* context) {
    furi_assert(context);
    CliRpc* cli_rpc = context;

    cli_rpc->session_close_request = true;
}

static void rpc_cli_session_terminated_callback(void* context) {
    furi_check(context);
    CliRpc* cli_rpc = context;

    furi_semaphore_release(cli_rpc->terminate_semaphore);
}

void rpc_cli_command_start_session(PipeSide* pipe, FuriString* args, void* context) {
    UNUSED(args);
    furi_assert(pipe);
    furi_assert(context);
    Rpc* rpc = context;

    uint32_t mem_before = memmgr_get_free_heap();
    FURI_LOG_D(TAG, "Free memory %lu", mem_before);

    furi_hal_usb_lock();
    RpcSession* rpc_session = rpc_session_open(rpc, RpcOwnerUsb);
    if(rpc_session == NULL) {
        printf("Session start error\r\n");
        furi_hal_usb_unlock();
        return;
    }

    CliRpc cli_rpc = {.pipe = pipe, .session_close_request = false};
    cli_rpc.terminate_semaphore = furi_semaphore_alloc(1, 0);
    rpc_session_set_context(rpc_session, &cli_rpc);
    rpc_session_set_send_bytes_callback(rpc_session, rpc_cli_send_bytes_callback);
    rpc_session_set_send_bytes_best_effort_callback(
        rpc_session, rpc_cli_send_bytes_best_effort_callback);
    rpc_session_set_close_callback(rpc_session, rpc_cli_session_close_callback);
    rpc_session_set_terminated_callback(rpc_session, rpc_cli_session_terminated_callback);

    uint8_t* buffer = malloc(CLI_READ_BUFFER_SIZE);
    size_t size_received = 0;

    while(1) {
        size_t to_receive = CLAMP(pipe_bytes_available(cli_rpc.pipe), CLI_READ_BUFFER_SIZE, 1UL);
        size_received = pipe_receive(cli_rpc.pipe, buffer, to_receive);
        if(size_received < to_receive || cli_rpc.session_close_request) {
            break;
        }

        if(size_received) {
            size_t fed_bytes = rpc_session_feed(rpc_session, buffer, size_received, 3000);
            (void)fed_bytes;
            furi_assert(fed_bytes == size_received);
        }
    }

    rpc_session_close(rpc_session);

    furi_check(
        furi_semaphore_acquire(cli_rpc.terminate_semaphore, FuriWaitForever) == FuriStatusOk);

    furi_semaphore_free(cli_rpc.terminate_semaphore);

    free(buffer);
    furi_hal_usb_unlock();
}
