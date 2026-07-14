#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="HamRadio-Pi Ultimate"
APP_VERSION="1.2.0"

APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
BIN_DIR="$HOME/.local/bin"
LOG_DIR="$ROOT/reports"
LOG_FILE="$LOG_DIR/install.log"

mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

trap 'echo; echo "Installation stopped unexpectedly."; echo "Log: $LOG_FILE"; exit 1' ERR

step() {
    echo
    echo "------------------------------------------------------------"
    echo "$1"
    echo "------------------------------------------------------------"
}

ok() {
    echo "✔ $1"
}

warn() {
    echo "⚠ $1"
}

fail() {
    echo "✘ $1"
    echo "Installation log: $LOG_FILE"
    exit 1
}

package_available() {
    apt-cache show "$1" >/dev/null 2>&1
}

install_available_packages() {
    local packages=()
    local package

    for package in "$@"; do
        if package_available "$package"; then
            packages+=("$package")
        else
            warn "Package unavailable on this OS; skipping: $package"
        fi
    done

    if [ "${#packages[@]}" -gt 0 ]; then
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "${packages[@]}"
    fi
}

install_first_available() {
    local candidate

    for candidate in "$@"; do
        if package_available "$candidate"; then
            sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "$candidate"
            ok "Installed $candidate"
            return 0
        fi
    done

    return 1
}

step "$APP_NAME $APP_VERSION"
echo "Automatic Raspberry Pi installer"
echo "No package editing or manual dependency installation is required."
echo

if ! command -v apt-get >/dev/null 2>&1; then
    fail "This installer requires Raspberry Pi OS or Debian."
fi

ARCH="$(dpkg --print-architecture 2>/dev/null || uname -m)"
OS_NAME="$(. /etc/os-release 2>/dev/null; echo "${PRETTY_NAME:-Unknown Debian system}")"

echo "Operating system: $OS_NAME"
echo "Architecture:     $ARCH"
echo "Project folder:   $ROOT"

step "Updating package information"
sudo apt-get update
ok "Package information updated"

step "Installing required system packages"

# Core packages known to exist across current Raspberry Pi OS releases.
install_available_packages \
    python3 \
    python3-pyqt6 \
    python3-pyqt6.qtquick \
    python3-pyqt6.qtsvg \
    python3-pyqt6.qtwebengine \
    qml6-module-qtquick \
    qml6-module-qtquick-controls \
    qml6-module-qtquick-layouts \
    qml6-module-qtquick-window \
    qml6-module-qtwebengine \
    qml6-module-qtwebengine-controlsdelegates \
    qml6-module-qtquick-dialogs \
    qml6-module-qtquick-templates \
    qml6-module-qtqml \
    qt6-image-formats-plugins \
    libqt6svg6 \
    curl \
    unzip \
    ca-certificates \
    git \
    usbutils \
    alsa-utils \
    pulseaudio-utils \
    python3-sounddevice \
    python3-numpy \
    portaudio19-dev \
    chrony \
    gpsd \
    gpsd-clients \
    pps-tools \
    xterm

# PolicyKit changed package names between Debian releases. It is optional,
# so install whichever modern package is available without stopping setup.
install_first_available pkexec policykit-1 polkitd || \
    warn "PolicyKit helper not available; privileged application actions may use sudo."

step "Verifying Python, Qt and QML"

if ! python3 - <<'PY'
from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtWebEngineQuick import QtWebEngineQuick
import numpy
import sounddevice
print("Qt version:", QT_VERSION_STR)
print("PyQt version:", PYQT_VERSION_STR)
print("Qt QML support: OK")
print("Qt WebEngine support: OK")
print("Live audio meter support: OK")
PY
then
    fail "PyQt6 or Qt Quick could not be imported."
fi

ok "Python, Qt and QML are available"

step "Creating application launcher"

chmod +x \
    "$ROOT/install.sh" \
    "$ROOT/install-public.sh" \
    "$ROOT/src/app.py" \
    "$ROOT/scripts/"*.sh

mkdir -p "$APP_DIR" "$ICON_DIR" "$BIN_DIR"

cat > "$BIN_DIR/hamradio-pi-ultimate" <<EOF
#!/usr/bin/env bash
export QT_QUICK_CONTROLS_STYLE=Basic
export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu"
exec python3 "$ROOT/src/app.py" "\$@"
EOF
chmod +x "$BIN_DIR/hamradio-pi-ultimate"

cp \
    "$ROOT/assets/branding/hamradio-pi-ultimate.png" \
    "$ICON_DIR/hamradio-pi-ultimate.png"

