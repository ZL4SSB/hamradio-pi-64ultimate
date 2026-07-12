# HamRadio-Pi Ultimate 4.3.1

Raspberry Pi test release with an anonymous public installer.

## Important

The GitHub repository must be set to **Public**. Public downloads do not
require a GitHub account, username, password, or access token.

## One-command public installation

On a fresh Raspberry Pi OS Trixie installation:

```bash
sudo apt update
sudo apt install -y curl
curl -fsSL \
  https://raw.githubusercontent.com/zl4ssb/hamradio-pi-64ultimate/main/install-public.sh \
  -o /tmp/install-hamradio-pi.sh
chmod +x /tmp/install-hamradio-pi.sh
/tmp/install-hamradio-pi.sh
```

The public installer:

- downloads the project as a ZIP archive
- does not run `git clone`
- does not ask for GitHub credentials
- installs all required Qt, QML, USB and audio packages
- creates the application launcher and icon
- runs a Qt/QML self-test

Start afterward with:

```bash
~/.local/bin/hamradio-pi-ultimate
```

## Anonymous update

```bash
cd ~/hamradio-pi-64ultimate
./scripts/update-public.sh
```

## Local installation from an extracted ZIP

```bash
cd ~/hamradio-pi-64ultimate
chmod +x install.sh scripts/*.sh src/app.py
./install.sh
```
