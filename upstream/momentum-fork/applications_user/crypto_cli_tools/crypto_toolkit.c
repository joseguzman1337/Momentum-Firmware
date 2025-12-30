#include "crypto_toolkit.h"
#include <furi.h>
#include <string.h>

#define TAG "CryptoToolkit"

struct CryptoToolkit {
    bool initialized;
    uint32_t operations_count;
    uint32_t start_time;
};

static void crypto_toolkit_print_hex(const char* label, const uint8_t* data, size_t len);

CryptoToolkit* crypto_toolkit_alloc(void) {
    CryptoToolkit* toolkit = malloc(sizeof(CryptoToolkit));
    
    toolkit->initialized = true;
    toolkit->operations_count = 0;
    toolkit->start_time = furi_get_tick();
    
    // Initialize crypto RNG for production use
    crypto_init_rng();
    
    FURI_LOG_I(TAG, "Production crypto toolkit initialized");
    return toolkit;
}

void crypto_toolkit_free(CryptoToolkit* toolkit) {
    furi_assert(toolkit);
    
    FURI_LOG_I(TAG, "Crypto toolkit completed %lu operations", (unsigned long)toolkit->operations_count);
    free(toolkit);
}

void crypto_toolkit_run_tests(CryptoToolkit* toolkit) {
    furi_assert(toolkit);
    
    FURI_LOG_I(TAG, "=== Production Crypto Toolkit Validation ===");
    FURI_LOG_I(TAG, "Running comprehensive cryptographic validation...");
    
    // Run all validation tests
    crypto_toolkit_validate_hashes(toolkit);
    crypto_toolkit_validate_keys(toolkit);
    crypto_toolkit_validate_encryption(toolkit);
    crypto_toolkit_validate_signatures(toolkit);
    crypto_toolkit_benchmark(toolkit);
    
    uint32_t elapsed = furi_get_tick() - toolkit->start_time;
    FURI_LOG_I(TAG, "=== Crypto toolkit validation complete - %lums elapsed ===", (unsigned long)elapsed);
}

void crypto_toolkit_validate_hashes(CryptoToolkit* toolkit) {
    furi_assert(toolkit);
    
    FURI_LOG_I(TAG, "--- Hash Function Validation ---");
    
    const char* test_vectors[] = {
        "Production test vector 1",
        "Cryptographic hash validation",
        "Flipper Zero secure operations"
    };
    
    for(size_t i = 0; i < 3; i++) {
        const uint8_t* data = (const uint8_t*)test_vectors[i];
        size_t data_len = strlen(test_vectors[i]);
        
        // SHA-256 Validation
        uint8_t sha256_digest[CRYPTO_SHA256_DIGEST_LENGTH];
        crypto_sha256(data, data_len, sha256_digest);
        crypto_toolkit_print_hex("SHA-256", sha256_digest, CRYPTO_SHA256_DIGEST_LENGTH);
        toolkit->operations_count++;
        
        // Keccak-256 Validation
        uint8_t keccak256_digest[CRYPTO_KECCAK256_DIGEST_LENGTH];
        crypto_keccak256(data, data_len, keccak256_digest);
        crypto_toolkit_print_hex("Keccak-256", keccak256_digest, CRYPTO_KECCAK256_DIGEST_LENGTH);
        toolkit->operations_count++;
        
        // RIPEMD-160 Validation
        uint8_t ripemd160_digest[CRYPTO_RIPEMD160_DIGEST_LENGTH];
        crypto_ripemd160(data, data_len, ripemd160_digest);
        crypto_toolkit_print_hex("RIPEMD-160", ripemd160_digest, CRYPTO_RIPEMD160_DIGEST_LENGTH);
        toolkit->operations_count++;
        
        // HASH160 Validation (Bitcoin-style)
        uint8_t hash160_digest[CRYPTO_RIPEMD160_DIGEST_LENGTH];
        crypto_hash160(data, data_len, hash160_digest);
        crypto_toolkit_print_hex("HASH160", hash160_digest, CRYPTO_RIPEMD160_DIGEST_LENGTH);
        toolkit->operations_count++;
        
        // HMAC-SHA512 Validation
        const char* key = "production_key";
        uint8_t hmac_digest[CRYPTO_HMAC_SHA512_DIGEST_LENGTH];
        crypto_hmac_sha512((const uint8_t*)key, strlen(key), data, data_len, hmac_digest);
        crypto_toolkit_print_hex("HMAC-SHA512", hmac_digest, CRYPTO_HMAC_SHA512_DIGEST_LENGTH);
        toolkit->operations_count++;
    }
    
    FURI_LOG_I(TAG, "Hash function validation complete");
}

