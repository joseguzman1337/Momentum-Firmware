// Comprehensive Test Suite for Crypto Core Functions
// Migrated from ~/x/fz/ function enumeration summary

#include <string.h>
#include <inttypes.h>
#include <furi.h>
#include "../crypto_libs/crypto_core.h"

#define TAG "TestCryptoCore"

// Test Results Structure
typedef struct {
    uint32_t tests_run;
    uint32_t tests_passed;
    uint32_t tests_failed;
} test_results_t;

static test_results_t test_results = {0};

// Test Assertion Macros
#define TEST_ASSERT(condition, test_name) do { \
    test_results.tests_run++; \
    if (condition) { \
        test_results.tests_passed++; \
        FURI_LOG_I(TAG, "PASS: %s", test_name); \
    } else { \
        test_results.tests_failed++; \
        FURI_LOG_E(TAG, "FAIL: %s", test_name); \
    } \
} while(0)

#define TEST_ASSERT_TRUE(condition, test_name) TEST_ASSERT((condition), test_name)
#define TEST_ASSERT_FALSE(condition, test_name) TEST_ASSERT(!(condition), test_name)
#define TEST_ASSERT_EQUAL(expected, actual, test_name) TEST_ASSERT((expected) == (actual), test_name)
#define TEST_ASSERT_NOT_EQUAL(expected, actual, test_name) TEST_ASSERT((expected) != (actual), test_name)
#define TEST_ASSERT_MEMORY_EQUAL(expected, actual, size, test_name) TEST_ASSERT(memcmp(expected, actual, size) == 0, test_name)
#define TEST_ASSERT_MEMORY_NOT_EQUAL(expected, actual, size, test_name) TEST_ASSERT(memcmp(expected, actual, size) != 0, test_name)

// --- Random Number Generation Tests (2 test functions) ---
void test_crypto_init_rng(void) {
    FURI_LOG_I(TAG, "Testing crypto_init_rng");
    TEST_ASSERT_TRUE(crypto_init_rng(), "crypto_init_rng should return true");
}

void test_crypto_get_random_bytes(void) {
    FURI_LOG_I(TAG, "Testing crypto_get_random_bytes");
    
    uint8_t buffer[32];
    uint8_t original_buffer[32];
    
    // Fill with known pattern
    memset(buffer, 0xAB, sizeof(buffer));
    memcpy(original_buffer, buffer, sizeof(buffer));
    
    // Test successful call
    TEST_ASSERT_TRUE(crypto_get_random_bytes(buffer, sizeof(buffer)), "crypto_get_random_bytes should return true");
    
    // Buffer content should have changed
    TEST_ASSERT_MEMORY_NOT_EQUAL(buffer, original_buffer, sizeof(buffer), "Buffer should change after crypto_get_random_bytes");
    
    // Test with zero length (should succeed and do nothing)
    TEST_ASSERT_TRUE(crypto_get_random_bytes(buffer, 0), "crypto_get_random_bytes with zero length should return true");
    
    // Test with NULL buffer (should fail)
    TEST_ASSERT_FALSE(crypto_get_random_bytes(NULL, sizeof(buffer)), "crypto_get_random_bytes with NULL buffer should return false");
}

// --- Hash Function Tests (5 test functions) ---
void test_crypto_sha256(void) {
    FURI_LOG_I(TAG, "Testing crypto_sha256");
    
    uint8_t data[10] = {0};
    uint8_t digest[CRYPTO_SHA256_DIGEST_LENGTH];
    uint8_t expected_digest[CRYPTO_SHA256_DIGEST_LENGTH];
    memset(expected_digest, 0xAA, CRYPTO_SHA256_DIGEST_LENGTH);
    
    crypto_sha256(data, sizeof(data), digest);
    TEST_ASSERT_MEMORY_EQUAL(digest, expected_digest, CRYPTO_SHA256_DIGEST_LENGTH, "SHA256 stub should return expected pattern");
}

void test_crypto_keccak256(void) {
    FURI_LOG_I(TAG, "Testing crypto_keccak256");
    
    uint8_t data[10] = {0};
    uint8_t digest[CRYPTO_KECCAK256_DIGEST_LENGTH];
    uint8_t expected_digest[CRYPTO_KECCAK256_DIGEST_LENGTH];
    memset(expected_digest, 0xBB, CRYPTO_KECCAK256_DIGEST_LENGTH);
    
    crypto_keccak256(data, sizeof(data), digest);
    TEST_ASSERT_MEMORY_EQUAL(digest, expected_digest, CRYPTO_KECCAK256_DIGEST_LENGTH, "Keccak256 stub should return expected pattern");
}

