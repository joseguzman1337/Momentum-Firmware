# RTL88xxAU macOS Driver Makefile
# Copyright (c) 2024 Realtek

# Project Configuration
PROJECT_NAME = RTL88xxAU
KEXT_NAME = $(PROJECT_NAME).kext
KEXT_VERSION = 1.0.0

# Directories
SRC_DIR = src
BUILD_DIR = build
KEXT_DIR = $(SRC_DIR)/kext/$(KEXT_NAME)
# Modern macOS: install third-party kexts under /Library/Extensions instead of /System/Library/Extensions
INSTALL_DIR = /Library/Extensions

# Compiler Configuration
CC = clang
CXX = clang++
ARCH = -arch x86_64 -arch arm64
SDK = -isysroot $(shell xcrun --show-sdk-path)
MIN_VERSION = -mmacosx-version-min=12.0

# Compiler Flags
CFLAGS = $(ARCH) $(SDK) $(MIN_VERSION) -O2 -Wall -Wextra
CXXFLAGS = $(CFLAGS) -std=c++17
KEXT_FLAGS = -fno-builtin -fno-stack-protector -mno-red-zone -fno-exceptions -fno-asynchronous-unwind-tables

# Framework Paths
FRAMEWORK_PATH = -F$(shell xcrun --show-sdk-path)/System/Library/Frameworks
PRIVATE_FRAMEWORK_PATH = -F$(shell xcrun --show-sdk-path)/System/Library/PrivateFrameworks

# Include Paths (add local kext stub headers first to satisfy missing legacy kernel C++ headers)
INCLUDE_PATHS = -I$(SRC_DIR)/kextstubs \
                -I$(SRC_DIR) \
                -I$(shell xcrun --show-sdk-path)/System/Library/Frameworks/IOKit.framework/Headers \
                -I$(shell xcrun --show-sdk-path)/System/Library/Frameworks/Security.framework/Headers

# Source Files
SOURCES = $(SRC_DIR)/RTL88xxAU.cpp
OBJECTS = $(SOURCES:.cpp=.o)

# Default target
all: build

# Create build directory
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Build object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(KEXT_FLAGS) $(INCLUDE_PATHS) -c $< -o $@

# Build the kernel extension
build: $(BUILD_DIR) $(OBJECTS)
	@echo "Building RTL88xxAU kernel extension..."
	@mkdir -p $(BUILD_DIR)/$(KEXT_NAME)/Contents/MacOS
	@cp $(KEXT_DIR)/Contents/Info.plist $(BUILD_DIR)/$(KEXT_NAME)/Contents/
	
	# Link the kernel extension
	$(CXX) $(ARCH) $(SDK) -Xlinker -kext -nostdlib -lkmod -lcc_kext $(OBJECTS) \
		-o $(BUILD_DIR)/$(KEXT_NAME)/Contents/MacOS/$(PROJECT_NAME)
	
	# Set permissions
	chmod -R 755 $(BUILD_DIR)/$(KEXT_NAME)
	chmod 644 $(BUILD_DIR)/$(KEXT_NAME)/Contents/Info.plist
	
	@echo "Build complete: $(BUILD_DIR)/$(KEXT_NAME)"

# Install the kernel extension (requires root)
install: build
	@echo "Installing RTL88xxAU kernel extension..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "Installation requires root privileges. Use: sudo make install"; \
		exit 1; \
	fi
	
	# Copy to system extensions directory
	cp -R $(BUILD_DIR)/$(KEXT_NAME) $(INSTALL_DIR)/
	
	# Update kernel extension cache
	kextcache -system-caches
	
	@echo "Installation complete"

# Uninstall the kernel extension (requires root)
uninstall:
	@echo "Uninstalling RTL88xxAU kernel extension..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "Uninstallation requires root privileges. Use: sudo make uninstall"; \
		exit 1; \
	fi
	
	# Unload if loaded
	-kextunload $(INSTALL_DIR)/$(KEXT_NAME)
	
	# Remove from system
	rm -rf $(INSTALL_DIR)/$(KEXT_NAME)
	
	# Update kernel extension cache
	kextcache -system-caches
	
	@echo "Uninstallation complete"

# Load the kernel extension
load: install
	@echo "Loading RTL88xxAU kernel extension..."
	kextload $(INSTALL_DIR)/$(KEXT_NAME)
	@echo "Driver loaded"

# Unload the kernel extension
unload:
	@echo "Unloading RTL88xxAU kernel extension..."
	kextunload $(INSTALL_DIR)/$(KEXT_NAME)
	@echo "Driver unloaded"

# Test the kernel extension
test:
	@echo "Testing RTL88xxAU kernel extension..."
	kextutil -t $(BUILD_DIR)/$(KEXT_NAME)

