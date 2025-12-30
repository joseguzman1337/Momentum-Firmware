#include "crypto_wallet.h"
#include <furi.h>
#include <furi_hal_random.h>
#include <storage/storage.h>

#define TAG "CryptoWallet"
#define WALLET_FILE_PATH APP_DATA_PATH("crypto_wallet.dat")
#define MNEMONIC_WORDS 12
#define MAX_SEED_SIZE 64
#define MAX_KEY_SIZE 32

// BIP39 word list (simplified - first 12 words for demo)
static const char* bip39_words[] = {
    "abandon", "ability", "able", "about", "above", "absent",
    "absorb", "abstract", "absurd", "abuse", "access", "accident"
};

struct CryptoWallet {
    bool initialized;
    uint8_t seed[MAX_SEED_SIZE];
    private_key_t private_key;
    public_key_t public_key;
    char mnemonic[256];
    Storage* storage;
    File* wallet_file;
};

static void crypto_wallet_generate_mnemonic(CryptoWallet* wallet);
static bool crypto_wallet_derive_keys(CryptoWallet* wallet);
static void crypto_wallet_simple_hash(const uint8_t* input, size_t input_len, uint8_t* output);

CryptoWallet* crypto_wallet_alloc() {
    CryptoWallet* wallet = malloc(sizeof(CryptoWallet));
    
    wallet->initialized = false;
    memset(wallet->seed, 0, sizeof(wallet->seed));
    memset(&wallet->private_key, 0, sizeof(wallet->private_key));
    memset(&wallet->public_key, 0, sizeof(wallet->public_key));
    memset(wallet->mnemonic, 0, sizeof(wallet->mnemonic));
    
    wallet->storage = furi_record_open(RECORD_STORAGE);
    wallet->wallet_file = storage_file_alloc(wallet->storage);
    
    return wallet;
}

void crypto_wallet_free(CryptoWallet* wallet) {
    furi_assert(wallet);
    
    if(wallet->wallet_file) {
        storage_file_free(wallet->wallet_file);
    }
    
    if(wallet->storage) {
        furi_record_close(RECORD_STORAGE);
    }
    
    // Clear sensitive data
    memset(wallet->seed, 0, sizeof(wallet->seed));
    memset(&wallet->private_key, 0, sizeof(wallet->private_key));
    memset(wallet->mnemonic, 0, sizeof(wallet->mnemonic));
    
    free(wallet);
}

bool crypto_wallet_generate_new(CryptoWallet* wallet) {
    furi_assert(wallet);
    
    FURI_LOG_I(TAG, "Generating new wallet");
    
    // Generate mnemonic
    crypto_wallet_generate_mnemonic(wallet);
    
    // Derive keys from mnemonic
    if(!crypto_wallet_derive_keys(wallet)) {
        FURI_LOG_E(TAG, "Failed to derive keys");
        return false;
    }
    
    wallet->initialized = true;
    
    FURI_LOG_I(TAG, "New wallet generated successfully");
    return true;
}

bool crypto_wallet_restore_from_mnemonic(CryptoWallet* wallet, const char* mnemonic) {
    furi_assert(wallet);
    furi_assert(mnemonic);
    
    FURI_LOG_I(TAG, "Restoring wallet from mnemonic");
    
    // Copy mnemonic
    strncpy(wallet->mnemonic, mnemonic, sizeof(wallet->mnemonic) - 1);
    wallet->mnemonic[sizeof(wallet->mnemonic) - 1] = '\0';
    
    // Derive keys from mnemonic
    if(!crypto_wallet_derive_keys(wallet)) {
        FURI_LOG_E(TAG, "Failed to derive keys from mnemonic");
        return false;
    }
    
    wallet->initialized = true;
    
    FURI_LOG_I(TAG, "Wallet restored successfully");
    return true;
}

const char* crypto_wallet_get_mnemonic(CryptoWallet* wallet) {
    furi_assert(wallet);
    
    if(!wallet->initialized) {
        return NULL;
    }
    
    return wallet->mnemonic;
}

