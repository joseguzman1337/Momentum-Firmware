#pragma once

#include <furi.h>
#include "crypto_libs/crypto_core.h"

typedef struct CryptoToolkit CryptoToolkit;

/**
 * @brief Allocate crypto toolkit instance
 * @return CryptoToolkit* Pointer to allocated instance
 */
CryptoToolkit* crypto_toolkit_alloc(void);

/**
 * @brief Free crypto toolkit instance
 * @param toolkit Pointer to crypto toolkit instance
 */
void crypto_toolkit_free(CryptoToolkit* toolkit);

/**
 * @brief Run comprehensive crypto toolkit tests
 * @param toolkit Pointer to crypto toolkit instance
 */
void crypto_toolkit_run_tests(CryptoToolkit* toolkit);

/**
 * @brief Validate hash function implementations
 * @param toolkit Pointer to crypto toolkit instance
 */
void crypto_toolkit_validate_hashes(CryptoToolkit* toolkit);

/**
 * @brief Validate key generation and derivation
 * @param toolkit Pointer to crypto toolkit instance
 */
void crypto_toolkit_validate_keys(CryptoToolkit* toolkit);

/**
 * @brief Validate encryption/decryption operations
 * @param toolkit Pointer to crypto toolkit instance
 */
void crypto_toolkit_validate_encryption(CryptoToolkit* toolkit);

/**
 * @brief Validate digital signature operations
 * @param toolkit Pointer to crypto toolkit instance
 */
void crypto_toolkit_validate_signatures(CryptoToolkit* toolkit);

/**
 * @brief Benchmark cryptographic operations performance
 * @param toolkit Pointer to crypto toolkit instance
 */
void crypto_toolkit_benchmark(CryptoToolkit* toolkit);
