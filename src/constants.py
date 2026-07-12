from pathlib import Path

APP_NAME = "HamRadio-Pi Ultimate"
APP_VERSION = "2.1.0"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
SCRIPTS_DIR = BASE_DIR / "scripts"
DOCS_DIR = BASE_DIR / "docs"
REPORTS_DIR = BASE_DIR / "reports"
ASSETS_DIR = BASE_DIR / "assets"

COLORS = {
    "background": "#0F1621",
    "background_alt": "#121C29",
    "sidebar": "#09111B",
    "sidebar_hover": "#132131",
    "panel": "#182535",
    "panel_alt": "#202F43",
    "panel_soft": "#152131",
    "border": "#2A3D55",
    "text": "#F1F6FB",
    "muted": "#9CB0C3",
    "teal": "#19C2AF",
    "teal_dark": "#0F887C",
    "teal_hover": "#16A596",
    "success": "#4BD9A8",
    "warning": "#F0C76D",
    "danger": "#F17982",
    "blue": "#66A8FF",
}

PROPAGATION_URLS = {
    "solar_flux": "https://services.swpc.noaa.gov/products/summary/10cm-flux.json",
    "k_index": "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json",
    "scales": "https://services.swpc.noaa.gov/products/noaa-scales.json",
    "solar_wind": "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json",
}

DONATE_URL = "https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=zl4ssb.glen%40paypal.com&currency_code=USD&amount=1.00"
