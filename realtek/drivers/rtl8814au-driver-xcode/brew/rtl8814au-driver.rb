class Rtl8814auDriver < Formula
  desc "DriverKit RTL8814AU driver for macOS Sequoia"
  homepage "https://github.com/yourorg/RTL8814AUDriver"
  url "https://github.com/yourorg/RTL8814AUDriver/releases/download/v0.1.0/RTL8814AUDriver-0.1.0.pkg"
  sha256 "REPLACE_WITH_REAL_SHA256"
  license "MIT"

  def install
    system "/usr/sbin/installer", "-pkg", cached_download, "-target", "/"
  end

  def caveats
    <<~EOS
      RTL8814AU DriverKit extension has been installed.

      Next steps:
        1. Open System Settings → Privacy & Security.
        2. If you see a message about a blocked system extension from this developer, click "Allow".
        3. Reboot if prompted.
    EOS
  end

  test do
    assert_predicate "/Applications/RTL8814AU Driver Manager.app", :exist?
  end
end
