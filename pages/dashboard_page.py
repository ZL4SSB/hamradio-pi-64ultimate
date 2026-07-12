from __future__ import annotations

import threading
import tkinter as tk

from constants import COLORS
from pages.base_page import BasePage
from services.system_service import system_snapshot
from ui.widgets import Card, MetricCard, ToolTip, action_button


class DashboardPage(BasePage):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, app, "Dashboard", "Live status for your Raspberry Pi ham shack.")

        grid = tk.Frame(self.body, bg=COLORS["background"])
        grid.pack(fill="x")
        for col in range(3):
            grid.grid_columnconfigure(col, weight=1, uniform="metrics")

        self.cards = {}
        definitions = [
            ("model", "Computer"),
            ("temperature", "CPU temperature"),
            ("memory", "Memory"),
            ("disk", "Storage"),
            ("network", "Network"),
            ("os", "Operating system"),
        ]
        for index, (key, title) in enumerate(definitions):
            card = MetricCard(grid, title)
            row, col = divmod(index, 3)
            card.grid(row=row, column=col, sticky="nsew", padx=(0 if col == 0 else 7, 0), pady=6)
            self.cards[key] = card

        lower = tk.Frame(self.body, bg=COLORS["background"])
        lower.pack(fill="both", expand=True, pady=(12, 0))
        lower.grid_columnconfigure(0, weight=2)
        lower.grid_columnconfigure(1, weight=1)
        lower.grid_rowconfigure(0, weight=1)

        activity = Card(lower)
        activity.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        tk.Label(activity, text="Recent activity", bg=COLORS["panel"], fg=COLORS["text"],
                 font=("DejaVu Sans", 12, "bold")).pack(anchor="w", padx=15, pady=(13, 8))
        self.output = tk.Text(
            activity, bg=COLORS["panel_alt"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief="flat", height=10,
            font=("DejaVu Sans Mono", 9), wrap="word", state="disabled"
        )
        self.output.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        yobbo = Card(lower)
        yobbo.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        tk.Label(yobbo, text="Yobbo says…", bg=COLORS["panel"], fg=COLORS["success"],
                 font=("DejaVu Sans", 13, "bold")).pack(anchor="w", padx=15, pady=(14, 8))
        tk.Label(
            yobbo,
            text="Run a hardware scan and I’ll recommend useful software for anything I recognise.",
            bg=COLORS["panel"], fg=COLORS["text"], justify="left",
            wraplength=300, font=("DejaVu Sans", 10)
        ).pack(anchor="w", padx=15, pady=(0, 12))
        button = action_button(yobbo, "Scan hardware", app.open_hardware_scan)
        button.pack(anchor="w", padx=15, pady=(0, 15))
        ToolTip(button, "Run a read-only scan for radio, SDR, audio and serial hardware.")

    def refresh(self) -> None:
        self.app.set_status("Refreshing dashboard…")

        def worker() -> None:
            snapshot = system_snapshot()
            self.after(0, self._apply_snapshot, snapshot)

        threading.Thread(target=worker, daemon=True).start()

    def _apply_snapshot(self, snapshot: dict) -> None:
        for key, (value, detail) in snapshot.items():
            colour = None
            if key == "network":
                colour = COLORS["success"] if value == "Online" else COLORS["danger"]
            self.cards[key].set(value, detail, colour)
        self.app.set_status("Dashboard updated")

    def log(self, line: str) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", line + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")
