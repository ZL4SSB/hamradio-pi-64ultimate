# HamRadio-Pi Ultimate v0.3.6

This update replaces the Applications pop-up with a full application browser.

## Added

- Search by name, activity, package, category, or description.
- Category filter.
- Application detail panel.
- Installed/not-installed status.
- Launch button for detected installed applications.
- Install button on Raspberry Pi OS.
- Windows development mode keeps installation disabled safely.

## Install

Replace or add:

```text
src/application_browser.py
src/dashboard.py
config/version.json
```

## Test

```powershell
python src/app.py
```

Then click **Applications**.

Try:

- searching for `FT8`
- selecting **Digital Modes**
- selecting an application
- checking that the detail panel updates

On Windows, Install remains disabled. On Raspberry Pi OS, it becomes available for missing packages.

## Commit

```powershell
git add src/application_browser.py src/dashboard.py config/version.json
```

```powershell
git commit -m "Add searchable application browser"
```

```powershell
git push
```
