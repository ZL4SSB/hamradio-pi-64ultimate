from __future__ import annotations

import json
import os
import platform
import shlex
import shutil
import socket
import subprocess
import sys
import time
import webbrowser
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, pyqtProperty, pyqtSignal, pyqtSlot

from core_services import (
    CatBroker,
    DigitalWorkspaceService,
    LogbookService,
    RadioStateService,
    SatelliteRotatorService,
)

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
    radioMapChanged = pyqtSignal()
    radioStateChanged = pyqtSignal()
    catBrokerChanged = pyqtSignal()
    digitalChanged = pyqtSignal()
    logbookChanged = pyqtSignal()
    satelliteChanged = pyqtSignal()
    toolsChanged = pyqtSignal()
    updateChanged = pyqtSignal()
    helpChanged = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self._page = "Dashboard"
        self._radio_service = RadioStateService()
        self._cat_broker = CatBroker(self._radio_service)
        self._digital_service = DigitalWorkspaceService()
        self._logbook_service = LogbookService(DATA_DIR / 'hrpu-logbook.sqlite3')
        self._satellite_service = SatelliteRotatorService()
        self._logbook_rows = self._logbook_service.recent()
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
        self._propagation_updated = "Never"
        self._solar_flux = "—"
        self._kp_index = "—"
        self._solar_wind_speed = "—"
        self._solar_wind_density = "—"
        self._solar_wind_bz = "—"
        self._xray_class = "—"
        self._geomagnetic_state = "Unknown"
        self._hf_conditions = []
        self._map_target = {
            "name": "Click the map",
            "bearing": "—",
            "long_path": "—",
            "distance": "—",
            "sunrise": "—",
            "sunset": "—",
            "greyline": "—",
        }
        self._map_spots = [
            {"call": "G4ABC", "grid": "IO91", "band": "20 m", "mode": "FT8", "snr": "-12", "source": "DECODED"},
            {"call": "JA1XYZ", "grid": "PM95", "band": "20 m", "mode": "SSB", "snr": "—", "source": "DX"},
            {"call": "VK3ABC", "grid": "QF22", "band": "40 m", "mode": "WSPR", "snr": "-18", "source": "WSPR"},
        ]
        self._map_demo_mode = True
        self._vhf_conditions = []
        self._meteor_status = {}
        self._beacon_status = {}
        self._propagation_confidence = []

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

        self.audio_meter_timer = QTimer(self)
        self.audio_meter_timer.timeout.connect(self._publish_audio_monitor)
        self.audio_meter_timer.start(50)

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


    # ------------------------- Unified station core ------------------

    @pyqtProperty("QVariantMap", notify=radioStateChanged)
    def radioState(self):
        return self._radio_service.state.to_dict()

    @pyqtProperty("QVariantMap", notify=catBrokerChanged)
    def catBroker(self):
        return self._cat_broker.snapshot()

    @pyqtProperty("QVariantMap", notify=digitalChanged)
    def digitalState(self):
        return self._digital_service.snapshot()

    @pyqtProperty("QVariantList", notify=logbookChanged)
    def logbookRows(self):
        return self._logbook_rows

    @pyqtProperty("QVariantMap", notify=satelliteChanged)
    def satelliteState(self):
        return self._satellite_service.snapshot()

    @pyqtSlot(float)
    def setRadioFrequency(self, frequency_mhz: float) -> None:
        self._radio_service.set_frequency_mhz(frequency_mhz)
        self._notification = (
            f"Radio context changed to "
            f"{self._radio_service.state.frequency_hz / 1_000_000:.6f} MHz "
            f"({self._radio_service.state.band})."
        )
        self._add_activity("Radio frequency context changed")
        self.radioStateChanged.emit()
        self.notificationChanged.emit()
        self.radioMapChanged.emit()

    @pyqtSlot(str)
    def setRadioMode(self, mode: str) -> None:
        self._radio_service.set_mode(mode)
        self.radioStateChanged.emit()
        self._add_activity(f"Radio mode changed to {self._radio_service.state.mode}")

    @pyqtSlot(bool)
    def setRadioPtt(self, active: bool) -> None:
        self._radio_service.set_ptt(active)
        self.radioStateChanged.emit()
        self._add_activity("PTT TX" if active else "PTT RX")

    @pyqtSlot(bool)
    def setRadioSplit(self, active: bool) -> None:
        self._radio_service.set_split(active)
        self.radioStateChanged.emit()

    @pyqtSlot(str, str, str, str, float, int)
    def saveRadioAudioProfile(
        self,
        rx_device: str,
        tx_device: str,
        rx_channel: str,
        tx_channel: str,
        rx_gain_db: float,
        tx_level: int,
    ) -> None:
        self._radio_service.configure_audio(
            rx_device,
            tx_device,
            rx_channel,
            tx_channel,
            rx_gain_db,
            tx_level,
        )
        self._notification = "Radio audio-routing profile updated."
        self._add_activity("Radio audio-routing profile updated")
        self.radioStateChanged.emit()
        self.notificationChanged.emit()

    @pyqtSlot()
    def probeCatBroker(self) -> None:
        self._cat_broker.probe()
        self._radio_service.state.cat_connected = (
            self._cat_broker.status == "Ready"
        )
        self.catBrokerChanged.emit()
        self.radioStateChanged.emit()
        self._notification = self._cat_broker.detail
        self.notificationChanged.emit()

    @pyqtSlot(str)
    def registerCatClient(self, client_name: str) -> None:
        self._cat_broker.register_client(client_name)
        self.catBrokerChanged.emit()

    @pyqtSlot(str)
    def setDigitalMode(self, mode: str) -> None:
        if mode in self._digital_service.MODES:
            self._digital_service.mode = mode
            self._digital_service.status = f"{mode} workspace selected"
            self.digitalChanged.emit()

    @pyqtSlot(bool)
    def setDigitalTxEnabled(self, enabled: bool) -> None:
        self._digital_service.tx_enabled = bool(enabled)
        self.digitalChanged.emit()

    @pyqtSlot(bool)
    def setDigitalAutoSequence(self, enabled: bool) -> None:
        self._digital_service.auto_sequence = bool(enabled)
        self.digitalChanged.emit()

    @pyqtSlot()
    def requestDigitalTune(self) -> None:
        self._digital_service.status = (
            "TUNE unavailable — no live HRPU modulator/PTT provider is configured"
        )
        self._digital_service.tx_enabled = False
        self.digitalChanged.emit()
        self._notification = "Digital TUNE was not started; live transmit provider unavailable."
        self.notificationChanged.emit()

    @pyqtSlot()
    def loadDigitalPreview(self) -> None:
        state = self._digital_service.demo_decode()
        digital_spots = [
            {
                "call": row["call"],
                "grid": row["grid"],
                "band": self._radio_service.state.band,
                "mode": state["mode"],
                "snr": str(row["snr"]),
                "source": "DECODED",
            }
            for row in state["decoded"]
        ]
        retained = [
            item for item in self._map_spots
            if item.get("source") != "DECODED"
        ]
        self._map_spots = retained + digital_spots
        self.digitalChanged.emit()
        self.radioMapChanged.emit()
        self._notification = "Preview decode activity loaded. This is not live RF decoding."
        self.notificationChanged.emit()

    @pyqtSlot(str, str, str, str, str)
    def addQso(
        self,
        callsign: str,
        grid: str,
        rst_sent: str,
        rst_received: str,
        notes: str,
    ) -> None:
        try:
            result = self._logbook_service.add(
                callsign,
                grid,
                self._radio_service.state.frequency_hz,
                self._digital_service.mode
                if self._digital_service.mode
                else self._radio_service.state.mode,
                rst_sent,
                rst_received,
                notes,
            )
            self._logbook_rows = self._logbook_service.recent()
            self._notification = (
                f"Logged {result['callsign']} on {result['band']} "
                f"{result['mode']}."
            )
            self._add_activity(f"QSO logged: {result['callsign']}")
            self.logbookChanged.emit()
            self.notificationChanged.emit()
        except Exception as exc:
            self._notification = f"Logbook error: {exc}"
            self.notificationChanged.emit()

    @pyqtSlot()
    def exportAdif(self) -> None:
        try:
            path = self._logbook_service.export_adif(
                REPORTS_DIR / "hrpu-logbook.adi"
            )
            self._notification = f"ADIF exported to {path}."
            self._add_activity("Logbook exported to ADIF")
        except Exception as exc:
            self._notification = f"ADIF export failed: {exc}"
        self.notificationChanged.emit()

    @pyqtSlot(str)
    def selectSatellitePreview(self, target: str) -> None:
        self._satellite_service.select_preview(target)
        self._radio_service.state.rotator_azimuth = (
            self._satellite_service.azimuth
        )
        self._radio_service.state.rotator_elevation = (
            self._satellite_service.elevation
        )
        self.satelliteChanged.emit()
        self.radioStateChanged.emit()

    @pyqtSlot(bool)
    def setSatelliteTracking(self, active: bool) -> None:
        self._satellite_service.tracking = False
        self._satellite_service.status = (
            "Tracking unavailable — live TLE and rotator providers are not configured"
            if active else "Tracking stopped"
        )
        self.satelliteChanged.emit()

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

    @pyqtSlot(str)
    def installApplication(self, package: str) -> None:
        item = next((app for app in self._applications if app.get("package") == package), None)
        if not item:
            self.setNotification("Application package was not found in the HRPU catalogue.")
            return
        if self._application_is_installed(item):
            self.setNotification(f"{item['name']} is already installed.")
            self.refreshApplications()
            return
        if platform.system() == "Windows":
            self.setNotification(
                f"{item['name']} has no automatic Windows installer in HRPU. "
                "Open its Help guide for supported installation options."
            )
            return
        terminal = (shutil.which("x-terminal-emulator") or shutil.which("lxterminal")
                    or shutil.which("gnome-terminal") or shutil.which("xterm"))
        if not terminal:
            self.setNotification("No terminal was found. Install the package with apt.")
            return
        command = f"sudo apt-get update && sudo apt-get install -y {shlex.quote(package)}; echo; read -r -p 'Press ENTER to close…'"
        try:
            if Path(terminal).name == "gnome-terminal":
                launch = [terminal, "--", "bash", "-lc", command]
            else:
                launch = [terminal, "-e", "bash", "-lc", command]
            subprocess.Popen(launch, start_new_session=True)
            self.setNotification(f"Installer opened for {item['name']}.")
            self._add_activity(f"Install requested: {item['name']}")
            QTimer.singleShot(5000, self.refreshApplications)
        except Exception as exc:
            self.setNotification(f"Could not open installer: {exc}")

    @pyqtSlot(str)
    def openApplicationHelp(self, name: str) -> None:
        filename = "APP-" + "".join(ch if ch.isalnum() else "-" for ch in name.upper()).strip("-") + ".md"
        self.openHelpDocument(filename)

    @pyqtSlot(str, str)
    def runWorkspaceAction(self, workspace: str, action: str) -> None:
        if workspace == "About":
            mapping = {
                "Project Information": "README.md", "Licence": "DEPENDENCIES.md",
                "GitHub Repository": "github", "Donate": "donate",
                "Credits": "DEPENDENCIES.md", "System Information": "report",
            }
            target = mapping.get(action)
            if target == "github": self.openGithubProject()
            elif target == "donate": self.openDonate()
            elif target == "report": self.createSystemReport()
            elif target:
                path = BASE_DIR / target
                if path.exists(): self._open_path(path)
            return
        # WPSD media writing is intentionally not simulated. The control opens
        # the exact guide and reports that the provider is not configured.
        self._help_status = f"{action}: open the WPSD guide for requirements and safety steps."
        self.helpChanged.emit()
        self._notification = f"{action} requires the WPSD media provider; guide opened."
        self.notificationChanged.emit()
        self.openHelpDocument("WPSD-CENTRE.md")

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

    @pyqtSlot(str, bool, bool, bool, str, str, str, str, str, bool, bool, str)
    def savePreferences(
        self,
        theme_name: str,
        show_splash: bool,
        auto_scan: bool,
        check_updates: bool,
        hamclock_url: str,
        default_cat_port: str,
        default_audio_device: str,
        preferred_sdr: str,
        update_channel: str,
        backup_before_updates: bool,
        spectrum_peak_hold_default: bool,
        spectrum_peak_decay_default: str,
    ) -> None:
        settings = self._read_settings()
        settings.update({
            "theme": theme_name.strip() or "Dark",
            "show_splash": bool(show_splash),
            "auto_scan": bool(auto_scan),
            "check_updates": bool(check_updates),
            "hamclock_url": self._normalise_web_url(hamclock_url),
            "default_cat_port": default_cat_port.strip(),
            "default_audio_device": default_audio_device.strip(),
            "preferred_sdr": preferred_sdr.strip(),
            "update_channel": update_channel.strip() or "Stable channel",
            "backup_before_updates": bool(backup_before_updates),
            "spectrum_peak_hold_default": bool(spectrum_peak_hold_default),
            "spectrum_peak_decay_default": (
                spectrum_peak_decay_default.strip() or "Medium"
            ),
        })
        self._write_settings(settings)
        self._load_settings()
        self.stationChanged.emit()
        self._notification = "Preferences saved and reloaded."
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
            self._update_radio_awareness(flux, kp)
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


    @pyqtProperty("QVariantMap", notify=radioMapChanged)
    def mapTarget(self):
        return self._map_target

    @pyqtProperty("QVariantList", notify=radioMapChanged)
    def mapSpots(self):
        return self._map_spots

    @pyqtProperty(bool, notify=radioMapChanged)
    def mapDemoMode(self) -> bool:
        return self._map_demo_mode

    @pyqtProperty("QVariantList", notify=propagationChanged)
    def vhfConditions(self):
        return self._vhf_conditions

    @pyqtProperty("QVariantMap", notify=propagationChanged)
    def meteorStatus(self):
        return self._meteor_status

    @pyqtProperty("QVariantMap", notify=propagationChanged)
    def beaconStatus(self):
        return self._beacon_status

    @pyqtProperty("QVariantList", notify=propagationChanged)
    def propagationConfidence(self):
        return self._propagation_confidence

    @staticmethod
    def _grid_to_latlon(locator: str):
        loc = (locator or "").strip().upper()
        if len(loc) < 4 or loc.startswith("NOT "):
            return None
        try:
            a = ord(loc[0]) - 65
            bb = ord(loc[1]) - 65
            c = int(loc[2])
            d = int(loc[3])
            if not (0 <= a <= 17 and 0 <= bb <= 17):
                return None
            lon = -180.0 + a * 20.0 + c * 2.0 + 1.0
            lat = -90.0 + bb * 10.0 + d + 0.5
            if len(loc) >= 6:
                e = ord(loc[4]) - 65
                f = ord(loc[5]) - 65
                if 0 <= e < 24 and 0 <= f < 24:
                    lon = -180.0 + a * 20.0 + c * 2.0 + e / 12.0 + 1.0 / 24.0
                    lat = -90.0 + bb * 10.0 + d + f / 24.0 + 1.0 / 48.0
            return lat, lon
        except Exception:
            return None

    @staticmethod
    def _bearing_distance(lat1, lon1, lat2, lon2):
        import math
        p1 = math.radians(lat1)
        p2 = math.radians(lat2)
        dl = math.radians(lon2 - lon1)
        y = math.sin(dl) * math.cos(p2)
        x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
        bearing = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
        aa = math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        distance = 6371.0 * 2.0 * math.atan2(math.sqrt(aa), math.sqrt(max(0.0, 1-aa)))
        return bearing, distance

    @staticmethod
    def _sun_times_utc(lat, lon, when=None):
        import math
        when = when or datetime.utcnow()
        day = when.timetuple().tm_yday
        gamma = 2.0 * math.pi / 365.0 * (day - 1)
        decl = (
            0.006918 - 0.399912*math.cos(gamma) + 0.070257*math.sin(gamma)
            - 0.006758*math.cos(2*gamma) + 0.000907*math.sin(2*gamma)
            - 0.002697*math.cos(3*gamma) + 0.00148*math.sin(3*gamma)
        )
        eqtime = 229.18 * (
            0.000075 + 0.001868*math.cos(gamma) - 0.032077*math.sin(gamma)
            - 0.014615*math.cos(2*gamma) - 0.040849*math.sin(2*gamma)
        )
        latr = math.radians(max(-89.8, min(89.8, lat)))
        zenith = math.radians(90.833)
        cos_ha = (math.cos(zenith)/(math.cos(latr)*math.cos(decl))
                  - math.tan(latr)*math.tan(decl))
        if cos_ha < -1 or cos_ha > 1:
            return "Polar", "Polar", "Seasonal"
        ha = math.degrees(math.acos(cos_ha))
        noon = 720 - 4*lon - eqtime
        rise = noon - 4*ha
        setting = noon + 4*ha
        def fmt(minutes):
            minutes %= 1440
            return f"{int(minutes//60):02d}:{int(minutes%60):02d} UTC"
        return fmt(rise), fmt(setting), f"{fmt(rise-24)}–{fmt(rise+24)}"

    @pyqtSlot(float, float)
    def selectMapTarget(self, lat: float, lon: float) -> None:
        home = self._grid_to_latlon(self._locator)
        if home is None:
            self._map_target = {
                "name": f"{lat:.2f}°, {lon:.2f}°",
                "bearing": "Set station locator",
                "long_path": "—",
                "distance": "—",
                "sunrise": "—",
                "sunset": "—",
                "greyline": "—",
            }
        else:
            bearing, distance = self._bearing_distance(home[0], home[1], lat, lon)
            sunrise, sunset, greyline = self._sun_times_utc(lat, lon)
            self._map_target = {
                "name": f"{lat:.2f}°, {lon:.2f}°",
                "bearing": f"{bearing:.0f}°",
                "long_path": f"{(bearing + 180) % 360:.0f}°",
                "distance": f"{distance:,.0f} km",
                "sunrise": sunrise,
                "sunset": sunset,
                "greyline": greyline,
            }
        self.radioMapChanged.emit()

    def _update_radio_awareness(self, flux, kp):
        now = datetime.utcnow()
        showers = [
            ("Quadrantids", 1, 3, 120), ("Lyrids", 4, 22, 18),
            ("Eta Aquariids", 5, 6, 50), ("Perseids", 8, 12, 100),
            ("Orionids", 10, 21, 20), ("Leonids", 11, 17, 15),
            ("Geminids", 12, 14, 120), ("Ursids", 12, 22, 10),
        ]
        def day_distance(month, day):
            target = datetime(now.year, month, day)
            return abs((target.date() - now.date()).days)
        shower = min(showers, key=lambda x: day_distance(x[1], x[2]))
        days = day_distance(shower[1], shower[2])
        state = "ACTIVE / PEAK" if days <= 1 else "APPROACHING" if days <= 7 else "QUIET"
        self._meteor_status = {
            "name": shower[0], "state": state, "peak": f"{shower[2]:02d}/{shower[1]:02d}",
            "zhr": str(shower[3]), "detail": "144 MHz meteor-scatter opportunity" if days <= 7 else f"{days} days from nearest major peak"
        }

        kp_value = kp if kp is not None else 3.0
        self._vhf_conditions = [
            {"name": "Aurora", "state": "HIGH" if kp_value >= 6 else "MODERATE" if kp_value >= 4 else "LOW"},
            {"name": "Meteor", "state": state},
            {"name": "Sporadic-E", "state": "SEASONAL / CHECK 6 m"},
            {"name": "Tropo", "state": "LOCAL WEATHER DEPENDENT"},
        ]

        beacons = [
            "4U1UN", "VE8AT", "W6WX", "KH6WO", "ZL6B",
            "VK6RBP", "JA2IGY", "RR9O", "VR2B", "4S7B",
            "ZS6DN", "5Z4B", "4X6TU", "OH2B", "CS3B",
            "LU4AA", "OA4B", "YV5B",
        ]
        slot = int(now.timestamp() // 10) % len(beacons)
        self._beacon_status = {
            "current": beacons[slot],
            "next": beacons[(slot + 1) % len(beacons)],
            "seconds": str(10 - (now.second % 10)),
            "bands": "14.100 • 18.110 • 21.150 • 24.930 • 28.200 MHz",
        }

        flux_value = flux if flux is not None else 100.0
        for item in self._hf_conditions:
            score = 45
            if item["condition"] == "Excellent": score = 88
            elif item["condition"] == "Good": score = 76
            elif item["condition"] == "Fair": score = 58
            score += 4 if flux_value >= 150 and item["band"] in ("20 m","17 m","15 m","10 m") else 0
            self._propagation_confidence.append({
                "band": item["band"],
                "confidence": min(96, score),
                "summary": "MODEL + OBSERVATION FRAMEWORK",
            })
        self._propagation_confidence = self._propagation_confidence[-len(self._hf_conditions):]
        self.propagationChanged.emit()
        self.radioMapChanged.emit()

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
        self._default_cat_port = settings.get("default_cat_port", "")
        self._default_audio_device = settings.get("default_audio_device", "")
        self._preferred_sdr = settings.get("preferred_sdr", "")
        self._update_channel = settings.get("update_channel", "Stable channel")
        self._backup_before_updates = settings.get("backup_before_updates", True)
        self._spectrum_peak_hold_default = settings.get(
            "spectrum_peak_hold_default",
            True,
        )
        self._spectrum_peak_decay_default = settings.get(
            "spectrum_peak_decay_default",
            "Medium",
        )


    @pyqtSlot()
    def refreshApplications(self) -> None:
        self._load_applications()
        installed_count = sum(
            1 for item in self._applications if item.get("installed")
        )
        self._notification = (
            f"Application check complete: {installed_count} installed."
        )
        self._add_activity(
            f"Applications checked: {installed_count} installed"
        )
        self.applicationsChanged.emit()
        self.notificationChanged.emit()

    def _application_is_installed(self, item: dict) -> bool:
        command = item.get("command", "")
        if command and shutil.which(command):
            return True

        package = item.get("package", "")
        if package and platform.system() != "Windows":
            try:
                result = subprocess.run(
                    ["dpkg-query", "-W", "-f=${Status}", package],
                    capture_output=True,
                    text=True,
                    timeout=6,
                )
                if (
                    result.returncode == 0
                    and "install ok installed" in result.stdout
                ):
                    return True
            except Exception:
                pass

        if platform.system() == "Windows":
            name = str(item.get("name", "")).lower()
            roots = [
                Path(os.environ.get("ProgramFiles", "")),
                Path(os.environ.get("ProgramFiles(x86)", "")),
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs",
            ]
            for root_path in roots:
                if not root_path.exists():
                    continue
                try:
                    if any(
                        name in child.name.lower()
                        for child in root_path.iterdir()
                    ):
                        return True
                except Exception:
                    continue

        return False

    @pyqtSlot(str)
    def removeApplication(self, package: str) -> None:
        item = next(
            (
                app for app in self._applications
                if app.get("package") == package
            ),
            None,
        )
        if not item:
            self.setNotification("Application entry was not found.")
            return

        if not self._application_is_installed(item):
            self.setNotification(
                f"{item.get('name', package)} is not installed."
            )
            self.refreshApplications()
            return

        if platform.system() == "Windows":
            safe_name = str(item.get("name", "")).replace("'", "''")
            script = (
                "$apps=@("
                "Get-ItemProperty "
                "'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' "
                "-ErrorAction SilentlyContinue;"
                "Get-ItemProperty "
                "'HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' "
                "-ErrorAction SilentlyContinue;"
                "Get-ItemProperty "
                "'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' "
                "-ErrorAction SilentlyContinue"
                ");"
                f"$app=$apps|Where-Object{{$_.DisplayName -like '*{safe_name}*'}}"
                "|Select-Object -First 1;"
                "if($app -and $app.UninstallString){"
                "Start-Process 'cmd.exe' "
                "-ArgumentList '/c',$app.UninstallString -Verb RunAs"
                "}else{"
                f"Write-Host 'No registered uninstaller found for {safe_name}';"
                "Read-Host 'Press Enter to close'"
                "}"
            )
            try:
                subprocess.Popen([
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    script,
                ])
                self.setNotification(
                    f"Windows uninstaller requested for {item['name']}."
                )
                QTimer.singleShot(3000, self.refreshApplications)
            except Exception as exc:
                self.setNotification(f"Remove failed: {exc}")
            return

        command = ["sudo", "apt", "remove", "--autoremove", package]
        quoted = " ".join(shlex.quote(part) for part in command)
        shell_cmd = f"{quoted}; echo; read -p 'Press Enter to close…'"

        candidates = [
            ["x-terminal-emulator", "-e", "bash", "-lc", shell_cmd],
            ["lxterminal", "-e", f"bash -lc {shlex.quote(shell_cmd)}"],
            ["gnome-terminal", "--", "bash", "-lc", shell_cmd],
            ["xterm", "-T", f"Remove {item['name']}", "-e", "bash", "-lc", shell_cmd],
        ]
        launch = next(
            (candidate for candidate in candidates if shutil.which(candidate[0])),
            None,
        )

        if launch is None:
            self.setNotification(
                "No terminal application was found for apt removal."
            )
            return

        try:
            subprocess.Popen(launch)
            self._add_activity(f"Remove requested: {item['name']}")
            self.setNotification(
                f"Removal opened for {item['name']}. Confirm the apt prompt."
            )
            QTimer.singleShot(3000, self.refreshApplications)
        except Exception as exc:
            self.setNotification(f"Remove failed: {exc}")

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
                "installed": self._application_is_installed(item),
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
