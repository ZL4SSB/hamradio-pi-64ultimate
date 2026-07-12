# HamRadio-Pi Ultimate v0.3.7c

This patch removes the duplicate Application Install button.

## Dashboard buttons

- Applications
- Build a Station
- WPSD SD Card Builder
- Hardware
- Updates
- Settings

## Replace

```text
src/dashboard.py
config/version.json
```

The old `src/activity_browser.py` file may remain in the repository for now, but it is no longer launched from the dashboard.

## Test

```powershell
python src/app.py
```

## Commit

```powershell
git add src/dashboard.py config/version.json
```

```powershell
git commit -m "Remove duplicate application installer"
```

```powershell
git push
```
