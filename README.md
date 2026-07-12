# HamRadio-Pi Ultimate 4.3.2

One-click Raspberry Pi test release.

## Easiest public installation

The repository must be public. No GitHub account or login is required.

Copy and paste this single command into a Raspberry Pi terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/zl4ssb/hamradio-pi-64ultimate/main/install-public.sh | bash
```

The installer automatically:

- downloads HamRadio-Pi Ultimate
- detects the Raspberry Pi OS environment
- installs only packages available for that OS
- handles Debian package-name changes
- installs PyQt6 and Qt Quick/QML
- creates the desktop launcher and icon
- runs a self-test
- starts the program when a graphical desktop is active

## Installing an extracted ZIP

Open a terminal inside the extracted folder and run:

```bash
chmod +x install.sh
./install.sh
```

## Starting later

From the desktop menu, select **HamRadio-Pi Ultimate**, or run:

```bash
hamradio-pi-ultimate
```

## Updating later

```bash
cd ~/hamradio-pi-64ultimate
./scripts/update-public.sh
```
