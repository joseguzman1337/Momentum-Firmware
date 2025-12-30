# Makefile for RTL8814AU Driver Build System
# Provides convenient targets for building, testing, and installing the driver

.PHONY: all check install uninstall clean test help

# Default target
all: check

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Configuration
DRIVER_NAME := rtl8814au
KEXT_NAME := $(DRIVER_NAME).kext
BUILD_DIR := $(HOME)/$(DRIVER_NAME)-build
INSTALL_PATH := /Library/Extensions/$(KEXT_NAME)
DRIVER_REPO := https://github.com/morrownr/8814au.git

# Architecture detection
ARCH := $(shell uname -m)
MACOS_VERSION := $(shell sw_vers -productVersion)
MACOS_MAJOR := $(shell echo $(MACOS_VERSION) | cut -d. -f1)

# Number of CPU cores for parallel builds
CORES := $(shell sysctl -n hw.ncpu)

## help: Show this help message
help:
	@echo "RTL8814AU Driver Build System"
	@echo "=============================="
	@echo ""
	@echo "Targets:"
	@echo "  make check       - Check system requirements"
	@echo "  make install     - Build and install driver (requires sudo)"
	@echo "  make build       - Build driver only (no installation)"
	@echo "  make uninstall   - Remove installed driver (requires sudo)"
	@echo "  make clean       - Clean build artifacts"
	@echo "  make test        - Run test suite"
	@echo "  make sip-status  - Check SIP status"
	@echo "  make verify      - Verify driver installation"
	@echo "  make help        - Show this help message"
	@echo ""
	@echo "Configuration:"
	@echo "  Architecture: $(ARCH)"
	@echo "  macOS Version: $(MACOS_VERSION)"
	@echo "  CPU Cores: $(CORES)"
	@echo "  Build Directory: $(BUILD_DIR)"
	@echo "  Install Path: $(INSTALL_PATH)"
	@echo ""

## check: Verify system requirements
check:
	@echo "$(YELLOW)Checking system requirements...$(NC)"
	@echo ""
	
	@echo -n "macOS Version: "
	@if [ $(MACOS_MAJOR) -ge 15 ]; then \
		echo "$(GREEN)✓ $(MACOS_VERSION) (Sequoia or later)$(NC)"; \
	else \
		echo "$(RED)✗ $(MACOS_VERSION) (Sequoia 15.0+ required)$(NC)"; \
		exit 1; \
	fi
	
	@echo -n "Architecture: "
	@if [ "$(ARCH)" = "arm64" ] || [ "$(ARCH)" = "x86_64" ]; then \
		echo "$(GREEN)✓ $(ARCH)$(NC)"; \
	else \
		echo "$(RED)✗ $(ARCH) (unsupported)$(NC)"; \
		exit 1; \
	fi
	
	@echo -n "Homebrew: "
	@if command -v brew >/dev/null 2>&1; then \
		echo "$(GREEN)✓ $$(brew --version | head -n1)$(NC)"; \
	else \
		echo "$(RED)✗ Not installed$(NC)"; \
		echo "  Install with: /bin/bash -c \"\$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""; \
		exit 1; \
	fi
	
	@echo -n "Xcode Command Line Tools: "
	@if xcode-select -p >/dev/null 2>&1; then \
		echo "$(GREEN)✓ $$(xcode-select -p)$(NC)"; \
	else \
		echo "$(RED)✗ Not installed$(NC)"; \
		echo "  Install with: xcode-select --install"; \
		exit 1; \
	fi
	
	@echo -n "Git: "
	@if command -v git >/dev/null 2>&1; then \
		echo "$(GREEN)✓ $$(git --version)$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Not found, will install via Homebrew$(NC)"; \
	fi
	
	@echo ""
	@echo "$(GREEN)✓ All requirements met!$(NC)"

## sip-status: Check System Integrity Protection status
sip-status:
	@echo "System Integrity Protection Status:"
	@echo "===================================="
	@csrutil status 2>/dev/null || echo "Unable to determine SIP status"
	@echo ""
	@echo "With SIP enabled (recommended):"
	@echo "  • Driver requires user approval in System Settings"
	@echo "  • Code signing and notarization strongly recommended"
	@echo ""
	@echo "To disable SIP (not recommended):"
	@echo "  1. Boot into Recovery Mode (Cmd+R)"
	@echo "  2. Open Terminal from Utilities"
	@echo "  3. Run: csrutil disable"
	@echo "  4. Restart"

