from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QSizePolicy
)

class Card(QFrame):
    def __init__(self, parent=None, soft: bool = False):
        super().__init__(parent)
        self.setObjectName("SoftCard" if soft else "Card")

class MetricCard(Card):
    def __init__(self, title: str, icon_text: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(5)

        top = QHBoxLayout()
        badge = QLabel(icon_text)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedSize(42, 32)
        badge.setStyleSheet("background:#202F43;color:#19C2AF;border-radius:6px;font-weight:700;")
        title_label = QLabel(title)
        title_label.setObjectName("Muted")
        top.addWidget(badge)
        top.addSpacing(8)
        top.addWidget(title_label)
        top.addStretch()
        layout.addLayout(top)

        self.value = QLabel("—")
        self.value.setObjectName("MetricValue")
        layout.addWidget(self.value)

        self.detail = QLabel("")
        self.detail.setObjectName("Muted")
        self.detail.setWordWrap(True)
        layout.addWidget(self.detail)

    def set_value(self, value: str, detail: str = "", colour: str | None = None):
        self.value.setText(value)
        if colour:
            self.value.setStyleSheet(f"color:{colour};")
        else:
            self.value.setStyleSheet("")
        self.detail.setText(detail)

class PageHeader(QWidget):
    def __init__(self, title: str, subtitle: str, logo_path: str | None = None, parent=None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)

        texts = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("PageSubtitle")
        texts.addWidget(title_label)
        texts.addWidget(subtitle_label)
        row.addLayout(texts)
        row.addStretch()

        if logo_path:
            logo = QLabel()
            pix = QPixmap(logo_path)
            if not pix.isNull():
                logo.setPixmap(pix.scaled(74, 74, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                row.addWidget(logo)

class ActionButton(QPushButton):
    def __init__(self, text: str, secondary: bool = False, parent=None):
        super().__init__(text, parent)
        if secondary:
            self.setProperty("secondary", True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
