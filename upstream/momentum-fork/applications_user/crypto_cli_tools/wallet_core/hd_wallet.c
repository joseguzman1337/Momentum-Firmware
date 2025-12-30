// Flipper Zero FAP: HD Wallet Implementation (BIP-32, BIP-39, BIP-44) - Enhanced
// Migrated from ~/x/fz/ function enumeration summary

#include "hd_wallet.h"
#include <string.h> // For memset, memcpy, strcpy, strtok_r
#include <stdio.h>  // For snprintf, sscanf
#include <stdlib.h> // For strtoul
#include <furi.h>

// --- Internal Helper Function Prototypes (Static) (5 internal static functions) ---
// Calculates fingerprint from a public key (first 4 bytes of HASH160(pubkey))
static uint32_t calculate_fingerprint(const public_key_t* pub_key);

// Derives the master extended private key from a BIP-39 seed.
static bool derive_master_key_from_seed(const uint8_t seed[HD_WALLET_MASTER_SEED_LEN], extended_key_t* master_xprv);

// Core private child key derivation (parent_xprv -> child_xprv)
static bool bip32_ckd_priv(const extended_key_t* parent_xprv, uint32_t child_index, extended_key_t* child_xprv);

// Core public child key derivation (parent_xpub -> child_xpub, non-hardened only)
static bool bip32_ckd_pub(const extended_key_t* parent_xpub, uint32_t child_index, extended_key_t* child_xpub);

// Internal neuter function (xprv -> xpub, for the same node)
static bool bip32_neuter_to_xpub(const extended_key_t* xprv, extended_key_t* xpub);

// --- Wallet Lifecycle & Initialization (7 functions) ---
void hd_wallet_init_context(WalletContext* context) {
    if(!context) return;
    memset(context, 0, sizeof(WalletContext));
    context->is_loaded = false;
    context->is_initialized = false;
}

bool hd_wallet_is_loaded(const WalletContext* context) {
    if(!context) return false;
    return context->is_loaded;
}

bool hd_wallet_is_initialized(const WalletContext* context) {
    if(!context) return false;
    return context->is_initialized;
}

bool hd_wallet_generate_mnemonic(char* mnemonic_buffer, size_t buffer_len, uint16_t strength_bits) {
    if(!mnemonic_buffer || buffer_len == 0) return false;
    // TODO: Implement actual BIP-39 mnemonic generation using crypto_get_random_bytes and wordlist
    // For now, return a fixed dummy mnemonic based on strength
    const char* dummy_mnemonic_12 = "legal winner thank year wave sausage worth useful legal winner thank yellow"; // 12 words
    const char* dummy_mnemonic_24 = "legal winner thank year wave sausage worth useful legal winner thank legal winner thank year wave sausage worth useful legal winner thank yellow"; // 24 words

    const char* chosen_mnemonic = dummy_mnemonic_12;
    if(strength_bits == 256) { // 24 words
        chosen_mnemonic = dummy_mnemonic_24;
    } else if (strength_bits != 128) {
        // Only supporting 12 or 24 words for this stub
        memset(mnemonic_buffer, 0, buffer_len);
        return false;
    }

    strncpy(mnemonic_buffer, chosen_mnemonic, buffer_len - 1);
    mnemonic_buffer[buffer_len - 1] = '\0'; // Ensure null termination
    return true;
}

bool hd_wallet_seed_from_mnemonic(WalletContext* context, const char* mnemonic, const char* passphrase) {
    if(!context || !mnemonic) return false;

    // TODO: Implement actual BIP-39 mnemonic_to_seed which calls PBKDF2
    // crypto_pbkdf2_hmac_sha512(mnemonic, salt="mnemonic"+passphrase, iterations=2048, dklen=64)
    // For now, use a dummy seed generation.
    uint8_t dummy_salt[8]; // Dummy salt
    memset(dummy_salt, 's', sizeof(dummy_salt));
    char combined_pass[256]; // passphrase can be long
    snprintf(combined_pass, sizeof(combined_pass), "mnemonic%s", passphrase ? passphrase : "");

    // Simulate PBKDF2 by hashing the mnemonic and passphrase. This is NOT secure.
    crypto_pbkdf2_hmac_sha256(
        mnemonic, // "password"
        (const uint8_t*)combined_pass, // "salt"
        strlen(combined_pass),
        2048, // iterations
        context->master_seed,
        HD_WALLET_MASTER_SEED_LEN);

    if(!derive_master_key_from_seed(context->master_seed, &context->root_key)) {
        return false;
    }

    context->is_initialized = true;
    context->is_loaded = true; // Seed is "loaded" into context
    return true;
}

