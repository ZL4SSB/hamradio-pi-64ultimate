from __future__ import annotations

from PyQt6.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPlainTextEdit, QProgressBar
)

from constants import ASSETS_DIR
from services.system_service import system_snapshot
from services.settings_service import load_settings
from qt_app.widgets import Card, MetricCard, PageHeader, ActionButton
from qt_app.workers import FunctionWorker


class DashboardPage(QWidget):
    open_page_requested = pyqtSignal(int)

    def __init__(self, open_hardware_callback, parent=None):
        super().__init__(parent)
        self.open_hardware_callback = open_hardware_callback
        self.pool = QThreadPool.globalInstance()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 18, 24, 18)
        outer.setSpacing(12)

        header_row = QHBoxLayout()
        header_row.addWidget(
            PageHeader(
                "Dashboard",
                "Your Raspberry Pi ham shack at a glance.",
                str(ASSETS_DIR / "branding" / "hamradio-pi-128.png"),
            ),
            1,
        )
        outer.addLayout(header_row)

        # Top headline cards.
        headline = QGridLayout()
        headline.setSpacing(10)
        self.headline_cards = {}

        headline_defs = [
            ("network", "Internet", "NET"),
            ("temperature", "CPU temperature", "CPU"),
            ("memory", "Memory", "RAM"),
            ("disk", "Storage", "SSD"),
        ]
        for index, (key, title, icon) in enumerate(headline_defs):
            card = MetricCard(title, icon)
            self.headline_cards[key] = card
            headline.addWidget(card, 0, index)
        outer.addLayout(headline)

        middle = QHBoxLayout()
        middle.setSpacing(10)

        # System status.
        system_card = Card()
        sys = QVBoxLayout(system_card)
        title = QLabel("System status")
        title.setStyleSheet("font-size:14pt;font-weight:700;")
        sys.addWidget(title)

        self.status_rows = {}
        for key, label in [
            ("model", "Computer"),
            ("os", "Operating system"),
            ("network_detail", "IP address"),
            ("callsign", "Callsign"),
            ("locator", "Locator"),
        ]:
            row = QHBoxLayout()
            name = QLabel(label)
            name.setObjectName("Muted")
            value = QLabel("—")
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            value.setStyleSheet("font-weight:700;")
            row.addWidget(name)
            row.addStretch()
            row.addWidget(value)
            sys.addLayout(row)
            self.status_rows[key] = value

        self.health_bar = QProgressBar()
        self.health_bar.setRange(0, 100)
        self.health_bar.setValue(0)
        self.health_bar.setFormat("System health %p%")
        sys.addWidget(self.health_bar)
        middle.addWidget(system_card, 2)

        # Quick actions.
        actions_card = Card()
        actions = QVBoxLayout(actions_card)
        action_title = QLabel("Quick actions")
        action_title.setStyleSheet("font-size:14pt;font-weight:700;")
        actions.addWidget(action_title)

        action_items = [
            ("Scan hardware", self.open_hardware_callback),
            ("Application manager", lambda: self.open_page_requested.emit(1)),
            ("WPSD Centre", lambda: self.open_page_requested.emit(2)),
            ("Propagation", lambda: self.open_page_requested.emit(4)),
            ("Settings", lambda: self.open_page_requested.emit(5)),
            ("Help & Logs", lambda: self.open_page_requested.emit(6)),
        ]
        for text, callback in action_items:
            button = ActionButton(text, secondary=True)
            button.clicked.connect(callback)
            actions.addWidget(button)
        actions.addStretch()
        middle.addWidget(actions_card, 1)

        # Assistant / mascot.
        assistant_card = Card()
        assistant = QVBoxLayout(assistant_card)
        heading = QLabel("Shack Assistant")
        heading.setStyleSheet("color:#4BD9A8;font-size:14pt;font-weight:700;")
        assistant.addWidget(heading)

        self.assistant_text = QLabel(
            "Run a hardware scan and I’ll recommend useful software for anything I recognise."
        )
        self.assistant_text.setWordWrap(True)
        assistant.addWidget(self.assistant_text)

        scan = ActionButton("Scan hardware")
        scan.clicked.connect(self.open_hardware_callback)
        assistant.addWidget(scan, alignment=Qt.AlignmentFlag.AlignLeft)

        mascot = QLabel()
        mascot.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        pix = QPixmap(str(ASSETS_DIR / "branding" / "mascot.png"))
        if not pix.isNull():
            mascot.setPixmap(
                pix.scaled(
                    200,
                    200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        assistant.addWidget(mascot, 1)
        middle.addWidget(assistant_card, 1)

        outer.addLayout(middle, 1)

        # Activity strip.
        activity = Card()
        activity_layout = QVBoxLayout(activity)
        activity_title = QLabel("Recent activity")
        activity_title.setStyleSheet("font-size:12pt;font-weight:700;")
        activity_layout.addWidget(activity_title)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(250)
        self.log.setPlaceholderText("Activity and command output will appear here.")
        activity_layout.addWidget(self.log)
        outer.addWidget(activity, 1)

        self.refresh()

    def refresh(self):
        worker = FunctionWorker(system_snapshot)
        worker.signals.finished.connect(self._apply)
        worker.signals.error.connect(lambda text: self.add_log(f"Dashboard error: {text}"))
        self.pool.start(worker)

    def _apply(self, snapshot: dict):
        settings = load_settings()

        model, model_detail = snapshot.get("model", ("—", ""))
        temperature, temperature_detail = snapshot.get("temperature", ("—", ""))
        memory, memory_detail = snapshot.get("memory", ("—", ""))
        disk, disk_detail = snapshot.get("disk", ("—", ""))
        network, network_detail = snapshot.get("network", ("Offline", ""))
        os_name, os_detail = snapshot.get("os", ("—", ""))

        self.headline_cards["temperature"].set_value(temperature, temperature_detail)
        self.headline_cards["memory"].set_value(memory, memory_detail)
        self.headline_cards["disk"].set_value(disk, disk_detail)

        network_colour = "#4BD9A8" if network == "Online" else "#F17982"
        self.headline_cards["network"].set_value(network, network_detail, network_colour)

        self.status_rows["model"].setText(model)
        self.status_rows["os"].setText(f"{os_name} {os_detail}".strip())
        self.status_rows["network_detail"].setText(network_detail or "Unavailable")
        self.status_rows["callsign"].setText(settings.get("callsign") or "Not configured")
        self.status_rows["locator"].setText(settings.get("locator") or "Not configured")

        score = 25
        if network == "Online":
            score += 25
        if temperature != "Unavailable":
            score += 20
        if settings.get("callsign"):
            score += 15
        if settings.get("locator"):
            score += 15
        self.health_bar.setValue(score)

        self.assistant_text.setText(
            "The network is online and external services are available."
            if network == "Online"
            else "The network appears offline. Local tools will still work."
        )

    def add_log(self, text: str):
        self.log.appendPlainText(text)
