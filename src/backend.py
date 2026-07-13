from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
import webbrowser
from datetime import datetime
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
    servicesChanged = pyqtSignal()
    activityChanged = pyqtSignal()
    dashboardsChanged = pyqtSignal()
    dashboardSelectionChanged = pyqtSignal()
    propagationChanged = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self._page = "Dashboard"
        self._notification = "System is ready."
        self._online = False
        self._cpu_temp = "—"
        self._system_load = "—"
        self._load_detail = "—"
        self._memory_percent = 0
        self._memory_detail = "—"
        self._disk_percent = 0
        self._disk_detail = "—"
        self._ip = "—"
        self._model = self._detect_model()
        self._os_name = self._detect_os()
        self._kernel = platform.release()
        self._hostname = socket.gethostname()
        self._uptime = "—"
        self._last_boot = "—"
        self._sd_card = "System disk"

        self._callsign = ""
        self._locator = ""
        self._operator_name = ""
        self._qth = ""
        self._country = ""
        self._dmr_id = ""

        self._theme = "Dark"
        self._show_splash = True
        self._auto_scan = False
        self._check_updates = True
        self._hamclock_url = ""

        self._applications: list[dict] = []
        self._devices: list[dict] = []
        self._services: list[dict] = []
        self._activity: list[dict] = []
        self._last_scan = "Not run"
        self._dashboards: list[dict] = []
        self._selected_dashboard_index = 0
        self._dashboard_status = "Ready"

        self._propagation_loading = False
        self._propagation_status = "Waiting for first update"
        self._propagation_updated = "Never"
        self._solar_flux = "—"
        self._kp_index = "—"
        self._solar_wind_speed = "—"
        self._solar_wind_density = "—"
        self._solar_wind_bz = "—"
        self._xray_class = "—"
        self._geomagnetic_state = "Unknown"
        self._hf_conditions = []

        self._load_settings()
        self._load_dashboards()
        self._load_applications()
        self._add_activity("HamRadio-Pi Ultimate started")
        self.refreshSystem()
        self.refreshServices()
        self.refreshPropagation()

        self.system_timer = QTimer(self)
        self.system_timer.timeout.connect(self.refreshSystem)
        self.system_timer.start(5000)

        self.service_timer = QTimer(self)
        self.service_timer.timeout.connect(self.refreshServices)
        self.service_timer.start(30000)

        self.propagation_timer = QTimer(self)
        self.propagation_timer.timeout.connect(self.refreshPropagation)
        self.propagation_timer.start(300000)

    # --------------------------- Constants ---------------------------

    @pyqtProperty(str, constant=True)
    def appName(self) -> str:
        return APP_NAME

    @pyqtProperty(str, constant=True)
    def appVersion(self) -> str:
        return APP_VERSION

    @pyqtProperty(str, constant=True)
    def assetRoot(self) -> str:
        return (ASSETS_DIR / "branding").resolve().as_uri()

    # ---------------------------- General ----------------------------

    @pyqtProperty(str, notify=pageChanged)
    def currentPage(self) -> str:
        return self._page

    @pyqtProperty(str, notify=notificationChanged)
    def notification(self) -> str:
        return self._notification

    @pyqtProperty(str, notify=systemChanged)
    def currentDateTime(self) -> str:
        return datetime.now().strftime("%d %B %Y | %I:%M %p")

    @pyqtProperty(bool, notify=systemChanged)
    def online(self) -> bool:
        return self._online

    # ----------------------------- System ----------------------------

    @pyqtProperty(str, notify=systemChanged)
    def cpuTemp(self) -> str:
        return self._cpu_temp

    @pyqtProperty(str, notify=systemChanged)
    def systemLoad(self) -> str:
        return self._system_load

    @pyqtProperty(str, notify=systemChanged)
    def loadDetail(self) -> str:
        return self._load_detail

    @pyqtProperty(int, notify=systemChanged)
    def memoryPercent(self) -> int:
        return self._memory_percent

    @pyqtProperty(str, notify=systemChanged)
    def memoryDetail(self) -> str:
        return self._memory_detail

    @pyqtProperty(int, notify=systemChanged)
    def diskPercent(self) -> int:
        return self._disk_percent

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

    @pyqtProperty(str, notify=systemChanged)
    def kernel(self) -> str:
        return self._kernel

    @pyqtProperty(str, notify=systemChanged)
    def hostname(self) -> str:
        return self._hostname

    @pyqtProperty(str, notify=systemChanged)
    def uptime(self) -> str:
        return self._uptime

    @pyqtProperty(str, notify=systemChanged)
    def lastBoot(self) -> str:
        return self._last_boot

    @pyqtProperty(str, notify=systemChanged)
    def sdCard(self) -> str:
        return self._sd_card

    # ----------------------------- Station ---------------------------

    @pyqtProperty(str, notify=stationChanged)
    def callsign(self) -> str:
        return self._callsign or "Not configured"

    @pyqtProperty(str, notify=stationChanged)
    def locator(self) -> str:
        return self._locator or "Not configured"

    @pyqtProperty(str, notify=stationChanged)
    def operatorName(self) -> str:
        return self._operator_name or "Not configured"

    @pyqtProperty(str, notify=stationChanged)
    def qth(self) -> str:
        return self._qth or "Not configured"

    @pyqtProperty(str, notify=stationChanged)
    def country(self) -> str:
        return self._country

    @pyqtProperty(str, notify=stationChanged)
    def dmrId(self) -> str:
        return self._dmr_id or "Not configured"

    # --------------------------- Preferences -------------------------

    @pyqtProperty(str, notify=stationChanged)
    def themeName(self) -> str:
        return self._theme

    @pyqtProperty(bool, notify=stationChanged)
    def showSplash(self) -> bool:
        return self._show_splash

    @pyqtProperty(bool, notify=stationChanged)
    def autoScan(self) -> bool:
        return self._auto_scan

    @pyqtProperty(bool, notify=stationChanged)
    def checkUpdates(self) -> bool:
        return self._check_updates

    @pyqtProperty(str, notify=stationChanged)
    def hamClockUrl(self) -> str:
        return self._hamclock_url

    # -------------------------- Dynamic lists ------------------------

    @pyqtProperty("QVariantList", notify=applicationsChanged)
    def applications(self):
        return self._applications

    @pyqtProperty("QVariantList", notify=devicesChanged)
    def devices(self):
        return self._devices

    @pyqtProperty("QVariantList", notify=servicesChanged)
    def activeServices(self):
        return self._services

    @pyqtProperty("QVariantList", notify=activityChanged)
    def recentActivity(self):
        return self._activity

    @pyqtProperty(str, notify=devicesChanged)
    def lastHardwareScan(self) -> str:
        return self._last_scan

    @pyqtProperty("QVariantList", notify=dashboardsChanged)
    def dashboards(self):
        return self._dashboards

    @pyqtProperty(int, notify=dashboardSelectionChanged)
    def selectedDashboardIndex(self) -> int:
        return self._selected_dashboard_index

    @pyqtProperty(str, notify=dashboardSelectionChanged)
    def selectedDashboardName(self) -> str:
        if 0 <= self._selected_dashboard_index < len(self._dashboards):
            return self._dashboards[self._selected_dashboard_index]["name"]
        return ""

    @pyqtProperty(str, notify=dashboardSelectionChanged)
    def selectedDashboardUrl(self) -> str:
        if 0 <= self._selected_dashboard_index < len(self._dashboards):
            return self._dashboards[self._selected_dashboard_index]["url"]
        return "about:blank"

    @pyqtProperty(str, notify=dashboardSelectionChanged)
    def selectedDashboardHomeUrl(self) -> str:
        if 0 <= self._selected_dashboard_index < len(self._dashboards):
            item = self._dashboards[self._selected_dashboard_index]
            return item.get("home_url", item["url"])
        return "about:blank"

    @pyqtProperty(str, notify=dashboardSelectionChanged)
    def dashboardStatus(self) -> str:
        return self._dashboard_status

    @pyqtProperty(bool, notify=propagationChanged)
    def propagationLoading(self) -> bool:
        return self._propagation_loading

    @pyqtProperty(str, notify=propagationChanged)
    def propagationStatus(self) -> str:
        return self._propagation_status

    @pyqtProperty(str, notify=propagationChanged)
    def propagationUpdated(self) -> str:
        return self._propagation_updated

    @pyqtProperty(str, notify=propagationChanged)
    def solarFlux(self) -> str:
        return self._solar_flux

    @pyqtProperty(str, notify=propagationChanged)
    def kpIndex(self) -> str:
        return self._kp_index

    @pyqtProperty(str, notify=propagationChanged)
    def solarWindSpeed(self) -> str:
        return self._solar_wind_speed

    @pyqtProperty(str, notify=propagationChanged)
    def solarWindDensity(self) -> str:
        return self._solar_wind_density

    @pyqtProperty(str, notify=propagationChanged)
    def solarWindBz(self) -> str:
        return self._solar_wind_bz

    @pyqtProperty(str, notify=propagationChanged)
    def xrayClass(self) -> str:
        return self._xray_class

    @pyqtProperty(str, notify=propagationChanged)
    def geomagneticState(self) -> str:
        return self._geomagnetic_state

    @pyqtProperty("QVariantList", notify=propagationChanged)
    def hfConditions(self):
        return self._hf_conditions

    # ------------------------------ Slots ----------------------------

    @pyqtSlot(str)
    def setPage(self, page: str) -> None:
        self._page = page
        self.pageChanged.emit()

    @pyqtSlot(str)
    def setNotification(self, message: str) -> None:
        self._notification = message
        self.notificationChanged.emit()

    @pyqtSlot()
    def openDonate(self) -> None:
        webbrowser.open(DONATE_URL)

    @pyqtSlot()
    def refreshSystem(self) -> None:
        self._online = self._check_online()
        self._cpu_temp = self._read_temperature()
        self._system_load, self._load_detail = self._read_load()
        self._memory_percent, self._memory_detail = self._memory_usage()
        self._disk_percent, self._disk_detail = self._disk_usage()
        self._ip = self._local_ip()
        self._uptime, self._last_boot = self._read_uptime()
        self.systemChanged.emit()

    @pyqtSlot()
    def refreshServices(self) -> None:
        candidates = [
            ("WSJT-X", "wsjtx"),
            ("Pi-Star", "pistar-watchdog"),
            ("CubicSDR", "cubicsdr"),
            ("FLDigi", "fldigi"),
            ("Dire Wolf", "direwolf"),
            ("GPredict", "gpredict"),
            ("KLog", "klog"),
            ("NTP", "systemd-timesyncd"),
        ]

        values = []
        for display, target in candidates:
            running = self._service_or_process_running(target)
            values.append({
                "name": display,
                "running": running,
            })

        self._services = values
        self.servicesChanged.emit()

    @pyqtSlot()
    def scanHardware(self) -> None:
        devices: list[dict] = []

        if shutil.which("lsusb"):
            output = self._run(["lsusb"])
            for line in output.splitlines():
                if not line.strip():
                    continue

                lower = line.lower()
                name = "USB Device"
                icon = "USB"

                if "rtl" in lower or "realtek" in lower:
                    name, icon = "RTL-SDR Receiver", "SDR"
                elif any(word in lower for word in ("ftdi", "ch340", "cp210")):
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
            devices.append({
                "name": "No external radio hardware detected",
                "detail": "Connect a radio, SDR, CAT cable or USB audio device and scan again.",
                "icon": "USB",
                "status": "Ready",
            })

        self._devices = devices
        self._last_scan = datetime.now().strftime("%d %b %Y %H:%M")
        self._notification = f"Hardware scan completed — {len(devices)} result(s)."
        self._add_activity("Hardware scan completed")
        self.devicesChanged.emit()
        self.notificationChanged.emit()

    @pyqtSlot(str)
    def launchApplication(self, command: str) -> None:
        if not command:
            return

        try:
            subprocess.Popen([command], start_new_session=True)
            self._notification = f"Launched {command}."
            self._add_activity(f"{command} started")
        except Exception as exc:
            self._notification = f"Could not launch {command}: {exc}"

        self.notificationChanged.emit()

    @pyqtSlot(str, str, str, str, str, str)
    def saveStation(
        self,
        callsign: str,
        locator: str,
        operator_name: str,
        qth: str,
        country: str,
        dmr_id: str,
    ) -> None:
        settings = self._read_settings()
        settings.update({
            "callsign": callsign.strip().upper(),
            "locator": locator.strip().upper(),
            "operator_name": operator_name.strip(),
            "qth": qth.strip(),
            "country": country.strip(),
            "dmr_id": dmr_id.strip(),
        })
        self._write_settings(settings)
        self._load_settings()
        self.stationChanged.emit()
        self._notification = "Station profile saved."
        self._add_activity("Station profile updated")
        self.notificationChanged.emit()

    @pyqtSlot(str, bool, bool, bool, str)
    def savePreferences(
        self,
        theme_name: str,
        show_splash: bool,
        auto_scan: bool,
        check_updates: bool,
        hamclock_url: str,
    ) -> None:
        settings = self._read_settings()
        settings.update({
            "theme": theme_name,
            "show_splash": bool(show_splash),
            "auto_scan": bool(auto_scan),
            "check_updates": bool(check_updates),
            "hamclock_url": self._normalise_web_url(hamclock_url),
        })
        self._write_settings(settings)
        self._load_settings()
        self.stationChanged.emit()
        self._notification = "Preferences saved."
        self.notificationChanged.emit()

    @pyqtSlot()
    def openHamClock(self) -> None:
        url = self._hamclock_url.strip()
        if not url:
            self._notification = (
                "HamClock URL is not configured. Open Preferences and enter its address."
            )
            self.notificationChanged.emit()
            self.setPage("Preferences")
            return

        webbrowser.open(url)
        self._notification = f"Opened HamClock: {url}"
        self._add_activity("HamClock opened in browser")
        self.notificationChanged.emit()

    @pyqtSlot(str, result=bool)
    def testWebUrl(self, url: str) -> bool:
        url = self._normalise_web_url(url)
        if not url:
            self._notification = "Enter a URL first."
            self.notificationChanged.emit()
            return False

        try:
            from urllib.request import Request, urlopen
            request = Request(
                url,
                headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"},
            )
            with urlopen(request, timeout=5) as response:
                ok = 200 <= response.status < 500
            self._notification = (
                "URL responded successfully."
                if ok
                else "The URL returned an unexpected response."
            )
        except Exception as exc:
            self._notification = f"Connection failed: {exc}"
            ok = False

        self.notificationChanged.emit()
        return ok

    @pyqtSlot(result=str)
    def createSystemReport(self) -> str:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / "system-report.txt"
        path.write_text(
            "\n".join([
                f"{APP_NAME} {APP_VERSION}",
                f"Generated: {datetime.now().isoformat(timespec='seconds')}",
                f"Hostname: {self._hostname}",
                f"Platform: {platform.platform()}",
                f"Python: {sys.version}",
                f"Model: {self._model}",
                f"OS: {self._os_name}",
                f"Kernel: {self._kernel}",
                f"Uptime: {self._uptime}",
                f"CPU temperature: {self._cpu_temp}",
                f"Load: {self._load_detail}",
                f"Memory: {self._memory_detail}",
                f"Disk: {self._disk_detail}",
                f"IP: {self._ip}",
                f"Callsign: {self.callsign}",
                f"Locator: {self.locator}",
            ]) + "\n",
            encoding="utf-8",
        )
        self._notification = f"System report created: {path}"
        self._add_activity("System report created")
        self.notificationChanged.emit()
        return str(path)

    @pyqtSlot()
    def checkForUpdates(self) -> None:
        if not (BASE_DIR / ".git").exists():
            self._notification = "Update check requires a Git clone."
            self.notificationChanged.emit()
            return

        try:
            subprocess.run(
                ["git", "-C", str(BASE_DIR), "fetch", "--quiet"],
                check=True,
                timeout=45,
            )
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(BASE_DIR),
                    "rev-list",
                    "--left-right",
                    "--count",
                    "HEAD...@{upstream}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                self._notification = "Update check completed; no upstream branch is configured."
            else:
                ahead, behind = result.stdout.strip().split()
                if int(behind) > 0:
                    self._notification = f"{behind} update(s) available from GitHub."
                else:
                    self._notification = "HamRadio-Pi Ultimate is up to date."

            self._add_activity("Update check completed")
        except Exception as exc:
            self._notification = f"Update check failed: {exc}"

        self.notificationChanged.emit()



    @pyqtSlot()
    def refreshPropagation(self) -> None:
        if self._propagation_loading:
            return

        self._propagation_loading = True
        self._propagation_status = "Downloading live NOAA space-weather data…"
        self.propagationChanged.emit()

        import threading

        worker = threading.Thread(
            target=self._fetch_propagation_worker,
            daemon=True,
        )
        worker.start()

    @pyqtSlot()
    def openNoaaSpaceWeather(self) -> None:
        webbrowser.open("https://www.spaceweather.gov/")

    def _fetch_propagation_worker(self) -> None:
        try:
            kp_data = self._download_json(
                "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
            )
            plasma_data = self._download_json(
                "https://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json"
            )
            mag_data = self._download_json(
                "https://services.swpc.noaa.gov/products/solar-wind/mag-7-day.json"
            )
            flux_data = self._download_json(
                "https://services.swpc.noaa.gov/json/solar-radio-flux.json"
            )
            xray_data = self._download_json(
                "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"
            )

            kp = self._latest_table_number(
                kp_data,
                ("kp", "Kp", "estimated_kp"),
            )
            speed = self._latest_table_number(
                plasma_data,
                ("speed",),
            )
            density = self._latest_table_number(
                plasma_data,
                ("density",),
            )
            bz = self._latest_table_number(
                mag_data,
                ("bz_gsm", "bz"),
            )
            flux = self._latest_solar_flux(flux_data)
            xray = self._latest_xray_class(xray_data)

            self._kp_index = self._format_number(kp, 1)
            self._solar_wind_speed = (
                f"{speed:.0f} km/s" if speed is not None else "—"
            )
            self._solar_wind_density = (
                f"{density:.1f} p/cm³" if density is not None else "—"
            )
            self._solar_wind_bz = (
                f"{bz:+.1f} nT" if bz is not None else "—"
            )
            self._solar_flux = (
                f"{flux:.0f} sfu" if flux is not None else "—"
            )
            self._xray_class = xray or "—"
            self._geomagnetic_state = self._kp_description(kp)
            self._hf_conditions = self._estimate_hf_conditions(
                flux,
                kp,
                xray,
            )
            self._propagation_updated = datetime.now().strftime(
                "%d %b %Y %H:%M"
            )
            self._propagation_status = "Live NOAA data received"
            self._add_activity("Propagation data refreshed")
        except Exception as exc:
            self._propagation_status = f"Update failed: {exc}"
        finally:
            self._propagation_loading = False
            self.propagationChanged.emit()

    @staticmethod
    def _download_json(url: str):
        from urllib.request import Request, urlopen

        request = Request(
            url,
            headers={
                "User-Agent": "HamRadio-Pi-Ultimate/4.5",
                "Accept": "application/json",
            },
        )
        with urlopen(request, timeout=15) as response:
            import json
            return json.load(response)

    @staticmethod
    def _table_rows(data):
        if not isinstance(data, list) or not data:
            return []

        if isinstance(data[0], list):
            headers = [str(value) for value in data[0]]
            rows = []
            for values in data[1:]:
                if not isinstance(values, list):
                    continue
                rows.append(dict(zip(headers, values)))
            return rows

        if isinstance(data[0], dict):
            return data

        return []

    @classmethod
    def _latest_table_number(cls, data, keys):
        rows = cls._table_rows(data)
        for row in reversed(rows):
            for key in keys:
                value = row.get(key)
                if value in (None, "", "null"):
                    continue
                try:
                    return float(value)
                except (TypeError, ValueError):
                    continue
        return None

    @classmethod
    def _latest_solar_flux(cls, data):
        rows = cls._table_rows(data)
        preferred = []

        for row in rows:
            frequency = str(
                row.get("frequency", row.get("freq", ""))
            ).lower()
            if "2800" in frequency or "2.8" in frequency:
                preferred.append(row)

        candidates = preferred or rows

        for row in reversed(candidates):
            for key in (
                "flux",
                "observed_flux",
                "adjusted_flux",
                "value",
            ):
                value = row.get(key)
                try:
                    number = float(value)
                    if number > 0:
                        return number
                except (TypeError, ValueError):
                    continue

        return None

    @classmethod
    def _latest_xray_class(cls, data):
        rows = cls._table_rows(data)
        best_flux = None

        for row in reversed(rows):
            energy = str(row.get("energy", "")).lower()
            if energy and "0.1-0.8" not in energy:
                continue

            try:
                flux = float(row.get("flux"))
            except (TypeError, ValueError):
                continue

            if flux > 0:
                best_flux = flux
                break

        if best_flux is None:
            return None

        if best_flux >= 1e-4:
            letter, base = "X", 1e-4
        elif best_flux >= 1e-5:
            letter, base = "M", 1e-5
        elif best_flux >= 1e-6:
            letter, base = "C", 1e-6
        elif best_flux >= 1e-7:
            letter, base = "B", 1e-7
        else:
            letter, base = "A", 1e-8

        value = best_flux / base
        return f"{letter}{value:.1f}"

    @staticmethod
    def _format_number(value, decimals):
        if value is None:
            return "—"
        return f"{value:.{decimals}f}"

    @staticmethod
    def _kp_description(kp):
        if kp is None:
            return "Unknown"
        if kp < 2:
            return "Very quiet"
        if kp < 4:
            return "Quiet to unsettled"
        if kp < 5:
            return "Active"
        if kp < 6:
            return "Minor storm"
        if kp < 7:
            return "Moderate storm"
        if kp < 8:
            return "Strong storm"
        return "Severe storm"

    @staticmethod
    def _estimate_hf_conditions(flux, kp, xray):
        flux_value = flux if flux is not None else 100.0
        kp_value = kp if kp is not None else 3.0
        flare_penalty = 0

        if xray:
            if xray.startswith("X"):
                flare_penalty = 3
            elif xray.startswith("M"):
                flare_penalty = 2
            elif xray.startswith("C"):
                flare_penalty = 1

        def label(score):
            if score >= 4:
                return "Excellent", "#61DC4C"
            if score >= 3:
                return "Good", "#9BE15D"
            if score >= 2:
                return "Fair", "#F0C76D"
            return "Poor", "#F17982"

        high_bonus = 2 if flux_value >= 150 else 1 if flux_value >= 110 else 0
        quiet_bonus = 2 if kp_value < 2 else 1 if kp_value < 4 else 0
        storm_penalty = 3 if kp_value >= 6 else 2 if kp_value >= 5 else 0

        bands = [
            ("160 m", 2 + quiet_bonus - storm_penalty),
            ("80 m", 3 + quiet_bonus - storm_penalty),
            ("40 m", 3 + quiet_bonus - storm_penalty),
            ("30 m", 3 + high_bonus + quiet_bonus - storm_penalty),
            ("20 m", 3 + high_bonus + quiet_bonus - storm_penalty - flare_penalty),
            ("17 m", 2 + high_bonus + quiet_bonus - storm_penalty - flare_penalty),
            ("15 m", 1 + high_bonus + quiet_bonus - storm_penalty - flare_penalty),
            ("10 m", high_bonus + quiet_bonus - storm_penalty - flare_penalty),
        ]

        results = []
        for band, score in bands:
            condition, colour = label(max(0, min(4, score)))
            results.append({
                "band": band,
                "condition": condition,
                "colour": colour,
            })

        return results

    @pyqtSlot(int)
    def selectDashboard(self, index: int) -> None:
        if 0 <= index < len(self._dashboards):
            self._selected_dashboard_index = index
            self._dashboard_status = f"Selected {self._dashboards[index]['name']}."
            self.dashboardSelectionChanged.emit()

    @pyqtSlot(str, str)
    def addDashboard(self, name: str, url: str) -> None:
        name=name.strip(); url=self._normalise_dashboard_url(url)
        if not name or not url:
            self._dashboard_status="Name and URL are required."; self.dashboardSelectionChanged.emit(); return
        self._dashboards.append({"name":name,"url":url,"home_url":url})
        self._selected_dashboard_index=len(self._dashboards)-1
        self._save_dashboards(); self._dashboard_status=f"Added {name}."
        self.dashboardsChanged.emit(); self.dashboardSelectionChanged.emit()

    @pyqtSlot(int, str, str)
    def updateDashboard(self,index:int,name:str,url:str)->None:
        if not 0 <= index < len(self._dashboards): return
        name=name.strip(); url=self._normalise_dashboard_url(url)
        if not name or not url:
            self._dashboard_status="Name and URL are required."; self.dashboardSelectionChanged.emit(); return
        self._dashboards[index]={"name":name,"url":url,"home_url":url}; self._selected_dashboard_index=index
        self._save_dashboards(); self._dashboard_status=f"Updated {name}."
        self.dashboardsChanged.emit(); self.dashboardSelectionChanged.emit()

    @pyqtSlot(int)
    def deleteDashboard(self,index:int)->None:
        if not 0 <= index < len(self._dashboards): return
        name=self._dashboards[index]["name"]; del self._dashboards[index]
        if not self._dashboards: self._dashboards=[{"name":"EuroNode","url":"http://dvmega-euronode.local/","home_url":"http://dvmega-euronode.local/"}]
        self._selected_dashboard_index=min(self._selected_dashboard_index,len(self._dashboards)-1)
        self._save_dashboards(); self._dashboard_status=f"Deleted {name}."
        self.dashboardsChanged.emit(); self.dashboardSelectionChanged.emit()

    @pyqtSlot()
    def openDashboardInBrowser(self)->None:
        if self.selectedDashboardUrl != "about:blank": webbrowser.open(self.selectedDashboardUrl)

    @pyqtSlot(str, result=bool)
    def testDashboardUrl(self,url:str)->bool:
        url=self._normalise_dashboard_url(url)
        if not url: self._dashboard_status="Enter a dashboard URL first."; self.dashboardSelectionChanged.emit(); return False
        try:
            from urllib.request import Request,urlopen
            with urlopen(Request(url,headers={"User-Agent":f"{APP_NAME}/{APP_VERSION}"}),timeout=5) as response: ok=200 <= response.status < 500
            self._dashboard_status="Dashboard responded successfully." if ok else "Unexpected response."
            self.dashboardSelectionChanged.emit(); return ok
        except Exception as exc:
            self._dashboard_status=f"Connection failed: {exc}"; self.dashboardSelectionChanged.emit(); return False

    # ----------------------------- Helpers ---------------------------

    def _add_activity(self, message: str) -> None:
        self._activity.insert(0, {
            "message": message,
            "time": datetime.now().strftime("%d/%m/%Y %I:%M %p"),
        })
        self._activity = self._activity[:8]
        self.activityChanged.emit()

    def _dashboards_path(self) -> Path:
        return CONFIG_DIR / "dashboards.json"

    def _load_dashboards(self) -> None:
        try:
            values=json.loads(self._dashboards_path().read_text(encoding="utf-8"))
            if not isinstance(values,list): raise ValueError
        except Exception:
            values=[{"name":"EuroNode","url":"http://dvmega-euronode.local/","home_url":"http://dvmega-euronode.local/"}]
        cleaned=[]
        for item in values:
            if not isinstance(item,dict): continue
            name=str(item.get("name","")).strip(); url=self._normalise_dashboard_url(str(item.get("url","")))
            if name and url: cleaned.append({"name":name,"url":url,"home_url":self._normalise_dashboard_url(str(item.get("home_url",url))) or url})
        self._dashboards=cleaned or [{"name":"EuroNode","url":"http://dvmega-euronode.local/","home_url":"http://dvmega-euronode.local/"}]
        self._save_dashboards()

    def _save_dashboards(self) -> None:
        CONFIG_DIR.mkdir(parents=True,exist_ok=True)
        self._dashboards_path().write_text(json.dumps(self._dashboards,indent=2)+"\n",encoding="utf-8")

    @staticmethod
    def _normalise_dashboard_url(url: str) -> str:
        url=url.strip()
        if not url: return ""
        if "://" not in url: url="http://"+url
        if not url.endswith("/"): url+="/"
        return url

    @staticmethod
    def _normalise_web_url(url: str) -> str:
        url = str(url or "").strip()
        if not url:
            return ""
        if "://" not in url:
            url = "http://" + url
        return url

    def _read_settings(self) -> dict:
        try:
            return json.loads(
                (CONFIG_DIR / "settings.json").read_text(encoding="utf-8")
            )
        except Exception:
            return {}

    def _write_settings(self, settings: dict) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        (CONFIG_DIR / "settings.json").write_text(
            json.dumps(settings, indent=2) + "\n",
            encoding="utf-8",
        )

    def _load_settings(self) -> None:
        settings = self._read_settings()
        self._callsign = settings.get("callsign", "")
        self._locator = settings.get("locator", "")
        self._operator_name = settings.get("operator_name", "")
        self._qth = settings.get("qth", "")
        self._country = settings.get("country", "")
        self._dmr_id = settings.get("dmr_id", "")
        self._theme = settings.get("theme", "Dark")
        self._show_splash = settings.get("show_splash", True)
        self._auto_scan = settings.get("auto_scan", False)
        self._check_updates = settings.get("check_updates", True)
        self._hamclock_url = self._normalise_web_url(settings.get("hamclock_url", ""))

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
            return "Windows Preview"

    def _detect_os(self) -> str:
        os_release = Path("/etc/os-release")
        if os_release.exists():
            values = {}
            for line in os_release.read_text(encoding="utf-8").splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    values[key] = value.strip('"')
            return values.get("PRETTY_NAME", platform.platform())

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
                return f"{value:.1f} °C"
            except Exception:
                continue

        return "Preview"

    def _read_load(self) -> tuple[str, str]:
        try:
            one, five, fifteen = os.getloadavg()
            cpu_count = max(os.cpu_count() or 1, 1)
            percent = int(round((one / cpu_count) * 100))
            return f"{percent}%", f"{one:.2f} / {five:.2f} / {fifteen:.2f}"
        except Exception:
            return "—", "Unavailable"

    def _memory_usage(self) -> tuple[int, str]:
        path = Path("/proc/meminfo")
        if path.exists():
            try:
                values = {}
                for line in path.read_text().splitlines():
                    key, raw = line.split(":", 1)
                    values[key] = int(raw.strip().split()[0])

                total_kb = values["MemTotal"]
                available_kb = values["MemAvailable"]
                used_kb = total_kb - available_kb
                percent = int(round(used_kb / total_kb * 100))
                detail = f"{used_kb / 1024**2:.1f} GB / {total_kb / 1024**2:.1f} GB"
                return percent, detail
            except Exception:
                pass

        return 0, "Unavailable"

    def _disk_usage(self) -> tuple[int, str]:
        total, used, _free = shutil.disk_usage("/")
        percent = int(round(used / total * 100))
        detail = f"{used / 1024**3:.1f} GB / {total / 1024**3:.1f} GB"
        return percent, detail

    def _read_uptime(self) -> tuple[str, str]:
        try:
            seconds = float(Path("/proc/uptime").read_text().split()[0])
        except Exception:
            return "Unavailable", "Unavailable"

        boot_time = time.time() - seconds
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes = remainder // 60

        uptime = f"{days} days, {hours} hours, {minutes} mins"
        last_boot = datetime.fromtimestamp(boot_time).strftime("%d %B %Y %I:%M %p")
        return uptime, last_boot

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

    def _service_or_process_running(self, target: str) -> bool:
        if shutil.which("systemctl"):
            result = subprocess.run(
                ["systemctl", "is-active", "--quiet", target],
                timeout=3,
            )
            if result.returncode == 0:
                return True

        if shutil.which("pgrep"):
            result = subprocess.run(
                ["pgrep", "-f", target],
                capture_output=True,
                timeout=3,
            )
            return result.returncode == 0

        return False

    def _run(self, command: list[str]) -> str:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return (result.stdout + result.stderr).strip()
        except Exception:
            return ""