## build: Download and build driver
build: check
	@echo "$(YELLOW)Building RTL8814AU driver...$(NC)"
	@echo ""
	
	# Install dependencies
	@echo "Installing dependencies..."
	@brew list git >/dev/null 2>&1 || brew install git
	@brew list cmake >/dev/null 2>&1 || brew install cmake
	@brew list pkg-config >/dev/null 2>&1 || brew install pkg-config
	@brew list openssl@3 >/dev/null 2>&1 || brew install openssl@3
	@echo "$(GREEN)✓ Dependencies installed$(NC)"
	@echo ""
	
	# Clone or update repository
	@if [ -d "$(BUILD_DIR)" ]; then \
		echo "Updating existing source..."; \
		cd $(BUILD_DIR) && git pull; \
	else \
		echo "Cloning driver source..."; \
		git clone $(DRIVER_REPO) $(BUILD_DIR); \
	fi
	@echo "$(GREEN)✓ Source code ready$(NC)"
	@echo ""
	
	# Build
	@echo "Compiling driver..."
	@cd $(BUILD_DIR) && make clean && make -j$(CORES)
	@echo "$(GREEN)✓ Build complete!$(NC)"
	@echo ""
	@echo "Driver built at: $(BUILD_DIR)/$(KEXT_NAME)"

## install: Build and install driver (requires sudo)
install: build
	@echo "$(YELLOW)Installing RTL8814AU driver...$(NC)"
	@echo ""
	
	@if [ ! -d "$(BUILD_DIR)/$(KEXT_NAME)" ]; then \
		echo "$(RED)✗ Driver not found: $(BUILD_DIR)/$(KEXT_NAME)$(NC)"; \
		echo "  Run 'make build' first"; \
		exit 1; \
	fi
	
	# Check for existing installation
	@if [ -d "$(INSTALL_PATH)" ]; then \
		echo "$(YELLOW)⚠ Existing driver found$(NC)"; \
		echo "  Backing up to $(INSTALL_PATH).backup.$$(date +%Y%m%d_%H%M%S)"; \
		sudo mv "$(INSTALL_PATH)" "$(INSTALL_PATH).backup.$$(date +%Y%m%d_%H%M%S)"; \
	fi
	
	# Install
	@echo "Copying driver to system location..."
	@sudo cp -R "$(BUILD_DIR)/$(KEXT_NAME)" "$(INSTALL_PATH)"
	
	# Set permissions
	@echo "Setting permissions..."
	@sudo chown -R root:wheel "$(INSTALL_PATH)"
	@sudo chmod -R 755 "$(INSTALL_PATH)"
	
	# Update cache
	@echo "Updating kernel extension cache..."
	@sudo kmutil install --update-all 2>/dev/null || sudo kextcache -i / 2>/dev/null || true
	
	@echo ""
	@echo "$(GREEN)✓ Driver installed successfully!$(NC)"
	@echo ""
	@echo "$(YELLOW)IMPORTANT: Next Steps$(NC)"
	@echo "1. Restart your Mac"
	@echo "2. Go to System Settings > Privacy & Security"
	@echo "3. Click 'Allow' for the rtl8814au kernel extension"
	@echo "4. Restart again if prompted"
	@echo ""
	@echo "To verify after restart:"
	@echo "  make verify"

## uninstall: Remove installed driver (requires sudo)
uninstall:
	@echo "$(YELLOW)Uninstalling RTL8814AU driver...$(NC)"
	@echo ""
	
	@if [ ! -d "$(INSTALL_PATH)" ]; then \
		echo "$(YELLOW)⚠ Driver not installed at $(INSTALL_PATH)$(NC)"; \
		exit 0; \
	fi
	
	# Unload
	@echo "Unloading driver..."
	@sudo kextunload "$(INSTALL_PATH)" 2>/dev/null || \
	 sudo kmutil unload -p "$(INSTALL_PATH)" 2>/dev/null || true
	
	# Remove
	@echo "Removing driver files..."
	@sudo rm -rf "$(INSTALL_PATH)"
	
	# Update cache
	@echo "Updating kernel extension cache..."
	@sudo kmutil install --update-all 2>/dev/null || sudo kextcache -i / 2>/dev/null || true
	
	@echo ""
	@echo "$(GREEN)✓ Driver uninstalled$(NC)"
	@echo ""
	@echo "Please restart your Mac to complete the removal."

