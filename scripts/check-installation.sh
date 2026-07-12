#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "HamRadio-Pi Ultimate installation check"
echo "======================================="

python3 - <<'PY'
from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtQml import QQmlApplicationEngine
print("Qt version:", QT_VERSION_STR)
print("PyQt version:", PYQT_VERSION_STR)
print("Qt QML import: OK")
PY

for command in git lsusb lsblk arecord xterm; do
    if command -v "$command" >/dev/null 2>&1; then
        echo "$command: installed"
    else
        echo "$command: missing"
    fi
done

echo
echo "Application self-test:"
QT_QPA_PLATFORM=offscreen \
QT_QUICK_BACKEND=software \
QT_QUICK_CONTROLS_STYLE=Basic \
python3 "$ROOT/src/app.py" --no-splash --self-test
