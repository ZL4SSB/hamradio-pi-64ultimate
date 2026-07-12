#!/usr/bin/env bash
set -euo pipefail
echo "WPSD DEVICE BACKUP"
echo "=================="
lsblk -o NAME,PATH,SIZE,FSTYPE,TYPE,TRAN,RM,MOUNTPOINTS,MODEL
echo
read -r -p "Enter the complete SOURCE device path (example /dev/sdb): " SOURCE
[[ -b "$SOURCE" ]] || { echo "Not a block device: $SOURCE"; exit 1; }
read -r -p "Enter output image path (example $HOME/wpsd-backup.img): " OUTPUT
echo "Source: $SOURCE"
echo "Output: $OUTPUT"
read -r -p "Type BACKUP to continue: " CONFIRM
[[ "$CONFIRM" == "BACKUP" ]] || { echo "Cancelled."; exit 1; }
sudo dd if="$SOURCE" of="$OUTPUT" bs=4M status=progress conv=fsync
sync
echo "Backup complete: $OUTPUT"
