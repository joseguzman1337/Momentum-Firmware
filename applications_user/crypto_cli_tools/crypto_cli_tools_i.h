#pragma once

#include <furi.h>
#include <gui/gui.h>

// Forward declarations for the application structure  
typedef struct Clibridge Clibridge;
typedef struct CryptoWallet CryptoWallet;
typedef struct SshTunnel SshTunnel;

// Entry point
int32_t crypto_cli_tools_app_main(void* p);