bool hd_wallet_load_master_seed_internals(WalletContext* context, const uint8_t decrypted_master_seed[HD_WALLET_MASTER_SEED_LEN]) {
    if(!context || !decrypted_master_seed) return false;
    memcpy(context->master_seed, decrypted_master_seed, HD_WALLET_MASTER_SEED_LEN);

    if(!derive_master_key_from_seed(context->master_seed, &context->root_key)) {
        return false;
    }

    context->is_initialized = true;
    context->is_loaded = true;
    return true;
}

void hd_wallet_unload(WalletContext* context) {
    if(!context) return;
    memset(context->master_seed, 0, HD_WALLET_MASTER_SEED_LEN);
    memset(&context->root_key, 0, sizeof(extended_key_t));
    context->is_loaded = false;
    // is_initialized might remain true if it was once initialized, or set to false too.
    // Let's keep it true if it was initialized, as the context structure might persist.
}

// --- Key Derivation (BIP-32) (3 functions) ---
bool hd_wallet_derive_child_key(const extended_key_t* parent_key, uint32_t child_index, extended_key_t* child_key) {
    if(!parent_key || !child_key) return false;

    if(parent_key->is_private) {
        return bip32_ckd_priv(parent_key, child_index, child_key);
    } else {
        if(child_index >= HD_WALLET_BIP32_HARDENED_OFFSET) {
            return false; // Cannot derive hardened key from public parent
        }
        return bip32_ckd_pub(parent_key, child_index, child_key);
    }
}

bool hd_wallet_neuter_xprv_to_xpub(const extended_key_t* xprv, extended_key_t* xpub) {
    if(!xprv || !xpub || !xprv->is_private) return false;
    return bip32_neuter_to_xpub(xprv, xpub);
}

bool hd_wallet_derive_key_from_path(WalletContext* context, const char* path, extended_key_t* derived_key) {
    if(!context || !path || !derived_key || !context->is_loaded) return false;

    char mutable_path[HD_WALLET_MAX_PATH_STR_LEN];
    strncpy(mutable_path, path, sizeof(mutable_path) -1);
    mutable_path[sizeof(mutable_path)-1] = '\0';

    // Check for "//" indicating an empty segment.
    if (strstr(mutable_path, "//")) {
        return false;
    }

    // Check for trailing slash if path is longer than "m" or "M".
    size_t path_len = strlen(mutable_path);
    if (path_len > 1 && mutable_path[path_len - 1] == '/') {
        return false; // Path with a trailing slash is invalid
    }

    char* saveptr; // For strtok_r
    char* segment = strtok_r(mutable_path, "/", &saveptr);

    // Path must start with 'm' or 'M'
    if(!segment || (strcmp(segment, "m") != 0 && strcmp(segment, "M") != 0)) {
        return false;
    }

    // Start with the root key
    memcpy(derived_key, &context->root_key, sizeof(extended_key_t));

    // Check if the path was just "m" or "M"
    segment = strtok_r(NULL, "/", &saveptr);
    while(segment != NULL) {
        if(strlen(segment) == 0) return false;

        char* endptr;
        long raw_index = strtol(segment, &endptr, 10);

        // Check if strtol consumed anything
        if (endptr == segment) {
            return false; // Not a number at the start
        }

        // BIP-32 indices are non-negative.
        if (raw_index < 0) {
            return false;
        }

        uint32_t parsed_child_index;

        if (*endptr == '\'') { // Hardened path component
            // Base number (before adding offset) must be < 0x80000000
            if (raw_index >= (long)HD_WALLET_BIP32_HARDENED_OFFSET) {
                return false;
            }
            parsed_child_index = (uint32_t)raw_index + HD_WALLET_BIP32_HARDENED_OFFSET;
            endptr++; // Move past apostrophe
            if (*endptr != '\0') { // Nothing should follow the apostrophe
                return false;
            }
        } else if (*endptr == '\0') { // Non-hardened
            // Number must be < 0x80000000
            if (raw_index >= (long)HD_WALLET_BIP32_HARDENED_OFFSET) {
                return false;
            }
            parsed_child_index = (uint32_t)raw_index;
        } else {
            // Characters exist after the number, but it's not an apostrophe
            return false;
        }

        extended_key_t current_parent_key;
        memcpy(&current_parent_key, derived_key, sizeof(extended_key_t));

        if(!hd_wallet_derive_child_key(&current_parent_key, parsed_child_index, derived_key)) {
            return false;
        }
        segment = strtok_r(NULL, "/", &saveptr);
    }
    return true;
}

