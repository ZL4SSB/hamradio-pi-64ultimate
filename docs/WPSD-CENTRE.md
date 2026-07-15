# WPSD Centre

WPSD Centre defines image download, removable-media detection, flashing,
verification, backup, restore and first-boot configuration. This build does not
include a privileged media-writing provider, so selecting a card opens this guide
and reports the capability unavailable instead of simulating success.

Before future flashing: back up the card, verify the image checksum, identify the
destination by size and device path, unmount its partitions, and confirm that all
existing data on it may be destroyed. Never target the running system disk.
