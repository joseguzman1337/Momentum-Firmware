// Flipper Zero FAP: Core Cryptographic Primitives (Enhanced Header)
// Migrated from ~/x/fz/ function enumeration summary

#pragma once

#include <stddef.h> // For size_t
#include <stdint.h>
#include <stdbool.h>
#include <furi.h>

// Define common crypto constants (e.g., curve types, hash output sizes)
#define CRYPTO_SHA256_DIGEST_LENGTH 32
#define CRYPTO_KECCAK256_DIGEST_LENGTH 32
#define CRYPTO_RIPEMD160_DIGEST_LENGTH 20
#define CRYPTO_HMAC_SHA512_DIGEST_LENGTH 64
#define CRYPTO_AES256_KEY_LENGTH 32 // 256 bits
#define CRYPTO_AES_IV_LENGTH 16     // AES block size is 128 bits (16 bytes) for CBC

// Fixed sizes for secp256k1
#define CRYPTO_EC_SECP256K1_PRIVATE_KEY_LENGTH 32
#define CRYPTO_EC_SECP256K1_PUBLIC_KEY_LENGTH 64    // X and Y coordinates (uncompressed)
#define CRYPTO_EC_SECP256K1_SIGNATURE_LENGTH 64     // r and s components

// Using these generic names now, assuming secp256k1 context for this app
#define CRYPTO_EC_PRIVATE_KEY_LENGTH CRYPTO_EC_SECP256K1_PRIVATE_KEY_LENGTH
#define CRYPTO_EC_PUBLIC_KEY_LENGTH CRYPTO_EC_SECP256K1_PUBLIC_KEY_LENGTH
#define CRYPTO_EC_SIGNATURE_LENGTH CRYPTO_EC_SECP256K1_SIGNATURE_LENGTH

// Type definitions for public/private keys
typedef struct {
    uint8_t bytes[CRYPTO_EC_PRIVATE_KEY_LENGTH];
} private_key_t;

typedef struct {
    uint8_t bytes[CRYPTO_EC_PUBLIC_KEY_LENGTH]; // Typically uncompressed: 0x04 followed by X and Y
} public_key_t;

// --- Random Number Generation (2 functions) ---
// Using Flipper Zero's hardware RNG where available, augmented with a strong PRNG
bool crypto_init_rng(void); // Returns true on success, false on failure
bool crypto_get_random_bytes(uint8_t* buffer, size_t length); // Returns true on success

// --- Hashing Functions (5 functions) ---
void crypto_sha256(const uint8_t* data, size_t data_len, uint8_t digest[CRYPTO_SHA256_DIGEST_LENGTH]);
void crypto_keccak256(const uint8_t* data, size_t data_len, uint8_t digest[CRYPTO_KECCAK256_DIGEST_LENGTH]);
void crypto_ripemd160(const uint8_t* data, size_t data_len, uint8_t digest[CRYPTO_RIPEMD160_DIGEST_LENGTH]);
void crypto_hmac_sha512(const uint8_t* key, size_t key_len, const uint8_t* data, size_t data_len, uint8_t digest[CRYPTO_HMAC_SHA512_DIGEST_LENGTH]);
// Helper for SHA256 then RIPEMD160 (common in Bitcoin for HASH160)
void crypto_hash160(const uint8_t* data, size_t data_len, uint8_t digest[CRYPTO_RIPEMD160_DIGEST_LENGTH]);

// --- Elliptic Curve Cryptography - secp256k1 (4 functions) ---
// Key pair generation
bool crypto_generate_keypair(private_key_t* priv_key, public_key_t* pub_key);

// ECDSA Signing
// Produces a compact signature (r,s) and a recovery ID.
// signature buffer should be at least CRYPTO_EC_SIGNATURE_LENGTH bytes.
bool crypto_sign_digest(const private_key_t* priv_key, const uint8_t digest[CRYPTO_SHA256_DIGEST_LENGTH], uint8_t signature[CRYPTO_EC_SIGNATURE_LENGTH], int* recid);

// ECDSA Verification (for internal sanity checks)
// signature buffer contains the compact signature (r,s).
bool crypto_verify_signature(const public_key_t* pub_key, const uint8_t digest[CRYPTO_SHA256_DIGEST_LENGTH], const uint8_t signature[CRYPTO_EC_SIGNATURE_LENGTH]);

// Public key derivation from private key
bool crypto_derive_public_key(const private_key_t* priv_key, public_key_t* pub_key);

// --- AES-256 Encryption/Decryption (2 functions) ---
// AES-256-CBC with PKCS7 padding (for secure storage)
// Note: Output buffers for ciphertext/plaintext must be large enough for data + padding.
// For encryption, ciphertext buffer should be pt_len + CRYPTO_AES_IV_LENGTH (for padding).
// For decryption, pt_len will be updated with the actual plaintext length after removing padding.
void crypto_aes256_encrypt(const uint8_t* plaintext, size_t pt_len, const uint8_t* key, const uint8_t* iv, uint8_t* ciphertext, size_t* ct_len);
void crypto_aes256_decrypt(const uint8_t* ciphertext, size_t ct_len, const uint8_t* key, const uint8_t* iv, uint8_t* plaintext, size_t* pt_len);

// --- Key Derivation Functions (1 function) ---
// Key Derivation Functions (for passphrase to encryption key)
void crypto_pbkdf2_hmac_sha256(const char* password, const uint8_t* salt, size_t salt_len, uint32_t iterations, uint8_t* dk, size_t dk_len);
