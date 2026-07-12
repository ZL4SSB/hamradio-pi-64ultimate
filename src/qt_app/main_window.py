from __future__ import annotations

import shutil
import subprocess
import webbrowser

from PyQt6.QtCore import Qt, QProcess, QThreadPool, QTimer
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QPushButton, QStackedWidget, QMessageBox, QButtonGroup
)

from constants import APP_NAME, APP_VERSION, ASSETS_DIR, DONATE_URL, SCRIPTS_DIR
from services.live_status_service import top_status_snapshot
from qt_app.workers import FunctionWorker
from qt_app.pages.dashboard import DashboardPage
from qt_app.pages.applications import ApplicationsPage
from qt_app.pages.hardware import HardwarePage
from qt_app.pages.wpsd import WPSDPage
from qt_app.pages.propagation import PropagationPage
from qt_app.pages.settings import SettingsPage
from qt_app.pages.logs import LogsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — Ham Shack Control Centre")
        self.resize(1320, 850)
        self.setMinimumSize(1040, 700)
        self.setWindowIcon(QIcon(str(ASSETS_DIR / "branding" / "hamradio-pi-256.png")))

        self.pool = QThreadPool.globalInstance()
        self.process = None

        central = QWidget()
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(245)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(12, 16, 12, 14)
        side.setSpacing(4)

        brand_row = QHBoxLayout()
        logo = QLabel()
        pix = QPixmap(str(ASSETS_DIR / "branding" / "hamradio-pi-128.png"))
        if not pix.isNull():
            logo.setPixmap(
                pix.scaled(
                    64,
                    64,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        brand_row.addWidget(logo)

        texts = QVBoxLayout()
        title = QLabel("HamRadio-Pi")
        title.setStyleSheet("font-size:15pt;font-weight:700;")
        texts.addWidget(title)
        sub = QLabel("ULTIMATE")
        sub.setStyleSheet("color:#19C2AF;font-weight:700;")
        texts.addWidget(sub)
        brand_row.addLayout(texts)
        side.addLayout(brand_row)
        side.addSpacing(10)

        self.stack = QStackedWidget()
        dashboard = DashboardPage(self.open_hardware)
        self.pages = [
            dashboard,
            ApplicationsPage(self),
            WPSDPage(self),
            HardwarePage(),
            PropagationPage(),
            SettingsPage(),
            LogsPage(),
        ]
        self.page_names = [
            "Dashboard",
            "Applications",
            "WPSD Centre",
            "Hardware",
            "Propagation",
            "Settings",
            "Help & Logs",
        ]
        icons = ["⌂", "▦", "◉", "⌁", "≋", "⚙", "?"]

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        for index, (name, icon) in enumerate(zip(self.page_names, icons)):
            button = QPushButton(f"  {icon}   {name}")
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.setToolTip(name)
            button.clicked.connect(lambda _, i=index: self.set_page(i))
            self.button_group.addButton(button, index)
            side.addWidget(button)
            self.stack.addWidget(self.pages[index])

        dashboard.open_page_requested.connect(self.set_page)
        self.button_group.button(0).setChecked(True)

        side.addStretch()

        donate = QPushButton("Donate")
        donate.setObjectName("Donate")
        donate.setToolTip("Support development through PayPal. Starts at $1 USD.")
        donate.clicked.connect(lambda: webbrowser.open(DONATE_URL))
        side.addWidget(donate)

        version = QLabel(f"Version {APP_VERSION}")
        version.setObjectName("Muted")
        side.addWidget(version)

        outer.addWidget(sidebar)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        top = QFrame()
        top.setObjectName("TopBar")
        top.setFixedHeight(52)
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(16, 0, 16, 0)

        self.top_title = QLabel("Dashboard")
        self.top_title.setStyleSheet("font-weight:700;font-size:11pt;")
        top_lay.addWidget(self.top_title)
        top_lay.addStretch()

        self.top_model = QLabel("Pi")
        self.top_model.setObjectName("TopMetric")
        top_lay.addWidget(self.top_model)
        top_lay.addSpacing(14)

        self.top_temperature = QLabel("CPU —")
        self.top_temperature.setObjectName("TopMetric")
        top_lay.addWidget(self.top_temperature)
        top_lay.addSpacing(14)

        self.top_memory = QLabel("RAM —")
        self.top_memory.setObjectName("TopMetric")
        top_lay.addWidget(self.top_memory)
        top_lay.addSpacing(14)

        self.top_station = QLabel("No callsign")
        self.top_station.setObjectName("TopMetric")
        top_lay.addWidget(self.top_station)
        top_lay.addSpacing(14)

        self.online = QLabel("● Checking")
        self.online.setStyleSheet("color:#F0C76D;font-weight:700;")
        top_lay.addWidget(self.online)

        right.addWidget(top)
        right.addWidget(self.stack, 1)

        status = QFrame()
        status.setFixedHeight(30)
        status.setStyleSheet("background:#08111A;")
        status_lay = QHBoxLayout(status)
        status_lay.setContentsMargins(12, 0, 12, 0)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color:#9CB0C3;")
        status_lay.addWidget(self.status_label)
        status_lay.addStretch()

        footer = QLabel("Built for Amateur Radio")
        footer.setStyleSheet("color:#9CB0C3;")
        status_lay.addWidget(footer)

        right.addWidget(status)
        outer.addLayout(right, 1)

        self.set_page(0)

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.refresh_top_status)
        self.status_timer.start(5000)
        self.refresh_top_status()

    @property
    def logs_page(self):
        return self.pages[-1]

    def set_page(self, index: int):
        self.stack.setCurrentIndex(index)
        button = self.button_group.button(index)
        if button:
            button.setChecked(True)
        self.top_title.setText(self.page_names[index])

    def refresh_top_status(self):
        worker = FunctionWorker(top_status_snapshot)
        worker.signals.finished.connect(self._apply_top_status)
        self.pool.start(worker)

    def _apply_top_status(self, data: dict):
        online = bool(data.get("online"))
        self.online.setText("● Online" if online else "● Offline")
        self.online.setStyleSheet(
            f"color:{'#4BD9A8' if online else '#F17982'};font-weight:700;"
        )
        self.top_temperature.setText(f"CPU {data.get('temperature', '—')}")
        mem = data.get("memory_percent")
        self.top_memory.setText(f"RAM {mem}%" if mem is not None else "RAM —")
        model = str(data.get("model", "Pi"))
        self.top_model.setText("Pi 400" if "400" in model else model[:22])
        callsign = data.get("callsign", "No callsign")
        locator = data.get("locator", "No locator")
        self.top_station.setText(f"{callsign} · {locator}")

    def log(self, text: str):
        self.logs_page.append(text)
        self.pages[0].add_log(text)

    def open_hardware(self):
        self.set_page(3)
        self.pages[3].scan()

    def launch_application(self, entry):
        try:
            subprocess.Popen([entry.command], start_new_session=True)
            self.status_label.setText(f"Launched {entry.name}")
        except Exception as exc:
            QMessageBox.critical(self, APP_NAME, str(exc))

    def install_application(self, entry):
        answer = QMessageBox.question(
            self,
            APP_NAME,
            f"Install {entry.name}?\n\nPackage: {entry.package}",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._run_package(["install", "-y", entry.package], f"Install {entry.name}")

    def package_action(self, action, entry):
        args = {
            "update": ["install", "--only-upgrade", "-y", entry.package],
            "repair": ["install", "--reinstall", "-y", entry.package],
            "remove": ["remove", "-y", entry.package],
        }[action]

        if action == "remove":
            answer = QMessageBox.question(self, APP_NAME, f"Remove {entry.name}?")
            if answer != QMessageBox.StandardButton.Yes:
                return

        self._run_package(args, f"{action.title()} {entry.name}")

    def _run_package(self, apt_args, label):
        prefix = ["pkexec", "apt-get"] if shutil.which("pkexec") else ["sudo", "apt-get"]
        self.run_command(prefix + apt_args, label)

    def run_script(self, name: str):
        path = SCRIPTS_DIR / name
        if not path.exists():
            QMessageBox.warning(self, APP_NAME, f"Script not found:\n{path}")
            return
        self.run_command(["bash", str(path)], name)

    def run_command(self, command: list[str], label: str | None = None):
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            QMessageBox.information(self, APP_NAME, "Another task is already running.")
            return

        self.set_page(len(self.pages) - 1)
        self.log("$ " + " ".join(command))
        self.status_label.setText(label or "Running command…")

        self.process = QProcess(self)
        self.process.setProgram(command[0])
        self.process.setArguments(command[1:])
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.finished.connect(self._finished)
        self.process.start()

    def _read_output(self):
        if self.process:
            text = bytes(self.process.readAllStandardOutput()).decode(errors="replace")
            for line in text.rstrip().splitlines():
                self.log(line)

    def _finished(self, code, status):
        self.log(f"Process finished with exit code {code}")
        self.status_label.setText("Ready")
