from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QCheckBox, QMessageBox
from constants import ASSETS_DIR
from services.settings_service import load_settings, save_settings
from qt_app.widgets import PageHeader, Card, ActionButton

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        settings = load_settings()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.addWidget(PageHeader("Settings", "Station identity and preferences.",
                                    str(ASSETS_DIR / "branding" / "hamradio-pi-128.png")))
        card = Card()
        form = QFormLayout(card)
        self.callsign = QLineEdit(settings.get("callsign", ""))
        self.locator = QLineEdit(settings.get("locator", ""))
        self.station = QLineEdit(settings.get("station_name", ""))
        self.confirm_remove = QCheckBox()
        self.confirm_remove.setChecked(settings.get("confirm_remove", True))
        form.addRow("Callsign", self.callsign)
        form.addRow("Maidenhead locator", self.locator)
        form.addRow("Station name", self.station)
        form.addRow("Confirm before remove", self.confirm_remove)
        save = ActionButton("Save settings")
        save.clicked.connect(self.save)
        form.addRow(save)
        layout.addWidget(card)
        layout.addStretch()

    def save(self):
        save_settings({
            "callsign": self.callsign.text().strip().upper(),
            "locator": self.locator.text().strip().upper(),
            "station_name": self.station.text().strip(),
            "confirm_remove": self.confirm_remove.isChecked(),
            "auto_refresh_dashboard": True,
        })
        QMessageBox.information(self, "HamRadio-Pi Ultimate", "Settings saved.")
