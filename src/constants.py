from pathlib import Path

APP_NAME = "HamRadio-Pi Ultimate"
APP_VERSION = "0.5.0"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
SCRIPTS_DIR = BASE_DIR / "scripts"

COLORS = {
    "background": "#101722",
    "sidebar": "#0A111B",
    "panel": "#182334",
    "panel_alt": "#202D40",
    "border": "#2A3A52",
    "text": "#EEF4FA",
    "muted": "#9DAFC0",
    "teal": "#18B6A4",
    "teal_dark": "#0E8378",
    "teal_hover": "#159A8E",
    "success": "#49D6A5",
    "warning": "#F1C768",
    "danger": "#F2747C",
}
