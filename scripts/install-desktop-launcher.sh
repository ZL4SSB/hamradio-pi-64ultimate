#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="HamRadio-Pi Ultimate"
APP_ID="hamradio-pi-ultimate"
LAUNCHER="$PROJECT_DIR/scripts/hamradio-pi-ultimate"
DESKTOP_TEMPLATE="$PROJECT_DIR/desktop/hamradio-pi-ultimate.desktop"
APPLICATIONS_DIR="$HOME/.local/share/applications"
DESKTOP_DIR="${XDG_DESKTOP_DIR:-$HOME/Desktop}"
MENU_FILE="$APPLICATIONS_DIR/${APP_ID}.desktop"
DESKTOP_FILE="$DESKTOP_DIR/${APP_NAME}.desktop"

echo "=============================================="
echo " HamRadio-Pi Ultimate - Desktop Installer"
echo "=============================================="
echo

if [[ ! -f "$PROJECT_DIR/src/app.py" ]]; then
    echo "ERROR: src/app.py was not found."
    echo "Run this installer from inside the project."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-tk
fi

chmod +x "$LAUNCHER"
chmod +x "$PROJECT_DIR/install.sh" 2>/dev/null || true
find "$PROJECT_DIR/scripts" -maxdepth 1 -type f -name "*.sh" -exec chmod +x {} \;

mkdir -p "$APPLICATIONS_DIR"
mkdir -p "$DESKTOP_DIR"

if [[ ! -f "$DESKTOP_TEMPLATE" ]]; then
    echo "ERROR: Desktop launcher template was not found."
    exit 1
fi

sed \
    -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
    "$DESKTOP_TEMPLATE" > "$MENU_FILE"

cp "$MENU_FILE" "$DESKTOP_FILE"

chmod +x "$MENU_FILE"
chmod +x "$DESKTOP_FILE"

if command -v gio >/dev/null 2>&1; then
    gio set "$DESKTOP_FILE" metadata::trusted true >/dev/null 2>&1 || true
fi

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPLICATIONS_DIR" >/dev/null 2>&1 || true
fi

echo
echo "Installation complete."
echo
echo "Created:"
echo "  Menu entry: $MENU_FILE"
echo "  Desktop icon: $DESKTOP_FILE"
echo
echo "You can also start the program with:"
echo "  $LAUNCHER"
echo
echo "If the desktop icon initially appears untrusted,"
echo "right-click it and choose 'Allow Launching'."