// --- Address Generation (2 functions) ---
bool hd_wallet_get_btc_address_from_pubkey(const public_key_t* pub_key, char* address_buffer, size_t buffer_len, bool is_testnet) {
    if(!pub_key || !address_buffer || buffer_len == 0) return false;
    // TODO: Implement actual BTC address generation (P2PKH, P2WPKH etc.)
    // This involves HASH160, Base58Check encoding, Bech32 encoding.
    const char* dummy_addr = is_testnet ? "tb1dummytestbtcaddressgenerated" : "bc1dummybtcaddressgenerated";
    strncpy(address_buffer, dummy_addr, buffer_len - 1);
    address_buffer[buffer_len - 1] = '\0';
    return true;
}

bool hd_wallet_get_eth_address_from_pubkey(const public_key_t* pub_key, char* address_buffer, size_t buffer_len) {
    if(!pub_key || !address_buffer || buffer_len == 0) return false;
    // TODO: Implement actual ETH address generation
    // Keccak256(public_key_bytes_uncompressed_no_prefix (64 bytes)) -> last 20 bytes, hex encoded with "0x"
    uint8_t keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH];
    crypto_keccak256(pub_key->bytes, CRYPTO_EC_PUBLIC_KEY_LENGTH, keccak_digest);

    // Format the last 20 bytes of the digest as the Ethereum address.
    snprintf(address_buffer, buffer_len, "0x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x%02x",
        keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-20], keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-19],
        keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-18], keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-17],
        keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-16], keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-15],
        keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-14], keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-13],
        keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-12], keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-11],
        keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-10], keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-9],
        keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-8], keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-7],
        keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-6], keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-5],
        keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-4], keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-3],
        keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-2], keccak_digest[CRYPTO_KECCAK256_DIGEST_LENGTH-1]);
    return true;
}

// --- Key Extraction Helpers (2 functions) ---
bool hd_wallet_get_public_key_from_extended_key(const extended_key_t* ext_key, public_key_t* out_pub_key) {
    if(!ext_key || !out_pub_key) return false;

    if(ext_key->is_private) {
        private_key_t priv_key_temp;
        if(CRYPTO_EC_PRIVATE_KEY_LENGTH > HD_WALLET_EXT_KEY_DATA_LEN) return false; // Safety check
        memcpy(priv_key_temp.bytes, ext_key->key_data, CRYPTO_EC_PRIVATE_KEY_LENGTH);
        return crypto_derive_public_key(&priv_key_temp, out_pub_key);
    } else {
        // ext_key->key_data should be a compressed public key (33 bytes: prefix + X)
        // public_key_t from crypto_core.h is uncompressed (64 bytes: X+Y, or 65 with prefix)
        // This requires decompression or consistent format.
        // For STUB: assume out_pub_key wants uncompressed and ext_key->key_data is compressed.
        if (CRYPTO_EC_PUBLIC_KEY_LENGTH > 0) { // Typically 64 or 65
             memset(out_pub_key->bytes, 0, CRYPTO_EC_PUBLIC_KEY_LENGTH);
             out_pub_key->bytes[0] = 0x04; // Mark as uncompressed
             if (HD_WALLET_EXT_KEY_DATA_LEN > 1 && CRYPTO_EC_PUBLIC_KEY_LENGTH > 1) {
                memcpy(out_pub_key->bytes + 1, ext_key->key_data + 1, CRYPTO_EC_SECP256K1_PRIVATE_KEY_LENGTH); // Copy X part
             }
             // Y part would need to be derived or also copied if ext_key was uncompressed
        }
        return true; // Placeholder
    }
}

