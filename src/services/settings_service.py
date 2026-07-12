from __future__ import annotations
import json
from constants import CONFIG_DIR

DEFAULTS = {
    "callsign": "",
    "locator": "",
    "station_name": "",
    "auto_refresh_dashboard": True,
    "confirm_remove": True,
}

def load_settings() -> dict:
    path = CONFIG_DIR / "settings.json"
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        saved = {}
    result = DEFAULTS.copy()
    result.update(saved)
    return result

def save_settings(settings: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    (CONFIG_DIR / "settings.json").write_text(
        json.dumps(settings, indent=2) + "\n", encoding="utf-8"
    )
