# HamRadio-Pi Ultimate 4.1.1

Clean Qt Quick/QML full replacement.

## Changes in 4.1.1

- Rebuilt Applications page with a stable two-column GridView
- Added application search and category filtering
- Corrected application-card sizing and scrolling
- Made the left navigation scroll safely on smaller displays


## Windows 11

```powershell
Set-Location "C:\Users\zl4ss\OneDrive\Documents\GitHub\hamradio-pi-64ultimate"
python -m pip install --upgrade PyQt6
python .\src\app.py
```

The application forces Qt Quick Controls to use the cross-platform `Basic` style before PyQt6 loads.
