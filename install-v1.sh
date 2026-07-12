#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Installing HamRadio-Pi Ultimate 1.0.0"
sudo apt-get update
sudo apt-get install -y python3 python3-tk git usbutils alsa-utils xz-utils gzip
chmod +x "$ROOT/src/app.py" "$ROOT/scripts/"*.sh
mkdir -p "$HOME/.local/share/applications" "$HOME/.local/share/desktop-directories"
sed "s|%h/hamradio-pi-64ultimate|$ROOT|g" \
  "$ROOT/desktop/hamradio-pi-ultimate.desktop" \
  > "$HOME/.local/share/applications/hamradio-pi-ultimate.desktop"
cp "$ROOT/desktop/hamradio.directory" "$HOME/.local/share/desktop-directories/hamradio.directory"
"$ROOT/scripts/group-hamradio-menu.sh" || true
echo
echo "Installation complete."
echo "Start with: python3 $ROOT/src/app.py"
