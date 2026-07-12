from __future__ import annotations
import webbrowser
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from constants import ASSETS_DIR
from qt_app.widgets import Card, PageHeader, ActionButton

class WPSDPage(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("WPSD Centre", "Prepare, inspect, back up and restore WPSD media.",
                                    str(ASSETS_DIR / "branding" / "hamradio-pi-128.png")))
        warning = QLabel("Safety: no drive is selected automatically. Always verify the exact target device.")
        warning.setStyleSheet("background:#3A301F;color:#F0C76D;border:1px solid #F0C76D;border-radius:8px;padding:10px;font-weight:700;")
        layout.addWidget(warning)

        actions = [
            ("Open WPSD download page", "Choose the correct image for your hotspot hardware.",
             lambda: webbrowser.open("https://wpsd.radio/#download-wpsd")),
            ("Detect removable drives", "Show a read-only drive report.",
             lambda: controller.run_command(["lsblk", "-o", "NAME,PATH,SIZE,FSTYPE,TYPE,TRAN,RM,MOUNTPOINTS,MODEL"])),
            ("Open existing card builder", "Run scripts/wpsd-card-builder.sh.",
             lambda: controller.run_script("wpsd-card-builder.sh")),
            ("Back up a selected device", "Run the guided backup helper.",
             lambda: controller.run_script("wpsd-backup.sh")),
            ("Restore an image", "Run the guided restore helper with confirmation.",
             lambda: controller.run_script("wpsd-restore.sh")),
        ]
        for title, detail, callback in actions:
            card = Card()
            box = QVBoxLayout(card)
            heading = QLabel(title)
            heading.setStyleSheet("font-size:13pt;font-weight:700;")
            box.addWidget(heading)
            description = QLabel(detail)
            description.setObjectName("Muted")
            box.addWidget(description)
            button = ActionButton(title)
            button.clicked.connect(callback)
            box.addWidget(button, alignment=0)
            layout.addWidget(card)
        layout.addStretch()
