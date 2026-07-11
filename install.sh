

#################################################
# HamRadio-Pi-64-Ultimate
# Simple Ham Radio Installer
#!/bin/bash

# ==========================================================
# HamRadio-Pi Ultimate
# Main Installer Engine
# Version 0.3.0
# ==========================================================

VERSION="0.3.0"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/install.log"

mkdir -p "$LOG_DIR"

# Save terminal output to both the screen and log file.
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
    "$PROJECT_DIR/scripts/system-check.sh"

    if [ $? -ne 0 ]; then
        echo
        echo "The system check found a problem."
        echo "Please correct it before continuing."
        pause_screen
        exit 1
    fi
}

check_install_space() {
    local install_type="$1"

    "$PROJECT_DIR/scripts/check-space.sh" "$install_type"
    return $?
}

show_reduced_menu() {
    while true; do
        show_header

        echo "There is not enough free space for the Complete Collection."
        echo
        echo "Choose a smaller installation:"
        echo
        echo "1) Digital Modes"
        echo "2) SDR Software"
        echo "3) APRS and Packet"
        echo "4) Satellite Tools"
        echo "5) Radio Programming"
        echo "6) Server Tools"
        echo "7) Return to Main Menu"
        echo
        read -r -p "Enter your choice: " reduced_choice

        case "$reduced_choice" in
            1) SELECTED_INSTALL="DIGITAL"; return 0 ;;
            2) SELECTED_INSTALL="SDR"; return 0 ;;
            3) SELECTED_INSTALL="APRS"; return 0 ;;
            4) SELECTED_INSTALL="SATELLITE"; return 0 ;;
            5) SELECTED_INSTALL="PROGRAMMING"; return 0 ;;
            6) SELECTED_INSTALL="SERVER"; return 0 ;;
            7) return 1 ;;
            *)
                echo
                echo "Please choose a number from 1 to 7."
                pause_screen
                ;;
        esac
    done
}

show_main_menu() {
    while true; do
        show_header

        echo "Choose an installation type:"
        echo
        echo "1) Recommended Ham Station"
        echo "2) Complete Collection"
        echo "3) Digital Modes"
        echo "4) SDR Software"
        echo "5) APRS and Packet"
        echo "6) Satellite Tools"
        echo "7) Radio Programming"
        echo "8) Headless Server"
        echo "9) Custom Installation"
        echo "0) Exit"
        echo
        read -r -p "Enter your choice: " choice

        case "$choice" in
            1)
                SELECTED_INSTALL="RECOMMENDED"
                break
                ;;
            2)
                SELECTED_INSTALL="FULL"

                if ! check_install_space "FULL"; then
                    pause_screen

                    if show_reduced_menu; then
                        break
                    fi
                else
                    break
                fi
                ;;
            3)
                SELECTED_INSTALL="DIGITAL"
                break
                ;;
            4)
                SELECTED_INSTALL="SDR"
                break
                ;;
            5)
                SELECTED_INSTALL="APRS"
                break
                ;;
            6)
                SELECTED_INSTALL="SATELLITE"
                break
                ;;
            7)
                SELECTED_INSTALL="PROGRAMMING"
                break
                ;;
            8)
                SELECTED_INSTALL="SERVER"
                break
                ;;
            9)
                SELECTED_INSTALL="CUSTOM"
                break
                ;;
            0)
                echo
                echo "Installer closed."
                exit 0
                ;;
            *)
                echo
                echo "Please choose a number from 0 to 9."
                pause_screen
                ;;
        esac
    done
}

show_selection() {
    show_header

    echo "Selected installation:"
    echo
    echo "  $SELECTED_INSTALL"
    echo
    echo "The software installation modules will be connected next."
    echo
    echo "No software has been installed by this test version."
    echo
    echo "Log file:"
    echo "  $LOG_FILE"
    echo
}

main() {
    show_header
    run_system_checks
    pause_screen

    show_main_menu
    show_selection
}

main
