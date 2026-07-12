# HamRadio-Pi Ultimate v0.3.8

This update adds real hardware detection.

## Added

- Hardware Detection window.
- System and Raspberry Pi model information.
- USB device listing.
- Serial-port detection for CAT, GPS, and radio programming.
- Audio-device listing.
- Radio and SDR keyword hints.
- Windows development support.
- Raspberry Pi OS support.
- Top and bottom Close buttons.
- Escape key closes the window.

## Install

Add or replace:

```text
src/hardware.py
src/dashboard.py
config/version.json
```

## Test

```powershell
python src/app.py
```

Click **Hardware** and test each tab.

You can also test the tool directly:

```powershell
python src/hardware.py
```

## Commit

```powershell
git add src/hardware.py src/dashboard.py config/version.json
```

```powershell
git commit -m "Add hardware detection"
```

```powershell
git push
```
