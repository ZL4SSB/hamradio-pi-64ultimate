#!/usr/bin/env bash
set -Eeuo pipefail

echo "Using anonymous public ZIP installation."
echo "No GitHub account or credentials are required."

URL="https://raw.githubusercontent.com/zl4ssb/hamradio-pi-64ultimate/main/install-public.sh"
TMP_INSTALLER="$(mktemp)"
trap 'rm -f "$TMP_INSTALLER"' EXIT

curl -fsSL --retry 3 "$URL" -o "$TMP_INSTALLER"
chmod +x "$TMP_INSTALLER"
exec "$TMP_INSTALLER"
