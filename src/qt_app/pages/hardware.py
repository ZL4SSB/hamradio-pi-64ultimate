from __future__ import annotations

from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
)

from constants import ASSETS_DIR
from services.hardware_service import scan_hardware
from qt_app.widgets import Card, PageHeader, ActionButton
from qt_app.workers import FunctionWorker

class HardwarePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pool = QThreadPool.globalInstance()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("Hardware", "Detect SDRs, serial interfaces and sound devices.",
                                    str(ASSETS_DIR / "branding" / "hamradio-pi-128.png")))

        row = QHBoxLayout()
        scan = ActionButton("Run hardware scan")
        scan.clicked.connect(self.scan)
        row.addWidget(scan)
        clear = ActionButton("Clear", secondary=True)
        clear.clicked.connect(self.clear)
        row.addWidget(clear)
        row.addStretch()
        self.summary = QLabel("No scan has been run.")
        self.summary.setObjectName("Muted")
        row.addWidget(self.summary)
        layout.addLayout(row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.box = QVBoxLayout(self.container)
        self.box.setSpacing(8)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll, 1)

    def clear(self):
        while self.box.count():
            item = self.box.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.summary.setText("No scan has been run.")

    def scan(self):
        self.clear()
        self.summary.setText("Scanning…")
        worker = FunctionWorker(scan_hardware)
        worker.signals.finished.connect(self._show)
        worker.signals.error.connect(lambda text: self.summary.setText(f"Scan failed: {text}"))
        self.pool.start(worker)

    def _show(self, items):
        for item in items:
            card = Card()
            layout = QVBoxLayout(card)
            title = QLabel(item.name)
            title.setStyleSheet("font-size:13pt;font-weight:700;")
            layout.addWidget(title)
            kind = QLabel(item.kind)
            kind.setObjectName("Teal")
            layout.addWidget(kind)
            detail = QLabel(item.detail)
            detail.setWordWrap(True)
            detail.setObjectName("Muted")
            layout.addWidget(detail)
            rec = QLabel(f"Recommended: {item.recommendation}")
            rec.setWordWrap(True)
            rec.setStyleSheet("color:#4BD9A8;")
            layout.addWidget(rec)
            self.box.addWidget(card)
        self.box.addStretch()
        self.summary.setText(f"{len(items)} result(s)")
