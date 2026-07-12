# HamRadio-Pi Ultimate 4.3.0

Raspberry Pi test release using the approved dashboard design.

## Fresh Raspberry Pi installation from GitHub

```bash
sudo apt update
sudo apt install -y git
git clone https://github.com/zl4ssb/hamradio-pi-64ultimate.git
cd hamradio-pi-64ultimate
chmod +x install.sh scripts/*.sh src/app.py
./install.sh
```

`install.sh` automatically downloads the Qt 6, PyQt6, QML, USB and audio
dependencies required by the application.

Start the application with:

```bash
~/.local/bin/hamradio-pi-ultimate
```

or select **HamRadio-Pi Ultimate** from the desktop application menu.


## Dashboard changes

- Uses the selected dashboard design
- Logo is inside the Station Profile / system summary card
- Quick Actions is a full two-column panel
- Live Station Profile, CPU, load, disk, system information, services and activity

