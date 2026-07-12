# HamRadio-Pi Ultimate v0.5.1

This patch fixes the startup crash in v0.5.0.

## Cause

The Quick Actions card used both `pack()` and `grid()` inside the same Tkinter container.

Tkinter does not allow those geometry managers to be mixed within one parent widget.

## Fix

The Quick Actions buttons now use a dedicated inner frame:

- the card itself continues using `pack()`
- the inner button frame uses `grid()`

## Replace

```text
src/app_shell.py
config/version.json
```

## Test

```powershell
python src/app.py
```

The modern dashboard should now open normally.

## Commit

```powershell
git add src/app_shell.py config/version.json
```

```powershell
git commit -m "Fix modern shell layout crash"
```

```powershell
git push
```
