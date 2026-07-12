# HamRadio-Pi Ultimate v0.3.7b

This update renames **Activities** to **Application Install**.

## Changes

- Dashboard button is now **Application Install**.
- Application Install window has clearer installation wording.
- Added top-right and bottom-right Close buttons.
- Pressing Esc closes the window.
- Existing activity-based groups remain unchanged underneath.
- Existing Applications button is renamed **Installed Applications**.

## Files

Replace:

```text
src/activity_browser.py
src/dashboard.py
config/version.json
```

## Test

```powershell
python src/app.py
```

Click **Application Install**.

## Commit

```powershell
git add src/activity_browser.py src/dashboard.py config/version.json
```

```powershell
git commit -m "Rename Activities to Application Install"
```

```powershell
git push
```
