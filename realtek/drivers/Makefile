# RTL88xxAU macOS DriverKit Makefile
# Copyright (c) 2024 Realtek

# Configuration
APP_NAME = RTLLoader
DEXT_NAME = com.realtek.driver
BUILD_DIR = build
DRIVERKIT_DIR = driverkit
ARCH = arm64 x86_64
CERT_ID = "Apple Development: ipartner@gmail.com (5VFBH8ZDF6)"

# Paths
APP_BUNDLE = $(BUILD_DIR)/$(APP_NAME).app
DEXT_BUNDLE = $(APP_BUNDLE)/Contents/Library/SystemExtensions/$(DEXT_NAME).dext
SDK_PATH = $(shell xcrun --show-sdk-path)

all: app

clean:
	rm -rf $(BUILD_DIR)

# 1. Build the DriverKit Extension (Manual Clang Build)
dext:
	mkdir -p $(BUILD_DIR)/dext/$(DEXT_NAME).dext/Contents/MacOS
	
	# Compile and Link the Dext
	# We use -target arm64-apple-driverkit19.0 (macOS 12.0 equiv)
	# And link against DriverKit properties
	# -nostdlib required as DriverKit has its own runtime
	clang++ -std=c++17 -target arm64-apple-driverkit19.0 \
		-isysroot $(shell xcrun --sdk driverkit --show-sdk-path) \
		-I$(DRIVERKIT_DIR) \
		-fno-exceptions -fno-rtti -nostdlib \
		-framework DriverKit \
		-framework NetworkingDriverKit \
		-framework USBDriverKit \
		-Xlinker -kext \
		$(DRIVERKIT_DIR)/RTL88xxAUUserDriver.cpp \
		-o $(BUILD_DIR)/dext/$(DEXT_NAME).dext/Contents/MacOS/RTL88xxAUUserDriver
		
	# Copy Info.plist
	cp $(DRIVERKIT_DIR)/Info.plist $(BUILD_DIR)/dext/$(DEXT_NAME).dext/Contents/Info.plist

# 2. Build the Swift Loader App
app: dext
	mkdir -p $(APP_BUNDLE)/Contents/MacOS
	mkdir -p $(APP_BUNDLE)/Contents/Resources
	mkdir -p $(APP_BUNDLE)/Contents/Library/SystemExtensions
	
	# Compile Swift App
	swiftc $(DRIVERKIT_DIR)/App/Sources/Loader.swift \
		-o $(APP_BUNDLE)/Contents/MacOS/$(APP_NAME) \
		-target arm64-apple-macos12.0
		
	# Copy Info.plist
	cp $(DRIVERKIT_DIR)/App/Info.plist $(APP_BUNDLE)/Contents/Info.plist
	
	# Copy Dext into App
	cp -R $(BUILD_DIR)/dext/$(DEXT_NAME).dext $(APP_BUNDLE)/Contents/Library/SystemExtensions/
	
	# Sign the Dext (must be signed before the app)
	codesign --force --sign $(CERT_ID) \
		--options runtime \
		--timestamp \
		--entitlements $(DRIVERKIT_DIR)/kext.entitlements \
		$(APP_BUNDLE)/Contents/Library/SystemExtensions/$(DEXT_NAME).dext
		
	# Sign the App
	codesign --force --sign $(CERT_ID) \
		--options runtime \
		--timestamp \
		--entitlements $(DRIVERKIT_DIR)/App/Loader.entitlements \
		$(APP_BUNDLE)
		
	@echo "Build Complete: $(APP_BUNDLE)"

install: app
	@echo "Installing App to /Applications..."
	cp -R $(APP_BUNDLE) /Applications/
	@echo "Launching App to trigger System Extension load..."
	open /Applications/$(APP_NAME).app

.PHONY: all clean dext app install
