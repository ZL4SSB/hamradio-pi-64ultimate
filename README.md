# HamRadio-Pi Ultimate 4.1.0

Clean Qt Quick/QML replacement build.

## Windows 11

```powershell
Set-Location "C:\Users\zl4ss\OneDrive\Documents\GitHub\hamradio-pi-64ultimate"
python -m pip install --upgrade PyQt6
python .\src\app.py
```

The application forces the Qt Quick Controls `Basic` style before importing
PyQt6, avoiding the optional Windows native-style plugin failure.

## Raspberry Pi OS Trixie

```bash
chmod +x install-qml.sh scripts/*.sh src/app.py
./install-qml.sh
./scripts/start-ultimate.sh
```

## Donation address

`zl4ssb.glen@gmail.com`
