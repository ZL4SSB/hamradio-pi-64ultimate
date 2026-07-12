from __future__ import annotations

import os
import platform
import shutil
import socket
from pathlib import Path
from typing import Dict


def raspberry_pi_model() -> str:
    path = Path("/proc/device-tree/model")
    try:
        return path.read_text(encoding="utf-8").replace("\x00", "").strip()
    except OSError:
        return platform.machine() or "Unknown computer"


def cpu_temperature() -> str:
    paths = [
        Path("/sys/class/thermal/thermal_zone0/temp"),
        Path("/sys/class/hwmon/hwmon0/temp1_input"),
    ]
    for path in paths:
        try:
            raw = float(path.read_text().strip())
            value = raw / 1000 if raw > 1000 else raw
            return f"{value:.1f} °C"
        except (OSError, ValueError):
            continue
    return "Unavailable"


def memory_usage() -> tuple[str, str]:
    try:
        values: Dict[str, int] = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, raw = line.split(":", 1)
            values[key] = int(raw.strip().split()[0])
        total = values["MemTotal"]
        available = values["MemAvailable"]
        used = total - available
        return (
            f"{used / 1024 / 1024:.1f} GB",
            f"of {total / 1024 / 1024:.1f} GB used",
        )
    except Exception:
        return ("Unavailable", "")


def disk_usage() -> tuple[str, str]:
    try:
        total, used, free = shutil.disk_usage("/")
        return (
            f"{free / (1024 ** 3):.1f} GB free",
            f"{used / total * 100:.0f}% used",
        )
    except OSError:
        return ("Unavailable", "")


def local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("1.1.1.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "Not connected"
    finally:
        sock.close()


def internet_online() -> bool:
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=1.5).close()
        return True
    except OSError:
        return False


def system_snapshot() -> dict:
    mem_value, mem_detail = memory_usage()
    disk_value, disk_detail = disk_usage()
    online = internet_online()
    return {
        "model": (raspberry_pi_model(), platform.machine()),
        "temperature": (cpu_temperature(), "CPU temperature"),
        "memory": (mem_value, mem_detail),
        "disk": (disk_value, disk_detail),
        "network": ("Online" if online else "Offline", local_ip()),
        "os": (platform.system(), platform.release()),
    }
