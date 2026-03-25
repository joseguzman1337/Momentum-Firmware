#!/usr/bin/env bash
set -euo pipefail

# This script expects that you have already built & archived the app via Xcode.
# It demonstrates a minimal flow using productbuild and productsign.

APP_BUNDLE="RTL8814AU Driver Manager.app"
APP_SOURCE_DIR="${1:-build/Release}"
PKG_ID="com.yourorg.rtl8814audriver"
UNSIGNED_PKG="RTL8814AUDriver-unsigned.pkg"
SIGNED_PKG="RTL8814AUDriver-signed.pkg"
DEVELOPER_ID_INSTALLER="Developer ID Installer: Your Name (TEAMID)"

if [[ ! -d "${APP_SOURCE_DIR}/${APP_BUNDLE}" ]]; then
  echo "App bundle not found at ${APP_SOURCE_DIR}/${APP_BUNDLE}" >&2
  exit 1
fi

mkdir -p pkgroot/Applications
cp -R "${APP_SOURCE_DIR}/${APP_BUNDLE}" pkgroot/Applications/

productbuild \
  --root pkgroot \
  --identifier "${PKG_ID}" \
  --version "0.1.0" \
  "${UNSIGNED_PKG}"

echo "Unsigned pkg created: ${UNSIGNED_PKG}" >&2

echo "Signing pkg with Developer ID Installer certificate..." >&2
productsign \
  --sign "${DEVELOPER_ID_INSTALLER}" \
  "${UNSIGNED_PKG}" \
  "${SIGNED_PKG}"

echo "Signed pkg: ${SIGNED_PKG}" >&2

echo "Next steps:" >&2
echo "  1. Notarize with xcrun notarytool submit ${SIGNED_PKG} ..." >&2
echo "  2. Staple with xcrun stapler staple ${SIGNED_PKG}" >&2