void crypto_toolkit_validate_keys(CryptoToolkit* toolkit) {
    furi_assert(toolkit);
    
    FURI_LOG_I(TAG, "--- Key Generation and Derivation Validation ---");
    
    for(int i = 0; i < 3; i++) {
        // Generate production keypair
        private_key_t private_key;
        public_key_t public_key;
        
        if(crypto_generate_keypair(&private_key, &public_key)) {
            crypto_toolkit_print_hex("Private Key", private_key.bytes, CRYPTO_EC_PRIVATE_KEY_LENGTH);
            crypto_toolkit_print_hex("Public Key", public_key.bytes, CRYPTO_EC_PUBLIC_KEY_LENGTH);
            FURI_LOG_I(TAG, "Keypair %d generation: VALIDATED", i + 1);
            toolkit->operations_count++;
            
            // Test public key derivation consistency
            public_key_t derived_public;
            if(crypto_derive_public_key(&private_key, &derived_public)) {
                bool keys_match = memcmp(public_key.bytes, derived_public.bytes, CRYPTO_EC_PUBLIC_KEY_LENGTH) == 0;
                FURI_LOG_I(TAG, "Key derivation consistency: %s", keys_match ? "VALIDATED" : "FAILED");
                toolkit->operations_count++;
            }
        } else {
            FURI_LOG_E(TAG, "Keypair %d generation: FAILED", i + 1);
        }
    }
    
    FURI_LOG_I(TAG, "Key validation complete");
}

void crypto_toolkit_validate_encryption(CryptoToolkit* toolkit) {
    furi_assert(toolkit);
    
    FURI_LOG_I(TAG, "--- Encryption/Decryption Validation ---");
    
    const char* test_messages[] = {
        "Production encryption test",
        "Secure AES-256 validation for Flipper Zero",
        "Cryptographic operations validation complete"
    };
    
    for(size_t i = 0; i < 3; i++) {
        const char* plaintext = test_messages[i];
        size_t pt_len = strlen(plaintext);
        
        // Generate production-grade key and IV
        uint8_t aes_key[CRYPTO_AES256_KEY_LENGTH];
        uint8_t aes_iv[CRYPTO_AES_IV_LENGTH];
        
        if(!crypto_get_random_bytes(aes_key, CRYPTO_AES256_KEY_LENGTH) ||
           !crypto_get_random_bytes(aes_iv, CRYPTO_AES_IV_LENGTH)) {
            FURI_LOG_E(TAG, "Failed to generate encryption parameters");
            continue;
        }
        
        crypto_toolkit_print_hex("AES Key", aes_key, CRYPTO_AES256_KEY_LENGTH);
        crypto_toolkit_print_hex("AES IV", aes_iv, CRYPTO_AES_IV_LENGTH);
        FURI_LOG_I(TAG, "Plaintext: %s", plaintext);
        
        // Encrypt
        uint8_t ciphertext[256];
        size_t ct_len;
        crypto_aes256_encrypt((const uint8_t*)plaintext, pt_len, aes_key, aes_iv, ciphertext, &ct_len);
        crypto_toolkit_print_hex("Ciphertext", ciphertext, ct_len);
        toolkit->operations_count++;
        
        // Decrypt
        uint8_t decrypted[256];
        size_t dec_len;
        crypto_aes256_decrypt(ciphertext, ct_len, aes_key, aes_iv, decrypted, &dec_len);
        decrypted[dec_len] = '\0';
        FURI_LOG_I(TAG, "Decrypted: %s", (char*)decrypted);
        toolkit->operations_count++;
        
        // Validate round-trip
        if(dec_len == pt_len && memcmp(plaintext, decrypted, pt_len) == 0) {
            FURI_LOG_I(TAG, "Encryption test %zu: VALIDATED", i + 1);
        } else {
            FURI_LOG_E(TAG, "Encryption test %zu: FAILED", i + 1);
        }
    }
    
    FURI_LOG_I(TAG, "Encryption validation complete");
}

