#!/bin/bash

set -u

VERSION="0.3.4"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/install.log"

mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

show_header() {
    clear
    echo "=================================================="
    echo "             HamRadio-Pi Ultimate"
    echo "                  Version $VERSION"
    echo "=================================================="
    echo
    echo " One command. One wizard. One Ham Radio menu."
    echo
}

pause_screen() {
    echo
    read -r -p "Press ENTER to continue..."
}

run_system_checks() {
    "$PROJECT_DIR/scripts/system-check.sh" || {
        echo
        echo "The system check found a problem."
        pause_screen
        exit 1
    }
}

show_menu() {
    while true; do
        show_header
        echo "1) Run Station Setup Wizard"
        echo "2) Open HamRadio-Pi Ultimate"
        echo "3) Run WPSD SD Card Builder"
        echo "4) Check storage for Complete Collection"
        echo "0) Exit"
        echo
        read -r -p "Enter your choice: " choice

        case "$choice" in
            1) python3 "$PROJECT_DIR/src/station_wizard.py";;
            2) python3 "$PROJECT_DIR/src/app.py";;
            3) "$PROJECT_DIR/scripts/wpsd-card-builder.sh";;
            4) "$PROJECT_DIR/scripts/check-space.sh" FULL; pause_screen;;
            0) exit 0;;
            *) echo "Choose a number from 0 to 4."; pause_screen;;
        esac
    done
}

main() {
    show_header
    run_system_checks
    pause_screen
    show_menu
}

main
