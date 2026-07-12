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

echo
echo "============================================================"
echo "     HamRadio-Pi Ultimate Public Installer 4.3.1"
echo "============================================================"
echo
echo "No GitHub account or login is required."
echo

sudo apt-get update
sudo apt-get install -y \
    curl \
    unzip \
    ca-certificates

DOWNLOAD_URL="https://codeload.github.com/${REPO_OWNER}/${REPO_NAME}/zip/refs/heads/${BRANCH}"

echo "Downloading the public release archive..."
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
    echo "ERROR: The downloaded archive did not contain the expected folder."
    echo "Expected: $SOURCE_DIR"
    exit 1
fi

echo "Installing files into:"
echo "  $TARGET"

rm -rf "$TARGET"
mv "$SOURCE_DIR" "$TARGET"

cd "$TARGET"

chmod +x install.sh src/app.py scripts/*.sh install-public.sh

exec ./install.sh
