#!/usr/bin/env bash
set -Eeuo pipefail

REPO_OWNER="zl4ssb"
REPO_NAME="hamradio-pi-64ultimate"
BRANCH="main"
TARGET="$HOME/hamradio-pi-64ultimate"

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

SOURCE="$EXTRACTED/${REPO_NAME}-${BRANCH}"

if [ ! -d "$SOURCE" ]; then
    echo "ERROR: Downloaded archive did not contain the expected project folder."
    exit 1
fi

if [ -d "$TARGET" ]; then
    BACKUP="$HOME/hamradio-pi-64ultimate-backup-$(date +%Y%m%d-%H%M%S)"
    echo "Backing up existing installation to:"
    echo "  $BACKUP"
    mv "$TARGET" "$BACKUP"
fi

mv "$SOURCE" "$TARGET"

cd "$TARGET"
chmod +x install.sh install-public.sh src/app.py scripts/*.sh

exec ./install.sh