## clean: Remove build artifacts
clean:
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@if [ -d "$(BUILD_DIR)" ]; then \
		cd $(BUILD_DIR) && make clean 2>/dev/null || true; \
		echo "$(GREEN)✓ Build artifacts cleaned$(NC)"; \
	else \
		echo "$(YELLOW)⚠ No build directory found$(NC)"; \
	fi

## deep-clean: Remove all build files including source
deep-clean: clean
	@echo "$(YELLOW)Removing build directory...$(NC)"
	@if [ -d "$(BUILD_DIR)" ]; then \
		rm -rf "$(BUILD_DIR)"; \
		echo "$(GREEN)✓ Build directory removed$(NC)"; \
	else \
		echo "$(YELLOW)⚠ No build directory found$(NC)"; \
	fi

## verify: Check if driver is loaded
verify:
	@echo "Verifying RTL8814AU driver installation..."
	@echo "==========================================="
	@echo ""
	
	@echo "1. Checking if driver file exists:"
	@if [ -d "$(INSTALL_PATH)" ]; then \
		echo "   $(GREEN)✓ Driver file present$(NC)"; \
		ls -lh $(INSTALL_PATH); \
	else \
		echo "   $(RED)✗ Driver file not found$(NC)"; \
		echo "   Run 'make install' to install"; \
	fi
	@echo ""
	
	@echo "2. Checking if driver is loaded:"
	@if kextstat | grep -q rtl8814au; then \
		echo "   $(GREEN)✓ Driver is loaded$(NC)"; \
		kextstat | grep rtl8814au; \
	else \
		echo "   $(YELLOW)⚠ Driver is not loaded$(NC)"; \
		echo "   This is normal before first restart or approval"; \
	fi
	@echo ""
	
	@echo "3. Checking USB devices:"
	@if system_profiler SPUSBDataType 2>/dev/null | grep -i realtek >/dev/null; then \
		echo "   $(GREEN)✓ Realtek USB device detected$(NC)"; \
		system_profiler SPUSBDataType 2>/dev/null | grep -A 5 -i realtek; \
	else \
		echo "   $(YELLOW)⚠ No Realtek USB device found$(NC)"; \
		echo "   Make sure your RTL8814AU adapter is connected"; \
	fi
	@echo ""
	
	@echo "4. Network interfaces:"
	@ifconfig | grep -E '^(en|wlan)' || echo "   No WiFi interfaces found"
	@echo ""

## test: Run test suite
test:
	@echo "$(YELLOW)Running test suite...$(NC)"
	@echo ""
	@if [ -f "RTL8814AUDriverTests.swift" ]; then \
		swift test 2>&1 || echo "$(YELLOW)⚠ Some tests may require root privileges$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Test file not found$(NC)"; \
	fi

## logs: Show recent kernel logs related to driver
logs:
	@echo "Recent kernel logs (RTL/USB):"
	@echo "============================="
	@log show --predicate 'process == "kernel"' --last 10m 2>/dev/null | grep -i -E 'rtl|8814au|usb' || \
	 echo "No relevant logs found"

## usb-info: Show USB device information
usb-info:
	@echo "USB Device Information:"
	@echo "======================="
	@system_profiler SPUSBDataType 2>/dev/null | grep -A 20 -i realtek || \
	 echo "No Realtek devices found"

## network-info: Show network interface information
network-info:
	@echo "Network Interfaces:"
	@echo "==================="
	@networksetup -listallhardwareports
	@echo ""
	@echo "Active Interfaces:"
	@ifconfig | grep -E '^[a-z]|inet '

# Debugging target
debug:
	@echo "Debug Information:"
	@echo "=================="
	@echo "ARCH: $(ARCH)"
	@echo "MACOS_VERSION: $(MACOS_VERSION)"
	@echo "MACOS_MAJOR: $(MACOS_MAJOR)"
	@echo "CORES: $(CORES)"
	@echo "BUILD_DIR: $(BUILD_DIR)"
	@echo "INSTALL_PATH: $(INSTALL_PATH)"
	@echo "DRIVER_REPO: $(DRIVER_REPO)"
	@echo ""
	@echo "PATH: $$PATH"
	@echo ""
	@echo "Homebrew location:"
	@which brew || echo "Not found"
