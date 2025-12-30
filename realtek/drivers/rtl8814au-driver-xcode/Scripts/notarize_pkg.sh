#!/usr/bin/env bash
set -euo pipefail

PKG=${1:-RTL8814AUDriver-signed.pkg}
PROFILE=${2:-YOUR_NOTARY_PROFILE}

if [[ ! -f "${PKG}" ]]; then
  echo "Package not found: ${PKG}" >&2
  exit 1
fi

echo "Submitting ${PKG} for notarization using profile ${PROFILE}..." >&2
xcrun notarytool submit "${PKG}" --keychain-profile "${PROFILE}" --wait

echo "Stapling ticket to ${PKG}..." >&2
xcrun stapler staple "${PKG}"

echo "Verifying stapled pkg..." >&2
spctl --assess --type install "${PKG}"
pkgutil --check-signature "${PKG}"

echo "Notarization and verification complete." >&2
