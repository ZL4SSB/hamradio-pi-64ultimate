# HamRadio-Pi Ultimate v0.6.0

This update adds dedicated weak-signal propagation tools.

## Added to Propagation

- PSK Reporter
- VKSpotter
- Modern information cards
- Hover descriptions
- External browser launching
- Inline success or error notifications

Both services open outside the main HamRadio-Pi Ultimate interface, so the
main program remains available.

Python requests a new browser window. Some browser settings may choose a new
tab instead.

## Replace

```text
src/app_shell.py
config/version.json
```

## Test

```powershell
python src/app.py
```

Open **Propagation**, then test:

- **Open PSK Reporter**
- **Open VKSpotter**

## Commit

```powershell
git add src/app_shell.py config/version.json
git commit -m "Add PSK Reporter and VKSpotter propagation tools"
git push
```