bool hd_wallet_get_private_key_from_extended_key(const extended_key_t* ext_key, private_key_t* out_priv_key) {
    if(!ext_key || !out_priv_key || !ext_key->is_private) return false;
    if(CRYPTO_EC_PRIVATE_KEY_LENGTH > HD_WALLET_EXT_KEY_DATA_LEN) return false; // Safety check

    memcpy(out_priv_key->bytes, ext_key->key_data, CRYPTO_EC_PRIVATE_KEY_LENGTH);
    return true;
}

// --- Internal Helper Function Implementations (Static) (5 functions) ---
static uint32_t calculate_fingerprint(const public_key_t* pub_key) {
    if(!pub_key) return 0;
    // TODO: Implement actual fingerprint calculation (first 4 bytes of HASH160 of compressed public key)
    uint8_t hash160_digest[CRYPTO_RIPEMD160_DIGEST_LENGTH];
    // This needs a compressed version of pub_key. Our current pub_key_t is uncompressed.
    // For STUB: Use part of the uncompressed key directly.
    crypto_hash160(pub_key->bytes, CRYPTO_EC_PUBLIC_KEY_LENGTH, hash160_digest); // This is not quite right for fingerprint

    return (uint32_t)hash160_digest[0] << 24 |
           (uint32_t)hash160_digest[1] << 16 |
           (uint32_t)hash160_digest[2] << 8  |
           (uint32_t)hash160_digest[3];
}

static bool derive_master_key_from_seed(const uint8_t seed[HD_WALLET_MASTER_SEED_LEN], extended_key_t* master_xprv) {
    if (!seed || !master_xprv) return false;
    // TODO: Implement actual BIP-32 master key derivation from seed
    // HMAC-SHA512 with key "Bitcoin seed" and data being the master seed.
    // Left half is master private key, right half is master chain code.

    uint8_t hmac_digest[CRYPTO_HMAC_SHA512_DIGEST_LENGTH];
    const char* hmac_key_str = "Bitcoin seed";
    crypto_hmac_sha512((const uint8_t*)hmac_key_str, strlen(hmac_key_str), seed, HD_WALLET_MASTER_SEED_LEN, hmac_digest);

    memset(master_xprv, 0, sizeof(extended_key_t));
    master_xprv->is_private = true;
    master_xprv->depth = 0;
    master_xprv->parent_fingerprint = 0x00000000;
    master_xprv->child_number = 0;

    memcpy(master_xprv->key_data, hmac_digest, CRYPTO_EC_PRIVATE_KEY_LENGTH); // First 32 bytes for private key
    memcpy(master_xprv->chain_code, hmac_digest + CRYPTO_EC_PRIVATE_KEY_LENGTH, HD_WALLET_CHAIN_CODE_LEN); // Next 32 for chain code

    return true;
}

static bool bip32_ckd_priv(const extended_key_t* parent_xprv, uint32_t child_index, extended_key_t* child_xprv) {
    if(!parent_xprv || !child_xprv || !parent_xprv->is_private) return false;
    // TODO: Implement actual BIP-32 private child key derivation (CKDpriv)
    // This involves HMAC-SHA512 and EC point addition/multiplication.
    memset(child_xprv, 0, sizeof(extended_key_t));
    child_xprv->is_private = true;
    child_xprv->depth = parent_xprv->depth + 1;
    public_key_t parent_pubkey_temp;
    if(hd_wallet_get_public_key_from_extended_key(parent_xprv, &parent_pubkey_temp)){
        child_xprv->parent_fingerprint = calculate_fingerprint(&parent_pubkey_temp);
    } else {
        child_xprv->parent_fingerprint = 0; // Error case
    }
    child_xprv->child_number = child_index;

    // Dummy key data
    memcpy(child_xprv->key_data, parent_xprv->key_data, CRYPTO_EC_PRIVATE_KEY_LENGTH);
    child_xprv->key_data[0] ^= (uint8_t)(child_index & 0xFF); // Vary it slightly
    memcpy(child_xprv->chain_code, parent_xprv->chain_code, HD_WALLET_CHAIN_CODE_LEN);
    child_xprv->chain_code[0] ^= (uint8_t)((child_index >> 8) & 0xFF);

    return true;
}

