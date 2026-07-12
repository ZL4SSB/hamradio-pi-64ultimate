from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QTextEdit, QPushButton
)

from constants import ASSETS_DIR
from services.system_service import system_snapshot
from qt_app.widgets import Card, MetricCard, PageHeader, ActionButton
from qt_app.workers import FunctionWorker

class DashboardPage(QWidget):
    hardware_requested = None

    def __init__(self, open_hardware_callback, parent=None):
        super().__init__(parent)
        self.open_hardware_callback = open_hardware_callback
        self.pool = QThreadPool.globalInstance()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.setSpacing(14)

        logo_path = str(ASSETS_DIR / "branding" / "hamradio-pi-128.png")
        layout.addWidget(PageHeader("Dashboard", "Live status for your Raspberry Pi ham shack.", logo_path))

        grid = QGridLayout()
        grid.setSpacing(10)
        definitions = [
            ("model", "Computer", "Pi"),
            ("temperature", "CPU temperature", "°C"),
            ("memory", "Memory", "RAM"),
            ("disk", "Storage", "SSD"),
            ("network", "Network", "IP"),
            ("os", "Operating system", "OS"),
        ]
        self.cards = {}
        for index, (key, title, icon) in enumerate(definitions):
            card = MetricCard(title, icon)
            self.cards[key] = card
            grid.addWidget(card, index // 3, index % 3)
        layout.addLayout(grid)

        lower = QHBoxLayout()
        lower.setSpacing(10)

        activity = Card()
        al = QVBoxLayout(activity)
        al.addWidget(QLabel("Recent activity"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        al.addWidget(self.log)
        lower.addWidget(activity, 2)

        assistant = Card()
        sl = QVBoxLayout(assistant)
        badge = QLabel("K")
        badge.setFixedSize(52, 52)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet("background:#0F887C;color:white;border-radius:26px;font-size:18pt;font-weight:700;")
        sl.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)
        heading = QLabel("Shack Assistant")
        heading.setStyleSheet("color:#4BD9A8;font-size:14pt;font-weight:700;")
        sl.addWidget(heading)
        self.assistant_text = QLabel("Run a hardware scan and I’ll recommend useful software for anything I recognise.")
        self.assistant_text.setWordWrap(True)
        sl.addWidget(self.assistant_text)
        scan = ActionButton("Scan hardware")
        scan.clicked.connect(open_hardware_callback)
        sl.addWidget(scan, alignment=Qt.AlignmentFlag.AlignLeft)

        mascot = QLabel()
        pix = QPixmap(str(ASSETS_DIR / "branding" / "mascot.png"))
        if not pix.isNull():
            mascot.setPixmap(pix.scaled(210, 210, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            sl.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        lower.addWidget(assistant, 1)

        layout.addLayout(lower, 1)
        self.refresh()

    def refresh(self):
        worker = FunctionWorker(system_snapshot)
        worker.signals.finished.connect(self._apply)
        worker.signals.error.connect(lambda text: self.add_log(f"Dashboard error: {text}"))
        self.pool.start(worker)

    def _apply(self, snapshot: dict):
        for key, (value, detail) in snapshot.items():
            colour = "#4BD9A8" if key == "network" and value == "Online" else None
            if key == "network" and value != "Online":
                colour = "#F17982"
            self.cards[key].set_value(value, detail, colour)

    def add_log(self, text: str):
        self.log.append(text)
