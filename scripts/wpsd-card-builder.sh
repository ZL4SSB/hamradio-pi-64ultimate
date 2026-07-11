#!/usr/bin/env bash

set -Eeuo pipefail

WPSD_URL="https://w0chp.radio/wpsd/"
MIN_IMAGE_BYTES=$((100 * 1024 * 1024))

have_gui() {
    [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]]
}

install_requirements() {
    local missing=()
    command -v rpi-imager >/dev/null 2>&1 || missing+=(rpi-imager)
    command -v zenity >/dev/null 2>&1 || missing+=(zenity)
    command -v xdg-open >/dev/null 2>&1 || missing+=(xdg-utils)
    command -v xz >/dev/null 2>&1 || missing+=(xz-utils)

    if ((${#missing[@]})); then
        sudo apt update
        sudo apt install -y "${missing[@]}"
    fi
}

choose_image() {
    if command -v zenity >/dev/null 2>&1 && have_gui; then
        zenity --file-selection \
            --title="Select the downloaded WPSD image" \
            --filename="${HOME}/Downloads/" \
            --file-filter="WPSD compressed images | *.img.xz *.xz"
    else
        read -r -p "Full path to WPSD .img.xz file: " image
        printf '%s\n' "$image"
    fi
}

main() {
    install_requirements
    xdg-open "$WPSD_URL" >/dev/null 2>&1 &

    image=$(choose_image) || exit 0
    [[ -f "$image" ]] || { echo "Image not found."; exit 1; }
    [[ $(stat -c '%s' "$image") -ge $MIN_IMAGE_BYTES ]] || {
        echo "Image appears too small."; exit 1;
    }
    xz --test "$image"

    echo
    echo "WARNING: Raspberry Pi Imager will erase the device you select."
    lsblk -d -e 7 -o NAME,MODEL,SIZE,TRAN,RM,TYPE
    echo
    read -r -p "Open Raspberry Pi Imager now? [y/N]: " reply
    [[ "$reply" =~ ^[Yy]$ ]] || exit 0

    rpi-imager
}

main "$@"
