#pragma once

#include <furi.h>

// Test function declarations for crypto core
void run_crypto_core_tests(void);
int test_crypto_core_main(void);

// Test function declarations for HD wallet (stubs for now)
void run_hd_wallet_tests(void);
int test_hd_wallet_main(void);

// Overall test runner
void run_all_tests(void);
