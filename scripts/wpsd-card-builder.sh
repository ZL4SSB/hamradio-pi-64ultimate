#!/usr/bin/env bash

# HamRadio-Pi Ultimate
# WPSD SD Card Builder
# Version 0.1.0
#
# This tool prepares the CURRENT Raspberry Pi to download and launch
# Raspberry Pi Imager for writing a WPSD image to an SD card intended
# for a SEPARATE Raspberry Pi / MMDVM hotspot.
#
# IMPORTANT:
# - This script never writes directly to any storage device.
# - Raspberry Pi Imager performs the actual write operation.
# - The user must select the destination card inside Imager.

set -Eeuo pipefail

VERSION="0.1.0"
WPSD_URL="https://w0chp.radio/wpsd/"
MIN_IMAGE_BYTES=$((100 * 1024 * 1024))

info() {
    printf '\n%s\n' "$*"
}

fail() {
    printf '\nERROR: %s\n' "$*" >&2
    exit 1
}

have_gui() {
    [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]
}

dialog_info() {
    local title="$1"
    local message="$2"

    if command -v zenity >/dev/null 2>&1 && have_gui; then
        zenity --info --width=560 --title="$title" --text="$message"
    else
        printf '\n%s\n\n%s\n' "$title" "$message"
    fi
}

dialog_warning() {
    local title="$1"
    local message="$2"

    if command -v zenity >/dev/null 2>&1 && have_gui; then
        zenity --warning --width=620 --title="$title" --text="$message"
    else
        printf '\nWARNING: %s\n\n%s\n' "$title" "$message"
    fi
}

ask_yes_no() {
    local title="$1"
    local message="$2"

    if command -v zenity >/dev/null 2>&1 && have_gui; then
        zenity --question --width=560 --title="$title" --text="$message"
        return $?
    fi

    local reply
    read -r -p "$message [y/N]: " reply
    [[ "$reply" =~ ^[Yy]$ ]]
}

install_requirements() {
    local missing=()

    command -v rpi-imager >/dev/null 2>&1 || missing+=(rpi-imager)
    command -v zenity >/dev/null 2>&1 || missing+=(zenity)
    command -v xdg-open >/dev/null 2>&1 || missing+=(xdg-utils)
    command -v lsblk >/dev/null 2>&1 || missing+=(util-linux)
    command -v xz >/dev/null 2>&1 || missing+=(xz-utils)

    if ((${#missing[@]} == 0)); then
        return
    fi

    info "The following required packages will be installed:"
    printf '  %s\n' "${missing[@]}"

    sudo apt update
    sudo apt install -y "${missing[@]}"
}

choose_image() {
    local default_dir="${HOME}/Downloads"
    mkdir -p "$default_dir"

    if command -v zenity >/dev/null 2>&1 && have_gui; then
        zenity --file-selection \
            --title="Select the downloaded WPSD image" \
            --filename="${default_dir}/" \
            --file-filter="WPSD compressed images | *.img.xz *.xz" \
            --file-filter="All files | *"
        return
    fi

    local image_path
    read -r -p "Enter the full path to the downloaded WPSD .img.xz file: " image_path
    printf '%s\n' "$image_path"
}

validate_image() {
    local image="$1"

    [[ -f "$image" ]] || fail "The selected image file does not exist."

    case "$image" in
        *.img.xz|*.xz) ;;
        *) fail "Please select the original compressed WPSD .img.xz image." ;;
    esac

    local image_bytes
    image_bytes=$(stat -c '%s' "$image")
    ((image_bytes >= MIN_IMAGE_BYTES)) ||
        fail "The selected file is unexpectedly small and may not be a complete WPSD image."

    if ! xz --test "$image"; then
        fail "The compressed image failed its integrity test. Download it again."
    fi
}

show_removable_devices() {
    info "Storage devices currently visible to Linux:"
    echo
    lsblk -d -e 7 -o NAME,MODEL,SIZE,TRAN,RM,TYPE | sed 's/^/  /'
    echo

    dialog_warning \
        "Check the destination carefully" \
        "Raspberry Pi Imager will erase the storage device you select.

Use the SD card connected through your USB card reader.

Do NOT select the SD card or drive currently running this Raspberry Pi.

HamRadio-Pi Ultimate does not select or erase a device automatically."
}

launch_imager() {
    local image="$1"
    local image_dir
    image_dir=$(dirname "$image")

    dialog_info \
        "WPSD image ready" \
        "The WPSD image has passed its basic integrity check.

Raspberry Pi Imager will now open.

In Imager:
1. Select the Raspberry Pi model used by the MMDVM hotspot.
2. Choose OS, then select Use Custom.
3. Select this file:
$image
4. Select the USB-connected SD card.
5. Do not apply normal Raspberry Pi OS customisation settings unless the official WPSD instructions specifically require them.
6. Check the selected card carefully before writing."

    # Open the folder so the image is easy to locate in Imager's file chooser.
    xdg-open "$image_dir" >/dev/null 2>&1 &

    # Run Imager in the foreground so terminal messages remain visible.
    rpi-imager
}

main() {
    clear
    cat <<EOF
============================================================
 HamRadio-Pi Ultimate
 WPSD SD Card Builder v${VERSION}
============================================================

This prepares an SD card for a separate Raspberry Pi fitted
with an MMDVM hotspot board.

The actual card write is performed by Raspberry Pi Imager.
This helper never writes directly to a disk.
EOF

    install_requirements

    dialog_info \
        "WPSD SD Card Builder" \
        "This tool prepares an SD card for a separate MMDVM hotspot Raspberry Pi.

You will download the correct official WPSD image, select it here, and then write it using Raspberry Pi Imager.

An SD card of at least 8 GB is required."

    if ask_yes_no \
        "Open official WPSD downloads" \
        "Open the official WPSD download page now?

Choose the image that exactly matches the Raspberry Pi and hotspot hardware that will use the card."; then
        xdg-open "$WPSD_URL" >/dev/null 2>&1 &
    fi

    dialog_info \
        "Download the image first" \
        "Download the appropriate WPSD image from the official page.

Leave the image compressed as .img.xz. Raspberry Pi Imager can use the compressed file directly.

Return to this builder after the download is complete."

    local image_file
    image_file=$(choose_image) || {
        info "No image was selected. Nothing was changed."
        exit 0
    }

    validate_image "$image_file"
    show_removable_devices

    if ! ask_yes_no \
        "Continue to Raspberry Pi Imager" \
        "The selected image is:

$image_file

Continue and open Raspberry Pi Imager?"; then
        info "Cancelled. Nothing was written."
        exit 0
    fi

    launch_imager "$image_file"

    dialog_info \
        "Builder finished" \
        "Raspberry Pi Imager has closed.

If the write and verification completed successfully, safely eject the SD card and fit it to the separate Raspberry Pi / MMDVM hotspot.

On first boot, follow the official WPSD setup instructions."

    info "73 de ZL4SSB"
}

main "$@"
