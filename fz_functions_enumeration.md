# Complete Function Enumeration from ~/x/fz/

This document enumerates all functions found in the ~/x/fz/ directory, organized by category and file.

## 1. CRYPTO CORE FUNCTIONS (`flipper_zero_fap/crypto_libs/crypto_core.h/.c`)

### Random Number Generation
- `crypto_init_rng(void)` - Initialize cryptographic RNG
- `crypto_get_random_bytes(uint8_t* buffer, size_t length)` - Generate secure random bytes

### Hash Functions
- `crypto_sha256(const uint8_t* data, size_t data_len, uint8_t digest[32])` - SHA-256 hashing
- `crypto_keccak256(const uint8_t* data, size_t data_len, uint8_t digest[32])` - Keccak-256 hashing
- `crypto_ripemd160(const uint8_t* data, size_t data_len, uint8_t digest[20])` - RIPEMD-160 hashing
- `crypto_hmac_sha512(const uint8_t* key, size_t key_len, const uint8_t* data, size_t data_len, uint8_t digest[64])` - HMAC-SHA512
- `crypto_hash160(const uint8_t* data, size_t data_len, uint8_t digest[20])` - Bitcoin-style HASH160 (SHA256 then RIPEMD160)

### Elliptic Curve Cryptography (secp256k1)
- `crypto_generate_keypair(private_key_t* priv_key, public_key_t* pub_key)` - Generate EC keypair
- `crypto_sign_digest(const private_key_t* priv_key, const uint8_t digest[32], uint8_t signature[64], int* recid)` - ECDSA signing
- `crypto_verify_signature(const public_key_t* pub_key, const uint8_t digest[32], const uint8_t signature[64])` - ECDSA verification
- `crypto_derive_public_key(const private_key_t* priv_key, public_key_t* pub_key)` - Derive public key from private key

### AES Encryption/Decryption
- `crypto_aes256_encrypt(const uint8_t* plaintext, size_t pt_len, const uint8_t* key, const uint8_t* iv, uint8_t* ciphertext, size_t* ct_len)` - AES-256 encryption
- `crypto_aes256_decrypt(const uint8_t* ciphertext, size_t ct_len, const uint8_t* key, const uint8_t* iv, uint8_t* plaintext, size_t* pt_len)` - AES-256 decryption

### Key Derivation
- `crypto_pbkdf2_hmac_sha256(const char* password, const uint8_t* salt, size_t salt_len, uint32_t iterations, uint8_t* dk, size_t dk_len)` - PBKDF2-HMAC-SHA256

**Total Crypto Core Functions: 15**

## 2. HD WALLET FUNCTIONS (`flipper_zero_fap/wallet_core/hd_wallet.h/.c`)

### Wallet Lifecycle & Initialization
- `hd_wallet_init_context(WalletContext* context)` - Initialize wallet context
- `hd_wallet_is_loaded(const WalletContext* context)` - Check if wallet is loaded
- `hd_wallet_is_initialized(const WalletContext* context)` - Check if wallet is initialized
- `hd_wallet_generate_mnemonic(char* mnemonic_buffer, size_t buffer_len, uint16_t strength_bits)` - Generate BIP-39 mnemonic
- `hd_wallet_seed_from_mnemonic(WalletContext* context, const char* mnemonic, const char* passphrase)` - Derive seed from mnemonic
- `hd_wallet_load_master_seed_internals(WalletContext* context, const uint8_t decrypted_master_seed[64])` - Load wallet from decrypted seed
- `hd_wallet_unload(WalletContext* context)` - Wipe sensitive data from context

### Key Derivation (BIP-32)
- `hd_wallet_derive_child_key(const extended_key_t* parent_key, uint32_t child_index, extended_key_t* child_key)` - Derive child key
- `hd_wallet_neuter_xprv_to_xpub(const extended_key_t* xprv, extended_key_t* xpub)` - Convert private to public extended key
- `hd_wallet_derive_key_from_path(WalletContext* context, const char* path, extended_key_t* derived_key)` - Derive key from BIP-32 path