# Clean build files
clean:
	@echo "Cleaning build files..."
	rm -rf $(BUILD_DIR)
	rm -f $(OBJECTS)
	@echo "Clean complete"

# Create installer package
package: build
	@echo "Creating installer package..."
	mkdir -p $(BUILD_DIR)/pkg/payload$(INSTALL_DIR)
	cp -R $(BUILD_DIR)/$(KEXT_NAME) $(BUILD_DIR)/pkg/payload$(INSTALL_DIR)/
	
	# Create pre-install script
	mkdir -p $(BUILD_DIR)/pkg/scripts
	echo '#!/bin/bash' > $(BUILD_DIR)/pkg/scripts/preinstall
	echo 'kextunload $(INSTALL_DIR)/$(KEXT_NAME) 2>/dev/null || true' >> $(BUILD_DIR)/pkg/scripts/preinstall
	chmod +x $(BUILD_DIR)/pkg/scripts/preinstall
	
	# Create post-install script
	echo '#!/bin/bash' > $(BUILD_DIR)/pkg/scripts/postinstall
	echo 'kextcache -system-caches' >> $(BUILD_DIR)/pkg/scripts/postinstall
	echo 'kextload $(INSTALL_DIR)/$(KEXT_NAME)' >> $(BUILD_DIR)/pkg/scripts/postinstall
	chmod +x $(BUILD_DIR)/pkg/scripts/postinstall
	
	# Build package
	pkgbuild --root $(BUILD_DIR)/pkg/payload \
			 --scripts $(BUILD_DIR)/pkg/scripts \
			 --identifier com.realtek.driver.RTL88xxAU \
			 --version $(KEXT_VERSION) \
			 $(BUILD_DIR)/RTL88xxAU-$(KEXT_VERSION).pkg
	
	@echo "Package created: $(BUILD_DIR)/RTL88xxAU-$(KEXT_VERSION).pkg"

# Build GUI application
gui:
	@echo "Building GUI installer application..."
	pip3 install -r requirements.txt
	@echo "GUI application ready: RTL88xxAU Installer.app"
	@echo "Run with: python3 installer_gui.py"
	@echo "Or double-click: RTL88xxAU Installer.app"

# Install GUI dependencies
gui-deps:
	@echo "Installing GUI dependencies..."
	pip3 install --upgrade pip
	pip3 install -r requirements.txt
	@echo "GUI dependencies installed"

# Help target
help:
	@echo "RTL88xxAU macOS Driver Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  all            - Build the kernel extension (default)"
	@echo "  build          - Build the kernel extension"
	@echo "  install        - Install the kernel extension (requires root)"
	@echo "  uninstall      - Uninstall the kernel extension (requires root)"
	@echo "  load           - Load the kernel extension"
	@echo "  unload         - Unload the kernel extension"
	@echo "  test           - Test the kernel extension"
	@echo "  package        - Create installer package"
	@echo "  gui            - Build GUI installer application"
	@echo "  gui-deps       - Install GUI dependencies"
	@echo "  driverkit-build - Build DriverKit user-space network extension (no signing)"
	@echo "  awus1900-install - Run AWUS1900 RTL8814AU installer (requires root)"
	@echo "  clean          - Clean build files"
	@echo "  help           - Show this help message"

# Build the DriverKit network extension sources (compile-only using DriverKit SDK; no signing/loading)
driverkit-build:
	@echo "Building DriverKit RTL88xxAUUserDriver (source-only, no signing, compile-only)..."
	@DRIVERKIT_SDK_PATH="$(shell xcrun --sdk driverkit --show-sdk-path)"; \
	if [ -z "$$DRIVERKIT_SDK_PATH" ]; then \
		echo "Error: DriverKit SDK not found. Ensure Xcode with DriverKit support is installed."; \
		exit 1; \
	fi; \
	mkdir -p driverkit/build; \
	$(CXX) -std=c++17 -Wall -Wextra -Idriverkit -isysroot "$$DRIVERKIT_SDK_PATH" -arch arm64 -arch x86_64 -c driverkit/RTL88xxAUUserDriver.cpp -o driverkit/build/RTL88xxAUUserDriver.o
	@echo "DriverKit source build complete: driverkit/build/RTL88xxAUUserDriver.o"

# AWUS1900 automated installer (Python kmutil-based flow)
awus1900-install:
	@echo "Running AWUS1900 (RTL8814AU) automated installer..."
	@if [ "$(shell id -u)" != "0" ]; then \
			echo "This target must be run as root. Use: sudo make awus1900-install"; \
			exit 1; \
		fi
	python3 install_awus1900_tahoe.py

.PHONY: all build install uninstall load unload test clean package gui gui-deps driverkit-build awus1900-install help
