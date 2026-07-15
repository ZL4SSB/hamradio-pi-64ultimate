"""Independent HRPU station-domain services.

No hardware or network adapter is enabled implicitly.  Every snapshot records
whether values are measured, modelled, preview, or unavailable.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Protocol


def maidenhead_to_latlon(locator: str) -> tuple[float, float]:
    value = locator.strip().upper()
    if len(value) not in (4, 6, 8) or not value[:2].isalpha() or not value[2:4].isdigit():
        raise ValueError("Maidenhead locator must contain 4, 6, or 8 valid characters")
    lon = (ord(value[0]) - 65) * 20.0 - 180.0
    lat = (ord(value[1]) - 65) * 10.0 - 90.0
    lon += int(value[2]) * 2.0
    lat += int(value[3])
    lon_step, lat_step = 2.0, 1.0
    if len(value) >= 6:
        if not value[4:6].isalpha() or not ("A" <= value[4] <= "X" and "A" <= value[5] <= "X"):
            raise ValueError("Invalid Maidenhead subsquare")
        lon_step, lat_step = 2.0 / 24.0, 1.0 / 24.0
        lon += (ord(value[4]) - 65) * lon_step
        lat += (ord(value[5]) - 65) * lat_step
    if len(value) == 8:
        if not value[6:8].isdigit():
            raise ValueError("Invalid Maidenhead extended square")
        lon_step /= 10.0
        lat_step /= 10.0
        lon += int(value[6]) * lon_step
        lat += int(value[7]) * lat_step
    return lat + lat_step / 2.0, lon + lon_step / 2.0


def path_geometry(source: tuple[float, float], target: tuple[float, float]) -> dict[str, float]:
    lat1, lon1, lat2, lon2 = map(math.radians, (*source, *target))
    dlon = lon2 - lon1
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    short = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
    a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    distance = 6371.0088 * 2 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1-a)))
    return {"short_bearing": short, "long_bearing": (short + 180.0) % 360.0,
            "distance_km": distance, "long_distance_km": 40030.2 - distance}


class Provider(Protocol):
    provider_id: str
    def available(self) -> bool: ...
    def snapshot(self) -> dict[str, Any]: ...


class UnavailableProvider:
    def __init__(self, provider_id: str, capability: str) -> None:
        self.provider_id, self.capability = provider_id, capability
    def available(self) -> bool: return False
    def snapshot(self) -> dict[str, Any]:
        return {"provider": self.provider_id, "capability": self.capability,
                "status": "unavailable", "live": False, "data": None}


@dataclass(frozen=True)
class PropagationRequest:
    source: tuple[float, float]
    target: tuple[float, float]
    frequency_hz: int
    utc: datetime
    month: int


class PropagationEngine:
    """Model/evidence boundary; it never manufactures missing observations."""
    def __init__(self, model: Provider | None = None, evidence: dict[str, Provider] | None = None):
        self.model = model or UnavailableProvider("none", "path-model")
        self.evidence = evidence or {}
    def evaluate(self, request: PropagationRequest) -> dict[str, Any]:
        model = self.model.snapshot()
        observed = {name: provider.snapshot() for name, provider in self.evidence.items()}
        available = [v for v in observed.values() if v.get("status") == "available"]
        return {"request": asdict(request), "model": model, "observed": observed,
                "predicted_muf_mhz": None, "path_mode": None,
                "model_reliability": None, "path_confidence": None,
                "status": "available" if model.get("status") == "available" else "unavailable",
                "evidence_sources_available": len(available)}


class BeaconScheduleService:
    CALLSIGNS = ("4U1UN", "VE8AT", "W6WX", "KH6WO", "ZL6B", "VK6RBP", "JA2IGY",
                 "RR9O", "VR2B", "4S7B", "ZS6DN", "5Z4B", "4X6TU", "OH2B", "CS3B",
                 "LU4AA", "OA4B", "YV5B")
    FREQUENCIES_MHZ = (14.100, 18.110, 21.150, 24.930, 28.200)
    def snapshot(self, now: datetime | None = None) -> dict[str, Any]:
        now = now or datetime.now(timezone.utc)
        second = int(now.timestamp())
        slot = (second // 10) % len(self.CALLSIGNS)
        return {"current": self.CALLSIGNS[slot], "next": self.CALLSIGNS[(slot+1) % len(self.CALLSIGNS)],
                "seconds_to_next": 10 - second % 10, "frequencies_mhz": self.FREQUENCIES_MHZ,
                "source": "documented schedule", "live": False}


class HardwareBoardService:
    """Safe provider boundary; UI code never touches GPIO directly."""
    OUTPUTS = ("ptt1", "ptt2", "band", "antenna", "rotator_cw", "rotator_ccw", "brake", "aux")
    def __init__(self, provider: Provider | None = None):
        self.provider = provider or UnavailableProvider("none", "HRPU hardware board")
    def snapshot(self) -> dict[str, Any]:
        return {"outputs": self.OUTPUTS, "provider": self.provider.snapshot(), "armed": False}
