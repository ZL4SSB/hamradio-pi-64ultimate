#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/zl4ssb/hamradio-pi-64ultimate.git"
TARGET="$HOME/hamradio-pi-64ultimate"

if [ -d "$TARGET/.git" ]; then
    git -C "$TARGET" pull --ff-only
else
    rm -rf "$TARGET"
    git clone "$REPO_URL" "$TARGET"
fi

cd "$TARGET"
chmod +x install.sh scripts/*.sh src/app.py
exec ./install.sh
