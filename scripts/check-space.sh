#!/bin/bash

# HamRadio-Pi Ultimate
# Disk-space checker

# Space estimates in gigabytes.
# These are temporary estimates and can be refined later.

FULL_REQUIRED_GB=30
DIGITAL_REQUIRED_GB=5
SDR_REQUIRED_GB=10
APRS_REQUIRED_GB=3
SATELLITE_REQUIRED_GB=2
PROGRAMMING_REQUIRED_GB=2
SERVER_REQUIRED_GB=8

# Keep this much free after installation.
SAFETY_RESERVE_GB=5

FREE_SPACE_KB=$(df / --output=avail | tail -n 1)
FREE_SPACE_GB=$((FREE_SPACE_KB / 1024 / 1024))

INSTALL_TYPE="$1"

case "$INSTALL_TYPE" in
    FULL)
        REQUIRED_GB=$FULL_REQUIRED_GB
        DISPLAY_NAME="Complete Ham Station"
        ;;
    DIGITAL)
        REQUIRED_GB=$DIGITAL_REQUIRED_GB
        DISPLAY_NAME="Digital Modes"
        ;;
    SDR)
        REQUIRED_GB=$SDR_REQUIRED_GB
        DISPLAY_NAME="SDR Software"
        ;;
    APRS)
        REQUIRED_GB=$APRS_REQUIRED_GB
        DISPLAY_NAME="APRS and Packet"
        ;;
    SATELLITE)
        REQUIRED_GB=$SATELLITE_REQUIRED_GB
        DISPLAY_NAME="Satellite Tools"
        ;;
    PROGRAMMING)
        REQUIRED_GB=$PROGRAMMING_REQUIRED_GB
        DISPLAY_NAME="Radio Programming"
        ;;
    SERVER)
        REQUIRED_GB=$SERVER_REQUIRED_GB
        DISPLAY_NAME="Server Tools"
        ;;
    *)
        echo "ERROR: Unknown installation type."
        echo
        echo "Example:"
        echo "./scripts/check-space.sh FULL"
        exit 2
        ;;
esac

TOTAL_NEEDED_GB=$((REQUIRED_GB + SAFETY_RESERVE_GB))
SPACE_AFTER_GB=$((FREE_SPACE_GB - REQUIRED_GB))

echo
echo "========================================"
echo " HamRadio-Pi Ultimate - Storage Check"
echo "========================================"
echo
echo "Selected installation: $DISPLAY_NAME"
echo
echo "Free space:            ${FREE_SPACE_GB} GB"
echo "Estimated install:     ${REQUIRED_GB} GB"
echo "Safety reserve:        ${SAFETY_RESERVE_GB} GB"
echo

if [ "$FREE_SPACE_GB" -lt "$TOTAL_NEEDED_GB" ]; then
    echo "NOT ENOUGH SPACE"
    echo
    echo "The selected installation cannot be installed safely."
    echo "Choose a smaller installation group or free more storage."
    echo
    exit 1
fi

echo "Space after install:   Approximately ${SPACE_AFTER_GB} GB"
echo
echo "PASS: Sufficient storage is available."
echo
exit 0
