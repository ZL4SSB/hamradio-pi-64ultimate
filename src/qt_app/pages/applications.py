from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QScrollArea, QGridLayout, QLabel, QPushButton
)

from constants import DATA_DIR, ASSETS_DIR
from services.application_service import load_catalogue, is_installed
from qt_app.widgets import Card, PageHeader, ActionButton

class ApplicationsPage(QWidget):
    def __init__(self, app_controller, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller
        self.entries = load_catalogue(DATA_DIR / "applications.json")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("Applications", "Install and manage amateur-radio software.",
                                    str(ASSETS_DIR / "branding" / "hamradio-pi-128.png")))

        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search applications…")
        self.search.textChanged.connect(self.render)
        controls.addWidget(self.search, 1)
        self.category = QComboBox()
        categories = ["All categories"] + sorted({x.category for x in self.entries})
        self.category.addItems(categories)
        self.category.currentTextChanged.connect(self.render)
        controls.addWidget(self.category)
        layout.addLayout(controls)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(10)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll, 1)
        self.render()

    def clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def render(self):
        self.clear_grid()
        query = self.search.text().strip().lower()
        category = self.category.currentText()
        filtered = [
            x for x in self.entries
            if (category == "All categories" or x.category == category)
            and (not query or query in x.name.lower() or query in x.description.lower() or query in x.category.lower())
        ]

        for index, entry in enumerate(filtered):
            installed = is_installed(entry)
            card = Card()
            box = QVBoxLayout(card)
            top = QHBoxLayout()
            badge = QLabel(entry.name[:2].upper())
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setFixedSize(46, 42)
            badge.setStyleSheet("background:#202F43;color:#19C2AF;border-radius:7px;font-weight:700;")
            top.addWidget(badge)

            names = QVBoxLayout()
            title = QLabel(entry.name)
            title.setStyleSheet("font-size:13pt;font-weight:700;")
            cat = QLabel(entry.category)
            cat.setObjectName("Teal")
            names.addWidget(title)
            names.addWidget(cat)
            top.addLayout(names)
            top.addStretch()

            status = QLabel("● Installed" if installed else "● Available")
            status.setStyleSheet(f"color:{'#4BD9A8' if installed else '#F0C76D'};font-weight:700;")
            top.addWidget(status)
            box.addLayout(top)

            desc = QLabel(entry.description)
            desc.setWordWrap(True)
            desc.setObjectName("Muted")
            box.addWidget(desc)

            buttons = QHBoxLayout()
            if installed:
                launch = ActionButton("Launch")
                launch.clicked.connect(lambda _, e=entry: self.app_controller.launch_application(e))
                buttons.addWidget(launch)
                for action in ("update", "repair", "remove"):
                    b = ActionButton(action.title(), secondary=True)
                    b.clicked.connect(lambda _, a=action, e=entry: self.app_controller.package_action(a, e))
                    buttons.addWidget(b)
            else:
                install = ActionButton("Install")
                install.clicked.connect(lambda _, e=entry: self.app_controller.install_application(e))
                buttons.addWidget(install)
            buttons.addStretch()
            if entry.recommended:
                recommended = QLabel("★ Recommended")
                recommended.setStyleSheet("color:#66A8FF;font-weight:700;")
                buttons.addWidget(recommended)
            box.addLayout(buttons)
            self.grid.addWidget(card, index // 2, index % 2)

        self.grid.setRowStretch((len(filtered) + 1) // 2, 1)