### Address Generation
- `hd_wallet_get_btc_address_from_pubkey(const public_key_t* pub_key, char* address_buffer, size_t buffer_len, bool is_testnet)` - Generate Bitcoin address
- `hd_wallet_get_eth_address_from_pubkey(const public_key_t* pub_key, char* address_buffer, size_t buffer_len)` - Generate Ethereum address
- `hd_wallet_get_public_key_from_extended_key(const extended_key_t* ext_key, public_key_t* out_pub_key)` - Extract public key from extended key
- `hd_wallet_get_private_key_from_extended_key(const extended_key_t* ext_key, private_key_t* out_priv_key)` - Extract private key from extended key

### Internal Helper Functions (Static)
- `calculate_fingerprint(const public_key_t* pub_key)` - Calculate key fingerprint
- `derive_master_key_from_seed(const uint8_t seed[64], extended_key_t* master_xprv)` - Derive master key from seed
- `bip32_ckd_priv(const extended_key_t* parent_xprv, uint32_t child_index, extended_key_t* child_xprv)` - Private child key derivation
- `bip32_ckd_pub(const extended_key_t* parent_xpub, uint32_t child_index, extended_key_t* child_xpub)` - Public child key derivation
- `bip32_neuter_to_xpub(const extended_key_t* xprv, extended_key_t* xpub)` - Internal neuter function

**Total HD Wallet Functions: 18**

## 3. CLI BRIDGE FUNCTIONS (`flipperzero-cli-bridge/`)

### CLI Control (`cli_control.h/.c`)
- `clicontrol_hijack(size_t tx_size, size_t rx_size)` - Hijack CLI control with stream buffers
- `clicontrol_unhijack(bool persist)` - Restore CLI control
- `tx_handler(const uint8_t* buffer, size_t size)` - Handle TX data
- `tx_handler_stdout(const char* buffer, size_t size)` - Handle stdout TX data
- `real_rx_handler(uint8_t* buffer, size_t size, uint32_t timeout)` - Handle RX data
- `session_init(void)` - Initialize CLI session
- `session_deinit(void)` - Deinitialize CLI session
- `session_connected(void)` - Check session connection status

### Console Output (`console_output.h/.c`)
- Functions for handling console output formatting and display

### Text Input (`text_input.h/.c`) 
- Functions for handling text input in the CLI GUI

### Main CLI GUI (`cligui_main.c/.h`)
- Main application entry point and GUI management functions

**Total CLI Bridge Functions: 8+ (plus additional GUI functions)**

## 4. PYTHON SERIAL FUNCTIONS (`lib/python/flipper_serial/`)

### FlipperBridge (`flipper_bridge.py`)
- `__init__(self, config: SerialConfig = None)` - Initialize bridge
- `connect(self)` - Establish serial connection
- `send_command(self, cmd, wait_time=1)` - Send command to Flipper
- `close(self)` - Close serial connection
- `log_event(self, message)` - Log events
- `get_device_status(self)` - Get device status
- `get_system_info(self)` - Get system information
- `get_storage_info(self)` - Get storage information
- `list_apps(self)` - List installed applications
- `is_connected(self)` - Check connection status

### FlipperSerial (`flipper_serial.py`)
- `__init__(self, config=None)` - Initialize serial interface
- `find_device(self)` - Find Flipper device automatically
- `connect(self, device_path=None)` - Connect to device
- `send_command(self, command, timeout=5.0)` - Send command with timeout
- `disconnect(self)` - Disconnect from device
- `is_connected(self)` - Check if connected
- `get_device_info(self)` - Get device information
- `list_files(self, path="/")` - List files on device
- `upload_file(self, local_path, remote_path)` - Upload file to device

### FlipperAPIServer (`flipper_api_server.py`)
- `__init__(self, host='localhost', port=8080)` - Initialize API server
- `start_server(self)` - Start HTTP API server
- `handle_status(self)` - Handle status requests
- `handle_command(self)` - Handle command execution requests
- `handle_upload(self)` - Handle file upload requests
- `handle_download(self)` - Handle file download requests
- `shutdown(self)` - Shutdown server
- `get_device_status(self)` - Get device status for API
- `execute_command(self, command)` - Execute command via API
- `upload_file_api(self, file_data, remote_path)` - Upload file via API
- `download_file_api(self, remote_path)` - Download file via API

