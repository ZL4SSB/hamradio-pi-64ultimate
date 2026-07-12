#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
from PyQt6.QtQml import QQmlApplicationEngine
print("Qt:", QT_VERSION_STR)
print("PyQt:", PYQT_VERSION_STR)
print("Qt QML import: OK")
PY
