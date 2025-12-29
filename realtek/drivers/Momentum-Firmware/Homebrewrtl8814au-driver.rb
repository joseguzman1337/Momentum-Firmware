cask "rtl8814au-driver" do
  version "1.0.0"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"

  url "https://github.com/yourusername/rtl8814au-macos/releases/download/v#{version}/RTL8814AUDriver-Release.tar.gz"
  name "RTL8814AU Driver"
  desc "Open-source DriverKit driver for Realtek RTL8814AU USB WiFi adapters"
  homepage "https://github.com/yourusername/rtl8814au-macos"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on macos: ">= :sequoia"

  pkg "Distribution/RTL8814AUDriver.dext"

  postflight do
    system_command "/usr/bin/systemextensionsctl",
                   args: ["list"],
                   sudo: false

    puts <<~EOS
      ======================================
      RTL8814AU Driver Installed
      ======================================

      IMPORTANT: You must approve the system extension:

      1. Open System Settings → Privacy & Security
      2. Scroll down to the Security section
      3. Click "Allow" next to the RTL8814AU Driver extension
      4. Restart your Mac
      5. Connect your RTL8814AU device

      To check the driver status:
        systemextensionsctl list

      To view driver logs:
        log stream --predicate 'subsystem == "com.opensource.RTL8814AUDriver"'

      Troubleshooting:
        https://github.com/yourusername/rtl8814au-macos/wiki/Troubleshooting

    EOS
  end

  uninstall_preflight do
    system_command "/usr/bin/systemextensionsctl",
                   args: ["uninstall", "com.opensource.RTL8814AUDriver", "com.opensource.RTL8814AUDriver"],
                   sudo: true
  end

  uninstall delete: [
    "/Library/SystemExtensions/*/com.opensource.RTL8814AUDriver.dext",
  ]

  zap trash: [
    "~/Library/Caches/com.opensource.RTL8814AUDriver",
    "~/Library/Preferences/com.opensource.RTL8814AUDriver.plist",
    "~/Library/Saved Application State/com.opensource.RTL8814AUDriver.savedState",
  ]

  caveats <<~EOS
    This driver requires System Integrity Protection (SIP) to be enabled.
    
    To check SIP status:
      csrutil status
    
    The driver uses DriverKit and is compatible with macOS Sequoia with SIP enabled.
    
    For more information and support:
      https://github.com/yourusername/rtl8814au-macos
  EOS
end
