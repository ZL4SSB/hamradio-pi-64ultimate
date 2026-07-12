#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
BIN_DIR="$HOME/.local/bin"

echo
echo "============================================================"
echo "          HamRadio-Pi Ultimate 4.3.0 Installer"
echo "============================================================"
echo
echo "This installer will automatically download all required"
echo "Raspberry Pi OS / Debian Trixie packages."
echo

if ! command -v apt-get >/dev/null 2>&1; then
    echo "ERROR: This installer requires Raspberry Pi OS or Debian."
    exit 1
fi

sudo apt-get update

sudo apt-get install -y \
    python3 \
    python3-pyqt6 \
    python3-pyqt6.qtquick \
    python3-pyqt6.qtsvg \
    qml6-module-qtquick \
    qml6-module-qtquick-controls \
    qml6-module-qtquick-layouts \
    qml6-module-qtquick-window \
    qml6-module-qtquick-templates \
    qml6-module-qtqml \
    qt6-image-formats-plugins \
    libqt6svg6 \
    git \
    curl \
    ca-certificates \
    usbutils \
    alsa-utils \
    policykit-1 \
    xterm

chmod +x \
    "$ROOT/src/app.py" \
    "$ROOT/scripts/"*.sh \
    "$ROOT/install.sh"

mkdir -p "$APP_DIR" "$ICON_DIR" "$BIN_DIR"

cat > "$BIN_DIR/hamradio-pi-ultimate" <<EOF
#!/usr/bin/env bash
export QT_QUICK_CONTROLS_STYLE=Basic
exec python3 "$ROOT/src/app.py" "\$@"
EOF
chmod +x "$BIN_DIR/hamradio-pi-ultimate"

sed \
    -e "s|@APP_ROOT@|$ROOT|g" \
    "$ROOT/desktop/hamradio-pi-ultimate.desktop" \
    > "$APP_DIR/hamradio-pi-ultimate.desktop"

cp \
    "$ROOT/assets/branding/hamradio-pi-256.png" \
    "$ICON_DIR/hamradio-pi-ultimate.png"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DIR" || true
fi

echo
echo "Checking the Qt/QML installation..."
export QT_QPA_PLATFORM=offscreen
export QT_QUICK_BACKEND=software
export QT_QUICK_CONTROLS_STYLE=Basic

if python3 "$ROOT/src/app.py" --no-splash --self-test; then
    echo "Qt/QML self-test passed."
else
    echo
    echo "WARNING: The graphical self-test did not complete."
    echo "Run this command from the desktop terminal for details:"
    echo "  python3 $ROOT/src/app.py --no-splash"
fi

unset QT_QPA_PLATFORM
unset QT_QUICK_BACKEND

echo
echo "Installation complete."
echo
echo "Start from the desktop menu or run:"
echo "  $BIN_DIR/hamradio-pi-ultimate"
echo
