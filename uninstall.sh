#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo
echo "HamRadio-Pi Ultimate uninstaller"
echo

systemctl --user disable --now hrpu-propagation.service \
    >/dev/null 2>&1 || true

rm -f "$HOME/.config/systemd/user/hrpu-propagation.service"
systemctl --user daemon-reload >/dev/null 2>&1 || true

rm -f "$HOME/.local/bin/hamradio-pi-ultimate"
rm -f "$HOME/.local/share/applications/hamradio-pi-ultimate.desktop"
rm -f "$HOME/Desktop/HamRadio-Pi-Ultimate.desktop"
rm -f "$HOME/.config/autostart/hamradio-pi-ultimate.desktop"
rm -f "$HOME/.local/share/icons/hicolor/256x256/apps/hamradio-pi-ultimate.png"

echo "Launchers and the propagation service have been removed."
echo
echo "The project folder and user settings were left in place:"
echo "  $ROOT"
echo
echo "Delete that folder manually only if you no longer need its settings."