void test_crypto_ripemd160(void) {
    FURI_LOG_I(TAG, "Testing crypto_ripemd160");
    
    uint8_t data[10] = {0};
    uint8_t digest[CRYPTO_RIPEMD160_DIGEST_LENGTH];
    uint8_t expected_digest[CRYPTO_RIPEMD160_DIGEST_LENGTH];
    memset(expected_digest, 0xCC, CRYPTO_RIPEMD160_DIGEST_LENGTH);
    
    crypto_ripemd160(data, sizeof(data), digest);
    TEST_ASSERT_MEMORY_EQUAL(digest, expected_digest, CRYPTO_RIPEMD160_DIGEST_LENGTH, "RIPEMD160 stub should return expected pattern");
}

void test_crypto_hmac_sha512(void) {
    FURI_LOG_I(TAG, "Testing crypto_hmac_sha512");
    
    uint8_t key[10] = {0};
    uint8_t data[10] = {0};
    uint8_t digest[CRYPTO_HMAC_SHA512_DIGEST_LENGTH];
    uint8_t expected_digest[CRYPTO_HMAC_SHA512_DIGEST_LENGTH];
    memset(expected_digest, 0xDD, CRYPTO_HMAC_SHA512_DIGEST_LENGTH);
    
    crypto_hmac_sha512(key, sizeof(key), data, sizeof(data), digest);
    TEST_ASSERT_MEMORY_EQUAL(digest, expected_digest, CRYPTO_HMAC_SHA512_DIGEST_LENGTH, "HMAC-SHA512 stub should return expected pattern");
}

void test_crypto_hash160(void) {
    FURI_LOG_I(TAG, "Testing crypto_hash160");
    
    uint8_t data[10] = {0};
    uint8_t digest[CRYPTO_RIPEMD160_DIGEST_LENGTH];
    uint8_t expected_digest[CRYPTO_RIPEMD160_DIGEST_LENGTH];
    memset(expected_digest, 0xEE, CRYPTO_RIPEMD160_DIGEST_LENGTH);
    
    crypto_hash160(data, sizeof(data), digest);
    TEST_ASSERT_MEMORY_EQUAL(digest, expected_digest, CRYPTO_RIPEMD160_DIGEST_LENGTH, "HASH160 stub should return expected pattern");
}

// --- Elliptic Curve Cryptography Tests (4 test functions) ---
void test_crypto_generate_keypair(void) {
    FURI_LOG_I(TAG, "Testing crypto_generate_keypair");
    
    private_key_t priv_key;
    public_key_t pub_key;
    
    // Stub always returns false
    TEST_ASSERT_FALSE(crypto_generate_keypair(&priv_key, &pub_key), "crypto_generate_keypair stub should return false");
}

void test_crypto_sign_digest(void) {
    FURI_LOG_I(TAG, "Testing crypto_sign_digest");
    
    private_key_t priv_key;
    uint8_t digest[CRYPTO_SHA256_DIGEST_LENGTH] = {0};
    uint8_t signature[CRYPTO_EC_SIGNATURE_LENGTH];
    int recid;
    
    // Stub always returns false
    TEST_ASSERT_FALSE(crypto_sign_digest(&priv_key, digest, signature, &recid), "crypto_sign_digest stub should return false");
}

void test_crypto_verify_signature(void) {
    FURI_LOG_I(TAG, "Testing crypto_verify_signature");
    
    public_key_t pub_key;
    uint8_t digest[CRYPTO_SHA256_DIGEST_LENGTH] = {0};
    uint8_t signature[CRYPTO_EC_SIGNATURE_LENGTH] = {0};
    
    // Stub always returns false
    TEST_ASSERT_FALSE(crypto_verify_signature(&pub_key, digest, signature), "crypto_verify_signature stub should return false");
}

void test_crypto_derive_public_key(void) {
    FURI_LOG_I(TAG, "Testing crypto_derive_public_key");
    
    private_key_t priv_key;
    public_key_t pub_key;
    
    // Stub returns true and fills public key with pattern
    TEST_ASSERT_TRUE(crypto_derive_public_key(&priv_key, &pub_key), "crypto_derive_public_key stub should return true");
    
    // Check that it marked as uncompressed
    if (CRYPTO_EC_PUBLIC_KEY_LENGTH > 0) {
        TEST_ASSERT_EQUAL(0x04, pub_key.bytes[0], "Public key should be marked as uncompressed (0x04)");
    }
}

