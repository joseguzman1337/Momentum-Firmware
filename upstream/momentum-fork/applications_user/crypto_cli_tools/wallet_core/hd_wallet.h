#pragma once

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <furi.h>
#include "../crypto_libs/crypto_core.h" // For private_key_t, public_key_t, crypto constants

// --- Constants ---
#define HD_WALLET_MASTER_SEED_LEN 64      // For BIP-39 derived seed (512 bits)
#define HD_WALLET_CHAIN_CODE_LEN 32
#define HD_WALLET_MAX_PATH_STR_LEN 256
#define HD_WALLET_MAX_MNEMONIC_WORDS 24
#define HD_WALLET_MAX_ADDRESS_LEN 128     // Generous buffer for various address formats
#define HD_WALLET_BIP32_HARDENED_OFFSET 0x80000000

// BIP-32 key type (can hold either private or public extended key)
// For an xprv, key_data holds the 32-byte private key.
// For an xpub, key_data holds the 33-byte compressed public key (prefix + X coordinate).
#define HD_WALLET_EXT_KEY_DATA_LEN 33

typedef struct {
    uint8_t key_data[HD_WALLET_EXT_KEY_DATA_LEN]; // Private key (32 bytes) or Compressed Public key (33 bytes)
    uint8_t chain_code[HD_WALLET_CHAIN_CODE_LEN];
    uint8_t depth;
    uint32_t parent_fingerprint; // Fingerprint of the parent key
    uint32_t child_number;       // Child number this key was derived with
    bool is_private;             // True if key_data holds a private key, false for public
} extended_key_t;

// Main context structure for the HD wallet
typedef struct WalletContext {
    uint8_t master_seed[HD_WALLET_MASTER_SEED_LEN];
    extended_key_t root_key; // This will be the master extended private key (m) after initialization
    bool is_loaded;          // True if master_seed and root_key are decrypted and ready
    bool is_initialized;     // True if the context has been set up (e.g. via mnemonic or loaded seed)
} WalletContext;

// --- Wallet Lifecycle & Initialization (7 functions) ---
void hd_wallet_init_context(WalletContext* context);
bool hd_wallet_is_loaded(const WalletContext* context);
bool hd_wallet_is_initialized(const WalletContext* context);

// Generates a new mnemonic phrase (BIP-39)
// strength_bits: 128 for 12 words, 160 for 15, 192 for 18, 224 for 21, 256 for 24 words.
bool hd_wallet_generate_mnemonic(char* mnemonic_buffer, size_t buffer_len, uint16_t strength_bits);

// Derives master seed and root extended private key from mnemonic and passphrase (BIP-39)
// Initializes the WalletContext.
bool hd_wallet_seed_from_mnemonic(WalletContext* context, const char* mnemonic, const char* passphrase);

// Loads wallet from an (externally) decrypted master seed.
// Typically used after user enters PIN and seed is decrypted from storage.
bool hd_wallet_load_master_seed_internals(WalletContext* context, const uint8_t decrypted_master_seed[HD_WALLET_MASTER_SEED_LEN]);

// Wipes sensitive data from the context (master_seed, root_key)
void hd_wallet_unload(WalletContext* context);

// --- Key Derivation - BIP-32 (3 functions) ---

// Derives a child extended key from a parent extended key.
// Handles both private-to-private (hardened/non-hardened) and public-to-public (non-hardened only) derivation.
// If parent_key is private, child_key will be private.
// If parent_key is public, child_key will be public (child_index must not be hardened).
bool hd_wallet_derive_child_key(const extended_key_t* parent_key, uint32_t child_index, extended_key_t* child_key);

// Converts an extended private key to its corresponding extended public key.
// (N((k,c)) in BIP-32 spec)
bool hd_wallet_neuter_xprv_to_xpub(const extended_key_t* xprv, extended_key_t* xpub);

// Derives a key (private or public) for a given BIP-32 path string (e.g., "m/44'/0'/0'/0/0").
// Resulting key is stored in derived_key.
// If path starts with "m" or "M", derivation starts from context->root_key.
bool hd_wallet_derive_key_from_path(WalletContext* context, const char* path, extended_key_t* derived_key);

// --- Address Generation (2 functions) ---
// Note: These functions typically take a public_key_t (from crypto_core.h) which is derived
// from the key_data within an extended_key_t after derivation.

// Generates Bitcoin P2WPKH (SegWit) or P2PKH address from a public key.
// Needs more parameters for type (P2PKH, P2SH-P2WPKH, P2WPKH) and network (mainnet/testnet).
// For simplicity, this is a placeholder. A real version would be more complex.
bool hd_wallet_get_btc_address_from_pubkey(const public_key_t* pub_key, char* address_buffer, size_t buffer_len, bool is_testnet);

// Generates Ethereum address from a public key.
bool hd_wallet_get_eth_address_from_pubkey(const public_key_t* pub_key, char* address_buffer, size_t buffer_len);

// --- Key Extraction Helpers (2 functions) ---
// Helper to get the public_key_t from an extended_key_t (either xpub or xprv)
bool hd_wallet_get_public_key_from_extended_key(const extended_key_t* ext_key, public_key_t* out_pub_key);

// Helper to get the private_key_t from an extended_key_t (must be an xprv)
bool hd_wallet_get_private_key_from_extended_key(const extended_key_t* ext_key, private_key_t* out_priv_key);