void crypto_toolkit_validate_signatures(CryptoToolkit* toolkit) {
    furi_assert(toolkit);
    
    FURI_LOG_I(TAG, "--- Digital Signature Validation ---");
    
    const char* messages[] = {
        "Production signature validation",
        "Secure digital signatures on Flipper Zero",
        "Cryptographic authentication complete"
    };
    
    for(size_t i = 0; i < 3; i++) {
        // Generate signing keypair
        private_key_t signing_key;
        public_key_t verify_key;
        
        if(!crypto_generate_keypair(&signing_key, &verify_key)) {
            FURI_LOG_E(TAG, "Failed to generate signing keypair");
            continue;
        }
        
        const char* message = messages[i];
        uint8_t message_hash[CRYPTO_SHA256_DIGEST_LENGTH];
        crypto_sha256((const uint8_t*)message, strlen(message), message_hash);
        
        FURI_LOG_I(TAG, "Message: %s", message);
        crypto_toolkit_print_hex("Message Hash", message_hash, CRYPTO_SHA256_DIGEST_LENGTH);
        
        // Generate signature
        uint8_t signature[CRYPTO_EC_SIGNATURE_LENGTH];
        int recovery_id;
        
        if(crypto_sign_digest(&signing_key, message_hash, signature, &recovery_id)) {
            crypto_toolkit_print_hex("Signature", signature, CRYPTO_EC_SIGNATURE_LENGTH);
            FURI_LOG_I(TAG, "Recovery ID: %d", recovery_id);
            toolkit->operations_count++;
            
            // Verify signature
            if(crypto_verify_signature(&verify_key, message_hash, signature)) {
                FURI_LOG_I(TAG, "Signature %zu verification: VALIDATED", i + 1);
                toolkit->operations_count++;
                
                // Test invalid signature detection
                uint8_t wrong_hash[CRYPTO_SHA256_DIGEST_LENGTH];
                crypto_sha256((const uint8_t*)"Wrong message", 13, wrong_hash);
                
                if(!crypto_verify_signature(&verify_key, wrong_hash, signature)) {
                    FURI_LOG_I(TAG, "Invalid signature detection: VALIDATED");
                } else {
                    FURI_LOG_E(TAG, "Invalid signature detection: FAILED");
                }
            } else {
                FURI_LOG_E(TAG, "Signature %zu verification: FAILED", i + 1);
            }
        } else {
            FURI_LOG_E(TAG, "Message signing: FAILED");
        }
    }
    
    // PBKDF2 Key Derivation Validation
    FURI_LOG_I(TAG, "--- Key Derivation Function Validation ---");
    const char* passwords[] = {"production_password", "secure_key_derivation", "flipper_zero_crypto"};
    const char* salts[] = {"salt_1", "crypto_salt", "secure_salt"};
    uint32_t iterations = 10000;
    
    for(size_t i = 0; i < 3; i++) {
        uint8_t derived_key[32];
        crypto_pbkdf2_hmac_sha256(passwords[i], (const uint8_t*)salts[i], strlen(salts[i]), iterations, derived_key, 32);
        crypto_toolkit_print_hex("PBKDF2 Key", derived_key, 32);
        FURI_LOG_I(TAG, "PBKDF2 %zu: pwd='%s', salt='%s', iter=%lu", i + 1, passwords[i], salts[i], (unsigned long)iterations);
        toolkit->operations_count++;
    }
    
    FURI_LOG_I(TAG, "Signature validation complete");
}

void crypto_toolkit_benchmark(CryptoToolkit* toolkit) {
    furi_assert(toolkit);
    
    FURI_LOG_I(TAG, "--- Performance Benchmark ---");
    
    uint32_t bench_start = furi_get_tick();
    const uint32_t benchmark_ops = 100;
    
    // Hash performance
    uint8_t test_data[64];
    crypto_get_random_bytes(test_data, sizeof(test_data));
    
    uint32_t hash_start = furi_get_tick();
    for(uint32_t i = 0; i < benchmark_ops; i++) {
        uint8_t digest[CRYPTO_SHA256_DIGEST_LENGTH];
        crypto_sha256(test_data, sizeof(test_data), digest);
    }
    uint32_t hash_time = furi_get_tick() - hash_start;
    
    // Key generation performance
    uint32_t keygen_start = furi_get_tick();
    for(uint32_t i = 0; i < benchmark_ops / 10; i++) {
        private_key_t priv;
        public_key_t pub;
        crypto_generate_keypair(&priv, &pub);
    }
    uint32_t keygen_time = furi_get_tick() - keygen_start;
    
    uint32_t bench_total = furi_get_tick() - bench_start;
    
    FURI_LOG_I(TAG, "Benchmark Results:");
    FURI_LOG_I(TAG, "- SHA-256 (%lu ops): %lums", (unsigned long)benchmark_ops, (unsigned long)hash_time);
    FURI_LOG_I(TAG, "- Key generation (%lu ops): %lums", (unsigned long)(benchmark_ops / 10), (unsigned long)keygen_time);
    FURI_LOG_I(TAG, "- Total benchmark time: %lums", (unsigned long)bench_total);
    
    toolkit->operations_count += benchmark_ops + (benchmark_ops / 10);
    
    FURI_LOG_I(TAG, "Performance benchmark complete");
}

static void crypto_toolkit_print_hex(const char* label, const uint8_t* data, size_t len) {
    char hex_str[256];
    char* p = hex_str;
    
    size_t max_len = (len > 32) ? 32 : len; // Limit output for readability
    
    for(size_t i = 0; i < max_len && (size_t)(p - hex_str) < sizeof(hex_str) - 3; i++) {
        p += snprintf(p, 3, "%02X", data[i]);
    }
    
    if(len > 32) {
        snprintf(p, 4, "...");
    }
    
    FURI_LOG_I(TAG, "%s: %s", label, hex_str);
}