bool crypto_wallet_get_address(CryptoWallet* wallet, char* address, size_t address_size) {
    furi_assert(wallet);
    furi_assert(address);
    
    if(!wallet->initialized) {
        return false;
    }
    
    // Generate Bitcoin-style address from public key hash
    uint8_t hash160[CRYPTO_RIPEMD160_DIGEST_LENGTH];
    crypto_hash160(wallet->public_key.bytes, CRYPTO_EC_PUBLIC_KEY_LENGTH, hash160);
    
    // Simple address generation using hash160
    snprintf(address, address_size, "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa%02X%02X", 
             hash160[0], hash160[1]);
    
    return true;
}

bool crypto_wallet_save(CryptoWallet* wallet, const char* password) {
    furi_assert(wallet);
    furi_assert(password);
    
    if(!wallet->initialized) {
        return false;
    }
    
    FURI_LOG_I(TAG, "Saving wallet to storage");
    
    // Create storage directory if it doesn't exist
    storage_simply_mkdir(wallet->storage, APP_DATA_PATH(""));
    
    // Open file for writing
    if(!storage_file_open(wallet->wallet_file, WALLET_FILE_PATH, FSAM_WRITE, FSOM_CREATE_ALWAYS)) {
        FURI_LOG_E(TAG, "Failed to open wallet file for writing");
        return false;
    }
    
    // Simple encryption (XOR with password hash)
    uint8_t key[32];
    crypto_wallet_simple_hash((const uint8_t*)password, strlen(password), key);
    
    // Encrypt and write mnemonic
    size_t mnemonic_len = strlen(wallet->mnemonic);
    uint8_t* encrypted_mnemonic = malloc(mnemonic_len);
    for(size_t i = 0; i < mnemonic_len; i++) {
        encrypted_mnemonic[i] = wallet->mnemonic[i] ^ key[i % 32];
    }
    
    storage_file_write(wallet->wallet_file, &mnemonic_len, sizeof(mnemonic_len));
    storage_file_write(wallet->wallet_file, encrypted_mnemonic, mnemonic_len);
    
    free(encrypted_mnemonic);
    storage_file_close(wallet->wallet_file);
    
    FURI_LOG_I(TAG, "Wallet saved successfully");
    return true;
}

bool crypto_wallet_load(CryptoWallet* wallet, const char* password) {
    furi_assert(wallet);
    furi_assert(password);
    
    FURI_LOG_I(TAG, "Loading wallet from storage");
    
    // Check if wallet file exists
    if(!storage_file_exists(wallet->storage, WALLET_FILE_PATH)) {
        FURI_LOG_W(TAG, "Wallet file does not exist");
        return false;
    }
    
    // Open file for reading
    if(!storage_file_open(wallet->wallet_file, WALLET_FILE_PATH, FSAM_READ, FSOM_OPEN_EXISTING)) {
        FURI_LOG_E(TAG, "Failed to open wallet file for reading");
        return false;
    }
    
    // Read and decrypt mnemonic
    size_t mnemonic_len;
    if(storage_file_read(wallet->wallet_file, &mnemonic_len, sizeof(mnemonic_len)) != sizeof(mnemonic_len)) {
        FURI_LOG_E(TAG, "Failed to read mnemonic length");
        storage_file_close(wallet->wallet_file);
        return false;
    }
    
    if(mnemonic_len >= sizeof(wallet->mnemonic)) {
        FURI_LOG_E(TAG, "Invalid mnemonic length");
        storage_file_close(wallet->wallet_file);
        return false;
    }
    
    uint8_t* encrypted_mnemonic = malloc(mnemonic_len);
    if(storage_file_read(wallet->wallet_file, encrypted_mnemonic, mnemonic_len) != mnemonic_len) {
        FURI_LOG_E(TAG, "Failed to read encrypted mnemonic");
        free(encrypted_mnemonic);
        storage_file_close(wallet->wallet_file);
        return false;
    }
    
    // Decrypt mnemonic
    uint8_t key[32];
    crypto_wallet_simple_hash((const uint8_t*)password, strlen(password), key);
    
    for(size_t i = 0; i < mnemonic_len; i++) {
        wallet->mnemonic[i] = encrypted_mnemonic[i] ^ key[i % 32];
    }
    wallet->mnemonic[mnemonic_len] = '\0';
    
    free(encrypted_mnemonic);
    storage_file_close(wallet->wallet_file);
    
    // Derive keys from loaded mnemonic
    if(!crypto_wallet_derive_keys(wallet)) {
        FURI_LOG_E(TAG, "Failed to derive keys from loaded mnemonic");
        return false;
    }
    
    wallet->initialized = true;
    
    FURI_LOG_I(TAG, "Wallet loaded successfully");
    return true;
}

