from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class HardwareItem:
    name: str
    kind: str
    detail: str
    recommendation: str


def _run(command: list[str], timeout: int = 8) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        return (result.stdout + result.stderr).strip()
    except Exception:
        return ""


def scan_hardware() -> list[HardwareItem]:
    items: list[HardwareItem] = []
    usb = _run(["lsusb"]) if shutil.which("lsusb") else ""

    rules = [
        (r"RTL2832|Realtek.*2838", "RTL-SDR receiver", "SDR", "Install GQRX, rtl-sdr and SDR++"),
        (r"FT232|FTDI", "FTDI serial interface", "CAT / Serial", "Useful for radio CAT control"),
        (r"CH340|CH341", "CH340 serial interface", "CAT / Serial", "Useful for programming and CAT control"),
        (r"CP210", "CP210x serial interface", "CAT / Serial", "Useful for radio or hotspot control"),
        (r"CM108|CM119", "CM108 USB audio device", "Audio", "Useful for packet, AllStar and digital modes"),
        (r"HackRF", "HackRF", "SDR", "Install GNU Radio and SDR tools"),
        (r"Airspy", "Airspy receiver", "SDR", "Install compatible SDR software"),
        (r"LimeSDR|Myriad", "LimeSDR", "SDR", "Install LimeSuite and GNU Radio"),
        (r"PlutoSDR|Analog Devices", "ADALM-Pluto", "SDR", "Install libiio and SDR tools"),
        (r"GPS|u-blox", "GPS receiver", "Navigation", "Useful for APRS and precise time"),
    ]

    for pattern, name, kind, recommendation in rules:
        match = re.search(pattern, usb, re.IGNORECASE)
        if match:
            detail = next((line for line in usb.splitlines() if re.search(pattern, line, re.IGNORECASE)), match.group(0))
            items.append(HardwareItem(name, kind, detail, recommendation))

    serial = _run(["bash", "-lc", "ls -1 /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true"])
    for device in [line.strip() for line in serial.splitlines() if line.strip()]:
        if not any(device in item.detail for item in items):
            items.append(HardwareItem("USB serial device", "CAT / Serial", device, "May be a CAT, programming or hotspot interface"))

    audio = _run(["bash", "-lc", "arecord -l 2>/dev/null || true"])
    if audio and "no soundcards" not in audio.lower():
        for line in audio.splitlines():
            if line.startswith("card "):
                items.append(HardwareItem("Audio capture device", "Audio", line, "Useful for digital modes and packet"))

    if not items:
        items.append(HardwareItem(
            "No supported radio hardware identified",
            "Information",
            "The scan completed but did not match known hardware rules.",
            "You can still install applications manually."
        ))

    return items
