from __future__ import annotations
from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from constants import ASSETS_DIR
from services.propagation_service import fetch_snapshot
from qt_app.widgets import PageHeader, MetricCard, ActionButton, Card
from qt_app.workers import FunctionWorker

class PropagationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pool = QThreadPool.globalInstance()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.addWidget(PageHeader("Propagation", "Live solar and geomagnetic data.",
                                    str(ASSETS_DIR / "branding" / "hamradio-pi-128.png")))
        refresh = ActionButton("Refresh propagation")
        refresh.clicked.connect(self.refresh)
        layout.addWidget(refresh, alignment=Qt.AlignmentFlag.AlignLeft)
        grid = QGridLayout()
        self.cards = {}
        defs = [
            ("solar_flux", "Solar flux", "SFI"),
            ("k_index", "Planetary K-index", "Kp"),
            ("solar_wind", "Solar wind", "SW"),
            ("r_scale", "Radio blackout", "R"),
            ("s_scale", "Radiation storm", "S"),
            ("g_scale", "Geomagnetic storm", "G"),
        ]
        for i, (key, title, icon) in enumerate(defs):
            card = MetricCard(title, icon)
            self.cards[key] = card
            grid.addWidget(card, i // 3, i % 3)
        layout.addLayout(grid)
        self.band_card = Card()
        self.band_layout = QVBoxLayout(self.band_card)
        self.band_labels = {}
        for band in ("80m", "40m", "20m", "15m", "10m"):
            label = QLabel(f"{band}: Press Refresh")
            self.band_labels[band] = label
            self.band_layout.addWidget(label)
        layout.addWidget(self.band_card)
        layout.addStretch()

    def refresh(self):
        worker = FunctionWorker(fetch_snapshot)
        worker.signals.finished.connect(self._apply)
        self.pool.start(worker)

    def _apply(self, data):
        for key, card in self.cards.items():
            card.set_value(str(data.get(key, "—")))
        for band, text in data.get("bands", {}).items():
            self.band_labels[band].setText(f"{band}: {text}")
