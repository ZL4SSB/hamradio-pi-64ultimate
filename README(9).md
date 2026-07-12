# HamRadio-Pi Ultimate v0.3.9

This update adds a one-command desktop installer for Raspberry Pi OS.

## Added

- Executable launcher:
  `scripts/hamradio-pi-ultimate`
- Desktop and menu installer:
  `scripts/install-desktop-launcher.sh`
- Launcher remover:
  `scripts/remove-desktop-launcher.sh`
- Desktop entry template:
  `desktop/hamradio-pi-ultimate.desktop`

## Install on Raspberry Pi OS

From the project directory:

```bash
chmod +x scripts/install-desktop-launcher.sh
./scripts/install-desktop-launcher.sh
```

This creates:

- a desktop icon
- a Raspberry Pi application-menu entry
- an executable command launcher

## Start manually

```bash
./scripts/hamradio-pi-ultimate
```

## Remove only the launchers

```bash
chmod +x scripts/remove-desktop-launcher.sh
./scripts/remove-desktop-launcher.sh
```

This does not delete the project.
