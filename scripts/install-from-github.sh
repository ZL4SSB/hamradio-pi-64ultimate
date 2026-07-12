#!/usr/bin/env bash
set -euo pipefail

echo "This installer uses the public ZIP download and does not require"
echo "a GitHub account or credentials."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -x "$SCRIPT_DIR/install-public.sh" ]; then
    exec "$SCRIPT_DIR/install-public.sh"
fi

echo "ERROR: install-public.sh was not found."
exit 1
