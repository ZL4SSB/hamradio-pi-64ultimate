#!/usr/bin/env bash
set -euo pipefail

MENU_DIR="$HOME/.local/share/desktop-directories"
APP_DIR="$HOME/.local/share/applications"
mkdir -p "$MENU_DIR" "$APP_DIR"

cat > "$MENU_DIR/hamradio.directory" <<'EOF'
[Desktop Entry]
Type=Directory
Name=Ham Radio
Comment=Amateur radio applications and tools
Icon=network-wireless
EOF

python3 - <<'PY'
from pathlib import Path
app_dir = Path.home() / ".local/share/applications"
system_dirs = [Path("/usr/share/applications"), app_dir]
keywords = (
    "wsjt", "fldigi", "js8", "chirp", "gqrx", "gnuradio", "direwolf",
    "xastir", "gpredict", "qsstv", "cqrlog", "hamlib", "sdr", "radio"
)
for folder in system_dirs:
    if not folder.exists():
        continue
    for source in folder.glob("*.desktop"):
        text = source.read_text(errors="ignore")
        lower = (source.name + "\n" + text).lower()
        if not any(word in lower for word in keywords):
            continue
        target = app_dir / source.name
        if source != target:
            target.write_text(text)
        lines = target.read_text(errors="ignore").splitlines()
        output = []
        changed = False
        for line in lines:
            if line.startswith("Categories="):
                cats = [x for x in line.split("=", 1)[1].split(";") if x]
                if "HamRadio" not in cats:
                    cats.insert(0, "HamRadio")
                    changed = True
                line = "Categories=" + ";".join(cats) + ";"
            output.append(line)
        if not any(line.startswith("Categories=") for line in output):
            output.append("Categories=HamRadio;")
            changed = True
        if changed:
            target.write_text("\n".join(output) + "\n")
print("Ham Radio menu entries updated.")
PY

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DIR" || true
fi
