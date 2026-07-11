#!/usr/bin/env bash

set -Eeuo pipefail

APP_NAME="HamRadio-Pi Ultimate"
APP_ID="hamradio-pi-ultimate"
APPLICATIONS_DIR="$HOME/.local/share/applications"
DESKTOP_DIR="${XDG_DESKTOP_DIR:-$HOME/Desktop}"

rm -f "$APPLICATIONS_DIR/${APP_ID}.desktop"
rm -f "$DESKTOP_DIR/${APP_NAME}.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPLICATIONS_DIR" >/dev/null 2>&1 || true
fi

echo "HamRadio-Pi Ultimate desktop and menu launchers were removed."
