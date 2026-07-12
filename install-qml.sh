#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo apt update
sudo apt install -y \
  python3 \
  python3-pyqt6 \
  python3-pyqt6.qtquick \
  python3-pyqt6.qtsvg \
  qml6-module-qtquick \
  qml6-module-qtquick-controls \
  qml6-module-qtquick-layouts \
  qml6-module-qtquick-window \
  qt6-image-formats-plugins \
  libqt6svg6 \
  git \
  usbutils \
  alsa-utils

chmod +x "$ROOT/src/app.py" "$ROOT/scripts/"*.sh

mkdir -p \
  "$HOME/.local/share/applications" \
  "$HOME/.local/share/icons/hicolor/256x256/apps"

sed "s|%h/hamradio-pi-64ultimate|$ROOT|g" \
  "$ROOT/desktop/hamradio-pi-ultimate.desktop" \
  > "$HOME/.local/share/applications/hamradio-pi-ultimate.desktop"

cp "$ROOT/assets/branding/hamradio-pi-256.png" \
  "$HOME/.local/share/icons/hicolor/256x256/apps/hamradio-pi-ultimate.png"

echo "HamRadio-Pi Ultimate installation complete."
