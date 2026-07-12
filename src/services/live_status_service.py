from __future__ import annotations

from services.system_service import cpu_temperature, local_ip, memory_usage, internet_online, raspberry_pi_model
from services.settings_service import load_settings

def top_status_snapshot() -> dict:
    settings = load_settings()
    memory_value, memory_detail = memory_usage()
    try:
        used = float(memory_value.split()[0])
        total = float(memory_detail.split()[1])
        memory_percent = int(round((used / total) * 100))
    except Exception:
        memory_percent = None

    return {
        "online": internet_online(),
        "temperature": cpu_temperature(),
        "memory_percent": memory_percent,
        "ip": local_ip(),
        "model": raspberry_pi_model(),
        "callsign": settings.get("callsign", "") or "No callsign",
        "locator": settings.get("locator", "") or "No locator",
    }