bool crypto_wallet_is_initialized(CryptoWallet* wallet) {
    furi_assert(wallet);
    return wallet->initialized;
}

void crypto_wallet_show_menu(CryptoWallet* wallet) {
    furi_assert(wallet);
    
    FURI_LOG_I(TAG, "Showing wallet menu");
    
    if(!wallet->initialized) {
        FURI_LOG_I(TAG, "Wallet not initialized - please create or restore a wallet");
    } else {
        FURI_LOG_I(TAG, "Wallet initialized - ready for operations");
        char address[64];
        if(crypto_wallet_get_address(wallet, address, sizeof(address))) {
            FURI_LOG_I(TAG, "Wallet address: %s", address);
        }
    }
}

// Helper functions
static void crypto_wallet_generate_mnemonic(CryptoWallet* wallet) {
    furi_assert(wallet);
    
    // Generate random indices for BIP39 words
    uint32_t indices[MNEMONIC_WORDS];
    for(int i = 0; i < MNEMONIC_WORDS; i++) {
        indices[i] = furi_hal_random_get() % 12; // Use first 12 words from our limited list
    }
    
    // Build mnemonic string
    wallet->mnemonic[0] = '\0';
    for(int i = 0; i < MNEMONIC_WORDS; i++) {
        if(i > 0) {
            strcat(wallet->mnemonic, " ");
        }
        strcat(wallet->mnemonic, bip39_words[indices[i]]);
    }
    
    FURI_LOG_D(TAG, "Generated mnemonic: %s", wallet->mnemonic);
}

static bool crypto_wallet_derive_keys(CryptoWallet* wallet) {
    furi_assert(wallet);
    
    // Use PBKDF2 for proper key derivation from mnemonic
    uint8_t salt[] = "mnemonic"; // BIP39 standard salt prefix
    
    crypto_pbkdf2_hmac_sha256(
        wallet->mnemonic,
        salt,
        sizeof(salt) - 1,  // Don't include null terminator
        2048,              // Standard iteration count
        wallet->seed,
        64                 // 512-bit seed
    );
    
    // Derive private key from first 32 bytes of seed
    memcpy(wallet->private_key.bytes, wallet->seed, CRYPTO_EC_PRIVATE_KEY_LENGTH);
    
    // Derive public key from private key using proper EC math
    if(!crypto_derive_public_key(&wallet->private_key, &wallet->public_key)) {
        FURI_LOG_E(TAG, "Failed to derive public key");
        return false;
    }
    
    FURI_LOG_D(TAG, "Keys derived successfully using crypto core");
    return true;
}

static void crypto_wallet_simple_hash(const uint8_t* input, size_t input_len, uint8_t* output) {
    // Simple hash function (not cryptographically secure)
    // In real implementation, use SHA-256 or similar
    
    memset(output, 0, 32);
    
    for(size_t i = 0; i < input_len; i++) {
        output[i % 32] ^= input[i];
        output[(i * 7) % 32] ^= input[i] >> 1;
        output[(i * 13) % 32] ^= input[i] << 1;
    }
    
    // Additional mixing
    for(int round = 0; round < 3; round++) {
        for(int i = 0; i < 32; i++) {
            output[i] ^= output[(i + 1) % 32] >> 2;
            output[i] ^= output[(i + 31) % 32] << 3;
        }
    }
}
