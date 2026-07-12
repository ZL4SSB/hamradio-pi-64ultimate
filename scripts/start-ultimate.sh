#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export QT_QUICK_CONTROLS_STYLE=Basic
exec python3 "$ROOT/src/app.py" "$@"
