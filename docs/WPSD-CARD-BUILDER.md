# WPSD SD Card Builder

This module is an early HamRadio-Pi Ultimate tool for preparing an SD card for a **separate Raspberry Pi fitted with an MMDVM hotspot board**.

## What it does

- Installs Raspberry Pi Imager and small supporting utilities if needed.
- Opens the official WPSD download page.
- Lets the user select the downloaded `.img.xz` file.
- Runs an `xz` integrity test.
- Displays currently detected storage devices.
- Gives a strong warning before Raspberry Pi Imager is launched.
- Opens Raspberry Pi Imager for the actual write.

## What it deliberately does not do

- It does not write directly to a disk.
- It does not automatically select an SD card.
- It does not install WPSD on the Pi running HamRadio-Pi Ultimate.
- It does not flash MMDVM modem firmware.
- It does not bypass WPSD's official setup instructions.

## Run it

From the project directory:

```bash
chmod +x scripts/wpsd-card-builder.sh
./scripts/wpsd-card-builder.sh
```

## Install the desktop launcher

```bash
mkdir -p ~/.local/share/applications
cp desktop/wpsd-card-builder.desktop ~/.local/share/applications/
chmod +x ~/.local/share/applications/wpsd-card-builder.desktop
```

The long-term HamRadio-Pi Ultimate menu generator will place this launcher under:

`Ham Radio → Digital Voice`

## Safety

Raspberry Pi Imager erases the destination selected by the user. Always verify the model and capacity shown in Imager before writing.

Use an SD card of at least 8 GB and select the WPSD image matching the hotspot's Raspberry Pi and MMDVM hardware.
