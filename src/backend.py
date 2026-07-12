from __future__ import annotations

import json
import platform
import shutil
import socket
import subprocess
import sys
import webbrowser
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, pyqtProperty, pyqtSignal, pyqtSlot

from constants import (
    APP_NAME,
    APP_VERSION,
    ASSETS_DIR,
    BASE_DIR,
    CONFIG_DIR,
    DATA_DIR,
    DONATE_URL,
    REPORTS_DIR,
)


class Backend(QObject):
    systemChanged = pyqtSignal()
    stationChanged = pyqtSignal()
    pageChanged = pyqtSignal()
    notificationChanged = pyqtSignal()
    applicationsChanged = pyqtSignal()
    devicesChanged = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._page = "Dashboard"
        self._notification = "System is ready."
        self._online = False
        self._cpu = "Preview"
        self._memory = 0
        self._disk = 0
        self._disk_detail = ""
        self._ip = "—"
        self._model = self._detect_model()
        self._os_name = self._detect_os()
        self._callsign = ""
        self._locator = ""
        self._applications: list[dict] = []
        self._devices: list[dict] = []
        self._last_scan = "Not run"
        self._latest_log = "Application started"

        self._load_station()
        self._load_applications()
        self.refreshSystem()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refreshSystem)
        self.timer.start(5000)

    @pyqtProperty(str, constant=True)
    def appName(self) -> str:
        return APP_NAME

    @pyqtProperty(str, constant=True)
    def appVersion(self) -> str:
        return APP_VERSION

    @pyqtProperty(str, constant=True)
    def assetRoot(self) -> str:
        return (ASSETS_DIR / "branding").resolve().as_uri()

    @pyqtProperty(str, notify=pageChanged)
    def currentPage(self) -> str:
        return self._page

    @pyqtProperty(str, notify=notificationChanged)
    def notification(self) -> str:
        return self._notification

    @pyqtProperty(bool, notify=systemChanged)
    def online(self) -> bool:
        return self._online

    @pyqtProperty(str, notify=systemChanged)
    def cpuTemp(self) -> str:
        return self._cpu

    @pyqtProperty(int, notify=systemChanged)
    def memoryPercent(self) -> int:
        return self._memory

    @pyqtProperty(int, notify=systemChanged)
    def diskPercent(self) -> int:
        return self._disk

    @pyqtProperty(str, notify=systemChanged)
    def diskDetail(self) -> str:
        return self._disk_detail

    @pyqtProperty(str, notify=systemChanged)
    def ipAddress(self) -> str:
        return self._ip

    @pyqtProperty(str, notify=systemChanged)
    def piModel(self) -> str:
        return self._model

    @pyqtProperty(str, notify=systemChanged)
    def osName(self) -> str:
        return self._os_name

    @pyqtProperty(str, notify=stationChanged)
    def callsign(self) -> str:
        return self._callsign or "Not configured"

    @pyqtProperty(str, notify=stationChanged)
    def locator(self) -> str:
        return self._locator or "Not configured"

    @pyqtProperty("QVariantList", notify=applicationsChanged)
    def applications(self):
        return self._applications

    @pyqtProperty("QVariantList", notify=devicesChanged)
    def devices(self):
        return self._devices

    @pyqtProperty(str, notify=devicesChanged)
    def lastHardwareScan(self) -> str:
        return self._last_scan

    @pyqtProperty(int, notify=devicesChanged)
    def usbDeviceCount(self) -> int:
        return len(self._devices)

    @pyqtProperty(str, notify=notificationChanged)
    def latestLog(self) -> str:
        return self._latest_log

    @pyqtSlot(str)
    def setPage(self, page: str) -> None:
        self._page = page
        self.pageChanged.emit()

    @pyqtSlot(str)
    def setNotification(self, message: str) -> None:
        self._notification = message
        self._latest_log = message
        self.notificationChanged.emit()

    @pyqtSlot()
    def openDonate(self) -> None:
        webbrowser.open(DONATE_URL)

    @pyqtSlot()
    def refreshSystem(self) -> None:
        self._online = self._check_online()
        self._cpu = self._read_temperature()
        self._memory = self._memory_usage()
        self._disk, self._disk_detail = self._disk_usage()
        self._ip = self._local_ip()
        self.systemChanged.emit()

    @pyqtSlot()
    def scanHardware(self) -> None:
        devices: list[dict] = []
        if shutil.which("lsusb"):
            text = self._run(["lsusb"])
            for line in text.splitlines():
                if not line.strip():
                    continue
                lower = line.lower()
                name = "USB Device"
                icon = "USB"
                if "rtl" in lower or "realtek" in lower:
                    name, icon = "RTL-SDR Receiver", "SDR"
                elif any(key in lower for key in ("ftdi", "ch340", "cp210")):
                    name, icon = "CAT / Serial Interface", "CAT"
                elif "audio" in lower or "cm108" in lower:
                    name, icon = "USB Audio Device", "AUD"
                devices.append({
                    "name": name,
                    "detail": line,
                    "icon": icon,
                    "status": "Connected",
                })

        if not devices:
            devices = [{
                "name": "Windows 11 Preview",
                "detail": "Full USB hardware detection is enabled on Raspberry Pi OS.",
                "icon": "PC",
                "status": "Preview",
            }]

        self._devices = devices
        self._last_scan = "Just now"
        self._notification = f"Hardware scan completed — {len(devices)} result(s)."
        self._latest_log = self._notification
        self.devicesChanged.emit()
        self.notificationChanged.emit()

    @pyqtSlot(str)
    def launchApplication(self, command: str) -> None:
        if not command:
            return
        try:
            subprocess.Popen([command], start_new_session=True)
            self.setNotification(f"Launched {command}.")
        except Exception as exc:
            self.setNotification(f"Could not launch {command}: {exc}")

    @pyqtSlot(str, str)
    def saveStation(self, callsign: str, locator: str) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        settings = self._read_settings()
        settings["callsign"] = callsign.strip().upper()
        settings["locator"] = locator.strip().upper()
        (CONFIG_DIR / "settings.json").write_text(
            json.dumps(settings, indent=2) + "\n",
            encoding="utf-8",
        )
        self._load_station()
        self.stationChanged.emit()
        self.setNotification("Station details saved.")

    @pyqtSlot(result=str)
    def createSystemReport(self) -> str:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / "system-report.txt"
        path.write_text(
            "\n".join([
                f"{APP_NAME} {APP_VERSION}",
                f"Platform: {platform.platform()}",
                f"Python: {sys.version}",
                f"Model: {self._model}",
                f"OS: {self._os_name}",
                f"CPU: {self._cpu}",
                f"Memory: {self._memory}%",
                f"Disk: {self._disk}% ({self._disk_detail})",
                f"IP: {self._ip}",
                f"Callsign: {self.callsign}",
                f"Locator: {self.locator}",
            ]) + "\n",
            encoding="utf-8",
        )
        self.setNotification(f"System report created: {path}")
        return str(path)

    def _read_settings(self) -> dict:
        try:
            return json.loads(
                (CONFIG_DIR / "settings.json").read_text(encoding="utf-8")
            )
        except Exception:
            return {}

    def _load_station(self) -> None:
        settings = self._read_settings()
        self._callsign = settings.get("callsign", "")
        self._locator = settings.get("locator", "")

    def _load_applications(self) -> None:
        try:
            values = json.loads(
                (DATA_DIR / "applications.json").read_text(encoding="utf-8")
            )
        except Exception:
            values = []
        self._applications = [
            {
                **item,
                "installed": shutil.which(item.get("command", "")) is not None,
            }
            for item in values
        ]

    def _detect_model(self) -> str:
        path = Path("/proc/device-tree/model")
        try:
            return path.read_text(encoding="utf-8").replace("\x00", "").strip()
        except Exception:
            return "Windows 11 Preview"

    def _detect_os(self) -> str:
        if platform.system() == "Windows":
            return f"Windows {platform.release()}"
        return platform.platform()

    def _read_temperature(self) -> str:
        for path in (
            Path("/sys/class/thermal/thermal_zone0/temp"),
            Path("/sys/class/hwmon/hwmon0/temp1_input"),
        ):
            try:
                raw = float(path.read_text().strip())
                value = raw / 1000 if raw > 1000 else raw
                return f"{value:.0f}°C"
            except Exception:
                continue
        return "Preview"

    def _memory_usage(self) -> int:
        path = Path("/proc/meminfo")
        if path.exists():
            try:
                values: dict[str, int] = {}
                for line in path.read_text().splitlines():
                    key, raw = line.split(":", 1)
                    values[key] = int(raw.strip().split()[0])
                total = values["MemTotal"]
                available = values["MemAvailable"]
                return int(round((total - available) / total * 100))
            except Exception:
                pass
        return 34

    def _disk_usage(self) -> tuple[int, str]:
        total, used, _free = shutil.disk_usage(BASE_DIR)
        percent = int(round(used / total * 100))
        detail = f"{used / 1024**3:.1f} GB / {total / 1024**3:.1f} GB"
        return percent, detail

    def _check_online(self) -> bool:
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=1).close()
            return True
        except Exception:
            return False

    def _local_ip(self) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("1.1.1.1", 80))
            return sock.getsockname()[0]
        except Exception:
            return "Offline"
        finally:
            sock.close()

    def _run(self, command: list[str]) -> str:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=8,
            )
            return (result.stdout + result.stderr).strip()
        except Exception:
            return ""
