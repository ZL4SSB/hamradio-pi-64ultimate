from __future__ import annotations
import json
import urllib.request
from datetime import datetime, timezone
from constants import PROPAGATION_URLS

HEADERS = {"User-Agent": "HamRadio-Pi-Ultimate/1.0"}

def _get_json(url: str, timeout: int = 10):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def _extract_summary_value(payload):
    if isinstance(payload, dict):
        for key in ("Flux", "flux", "value", "Value", "speed"):
            if key in payload:
                return str(payload[key])
        for value in payload.values():
            if isinstance(value, (str, int, float)):
                return str(value)
    if isinstance(payload, list) and payload:
        row = payload[-1]
        if isinstance(row, dict):
            return _extract_summary_value(row)
        if isinstance(row, list) and row:
            return str(row[-1])
    return "—"

def _latest_kp(payload):
    if not isinstance(payload, list) or len(payload) < 2:
        return "—"
    rows = payload[1:] if isinstance(payload[0], list) else payload
    row = rows[-1]
    if isinstance(row, list):
        # NOAA product typically: time_tag, Kp, ...
        for index in (1, 2):
            if len(row) > index:
                try:
                    return f"{float(row[index]):.1f}"
                except Exception:
                    pass
    if isinstance(row, dict):
        for key in ("Kp", "kp", "estimated_kp"):
            if key in row:
                return str(row[key])
    return "—"

def _scales(payload):
    current = payload.get("0", payload) if isinstance(payload, dict) else {}
    values = {}
    for key in ("R", "S", "G"):
        item = current.get(key, {}) if isinstance(current, dict) else {}
        value = item.get("Scale", item.get("scale", "0")) if isinstance(item, dict) else "0"
        values[key] = str(value)
    return values

def band_guidance(flux: float | None, kp: float | None) -> dict:
    if flux is None or kp is None:
        return {
            "80m": "Check local conditions",
            "40m": "Usually dependable",
            "20m": "Check live conditions",
            "15m": "Check live conditions",
            "10m": "Check live conditions",
        }
    disturbed = kp >= 5
    strong = flux >= 150
    moderate = flux >= 110
    return {
        "80m": "Noisy / auroral risk" if disturbed else "Good after dark",
        "40m": "Variable" if disturbed else "Good",
        "20m": "Poor polar paths" if disturbed else "Very good",
        "15m": "Fair" if moderate and not disturbed else "Limited",
        "10m": "Good" if strong and kp < 4 else "Sporadic / limited",
    }

def fetch_snapshot() -> dict:
    errors = []
    result = {
        "solar_flux": "—",
        "k_index": "—",
        "solar_wind": "—",
        "r_scale": "0",
        "s_scale": "0",
        "g_scale": "0",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    try:
        result["solar_flux"] = _extract_summary_value(_get_json(PROPAGATION_URLS["solar_flux"]))
    except Exception as exc:
        errors.append(f"Solar flux: {exc}")
    try:
        result["k_index"] = _latest_kp(_get_json(PROPAGATION_URLS["k_index"]))
    except Exception as exc:
        errors.append(f"K-index: {exc}")
    try:
        result["solar_wind"] = _extract_summary_value(_get_json(PROPAGATION_URLS["solar_wind"]))
    except Exception as exc:
        errors.append(f"Solar wind: {exc}")
    try:
        scales = _scales(_get_json(PROPAGATION_URLS["scales"]))
        result.update({
            "r_scale": scales["R"],
            "s_scale": scales["S"],
            "g_scale": scales["G"],
        })
    except Exception as exc:
        errors.append(f"NOAA scales: {exc}")

    try:
        flux = float(result["solar_flux"])
    except Exception:
        flux = None
    try:
        kp = float(result["k_index"])
    except Exception:
        kp = None

    result["bands"] = band_guidance(flux, kp)
    result["errors"] = errors
    return result
