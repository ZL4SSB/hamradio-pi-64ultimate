#!/usr/bin/env bash
set -euo pipefail

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

sudo apt-get update
sudo apt-get install -y curl unzip ca-certificates

DOWNLOAD_URL="https://codeload.github.com/${REPO_OWNER}/${REPO_NAME}/zip/refs/heads/${BRANCH}"

echo "Downloading the latest public version..."
curl \
    --fail \
    --location \
    --retry 3 \
    --connect-timeout 20 \
    --output "$ARCHIVE" \
    "$DOWNLOAD_URL"

mkdir -p "$EXTRACTED"
unzip -q "$ARCHIVE" -d "$EXTRACTED"

SOURCE_DIR="$EXTRACTED/${REPO_NAME}-${BRANCH}"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "ERROR: Downloaded archive structure was not recognised."
    exit 1
fi

BACKUP="$HOME/hamradio-pi-64ultimate-backup-$(date +%Y%m%d-%H%M%S)"

if [ -d "$TARGET" ]; then
    echo "Creating backup:"
    echo "  $BACKUP"
    mv "$TARGET" "$BACKUP"
fi

mv "$SOURCE_DIR" "$TARGET"

cd "$TARGET"
chmod +x install.sh install-public.sh src/app.py scripts/*.sh

echo "Running the installer for the updated version..."
exec ./install.sh
