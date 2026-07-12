from pathlib import Path

APP_NAME = "HamRadio-Pi Ultimate"
APP_VERSION = "4.1.0"

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
REPORTS_DIR = BASE_DIR / "reports"
SCRIPTS_DIR = BASE_DIR / "scripts"

DONATE_URL = (
    "https://www.paypal.com/cgi-bin/webscr"
    "?cmd=_donations"
    "&business=zl4ssb.glen%40gmail.com"
    "&currency_code=USD"
    "&amount=1.00"
)
