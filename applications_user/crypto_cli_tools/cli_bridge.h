#pragma once

#include <furi.h>

typedef struct Clibridge Clibridge;

/**
 * @brief Allocate CLI bridge instance
 * @return Clibridge* Pointer to allocated instance
 */
Clibridge* cli_bridge_alloc(void);

/**
 * @brief Free CLI bridge instance
 * @param cli_bridge Pointer to CLI bridge instance
 */
void cli_bridge_free(Clibridge* cli_bridge);

/**
 * @brief Start CLI bridge session
 * @param cli_bridge Pointer to CLI bridge instance
 * @return bool True if started successfully
 */
bool cli_bridge_start(Clibridge* cli_bridge);

/**
 * @brief Stop CLI bridge session
 * @param cli_bridge Pointer to CLI bridge instance
 * @return bool True if stopped successfully
 */
bool cli_bridge_stop(Clibridge* cli_bridge);

/**
 * @brief Execute command through CLI bridge
 * @param cli_bridge Pointer to CLI bridge instance
 * @param command Command string to execute
 * @param result FuriString to store result
 * @return bool True if command executed successfully
 */
bool cli_bridge_execute_command(Clibridge* cli_bridge, const char* command, FuriString* result);

/**
 * @brief Check if CLI bridge is active
 * @param cli_bridge Pointer to CLI bridge instance
 * @return bool True if active
 */
bool cli_bridge_is_active(Clibridge* cli_bridge);