// --- AES Encryption/Decryption Tests (2 test functions) ---
void test_crypto_aes256_encrypt(void) {
    FURI_LOG_I(TAG, "Testing crypto_aes256_encrypt");
    
    uint8_t plaintext[16] = {0};
    uint8_t key[32] = {0};
    uint8_t iv[16] = {0};
    uint8_t ciphertext[32];
    size_t ct_len = 0;
    
    crypto_aes256_encrypt(plaintext, sizeof(plaintext), key, iv, ciphertext, &ct_len);
    TEST_ASSERT_EQUAL(0, ct_len, "AES256 encrypt stub should set ct_len to 0");
}

void test_crypto_aes256_decrypt(void) {
    FURI_LOG_I(TAG, "Testing crypto_aes256_decrypt");
    
    uint8_t ciphertext[16] = {0};
    uint8_t key[32] = {0};
    uint8_t iv[16] = {0};
    uint8_t plaintext[32];
    size_t pt_len = 0;
    
    crypto_aes256_decrypt(ciphertext, sizeof(ciphertext), key, iv, plaintext, &pt_len);
    TEST_ASSERT_EQUAL(0, pt_len, "AES256 decrypt stub should set pt_len to 0");
}

// --- Key Derivation Function Tests (1 test function) ---
void test_crypto_pbkdf2_hmac_sha256(void) {
    FURI_LOG_I(TAG, "Testing crypto_pbkdf2_hmac_sha256");
    
    char password[] = "password";
    uint8_t salt[8] = {0};
    uint32_t iterations = 2048;
    uint8_t dk[32];
    uint8_t expected_dk[32];
    memset(expected_dk, 0x55, sizeof(expected_dk));
    
    crypto_pbkdf2_hmac_sha256(password, salt, sizeof(salt), iterations, dk, sizeof(dk));
    TEST_ASSERT_MEMORY_EQUAL(dk, expected_dk, sizeof(dk), "PBKDF2-HMAC-SHA256 stub should return expected pattern");
    
    // Test with 0 dk_len (should not crash)
    crypto_pbkdf2_hmac_sha256(password, salt, sizeof(salt), iterations, dk, 0);
    // dk should remain unchanged from previous call
    TEST_ASSERT_MEMORY_EQUAL(dk, expected_dk, sizeof(dk), "PBKDF2 with 0 dk_len should not modify buffer");
    
    // Test with NULL dk and dk_len = 0 (should not crash)
    crypto_pbkdf2_hmac_sha256(password, salt, sizeof(salt), iterations, NULL, 0);
}

// --- Main Test Runner Functions (2 functions) ---
void run_crypto_core_tests(void) {
    FURI_LOG_I(TAG, "Starting Crypto Core Tests");
    
    // Reset test results
    memset(&test_results, 0, sizeof(test_results));
    
    // Run all tests
    test_crypto_init_rng();
    test_crypto_get_random_bytes();
    test_crypto_sha256();
    test_crypto_keccak256();
    test_crypto_ripemd160();
    test_crypto_hmac_sha512();
    test_crypto_hash160();
    test_crypto_generate_keypair();
    test_crypto_sign_digest();
    test_crypto_verify_signature();
    test_crypto_derive_public_key();
    test_crypto_aes256_encrypt();
    test_crypto_aes256_decrypt();
    test_crypto_pbkdf2_hmac_sha256();
    
    // Print results
    FURI_LOG_I(TAG, "Crypto Core Tests Complete");
    FURI_LOG_I(TAG, "Tests Run: %" PRIu32 ", Passed: %" PRIu32 ", Failed: %" PRIu32, 
               test_results.tests_run, test_results.tests_passed, test_results.tests_failed);
    
    if(test_results.tests_failed == 0) {
        FURI_LOG_I(TAG, "ALL CRYPTO CORE TESTS PASSED!");
    } else {
        FURI_LOG_E(TAG, "SOME CRYPTO CORE TESTS FAILED!");
    }
}

int test_crypto_core_main(void) {
    run_crypto_core_tests();
    return (test_results.tests_failed == 0) ? 0 : 1;
}
