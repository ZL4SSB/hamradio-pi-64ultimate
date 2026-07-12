# HamRadio-Pi Ultimate v0.5.0

This is the first full modern application shell.

## Major changes

- Single main application window
- Left sidebar navigation
- Teal accent colour
- Brighter white text
- Modern card layout
- Hover tooltips
- Global search
- Inline toast notifications
- Dashboard, Station, Applications, WPSD, Hardware, Station Health,
  Propagation, Weather, Settings, Updates and Help pages
- Reduced reliance on message boxes
- Existing detailed tools still open when needed

## Add or replace

```text
src/app.py
src/hamshack.py
src/app_shell.py
src/ui/__init__.py
src/ui/theme.py
src/ui/tooltip.py
src/ui/toast.py
config/version.json
```

## Test

```powershell
python src/app.py
```

Check:

1. Sidebar navigation
2. Teal buttons and white text
3. Hover help
4. Search for `weather`, `usb`, or `wsjt`
5. Weather refresh notification
6. Existing Applications, Hardware and Settings tools

## Commit

```powershell
git add src/app.py src/hamshack.py src/app_shell.py src/ui config/version.json
```

```powershell
git commit -m "Add modern single-window application shell"
```

```powershell
git push
```
