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
    propagationServerChanged = pyqtSignal()
    toolsChanged = pyqtSignal()
    updateChanged = pyqtSignal()
    helpChanged = pyqtSignal()
    shackClockChanged = pyqtSignal()
    timeSyncChanged = pyqtSignal()
    skipSplashRequested = pyqtSignal()
    startupProgressChanged = pyqtSignal()

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
        self._default_cat_port = ""
        self._default_audio_device = ""
        self._preferred_sdr = ""
        self._update_channel = "Stable channel"
        self._backup_before_updates = True
        self._start_at_login = False
        self._spectrum_peak_hold_default = True
        self._spectrum_peak_decay_default = "Medium"

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

        self._dx_cluster_host = ""
        self._dx_cluster_port = 7300
        self._dx_cluster_login = ""
        self._dx_cluster_enabled = False
        self._propagation_demo_mode = True

        self._propagation_server_status = "Stopped"
        self._propagation_server_detail = "Server has not been checked."
        self._propagation_server_last_update = "Never"
        self._propagation_cluster_status = "Unknown"
        self._propagation_spot_count = 0
        self._propagation_process = None
        self._propagation_updated = "Never"
        self._solar_flux = "—"
        self._kp_index = "—"
        self._solar_wind_speed = "—"
        self._solar_wind_density = "—"
        self._solar_wind_bz = "—"
        self._xray_class = "—"
        self._geomagnetic_state = "Unknown"
        self._hf_conditions = []

        self._audio_inputs: list[dict] = []
        self._audio_outputs: list[dict] = []
        self._audio_status = "Audio devices have not been scanned."
        self._audio_busy = False
        self._tool_status = "System tools are ready."
        self._network_test_result = "Not run"
        self._disk_test_result = "Not run"
        self._usb_test_result = "Not run"
        self._diagnostics_result = "Not run"

        self._audio_monitoring = False
        self._audio_level = 0.0
        self._audio_peak = 0.0
        self._audio_clip = False
        self._audio_dominant_frequency = "—"
        self._audio_bandwidth = "—"
        self._audio_spectrum = [0.0] * 48
        self._audio_spectrum_peaks = [0.0] * 48
        self._audio_peak_hold = True
        self._audio_peak_decay = "Medium"
        self._audio_stream = None
        self._audio_monitor_error = ""

        self._update_status = "No update operation running."
        self._update_busy = False
        self._help_status = "Choose a help topic."

        self._startup_progress = 0
        self._startup_stage = "Preparing HamRadio-Pi Ultimate"
        self._startup_ready = False
        self._time_sync_status = "Not checked"
        self._time_sync_source = "Unknown"
        self._time_sync_quality = "Unknown"
        self._gps_status = "Not detected"
        self._pps_status = "Not detected"

        self._shack_local_time = ""
        self._shack_utc_time = ""
        self._shack_local_date = ""
        self._shack_utc_date = ""
        self._shack_sunrise = "—"
        self._shack_sunset = "—"
        self._shack_daylight = "Unknown"
        self._shack_bearing = "—"
        self._shack_distance = "—"
        self._shack_weather = "Weather source not configured"
        self._shack_weather_detail = ""

        self._load_settings()
        self._load_dashboards()
        self._load_applications()
        self._add_activity("HamRadio-Pi Ultimate started")
        self.refreshSystem()
        self.refreshServices()

        self.system_timer = QTimer(self)
        self.system_timer.timeout.connect(self.refreshSystem)
        self.system_timer.start(5000)

        self.service_timer = QTimer(self)
        self.service_timer.timeout.connect(self.refreshServices)
        self.service_timer.start(30000)

        self.audio_meter_timer = QTimer(self)
        self.audio_meter_timer.timeout.connect(self._publish_audio_monitor)
        self.audio_meter_timer.start(50)

        self.shack_clock_timer = QTimer(self)
        self.shack_clock_timer.timeout.connect(self.refreshShackClock)
        self.shack_clock_timer.start(1000)
        self.refreshShackClock()

        self.propagation_server_timer = QTimer(self)
        self.propagation_server_timer.timeout.connect(
            self.refreshPropagationServerStatus
        )
        self.propagation_server_timer.start(5000)

        QTimer.singleShot(
            800,
            self.ensurePropagationServer,
        )

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

    @pyqtProperty(str, notify=stationChanged)
    def defaultCatPort(self) -> str:
        return self._default_cat_port

    @pyqtProperty(str, notify=stationChanged)
    def defaultAudioDevice(self) -> str:
        return self._default_audio_device

    @pyqtProperty(str, notify=stationChanged)
    def preferredSdr(self) -> str:
        return self._preferred_sdr

    @pyqtProperty(str, notify=stationChanged)
    def updateChannel(self) -> str:
        return self._update_channel

    @pyqtProperty(bool, notify=stationChanged)
    def backupBeforeUpdates(self) -> bool:
        return self._backup_before_updates

    @pyqtProperty(bool, notify=stationChanged)
    def startAtLogin(self) -> bool:
        return self._start_at_login

    @pyqtProperty(bool, notify=stationChanged)
    def spectrumPeakHoldDefault(self) -> bool:
        return self._spectrum_peak_hold_default

    @pyqtProperty(str, notify=stationChanged)
    def spectrumPeakDecayDefault(self) -> str:
        return self._spectrum_peak_decay_default

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


    # --------------------------- System Tools -------------------------

    @pyqtProperty("QVariantList", notify=toolsChanged)
    def audioInputs(self):
        return self._audio_inputs

    @pyqtProperty("QVariantList", notify=toolsChanged)
    def audioOutputs(self):
        return self._audio_outputs

    @pyqtProperty(str, notify=toolsChanged)
    def audioStatus(self) -> str:
        return self._audio_status

    @pyqtProperty(bool, notify=toolsChanged)
    def audioBusy(self) -> bool:
        return self._audio_busy

    @pyqtProperty(bool, notify=toolsChanged)
    def audioMonitoring(self) -> bool:
        return self._audio_monitoring

    @pyqtProperty(float, notify=toolsChanged)
    def audioLevel(self) -> float:
        return self._audio_level

    @pyqtProperty(float, notify=toolsChanged)
    def audioPeak(self) -> float:
        return self._audio_peak

    @pyqtProperty(bool, notify=toolsChanged)
    def audioClip(self) -> bool:
        return self._audio_clip

    @pyqtProperty(str, notify=toolsChanged)
    def audioDominantFrequency(self) -> str:
        return self._audio_dominant_frequency

    @pyqtProperty(str, notify=toolsChanged)
    def audioBandwidth(self) -> str:
        return self._audio_bandwidth

    @pyqtProperty("QVariantList", notify=toolsChanged)
    def audioSpectrum(self):
        return self._audio_spectrum

    @pyqtProperty("QVariantList", notify=toolsChanged)
    def audioSpectrumPeaks(self):
        return self._audio_spectrum_peaks

    @pyqtProperty(bool, notify=toolsChanged)
    def audioPeakHold(self) -> bool:
        return self._audio_peak_hold

    @pyqtProperty(str, notify=toolsChanged)
    def audioPeakDecay(self) -> str:
        return self._audio_peak_decay

    @pyqtProperty(str, notify=toolsChanged)
    def toolStatus(self) -> str:
        return self._tool_status

    @pyqtProperty(str, notify=toolsChanged)
    def networkTestResult(self) -> str:
        return self._network_test_result

    @pyqtProperty(str, notify=toolsChanged)
    def diskTestResult(self) -> str:
        return self._disk_test_result

    @pyqtProperty(str, notify=toolsChanged)
    def usbTestResult(self) -> str:
        return self._usb_test_result

    @pyqtProperty(str, notify=toolsChanged)
    def diagnosticsResult(self) -> str:
        return self._diagnostics_result

    @pyqtProperty(str, notify=updateChanged)
    def updateStatus(self) -> str:
        return self._update_status

    @pyqtProperty(bool, notify=updateChanged)
    def updateBusy(self) -> bool:
        return self._update_busy


    @pyqtProperty(str, notify=helpChanged)
    def helpStatus(self) -> str:
        return self._help_status

    @pyqtProperty(str, constant=True)
    def settingsPath(self) -> str:
        return str(CONFIG_DIR / "settings.json")

    @pyqtProperty(str, constant=True)
    def reportsPath(self) -> str:
        return str(REPORTS_DIR)


    # -------------------------- Shack Clock ---------------------------

    @pyqtProperty(str, notify=shackClockChanged)
    def shackLocalTime(self) -> str:
        return self._shack_local_time

    @pyqtProperty(str, notify=shackClockChanged)
    def shackUtcTime(self) -> str:
        return self._shack_utc_time

    @pyqtProperty(str, notify=shackClockChanged)
    def shackLocalDate(self) -> str:
        return self._shack_local_date

    @pyqtProperty(str, notify=shackClockChanged)
    def shackUtcDate(self) -> str:
        return self._shack_utc_date

    @pyqtProperty(str, notify=shackClockChanged)
    def shackSunrise(self) -> str:
        return self._shack_sunrise

    @pyqtProperty(str, notify=shackClockChanged)
    def shackSunset(self) -> str:
        return self._shack_sunset

    @pyqtProperty(str, notify=shackClockChanged)
    def shackDaylight(self) -> str:
        return self._shack_daylight

    @pyqtProperty(str, notify=shackClockChanged)
    def shackWeather(self) -> str:
        return self._shack_weather

    @pyqtProperty(str, notify=shackClockChanged)
    def shackWeatherDetail(self) -> str:
        return self._shack_weather_detail

    @pyqtSlot()
    def requestSkipSplash(self) -> None:
        self.skipSplashRequested.emit()

    @pyqtProperty(str, notify=timeSyncChanged)
    def timeSyncStatus(self) -> str:
        return self._time_sync_status

    @pyqtProperty(str, notify=timeSyncChanged)
    def timeSyncSource(self) -> str:
        return self._time_sync_source

    @pyqtProperty(str, notify=timeSyncChanged)
    def timeSyncQuality(self) -> str:
        return self._time_sync_quality

    @pyqtProperty(str, notify=timeSyncChanged)
    def gpsStatus(self) -> str:
        return self._gps_status

    @pyqtProperty(str, notify=timeSyncChanged)
    def ppsStatus(self) -> str:
        return self._pps_status


    @pyqtSlot()
    def openActivityLog(self) -> None:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / "activity.log"
        lines = [
            f"{item.get('time', '')}  {item.get('message', '')}"
            for item in reversed(self._activity)
        ]
        path.write_text(
            "\n".join(lines) + ("\n" if lines else ""),
            encoding="utf-8",
        )
        try:
            self._open_path(path)
            self._notification = f"Opened activity log: {path}"
        except Exception as exc:
            self._notification = f"Could not open activity log: {exc}"
        self.notificationChanged.emit()

    @pyqtSlot()
    def openWpsdProject(self) -> None:
        webbrowser.open("https://w0chp.radio/wpsd/")

    @pyqtSlot()
    def openWpsdDownloads(self) -> None:
        webbrowser.open("https://w0chp.radio/wpsd/")

    @pyqtSlot()
    def openWpsdManual(self) -> None:
        webbrowser.open("https://manual.wpsd.radio/")

    @pyqtSlot()
    def openRaspberryPiImager(self) -> None:
        webbrowser.open("https://www.raspberrypi.com/software/")

    @pyqtSlot()
    def openWpsdDashboard(self) -> None:
        self.setPage("Radio Dashboards")

    @pyqtSlot()
    def openPropagationBrowser(self) -> None:
        webbrowser.open("https://solar.w5mmw.net/")
        self._notification = "Opened W5MMW propagation in the default browser."
        self._add_activity("W5MMW propagation opened")
        self.notificationChanged.emit()

    @pyqtSlot()
    def openLocalWpsd(self) -> None:
        webbrowser.open("http://wpsd.local/")
        self._notification = "Opened http://wpsd.local/ in the default browser."
        self._add_activity("Local WPSD dashboard opened")
        self.notificationChanged.emit()


    @pyqtProperty(str, notify=stationChanged)
    def dxClusterHost(self) -> str:
        return self._dx_cluster_host

    @pyqtProperty(int, notify=stationChanged)
    def dxClusterPort(self) -> int:
        return self._dx_cluster_port

    @pyqtProperty(str, notify=stationChanged)
    def dxClusterLogin(self) -> str:
        return self._dx_cluster_login

    @pyqtProperty(bool, notify=stationChanged)
    def dxClusterEnabled(self) -> bool:
        return self._dx_cluster_enabled

    @pyqtProperty(bool, notify=stationChanged)
    def propagationDemoMode(self) -> bool:
        return self._propagation_demo_mode

    @pyqtProperty(str, notify=propagationServerChanged)
    def propagationServerStatus(self) -> str:
        return self._propagation_server_status

    @pyqtProperty(str, notify=propagationServerChanged)
    def propagationServerDetail(self) -> str:
        return self._propagation_server_detail

    @pyqtProperty(str, notify=propagationServerChanged)
    def propagationServerLastUpdate(self) -> str:
        return self._propagation_server_last_update

    @pyqtProperty(str, notify=propagationServerChanged)
    def propagationClusterStatus(self) -> str:
        return self._propagation_cluster_status

    @pyqtProperty(int, notify=propagationServerChanged)
    def propagationSpotCount(self) -> int:
        return self._propagation_spot_count


    @pyqtSlot()
    def ensurePropagationServer(self) -> None:
        self._sync_propagation_config()

        if self._propagation_endpoint_available():
            self.refreshPropagationServerStatus()
            return

        self.startPropagationServer()

    @pyqtSlot()
    def startPropagationServer(self) -> None:
        self._sync_propagation_config()
        self._propagation_server_status = "Stopped"
        self._propagation_server_detail = "Starting local propagation server…"
        self.propagationServerChanged.emit()

        try:
            if platform.system() == "Windows":
                if (
                    self._propagation_process is not None
                    and self._propagation_process.poll() is None
                ):
                    self._propagation_server_detail = (
                        "Propagation server is already running."
                    )
                else:
                    flags = getattr(
                        subprocess,
                        "CREATE_NO_WINDOW",
                        0,
                    )
                    self._propagation_process = subprocess.Popen(
                        [
                            sys.executable,
                            str(
                                BASE_DIR
                                / "propagation"
                                / "server.py"
                            ),
                        ],
                        cwd=str(
                            BASE_DIR / "propagation"
                        ),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=flags,
                    )
            else:
                result = subprocess.run(
                    [
                        "systemctl",
                        "--user",
                        "start",
                        "hrpu-propagation.service",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=20,
                )

                if result.returncode != 0:
                    self._start_propagation_fallback()

            QTimer.singleShot(
                900,
                self.refreshPropagationServerStatus,
            )
            self._add_activity(
                "Propagation server start requested"
            )
        except Exception as exc:
            self._propagation_server_status = "Connection Error"
            self._propagation_server_detail = str(exc)
            self.propagationServerChanged.emit()

    @pyqtSlot()
    def stopPropagationServer(self) -> None:
        try:
            if platform.system() == "Windows":
                if (
                    self._propagation_process is not None
                    and self._propagation_process.poll() is None
                ):
                    self._propagation_process.terminate()
                    try:
                        self._propagation_process.wait(
                            timeout=5,
                        )
                    except subprocess.TimeoutExpired:
                        self._propagation_process.kill()
                self._propagation_process = None
            else:
                subprocess.run(
                    [
                        "systemctl",
                        "--user",
                        "stop",
                        "hrpu-propagation.service",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=20,
                )

                if (
                    self._propagation_process is not None
                    and self._propagation_process.poll() is None
                ):
                    self._propagation_process.terminate()

                self._propagation_process = None

            self._propagation_server_status = "Stopped"
            self._propagation_server_detail = (
                "Propagation server stopped."
            )
            self._propagation_server_last_update = (
                datetime.now().strftime(
                    "%d %b %Y %H:%M:%S"
                )
            )
            self._add_activity(
                "Propagation server stopped"
            )
        except Exception as exc:
            self._propagation_server_status = "Connection Error"
            self._propagation_server_detail = str(exc)

        self.propagationServerChanged.emit()

    @pyqtSlot()
    def restartPropagationServer(self) -> None:
        self.stopPropagationServer()
        QTimer.singleShot(
            500,
            self.startPropagationServer,
        )

    @pyqtSlot()
    def refreshPropagationServerStatus(self) -> None:
        try:
            request = Request(
                "http://127.0.0.1:8765/api/status",
                headers={
                    "User-Agent": (
                        f"{APP_NAME}/{APP_VERSION}"
                    ),
                    "Cache-Control": "no-cache",
                },
            )

            with urlopen(
                request,
                timeout=2.5,
            ) as response:
                status = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

            self._propagation_server_status = "Running"
            self._propagation_cluster_status = str(
                status.get(
                    "cluster_status",
                    "Unknown",
                )
            )
            self._propagation_spot_count = int(
                status.get(
                    "spot_count",
                    0,
                )
            )
            last_update = status.get(
                "last_update",
                status.get(
                    "updated",
                    "",
                ),
            )
            self._propagation_server_last_update = (
                self._format_iso_datetime(
                    last_update
                )
            )

            if status.get(
                "cluster_enabled",
                False,
            ):
                self._propagation_server_detail = (
                    "DX cluster "
                    + self._propagation_cluster_status
                    + f" · {self._propagation_spot_count} spots"
                )
            elif status.get(
                "demo_mode",
                True,
            ):
                self._propagation_server_detail = (
                    "Demo mode · "
                    f"{self._propagation_spot_count} spots"
                )
            else:
                self._propagation_server_detail = (
                    "Running without DX-cluster connection."
                )
        except Exception as exc:
            active = self._propagation_process_active()

            if active:
                self._propagation_server_status = "Connection Error"
                self._propagation_server_detail = (
                    "Server process appears active, "
                    "but the local API did not respond: "
                    + str(exc)
                )
            else:
                self._propagation_server_status = "Stopped"
                self._propagation_server_detail = (
                    "Local propagation server is not running."
                )

            self._propagation_cluster_status = "Unknown"
            self._propagation_spot_count = 0

        self.propagationServerChanged.emit()

    def _propagation_endpoint_available(self) -> bool:
        try:
            with urlopen(
                "http://127.0.0.1:8765/api/status",
                timeout=1.5,
            ) as response:
                return response.status == 200
        except Exception:
            return False

    def _propagation_process_active(self) -> bool:
        if (
            self._propagation_process is not None
            and self._propagation_process.poll() is None
        ):
            return True

        if platform.system() != "Windows":
            try:
                result = subprocess.run(
                    [
                        "systemctl",
                        "--user",
                        "is-active",
                        "--quiet",
                        "hrpu-propagation.service",
                    ],
                    timeout=5,
                )
                return result.returncode == 0
            except Exception:
                return False

        return False

    def _start_propagation_fallback(self) -> None:
        if (
            self._propagation_process is not None
            and self._propagation_process.poll() is None
        ):
            return

        self._propagation_process = subprocess.Popen(
            [
                sys.executable,
                str(
                    BASE_DIR
                    / "propagation"
                    / "server.py"
                ),
            ],
            cwd=str(
                BASE_DIR / "propagation"
            ),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    def _sync_propagation_config(self) -> None:
        script = (
            BASE_DIR
            / "scripts"
            / "sync-propagation-config.py"
        )

        try:
            subprocess.run(
                [
                    sys.executable,
                    str(script),
                ],
                cwd=str(BASE_DIR),
                check=True,
                timeout=15,
            )
        except Exception as exc:
            self._propagation_server_detail = (
                "Could not update propagation configuration: "
                + str(exc)
            )

    @staticmethod
    def _format_iso_datetime(value: str) -> str:
        if not value:
            return "Never"

        try:
            parsed = datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            )
            return parsed.astimezone().strftime(
                "%d %b %Y %H:%M:%S"
            )
        except Exception:
            return str(value)

    @pyqtProperty(int, notify=startupProgressChanged)
    def startupProgress(self) -> int:
        return self._startup_progress

    @pyqtProperty(str, notify=startupProgressChanged)
    def startupStage(self) -> str:
        return self._startup_stage

    @pyqtProperty(bool, notify=startupProgressChanged)
    def startupReady(self) -> bool:
        return self._startup_ready

    @pyqtSlot(int, str)
    def setStartupProgress(self, value: int, stage: str) -> None:
        self._startup_progress = max(0, min(100, int(value)))
        self._startup_stage = stage.strip() or "Loading"
        self._startup_ready = self._startup_progress >= 100
        self.startupProgressChanged.emit()

    @pyqtSlot()
    def completeStartup(self) -> None:
        self._startup_progress = 100
        self._startup_stage = "Ready"
        self._startup_ready = True
        self.startupProgressChanged.emit()

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
        self._sync_propagation_config()
        self.stationChanged.emit()
        self._notification = "Station profile saved."
        QTimer.singleShot(
            300,
            self.restartPropagationServer,
        )
        self._add_activity("Station profile updated")
        self.notificationChanged.emit()

    @pyqtSlot(
        str, bool, bool, bool, str, str, str, str,
        bool, bool, str, bool, str, int, str, bool, bool
    )
    def savePreferences(
        self,
        theme_name: str,
        show_splash: bool,
        auto_scan: bool,
        check_updates: bool,
        default_cat_port: str,
        default_audio_device: str,
        preferred_sdr: str,
        update_channel: str,
        backup_before_updates: bool,
        spectrum_peak_hold_default: bool,
        spectrum_peak_decay_default: str,
        start_at_login: bool,
        dx_cluster_host: str,
        dx_cluster_port: int,
        dx_cluster_login: str,
        dx_cluster_enabled: bool,
        propagation_demo_mode: bool,
    ) -> None:
        settings = self._read_settings()
        settings.update({
            "theme": theme_name.strip() or "Ultimate Teal",
            "show_splash": bool(show_splash),
            "auto_scan": bool(auto_scan),
            "check_updates": bool(check_updates),
            "hamclock_url": "",
            "external_clock_url": "",
            "default_cat_port": default_cat_port.strip(),
            "default_audio_device": default_audio_device.strip(),
            "preferred_sdr": preferred_sdr.strip(),
            "update_channel": update_channel.strip() or "Stable channel",
            "backup_before_updates": bool(backup_before_updates),
            "spectrum_peak_hold_default": bool(spectrum_peak_hold_default),
            "spectrum_peak_decay_default": (
                spectrum_peak_decay_default.strip() or "Medium"
            ),
            "start_at_login": bool(start_at_login),
            "dx_cluster_host": dx_cluster_host.strip(),
            "dx_cluster_port": int(dx_cluster_port),
            "dx_cluster_login": dx_cluster_login.strip().upper(),
            "dx_cluster_enabled": bool(dx_cluster_enabled),
            "propagation_demo_mode": bool(propagation_demo_mode),
        })
        self._write_settings(settings)
        self._apply_start_at_login(bool(start_at_login))
        self._load_settings()
        self._sync_propagation_config()
        QTimer.singleShot(
            300,
            self.restartPropagationServer,
        )
        self.stationChanged.emit()
        self._notification = "Preferences saved and applied."
        self._add_activity("Preferences updated")
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
        errors = []
        received = 0

        def safe_download(label: str, urls: list[str]):
            nonlocal received
            last_error = None

            for url in urls:
                try:
                    data = self._download_json(url)
                    received += 1
                    return data
                except Exception as exc:
                    last_error = exc

            errors.append(f"{label}: {last_error}")
            return None

        try:
            # These are current NOAA SWPC operational feeds. Alternative
            # endpoints are included so one changed URL cannot break the page.
            kp_data = safe_download(
                "Kp",
                [
                    "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json",
                    "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json",
                ],
            )
            plasma_data = safe_download(
                "solar wind plasma",
                [
                    "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json",
                    "https://services.swpc.noaa.gov/products/solar-wind/plasma-2-hour.json",
                ],
            )
            mag_data = safe_download(
                "solar wind magnetic field",
                [
                    "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json",
                    "https://services.swpc.noaa.gov/products/solar-wind/mag-2-hour.json",
                ],
            )
            flux_data = safe_download(
                "solar flux",
                [
                    "https://services.swpc.noaa.gov/json/f107_cm_flux.json",
                    "https://services.swpc.noaa.gov/products/10cm-flux-30-day.json",
                    "https://services.swpc.noaa.gov/json/solar-radio-flux.json",
                ],
            )
            xray_data = safe_download(
                "X-ray",
                [
                    "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json",
                    "https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json",
                ],
            )

            kp = self._latest_table_number(
                kp_data or [],
                ("kp", "Kp", "estimated_kp", "kp_index"),
            )
            speed = self._latest_table_number(
                plasma_data or [],
                ("speed",),
            )
            density = self._latest_table_number(
                plasma_data or [],
                ("density",),
            )
            bz = self._latest_table_number(
                mag_data or [],
                ("bz_gsm", "bz", "bz_gse"),
            )
            flux = self._latest_solar_flux(flux_data or [])
            xray = self._latest_xray_class(xray_data or [])

            self._kp_index = self._format_number(kp, 1)
            self._solar_wind_speed = (
                f"{speed:.0f} km/s" if speed is not None else "Unavailable"
            )
            self._solar_wind_density = (
                f"{density:.1f} p/cm³" if density is not None else "Unavailable"
            )
            self._solar_wind_bz = (
                f"{bz:+.1f} nT" if bz is not None else "Unavailable"
            )
            self._solar_flux = (
                f"{flux:.0f} sfu" if flux is not None else "Unavailable"
            )
            self._xray_class = xray or "Unavailable"
            self._geomagnetic_state = self._kp_description(kp)
            self._hf_conditions = self._estimate_hf_conditions(
                flux,
                kp,
                xray,
            )
            self._propagation_updated = datetime.now().strftime(
                "%d %b %Y %H:%M"
            )

            if received == 0:
                self._propagation_status = (
                    "No NOAA feeds could be reached. Check the internet connection."
                )
            elif errors:
                self._propagation_status = (
                    f"Live NOAA data received ({received} feeds); "
                    f"{len(errors)} reading(s) unavailable."
                )
            else:
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
                "User-Agent": f"HamRadio-Pi-Ultimate/{APP_VERSION}",
                "Accept": "application/json",
                "Cache-Control": "no-cache",
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
                "f107",
                "f10.7",
                "f10_7",
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


    # ------------------------- System Tool Slots ----------------------

    @pyqtSlot()
    def startAudioMonitor(self) -> None:
        if self._audio_monitoring:
            return
        try:
            import numpy as np
            import sounddevice as sd

            self._audio_peak_hold = self._spectrum_peak_hold_default
            self._audio_peak_decay = self._spectrum_peak_decay_default
            self._audio_spectrum_peaks = [0.0] * 48

            sample_rate = 48000
            block_size = 2048
            self._audio_monitor_error = ""

            def callback(indata, frames, time_info, status):
                del frames, time_info
                if status:
                    self._audio_monitor_error = str(status)

                samples = np.asarray(indata[:, 0], dtype=np.float32)
                if samples.size == 0:
                    return

                rms = float(np.sqrt(np.mean(np.square(samples))))
                peak = float(np.max(np.abs(samples)))
                windowed = samples * np.hanning(samples.size)
                fft_values = np.abs(np.fft.rfft(windowed))
                frequencies = np.fft.rfftfreq(samples.size, 1.0 / sample_rate)
                if fft_values.size:
                    fft_values[0] = 0.0

                maximum = float(np.max(fft_values)) if fft_values.size else 0.0
                normalised = fft_values / maximum if maximum > 0 else fft_values
                mask = frequencies <= 6000.0
                display = normalised[mask]
                display_freqs = frequencies[mask]

                boundaries = np.linspace(0, display.size, 49, dtype=int)
                bars = []
                for index in range(48):
                    section = display[boundaries[index]:boundaries[index + 1]]
                    bars.append(
                        max(0.0, min(1.0, float(np.max(section))))
                        if section.size else 0.0
                    )

                dominant_hz = 0.0
                if fft_values.size > 1:
                    dominant_hz = float(frequencies[int(np.argmax(fft_values))])

                bandwidth_hz = 0.0
                if maximum > 0 and display.size:
                    active = np.flatnonzero(display >= 0.10)
                    if active.size:
                        bandwidth_hz = max(
                            0.0,
                            float(display_freqs[active[-1]])
                            - float(display_freqs[active[0]]),
                        )

                self._audio_level = max(0.0, min(1.0, rms * 4.0))
                self._audio_peak = max(0.0, min(1.0, peak))
                self._audio_clip = peak >= 0.98
                self._audio_dominant_frequency = (
                    f"{dominant_hz:.0f} Hz" if dominant_hz > 0 else "—"
                )
                self._audio_bandwidth = (
                    f"{bandwidth_hz:.0f} Hz" if bandwidth_hz > 0 else "—"
                )
                self._audio_spectrum = bars

                if self._audio_peak_hold:
                    decay_factor = {
                        "Fast": 0.93,
                        "Medium": 0.965,
                        "Slow": 0.985,
                    }.get(self._audio_peak_decay, 0.965)
                    self._audio_spectrum_peaks = [
                        max(current, previous * decay_factor)
                        for current, previous in zip(
                            bars,
                            self._audio_spectrum_peaks,
                        )
                    ]
                else:
                    self._audio_spectrum_peaks = [0.0] * 48

            self._audio_stream = sd.InputStream(
                channels=1,
                samplerate=sample_rate,
                blocksize=block_size,
                dtype="float32",
                callback=callback,
            )
            self._audio_stream.start()
            self._audio_monitoring = True
            self._audio_status = (
                "Live microphone monitor started. Audio is analysed in memory "
                "and is not saved or transmitted."
            )
            self._add_activity("Live microphone monitor started")
        except Exception as exc:
            self._audio_stream = None
            self._audio_monitoring = False
            self._audio_status = f"Could not start live microphone monitor: {exc}"
        self.toolsChanged.emit()

    @pyqtSlot()
    def stopAudioMonitor(self) -> None:
        try:
            if self._audio_stream is not None:
                self._audio_stream.stop()
                self._audio_stream.close()
        except Exception:
            pass
        self._audio_stream = None
        self._audio_monitoring = False
        self._audio_level = 0.0
        self._audio_peak = 0.0
        self._audio_clip = False
        self._audio_dominant_frequency = "—"
        self._audio_bandwidth = "—"
        self._audio_spectrum = [0.0] * 48
        self._audio_spectrum_peaks = [0.0] * 48
        self._audio_status = "Live microphone monitor stopped."
        self._add_activity("Live microphone monitor stopped")
        self.toolsChanged.emit()

    def _publish_audio_monitor(self) -> None:
        if not self._audio_monitoring:
            return
        if self._audio_monitor_error:
            self._audio_status = "Audio monitor warning: " + self._audio_monitor_error
            self._audio_monitor_error = ""
        self.toolsChanged.emit()

    @pyqtSlot(bool)
    def setAudioPeakHold(self, enabled: bool) -> None:
        self._audio_peak_hold = bool(enabled)
        if not self._audio_peak_hold:
            self._audio_spectrum_peaks = [0.0] * 48
        self.toolsChanged.emit()

    @pyqtSlot(str)
    def setAudioPeakDecay(self, speed: str) -> None:
        speed = speed.strip().title()
        if speed not in {"Fast", "Medium", "Slow"}:
            speed = "Medium"
        self._audio_peak_decay = speed
        self.toolsChanged.emit()

    @pyqtSlot()
    def clearAudioPeaks(self) -> None:
        self._audio_spectrum_peaks = [0.0] * 48
        self.toolsChanged.emit()

    @pyqtSlot()
    def scanAudioDevices(self) -> None:
        if self._audio_busy:
            return
        self._audio_busy = True
        self._audio_status = "Scanning microphones and speakers…"
        self.toolsChanged.emit()
        self._run_in_thread(self._scan_audio_worker)

    @pyqtSlot()
    def testSpeakers(self) -> None:
        if self._audio_busy:
            return
        self._audio_busy = True
        self._audio_status = "Playing a two-second test tone…"
        self.toolsChanged.emit()
        self._run_in_thread(self._speaker_test_worker)

    @pyqtSlot()
    def testMicrophone(self) -> None:
        if self._audio_busy:
            return
        self._audio_busy = True
        self._audio_status = "Recording the microphone for three seconds…"
        self.toolsChanged.emit()
        self._run_in_thread(self._microphone_test_worker)

    @pyqtSlot()
    def runNetworkTest(self) -> None:
        self._tool_status = "Running network test…"
        self.toolsChanged.emit()
        self._run_in_thread(self._network_test_worker)

    @pyqtSlot()
    def runDiskTest(self) -> None:
        self._tool_status = "Checking disk usage and write access…"
        self.toolsChanged.emit()
        self._run_in_thread(self._disk_test_worker)

    @pyqtSlot()
    def runUsbTest(self) -> None:
        self._tool_status = "Scanning USB hardware…"
        self.toolsChanged.emit()
        self._run_in_thread(self._usb_test_worker)

    @pyqtSlot()
    def runDiagnostics(self) -> None:
        self._tool_status = "Creating full diagnostics report…"
        self.toolsChanged.emit()
        self._run_in_thread(self._diagnostics_worker)

    @pyqtSlot()
    def openTerminal(self) -> None:
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["cmd.exe"])
            else:
                terminal = (
                    shutil.which("x-terminal-emulator")
                    or shutil.which("lxterminal")
                    or shutil.which("xterm")
                )
                if not terminal:
                    raise RuntimeError("No terminal program was found.")
                subprocess.Popen([terminal], start_new_session=True)
            self._tool_status = "Terminal opened."
        except Exception as exc:
            self._tool_status = f"Could not open terminal: {exc}"
        self.toolsChanged.emit()

    @pyqtSlot()
    def updateDependencies(self) -> None:
        if self._update_busy:
            return
        self._update_busy = True
        self._update_status = "Opening dependency updater…"
        self.updateChanged.emit()

        try:
            if platform.system() == "Windows":
                command = (
                    'py -3 -m pip install --upgrade '
                    'pip PyQt6 PyQt6-WebEngine sounddevice numpy'
                )
                subprocess.Popen(
                    ["cmd.exe", "/k", command],
                    creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
                )
                self._update_status = (
                    "Windows dependency updater opened in a command window."
                )
            else:
                terminal = (
                    shutil.which("x-terminal-emulator")
                    or shutil.which("lxterminal")
                    or shutil.which("xterm")
                )
                if not terminal:
                    raise RuntimeError("No terminal program was found.")

                command = (
                    "sudo apt-get update && "
                    "sudo apt-get install --only-upgrade -y "
                    "python3 python3-pyqt6 python3-pyqt6.qtquick "
                    "python3-pyqt6.qtwebengine python3-pyqt6.qtsvg "
                    "qml6-module-qtquick qml6-module-qtquick-controls "
                    "qml6-module-qtquick-layouts qml6-module-qtwebengine "
                    "alsa-utils usbutils curl unzip; "
                    "echo; echo Dependency update finished.; "
                    "read -r -p 'Press ENTER to close…'"
                )
                subprocess.Popen(
                    [terminal, "-e", "bash", "-lc", command],
                    start_new_session=True,
                )
                self._update_status = (
                    "Raspberry Pi dependency updater opened in a terminal."
                )
        except Exception as exc:
            self._update_status = f"Could not start dependency update: {exc}"
        finally:
            self._update_busy = False
            self.updateChanged.emit()

    @pyqtSlot()
    def updateProgram(self) -> None:
        if self._update_busy:
            return
        self._update_busy = True
        self._update_status = "Preparing program update…"
        self.updateChanged.emit()

        try:
            if platform.system() == "Windows":
                webbrowser.open(
                    "https://github.com/ZL4SSB/Ham-Radio-Pi-Ultimate/"
                    "archive/refs/heads/main.zip"
                )
                self._update_status = (
                    "Latest Windows ZIP opened in your browser. "
                    "Close Ultimate before replacing its files."
                )
            else:
                terminal = (
                    shutil.which("x-terminal-emulator")
                    or shutil.which("lxterminal")
                    or shutil.which("xterm")
                )
                if not terminal:
                    raise RuntimeError("No terminal program was found.")

                command = (
                    "curl -fsSL "
                    "https://raw.githubusercontent.com/ZL4SSB/"
                    "Ham-Radio-Pi-Ultimate/main/install-public.sh "
                    "-o /tmp/install-hamradio-pi.sh && "
                    "chmod +x /tmp/install-hamradio-pi.sh && "
                    "/tmp/install-hamradio-pi.sh; "
                    "echo; read -r -p 'Press ENTER to close…'"
                )
                subprocess.Popen(
                    [terminal, "-e", "bash", "-lc", command],
                    start_new_session=True,
                )
                self._update_status = (
                    "Anonymous Raspberry Pi program updater opened."
                )
        except Exception as exc:
            self._update_status = f"Could not start program update: {exc}"
        finally:
            self._update_busy = False
            self.updateChanged.emit()

    def _run_in_thread(self, target) -> None:
        import threading
        threading.Thread(target=target, daemon=True).start()

    def _scan_audio_worker(self) -> None:
        inputs = []
        outputs = []

        try:
            try:
                import sounddevice as sd
                for index, device in enumerate(sd.query_devices()):
                    name = str(device.get("name", f"Device {index}"))
                    hostapi = str(device.get("hostapi", ""))
                    detail = f"Device {index}"
                    if hostapi:
                        detail += f" · Host API {hostapi}"
                    if int(device.get("max_input_channels", 0)) > 0:
                        inputs.append({
                            "name": name,
                            "detail": detail,
                        })
                    if int(device.get("max_output_channels", 0)) > 0:
                        outputs.append({
                            "name": name,
                            "detail": detail,
                        })
            except Exception:
                if platform.system() == "Windows":
                    script = (
                        "Get-PnpDevice -Class AudioEndpoint | "
                        "Where-Object {$_.Status -eq 'OK'} | "
                        "Select-Object FriendlyName,InstanceId | "
                        "ConvertTo-Json -Compress"
                    )
                    raw = subprocess.run(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-ExecutionPolicy",
                            "Bypass",
                            "-Command",
                            script,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=15,
                    ).stdout.strip()
                    if raw:
                        data = json.loads(raw)
                        if isinstance(data, dict):
                            data = [data]
                        for item in data:
                            name = str(item.get("FriendlyName", "Audio device"))
                            lower = name.lower()
                            record = {
                                "name": name,
                                "detail": "Windows audio endpoint",
                            }
                            if any(word in lower for word in (
                                "microphone", "mic", "input", "line in"
                            )):
                                inputs.append(record)
                            else:
                                outputs.append(record)
                else:
                    outputs.extend(
                        self._parse_alsa_cards(
                            self._run(["aplay", "-l"]),
                            "Playback",
                        )
                    )
                    inputs.extend(
                        self._parse_alsa_cards(
                            self._run(["arecord", "-l"]),
                            "Capture",
                        )
                    )

            self._audio_inputs = inputs
            self._audio_outputs = outputs
            self._audio_status = (
                f"Found {len(inputs)} microphone/input device(s) and "
                f"{len(outputs)} speaker/output device(s)."
            )
            self._add_activity("Audio devices scanned")
        except Exception as exc:
            self._audio_status = f"Audio scan failed: {exc}"
        finally:
            self._audio_busy = False
            self.toolsChanged.emit()

    @staticmethod
    def _parse_alsa_cards(text: str, direction: str) -> list[dict]:
        devices = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("card "):
                continue
            devices.append({
                "name": stripped,
                "detail": f"ALSA {direction} device",
            })
        return devices

    def _create_test_tone(self, path: Path) -> None:
        import math
        import struct
        import wave

        sample_rate = 44100
        duration = 2.0
        frequency = 700.0
        amplitude = 0.30

        with wave.open(str(path), "wb") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(sample_rate)

            frames = bytearray()
            for index in range(int(sample_rate * duration)):
                fade = min(
                    1.0,
                    index / (sample_rate * 0.05),
                    (sample_rate * duration - index) / (sample_rate * 0.05),
                )
                value = int(
                    32767
                    * amplitude
                    * max(0.0, fade)
                    * math.sin(2 * math.pi * frequency * index / sample_rate)
                )
                frames.extend(struct.pack("<h", value))
            handle.writeframes(frames)

    def _speaker_test_worker(self) -> None:
        import tempfile

        path = Path(tempfile.gettempdir()) / "hamradio-pi-speaker-test.wav"
        try:
            self._create_test_tone(path)

            if platform.system() == "Windows":
                import winsound
                winsound.PlaySound(str(path), winsound.SND_FILENAME)
            else:
                player = shutil.which("aplay") or shutil.which("paplay")
                if not player:
                    raise RuntimeError("Neither aplay nor paplay was found.")
                subprocess.run(
                    [player, str(path)],
                    check=True,
                    timeout=15,
                )

            self._audio_status = (
                "Speaker test finished. You should have heard a two-second tone."
            )
            self._add_activity("Speaker test completed")
        except Exception as exc:
            self._audio_status = f"Speaker test failed: {exc}"
        finally:
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass
            self._audio_busy = False
            self.toolsChanged.emit()

    def _microphone_test_worker(self) -> None:
        import tempfile

        path = Path(tempfile.gettempdir()) / "hamradio-pi-microphone-test.wav"
        try:
            peak = None
            rms = None

            try:
                import numpy as np
                import sounddevice as sd

                sample_rate = 44100
                recording = sd.rec(
                    int(3 * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype="float32",
                )
                sd.wait()
                samples = np.asarray(recording).reshape(-1)
                peak = float(np.max(np.abs(samples)))
                rms = float(np.sqrt(np.mean(np.square(samples))))
            except Exception:
                if platform.system() == "Windows":
                    raise RuntimeError(
                        "Install or update the sounddevice package, then retry."
                    )

                recorder = shutil.which("arecord")
                if not recorder:
                    raise RuntimeError("arecord was not found.")

                subprocess.run(
                    [
                        recorder,
                        "-q",
                        "-d",
                        "3",
                        "-f",
                        "S16_LE",
                        "-r",
                        "44100",
                        "-c",
                        "1",
                        str(path),
                    ],
                    check=True,
                    timeout=12,
                )
                peak, rms = self._analyse_pcm_wav(path)

            peak_percent = min(100, int(round((peak or 0.0) * 100)))
            rms_percent = min(100, int(round((rms or 0.0) * 100)))

            if peak_percent < 1:
                self._audio_status = (
                    "Microphone test recorded almost no signal. "
                    "Check the selected input and its level."
                )
            else:
                self._audio_status = (
                    f"Microphone test passed — peak {peak_percent}%, "
                    f"average {rms_percent}%."
                )
            self._add_activity("Microphone test completed")
        except Exception as exc:
            self._audio_status = f"Microphone test failed: {exc}"
        finally:
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass
            self._audio_busy = False
            self.toolsChanged.emit()

    @staticmethod
    def _analyse_pcm_wav(path: Path) -> tuple[float, float]:
        import array
        import math
        import wave

        with wave.open(str(path), "rb") as handle:
            width = handle.getsampwidth()
            frames = handle.readframes(handle.getnframes())

        if width != 2:
            raise RuntimeError("Only 16-bit PCM microphone recordings are supported.")

        values = array.array("h")
        values.frombytes(frames)
        if sys.byteorder != "little":
            values.byteswap()
        if not values:
            return 0.0, 0.0

        normalised = [abs(value) / 32768.0 for value in values]
        peak = max(normalised)
        rms = math.sqrt(sum(value * value for value in normalised) / len(normalised))
        return peak, rms

    def _network_test_worker(self) -> None:
        from urllib.request import Request, urlopen

        targets = [
            (
                "Cloudflare",
                "https://www.cloudflare.com/cdn-cgi/trace",
            ),
            (
                "Google",
                "https://www.google.com/generate_204",
            ),
        ]
        failures = []

        try:
            dns_started = time.monotonic()
            resolved = socket.gethostbyname("www.cloudflare.com")
            dns_ms = (time.monotonic() - dns_started) * 1000

            success = None
            for name, url in targets:
                started = time.monotonic()
                try:
                    request = Request(
                        url,
                        headers={
                            "User-Agent": f"{APP_NAME}/{APP_VERSION}",
                            "Cache-Control": "no-cache",
                        },
                    )
                    with urlopen(request, timeout=6) as response:
                        status = response.status
                    elapsed_ms = (time.monotonic() - started) * 1000
                    if 200 <= status < 400:
                        success = (name, status, elapsed_ms)
                        break
                    failures.append(f"{name}: HTTP {status}")
                except Exception as exc:
                    failures.append(f"{name}: {exc}")

            if success:
                name, status, elapsed_ms = success
                self._network_test_result = (
                    f"PASS — {name} HTTP {status} in {elapsed_ms:.0f} ms; "
                    f"DNS {dns_ms:.0f} ms ({resolved}); "
                    f"local IP {self._local_ip()}."
                )
            else:
                self._network_test_result = (
                    "FAIL — neither Cloudflare nor Google responded. "
                    + " | ".join(failures)
                )
        except Exception as exc:
            self._network_test_result = f"FAIL — {exc}"

        self._tool_status = "Network test finished."
        self.toolsChanged.emit()

    def _disk_test_worker(self) -> None:
        try:
            total, used, free = shutil.disk_usage(BASE_DIR)
            test_file = REPORTS_DIR / ".write-test"
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            test_file.write_text("HamRadio-Pi write test\n", encoding="utf-8")
            test_file.unlink()
            self._disk_test_result = (
                f"PASS — {free / 1024**3:.1f} GB free of "
                f"{total / 1024**3:.1f} GB; project folder is writable."
            )
        except Exception as exc:
            self._disk_test_result = f"FAIL — {exc}"
        self._tool_status = "Disk test finished."
        self.toolsChanged.emit()

    def _usb_test_worker(self) -> None:
        try:
            if platform.system() == "Windows":
                script = (
                    "Get-PnpDevice -PresentOnly | "
                    "Where-Object {$_.InstanceId -like 'USB*'} | "
                    "Select-Object -First 100 FriendlyName,Status | "
                    "ConvertTo-Json -Compress"
                )
                raw = subprocess.run(
                    [
                        "powershell.exe",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-Command",
                        script,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=20,
                ).stdout.strip()
                count = 0
                if raw:
                    data = json.loads(raw)
                    count = len(data) if isinstance(data, list) else 1
                self._usb_test_result = (
                    f"PASS — Windows reports {count} present USB device(s)."
                )
            else:
                lines = [
                    line for line in self._run(["lsusb"]).splitlines()
                    if line.strip()
                ]
                self._usb_test_result = (
                    f"PASS — lsusb reports {len(lines)} USB device(s)."
                )
        except Exception as exc:
            self._usb_test_result = f"FAIL — {exc}"
        self._tool_status = "USB test finished."
        self.toolsChanged.emit()

    def _diagnostics_worker(self) -> None:
        try:
            path = Path(self.createSystemReport())
            with path.open("a", encoding="utf-8") as handle:
                handle.write(f"Audio status: {self._audio_status}\n")
                handle.write(f"Network test: {self._network_test_result}\n")
                handle.write(f"Disk test: {self._disk_test_result}\n")
                handle.write(f"USB test: {self._usb_test_result}\n")
                handle.write(f"Python executable: {sys.executable}\n")
            self._diagnostics_result = f"Report created: {path}"
        except Exception as exc:
            self._diagnostics_result = f"Diagnostics failed: {exc}"
        self._tool_status = "Diagnostics finished."
        self.toolsChanged.emit()



    @pyqtSlot()
    def refreshShackClock(self) -> None:
        from datetime import datetime, timezone
        import math

        local_now = datetime.now().astimezone()
        utc_now = datetime.now(timezone.utc)

        self._shack_local_time = local_now.strftime("%H:%M:%S")
        self._shack_utc_time = utc_now.strftime("%H:%M:%S")
        self._shack_local_date = local_now.strftime("%A, %d %B %Y")
        self._shack_utc_date = utc_now.strftime("%d %B %Y UTC")

        latitude, longitude = self._locator_to_lat_lon(self._locator)
        if latitude is not None and longitude is not None:
            sunrise, sunset = self._calculate_sun_times(
                local_now.date(),
                latitude,
                longitude,
                local_now.utcoffset().total_seconds() / 3600.0,
            )
            self._shack_sunrise = sunrise
            self._shack_sunset = sunset

            try:
                sunrise_dt = datetime.strptime(
                    f"{local_now.date()} {sunrise}",
                    "%Y-%m-%d %H:%M",
                ).replace(tzinfo=local_now.tzinfo)
                sunset_dt = datetime.strptime(
                    f"{local_now.date()} {sunset}",
                    "%Y-%m-%d %H:%M",
                ).replace(tzinfo=local_now.tzinfo)
                self._shack_daylight = (
                    "Daylight"
                    if sunrise_dt <= local_now <= sunset_dt
                    else "Night"
                )
            except Exception:
                self._shack_daylight = "Unknown"
        else:
            self._shack_sunrise = "Set station locator"
            self._shack_sunset = "Set station locator"
            self._shack_daylight = "Unknown"

        self.shackClockChanged.emit()

    @pyqtSlot()
    def openExternalClock(self) -> None:
        self.openHamClock()

    @staticmethod
    def _locator_to_lat_lon(locator: str):
        locator = (locator or "").strip().upper()
        if len(locator) < 4:
            return None, None

        try:
            lon = (ord(locator[0]) - ord("A")) * 20 - 180
            lat = (ord(locator[1]) - ord("A")) * 10 - 90
            lon += int(locator[2]) * 2
            lat += int(locator[3])

            if len(locator) >= 6:
                lon += (ord(locator[4]) - ord("A")) * (5 / 60)
                lat += (ord(locator[5]) - ord("A")) * (2.5 / 60)
                lon += 2.5 / 60
                lat += 1.25 / 60
            else:
                lon += 1.0
                lat += 0.5

            return lat, lon
        except Exception:
            return None, None

    @staticmethod
    def _calculate_sun_times(date_value, latitude, longitude, utc_offset):
        import math
        from datetime import datetime, timedelta

        def calc(is_sunrise: bool):
            day = date_value.timetuple().tm_yday
            lng_hour = longitude / 15.0
            approximate = day + (
                (6 - lng_hour) / 24.0
                if is_sunrise
                else (18 - lng_hour) / 24.0
            )

            mean_anomaly = (0.9856 * approximate) - 3.289
            true_long = (
                mean_anomaly
                + 1.916 * math.sin(math.radians(mean_anomaly))
                + 0.020 * math.sin(math.radians(2 * mean_anomaly))
                + 282.634
            ) % 360

            right_ascension = math.degrees(
                math.atan(0.91764 * math.tan(math.radians(true_long)))
            ) % 360

            l_quadrant = math.floor(true_long / 90) * 90
            ra_quadrant = math.floor(right_ascension / 90) * 90
            right_ascension = (
                right_ascension + (l_quadrant - ra_quadrant)
            ) / 15.0

            sin_dec = 0.39782 * math.sin(math.radians(true_long))
            cos_dec = math.cos(math.asin(sin_dec))
            zenith = 90.833

            cos_h = (
                math.cos(math.radians(zenith))
                - sin_dec * math.sin(math.radians(latitude))
            ) / (
                cos_dec * math.cos(math.radians(latitude))
            )

            if cos_h > 1 or cos_h < -1:
                return None

            if is_sunrise:
                hour_angle = 360 - math.degrees(math.acos(cos_h))
            else:
                hour_angle = math.degrees(math.acos(cos_h))

            hour_angle /= 15.0

            local_mean_time = (
                hour_angle
                + right_ascension
                - (0.06571 * approximate)
                - 6.622
            )

            utc_hour = (local_mean_time - lng_hour) % 24
            local_hour = (utc_hour + utc_offset) % 24

            hours = int(local_hour)
            minutes = int(round((local_hour - hours) * 60))
            if minutes >= 60:
                hours = (hours + 1) % 24
                minutes = 0

            return f"{hours:02d}:{minutes:02d}"

        sunrise = calc(True)
        sunset = calc(False)
        return sunrise or "No sunrise", sunset or "No sunset"

    # --------------------- Preferences and Help Slots -----------------

    @pyqtSlot()
    def resetPreferences(self) -> None:
        defaults = {
            "theme": "Dark",
            "show_splash": True,
            "auto_scan": False,
            "check_updates": True,
            "hamclock_url": "",
            "default_cat_port": "",
            "default_audio_device": "",
            "preferred_sdr": "",
            "update_channel": "Stable channel",
            "backup_before_updates": True,
            "spectrum_peak_hold_default": True,
            "spectrum_peak_decay_default": "Medium",
        }

        station_keys = (
            "callsign",
            "locator",
            "operator_name",
            "qth",
            "country",
            "dmr_id",
        )
        existing = self._read_settings()
        for key in station_keys:
            if key in existing:
                defaults[key] = existing[key]

        self._write_settings(defaults)
        self._load_settings()
        self.stationChanged.emit()
        self._notification = "Preferences reset to defaults. Station details were preserved."
        self.notificationChanged.emit()
        self._add_activity("Preferences reset")

    @pyqtSlot(result=str)
    def exportPreferences(self) -> str:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORTS_DIR / "hamradio-pi-settings-backup.json"
        path.write_text(
            json.dumps(self._read_settings(), indent=2) + "\n",
            encoding="utf-8",
        )
        self._notification = f"Settings backup created: {path}"
        self.notificationChanged.emit()
        self._add_activity("Preferences exported")
        return str(path)

    @pyqtSlot()
    def openSettingsFolder(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._open_path(CONFIG_DIR)

    @pyqtSlot()
    def openReportsFolder(self) -> None:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self._open_path(REPORTS_DIR)

    @pyqtSlot(str)
    def openHelpDocument(self, filename: str) -> None:
        safe_name = Path(filename).name
        path = BASE_DIR / "docs" / safe_name

        if not path.exists():
            self._help_status = f"Help document not found: {safe_name}"
            self.helpChanged.emit()
            return

        try:
            self._open_path(path)
            self._help_status = f"Opened {safe_name}."
        except Exception as exc:
            self._help_status = f"Could not open {safe_name}: {exc}"

        self.helpChanged.emit()

    @pyqtSlot()
    def openGithubProject(self) -> None:
        webbrowser.open("https://github.com/ZL4SSB/Ham-Radio-Pi-Ultimate")
        self._help_status = "Opened the project page in your browser."
        self.helpChanged.emit()

    @pyqtSlot()
    def openGithubIssues(self) -> None:
        webbrowser.open(
            "https://github.com/ZL4SSB/Ham-Radio-Pi-Ultimate/issues"
        )
        self._help_status = "Opened GitHub Issues in your browser."
        self.helpChanged.emit()

    @pyqtSlot(result=str)
    def createSupportBundle(self) -> str:
        import zipfile

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = Path(self.createSystemReport())
        bundle = REPORTS_DIR / "hamradio-pi-support-bundle.zip"

        with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
            if report_path.exists():
                archive.write(report_path, report_path.name)

            settings = CONFIG_DIR / "settings.json"
            dashboards = CONFIG_DIR / "dashboards.json"

            if settings.exists():
                archive.write(settings, "settings.json")
            if dashboards.exists():
                archive.write(dashboards, "dashboards.json")

            for log in REPORTS_DIR.glob("*.log"):
                archive.write(log, log.name)

        self._help_status = f"Support bundle created: {bundle}"
        self.helpChanged.emit()
        self._add_activity("Support bundle created")
        return str(bundle)


    def _apply_start_at_login(self, enabled: bool) -> None:
        try:
            if platform.system() == "Windows":
                startup_dir = Path(
                    os.environ.get(
                        "APPDATA",
                        str(Path.home() / "AppData/Roaming"),
                    )
                ) / "Microsoft/Windows/Start Menu/Programs/Startup"
                startup_dir.mkdir(parents=True, exist_ok=True)
                shortcut = startup_dir / "HamRadio-Pi Ultimate.lnk"

                if enabled:
                    launcher = BASE_DIR / "Start-HamRadio-Pi-Ultimate.bat"
                    shortcut_ps = str(shortcut).replace("'", "''")
                    launcher_ps = str(launcher).replace("'", "''")
                    base_dir_ps = str(BASE_DIR).replace("'", "''")
                    script = (
                        "$s=(New-Object -COM WScript.Shell).CreateShortcut("
                        f"'{shortcut_ps}');"
                        f"$s.TargetPath='{launcher_ps}';"
                        f"$s.WorkingDirectory='{base_dir_ps}';"
                        "$s.Description='HamRadio-Pi Ultimate';"
                        "$s.Save()"
                    )
                    subprocess.run(
                        [
                            "powershell.exe",
                            "-NoProfile",
                            "-ExecutionPolicy",
                            "Bypass",
                            "-Command",
                            script,
                        ],
                        check=True,
                        timeout=20,
                    )
                else:
                    shortcut.unlink(missing_ok=True)
            else:
                autostart_dir = Path.home() / ".config/autostart"
                autostart_dir.mkdir(parents=True, exist_ok=True)
                desktop_file = autostart_dir / "hamradio-pi-ultimate.desktop"

                if enabled:
                    launcher = Path.home() / ".local/bin/hamradio-pi-ultimate"
                    desktop_file.write_text(
                        "[Desktop Entry]\n"
                        "Type=Application\n"
                        "Name=HamRadio-Pi Ultimate\n"
                        f"Exec={launcher}\n"
                        "Icon=hamradio-pi-ultimate\n"
                        "Terminal=false\n"
                        "X-GNOME-Autostart-enabled=true\n",
                        encoding="utf-8",
                    )
                    desktop_file.chmod(0o755)
                else:
                    desktop_file.unlink(missing_ok=True)
        except Exception as exc:
            self._notification = f"Could not update start-at-login setting: {exc}"
            self.notificationChanged.emit()

    def _open_path(self, path: Path) -> None:
        path = path.resolve()

        if platform.system() == "Windows":
            os.startfile(str(path))
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            opener = shutil.which("xdg-open")
            if not opener:
                raise RuntimeError("xdg-open is not installed.")
            subprocess.Popen([opener, str(path)], start_new_session=True)

    @pyqtSlot()
    def checkTimeSync(self) -> None:
        self._time_sync_status = "Checking…"
        self.timeSyncChanged.emit()
        self._run_in_thread(self._check_time_sync_worker)

    @pyqtSlot()
    def syncTimeNow(self) -> None:
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["w32tm", "/resync"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self._time_sync_status = (
                    "Resynchronisation requested"
                    if result.returncode == 0
                    else "Windows Time resync failed"
                )
            else:
                if shutil.which("timedatectl"):
                    subprocess.run(
                        ["sudo", "timedatectl", "set-ntp", "true"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    self._time_sync_status = "Network time enabled"
                elif shutil.which("chronyc"):
                    subprocess.run(
                        ["sudo", "chronyc", "makestep"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    self._time_sync_status = "Chrony sync requested"
                else:
                    self._time_sync_status = "No supported time service found"
        except Exception as exc:
            self._time_sync_status = f"Sync failed: {exc}"
        self.timeSyncChanged.emit()
        QTimer.singleShot(1200, self.checkTimeSync)

    def _check_time_sync_worker(self) -> None:
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["w32tm", "/query", "/status"],
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                output = result.stdout or ""
                self._time_sync_status = (
                    "Synchronised" if result.returncode == 0 else "Not synchronised"
                )
                self._time_sync_source = "Windows Time"
                for line in output.splitlines():
                    if line.lower().startswith("source:"):
                        self._time_sync_source = line.split(":", 1)[1].strip()
                        break
                self._time_sync_quality = (
                    "Good for digital modes"
                    if result.returncode == 0
                    else "Needs attention"
                )
                self._gps_status = "USB GPS scan available under Hardware"
                self._pps_status = "Not detected"
            else:
                synced = False
                source = "System clock"
                if shutil.which("timedatectl"):
                    result = subprocess.run(
                        ["timedatectl", "show"],
                        capture_output=True,
                        text=True,
                        timeout=20,
                    )
                    values = {}
                    for line in result.stdout.splitlines():
                        if "=" in line:
                            key, value = line.split("=", 1)
                            values[key] = value
                    synced = values.get("NTPSynchronized", "no").lower() == "yes"
                    source = (
                        "Network NTP"
                        if values.get("NTP", "no").lower() == "yes"
                        else "System clock"
                    )
                elif shutil.which("chronyc"):
                    result = subprocess.run(
                        ["chronyc", "tracking"],
                        capture_output=True,
                        text=True,
                        timeout=20,
                    )
                    synced = result.returncode == 0
                    source = "Chrony"

                self._time_sync_status = "Synchronised" if synced else "Not synchronised"
                self._time_sync_source = source
                self._time_sync_quality = (
                    "Good for digital modes" if synced else "Needs attention"
                )
                self._gps_status = (
                    "Detected"
                    if shutil.which("gpspipe")
                    else "Not detected"
                )
                self._pps_status = (
                    "Detected"
                    if Path("/dev/pps0").exists()
                    else "Not detected"
                )
        except Exception as exc:
            self._time_sync_status = f"Check failed: {exc}"
        self.timeSyncChanged.emit()

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
        self._theme = settings.get("theme", "Ultimate Teal")
        self._show_splash = settings.get("show_splash", True)
        self._auto_scan = settings.get("auto_scan", False)
        self._check_updates = settings.get("check_updates", True)
        self._hamclock_url = ""
        self._default_cat_port = settings.get("default_cat_port", "")
        self._default_audio_device = settings.get("default_audio_device", "")
        self._preferred_sdr = settings.get("preferred_sdr", "")
        self._update_channel = settings.get("update_channel", "Stable channel")
        self._backup_before_updates = settings.get("backup_before_updates", True)
        self._start_at_login = settings.get("start_at_login", False)
        self._spectrum_peak_hold_default = settings.get(
            "spectrum_peak_hold_default",
            True,
        )
        self._spectrum_peak_decay_default = settings.get(
            "spectrum_peak_decay_default",
            "Medium",
        )
        self._dx_cluster_host = str(
            settings.get(
                "dx_cluster_host",
                "",
            )
        )
        try:
            self._dx_cluster_port = int(
                settings.get(
                    "dx_cluster_port",
                    7300,
                )
            )
        except (TypeError, ValueError):
            self._dx_cluster_port = 7300
        self._dx_cluster_login = str(
            settings.get(
                "dx_cluster_login",
                "",
            )
        )
        self._dx_cluster_enabled = bool(
            settings.get(
                "dx_cluster_enabled",
                False,
            )
        )
        self._propagation_demo_mode = bool(
            settings.get(
                "propagation_demo_mode",
                True,
            )
        )

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
