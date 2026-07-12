# HamRadio-Pi Ultimate v0.3.7

This update adds the first activity-based station workflow.

## Added

- Activities button on the dashboard.
- Searchable Activity Browser.
- Filters by category.
- Activity descriptions and included applications.
- Storage estimates.
- Beginner-friendly indicator.
- Raspberry Pi OS package installation for each activity.
- Safe Windows preview mode.

## Install

Add or replace:

```text
src/activity_browser.py
src/dashboard.py
src/data/activities.json
config/version.json
```

## Test

```powershell
python src/app.py
```

Then click **Activities**.

Try searching for:

- `FT8`
- `APRS`
- `MMDVM`
- `SDR`

On Windows, **Build This Activity** displays a safe preview message. On Raspberry Pi OS, it can install the activity's package set.

## Commit

```powershell
git add src/activity_browser.py src/dashboard.py src/data/activities.json config/version.json
```

```powershell
git commit -m "Add activity-based station builder"
```

```powershell
git push
```
