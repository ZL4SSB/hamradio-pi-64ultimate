# HamRadio-Pi Ultimate modern GUI drop-in

This package supplies the first working version of the redesigned single-window
application.

It does not replace or modify the existing installer and WPSD shell scripts.
Copy the included `src/app.py` and `data/applications.json` into the repository.

## Test on Raspberry Pi

```bash
cd ~/hamradio-pi-64ultimate
chmod +x src/app.py
python3 src/app.py
```

The GUI uses Tkinter from the Python standard library. If Raspberry Pi OS says
Tkinter is missing:

```bash
sudo apt update
sudo apt install -y python3-tk
```

## Included features

- Single resizable window
- Left navigation sidebar
- Dark teal theme
- Hover tooltips
- Dashboard and activity log
- Application catalogue with install/launch state
- WPSD script launcher
- Read-only hardware detection
- Git update status page
- Settings storage
- Propagation-page foundation
- Background workers to avoid frozen windows

Version: 0.4.0-dev