cat > "$APP_DIR/hamradio-pi-ultimate.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=HamRadio-Pi Ultimate
Comment=Modern Ham Shack Control Centre
Exec=$BIN_DIR/hamradio-pi-ultimate
Icon=hamradio-pi-ultimate
Terminal=false
Categories=HamRadio;Utility;
StartupNotify=true
EOF
chmod +x "$APP_DIR/hamradio-pi-ultimate.desktop"

# Create the Ham Radio menu category if the desktop supports menu merging.
MENU_DIR="$HOME/.config/menus/applications-merged"
DIRECTORY_DIR="$HOME/.local/share/desktop-directories"
mkdir -p "$MENU_DIR" "$DIRECTORY_DIR"

cat > "$DIRECTORY_DIR/hamradio.directory" <<EOF
[Desktop Entry]
Type=Directory
Name=Ham Radio
Comment=Amateur radio applications
Icon=hamradio-pi-ultimate
EOF

cat > "$MENU_DIR/hamradio.menu" <<EOF
<Menu>
  <Name>Applications</Name>
  <Menu>
    <Name>HamRadio</Name>
    <Directory>hamradio.directory</Directory>
    <Include>
      <Category>HamRadio</Category>
    </Include>
  </Menu>
</Menu>
EOF

CREATE_DESKTOP="yes"
LAUNCH_AFTER="yes"

if [ -r /dev/tty ]; then
    printf "Create a desktop shortcut? [Y/n]: " > /dev/tty
    read -r answer < /dev/tty || answer=""
    case "${answer:-Y}" in
        n|N|no|NO) CREATE_DESKTOP="no" ;;
    esac

    printf "Launch HamRadio-Pi Ultimate after installation? [Y/n]: " > /dev/tty
    read -r answer < /dev/tty || answer=""
    case "${answer:-Y}" in
        n|N|no|NO) LAUNCH_AFTER="no" ;;
    esac
fi

if [ "$CREATE_DESKTOP" = "yes" ]; then
    DESKTOP_DIR="$HOME/Desktop"
    mkdir -p "$DESKTOP_DIR"
    cp \
        "$APP_DIR/hamradio-pi-ultimate.desktop" \
        "$DESKTOP_DIR/HamRadio-Pi-Ultimate.desktop"
    chmod +x "$DESKTOP_DIR/HamRadio-Pi-Ultimate.desktop"

    # Mark trusted where supported.
    if command -v gio >/dev/null 2>&1; then
        gio set \
            "$DESKTOP_DIR/HamRadio-Pi-Ultimate.desktop" \
            metadata::trusted true >/dev/null 2>&1 || true
    fi
fi

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DIR" || true
fi

ok "Desktop shortcut, Ham Radio menu entry and command launcher created"

step "Installing local propagation service"

python3 "$ROOT/scripts/sync-propagation-config.py"

USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
USER_SERVICE="$USER_SYSTEMD_DIR/hrpu-propagation.service"
mkdir -p "$USER_SYSTEMD_DIR"

sed \
    "s|__PROPAGATION_DIR__|$ROOT/propagation|g" \
    "$ROOT/propagation/hrpu-propagation.service.template" \
    > "$USER_SERVICE"

if command -v systemctl >/dev/null 2>&1; then
    systemctl --user daemon-reload || true
    systemctl --user enable --now hrpu-propagation.service || \
        warn "Could not enable the user propagation service; HRPU will start it directly."

    if command -v loginctl >/dev/null 2>&1; then
        sudo loginctl enable-linger "$USER" >/dev/null 2>&1 || true
    fi
else
    warn "systemctl is unavailable; HRPU will start propagation directly."
fi

ok "Local propagation module installed at http://127.0.0.1:8765"

step "Running automatic application self-test"

if QT_QPA_PLATFORM=offscreen \
   QT_QUICK_BACKEND=software \
   QT_QUICK_CONTROLS_STYLE=Basic \
   python3 "$ROOT/src/app.py" --no-splash --self-test; then
    ok "Application self-test passed"
else
    warn "Off-screen self-test was not supported by this display driver."
    warn "The installation will continue; the normal desktop launch may still work."
fi

step "Installation complete"

echo "Start from the Raspberry Pi desktop menu:"
echo "  HamRadio-Pi Ultimate"
echo
echo "Or run:"
echo "  hamradio-pi-ultimate"
echo

# Start automatically only when installed from an active graphical desktop.
if [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; then
    echo "Starting $APP_NAME..."
    nohup "$BIN_DIR/hamradio-pi-ultimate" \
        > "$LOG_DIR/application-start.log" 2>&1 &
    ok "$APP_NAME started"
else
    echo "No graphical desktop session was detected."
    echo "Log into the Raspberry Pi desktop and select HamRadio-Pi Ultimate."
fi