### Common (`common.py`)
- `SerialConfig.__init__(self, ...)` - Serial configuration
- `validate_port(port)` - Validate serial port
- `get_default_port()` - Get default serial port
- `SerialError.__init__(self, message)` - Serial error handling
- `ConnectionError.__init__(self, message)` - Connection error handling
- `DeviceNotFoundError.__init__(self, message)` - Device not found error

**Total Python Serial Functions: 35**

## 5. MONITORING FUNCTIONS (`lib/python/monitoring/`)

### FlipperMonitor (`flipper_monitor.py`)
- `__init__(self, config=None)` - Initialize monitor
- `start_monitoring(self)` - Start device monitoring
- `stop_monitoring(self)` - Stop monitoring
- `check_connection(self)` - Check device connection
- `log_status(self, status)` - Log device status
- `handle_disconnect(self)` - Handle disconnect events
- `handle_reconnect(self)` - Handle reconnect events
- `get_uptime(self)` - Get monitoring uptime
- `get_connection_stats(self)` - Get connection statistics
- `save_status_history(self)` - Save status to history
- `load_status_history(self)` - Load status history
- `generate_report(self)` - Generate monitoring report
- `cleanup(self)` - Cleanup monitoring resources

### StatusHandler (`status_handler.py`)
- `__init__(self, config=None)` - Initialize status handler
- `handle_status_update(self, status)` - Handle status updates
- `get_current_status(self)` - Get current device status
- `save_status(self, status)` - Save status to storage
- `load_status(self)` - Load status from storage
- `format_status(self, status)` - Format status for display
- `validate_status(self, status)` - Validate status data
- `get_status_history(self, limit=100)` - Get status history
- `clear_status_history(self)` - Clear status history
- `export_status(self, filename)` - Export status to file
- `import_status(self, filename)` - Import status from file
- `calculate_uptime(self)` - Calculate device uptime
- `calculate_statistics(self)` - Calculate connection statistics
- `generate_status_report(self)` - Generate detailed status report
- `send_status_notification(self, status)` - Send status notifications
- `check_status_alerts(self, status)` - Check for status alerts
- `handle_status_change(self, old_status, new_status)` - Handle status changes

**Total Monitoring Functions: 30**

## 6. UTILITY FUNCTIONS (`lib/python/utils/`)

### Logging (`logging.py`)
- `setup_logger(name, log_file=None, level=logging.INFO)` - Setup logger
- `log_to_file(message, filename)` - Log message to file
- `get_logger(name)` - Get logger instance
- `configure_logging(config)` - Configure logging system
- `rotate_logs(log_dir, max_files=10)` - Rotate log files
- `parse_log_level(level_str)` - Parse log level string
- `format_log_message(level, message, timestamp=None)` - Format log message

### Configuration (`config.py`)
- `__init__(self, config_file=None)` - Initialize config
- `load_config(self, config_file)` - Load configuration file
- `save_config(self, config_file=None)` - Save configuration
- `get(self, key, default=None)` - Get configuration value
- `set(self, key, value)` - Set configuration value
- `update(self, updates)` - Update multiple config values
- `validate_config(self)` - Validate configuration
- `get_default_config(self)` - Get default configuration
- `merge_configs(self, other_config)` - Merge configurations
- `reset_to_defaults(self)` - Reset to default configuration
- `export_config(self, filename)` - Export configuration
- `import_config(self, filename)` - Import configuration
- `get_config_path(self)` - Get configuration file path

### TimeUtils (`time_utils.py`)
- `get_timestamp()` - Get current timestamp
- `format_timestamp(timestamp, format_str=None)` - Format timestamp
- `parse_timestamp(timestamp_str, format_str=None)` - Parse timestamp
- `get_elapsed_time(start_time, end_time=None)` - Calculate elapsed time
- `format_duration(seconds)` - Format duration
- `get_current_time()` - Get current time
- `sleep_until(target_time)` - Sleep until target time
- `measure_execution_time(func)` - Measure function execution time

**Total Utility Functions: 28**

## 7. SHELL FUNCTIONS (`lib/`)

### Serial Functions (`serial_functions.zsh`)
- `fzs()` - Serial connection with device detection
- `_fz_find_devices()` - Find available Flipper devices
- `_fz_verify_device()` - Verify device is Flipper Zero
- `_fz_test_serial()` - Test serial connection

