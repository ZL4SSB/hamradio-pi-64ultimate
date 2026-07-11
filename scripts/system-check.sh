#!/bin/bash

echo
echo "========================================"
echo " HamRadio-Pi Ultimate - System Check"
echo "========================================"
echo

if [ -f /proc/device-tree/model ]; then
    PI_MODEL=$(tr -d '\0' </proc/device-tree/model)
    echo "Raspberry Pi model: $PI_MODEL"
else
    echo "WARNING: Raspberry Pi model not detected."
fi

source /etc/os-release
echo "Operating system: $PRETTY_NAME"
echo "Architecture: $(uname -m)"

if ping -c 1 -W 3 deb.debian.org >/dev/null 2>&1; then
    echo "Internet: PASS"
else
    echo "Internet: FAIL"
    exit 1
fi

FREE_SPACE_KB=$(df / --output=avail | tail -n 1)
FREE_SPACE_GB=$((FREE_SPACE_KB / 1024 / 1024))
echo "Free storage: approximately ${FREE_SPACE_GB} GB"
