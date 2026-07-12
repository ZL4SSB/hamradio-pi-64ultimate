from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit
from constants import ASSETS_DIR
from qt_app.widgets import PageHeader

class LogsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.addWidget(PageHeader("Help & Logs", "Live command output and troubleshooting.",
                                    str(ASSETS_DIR / "branding" / "hamradio-pi-128.png")))
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

    def append(self, text: str):
        self.output.appendPlainText(text)