### SSH Functions (`ssh_functions.zsh`)
- `fztunnel()` - Start SSH tunnel in background
- `fz()` - Main Flipper Zero command interface
- `_fz_check_ssh_key()` - Check SSH key permissions
- `_fz_retry_ssh()` - Retry SSH connection with backoff
- `_fz_tunnel_status()` - Check SSH tunnel status with timeout

### Core Functions (`core.sh`)
- `log_info()` - Log info messages
- `log_error()` - Log error messages
- `_fz_check_tunnel()` - Check tunnel status

### Manager Functions (`manager.sh`)
- `fz_manager_start()` - Start Flipper management
- `fz_cleanup()` - Cleanup function

### Logging Functions (`logging.sh`)
- `log_info()` - Info logging function
- `log_error()` - Error logging function
- `log_debug()` - Debug logging function

**Total Shell Functions: 16**

## 8. SCRIPT FUNCTIONS (Various `.sh` files)

### Tunnel Management Scripts
- `bluetooth-tunnel-manager.sh` - Bluetooth tunnel management
- `deploy-bluetooth-tunnel.sh` - Deploy bluetooth tunnel
- `manage-tunnel.sh` - General tunnel management
- `ssh_tunnel_monitor()` - Monitor SSH tunnel
- `start_bluetooth_tunnel()` - Start bluetooth tunnel
- `stop_tunnel()` - Stop tunnel connections

### Build and Deploy Scripts
- `build-macos.sh` - macOS build functions
- `deploy.sh` - Deployment functions
- `quick_deploy.sh` - Quick deployment
- `quick_smart_deploy.sh` - Smart deployment
- `real-time-build-deploy.sh` - Real-time build and deploy

### Monitoring Scripts  
- `monitor_sync.sh` - Synchronization monitoring
- `auto-tune-cpu.sh` - CPU auto-tuning
- `auto_tunnel.sh` - Automatic tunnel management

**Total Script Functions: 20+**

## 9. JAVASCRIPT FUNCTIONS (`lib/js/`)

### DOM Utilities (`common/dom_utils.js`)
- `getElementById(id)` - Get element by ID
- `getElementsByClassName(className)` - Get elements by class
- `createElement(tagName, attributes)` - Create element
- `appendChild(parent, child)` - Append child element
- `removeElement(element)` - Remove element
- `setElementText(element, text)` - Set element text
- `setElementHtml(element, html)` - Set element HTML
- `addEventListenerToElement(element, event, handler)` - Add event listener
- `removeEventListenerFromElement(element, event, handler)` - Remove event listener
- `toggleElementClass(element, className)` - Toggle CSS class
- `setElementAttribute(element, attribute, value)` - Set element attribute
- `getElementAttribute(element, attribute)` - Get element attribute
- `showElement(element)` - Show element
- `hideElement(element)` - Hide element
- `isElementVisible(element)` - Check if element is visible

### Dashboard Functions (`dashboard/dashboard.js`)
- `initializeDashboard()` - Initialize dashboard
- `updateStatus(status)` - Update status display
- `refreshData()` - Refresh dashboard data
- `handleStatusUpdate(data)` - Handle status updates
- `renderStatusCards()` - Render status cards
- `updateConnectionStatus()` - Update connection status
- Various dashboard UI update functions

### Common Functions (`common/common.js`)
- `makeApiRequest(url, options)` - Make API requests
- `formatTimestamp(timestamp)` - Format timestamps
- `showNotification(message, type)` - Show notifications

**Total JavaScript Functions: 25+**

## GRAND TOTAL FUNCTION COUNT

| Category | Function Count |
|----------|----------------|
| Crypto Core Functions | 15 |
| HD Wallet Functions | 18 |
| CLI Bridge Functions | 8+ |
| Python Serial Functions | 35 |
| Monitoring Functions | 30 |
| Utility Functions | 28 |
| Shell Functions | 16 |
| Script Functions | 20+ |
| JavaScript Functions | 25+ |

**TOTAL: 195+ Functions**

This enumeration covers all major function categories found in the ~/x/fz/ directory, representing a comprehensive Flipper Zero development toolkit with cryptographic capabilities, serial communication, monitoring, tunneling, and web interfaces.
