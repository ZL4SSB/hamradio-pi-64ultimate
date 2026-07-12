from __future__ import annotations
import shutil
import subprocess
import webbrowser
from pathlib import Path

from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QPushButton, QStackedWidget, QMessageBox, QButtonGroup, QApplication
)

from constants import APP_NAME, APP_VERSION, ASSETS_DIR, DONATE_URL, SCRIPTS_DIR
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
        self.resize(1280, 820)
        self.setMinimumSize(1040, 700)
        self.setWindowIcon(QIcon(str(ASSETS_DIR / "branding" / "hamradio-pi-256.png")))

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

        brand_row = QHBoxLayout()
        logo = QLabel()
        pix = QPixmap(str(ASSETS_DIR / "branding" / "hamradio-pi-128.png"))
        if not pix.isNull():
            logo.setPixmap(pix.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
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
        self.pages = [
            DashboardPage(self.open_hardware),
            ApplicationsPage(self),
            WPSDPage(self),
            HardwarePage(),
            PropagationPage(),
            SettingsPage(),
            LogsPage(),
        ]
        names = ["Dashboard", "Applications", "WPSD Centre", "Hardware", "Propagation", "Settings", "Help & Logs"]
        icons = ["⌂", "▦", "◉", "⌁", "≋", "⚙", "?"]

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        for index, (name, icon) in enumerate(zip(names, icons)):
            button = QPushButton(f"  {icon}   {name}")
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.clicked.connect(lambda _, i=index: self.stack.setCurrentIndex(i))
            self.button_group.addButton(button, index)
            side.addWidget(button)
            self.stack.addWidget(self.pages[index])
        self.button_group.button(0).setChecked(True)

        side.addStretch()
        donate = QPushButton("Donate")
        donate.setObjectName("Donate")
        donate.clicked.connect(lambda: webbrowser.open(DONATE_URL))
        side.addWidget(donate)
        side.addWidget(QLabel(f"Version {APP_VERSION}"))

        outer.addWidget(sidebar)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        top = QFrame()
        top.setObjectName("TopBar")
        top.setFixedHeight(48)
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(16, 0, 16, 0)
        self.top_title = QLabel("Dashboard")
        self.top_title.setStyleSheet("font-weight:700;")
        top_lay.addWidget(self.top_title)
        top_lay.addStretch()
        self.online = QLabel("● Ready")
        self.online.setStyleSheet("color:#4BD9A8;font-weight:700;")
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
        status_lay.addWidget(QLabel("Built for Amateur Radio"))
        right.addWidget(status)

        outer.addLayout(right, 1)
        self.stack.currentChanged.connect(lambda i: self.top_title.setText(names[i]))

        self.process = None

    @property
    def logs_page(self):
        return self.pages[-1]

    def log(self, text: str):
        self.logs_page.append(text)
        self.pages[0].add_log(text)

    def open_hardware(self):
        self.stack.setCurrentIndex(3)
        self.button_group.button(3).setChecked(True)
        self.pages[3].scan()

    def launch_application(self, entry):
        try:
            subprocess.Popen([entry.command], start_new_session=True)
        except Exception as exc:
            QMessageBox.critical(self, APP_NAME, str(exc))

    def install_application(self, entry):
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
        self.stack.setCurrentIndex(len(self.pages) - 1)
        self.button_group.button(len(self.pages) - 1).setChecked(True)
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
