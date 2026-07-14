#!/usr/bin/env bash
set -Eeuo pipefail

REPO_OWNER="ZL4SSB"
REPO_NAME="Ham-Radio-Pi-Ultimate"
BRANCH="main"
TARGET="$HOME/Ham-Radio-Pi-Ultimate"

TMP_DIR="$(mktemp -d)"
ARCHIVE="$TMP_DIR/project.zip"
EXTRACTED="$TMP_DIR/extracted"

cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo
echo "HamRadio-Pi Ultimate public installer"
echo "No GitHub login or account is required."
echo

if ! command -v curl >/dev/null 2>&1 || ! command -v unzip >/dev/null 2>&1; then
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
        curl unzip ca-certificates
fi

URL="https://codeload.github.com/${REPO_OWNER}/${REPO_NAME}/zip/refs/heads/${BRANCH}"

echo "Downloading HamRadio-Pi Ultimate..."
curl \
    --fail \
    --location \
    --retry 3 \
    --connect-timeout 20 \
    --output "$ARCHIVE" \
    "$URL"

mkdir -p "$EXTRACTED"
unzip -q "$ARCHIVE" -d "$EXTRACTED"

SOURCE="$(find "$EXTRACTED" -mindepth 1 -maxdepth 1 -type d | head -n 1)"

if [ -z "$SOURCE" ] || [ ! -f "$SOURCE/install.sh" ]; then
    echo "ERROR: Downloaded archive did not contain a valid project folder."
    exit 1
fi

PRESERVE_DIR="$TMP_DIR/preserve"
mkdir -p "$PRESERVE_DIR"

if [ -d "$TARGET" ]; then
    systemctl --user stop hrpu-propagation.service >/dev/null 2>&1 || true

    for item in         config/settings.json         config/dashboards.json         propagation/config.json
    do
        if [ -f "$TARGET/$item" ]; then
            mkdir -p "$PRESERVE_DIR/$(dirname "$item")"
            cp "$TARGET/$item" "$PRESERVE_DIR/$item"
        fi
    done

    BACKUP="$HOME/Ham-Radio-Pi-Ultimate-backup-$(date +%Y%m%d-%H%M%S)"
    echo "Backing up existing installation to:"
    echo "  $BACKUP"
    mv "$TARGET" "$BACKUP"
fi

mv "$SOURCE" "$TARGET"

if [ -d "$PRESERVE_DIR" ]; then
    cp -a "$PRESERVE_DIR/." "$TARGET/" 2>/dev/null || true
fi

cd "$TARGET"
chmod +x install.sh install-public.sh src/app.py scripts/*.sh

exec ./install.sh
