#pragma once

#include <furi.h>
#include "crypto_libs/crypto_core.h"

typedef struct CryptoWallet CryptoWallet;

/**
 * @brief Allocate crypto wallet instance
 * @return CryptoWallet* Pointer to allocated instance
 */
CryptoWallet* crypto_wallet_alloc(void);

/**
 * @brief Free crypto wallet instance
 * @param wallet Pointer to crypto wallet instance
 */
void crypto_wallet_free(CryptoWallet* wallet);

/**
 * @brief Generate new wallet with random mnemonic
 * @param wallet Pointer to crypto wallet instance
 * @return bool True if wallet generated successfully
 */
bool crypto_wallet_generate_new(CryptoWallet* wallet);

/**
 * @brief Restore wallet from mnemonic phrase
 * @param wallet Pointer to crypto wallet instance
 * @param mnemonic Mnemonic phrase string
 * @return bool True if wallet restored successfully
 */
bool crypto_wallet_restore_from_mnemonic(CryptoWallet* wallet, const char* mnemonic);

/**
 * @brief Get wallet mnemonic phrase
 * @param wallet Pointer to crypto wallet instance
 * @return const char* Mnemonic phrase or NULL if not initialized
 */
const char* crypto_wallet_get_mnemonic(CryptoWallet* wallet);

/**
 * @brief Get wallet address
 * @param wallet Pointer to crypto wallet instance
 * @param address Buffer to store address
 * @param address_size Size of address buffer
 * @return bool True if address retrieved successfully
 */
bool crypto_wallet_get_address(CryptoWallet* wallet, char* address, size_t address_size);

/**
 * @brief Save wallet to encrypted storage
 * @param wallet Pointer to crypto wallet instance
 * @param password Password for encryption
 * @return bool True if wallet saved successfully
 */
bool crypto_wallet_save(CryptoWallet* wallet, const char* password);

/**
 * @brief Load wallet from encrypted storage
 * @param wallet Pointer to crypto wallet instance
 * @param password Password for decryption
 * @return bool True if wallet loaded successfully
 */
bool crypto_wallet_load(CryptoWallet* wallet, const char* password);

/**
 * @brief Check if wallet is initialized
 * @param wallet Pointer to crypto wallet instance
 * @return bool True if wallet is initialized
 */
bool crypto_wallet_is_initialized(CryptoWallet* wallet);

/**
 * @brief Show wallet menu interface
 * @param wallet Pointer to crypto wallet instance
 */
void crypto_wallet_show_menu(CryptoWallet* wallet);
