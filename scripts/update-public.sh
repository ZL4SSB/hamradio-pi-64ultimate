#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALLER_URL="https://raw.githubusercontent.com/zl4ssb/hamradio-pi-64ultimate/main/install-public.sh"
TMP_INSTALLER="$(mktemp)"

cleanup() {
    rm -f "$TMP_INSTALLER"
}
trap cleanup EXIT

echo "Downloading the latest public installer..."
curl -fsSL --retry 3 "$INSTALLER_URL" -o "$TMP_INSTALLER"
chmod +x "$TMP_INSTALLER"
exec "$TMP_INSTALLER"
