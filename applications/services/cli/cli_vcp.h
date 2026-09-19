#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#define RECORD_CLI_VCP "cli_vcp"

// Shared with the USB RPC transport so best-effort traffic can account for queued bytes while
// reliable command bursts retain the full pipe capacity.
#define CLI_VCP_TX_BUF_SIZE (32UL * 1024UL)

typedef struct CliVcp CliVcp;

void cli_vcp_enable(CliVcp* cli_vcp);
void cli_vcp_disable(CliVcp* cli_vcp);
#ifdef __cplusplus
}
#endif
