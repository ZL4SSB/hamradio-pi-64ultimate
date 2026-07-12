#!/usr/bin/env bash
set -euo pipefail
echo "WPSD IMAGE RESTORE"
echo "=================="
lsblk -o NAME,PATH,SIZE,FSTYPE,TYPE,TRAN,RM,MOUNTPOINTS,MODEL
echo
read -r -p "Enter image file path: " IMAGE
[[ -f "$IMAGE" ]] || { echo "Image not found: $IMAGE"; exit 1; }
read -r -p "Enter complete TARGET device path (example /dev/sdb): " TARGET
[[ -b "$TARGET" ]] || { echo "Not a block device: $TARGET"; exit 1; }
echo
echo "WARNING: ALL DATA ON $TARGET WILL BE DESTROYED."
read -r -p "Type the exact target path again to continue: " CONFIRM
[[ "$CONFIRM" == "$TARGET" ]] || { echo "Cancelled."; exit 1; }
sudo umount "${TARGET}"* 2>/dev/null || true
case "$IMAGE" in
  *.xz) xzcat "$IMAGE" | sudo dd of="$TARGET" bs=4M status=progress conv=fsync ;;
  *.gz) gzip -dc "$IMAGE" | sudo dd of="$TARGET" bs=4M status=progress conv=fsync ;;
  *) sudo dd if="$IMAGE" of="$TARGET" bs=4M status=progress conv=fsync ;;
esac
sync
echo "Restore complete."
