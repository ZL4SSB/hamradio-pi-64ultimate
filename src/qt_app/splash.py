from __future__ import annotations

import webbrowser
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog, QLabel, QPushButton, QProgressBar, QVBoxLayout, QHBoxLayout,
    QFrame
)

from constants import APP_NAME, APP_VERSION, ASSETS_DIR, DONATE_URL

class SplashDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(620, 720)
        self.setStyleSheet("""
            QDialog { background:#07111A; border:2px solid #19C2AF; }
            QLabel { color:#F1F6FB; }
            QProgressBar { background:#152131; border:1px solid #2A3D55; border-radius:7px; height:18px; }
            QProgressBar::chunk { background:#19C2AF; border-radius:6px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 20, 26, 22)
        layout.setSpacing(10)

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(str(ASSETS_DIR / "branding" / "hamradio-pi-logo.png"))
        if not pix.isNull():
            logo.setPixmap(pix.scaled(340, 340, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(logo)

        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:25pt;font-weight:700;")
        layout.addWidget(title)

        sub = QLabel("Ham Shack Control Centre for Raspberry Pi")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color:#9CB0C3;font-size:11pt;")
        layout.addWidget(sub)

        self.status = QLabel("Starting…")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(5)
        layout.addWidget(self.progress)

        version = QLabel(f"Version {APP_VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color:#9CB0C3;")
        layout.addWidget(version)

        donate = QFrame()
        donate.setStyleSheet("QFrame{background:#111923;border:1px solid #C99B16;border-radius:8px;}")
        dlay = QVBoxLayout(donate)
        heading = QLabel("Support HamRadio-Pi Ultimate")
        heading.setStyleSheet("color:#FFD55A;font-weight:700;font-size:11pt;")
        dlay.addWidget(heading)
        text = QLabel("If this project is useful, please consider supporting development.")
        text.setWordWrap(True)
        dlay.addWidget(text)
        row = QHBoxLayout()
        button = QPushButton("Donate")
        button.setStyleSheet("background:#F4C430;color:#111111;border:none;border-radius:7px;padding:9px 24px;font-weight:700;")
        button.clicked.connect(lambda: webbrowser.open(DONATE_URL))
        row.addWidget(button)
        row.addWidget(QLabel("Minimum $1 USD"))
        row.addStretch()
        dlay.addLayout(row)
        layout.addWidget(donate)

    def update_stage(self, value: int, text: str):
        self.progress.setValue(value)
        self.status.setText(text)
