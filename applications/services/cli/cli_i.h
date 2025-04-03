/**
 * @file cli_i.h
 * Internal API for getting commands registered with the CLI
 */

#pragma once

#include <furi.h>
#include <m-bptree.h>
#include "cli.h"

#ifdef __cplusplus
extern "C" {
#endif

#define CLI_BUILTIN_COMMAND_STACK_SIZE (3 * 1024U)

typedef struct {
    void* context; //<! Context passed to callbacks
    CliExecuteCallback execute_callback; //<! Callback for command execution
    CliCommandFlag flags;
    size_t stack_depth;
} CliCommand;

#define CLI_COMMANDS_TREE_RANK 4

// -V:BPTREE_DEF2:1103
// -V:BPTREE_DEF2:524
BPTREE_DEF2(
    CliCommandTree,
    CLI_COMMANDS_TREE_RANK,
    FuriString*,
    FURI_STRING_OPLIST,
    CliCommand,
    M_POD_OPLIST);
#define M_OPL_CliCommandTree_t() BPTREE_OPLIST(CliCommandTree, M_POD_OPLIST)

bool cli_get_command(Cli* cli, FuriString* command, CliCommand* result);

void cli_lock_commands(Cli* cli);

void cli_unlock_commands(Cli* cli);

/**
 * @warning Surround calls to this function with `cli_[un]lock_commands`
 */
CliCommandTree_t* cli_get_commands(Cli* cli);

// CLI command wrapping to load from plugin file on SD card
// Just need to:
// - Use CLI_PLUGIN_WRAPPER("name", cmd_callback)
// - Replace callback usages with cmd_callback_wrapper
// - Add "name_cli" entry in app manifest to build as plugin
void cli_plugin_wrapper(const char* name, PipeSide* pipe, FuriString* args, void* context);
#include <flipper_application/flipper_application.h>
#define CLI_PLUGIN_APP_ID      "cli"
#define CLI_PLUGIN_API_VERSION 1
#define CLI_PLUGIN_WRAPPER(plugin_name_without_cli_suffix, cli_command_callback)           \
    void cli_command_callback##_wrapper(PipeSide* pipe, FuriString* args, void* context) { \
        cli_plugin_wrapper(plugin_name_without_cli_suffix, pipe, args, context);           \
    }                                                                                      \
    static const FlipperAppPluginDescriptor cli_command_callback##_plugin_descriptor = {   \
        .appid = CLI_PLUGIN_APP_ID,                                                        \
        .ep_api_version = CLI_PLUGIN_API_VERSION,                                          \
        .entry_point = &cli_command_callback,                                              \
    };                                                                                     \
    const FlipperAppPluginDescriptor* cli_command_callback##_plugin_ep(void) {             \
        UNUSED(cli_command_callback##_wrapper);                                            \
        return &cli_command_callback##_plugin_descriptor;                                  \
    }

#ifdef __cplusplus
}
#endif
