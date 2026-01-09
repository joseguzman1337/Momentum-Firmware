# Homebrew Formula for RTL8814AU Driver
# Install with: brew install --cask rtl8814au-driver

class Rtl8814auDriver < Formula
  desc "Open-source driver for Realtek RTL8814AU WiFi adapters on macOS"
  homepage "https://github.com/morrownr/8814au"
  url "https://github.com/morrownr/8814au/archive/refs/heads/main.tar.gz"
  version "1.0.0"
  sha256 "" # Will be calculated on first install
  license "GPL-2.0"

  depends_on "cmake" => :build
  depends_on "pkg-config" => :build
  depends_on "openssl@3"
  depends_on xcode: :build
  depends_on macos: :sequoia

  # Additional resources needed
  resource "driverkit-sdk" do
    url "https://github.com/acidanthera/MacKernelSDK/archive/refs/heads/master.tar.gz"
  end

  def install
    # Set up environment
    ENV["MACOSX_DEPLOYMENT_TARGET"] = "15.0"
    ENV["ARCHS"] = Hardware::CPU.arch.to_s
    
    ohai "Building RTL8814AU driver for macOS Sequoia"
    
    # Extract kernel version
    kernel_version = `uname -r`.strip
    ohai "Kernel version: #{kernel_version}"
    
    # Check SIP status
    sip_status = `csrutil status 2>/dev/null`.strip
    opoo "SIP Status: #{sip_status}"
    
    if sip_status.include?("enabled")
      opoo "System Integrity Protection (SIP) is enabled."
      opoo "This driver requires SIP to be disabled for installation,"
      opoo "OR it must be properly signed and notarized by Apple."
    end
    
    # Download MacKernelSDK
    resource("driverkit-sdk").stage do
      (buildpath/"MacKernelSDK").install Dir["*"]
    end
    
    # Configure build for macOS
    system "make", "clean"
    
    # Create macOS-specific configuration
    (buildpath/"platform.config").write <<~EOS
      CONFIG_PLATFORM_MACOS=y
      CONFIG_PLATFORM_ARM_MAC=#{Hardware::CPU.arm? ? "y" : "n"}
      CONFIG_PLATFORM_I386_PC=#{Hardware::CPU.intel? ? "y" : "n"}
    EOS
    
    # Build the driver
    system "make",
           "-j#{ENV.make_jobs}",
           "KSRC=#{buildpath}/MacKernelSDK",
           "KVER=#{kernel_version}"
    
    # Install to Homebrew prefix
    # Note: Actual system installation requires root privileges
    prefix.install Dir["*.kext"]
    share.install "README.md" if File.exist?("README.md")
    
    # Create installation script
    (bin/"rtl8814au-install").write <<~EOS
      #!/bin/bash
      set -e
      
      echo "RTL8814AU Driver Installation Script"
      echo "====================================="
      echo ""
      
      if [[ $EUID -ne 0 ]]; then
         echo "This script must be run as root (use sudo)"
         exit 1
      fi
      
      # Check SIP
      SIP_STATUS=$(csrutil status 2>/dev/null || echo "unknown")
      echo "SIP Status: $SIP_STATUS"
      
      if [[ "$SIP_STATUS" == *"enabled"* ]]; then
        echo ""
        echo "WARNING: SIP is enabled. Installation may fail."
        echo "To disable SIP:"
        echo "  1. Restart in Recovery Mode (hold Cmd+R during boot)"
        echo "  2. Open Terminal from Utilities menu"
        echo "  3. Run: csrutil disable"
        echo "  4. Restart normally"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
          exit 1
        fi
      fi
      
      # Copy kext to system location
      KEXT_NAME="rtl8814au.kext"
      KEXT_SOURCE="#{prefix}/$KEXT_NAME"
      KEXT_DEST="/Library/Extensions/$KEXT_NAME"
      
      if [ -d "$KEXT_SOURCE" ]; then
        echo "Installing $KEXT_NAME to $KEXT_DEST..."
        
        # Backup existing if present
        if [ -d "$KEXT_DEST" ]; then
          echo "Backing up existing driver..."
          mv "$KEXT_DEST" "${KEXT_DEST}.backup.$(date +%Y%m%d_%H%M%S)"
        fi
        
        # Copy new kext
        cp -R "$KEXT_SOURCE" "$KEXT_DEST"
        
        # Set proper permissions
        chown -R root:wheel "$KEXT_DEST"
        chmod -R 755 "$KEXT_DEST"
        
        echo "Driver installed successfully!"
        echo ""
        echo "Next steps:"
        echo "  1. Restart your Mac"
        echo "  2. Go to System Settings > Privacy & Security"
        echo "  3. Allow the kernel extension when prompted"
        echo "  4. Your RTL8814AU adapter should now work"
        echo ""
        echo "To verify installation:"
        echo "  kextstat | grep rtl8814au"
        
      else
        echo "ERROR: Driver file not found at $KEXT_SOURCE"
        exit 1
      fi
    EOS
    
    chmod 0755, bin/"rtl8814au-install"
    
    # Create uninstallation script
    (bin/"rtl8814au-uninstall").write <<~EOS
      #!/bin/bash
      set -e
      
      echo "RTL8814AU Driver Uninstallation Script"
      echo "======================================"
      echo ""
      
      if [[ $EUID -ne 0 ]]; then
         echo "This script must be run as root (use sudo)"
         exit 1
      fi
      
      KEXT_DEST="/Library/Extensions/rtl8814au.kext"
      
      if [ -d "$KEXT_DEST" ]; then
        echo "Unloading driver..."
        kextunload "$KEXT_DEST" 2>/dev/null || kmutil unload -p "$KEXT_DEST" 2>/dev/null || true
        
        echo "Removing driver..."
        rm -rf "$KEXT_DEST"
        
        echo "Rebuilding kernel extension cache..."
        kmutil install --update-all 2>/dev/null || kextcache -i / 2>/dev/null || true
        
        echo "Driver uninstalled successfully!"
      else
        echo "Driver not found at $KEXT_DEST"
      fi
    EOS
    
    chmod 0755, bin/"rtl8814au-uninstall"
  end

  def caveats
    <<~EOS
      ⚠️  IMPORTANT NOTES FOR MACOS SEQUOIA:
      
      1. System Integrity Protection (SIP):
         - This driver requires kernel extension loading
         - With SIP enabled, you must:
           a) Have a properly signed driver from Apple Developer Program
           b) Get the driver notarized by Apple
           c) Allow it in System Settings > Privacy & Security
         
      2. Installation Steps:
         Run the following command with sudo:
         
           sudo rtl8814au-install
         
         Then restart your Mac.
      
      3. After Restart:
         - Go to System Settings > Privacy & Security
         - Click "Allow" for the rtl8814au kernel extension
         - Your WiFi adapter should now appear in Network settings
      
      4. Verification:
         Check if the driver is loaded:
         
           kextstat | grep rtl8814au
         
      5. Uninstallation:
         To remove the driver:
         
           sudo rtl8814au-uninstall
         
      6. Troubleshooting:
         - Check system logs: log show --predicate 'process == "kernel"' --last 5m
         - Verify USB device: system_profiler SPUSBDataType
         - Check kernel extensions: kextstat
      
      ⚠️  Security Warning:
      Installing third-party kernel extensions can pose security risks.
      Only install drivers from trusted sources. This is an open-source
      driver but has not been signed by Apple.
      
      For production use, consider:
      - Purchasing Apple-certified WiFi adapters
      - Using USB WiFi adapters with native macOS support
    EOS
  end

  test do
    assert_predicate prefix/"rtl8814au.kext", :exist?, "Driver kext not found"
    assert_predicate bin/"rtl8814au-install", :exist?, "Install script not found"
    assert_predicate bin/"rtl8814au-uninstall", :exist?, "Uninstall script not found"
  end
end