static bool bip32_ckd_pub(const extended_key_t* parent_xpub, uint32_t child_index, extended_key_t* child_xpub) {
    if(!parent_xpub || !child_xpub || parent_xpub->is_private) return false;
    if(child_index >= HD_WALLET_BIP32_HARDENED_OFFSET) return false; // Cannot derive hardened from public
    // TODO: Implement actual BIP-32 public child key derivation (CKDpub)
    // HMAC-SHA512 and EC point addition/multiplication.
    memset(child_xpub, 0, sizeof(extended_key_t));
    child_xpub->is_private = false;
    child_xpub->depth = parent_xpub->depth + 1;
    public_key_t parent_pubkey_temp;
     if(hd_wallet_get_public_key_from_extended_key(parent_xpub, &parent_pubkey_temp)){ // Should directly use parent_xpub's key_data if formatted correctly
        child_xpub->parent_fingerprint = calculate_fingerprint(&parent_pubkey_temp);
    } else {
        child_xpub->parent_fingerprint = 0; // Error case
    }
    child_xpub->child_number = child_index;

    // Dummy key data for public key (33 bytes compressed)
    memcpy(child_xpub->key_data, parent_xpub->key_data, HD_WALLET_EXT_KEY_DATA_LEN);
    child_xpub->key_data[1] ^= (uint8_t)(child_index & 0xFF); // Vary X coord slightly
    memcpy(child_xpub->chain_code, parent_xpub->chain_code, HD_WALLET_CHAIN_CODE_LEN);
    child_xpub->chain_code[0] ^= (uint8_t)((child_index >> 8) & 0xFF);

    return true;
}

static bool bip32_neuter_to_xpub(const extended_key_t* xprv, extended_key_t* xpub) {
    if(!xprv || !xpub || !xprv->is_private) return false;
    // TODO: Implement actual neutering: derive public key from xprv->key_data
    // The public key becomes xpub->key_data (compressed, 33 bytes).
    // Other fields (chain_code, depth, fingerprint, child_number) are copied.

    public_key_t temp_pub_key;
    private_key_t temp_priv_key;
    memcpy(temp_priv_key.bytes, xprv->key_data, CRYPTO_EC_PRIVATE_KEY_LENGTH);

    if(!crypto_derive_public_key(&temp_priv_key, &temp_pub_key)) {
        return false;
    }

    // Assuming temp_pub_key.bytes is uncompressed (0x04 + X + Y) = 65 bytes
    // And xpub->key_data needs to be compressed (prefix 0x02/0x03 + X) = 33 bytes
    // This part is complex and requires EC math to get the compressed form.
    // For STUB:
    xpub->key_data[0] = (temp_pub_key.bytes[CRYPTO_EC_PUBLIC_KEY_LENGTH-1] % 2 == 0) ? 0x02 : 0x03; // Parity for compressed
    if (CRYPTO_EC_PUBLIC_KEY_LENGTH == 65) { // If temp_pub_key.bytes includes 0x04 prefix
         memcpy(xpub->key_data + 1, temp_pub_key.bytes + 1, CRYPTO_EC_SECP256K1_PRIVATE_KEY_LENGTH); // Copy X part
    } else { // Assuming temp_pub_key.bytes is 64 bytes (X+Y)
         memcpy(xpub->key_data + 1, temp_pub_key.bytes, CRYPTO_EC_SECP256K1_PRIVATE_KEY_LENGTH); // Copy X part
    }

    memcpy(xpub->chain_code, xprv->chain_code, HD_WALLET_CHAIN_CODE_LEN);
    xpub->depth = xprv->depth;
    xpub->parent_fingerprint = xprv->parent_fingerprint;
    xpub->child_number = xprv->child_number;
    xpub->is_private = false;

    return true;
}
